// Copyright (c) 2026, IRSAA Business Solution (AlphaX)
frappe.query_reports["GRC Maturity Summary"] = {
	filters: [
		{ fieldname: "from_date", label: __("From"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To"), fieldtype: "Date" },
		{ fieldname: "industry_type", label: __("Industry Type"), fieldtype: "Link", options: "GRC Maturity Industry Type" },
		{ fieldname: "industry_sector", label: __("Industry Sector"), fieldtype: "Link", options: "GRC Maturity Industry Sector",
		  get_query: () => { const i = frappe.query_report.get_filter_value("industry_type"); return { filters: i ? { industry_type: i } : {} }; } },
		{ fieldname: "company_nationality", label: __("Company Nationality"), fieldtype: "Link", options: "GRC Maturity Nationality" },
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nDraft\nSubmitted\nReviewed\nClosed" },
		{ fieldname: "brand", label: __("Brand"), fieldtype: "Link", options: "GRC Maturity Brand" },
	],
};
