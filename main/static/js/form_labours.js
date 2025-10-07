(function () {
  // ---------- Helpers ----------
  function isSelect2Available() {
    return window.jQuery && jQuery.fn && typeof jQuery.fn.select2 === "function";
  }
  function initSelect2On(el) {
    if (!el || !isSelect2Available()) return;
    try {
      jQuery(el).select2({
        placeholder: "Buscar mano de obra...",
        allowClear: true,
        width: "100%"
      });
    } catch (err) {
      console.error("[labours_formset] initSelect2On error", err);
    }
  }
  function _ensureSelect2Change(el) {
    if (!el) return;
    try {
      if (isSelect2Available() && jQuery(el).data("select2")) {
        jQuery(el).trigger("change"); // Select2 4.x escucha 'change'
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

  // ---------- Estado: select activo (para popup) ----------
  window._labourActiveSelect = null;
  function _rememberActiveLabourSelectFromButton(btnEl) {
    try {
      const row = (btnEl && btnEl.closest(".labour-form")) || null;
      window._labourActiveSelect = row ? row.querySelector('select[name$="-labour"]') : null;
    } catch {
      window._labourActiveSelect = null;
    }
  }
  function _rememberActiveLabourSelectFromRow(btnEl) {
    try {
      const row = (btnEl && (btnEl.closest(".labour-form") || btnEl.closest(".row"))) || null;
      window._labourActiveSelect = row ? row.querySelector('select[name$="-labour"]') : null;
    } catch {
      window._labourActiveSelect = null;
    }
  }

  // ---------- DOM Ready ----------
  document.addEventListener("DOMContentLoaded", function () {
    const container  = document.getElementById("labours-formset");
    if (!container) return;

    const addButton  = document.getElementById("add-labour");
    const totalForms = container.querySelector('input[name$="-TOTAL_FORMS"]');
    const proto      = document.getElementById("labour-empty-form");

    if (!addButton || !totalForms || !proto) {
      console.error("[labours_formset] faltan elementos (botón/template/TOTAL_FORMS)");
      return;
    }

    // Init Select2 en selects existentes
    container.querySelectorAll('select[name$="-labour"]').forEach(initSelect2On);

    // Agregar fila
    addButton.addEventListener("click", function () {
      const index = Number.parseInt(totalForms.value, 10) || container.querySelectorAll(".labour-form").length;
      const html  = proto.innerHTML.replace(/__prefix__/g, String(index)); // regex g, compatible
      addButton.insertAdjacentHTML("beforebegin", html);
      totalForms.value = String(index + 1);

      // init Select2 en el nuevo select
      const rows = container.querySelectorAll(".labour-form");
      const newRow = rows[rows.length - 1] || null;
      if (newRow) {
        const newSelect = newRow.querySelector('select[name$="-labour"]');
        initSelect2On(newSelect);
      }
    });

    // Marcar DELETE con opacidad
    container.addEventListener("change", function(e) {
      if (e.target && e.target.type === "checkbox" && e.target.name.endsWith("-DELETE")) {
        const row = e.target.closest(".labour-form");
        if (row) row.classList.toggle("opacity-50", e.target.checked);
      }
    });
  });

  // ---------- POPUPS ----------
  window.openLabourPopup = function (projectId) {
    const width = 600, height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top  = (window.screen.height / 2) - (height / 2);

    const btn = document.activeElement;
    _rememberActiveLabourSelectFromButton(btn);

    const url = `/dashboard/project/${projectId}/catalogos/mano_obra/?popup=1`;
    window.open(url, "Agregar Mano de Obra",
      `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`);
  };

  window.openEditLabourPopup = function (projectId, btnElement) {
    const width = 600, height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top  = (window.screen.height / 2) - (height / 2);

    try {
      const row = btnElement.closest(".row") || btnElement.closest(".labour-form");
      if (!row) { alert("No se pudo localizar la fila de la mano de obra."); return; }
      const select = row.querySelector('select[name$="-labour"]');
      const labourId = select ? select.value : null;
      if (!labourId) { alert("Selecciona una mano de obra para editar."); return; }

      _rememberActiveLabourSelectFromRow(btnElement);

      const url = `/dashboard/project/${projectId}/catalogos/mano_obra/edit/${labourId}/?popup=1`;
      window.open(url, "Editar Mano de Obra",
        `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`);
    } catch (err) {
      console.error("[labours_formset] openEditLabourPopup error", err);
    }
  };

  // ---------- Callbacks invocados por el popup ----------
  window.closePopupAndAddLabour = function (id, label) {
    let sel = window._labourActiveSelect;
    if (!sel) {
      const all = document.querySelectorAll('select[name$="-labour"]');
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

  window.updateLabourInSelect = function (id, label) {
    const vid = String(id);
    const selects = document.querySelectorAll('select[name$="-labour"]');

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

      // Reinit suave si el render visible no coincide (solo cuando estaba seleccionado)
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