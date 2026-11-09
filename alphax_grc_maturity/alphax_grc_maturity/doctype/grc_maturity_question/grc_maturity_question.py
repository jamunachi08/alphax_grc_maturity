# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GRCMaturityQuestion(Document):
	def validate(self):
		from alphax_grc_maturity.engine.resolver import DIMENSION_DOCTYPE

		if self.topic:
			topic_section = frappe.db.get_value("GRC Maturity Topic", self.topic, "section")
			if topic_section != self.section:
				frappe.throw(_("Topic {0} belongs to section {1}.").format(self.topic, topic_section))
		seen = set()
		for opt in self.options:
			if opt.option_value in seen:
				frappe.throw(_("Option value {0} is repeated.").format(opt.option_value))
			if (opt.option_value or "").upper() == "NA":
				frappe.throw(_("Do not add an NA option. Tick 'Allow N/A' instead."))
			seen.add(opt.option_value)
		for rule in self.rules:
			rule.value_doctype = DIMENSION_DOCTYPE.get(rule.dimension)
		if self.scope == "Conditional" and not any(r.rule_type == "Include" for r in self.rules):
			frappe.throw(_("A Conditional question needs at least one Include rule."))
		if self.replaces_question == self.name:
			frappe.throw(_("A question cannot replace itself."))
		if (self.default_weight or 0) < 0:
			frappe.throw(_("Weight cannot be negative."))

	def on_update(self):
		from alphax_grc_maturity.engine.resolver import clear_cache

		clear_cache()
