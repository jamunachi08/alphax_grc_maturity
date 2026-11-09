# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
import json

import frappe

from alphax_grc_maturity.engine.resolver import build_context, get_catalog, resolve_questions

ROLES = ("System Manager", "GRC Maturity Manager")


@frappe.whitelist()
def preview_resolution(context):
	frappe.only_for(ROLES + ("GRC Maturity Consultant",))
	c = json.loads(context) if isinstance(context, str) else context
	ctx = build_context(
		industry_type=c.get("industry_type"), industry_sector=c.get("industry_sector"),
		company_nationality=c.get("company_nationality"), legal_form=c.get("legal_form"),
		entity_size=c.get("entity_size"), license_types=[c.get("license_type")] if c.get("license_type") else [],
		regulators_yes=[c.get("regulator")] if c.get("regulator") else [],
	)
	questions, profiles = resolve_questions(ctx)
	cat = get_catalog()
	sl = {s["name"]: s["section_label"] for s in cat["sections"]}
	tl = {t["name"]: t["topic_label"] for t in cat["topics"]}
	return {
		"profiles": profiles, "question_count": len(questions),
		"questions": [{
			"code": q["code"], "scope": q["scope"], "section_label": sl.get(q["section"]), "topic_label": tl.get(q["topic"]),
			"section_weight": q["section_weight"], "topic_weight": q["topic_weight"], "question_weight": q["question_weight"],
			"weight": round(q["section_weight"] * q["weight"], 4), "weight_source": q["weight_source"],
		} for q in questions],
	}


@frappe.whitelist()
def run_seeder():
	frappe.only_for(ROLES)
	from alphax_grc_maturity.setup.seed import seed

	seed(force=True)


@frappe.whitelist()
def recalculate_all():
	"""Re-score every assessment with the current scale, bands and roll-up (weights stay as snapshotted)."""
	frappe.only_for(ROLES)
	n = 0
	for name in frappe.get_all("GRC Maturity Assessment", pluck="name"):
		try:
			doc = frappe.get_doc("GRC Maturity Assessment", name)
			doc.flags.ignore_permissions = True
			doc.save()
			n += 1
		except Exception:
			frappe.log_error(title=f"GRC Maturity: recalculation failed for {name}")
	frappe.db.commit()
	return n
