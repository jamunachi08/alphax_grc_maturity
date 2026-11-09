// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
frappe.ui.form.on("GRC Maturity Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Open Assessment Page"), () => window.open("/grc-assessment", "_blank"));
		frm.add_custom_button(__("Re-run Seeder"), () => {
			frappe.confirm(__("Adds any missing standard masters, questions and themes. Records you edited are left as they are. Continue?"), () => {
				frappe.call({ method: "alphax_grc_maturity.api.admin.run_seeder", freeze: true, callback: () => frappe.show_alert({ message: __("Seeder finished"), indicator: "green" }) });
			});
		}, __("Tools"));
		frm.add_custom_button(__("Recalculate All Assessments"), () => {
			frappe.call({ method: "alphax_grc_maturity.api.admin.recalculate_all", freeze: true, callback: (r) => frappe.msgprint(__("Recalculated {0} assessments", [r.message])) });
		}, __("Tools"));
	},
});
