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

        message = (
                f"<b>{full_name}</b> {action} payment plan "
                f"<b>{self.name}</b>"
        )

        # detailed field tracking for updates
        if action == "updated":
                old_doc = self.get_doc_before_save()

                if old_doc:
                        tracked_fields = {
							"area": "Area",
							"price_per_m2": "Price per m²",
							"years": "Years",
							"total_price": "Total Price",

							"downpayment_percent": "Downpayment %",
							"total_downpayment_value": "Downpayment Value",

							"frequency": "Installment Frequency",
							"installment_type": "Installment Type",

							"maintenance_fee": "Maintenance Fee",
							"garden_price": "Garden Price",
							"roof_price": "Roof Price",
							"pool_price": "Pool Price",
					}
                        changes = []

                        def normalize(v):
                                if v in (None, ""):
                                        return "Empty"
                                return str(v)

                        for fieldname, label in tracked_fields.items():
                                old_val = normalize(old_doc.get(fieldname))
                                new_val = normalize(self.get(fieldname))

                                if old_val != new_val:
                                        changes.append(
                                                f"<b>{label}</b>: "
                                                f"{old_val} → {new_val}"
                                        )

                        if changes:
                                message += "<br>" + "<br>".join(changes)

        lead.add_comment(
                "Info",
                text=message,
        )