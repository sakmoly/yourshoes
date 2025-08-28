frappe.provide("frappe.treeview_settings");

(function () {
  const tv = (frappe.treeview_settings["Item Group"] =
    frappe.treeview_settings["Item Group"] || {});

  tv.fields = (tv.fields || []).concat([
    "item_group_name",
    "full_group_code",
    "combined_code_name",
    "is_group",
  ]);

  tv.get_label = function (node) {
    const d = node.data || node;
    if (d.combined_code_name) return d.combined_code_name; // e.g., "WMN.RNG - Women Ring"
    const left = d.full_group_code || "";
    const right = d.item_group_name || d.value || "";
    return left ? `${left} - ${right}` : right;
  };
})();
