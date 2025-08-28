console.log("[yourshoes] item_group.js loaded");

frappe.ui.form.on("Item Group", {
  async refresh(frm) { await build(frm); },
  async parent_item_group(frm) { await build(frm, true); },
  async item_group_name(frm) { await build(frm); },
  async group_code(frm) { await build(frm); },
});

async function build(frm, maybePrefix=false) {
  const d = frm.doc;

  // live prefix for user experience (server will enforce anyway)
  if (maybePrefix && d.parent_item_group && d.item_group_name) {
    try {
      const r = await frappe.db.get_value("Item Group", d.parent_item_group, "item_group_name");
      const parentName = (r && r.message && r.message.item_group_name) || "";
      const base = (d.item_group_name || "").trim();
      const low = base.toLowerCase(), p = parentName.toLowerCase();
      let child = base;
      if (low.startsWith(p + " - ")) child = base.slice(parentName.length + 3).trim();
      else if (low.startsWith(p + " ")) child = base.slice(parentName.length).trim();
      const prefixed = child ? `${parentName} - ${child}` : parentName;
      if (prefixed && prefixed !== d.item_group_name) {
        await frm.set_value("item_group_name", prefixed);
      }
    } catch (e) {}
  }

  // compute full path code for preview
  let parentFull = "";
  if (d.parent_item_group) {
    try {
      const r2 = await frappe.db.get_value("Item Group", d.parent_item_group, "full_group_code");
      parentFull = (r2 && r2.message && r2.message.full_group_code) || "";
    } catch (e) {}
  }
  const code = (d.group_code || "").trim();
  const full = parentFull ? `${parentFull}.${code}` : code;

  if (frm.fields_dict.full_group_code && d.full_group_code !== full) {
    await frm.set_value("full_group_code", full);
  }
  if (frm.fields_dict.combined_code_name) {
    const combo = full ? `${full} - ${d.item_group_name || ""}` : (d.item_group_name || "");
    if (d.combined_code_name !== combo) {
      await frm.set_value("combined_code_name", combo);
    }
  }
}
