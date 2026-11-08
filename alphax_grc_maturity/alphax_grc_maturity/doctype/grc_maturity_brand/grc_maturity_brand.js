// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
frappe.ui.form.on("GRC Maturity Brand", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.route_slug) {
			frm.add_custom_button(__("Open Assessment Page"), () => {
				window.open(`/grc-assessment?b=${encodeURIComponent(frm.doc.route_slug)}`, "_blank");
			});
		}
	},
});
