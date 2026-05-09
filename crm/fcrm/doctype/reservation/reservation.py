import frappe
from frappe import _
from frappe.model.document import Document

FREQ = {"Monthly": 12, "Quarterly": 4, "Biannual": 2, "Annual": 1}


def _pick_first(*vals):
    """Return first non-empty/stripped value."""
    for v in vals:
        if isinstance(v, str):
            v = v.strip()
            if v:
                return v
        elif v:
            return v
    return None


class Reservation(Document):
    def validate(self):
        self._pull_lead()
        self._pull_plan()
        self._pull_unit_meta()
        self._compute_plan()

    @classmethod
    def default_list_data(cls):
        """
        Columns for crm.api.doc.get_data / ViewControls.
        We keep 'name' in rows (needed for navigation) but we don't show it as a column.
        We show Lead Name and a human Payment Plan title instead.
        """
        meta = frappe.get_meta("Reservation")

        # pick whichever field you have added: plan_name or plan_label; else fall back to 'payment_plan'
        plan_col = "plan_name" if meta.has_field("plan_name") else (
            "plan_label" if meta.has_field("plan_label") else "payment_plan"
        )
        plan_type = "Data"

        return {
            "columns": [
                {"key": "lead_name",  "label": "Lead",          "type": "Data", "width": 240},
                {"key": plan_col,     "label": "Payment Plan",  "type": plan_type, "options": "Payment Plan", "width": 240},
                {"key": "project",    "label": "Project",       "type": "Link", "options": "Real Estate Project", "width": 220},
                {"key": "unit",       "label": "Unit",          "type": "Data", "width": 220},
                {"key": "total_cost", "label": "Total Cost",    "type": "Currency", "width": 160},
                {"key": "modified",   "label": "Last Updated",  "type": "Datetime", "width": 180},
            ],
            "rows": [
                "name",
                "lead_name",
                plan_col,
                "project",
                "unit",
                "total_cost",
                "modified",
                "crm_lead",
                "payment_plan",
            ],
            "order_by": "modified desc",
            "page_length": 100,
        }

    def _pull_lead(self):
        """Safe stub if method not yet implemented elsewhere."""
        pass

    def _pull_unit_meta(self):
        """Safe stub if method not yet implemented elsewhere."""
        pass

    def _compute_plan(self):
        """Safe stub if method not yet implemented elsewhere."""
        pass

    def _pull_plan(self):
        """If a Payment Plan is selected, capture a human title and pull key fields."""
        if not getattr(self, "payment_plan", None):
            return

        try:
            pp = frappe.get_doc("Payment Plan", self.payment_plan)
        except Exception:
            return

        # Human-friendly plan title
        plan_title = _pick_first(
            getattr(pp, "plan_name", None),
            getattr(pp, "title", None),
            pp.name,
        )

        # Save into whichever field exists on Reservation
        for fld in ("plan_name", "plan_label"):
            if frappe.get_meta("Reservation").has_field(fld):
                setattr(self, fld, plan_title)
                break

        # If project / unit are empty, try to pull from plan
        plan_project = _pick_first(getattr(pp, "project", None), getattr(pp, "project_name", None))
        plan_unit = _pick_first(
            getattr(pp, "project_unit", None),
            getattr(pp, "unit", None),
            getattr(pp, "unit_name", None),
            getattr(pp, "unit_id", None),
        )

        if plan_project and not getattr(self, "project", None):
            self.project = plan_project
        if plan_unit and not getattr(self, "unit", None):
            self.unit = plan_unit

        # Prefer server-side total cost = Area × Price if Reservation total is empty
        area = _pick_first(
            getattr(pp, "area", None),
            getattr(pp, "unit_area", None),
            getattr(pp, "built_up_area", None),
            getattr(pp, "bua", None),
            getattr(pp, "sqm", None),
            getattr(pp, "sqft", None),
            getattr(pp, "total_area", None),
            getattr(pp, "net_area", None),
        )
        price = _pick_first(
            getattr(pp, "price", None),
            getattr(pp, "rate", None),
            getattr(pp, "price_per_sqm", None),
            getattr(pp, "price_per_sqft", None),
            getattr(pp, "basic_rate", None),
            getattr(pp, "selling_price", None),
            getattr(pp, "list_price", None),
            getattr(pp, "base_price", None),
            getattr(pp, "price_per_m2", None),
        )

        if not getattr(self, "total_cost", None):
            try:
                if area and price:
                    self.total_cost = float(area) * float(price)
                elif getattr(pp, "total_cost", None):
                    self.total_cost = float(pp.total_cost)
                elif getattr(pp, "total_price", None):
                    self.total_cost = float(pp.total_price)
            except Exception:
                pass

        # Frequency / Years fallback from plan
        if not getattr(self, "frequency", None):
            self.frequency = _pick_first(getattr(pp, "frequency", None))
        if not getattr(self, "years", None):
            self.years = _pick_first(
                getattr(pp, "years", None),
                getattr(pp, "tenure", None),
                getattr(pp, "tenor", None),
                getattr(pp, "duration_years", None),
            )


# ---------- AUTO CREATE DEAL ----------
def create_deal_from_reservation(doc, method=None):
    # only when status becomes Deal Done
    if (doc.status or "").strip() != "Deal Done":
        return

    old_doc = doc.get_doc_before_save() if not doc.is_new() else None
    old_status = (old_doc.status or "").strip() if old_doc else None

    # avoid rerun if already Deal Done before
    if old_status == "Deal Done":
        return

    # only from Reserved -> Deal Done
    if old_doc and old_status not in (None, "Reserved"):
        return

    # already linked
    if hasattr(doc, "deal") and doc.deal:
        return

    # already exists
    existing = frappe.db.get_value("CRM Deal", {"reservation": doc.name}, "name")
    if existing:
        frappe.db.set_value("Reservation", doc.name, "deal", existing, update_modified=False)
        return

    lead = frappe.get_doc("CRM Lead", doc.lead) if doc.lead else None
    payment_plan = frappe.get_doc("Payment Plan", doc.payment_plan) if doc.payment_plan else None

    deal = frappe.new_doc("CRM Deal")

    # standard deal fields
    deal.lead = doc.lead
    deal.source = doc.source
    deal.lead_name = doc.lead_name
    deal.email = lead.email if lead and hasattr(lead, "email") else None
    deal.mobile_no = lead.mobile_no if lead and hasattr(lead, "mobile_no") else None
    deal.phone = lead.phone if lead and hasattr(lead, "phone") else None
    deal.website = lead.website if lead and hasattr(lead, "website") else None
    deal.job_title = lead.job_title if lead and hasattr(lead, "job_title") else None
    deal.no_of_employees = lead.no_of_employees if lead and hasattr(lead, "no_of_employees") else None
    deal.territory = lead.territory if lead and hasattr(lead, "territory") else None
    deal.industry = lead.industry if lead and hasattr(lead, "industry") else None
    deal.salutation = lead.salutation if lead and hasattr(lead, "salutation") else None
    deal.first_name = lead.first_name if lead and hasattr(lead, "first_name") else None
    deal.last_name = lead.last_name if lead and hasattr(lead, "last_name") else None
    deal.gender = lead.gender if lead and hasattr(lead, "gender") else None

    # optional visual field
    deal.organization_name = lead.project if lead and hasattr(lead, "project") else None

    # financial defaults
    deal.deal_value = doc.total_cost
    deal.expected_deal_value = doc.total_cost
    deal.total_deal_value = doc.total_cost or 0

    # 🔥 get down payment from payment plan snapshot
    deal.down_payment_amount = (
        getattr(payment_plan, "total_downpayment_value", None)
        if payment_plan else None
    ) or (
        getattr(doc, "plan_total_downpayment_value", None)
    ) or 0

    deal.deal_date = frappe.utils.nowdate()

    deal.down_payment_date = (
        getattr(doc, "plan_downpayment_date", None)
        or getattr(payment_plan, "downpayment_date", None)
        or None
    )

    # reservation snapshot
    deal.reservation = doc.name
    deal.reservation_fee = doc.reservation_fee
    deal.reservation_date = doc.reservation_date
    deal.reservation_project = doc.project
    deal.reservation_unit = doc.unit
    deal.payment_plan = doc.payment_plan
    deal.total_cost = doc.total_cost
    deal.per_installment = doc.per_installment
    deal.installments = doc.installments
    deal.years = doc.years
    deal.frequency = doc.frequency

    # property preferences from lead
    if lead:
        deal.property_city = lead.property_city
        deal.property_region = lead.property_region
        deal.property_type = lead.property_type
        deal.property_subtype = lead.property_subtype
        deal.property_space = lead.property_space
        deal.property_floor = lead.property_floor
        deal.property_condition = lead.property_condition
        deal.property_decoration = lead.property_decoration
        deal.property_relation = lead.property_relation
        deal.property_project = lead.property_project
        deal.property_year_built = lead.property_year_built
        deal.property_delivery_date = lead.property_delivery_date
        deal.property_bedrooms = lead.property_bedrooms
        deal.property_bathrooms = lead.property_bathrooms
        deal.property_view = lead.property_view
        deal.property_finishing = lead.property_finishing
        deal.property_features = lead.property_features
        deal.property_min_price = lead.property_min_price
        deal.property_max_price = lead.property_max_price
        deal.property_payment = lead.property_payment
        deal.property_down_payment = lead.property_down_payment
        deal.property_ownership = lead.property_ownership

    # payment plan snapshot
    if payment_plan:
        deal.plan_name = payment_plan.plan_name
        deal.plan_notes = payment_plan.notes
        deal.plan_area = payment_plan.area
        deal.plan_price_per_m2 = payment_plan.price_per_m2
        deal.plan_total_price = payment_plan.total_price
        deal.plan_split_downpayment = payment_plan.split_downpayment
        deal.plan_downpayment_percent = payment_plan.downpayment_percent
        deal.plan_downpayment_date = payment_plan.downpayment_date
        deal.plan_dp1_percent = payment_plan.dp1_percent
        deal.plan_dp1_date = payment_plan.dp1_date
        deal.plan_dp2_percent = payment_plan.dp2_percent
        deal.plan_dp2_date = payment_plan.dp2_date
        deal.plan_total_downpayment_percent = payment_plan.total_downpayment_percent
        deal.plan_total_downpayment_value = payment_plan.total_downpayment_value
        deal.plan_start_date = payment_plan.start_date
        deal.plan_installment_type = payment_plan.installment_type
        deal.plan_has_garage = payment_plan.has_garage
        deal.plan_garage_price = payment_plan.garage_price
        deal.plan_has_clubhouse = payment_plan.has_clubhouse
        deal.plan_clubhouse_price = payment_plan.clubhouse_price
        deal.plan_has_maintainance = payment_plan.has_maintainance
        deal.plan_maintenance_fee = payment_plan.maintenance_fee
        deal.plan_has_garden = payment_plan.has_garden
        deal.plan_garden_price = payment_plan.garden_price
        deal.plan_has_roof = payment_plan.has_roof
        deal.plan_roof_price = payment_plan.roof_price
        deal.plan_has_pool = payment_plan.has_pool
        deal.plan_pool_price = payment_plan.pool_price

    deal.insert(ignore_permissions=True)

    frappe.db.set_value("Reservation", doc.name, "deal", deal.name, update_modified=False)

    doc.add_comment("Comment", f"CRM Deal {deal.name} was auto-created from this reservation.")


# ---------- AJAX helpers (whitelisted) ----------
@frappe.whitelist()
def get_unit_meta(name: str, project: str | None = None):
    """
    Normalize Unit / Project Unit data for the Reservation form.
    Returns keys that actually exist on your doctypes.
    """
    if not name:
        return {}

    target_dt = None
    if frappe.db.exists("Project Unit", name):
        target_dt = "Project Unit"
    elif frappe.db.exists("Unit", name):
        target_dt = "Unit"
    else:
        return {}

    doc = frappe.get_doc(target_dt, name)

    def pick(*fields):
        for f in fields:
            if hasattr(doc, f):
                v = getattr(doc, f)
                if isinstance(v, str):
                    v = v.strip()
                if v not in (None, ""):
                    return v
        return None

    area_val = _pick_first(
        getattr(doc, "area_sqm", None),
        getattr(doc, "builtup_area_m²", None),
    )

    availability_val = _pick_first(
        getattr(doc, "availability", None),
        getattr(doc, "status", None),
    )

    return {
        "doctype": target_dt,
        "name": doc.name,
        "unit_name": pick("unit_name") or doc.name,
        "project": pick("project") or (project or None),
        "property_type": pick("type"),
        "area": area_val,
        "price": pick("price"),
        "price_per_meter": pick("price_per_meter"),
        "maintenance_fees": pick("maintenance_fees"),
        "availability": availability_val,
        "floor": pick("floor"),
        "view": pick("view"),
        "orientation": pick("orientation"),
        "furnished": pick("furnished"),
        "finishing": pick("finishing"),
        "parking": pick("parking"),
        "bedrooms": pick("bedrooms"),
        "bathrooms": pick("bathrooms"),
        "master_bed_rooms": pick("master_bed_rooms"),
        "categories": pick("categories"),
        "property_image": pick("cover_image", "property_image", "image", "unit_image", "image_url", "thumbnail"),
        "floor_plan": pick("floor_plan"),
        "brochure": pick("brochure"),
        "video_url": pick("video_url"),
    }


@frappe.whitelist()
def search_units_by_title(doctype=None, txt: str = "", searchfield: str = "name",
                          start: int = 0, page_len: int = 20, filters=None):
    """
    Custom search used by Reservation.unit. Returns [[value, label], ...].
    Label = human title (no numeric prefixes).
    """
    if isinstance(filters, str):
        try:
            filters = frappe.parse_json(filters) or {}
        except Exception:
            filters = {}
    filters = filters or {}

    target_dt = (filters.get("target_dt") or "Unit").strip()
    q = (txt or "").strip().lower()

    meta = frappe.get_meta(target_dt)
    candidates = ["unit_name", "unit_title", "title", "name"]
    display_field = next((f for f in candidates if (f == "name" or meta.has_field(f))), "name")

    base_filters = {}
    if target_dt == "Project Unit" and filters.get("project"):
        base_filters["project"] = filters.get("project")

    order_by = f"{display_field} asc" if display_field != "name" else "modified desc"

    rows = frappe.get_all(
        target_dt,
        filters=base_filters,
        fields=["name", display_field],
        order_by=order_by,
        start=start,
        page_length=page_len,
    )

    import re
    def strip_num_prefix(s: str) -> str:
        return re.sub(r"^\s*\d+\s*[-–.:]*\s*", "", s or "").strip()

    out = []
    for r in rows:
        raw_label = (r.get(display_field) or r.get("name") or "").strip()
        label = strip_num_prefix(raw_label)
        if q and q not in label.lower():
            continue
        out.append([r["name"], label])
    return out


def get_dashboard_data():
    return {
        "non_standard_fieldnames": {
            "Payment Plan": "reservation",
        },
        "internal_links": {
            "CRM Lead": ["lead"],
            "Real Estate Project": ["project"],
        },
        "transactions": [
            {"label": _("Payments"), "items": ["Payment Plan"]},
        ],
    }