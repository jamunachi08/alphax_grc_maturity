# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	f = filters or {}
	cond = {}
	for key in ("industry_type", "industry_sector", "company_nationality", "status", "brand"):
		if f.get(key):
			cond[key] = f[key]
	if f.get("from_date") and f.get("to_date"):
		cond["creation"] = ("between", [f["from_date"], f["to_date"] + " 23:59:59"])
	sections = frappe.get_all("GRC Maturity Section", filters={"enabled": 1}, fields=["name", "section_label"], order_by="sequence asc")
	columns = [
		{"fieldname": "name", "label": _("Assessment"), "fieldtype": "Link", "options": "GRC Maturity Assessment", "width": 210},
		{"fieldname": "organization_name", "label": _("Organization"), "fieldtype": "Data", "width": 190},
		{"fieldname": "industry_type", "label": _("Industry"), "fieldtype": "Data", "width": 170},
		{"fieldname": "industry_sector", "label": _("Sector"), "fieldtype": "Data", "width": 190},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 90},
		{"fieldname": "overall_percentage", "label": _("Overall %"), "fieldtype": "Percent", "width": 95},
		{"fieldname": "maturity_band", "label": _("Level"), "fieldtype": "Data", "width": 90},
	] + [{"fieldname": f"s_{s.name}", "label": s.section_label, "fieldtype": "Percent", "width": 110} for s in sections]
	rows = frappe.get_all("GRC Maturity Assessment", filters=cond,
		fields=["name", "organization_name", "industry_type", "industry_sector", "status", "overall_percentage", "maturity_band"],
		order_by="creation desc", limit_page_length=0)
	if rows:
		res = frappe.get_all("GRC Maturity Assessment Result", filters={"parent": ("in", [r.name for r in rows]), "result_level": "Section"},
			fields=["parent", "section", "percentage"], limit_page_length=0)
		by = {}
		for r in res:
			by.setdefault(r.parent, {})[f"s_{r.section}"] = r.percentage
		for r in rows:
			r.update(by.get(r.name, {}))
	chart = None
	if rows:
		labels = [s.section_label for s in sections]
		vals = [round(sum(flt(r.get(f"s_{s.name}")) for r in rows) / len(rows), 1) for s in sections]
		chart = {"data": {"labels": labels, "datasets": [{"name": _("Average %"), "values": vals}]}, "type": "bar", "colors": ["#1e3a5f"]}
	bands = {}
	for r in rows:
		bands[r.maturity_band or _("Not scored")] = bands.get(r.maturity_band or _("Not scored"), 0) + 1
	summary = [{"value": len(rows), "label": _("Assessments"), "datatype": "Int"},
		{"value": round(sum(flt(r.overall_percentage) for r in rows) / len(rows), 1) if rows else 0, "label": _("Average score %"), "datatype": "Float"}]
	summary += [{"value": v, "label": k, "datatype": "Int"} for k, v in bands.items()]
	return columns, rows, None, chart, summary
