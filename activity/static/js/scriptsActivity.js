(function () {
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    const container = document.getElementById("headers-forms");
    if (!container) return;

    const prefix = container.dataset.prefix || "headers";
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    const maxFormsInput = document.getElementById(`id_${prefix}-MAX_NUM_FORMS`);
    const addBtn = document.getElementById("add-header");

    const tmplEl = document.getElementById("empty-form-template");
    if (!tmplEl) return;
    const template = tmplEl.content;

    function updateAttributes(node, index) {
      const walker = document.createTreeWalker(node, NodeFilter.SHOW_ELEMENT, null);
      let current = node;
      do {
        if (current.name && current.name.includes(`${prefix}-__prefix__-`)) {
          current.name = current.name.replace(`${prefix}-__prefix__-`, `${prefix}-${index}-`);
        }
        if (current.id && current.id.includes(`id_${prefix}-__prefix__-`)) {
          current.id = current.id.replace(`id_${prefix}-__prefix__-`, `id_${prefix}-${index}-`);
        }
        if (current.getAttribute && current.getAttribute("for")) {
          const f = current.getAttribute("for");
          if (f.includes(`id_${prefix}-__prefix__-`)) {
            current.setAttribute("for", f.replace(`id_${prefix}-__prefix__-`, `id_${prefix}-${index}-`));
          }
        }
      } while ((current = walker.nextNode()));
    }

    function addFormRow() {
      const total = parseInt(totalFormsInput.value, 10);
      const max = maxFormsInput.value ? parseInt(maxFormsInput.value, 10) : null;
      if (max !== null && total >= max) return;

      const clone = document.importNode(template, true);
      updateAttributes(clone, total);
      container.appendChild(clone);
      totalFormsInput.value = total + 1;
    }

    if (addBtn) addBtn.addEventListener("click", addFormRow);

    container.addEventListener("click", function (e) {
      if (e.target.closest(".remove-row")) {
        const item = e.target.closest(".header-form-item");
        item.remove();

        // Reindexar
        const items = container.querySelectorAll(".header-form-item");
        items.forEach((el, idx) => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT, null);
          let node = el;
          do {
            if (node.name && node.name.match(new RegExp(`${prefix}-\\d+-`))) {
              node.name = node.name.replace(new RegExp(`${prefix}-(\\d+)-`, "g"), `${prefix}-${idx}-`);
            }
            if (node.id && node.id.match(new RegExp(`id_${prefix}-\\d+-`))) {
              node.id = node.id.replace(new RegExp(`id_${prefix}-(\\d+)-`, "g"), `id_${prefix}-${idx}-`);
            }
            if (node.getAttribute && node.getAttribute("for")) {
              const f = node.getAttribute("for");
              if (f && f.match(new RegExp(`id_${prefix}-\\d+-`))) {
                node.setAttribute("for", f.replace(new RegExp(`id_${prefix}-(\\d+)-`, "g"), `id_${prefix}-${idx}-`));
              }
            }
          } while ((node = walker.nextNode()));
        });
        totalFormsInput.value = items.length;
      }
    });
  });
})();
