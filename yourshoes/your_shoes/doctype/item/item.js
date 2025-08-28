console.log("[yourshoes] item.js loaded");

frappe.ui.form.on("Item", {
  onload(frm) {
    // Filter Sub Group to direct children of selected Group
    frm.set_query("sub_item_group", function () {
      const parent = frm.doc.item_group || "";
      if (!parent) return { filters: { name: ["in", []] } };
      return {
        filters: {
          parent_item_group: parent, // direct children only
          is_group: 0               // leaf nodes
        }
      };
    });
  },

  // When Group changes, clear Sub Group so user re-selects from filtered list
  item_group(frm) {
    frm.set_value("sub_item_group", null);
  },
});
