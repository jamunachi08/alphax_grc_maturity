// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
frappe.ui.form.on("GRC Maturity Assessment", {
	onload(frm) {
		frm.set_query("industry_sector", () => ({ filters: frm.doc.industry_type ? { industry_type: frm.doc.industry_type } : {} }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		const color = frm.doc.band_color || "blue";
		if (frm.doc.maturity_band) {
			frm.dashboard.set_headline(`<span style="font-weight:600">${frappe.utils.escape_html(frm.doc.maturity_band)}</span> · ${format_number(frm.doc.overall_percentage, null, 1)}% · ${frm.doc.answered_count}/${frm.doc.question_count} ${__("answered")}`);
		}
		frm.add_custom_button(__("Rebuild Questionnaire"), () => {
			frappe.confirm(__("Re-resolve questions and weights for this profile? Existing answers are kept for questions that still apply."), () => {
				frm.call("rebuild_questionnaire").then(() => frm.reload_doc());
			});
		}, __("Actions"));
		frm.add_custom_button(__("Email Report"), () => frm.call("send_report_email").then(() => frappe.show_alert({ message: __("Queued"), indicator: "green" })), __("Actions"));
		if (frm.doc.status === "Submitted") {
			frm.add_custom_button(__("Mark Reviewed"), () => { frm.set_value("status", "Reviewed"); frm.save(); }, __("Actions"));
		}
		frm.add_custom_button(__("Open Respondent View"), () => {
			frm.call("get_portal_link").then(r => window.open(r.message, "_blank"));
		}, __("Actions"));
	},
});
