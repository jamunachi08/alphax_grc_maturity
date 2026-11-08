// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
frappe.ui.form.on("GRC Maturity Registration", {
	onload(frm) {
		frm.set_query("industry_sector", () => ({ filters: frm.doc.industry_type ? { industry_type: frm.doc.industry_type } : {} }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		const act = (method, label) => frm.add_custom_button(__(label), () =>
			frappe.confirm(__("{0} this registration?", [__(label)]), () => frm.call(method).then(() => frm.reload_doc())), __("Actions"));
		if (["Pending Approval", "Rejected", "Disabled"].includes(frm.doc.status) && frm.doc.email_verified) act("approve", "Approve");
		if (["Pending Approval", "Pending Verification"].includes(frm.doc.status)) act("reject", "Reject");
		if (frm.doc.status === "Active") act("disable", "Disable");
		if (frm.doc.user) frm.add_custom_button(__("Assessments"), () => frappe.set_route("List", "GRC Maturity Assessment", { registration: frm.doc.name }));
	},
});
