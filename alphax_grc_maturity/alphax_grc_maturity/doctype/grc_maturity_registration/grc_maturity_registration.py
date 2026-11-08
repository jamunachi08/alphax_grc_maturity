# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturityRegistration(Document):
	def validate(self):
		self.email = (self.email or "").strip().lower()
		if self.industry_sector and self.industry_type:
			if frappe.db.get_value("GRC Maturity Industry Sector", self.industry_sector, "industry_type") != self.industry_type:
				frappe.throw(_("Sector {0} does not belong to industry {1}.").format(self.industry_sector, self.industry_type))

	@frappe.whitelist()
	def approve(self):
		from alphax_grc_maturity.api.registration import set_registration_status

		set_registration_status(self, "Active")

	@frappe.whitelist()
	def reject(self):
		from alphax_grc_maturity.api.registration import set_registration_status

		set_registration_status(self, "Rejected")

	@frappe.whitelist()
	def disable(self):
		from alphax_grc_maturity.api.registration import set_registration_status

		set_registration_status(self, "Disabled")
