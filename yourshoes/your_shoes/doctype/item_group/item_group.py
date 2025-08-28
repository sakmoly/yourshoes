frappe.ui.form.on("Item Group", {
  async refresh(frm) { await build_codes(frm); },
  async parent_item_group(frm) { await build_codes(frm); },
  async item_group_name(frm) { await build_codes(frm); },
  async group_code(frm) { await build_codes(frm); },
});

async function build_codes(frm) {
  const d = frm.doc;
  const myCode = (d.group_code || "").trim();

  // fetch parent fields we need
  let parentFull = "", parentName = "";
  if (d.parent_item_group) {
    try {
      const r = await frappe.db.get_value(
        "Item Group",
        d.parent_item_group,
        ["full_group_code", "item_group_name"]
      );
      parentFull = (r?.message?.full_group_code) || "";
      parentName = (r?.message?.item_group_name) || "";
    } catch (e) {}
  }

  // full code = parent.full + "." + myCode  (or just myCode at root)
  const full = parentFull ? `${parentFull}.${myCode}` : myCode;
  if (frm.doc.full_group_code !== full) {
    await frm.set_value("full_group_code", full);
  }

  // display name = "ParentName ChildName" (if parent exists and not already prefixed)
  let displayName = (d.item_group_name || "").trim();
  if (parentName && displayName && !displayName.toLowerCase().startsWith(parentName.toLowerCase())) {
    displayName = `${parentName} ${displayName}`;  // e.g., "Women Watch"
  }

  // Code + Name field
  if (frm.fields_dict.combined_code_name) {
    const combined = full ? `${full} - ${displayName}` : displayName;
    if (frm.doc.combined_code_name !== combined) {
      await frm.set_value("combined_code_name", combined);
    }
  }
}


from erpnext.stock.doctype.item_group.item_group import ItemGroup as CoreItemGroup

class CustomItemGroup(CoreItemGroup):
    def autoname(self):
        # Make docname unique per parent
        base = (self.item_group_name or "").strip()
        parent = (self.parent_item_group or "").strip()
        self.name = f"{parent} - {base}" if parent else base
