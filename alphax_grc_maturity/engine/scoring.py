# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
"""Profile validation, questionnaire sync and scoring for GRC Maturity Assessment."""

import random
import re
import secrets

import frappe
from frappe import _
from frappe.utils import flt, getdate, now_datetime, today

from alphax_grc_maturity.engine.resolver import (
	context_from_doc,
	context_hash,
	get_catalog,
	resolve_questions,
	resolve_regulators,
)

KEY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def settings():
	return frappe.get_cached_doc("GRC Maturity Settings")


# ---------------------------------------------------------------- ids
def new_assessment_id():
	for _i in range(20):
		d = now_datetime()
		name = f"GRC-{d:%Y-%m-%d-%H%M}-{random.randint(1000, 9999)}"
		if not frappe.db.exists("GRC Maturity Assessment", name):
			return name
	frappe.throw(_("Could not create a unique assessment ID. Try again."))


def new_access_key():
	length = max(6, min(32, settings().access_key_length or 8))
	return "".join(secrets.choice(KEY_ALPHABET) for _i in range(length))


# ---------------------------------------------------------------- profile
def validate_profile(doc):
	s = settings()
	if not (doc.organization_name or "").strip():
		frappe.throw(_("Enter the organization name."))
	if not doc.industry_type:
		frappe.throw(_("Select the industry type."))
	if not doc.industry_sector:
		frappe.throw(_("Select the industry sector."))
	sector = frappe.get_cached_doc("GRC Maturity Industry Sector", doc.industry_sector)
	if sector.industry_type != doc.industry_type:
		frappe.throw(_("Select the industry sector."))
	if sector.is_other and not (doc.sector_other or "").strip():
		frappe.throw(_("Name the sector."))
	if not sector.is_other:
		doc.sector_other = None
	if not doc.company_nationality:
		frappe.throw(_("Select the company nationality."))
	ask_cr = frappe.get_cached_doc("GRC Maturity Nationality", doc.company_nationality).ask_cr
	doc.cr_number = re.sub(r"\D", "", doc.cr_number or "") if ask_cr else None
	if doc.cr_number and len(doc.cr_number) != 10:
		frappe.throw(_("The CR number must be 10 digits, or leave it empty."))

	if s.ask_license_types:
		if doc.license_na:
			doc.set("licenses", [])
			doc.license_types_text = None
		else:
			rows = [l for l in doc.licenses if l.license_type or l.license_name or l.is_valid or l.expiry_date]
			doc.set("licenses", rows)
			if not (doc.license_types_text or "").strip() and not any(l.license_type for l in rows):
				frappe.throw(_("Enter the KSA license type, or tick N/A."))
			for l in rows:
				if l.license_type and not l.license_name:
					l.license_name = l.license_type
				if not ((l.license_name or "").strip() and l.is_valid and l.expiry_date):
					frappe.throw(_("Complete each license row (name, valid, expiry date), or remove it."))
				if l.is_valid == "Yes" and getdate(l.expiry_date) < getdate(today()):
					frappe.throw(_("A license with a past expiry date cannot be marked valid: {0}.").format(l.license_name))

	if doc.status != "Draft" and s.require_contact_email and not doc.contact_email:
		frappe.throw(_("Enter the contact email."))
	_sync_regulators(doc)


def _sync_regulators(doc):
	ctx = context_from_doc(doc)
	answers = {r.regulator: r.response for r in doc.regulators}
	doc.set("regulators", [])
	for r in resolve_regulators(ctx):
		doc.append("regulators", {**r, "response": answers.get(r["regulator"]) or ""})


# ---------------------------------------------------------------- questionnaire
def sync_questionnaire(doc):
	"""Rebuild the answer rows when the profile changes, keeping answers to questions that still apply."""
	incoming = doc.flags.get("incoming_answers") or {}
	ctx = context_from_doc(doc)
	h = context_hash(ctx)
	force = doc.flags.get("force_rebuild") or not doc.answers
	if not force and (doc.context_hash == h or doc.status != "Draft"):
		for row in doc.answers:
			if row.question in incoming:
				row.selected_value = incoming[row.question]
		return
	kept = {r.question: (r.selected_value, r.comment) for r in doc.answers}
	questions, profiles = resolve_questions(ctx)
	doc.set("answers", [])
	for q in questions:
		value, comment = kept.get(q["name"], (None, None))
		if q["name"] in incoming:
			value = incoming[q["name"]]
		doc.append("answers", {
			"question": q["name"], "question_code": q["code"], "section": q["section"], "topic": q["topic"],
			"question_text": q["text"], "selected_value": value, "comment": comment,
			"weight": q["weight"], "section_weight": q["section_weight"], "weight_source": q["weight_source"],
		})
	doc.context_hash = h
	doc.weightage_trace = " → ".join(profiles) or _("No profile (all weights 1)")


def _scale():
	s = settings()
	return {r.option_value: flt(r.points) for r in s.answer_scale}


def band_for(pct):
	bands = sorted(settings().bands, key=lambda b: b.min_pct, reverse=True)
	for b in bands:
		if flt(pct, 4) >= flt(b.min_pct):
			return b
	return bands[-1] if bands else None


def compute(doc):
	s = settings()
	scale = _scale()
	qmap = {q["name"]: q for q in get_catalog()["questions"]}
	threshold = {v.strip() for v in (s.improvement_threshold or "").split(",") if v.strip()}
	ar = doc.language == "ar"
	pick = lambda en, a: (a or en) if ar else en
	sections = {}
	topics = {}
	answered = na = 0

	for row in doc.answers:
		q = qmap.get(row.question)
		if not q:
			continue
		options = q["options"]
		pts_of = lambda o: flt(o["points"]) if flt(o["points"]) else scale.get(o["value"], 0)
		max_pts = max([pts_of(o) for o in options] or [100]) or 100
		row.max_points = max_pts
		value = (row.selected_value or "").strip().upper()
		valid = {o["value"].upper() for o in options} | ({"NA"} if q["allow_na"] else set())
		if value and value not in valid:
			value = ""
		row.selected_value = value or None
		row.is_na = 1 if value == "NA" else 0
		row.selected_label = row.selected_description = row.target_description = None
		counted = True
		if value == "NA":
			na += 1
			answered += 1
			row.points = 0
			row.selected_label = _("N/A")
			counted = not s.na_excluded
		elif value:
			answered += 1
			idx = next(i for i, o in enumerate(options) if o["value"].upper() == value)
			opt = options[idx]
			row.points = pts_of(opt)
			row.selected_label = pick(opt["label"], opt["label_ar"])
			row.selected_description = pick(opt["desc"], opt["desc_ar"])
			if opt["value"] in threshold:
				nxt = options[idx + 1] if idx + 1 < len(options) else None
				row.target_description = pick(opt["rec"], opt["rec_ar"]) or (
					(pick(nxt["label"], nxt["label_ar"]) + ": " + pick(nxt["desc"], nxt["desc_ar"])) if nxt else None
				)
		else:
			# Only possible on a Draft: submission is blocked while any answer is blank.
			row.points = 0
		w = flt(row.weight, 6)
		row.weighted_points = flt(row.points * w, 4) if counted else 0
		row.weighted_max = flt(max_pts * w, 4) if counted else 0

		sec = sections.setdefault(row.section, {"earned": 0, "possible": 0, "weight": flt(row.section_weight or 1), "answered": 0, "total": 0})
		sec["earned"] += row.weighted_points
		sec["possible"] += row.weighted_max
		sec["total"] += 1
		sec["answered"] += 1 if value else 0
		if row.topic:
			t = topics.setdefault(row.topic, {"section": row.section, "earned": 0, "possible": 0, "answered": 0, "total": 0})
			t["earned"] += row.weighted_points
			t["possible"] += row.weighted_max
			t["total"] += 1
			t["answered"] += 1 if value else 0

	cat = get_catalog()
	slabel = {x["name"]: pick(x["section_label"], x["section_label_ar"]) for x in cat["sections"]}
	tlabel = {x["name"]: pick(x["topic_label"], x["topic_label_ar"]) for x in cat["topics"]}
	doc.set("results", [])
	for name, v in sections.items():
		pct = v["earned"] / v["possible"] * 100 if v["possible"] else 0
		b = band_for(pct)
		doc.append("results", {"result_level": "Section", "section": name, "label": slabel.get(name, name), "weight": v["weight"],
			"earned": v["earned"], "possible": v["possible"], "percentage": pct, "band": _band_label(b, ar), "band_color": b.color if b else None,
			"answered": v["answered"], "total": v["total"]})
		v["pct"] = pct
	for name, v in topics.items():
		pct = v["earned"] / v["possible"] * 100 if v["possible"] else 0
		b = band_for(pct)
		doc.append("results", {"result_level": "Topic", "section": v["section"], "topic": name, "label": tlabel.get(name, name),
			"earned": v["earned"], "possible": v["possible"], "percentage": pct, "band": _band_label(b, ar), "band_color": b.color if b else None,
			"answered": v["answered"], "total": v["total"]})

	doc.rollup_method = s.rollup_method or "Pooled Points"
	if doc.rollup_method == "Weighted Section Average":
		live = [v for v in sections.values() if v["possible"]]
		wsum = sum(v["weight"] for v in live)
		overall = sum(v["pct"] * v["weight"] for v in live) / wsum if wsum else 0
		doc.points_earned = sum(v["earned"] for v in sections.values())
		doc.points_possible = sum(v["possible"] for v in sections.values())
	else:
		doc.points_earned = sum(v["earned"] * v["weight"] for v in sections.values())
		doc.points_possible = sum(v["possible"] * v["weight"] for v in sections.values())
		overall = doc.points_earned / doc.points_possible * 100 if doc.points_possible else 0
	b = band_for(overall)
	doc.overall_percentage = overall
	doc.maturity_band = _band_label(b, ar)
	doc.band_color = b.color if b else None
	doc.question_count = len(doc.answers)
	doc.answered_count = answered
	doc.na_count = na


def _band_label(b, ar=False):
	if not b:
		return None
	return (b.band_label_ar or b.band_label) if ar else b.band_label


def validate_complete(doc):
	"""Hard rule: no blank answers on a submitted, reviewed or closed assessment.

	Runs on every save once the assessment has left Draft, so answers cannot be blanked later from the desk either.
	An answer that is not a valid option (or N/A where the question does not allow it) is cleared by compute()
	and therefore also counts as blank here.
	"""
	if not doc.answers:
		frappe.throw(_("This assessment has no questions. Rebuild the questionnaire before submitting."), title=_("Incomplete"))
	missing = [r for r in doc.answers if not (r.selected_value or "").strip()]
	if missing:
		codes = ", ".join(r.question_code for r in missing[:15]) + (" …" if len(missing) > 15 else "")
		frappe.throw(
			_("Answer all questions before submitting. {0} left, starting with {1}.").format(len(missing), missing[0].question_code)
			+ "<br><small>" + codes + "</small>",
			title=_("Incomplete"),
		)


# ---------------------------------------------------------------- report payload
def build_report(doc):
	s = settings()
	ar = doc.language == "ar"
	pick = lambda en, a: (a or en) if ar else en
	bands = sorted(s.bands, key=lambda b: b.min_pct)
	band = next((b for b in bands if _band_label(b, ar) == doc.maturity_band), None)
	brand = frappe.get_cached_doc("GRC Maturity Brand", doc.brand) if doc.brand else None
	cat = get_catalog()
	slabel = {x["name"]: pick(x["section_label"], x["section_label_ar"]) for x in cat["sections"]}
	tlabel = {x["name"]: pick(x["topic_label"], x["topic_label_ar"]) for x in cat["topics"]}
	nat = frappe.get_cached_doc("GRC Maturity Nationality", doc.company_nationality)
	sector = frappe.get_cached_doc("GRC Maturity Industry Sector", doc.industry_sector)
	ind = frappe.get_cached_doc("GRC Maturity Industry Type", doc.industry_type)
	reg_ar = dict(frappe.get_all("GRC Maturity Regulator", fields=["name", "regulator_name_ar"], as_list=True)) if ar else {}
	return {
		"id": doc.name, "key": doc.access_key, "status": doc.status, "date": str(doc.submitted_on or doc.modified),
		"overall": round(doc.overall_percentage or 0, 1), "band": doc.maturity_band, "band_key": band.band_key if band else "",
		"band_color": doc.band_color, "band_icon": band.icon if band else "",
		"earned": round(doc.points_earned or 0, 2), "possible": round(doc.points_possible or 0, 2),
		"answered": doc.answered_count, "total": doc.question_count, "na": doc.na_count, "rollup": doc.rollup_method,
		"profile": {
			"org": doc.organization_name, "industry": pick(ind.industry_type, ind.industry_type_ar),
			"sector": doc.sector_other or pick(sector.sector_name, sector.sector_name_ar),
			"nationality": pick(nat.nationality, nat.nationality_ar), "cr": doc.cr_number,
			"legal_form": doc.legal_form, "entity_size": doc.entity_size,
			"license_na": doc.license_na, "license_text": doc.license_types_text,
			"licenses": [{"name": l.license_name, "type": l.license_type, "valid": l.is_valid, "exp": str(l.expiry_date or "")} for l in doc.licenses],
			"regulators": [{"name": reg_ar.get(r.regulator) or r.regulator, "response": r.response or "—"} for r in doc.regulators],
			"other_regulator": doc.other_regulator,
		},
		"sections": [_res(r) for r in doc.results if r.result_level == "Section"],
		"topics": [{**_res(r), "section_label": slabel.get(r.section, r.section)} for r in doc.results if r.result_level == "Topic"],
		"questions": [{
			"code": a.question_code, "text": a.question_text, "value": a.selected_value or "", "label": a.selected_label or "",
			"score": None if a.is_na else a.points, "max": a.max_points,
			"category": slabel.get(a.section, a.section) + (" · " + tlabel.get(a.topic, a.topic) if a.topic else ""),
		} for a in doc.answers],
		"roadmap": [{"code": a.question_code, "text": a.question_text, "current": a.selected_label, "current_desc": a.selected_description,
			"target": a.target_description, "category": slabel.get(a.section, a.section)} for a in doc.answers if a.target_description],
		"bands": [{"label": _band_label(b, ar), "min": b.min_pct, "max": b.max_pct, "color": b.color, "icon": b.icon,
			"text": pick(b.interpretation, b.interpretation_ar)} for b in bands],
		"disclaimer": pick(brand.report_disclaimer, brand.report_disclaimer_ar) if brand else "",
		"consultant_notes": doc.consultant_notes if doc.status in ("Reviewed", "Closed") else "",
	}


def _res(r):
	return {"label": r.label, "pct": round(r.percentage or 0, 1), "earned": round(r.earned or 0, 2), "possible": round(r.possible or 0, 2),
		"band": r.band, "color": r.band_color, "answered": r.answered, "total": r.total, "weight": r.weight}
