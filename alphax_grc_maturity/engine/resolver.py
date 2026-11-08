# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
"""Resolves which questions apply, which regulators to ask about and which weights to use.

Resolution order for every weight (section, topic, question) is the same:
the most specific matching Weightage Profile that sets it wins, then the next one,
ending with the Global profile, then 1 (or the question's default weight).
"""

import hashlib
import json

import frappe

CACHE_KEYS = ("axg:catalog", "axg:profiles", "axg:regulators")

DIMENSION_DOCTYPE = {
	"Industry Type": "GRC Maturity Industry Type",
	"Industry Sector": "GRC Maturity Industry Sector",
	"Company Nationality": "GRC Maturity Nationality",
	"License Type": "GRC Maturity License Type",
	"Regulator": "GRC Maturity Regulator",
	"Legal Form": "GRC Maturity Legal Form",
	"Entity Size": "GRC Maturity Entity Size",
}
DIMENSION_KEY = {
	"Industry Type": "industry_type",
	"Industry Sector": "industry_sector",
	"Company Nationality": "company_nationality",
	"License Type": "license_types",
	"Regulator": "regulators",
	"Legal Form": "legal_form",
	"Entity Size": "entity_size",
}
PROFILE_SCOPE = {
	"industry_sector": "industry_sector",
	"industry_type": "industry_type",
	"license_type": "license_types",
	"regulator": "regulators",
	"company_nationality": "company_nationality",
	"legal_form": "legal_form",
	"entity_size": "entity_size",
}


def clear_cache():
	for key in CACHE_KEYS:
		frappe.cache.delete_value(key)


# ---------------------------------------------------------------- context
def build_context(industry_type=None, industry_sector=None, company_nationality=None, legal_form=None,
		entity_size=None, license_types=None, regulators_yes=None):
	settings = frappe.get_cached_doc("GRC Maturity Settings")
	return {
		"industry_type": industry_type or None,
		"industry_sector": industry_sector or None,
		"company_nationality": company_nationality or None,
		"legal_form": legal_form or None,
		"entity_size": entity_size or None,
		"license_types": sorted({l for l in (license_types or []) if l}),
		"regulators": sorted({r for r in (regulators_yes or []) if r})
		if settings.regulator_answers_drive_questions else [],
	}


def context_from_doc(doc):
	return build_context(
		industry_type=doc.industry_type,
		industry_sector=doc.industry_sector,
		company_nationality=doc.company_nationality,
		legal_form=doc.legal_form,
		entity_size=doc.entity_size,
		license_types=[] if doc.license_na else [l.license_type for l in doc.licenses if l.license_type],
		regulators_yes=[r.regulator for r in doc.regulators if r.response == "Yes"],
	)


def context_hash(ctx):
	return hashlib.sha1(json.dumps(ctx, sort_keys=True).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- catalog
def get_catalog():
	data = frappe.cache.get_value("axg:catalog")
	if data:
		return data
	sections = frappe.get_all(
		"GRC Maturity Section", filters={"enabled": 1},
		fields=["name", "section_label", "section_label_ar", "sequence", "description"], order_by="sequence asc, name asc",
	)
	topics = frappe.get_all(
		"GRC Maturity Topic", filters={"enabled": 1},
		fields=["name", "section", "topic_label", "topic_label_ar", "sequence"], order_by="sequence asc, name asc",
	)
	questions = []
	for name in frappe.get_all("GRC Maturity Question", filters={"enabled": 1}, pluck="name", order_by="sequence asc, name asc"):
		q = frappe.get_doc("GRC Maturity Question", name)
		questions.append({
			"name": q.name, "code": q.question_code, "section": q.section, "topic": q.topic, "sequence": q.sequence,
			"scope": q.scope, "text": q.question_text, "text_ar": q.question_text_ar, "guidance": q.guidance,
			"framework_refs": q.framework_refs, "is_mandatory": q.is_mandatory, "allow_na": q.allow_na,
			"default_weight": q.default_weight if q.default_weight is not None else 1,
			"replaces": q.replaces_question,
			"options": [
				{"value": o.option_value, "label": o.option_label, "label_ar": o.option_label_ar, "desc": o.description,
				 "desc_ar": o.description_ar, "points": o.points, "rec": o.recommendation, "rec_ar": o.recommendation_ar}
				for o in q.options
			],
			"rules": [{"dimension": r.dimension, "type": r.rule_type, "value": r.value} for r in q.rules],
		})
	section_seq = {s.name: i for i, s in enumerate(sections)}
	topic_seq = {t.name: i for i, t in enumerate(topics)}
	questions = [q for q in questions if q["section"] in section_seq and (not q["topic"] or q["topic"] in topic_seq)]
	questions.sort(key=lambda q: (section_seq[q["section"]], topic_seq.get(q["topic"], -1), q["sequence"] or 0, q["code"]))
	data = {
		"sections": [dict(s) for s in sections],
		"topics": [dict(t) for t in topics],
		"questions": questions,
	}
	frappe.cache.set_value("axg:catalog", data, expires_in_sec=3600)
	return data


def get_profiles():
	data = frappe.cache.get_value("axg:profiles")
	if data is not None:
		return data
	data = []
	for name in frappe.get_all("GRC Maturity Weightage Profile", filters={"enabled": 1}, pluck="name"):
		p = frappe.get_doc("GRC Maturity Weightage Profile", name)
		lines = {}
		for l in p.lines:
			target = l.get(l.applies_to.lower())
			if target:
				lines[f"{l.applies_to}|{target}"] = l.weight
		data.append({
			"name": p.name, "is_global": p.is_global, "priority": p.priority or 0, "specificity": p.specificity or 0,
			"scope": {f: p.get(f) for f in PROFILE_SCOPE if p.get(f)}, "lines": lines,
		})
	frappe.cache.set_value("axg:profiles", data, expires_in_sec=3600)
	return data


# ---------------------------------------------------------------- matching
def _ctx_has(ctx, key, value):
	have = ctx.get(key)
	if isinstance(have, list):
		return value in have
	return have == value


def question_applies(q, ctx):
	for r in q["rules"]:
		if r["type"] == "Exclude" and _ctx_has(ctx, DIMENSION_KEY[r["dimension"]], r["value"]):
			return False
	if q["scope"] != "Conditional":
		return True
	groups = {}
	for r in q["rules"]:
		if r["type"] == "Include":
			groups.setdefault(r["dimension"], []).append(r["value"])
	if not groups:
		return False
	return all(any(_ctx_has(ctx, DIMENSION_KEY[d], v) for v in values) for d, values in groups.items())


def matching_profiles(ctx):
	out = []
	for p in get_profiles():
		if p["is_global"]:
			out.append(p)
			continue
		if all(_ctx_has(ctx, PROFILE_SCOPE[f], v) for f, v in p["scope"].items()):
			out.append(p)
	out.sort(key=lambda p: (0 if p["is_global"] else 1, p["specificity"], p["priority"]), reverse=True)
	return out


def _pick(profiles, key, fallback):
	for p in profiles:
		if key in p["lines"]:
			return p["lines"][key], p["name"]
	return fallback, None


# ---------------------------------------------------------------- public resolution
def resolve_questions(ctx):
	"""Return the list of question dicts (copies) that apply to the context, with weights attached."""
	catalog = get_catalog()
	applicable = [q for q in catalog["questions"] if question_applies(q, ctx)]
	replaced = {q["replaces"] for q in applicable if q["replaces"]}
	applicable = [dict(q) for q in applicable if q["name"] not in replaced]
	profiles = matching_profiles(ctx)
	for q in applicable:
		sw, s_src = _pick(profiles, f"Section|{q['section']}", 1.0)
		tw, t_src = _pick(profiles, f"Topic|{q['topic']}", 1.0) if q["topic"] else (1.0, None)
		qw, q_src = _pick(profiles, f"Question|{q['name']}", q["default_weight"])
		q["section_weight"] = float(sw)
		q["topic_weight"] = float(tw)
		q["question_weight"] = float(qw)
		q["weight"] = float(tw) * float(qw)
		q["weight_source"] = " · ".join(
			f"{k}:{v}" for k, v in (("S", s_src), ("T", t_src), ("Q", q_src or "default")) if v
		)
	return applicable, [p["name"] for p in profiles]


def resolve_regulators(ctx):
	"""General regulators + sector list (or industry list) + nationality extras, de-duplicated in order."""
	out, seen = [], set()

	def add(names, source):
		for n in names:
			if n and n not in seen:
				seen.add(n)
				out.append({"regulator": n, "source": source})

	add(frappe.get_all("GRC Maturity Regulator", filters={"is_general": 1, "enabled": 1}, pluck="name", order_by="creation asc"), "General")
	sector = frappe.get_cached_doc("GRC Maturity Industry Sector", ctx["industry_sector"]) if ctx.get("industry_sector") and frappe.db.exists("GRC Maturity Industry Sector", ctx["industry_sector"]) else None
	if sector and sector.has_own_regulators:
		add([r.regulator for r in sector.regulators], "Sector")
	elif ctx.get("industry_type") and frappe.db.exists("GRC Maturity Industry Type", ctx["industry_type"]):
		add([r.regulator for r in frappe.get_cached_doc("GRC Maturity Industry Type", ctx["industry_type"]).regulators], "Industry")
	if ctx.get("company_nationality") and frappe.db.exists("GRC Maturity Nationality", ctx["company_nationality"]):
		add([r.regulator for r in frappe.get_cached_doc("GRC Maturity Nationality", ctx["company_nationality"]).regulators], "Nationality")
	return out


def structure(questions, lang="en", show_weights=False):
	"""Group resolved questions into sections → topics for the portal."""
	catalog = get_catalog()
	ar = lang == "ar"
	pick = lambda en, a: (a or en) if ar else en
	topics = {t["name"]: t for t in catalog["topics"]}
	sections = []
	for s in catalog["sections"]:
		qs = [q for q in questions if q["section"] == s["name"]]
		if not qs:
			continue
		groups = []
		for q in qs:
			key = q["topic"] or ""
			if not groups or groups[-1]["key"] != key:
				t = topics.get(key)
				groups.append({"key": key, "label": pick(t["topic_label"], t["topic_label_ar"]) if t else "", "questions": []})
			item = {
				"name": q["name"], "code": q["code"], "text": pick(q["text"], q["text_ar"]), "guidance": q["guidance"],
				"mandatory": q["is_mandatory"], "allow_na": q["allow_na"], "conditional": q["scope"] == "Conditional",
				"options": [{"value": o["value"], "label": pick(o["label"], o["label_ar"]), "desc": pick(o["desc"], o["desc_ar"])} for o in q["options"]],
			}
			if show_weights:
				item["weight"] = round(q["section_weight"] * q["weight"], 3)
			groups[-1]["questions"].append(item)
		sections.append({"id": s["name"], "label": pick(s["section_label"], s["section_label_ar"]), "topics": groups})
	return sections


def on_master_change(doc, method=None):
	clear_cache()
