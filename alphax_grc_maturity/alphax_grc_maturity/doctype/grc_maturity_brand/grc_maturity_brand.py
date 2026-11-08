# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturityBrand(Document):
	def validate(self):
		import re

		self.route_slug = re.sub(r"[^a-z0-9-]+", "-", (self.route_slug or "").strip().lower()).strip("-")
		if not self.route_slug:
			frappe.throw(_("URL Key must contain letters or digits."))
