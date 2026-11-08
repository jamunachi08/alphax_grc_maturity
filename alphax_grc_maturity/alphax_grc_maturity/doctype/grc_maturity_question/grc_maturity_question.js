// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
const AXG_DIM_MAP = {
	"Industry Type": "GRC Maturity Industry Type",
	"Industry Sector": "GRC Maturity Industry Sector",
	"Company Nationality": "GRC Maturity Nationality",
	"License Type": "GRC Maturity License Type",
	"Regulator": "GRC Maturity Regulator",
	"Legal Form": "GRC Maturity Legal Form",
	"Entity Size": "GRC Maturity Entity Size",
};
frappe.ui.form.on("GRC Maturity Applicability Rule", {
	dimension(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "value_doctype", AXG_DIM_MAP[row.dimension] || "");
		frappe.model.set_value(cdt, cdn, "value", "");
	},
	rules_add(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.dimension) frappe.model.set_value(cdt, cdn, "value_doctype", AXG_DIM_MAP[row.dimension]);
	},
});
