// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
frappe.ui.form.on("GRC Maturity Weightage Profile", {
	refresh(frm) {
		if (frm.doc.is_global) {
			frm.dashboard.set_headline(__("Global profile: the fallback for every weight that no specific profile sets."));
		}
		frm.add_custom_button(__("Preview Resolution"), () => alphax_grc_maturity_preview(frm));
	},
	is_global(frm) {
		if (frm.doc.is_global) {
			["industry_type","industry_sector","company_nationality","license_type","regulator","legal_form","entity_size"].forEach(f => frm.set_value(f, ""));
		}
	},
	industry_type(frm) {
		frm.set_query("industry_sector", () => ({ filters: { industry_type: frm.doc.industry_type || undefined } }));
	},
	onload(frm) {
		frm.set_query("industry_sector", () => ({ filters: frm.doc.industry_type ? { industry_type: frm.doc.industry_type } : {} }));
		frm.set_query("topic", "lines", (doc, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return { filters: row.section ? { section: row.section } : {} };
		});
	},
});

function alphax_grc_maturity_preview(frm) {
	const d = new frappe.ui.Dialog({
		title: __("Preview: questions and weights for a profile"),
		size: "extra-large",
		fields: [
			{ fieldname: "industry_type", label: __("Industry Type"), fieldtype: "Link", options: "GRC Maturity Industry Type", default: frm.doc.industry_type },
			{ fieldname: "industry_sector", label: __("Industry Sector"), fieldtype: "Link", options: "GRC Maturity Industry Sector", default: frm.doc.industry_sector,
			  get_query: () => ({ filters: d.get_value("industry_type") ? { industry_type: d.get_value("industry_type") } : {} }) },
			{ fieldtype: "Column Break" },
			{ fieldname: "company_nationality", label: __("Company Nationality"), fieldtype: "Link", options: "GRC Maturity Nationality", default: frm.doc.company_nationality },
			{ fieldname: "license_type", label: __("License Type"), fieldtype: "Link", options: "GRC Maturity License Type", default: frm.doc.license_type },
			{ fieldtype: "Column Break" },
			{ fieldname: "legal_form", label: __("Legal Form"), fieldtype: "Link", options: "GRC Maturity Legal Form", default: frm.doc.legal_form },
			{ fieldname: "entity_size", label: __("Entity Size"), fieldtype: "Link", options: "GRC Maturity Entity Size", default: frm.doc.entity_size },
			{ fieldtype: "Section Break" },
			{ fieldname: "out", fieldtype: "HTML" },
		],
		primary_action_label: __("Resolve"),
		primary_action(v) {
			frappe.call({
				method: "alphax_grc_maturity.api.admin.preview_resolution",
				args: { context: v },
				callback(r) {
					const m = r.message || {};
					const esc = frappe.utils.escape_html;
					let h = `<p class="text-muted">${__("Profiles in order")}: ${(m.profiles || []).map(esc).join(" → ") || __("none")}</p>`;
					h += `<p>${__("Questions")}: <b>${m.question_count}</b></p><div style="max-height:420px;overflow:auto"><table class="table table-bordered table-sm"><thead><tr><th>${__("Code")}</th><th>${__("Section")}</th><th>${__("Topic")}</th><th>${__("Section W")}</th><th>${__("Topic W")}</th><th>${__("Question W")}</th><th>${__("Effective")}</th><th>${__("Source")}</th></tr></thead><tbody>`;
					(m.questions || []).forEach(q => {
						h += `<tr><td>${esc(q.code)}${q.scope === "Conditional" ? " <span class='indicator-pill blue'>C</span>" : ""}</td><td>${esc(q.section_label)}</td><td>${esc(q.topic_label || "")}</td><td>${q.section_weight}</td><td>${q.topic_weight}</td><td>${q.question_weight}</td><td><b>${q.weight}</b></td><td class="small">${esc(q.weight_source)}</td></tr>`;
					});
					h += "</tbody></table></div>";
					d.fields_dict.out.$wrapper.html(h);
				},
			});
		},
	});
	d.show();
}
