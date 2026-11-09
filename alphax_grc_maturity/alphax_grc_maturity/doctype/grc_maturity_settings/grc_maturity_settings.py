# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturitySettings(Document):
	def validate(self):
		bands = sorted(self.bands, key=lambda b: b.min_pct)
		for prev, cur in zip(bands, bands[1:]):
			if cur.min_pct <= prev.max_pct:
				frappe.throw(_("Maturity bands {0} and {1} overlap.").format(prev.band_label, cur.band_label))
		values = [s.option_value for s in self.answer_scale]
		if len(values) != len(set(values)):
			frappe.throw(_("Answer scale values must be unique."))

	def on_update(self):
		from alphax_grc_maturity.engine.resolver import clear_cache

		clear_cache()
