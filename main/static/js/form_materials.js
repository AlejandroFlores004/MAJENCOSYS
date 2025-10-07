// static/js/materials_formset.js
(function () {
  // -------- Helpers comunes --------
  function isSelect2Available() {
    return window.jQuery && jQuery.fn && typeof jQuery.fn.select2 === "function";
  }
  function initSelect2On(el) {
    if (!el || !isSelect2Available()) return;
    try {
      jQuery(el).select2({
        placeholder: "Buscar material...",
        allowClear: true,
        width: "100%"
      });
    } catch (err) {
      console.error("[materials_formset] initSelect2On error", err);
    }
  }
  function _ensureSelect2Change(el) {
    if (!el) return;
    try {
      if (isSelect2Available() && jQuery(el).data("select2")) {
        jQuery(el).trigger("change");
      } else {
        el.dispatchEvent(new Event("change", { bubbles: true }));
      }
    } catch {
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }
  function _refreshSelect2(sel) {
    if (!sel) return;
    try {
      if (isSelect2Available() && jQuery(sel).data("select2")) {
        jQuery(sel).trigger("change");
      } else {
        sel.dispatchEvent(new Event("change", { bubbles: true }));
      }
    } catch {
      sel.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }
  function _findOption(sel, id) {
    const vid = String(id);
    return Array.from(sel.options).find(o => String(o.value) === vid) || null;
  }

  // -------- Estado: select activo (para devolver del popup) --------
  window._materialActiveSelect = null;
  function _rememberActiveMaterialSelectFromButton(btnEl) {
    try {
      const row = (btnEl && btnEl.closest(".material-form")) || null;
      window._materialActiveSelect = row ? row.querySelector('select[name$="-material"]') : null;
    } catch {
      window._materialActiveSelect = null;
    }
  }
  function _rememberActiveMaterialSelectFromRow(btnEl) {
    try {
      const row = (btnEl && (btnEl.closest(".material-form") || btnEl.closest(".row"))) || null;
      window._materialActiveSelect = row ? row.querySelector('select[name$="-material"]') : null;
    } catch {
      window._materialActiveSelect = null;
    }
  }

  // -------- DOM Ready --------
  document.addEventListener("DOMContentLoaded", function () {
    const container  = document.getElementById("materials-formset");
    if (!container) return;

    const addButton  = document.getElementById("add-material");
    const totalForms = container.querySelector('input[name$="-TOTAL_FORMS"]');
    const templateEl = document.getElementById("material-empty-form");

    if (!addButton || !totalForms || !templateEl) {
      console.error("[materials_formset] faltan elementos (botón/template/TOTAL_FORMS)");
      return;
    }

    // init Select2 en selects existentes
    container.querySelectorAll('select[name$="-material"]').forEach(initSelect2On);

    // Agregar fila
    addButton.addEventListener("click", function () {
      const index = Number.parseInt(totalForms.value, 10) || container.querySelectorAll(".material-form").length;
      const html  = templateEl.innerHTML.replace(/__prefix__/g, String(index));
      addButton.insertAdjacentHTML("beforebegin", html);
      totalForms.value = String(index + 1);

      // init Select2 en el nuevo select
      const rows = container.querySelectorAll(".material-form");
      const newRow = rows[rows.length - 1] || null;
      if (newRow) {
        const newSelect = newRow.querySelector('select[name$="-material"]');
        initSelect2On(newSelect);
      }
    });

    // Marcar DELETE con opacidad
    container.addEventListener("change", function (e) {
      if (e.target && e.target.type === "checkbox" && e.target.name.endsWith("-DELETE")) {
        const row = e.target.closest(".material-form");
        if (row) row.classList.toggle("opacity-50", e.target.checked);
      }
    });
  });

  // -------- POPUPS --------
  window.openMaterialPopup = function (projectId) {
    const width = 600, height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top  = (window.screen.height / 2) - (height / 2);

    const btn = document.activeElement;
    _rememberActiveMaterialSelectFromButton(btn);

    const url = `/dashboard/project/${projectId}/catalogos/material/?popup=1`;
    window.open(url, "Agregar Material",
      `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`);
  };

  window.openEditMaterialPopup = function (projectId, btnElement) {
    const width = 600, height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top  = (window.screen.height / 2) - (height / 2);

    try {
      const row = btnElement.closest(".row") || btnElement.closest(".material-form");
      if (!row) { alert("No se pudo localizar la fila del material."); return; }
      const select = row.querySelector('select[name$="-material"]');
      const materialId = select ? select.value : null;
      if (!materialId) { alert("Selecciona un material para editar."); return; }

      _rememberActiveMaterialSelectFromRow(btnElement);

      const url = `/dashboard/project/${projectId}/catalogos/material/edit/${materialId}/?popup=1`;
      window.open(url, "Editar Material",
        `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`);
    } catch (err) {
      console.error("[materials_formset] openEditMaterialPopup error", err);
    }
  };

  // -------- Callbacks desde el popup --------
  window.closePopupAndAddMaterial = function (id, label) {
    let sel = window._materialActiveSelect;
    if (!sel) {
      const all = document.querySelectorAll('select[name$="-material"]');
      sel = all.length ? all[all.length - 1] : null;
    }
    if (!sel) return;

    const vid = String(id);
    let opt = _findOption(sel, vid);
    if (!opt) {
      opt = new Option(label, vid, true, true);
      sel.add(opt);
    } else {
      opt.text = label;
      sel.value = vid;
    }
    sel.value = vid;
    _refreshSelect2(sel);
  };

  window.updateMaterialInSelect = function (id, label) {
    const vid = String(id);
    const selects = document.querySelectorAll('select[name$="-material"]');

    selects.forEach(sel => {
      let opt = _findOption(sel, vid);
      if (!opt) {
        opt = new Option(label, vid, false, false);
        sel.add(opt);
      }

      const wasSelected = String(sel.value) === vid;
      opt.text = label;
      if (wasSelected) sel.value = vid;

      _ensureSelect2Change(sel);

      // Reinit suave si el render no refleja el nuevo texto (cuando estaba seleccionado)
      if (isSelect2Available() && jQuery(sel).data("select2") && wasSelected) {
        const $sel = jQuery(sel);
        const rendered = $sel.next(".select2").find(".select2-selection__rendered");
        if (rendered.length && rendered.text().trim() !== label.trim()) {
          $sel.select2("destroy");
          initSelect2On(sel);
          $sel.val(vid).trigger("change");
        }
      }
    });
  };
})();
