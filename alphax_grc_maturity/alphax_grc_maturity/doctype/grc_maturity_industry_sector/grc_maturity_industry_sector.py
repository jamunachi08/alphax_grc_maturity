# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturityIndustrySector(Document):
	def autoname(self):
		self.name = f"{self.industry_type} | {self.sector_name}"

	def validate(self):
		if not self.has_own_regulators:
			self.set("regulators", [])
