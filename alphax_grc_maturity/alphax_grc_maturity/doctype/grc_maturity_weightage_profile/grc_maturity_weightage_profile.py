# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturityWeightageProfile(Document):
	SPECIFICITY = {
		"industry_sector": 64,
		"industry_type": 32,
		"license_type": 16,
		"regulator": 8,
		"company_nationality": 4,
		"legal_form": 2,
		"entity_size": 1,
	}

	def validate(self):
		if self.is_global:
			for f in self.SPECIFICITY:
				self.set(f, None)
			other = frappe.db.get_value(
				"GRC Maturity Weightage Profile", {"is_global": 1, "name": ("!=", self.name)}, "name"
			)
			if other:
				frappe.throw(_("Profile {0} is already the global profile.").format(other))
		elif not any(self.get(f) for f in self.SPECIFICITY):
			frappe.throw(_("Set at least one scope field, or tick Global Profile."))
		if self.industry_sector and self.industry_type:
			sector_industry = frappe.db.get_value("GRC Maturity Industry Sector", self.industry_sector, "industry_type")
			if sector_industry != self.industry_type:
				frappe.throw(_("Sector {0} does not belong to industry {1}.").format(self.industry_sector, self.industry_type))
		self.specificity = sum(v for f, v in self.SPECIFICITY.items() if self.get(f))
		seen = set()
		for line in self.lines:
			target = line.get(line.applies_to.lower())
			if not target:
				frappe.throw(_("Row {0}: choose the {1}.").format(line.idx, line.applies_to))
			for f in ("section", "topic", "question"):
				if f != line.applies_to.lower():
					line.set(f, None)
			key = (line.applies_to, target)
			if key in seen:
				frappe.throw(_("Row {0}: {1} {2} is weighted twice.").format(line.idx, line.applies_to, target))
			seen.add(key)
			if (line.weight or 0) < 0:
				frappe.throw(_("Row {0}: weight cannot be negative.").format(line.idx))

	def on_update(self):
		from alphax_grc_maturity.engine.resolver import clear_cache

		clear_cache()

	def on_trash(self):
		from alphax_grc_maturity.engine.resolver import clear_cache

		clear_cache()
