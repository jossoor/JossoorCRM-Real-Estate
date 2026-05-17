# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

PROJECT_NAME_MAX = 140
DESCRIPTION_MAX  = 2000
PAYMENT_PLAN_MAX = 1000

# Canonical casing that Frappe stores — must match the JSON options exactly.
VALID_FURNISHING = {"Unfurnished", "Semi-Furnished", "Fully-Furnished"}
VALID_STATUS = {
    "Available", "On Lease", "On Sale", "Reserved",
    "Off lease in 3 months", "Leased", "Sold", "Removed",
}

# Map common user-submitted variants → canonical stored value (case-insensitive key)
FURNISHING_ALIAS = {
    "unfurnished":    "Unfurnished",
    "semi-furnished": "Semi-Furnished",
    "semi furnished": "Semi-Furnished",
    "semifurnished":  "Semi-Furnished",
    "fully-furnished":"Fully-Furnished",
    "fully furnished":"Fully-Furnished",
    "fullyfurnished": "Fully-Furnished",
}

STATUS_ALIAS = {
    "available":               "Available",
    "on lease":                "On Lease",
    "on sale":                 "On Sale",
    "reserved":                "Reserved",
    "off lease in 3 months":   "Off lease in 3 months",
    "leased":                  "Leased",
    "sold":                    "Sold",
    "removed":                 "Removed",
    # legacy / typo variants that were causing the 500
    "leased sold removed":     "Removed",
    "leasedsoldremoved":       "Removed",
}


class RealEstateProject(Document):

	# ------------------------------------------------------------------
	# Lifecycle hooks
	# ------------------------------------------------------------------

	def before_insert(self):
		self._normalize_selects()

	def validate(self):
		self._normalize_selects()
		self._validate_project_name()
		self._validate_prices()
		self._validate_lengths()

	# ------------------------------------------------------------------
	# Normalisation helpers
	# ------------------------------------------------------------------

	def _normalize_selects(self):
		"""
		Fix case mismatches sent by the frontend before Frappe validates
		the Select field options (which are case-sensitive).
		"""
		# --- furnishing ---
		raw = (self.furnishing or "").strip()
		if raw:
			canonical = FURNISHING_ALIAS.get(raw.lower())
			if canonical:
				self.furnishing = canonical
			elif raw not in VALID_FURNISHING:
				frappe.throw(
					_("Invalid furnishing value: {0}. Allowed values: {1}").format(
						raw, ", ".join(sorted(VALID_FURNISHING))
					)
				)

		# --- status ---
		raw_status = (self.status or "").strip()
		if raw_status:
			canonical_s = STATUS_ALIAS.get(raw_status.lower())
			if canonical_s:
				self.status = canonical_s
			elif raw_status not in VALID_STATUS:
				frappe.throw(
					_("Invalid status value: {0}. Allowed values: {1}").format(
						raw_status, ", ".join(sorted(VALID_STATUS))
					)
				)

	# ------------------------------------------------------------------
	# Field-level validations
	# ------------------------------------------------------------------

	def _validate_project_name(self):
		name = (self.project_name or "").strip()
		if not name:
			frappe.throw(_("Project Name is required."))
		if len(name) > PROJECT_NAME_MAX:
			frappe.throw(
				_("Project Name must not exceed {0} characters (currently {1}).").format(
					PROJECT_NAME_MAX, len(name)
				)
			)

	def _validate_prices(self):
		min_p = self.min_price or 0
		max_p = self.max_price or 0
		if min_p and max_p and min_p > max_p:
			frappe.throw(
				_("Min Price ({0}) cannot be greater than Max Price ({1}).").format(
					frappe.format_value(min_p, {"fieldtype": "Currency"}),
					frappe.format_value(max_p, {"fieldtype": "Currency"}),
				)
			)

	def _validate_lengths(self):
		desc = self.description or ""
		if len(desc) > DESCRIPTION_MAX:
			frappe.throw(
				_("Description must not exceed {0} characters (currently {1}).").format(
					DESCRIPTION_MAX, len(desc)
				)
			)

		plan = self.payment_plan or ""
		if len(plan) > PAYMENT_PLAN_MAX:
			frappe.throw(
				_("Payment Plan must not exceed {0} characters (currently {1}).").format(
					PAYMENT_PLAN_MAX, len(plan)
				)
			)