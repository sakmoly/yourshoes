import frappe

# ---------- helpers ----------
def _fields_ready():
    m = frappe.get_meta("Item Group")
    return m.has_field("group_code") and m.has_field("full_group_code")

def _prefixed_name(doc):
    """Return 'Parent - Child' without double-prefixing."""
    base = (doc.item_group_name or "").strip()
    if not doc.parent_item_group:
        return base
    parent_name = frappe.db.get_value("Item Group", doc.parent_item_group, "item_group_name") or ""
    if not parent_name:
        return base
    # strip existing "Parent - " if user typed it already
    low = base.lower()
    p_low = parent_name.lower()
    if low.startswith(p_low + " - "):
        child = base[len(parent_name) + 3 :].strip()
    elif low.startswith(p_low + " "):
        child = base[len(parent_name) :].strip()
    else:
        child = base
    return f"{parent_name} - {child}" if child else parent_name

# ---------- events ----------
def before_insert_item_group(doc, method=None):
    """Prefix the sub-group name with the main group before insert,
    so doc.name and item_group_name are both unique per parent."""
    new_title = _prefixed_name(doc)
    doc.item_group_name = new_title
    doc.name = new_title  # initial name

def validate_item_group(doc, method=None):
    """Build path code and keep it unique. Do NOT rename here (only on insert)."""
    # Prefix the title again in case parent or name changed before save
    doc.item_group_name = _prefixed_name(doc)

    if not _fields_ready():
        return  # custom fields not on this site yet

    # normalize short code and require it
    code = (doc.get("group_code") or "").strip()
    if not code:
        frappe.throw("Group Code is required.")
    doc.group_code = code

    # parent path code
    parent_full = ""
    parent_name = ""
    if doc.parent_item_group:
        parent_full, parent_name = frappe.db.get_value(
            "Item Group", doc.parent_item_group, ["full_group_code", "item_group_name"]
        ) or ("", "")

    full = f"{parent_full}.{code}" if parent_full else code
    doc.full_group_code = full

    # optional helpful label
    m = frappe.get_meta("Item Group")
    if m.has_field("combined_code_name"):
        # build "WMN.RNG - Women Ring"
        display = doc.item_group_name or ""
        doc.combined_code_name = f"{full} - {display}" if full else display

    # keep ONLY the full path code unique (allow same sub-code under different parents)
    if full and frappe.db.exists("Item Group", {"name": ["!=", doc.name], "full_group_code": full}):
        frappe.throw(f"Full Group Code '{full}' already exists. Choose a different Group Code.")
