# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentPlan(Document):
	def after_insert(self):
		self.log_activity("created")

	def on_update(self):
		# avoid noisy log on first insert save cycle
		if self.is_new():
			return
		self.log_activity("updated")

	def on_trash(self):
		self.log_activity("deleted")

	def get_linked_lead(self):
		"""
		Tries common link patterns to find the related CRM Lead.
		Adjust if your Payment Plan uses a different link field.
		"""
		# direct lead link
		if hasattr(self, "lead") and self.lead:
			return self.lead

		# generic reference pattern
		if (
			hasattr(self, "reference_doctype")
			and hasattr(self, "reference_docname")
			and self.reference_doctype == "CRM Lead"
			and self.reference_docname
		):
			return self.reference_docname

		# fallback common fieldnames
		for fieldname in ("crm_lead", "lead_name", "parent_lead"):
			if hasattr(self, fieldname) and getattr(self, fieldname):
				return getattr(self, fieldname)

		return None

	def log_activity(self, action):
		lead_name = self.get_linked_lead()
		if not lead_name or not frappe.db.exists("CRM Lead", lead_name):
			return

		lead = frappe.get_doc("CRM Lead", lead_name)
		full_name = frappe.utils.get_fullname(frappe.session.user)

		lead.add_comment(
			"Info",
			text=f"<b>{full_name}</b> {action} payment plan <b>{self.name}</b>",
		)