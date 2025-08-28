import frappe

# -------- helpers --------
def _fields_ready():
    m = frappe.get_meta("Item Group")
    return m.has_field("group_code") and m.has_field("full_group_code")

def _prefixed_name(doc):
    """
    Return 'Parent - Child' without double-prefixing if the user already typed it.
    """
    base = (doc.item_group_name or "").strip()
    if not doc.parent_item_group:
        return base

    parent_name = frappe.db.get_value("Item Group", doc.parent_item_group, "item_group_name") or ""
    if not parent_name:
        return base

    low = base.lower()
    p_low = parent_name.lower()
    # strip an existing prefix like "Women - Ring" ? "Ring"
    if low.startswith(p_low + " - "):
        child = base[len(parent_name) + 3 :].strip()
    elif low.startswith(p_low + " "):
        child = base[len(parent_name) :].strip()
    else:
        child = base

    return f"{parent_name} - {child}" if child else parent_name

# -------- events --------
def before_insert_item_group(doc, method=None):
    """
    Ensure sub-groups get a unique title & docname:
    - Item Group Name: 'Parent - Child' for children
    - doc.name is set to the same on insert (avoids "already exists")
    """
    new_title = _prefixed_name(doc)
    doc.item_group_name = new_title
    doc.name = new_title  # initial name at insert time

def before_save_item_group(doc, method=None):
    """
    Build full_group_code and enforce its uniqueness.
    Allows repeating 'group_code' under different parents.
    """
    # keep the title prefixed if parent changed
    doc.item_group_name = _prefixed_name(doc)

    if not _fields_ready():
        return  # fields not on this site yet, skip quietly

    code = (doc.get("group_code") or "").strip()
    if not code:
        frappe.throw("Group Code is required.")
    doc.group_code = code  # normalize

    parent_full = ""
    parent_name = ""
    if doc.parent_item_group:
        vals = frappe.db.get_value(
            "Item Group", doc.parent_item_group, ["full_group_code", "item_group_name"], as_dict=True
        )
        if vals:
            parent_full = vals.get("full_group_code") or ""
            parent_name = vals.get("item_group_name") or ""

    full = f"{parent_full}.{code}" if parent_full else code
    doc.full_group_code = full

    # Optional: combined label "WMN.RNG - Women Ring"
    m = frappe.get_meta("Item Group")
    if m.has_field("combined_code_name"):
        disp = doc.item_group_name or ""
        doc.combined_code_name = f"{full} - {disp}" if full else disp

    # Enforce ONLY full_group_code uniqueness (so same sub-code can repeat across parents)
    if full and frappe.db.exists("Item Group", {"name": ["!=", doc.name], "full_group_code": full}):
        frappe.throw(f"Full Group Code '{full}' already exists. Choose a different Group Code.")
        
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

def validate_item_subgroup(doc, method=None):
    # Only check when both fields are set
    parent = doc.get("item_group")
    child  = doc.get("sub_item_group")
    if not (parent and child):
        return

    # Support deep hierarchy using nested set (lft/rgt)
    pl, pr = frappe.db.get_value("Item Group", parent, ["lft", "rgt"])
    cl, cr = frappe.db.get_value("Item Group", child,  ["lft", "rgt"])

    # Ensure child sits anywhere inside the parent subtree
    if not (pl and pr and cl and cr and (pl < cl < cr < pr)):
        frappe.throw(f"Sub Group '{child}' must be under the selected Group '{parent}'.")
