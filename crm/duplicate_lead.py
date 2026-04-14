import frappe
from frappe.utils import now

CHILD_TABLE_FIELDNAME = "duplicate_leads"
CHILD_LINK_FIELDNAME  = "lead"

# ---------- Utilities ----------

def normalize_egyptian_phone(number: str) -> str:
    if not number:
        return ""
    number = number.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    cleaned = []
    for i, ch in enumerate(number.strip()):
        if ch.isdigit() or (ch == "+" and i == 0):
            cleaned.append(ch)
    number = "".join(cleaned)

    if number.startswith("+20"):
        return "+20" + number[3:]
    if number.startswith("0020"):
        return "+20" + number[4:]
    if number.startswith("20"):
        return "+20" + number[2:]
    if number.startswith("0"):
        return "+20" + number[1:]
    if len(number) == 10 and number.startswith("1"):
        return "+20" + number
    if len(number) == 11 and number.startswith("01"):
        return "+20" + number[1:]
    return number


def _collect_numbers(doc):
    p = normalize_egyptian_phone(getattr(doc, "phone", "") or "")
    m = normalize_egyptian_phone(getattr(doc, "mobile_no", "") or "")

    if hasattr(doc, "phone"):
        doc.phone = p
    if hasattr(doc, "mobile_no"):
        doc.mobile_no = m

    return [n for n in {p, m} if n]


def _find_original(numbers, exclude=None):
    if not numbers:
        return None

    or_filters = (
        [["CRM Lead", "phone", "=", n] for n in numbers] +
        [["CRM Lead", "mobile_no", "=", n] for n in numbers]
    )

    rows = frappe.get_all(
        "CRM Lead",
        filters={"name": ["!=", exclude]} if exclude else {},
        or_filters=or_filters,
        fields=["name", "creation", "original_lead", "is_duplicate"],
        order_by="original_lead desc, is_duplicate asc, creation asc",
        limit=1,
    )

    return rows[0]["name"] if rows else None


def _ensure_child_once(original, duplicate_name, timestamp):
    if duplicate_name == original.name:
        return

    rows = original.get(CHILD_TABLE_FIELDNAME) or []
    if any(getattr(r, CHILD_LINK_FIELDNAME, None) == duplicate_name for r in rows):
        return

    original.append(
        CHILD_TABLE_FIELDNAME,
        {
            CHILD_LINK_FIELDNAME: duplicate_name,
            "created_on": timestamp,
            "note": "Auto-added duplicate",
        },
    )


# ---------- Hooks ----------

def check_duplicates(doc, method):
    if getattr(doc.flags, "ignore_duplicate_check", False):
        return

    numbers = _collect_numbers(doc)

    if not numbers:
        doc.is_duplicate = 0
        doc.duplicated_from = None
        doc.original_lead = 0
        return

    original = _find_original(numbers)

    if original:
        doc.is_duplicate = 1
        doc.duplicated_from = original
        doc.original_lead = 0

        # ensure original is marked immediately
        frappe.db.set_value(
            "CRM Lead",
            original,
            "original_lead",
            1,
            update_modified=False,
        )

    else:
        doc.is_duplicate = 0
        doc.duplicated_from = None
        doc.original_lead = 0


def append_to_original_lead(doc, method):
    frappe.db.after_commit(lambda doc=doc: _append(doc))


def _append(doc):
    if not doc or not doc.is_duplicate:
        return

    numbers = [
        n for n in {
            normalize_egyptian_phone(getattr(doc, "phone", "") or ""),
            normalize_egyptian_phone(getattr(doc, "mobile_no", "") or ""),
        }
        if n
    ]

    if not numbers:
        return

    original_name = _find_original(numbers, exclude=doc.name)

    if not original_name or original_name == doc.name:
        return

    frappe.db.set_value(
        "CRM Lead",
        doc.name,
        {
            "duplicated_from": original_name,
            "is_duplicate": 1,
        },
        update_modified=False,
    )

    try:
        original = frappe.get_doc("CRM Lead", original_name)
        original.flags.ignore_duplicate_check = True

        # ✅ STRICT RULE: original only if it HAS duplicates
        original.original_lead = 1

        _ensure_child_once(original, doc.name, now())

        original.save(ignore_permissions=True)

    except Exception:
        frappe.log_error(
            title="Duplicate Lead Error",
            message=frappe.get_traceback(),
        )
import frappe
from frappe.utils import now

CHILD_TABLE_FIELDNAME = "duplicate_leads"
CHILD_LINK_FIELDNAME  = "lead"

# ---------- Utilities ----------

def normalize_egyptian_phone(number: str) -> str:
    if not number:
        return ""
    number = number.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    cleaned = []
    for i, ch in enumerate(number.strip()):
        if ch.isdigit() or (ch == "+" and i == 0):
            cleaned.append(ch)
    number = "".join(cleaned)

    if number.startswith("+20"):
        return "+20" + number[3:]
    if number.startswith("0020"):
        return "+20" + number[4:]
    if number.startswith("20"):
        return "+20" + number[2:]
    if number.startswith("0"):
        return "+20" + number[1:]
    if len(number) == 10 and number.startswith("1"):
        return "+20" + number
    if len(number) == 11 and number.startswith("01"):
        return "+20" + number[1:]
    return number


def _collect_numbers(doc):
    p = normalize_egyptian_phone(getattr(doc, "phone", "") or "")
    m = normalize_egyptian_phone(getattr(doc, "mobile_no", "") or "")

    if hasattr(doc, "phone"):
        doc.phone = p
    if hasattr(doc, "mobile_no"):
        doc.mobile_no = m

    return [n for n in {p, m} if n]


def _find_original(numbers, exclude=None):
    if not numbers:
        return None

    or_filters = (
        [["CRM Lead", "phone", "=", n] for n in numbers] +
        [["CRM Lead", "mobile_no", "=", n] for n in numbers]
    )

    rows = frappe.get_all(
        "CRM Lead",
        filters={"name": ["!=", exclude]} if exclude else {},
        or_filters=or_filters,
        fields=["name", "creation", "original_lead", "is_duplicate"],
        order_by="original_lead desc, is_duplicate asc, creation asc",
        limit=1,
    )

    return rows[0]["name"] if rows else None


def _ensure_child_once(original, duplicate_name, timestamp):
    if duplicate_name == original.name:
        return

    rows = original.get(CHILD_TABLE_FIELDNAME) or []
    if any(getattr(r, CHILD_LINK_FIELDNAME, None) == duplicate_name for r in rows):
        return

    original.append(
        CHILD_TABLE_FIELDNAME,
        {
            CHILD_LINK_FIELDNAME: duplicate_name,
            "created_on": timestamp,
            "note": "Auto-added duplicate",
        },
    )


# ✅ NEW: Sync original flag based on actual duplicates
def _sync_original_flag(lead_name):
    count = frappe.db.count("CRM Lead", {
        "duplicated_from": lead_name
    })

    frappe.db.set_value(
        "CRM Lead",
        lead_name,
        "original_lead",
        1 if count > 0 else 0,
        update_modified=False
    )


# ---------- Hooks ----------

def check_duplicates(doc, method):
    if not doc.is_new:
        return

    if getattr(doc.flags, "ignore_duplicate_check", False):
        return

    numbers = _collect_numbers(doc)

    if not numbers:
        doc.is_duplicate = 0
        doc.duplicated_from = None
        doc.original_lead = 0
        return

    original = _find_original(numbers)

    if original:
        doc.is_duplicate = 1
        doc.duplicated_from = original
        doc.original_lead = 0

        # enforce original immediately
        frappe.db.set_value(
            "CRM Lead",
            original,
            "original_lead",
            1,
            update_modified=False,
        )

    else:
        doc.is_duplicate = 0
        doc.duplicated_from = None
        doc.original_lead = 0


def append_to_original_lead(doc, method):
    frappe.db.after_commit(lambda doc=doc: _append(doc))


def _append(doc):
    if not doc:
        return

    original_name = doc.duplicated_from

    if not original_name or original_name == doc.name:
        return

    try:
        original = frappe.get_doc("CRM Lead", original_name)
        original.flags.ignore_duplicate_check = True

        # ensure original flag
        original.original_lead = 1

        # 🔥 SAFE APPEND (your table is Duplicate Lead Entry)
        exists = False

        for r in original.get("duplicate_leads") or []:
            if r.lead == doc.name:
                exists = True
                break

        if not exists:
            original.append("duplicate_leads", {
                "lead": doc.name,
                "created_on": now(),
                "note": "Auto-added duplicate"
            })

        original.save(ignore_permissions=True)

        # IMPORTANT: refresh DB state
        frappe.db.commit()

    except Exception:
        frappe.log_error(
            title="Duplicate Lead Append Error",
            message=frappe.get_traceback(),
        )
