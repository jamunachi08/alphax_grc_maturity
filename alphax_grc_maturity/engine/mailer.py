# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
import frappe
from frappe import _


def queue_report_email(name, event="Submitted"):
	frappe.enqueue(
		"alphax_grc_maturity.engine.mailer.send_report_email",
		queue="short", name=name, event=event, enqueue_after_commit=True,
	)


def send_report_email(name, event="Submitted"):
	doc = frappe.get_doc("GRC Maturity Assessment", name)
	brand = frappe.get_doc("GRC Maturity Brand", doc.brand) if doc.brand else None
	if not brand:
		return
	hide = brand.hide_score_from_respondent and doc.status not in ("Reviewed", "Closed")
	lang = doc.language or "en"
	attachments = []
	if brand.attach_pdf:
		try:
			attachments.append(frappe.attach_print(
				"GRC Maturity Assessment", doc.name, print_format="GRC Maturity Report", file_name=doc.name, lang=lang
			))
		except Exception:
			frappe.log_error(title=f"GRC Maturity: PDF failed for {doc.name}")
	subject = (brand.email_subject or _("GRC Maturity Assessment report – {name}")).format(name=doc.name, org=doc.organization_name)
	sender = frappe.db.get_value("Email Account", brand.email_account, "email_id") if brand.email_account else None
	link = frappe.utils.get_url(f"/grc-assessment?b={brand.route_slug}&id={doc.name}&k={doc.access_key}")
	ctx = {"doc": doc, "brand": brand, "link": link, "hide": hide, "lang": lang}

	respondent_event = event in ("Submitted", "Manual") or (event == "Reviewed" and brand.hide_score_from_respondent)
	if brand.send_report_to_respondent and doc.contact_email and respondent_event:
		frappe.sendmail(
			recipients=[doc.contact_email], sender=sender, subject=subject,
			template="grc_maturity_report", args={**ctx, "internal": False},
			attachments=[] if hide else attachments,
			reference_doctype=doc.doctype, reference_name=doc.name, now=False,
		)
	internal = [n.email for n in brand.notify if event in ("Submitted", "Manual") or n.send_on == "Submit and Review"]
	if internal:
		frappe.sendmail(
			recipients=internal, sender=sender, subject=f"[{doc.status}] {subject}",
			template="grc_maturity_report", args={**ctx, "hide": False, "internal": True},
			attachments=attachments, reference_doctype=doc.doctype, reference_name=doc.name, now=False,
		)
	doc.db_set("report_emailed", 1, update_modified=False)
