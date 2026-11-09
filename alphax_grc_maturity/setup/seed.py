# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
"""Idempotent seeder. Inserts what is missing; never overwrites records an admin has edited."""

import json
import os

import frappe

SEED_VERSION = 5
HERE = os.path.join(os.path.dirname(__file__), "seed_data")
ROLES = ("GRC Maturity Manager", "GRC Maturity Consultant")
WEB_ROLES = ("GRC Maturity Respondent",)


def _data(name):
	with open(os.path.join(HERE, f"{name}.json"), encoding="utf-8") as f:
		return json.load(f)


def _links(rows):
	return [{"regulator": r} for r in rows if frappe.db.exists("GRC Maturity Regulator", r)]


def _insert(doctype, name, values):
	if frappe.db.exists(doctype, name):
		return False
	doc = frappe.get_doc({"doctype": doctype, **values})
	doc.flags.ignore_permissions = True
	doc.flags.ignore_links = False
	doc.insert()
	return True


def after_install():
	seed(force=True)


def after_migrate():
	seed()


def seed(force=False):
	current = frappe.db.get_single_value("GRC Maturity Settings", "seed_version") or 0
	if not force and current >= SEED_VERSION:
		return
	frappe.flags.in_axg_seed = True
	try:
		_roles()
		for r in _data("regulators"):
			_insert("GRC Maturity Regulator", r["regulator_name"], {**r, "enabled": 1})
		for i in _data("industries"):
			_insert("GRC Maturity Industry Type", i["industry_type"], {**i, "regulators": _links(i["regulators"])})
		for s in _data("sectors"):
			_insert("GRC Maturity Industry Sector", f"{s['industry_type']} | {s['sector_name']}", {**s, "regulators": _links(s["regulators"])})
		for n in _data("nationalities"):
			_insert("GRC Maturity Nationality", n["nationality"], {**n, "regulators": _links(n["regulators"])})
		for l in _data("license_types"):
			_insert("GRC Maturity License Type", l["license_type"], l)
		for l in _data("legal_forms"):
			_insert("GRC Maturity Legal Form", l["legal_form"], l)
		for e in _data("entity_sizes"):
			_insert("GRC Maturity Entity Size", e["entity_size"], e)
		for s in _data("sections"):
			_insert("GRC Maturity Section", s["section_id"], s)
		for t in _data("topics"):
			_insert("GRC Maturity Topic", f"{t['section']} | {t['topic_label']}", t)
		from alphax_grc_maturity.engine.resolver import DIMENSION_DOCTYPE

		for q in _data("questions") + _data("sample_questions"):
			for r in q.get("rules") or []:
				r["value_doctype"] = DIMENSION_DOCTYPE[r["dimension"]]
			_insert("GRC Maturity Question", q["question_code"], q)
		for t in _data("themes"):
			_insert("GRC Maturity Theme", t["theme_name"], t)
		for b in _data("brands"):
			if not _insert("GRC Maturity Brand", b["brand_name"], b):
				_fill_empty("GRC Maturity Brand", b["brand_name"], b,
					("registration_intro", "registration_intro_ar", "consent_text", "consent_text_ar"))
		for p in _data("profiles"):
			_insert("GRC Maturity Weightage Profile", p["profile_name"], p)
		_settings()
	finally:
		frappe.flags.in_axg_seed = False
	from alphax_grc_maturity.engine.resolver import clear_cache

	clear_cache()
	frappe.db.commit()


def _fill_empty(doctype, name, values, fields):
	"""Fill fields added in a later version on records that already exist, without touching edited values."""
	doc = frappe.get_doc(doctype, name)
	changed = False
	for f in fields:
		if not doc.get(f) and values.get(f):
			doc.set(f, values[f])
			changed = True
	if changed:
		doc.flags.ignore_permissions = True
		doc.save()


def _roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)
	for role in WEB_ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 0}).insert(ignore_permissions=True)


def _settings():
	s = frappe.get_single("GRC Maturity Settings")
	if not s.default_brand:
		s.default_brand = _data("brands")[0]["brand_name"]
	if not s.answer_scale:
		for r in _data("scale"):
			s.append("answer_scale", r)
	if not s.bands:
		for b in _data("bands"):
			s.append("bands", b)
	if not s.registration_mode:
		s.registration_mode = "Registration Required"
	for field, default in (
		("otp_expiry_minutes", 10), ("otp_max_attempts", 5), ("otp_resend_seconds", 60),
		("rollup_method", "Pooled Points"), ("default_language", "en"), ("license_mode", "Both"),
		("improvement_threshold", "A,B"), ("access_key_length", 8), ("max_saves_per_hour", 300), ("app_version_label", "v1.0"),
	):
		if not s.get(field):
			s.set(field, default)
	if not s.seed_version:
		for field in ("enable_arabic", "require_contact_email", "na_excluded",
				"ask_legal_form", "ask_entity_size", "ask_license_types", "ask_regulators"):
			s.set(field, 1)
	if (s.seed_version or 0) < 5:
		s.registration_require_mobile = 1
	s.seed_version = SEED_VERSION
	s.flags.ignore_permissions = True
	s.save()
