# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturityAssessment(Document):
	def autoname(self):
		from alphax_grc_maturity.engine.scoring import new_assessment_id

		self.name = new_assessment_id()

	def before_insert(self):
		if not self.access_key:
			from alphax_grc_maturity.engine.scoring import new_access_key

			self.access_key = new_access_key()
		if not self.brand:
			self.brand = frappe.db.get_single_value("GRC Maturity Settings", "default_brand")

	def validate(self):
		from alphax_grc_maturity.engine.scoring import validate_profile, sync_questionnaire, compute

		validate_profile(self)
		sync_questionnaire(self)
		compute(self)
		if self.status != "Draft":
			from alphax_grc_maturity.engine.scoring import validate_complete

			validate_complete(self)
			if not self.submitted_on:
				self.submitted_on = frappe.utils.now_datetime()
		if self.status == "Reviewed" and not self.reviewed_on:
			self.reviewed_on = frappe.utils.now_datetime()

	def on_update(self):
		before = self.get_doc_before_save()
		changed_to = lambda s: self.status == s and (not before or before.status != s)
		if changed_to("Submitted") or changed_to("Reviewed"):
			from alphax_grc_maturity.engine.mailer import queue_report_email

			queue_report_email(self.name, event=self.status)

	@frappe.whitelist()
	def rebuild_questionnaire(self):
		self.context_hash = None
		self.save()

	@frappe.whitelist()
	def send_report_email(self):
		from alphax_grc_maturity.engine.mailer import queue_report_email

		queue_report_email(self.name, event="Manual")

	@frappe.whitelist()
	def get_portal_link(self):
		slug = frappe.db.get_value("GRC Maturity Brand", self.brand, "route_slug") if self.brand else ""
		q = f"?id={self.name}&k={self.access_key}" + (f"&b={slug}" if slug else "")
		return frappe.utils.get_url("/grc-assessment" + q)
