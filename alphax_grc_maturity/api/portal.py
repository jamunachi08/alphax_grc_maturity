# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
"""Whitelisted endpoints used by the /grc-assessment page (guests allowed when Settings permit)."""

import json
import secrets

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from alphax_grc_maturity.engine import branding
from alphax_grc_maturity.engine.resolver import build_context, resolve_questions, resolve_regulators, structure
from alphax_grc_maturity.engine.scoring import build_report

DT = "GRC Maturity Assessment"
PROFILE_FIELDS = (
	"organization_name", "contact_name", "contact_email", "contact_phone", "language", "industry_type",
	"industry_sector", "sector_other", "company_nationality", "cr_number", "legal_form", "entity_size",
	"license_na", "license_types_text", "other_regulator",
)


def _settings():
	return frappe.get_cached_doc("GRC Maturity Settings")


def _guard():
	if frappe.session.user == "Guest" and not _settings().allow_guest:
		frappe.throw(_("Please sign in to take the assessment."), frappe.PermissionError)


def _load(id, k):
	_guard()
	if not id or not frappe.db.exists(DT, id):
		frappe.throw(_("No saved assessment found with that ID."), frappe.DoesNotExistError)
	key = frappe.db.get_value(DT, id, "access_key") or ""
	if not (k and secrets.compare_digest(str(k).strip().upper(), key)):
		if not (frappe.session.user != "Guest" and frappe.has_permission(DT, "read", id)):
			frappe.throw(_("No saved assessment found with that ID."), frappe.DoesNotExistError)
	return frappe.get_doc(DT, id)


def _parse(v):
	return json.loads(v) if isinstance(v, str) else (v or {})


def _ctx(p):
	return build_context(
		industry_type=p.get("industry_type"), industry_sector=p.get("industry_sector"),
		company_nationality=p.get("company_nationality"), legal_form=p.get("legal_form"),
		entity_size=p.get("entity_size"),
		license_types=[] if p.get("license_na") else [l.get("license_type") for l in p.get("licenses") or []],
		regulators_yes=[r for r, v in (p.get("regulators") or {}).items() if v == "Yes"],
	)


@frappe.whitelist(allow_guest=True)
def bootstrap(b=None, lang=None):
	_guard()
	return branding.boot_payload(b, lang)


@frappe.whitelist(allow_guest=True)
def resolve(profile, lang="en"):
	"""Regulator list and question structure for a (possibly unsaved) profile."""
	_guard()
	p = _parse(profile)
	ctx = _ctx(p)
	brand = branding.get_brand(p.get("brand"))
	questions, _profiles = resolve_questions(ctx)
	return {
		"regulators": branding.label_regulators(resolve_regulators(ctx), lang),
		"sections": structure(questions, lang, show_weights=bool(brand and brand.show_weights)),
		"question_count": len(questions),
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=lambda: _settings().max_saves_per_hour or 300, seconds=3600)
def save(payload, id=None, k=None):
	p = _parse(payload)
	if id:
		doc = _load(id, k)
		if doc.status != "Draft":
			frappe.throw(_("This assessment has been submitted and can no longer be changed."))
	else:
		_guard()
		doc = frappe.new_doc(DT)
		doc.brand = branding.get_brand(p.get("brand")).name
		doc.source_ip = frappe.local.request_ip if getattr(frappe.local, "request_ip", None) else None
	_apply(doc, p)
	doc.flags.ignore_permissions = True
	doc.save()
	frappe.db.commit()
	return _state(doc)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=60, seconds=3600)
def submit(id, k, payload=None):
	doc = _load(id, k)
	if doc.status != "Draft":
		return report(id, k)
	if payload:
		_apply(doc, _parse(payload))
	doc.status = "Submitted"
	doc.flags.ignore_permissions = True
	doc.save()
	frappe.db.commit()
	return report(id, k)


@frappe.whitelist(allow_guest=True)
def load(id, k):
	doc = _load(id, k)
	return _state(doc)


@frappe.whitelist(allow_guest=True)
def report(id, k):
	doc = _load(id, k)
	brand = branding.get_brand(doc.brand)
	if doc.status == "Draft":
		frappe.throw(_("This assessment has not been submitted yet."))
	if brand.hide_score_from_respondent and doc.status not in ("Reviewed", "Closed") and frappe.session.user == "Guest":
		return {"hidden": True, "id": doc.name, "key": doc.access_key, "status": doc.status}
	return build_report(doc)


@frappe.whitelist(allow_guest=True)
def pdf(id, k):
	doc = _load(id, k)
	brand = branding.get_brand(doc.brand)
	if doc.status == "Draft" or (brand.hide_score_from_respondent and doc.status not in ("Reviewed", "Closed") and frappe.session.user == "Guest"):
		frappe.throw(_("The report is not available yet."))
	from frappe.utils.pdf import get_pdf

	html = frappe.get_print(DT, doc.name, print_format="GRC Maturity Report", doc=doc, no_letterhead=1)
	frappe.local.response.filename = f"{doc.name}.pdf"
	frappe.local.response.filecontent = get_pdf(html)
	frappe.local.response.type = "download"


# ---------------------------------------------------------------- helpers
def _apply(doc, p):
	for f in PROFILE_FIELDS:
		if f in p:
			doc.set(f, p.get(f))
	if "licenses" in p:
		doc.set("licenses", [])
		for l in p.get("licenses") or []:
			doc.append("licenses", {
				"license_type": l.get("license_type") or None, "license_name": l.get("license_name"),
				"is_valid": l.get("is_valid") or None, "expiry_date": l.get("expiry_date") or None,
			})
	if "regulators" in p:
		answers = p.get("regulators") or {}
		for r in doc.regulators:
			if r.regulator in answers:
				r.response = answers[r.regulator]
		known = {r.regulator for r in doc.regulators}
		for name, v in answers.items():
			if name not in known and frappe.db.exists("GRC Maturity Regulator", name):
				doc.append("regulators", {"regulator": name, "response": v})
	if "answers" in p:
		doc.flags.incoming_answers = {q: (v or None) for q, v in (p.get("answers") or {}).items()}


def _state(doc):
	lang = doc.language or "en"
	brand = branding.get_brand(doc.brand)
	from alphax_grc_maturity.engine.resolver import get_catalog

	qmap = {q["name"]: q for q in get_catalog()["questions"]}
	questions = []
	for a in doc.answers:
		q = qmap.get(a.question)
		if q:
			questions.append({**q, "section_weight": a.section_weight or 1, "weight": a.weight or 1})
	return {
		"id": doc.name, "k": doc.access_key, "status": doc.status,
		"profile": {
			**{f: doc.get(f) for f in PROFILE_FIELDS},
			"licenses": [{"license_type": l.license_type, "license_name": l.license_name, "is_valid": l.is_valid,
				"expiry_date": str(l.expiry_date or "")} for l in doc.licenses],
			"regulators": {r.regulator: r.response for r in doc.regulators if r.response},
		},
		"answers": {a.question: a.selected_value for a in doc.answers if a.selected_value},
		"regulators": branding.label_regulators(
			[{"regulator": r.regulator, "source": r.source} for r in doc.regulators], lang
		),
		"sections": structure(questions, lang, show_weights=bool(brand.show_weights)),
		"answered": doc.answered_count, "total": doc.question_count,
	}
