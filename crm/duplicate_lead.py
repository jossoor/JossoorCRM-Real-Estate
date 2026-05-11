import frappe
from frappe.utils import now

CHILD_TABLE_FIELDNAME = "duplicate_leads"
CHILD_LINK_FIELDNAME  = "lead"


# ─── Phone Normalization ──────────────────────────────────────────────────────

def _clean_raw(number: str) -> str:
    """Remove spaces/dashes, convert Arabic-Indic digits, keep leading +."""
    if not number:
        return ""
    number = number.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    cleaned = []
    for i, ch in enumerate(number.strip()):
        if ch.isdigit() or (ch == "+" and i == 0):
            cleaned.append(ch)
    return "".join(cleaned)


def normalize_phone(number: str) -> str:
    """
    Normalize any Egyptian or Saudi phone number to E.164 format.
    Pure shape-based — no country field needed.

    Egyptian mobile prefixes : 010, 011, 012, 015
    Saudi   mobile prefixes  : 050-059
    These shapes never overlap — the number identifies itself.
    """
    n = _clean_raw(number)
    if not n:
        return ""

    # 1. Explicit country code already present
    if n.startswith("+20"):    return "+20"  + n[3:]
    if n.startswith("0020"):   return "+20"  + n[4:]
    if n.startswith("+966"):   return "+966" + n[4:]
    if n.startswith("00966"):  return "+966" + n[5:]

    # 2. Country code without +/00
    if n.startswith("20")  and len(n) == 12: return "+20"  + n[2:]
    if n.startswith("966") and len(n) == 12: return "+966" + n[3:]

    # 3. Local format — shape uniquely identifies country
    if len(n) == 11 and n.startswith("01") and n[2] in "0125":
        return "+20" + n[1:]                        # Egypt mobile  01[0125]xxxxxxx

    if len(n) == 10 and n.startswith("05"):
        return "+966" + n[1:]                       # Saudi mobile  05xxxxxxxx

    if len(n) == 10 and n[0] == "1" and n[1] in "0125":
        return "+20" + n                            # Egypt mobile  no leading 0

    if len(n) == 10 and n[0] == "0" and n[1] in "23":
        return "+20" + n[1:]                        # Egypt landline 0[23]xxxxxxxx

    if len(n) == 10 and n.startswith("01") and n[2] in "1234567":
        return "+966" + n[1:]                       # Saudi landline 01[1-7]xxxxxxx

    if len(n) == 9 and n.startswith("5"):
        return "+966" + n                           # Saudi mobile  no leading 0

    # 4. Cannot determine — return cleaned, never corrupt
    return n


def all_variants(number: str) -> list:
    """
    Return every plausible format of a number so we can match
    against old un-normalized records in the DB.

    Example for Egyptian 01012345678:
      +201012345678, 201012345678, 01012345678, 1012345678
    Example for Saudi 0512345678:
      +966512345678, 00966512345678, 966512345678, 0512345678, 512345678
    """
    e164 = normalize_phone(number)
    if not e164:
        return []

    variants = {e164}

    if e164.startswith("+20"):
        local = e164[3:]          # e.g. 1012345678
        variants.update([
            "20" + local,         # 201012345678
            "0020" + local,       # 00201012345678
            "0" + local,          # 01012345678
            local,                # 1012345678
        ])

    elif e164.startswith("+966"):
        local = e164[4:]          # e.g. 512345678
        variants.update([
            "966" + local,        # 966512345678
            "00966" + local,      # 00966512345678
            "0" + local,          # 0512345678
            local,                # 512345678
        ])

    return list(variants)


# Backward-compat alias
def normalize_egyptian_phone(number: str) -> str:
    return normalize_phone(number)


# ─── Collect & normalize phone fields on a doc ────────────────────────────────

def _collect_numbers(doc):
    p_raw = getattr(doc, "phone",     "") or ""
    m_raw = getattr(doc, "mobile_no", "") or ""

    p = normalize_phone(p_raw)
    m = normalize_phone(m_raw)

    # Write normalized values back onto the doc
    if hasattr(doc, "phone")     and p_raw: doc.phone     = p
    if hasattr(doc, "mobile_no") and m_raw: doc.mobile_no = m

    return [n for n in {p, m} if n]


# ─── Find the "original" lead — matches normalized AND raw formats ────────────

def _find_original(numbers, exclude=None):
    """
    Build OR-filters for every plausible format of every number.
    This catches old un-normalized records (e.g. stored as 01012345678)
    even when the new lead arrives as +201012345678.
    """
    if not numbers:
        return None

    # Expand each number into all its variants
    all_nums = set()
    for n in numbers:
        all_nums.update(all_variants(n))

    if not all_nums:
        return None

    or_filters = (
        [["CRM Lead", "phone",     "=", n] for n in all_nums] +
        [["CRM Lead", "mobile_no", "=", n] for n in all_nums]
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


def _sync_original_flag(lead_name):
    count = frappe.db.count("CRM Lead", {"duplicated_from": lead_name})
    frappe.db.set_value(
        "CRM Lead", lead_name, "original_lead",
        1 if count > 0 else 0,
        update_modified=False,
    )


# ─── Hooks ───────────────────────────────────────────────────────────────────

def check_duplicates(doc, method):
    """before_insert: flag new lead as duplicate if phone already exists."""
    if not doc.is_new():
        return
    if getattr(doc.flags, "ignore_duplicate_check", False):
        return

    numbers = _collect_numbers(doc)

    if not numbers:
        doc.is_duplicate    = 0
        doc.duplicated_from = None
        doc.original_lead   = 0
        return

    original = _find_original(numbers)

    if original:
        doc.is_duplicate    = 1
        doc.duplicated_from = original
        doc.original_lead   = 0
        frappe.db.set_value(
            "CRM Lead", original, "original_lead", 1,
            update_modified=False,
        )
    else:
        doc.is_duplicate    = 0
        doc.duplicated_from = None
        doc.original_lead   = 0


def append_to_original_lead(doc, method):
    """after_insert: schedule child-table update after DB commit."""
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
        original.original_lead = 1

        exists = any(
            r.lead == doc.name
            for r in (original.get("duplicate_leads") or [])
        )
        if not exists:
            original.append("duplicate_leads", {
                "lead":       doc.name,
                "created_on": now(),
                "note":       "Auto-added duplicate",
            })

        original.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        frappe.log_error(
            title="Duplicate Lead Append Error",
            message=frappe.get_traceback(),
        )


# ─── One-time Migration: normalize all existing phone numbers in DB ───────────
#
# Run once from bench console:
#   bench --site your-site.com execute \
#     jossoor_crm.fcrm.utils.duplicate_lead.normalize_all_existing_phones
#
# Safe to run multiple times — idempotent.

@frappe.whitelist()
def normalize_all_existing_phones():
    """
    Normalize phone/mobile_no on every existing CRM Lead.
    Fixes old un-normalized records so duplicate detection works correctly
    against both old and new leads.
    """
    leads = frappe.get_all(
        "CRM Lead",
        fields=["name", "phone", "mobile_no"],
        limit_page_length=0,
    )

    updated = 0
    skipped = 0

    for row in leads:
        p_raw = row.get("phone")     or ""
        m_raw = row.get("mobile_no") or ""

        p_new = normalize_phone(p_raw) if p_raw else ""
        m_new = normalize_phone(m_raw) if m_raw else ""

        changes = {}
        if p_raw and p_new and p_new != p_raw:
            changes["phone"] = p_new
        if m_raw and m_new and m_new != m_raw:
            changes["mobile_no"] = m_new

        if changes:
            frappe.db.set_value(
                "CRM Lead", row["name"], changes,
                update_modified=False,
            )
            updated += 1
        else:
            skipped += 1

    frappe.db.commit()

    msg = f"Done. Updated: {updated} leads, Skipped (already normalized): {skipped} leads."
    frappe.logger().info(msg)
    return msg