# apps/yourshoes/yourshoes/your_shoes/item_hooks.py

import frappe

def validate_item_subgroup(doc, method=None):
    """
    Ensure Item.sub_item_group is under Item.item_group (any depth).
    Safe if the custom field doesn't exist yet.
    """
    # Skip on sites where the custom field wasn't created yet
    if not frappe.get_meta("Item").has_field("sub_item_group"):
        return

    parent = doc.get("item_group")
    child  = doc.get("sub_item_group")
    if not (parent and child):
        return

    # Use nested-set bounds so it works at any depth
    pl, pr = frappe.db.get_value("Item Group", parent, ["lft", "rgt"])
    cl, cr = frappe.db.get_value("Item Group", child,  ["lft", "rgt"])

    if not (pl and pr and cl and cr and (pl < cl < cr < pr)):
        frappe.throw(f"Sub Group '{child}' must be under the selected Group '{parent}'.")
