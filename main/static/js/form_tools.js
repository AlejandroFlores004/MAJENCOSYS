// static/js/tools_formset.js
(function () {
  // ---------------------- Helpers ----------------------
  function log(...args) { if (window.console) console.log("[tools_formset]", ...args); }
  function isSelect2Available() {
    return window.jQuery && jQuery.fn && typeof jQuery.fn.select2 === "function";
  }
  function initSelect2On(el) {
    if (!el || !isSelect2Available()) return;
    try {
      jQuery(el).select2({
        placeholder: "Buscar herramienta...",
        allowClear: true,
        width: "100%"
      });
    } catch (err) {
      console.error("[tools_formset] initSelect2On error", err);
    }
  }

  // ====== Estado: select activo de herramientas ======
  window._toolActiveSelect = null;

  // Guardar el select activo cuando se abre el popup (crear)
  const _rememberActiveToolSelectFromButton = (btnEl) => {
    try {
      const row = (btnEl && btnEl.closest(".tool-form")) || null;
      window._toolActiveSelect = row ? row.querySelector('select[name$="-tool"]') : null;
    } catch {
      window._toolActiveSelect = null;
    }
  };

  // Guardar el select activo cuando se abre el popup (editar)
  const _rememberActiveToolSelectFromRow = (btnEl) => {
    try {
      const row = (btnEl && (btnEl.closest(".tool-form") || btnEl.closest(".row"))) || null;
      window._toolActiveSelect = row ? row.querySelector('select[name$="-tool"]') : null;
    } catch {
      window._toolActiveSelect = null;
    }
  };

  // ====== Helpers para actualizar selects ======
  function _ensureSelect2Change(el) {
    if (!el) return;
    // Select2 4.x escucha 'change' normal.
    try {
      if (isSelect2Available() && jQuery(el).data('select2')) {
        jQuery(el).trigger('change'); // <- clave
      } else {
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    } catch {
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  function _refreshSelect2(sel) {
    if (!sel) return;
    try {
      if (isSelect2Available() && jQuery(sel).data('select2')) {
        // forzar que Select2 rehaga el render del label seleccionado
        jQuery(sel).trigger('change'); // <- NO usar change.select2
      } else {
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    } catch {
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

function _findOption(sel, id) {
  const vid = String(id);
  return Array.from(sel.options).find(o => String(o.value) === vid) || null;
}


  function _refreshSelect2(sel) {
  if (!sel) return;
  if (isSelect2Available()) {
    try {
      const $sel = jQuery(sel);
      // asegúrate de que Select2 repinte el label seleccionado
      if ($sel.data("select2")) {
        $sel.trigger("change.select2");
      } else {
        $sel.trigger("change");
      }
    } catch {
      sel.dispatchEvent(new Event("change"));
    }
  } else {
    sel.dispatchEvent(new Event("change"));
  }
}

function _findOption(sel, id) {
  const vid = String(id);
  return Array.from(sel.options).find(o => String(o.value) === vid) || null;
}


  // ---------------------- DOM ready ----------------------
  document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("tools-formset");
    if (!container) { console.error("[tools_formset] container #tools-formset no encontrado"); return; }

    const addButton = document.getElementById("add-tool");
    if (!addButton) { console.error("[tools_formset] botón #add-tool no encontrado"); return; }

    const templateEl = document.getElementById("tool-empty-form");
    if (!templateEl) { console.error("[tools_formset] template #tool-empty-form no encontrado"); return; }

    const totalFormsInput = container.querySelector('input[name$="-TOTAL_FORMS"]');
    if (!totalFormsInput) { console.error("[tools_formset] input TOTAL_FORMS no encontrado"); return; }

    // Inicializa Select2 en los selects existentes (si está disponible)
    const existingSelects = container.querySelectorAll('select[name$="-tool"]');
    existingSelects.forEach(s => initSelect2On(s));

    // Click para agregar un nuevo form
    addButton.addEventListener("click", function () {
      // calcula índice (fallback por si TOTAL_FORMS no es numérico)
      const formIndex = Number.parseInt(totalFormsInput.value, 10) || container.querySelectorAll('.tool-form').length;
      // remplaza __prefix__ usando regex global (mejor compatibilidad que replaceAll)
      const html = templateEl.innerHTML.replace(/__prefix__/g, String(formIndex));

      // Inserta el nuevo form antes del botón
      addButton.insertAdjacentHTML("beforebegin", html);

      // Incrementa TOTAL_FORMS
      totalFormsInput.value = String(formIndex + 1);

      // Busca el nuevo row insertado (último .tool-form)
      const rows = container.querySelectorAll(".tool-form");
      const newRow = rows[rows.length - 1] || null;

      // Inicializa Select2 en el select del nuevo row (si existe)
      if (newRow) {
        const newSelect = newRow.querySelector('select[name$="-tool"]');
        initSelect2On(newSelect);
      } else {
        // fallback: intenta inicializar el último select en todo el container
        const lastSelect = container.querySelectorAll('select[name$="-tool"]');
        if (lastSelect.length) initSelect2On(lastSelect[lastSelect.length - 1]);
      }
    });

    // Delegación: marcar visualmente filas eliminadas
    container.addEventListener("change", function (e) {
      if (e.target && e.target.type === "checkbox" && e.target.name && e.target.name.endsWith("-DELETE")) {
        const row = e.target.closest(".tool-form");
        if (row) row.classList.toggle("opacity-50", e.target.checked);
      }
    });

    log("tools_formset inicializado");
  }); // DOMContentLoaded


  // ---------------------- FUNCIONES POPUP (expuestas en window) ----------------------
  // ---- TOOLS: abrir popups ----
  window.openToolPopup = function (projectId) {
    const width = 600;
    const height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    // Intenta tomar el botón actualmente activo (para recordar el select de su fila)
    const btn = document.activeElement;
    _rememberActiveToolSelectFromButton(btn);

    const url = `/dashboard/project/${projectId}/catalogos/tools/?popup=1`;
    window.open(
      url,
      "Agregar Herramienta",
      `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`
    );
  };

  window.openEditToolPopup = function (projectId, btnElement) {
    const width = 600;
    const height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    try {
      const row = btnElement.closest(".row") || btnElement.closest(".tool-form");
      if (!row) { alert("No se pudo localizar la fila de la herramienta."); return; }
      const select = row.querySelector('select[name$="-tool"]');
      const toolId = select ? select.value : null;
      if (!toolId) { alert("Selecciona una herramienta para editar."); return; }

      // Recuerda el select de esta fila para refrescarlo al volver
      _rememberActiveToolSelectFromRow(btnElement);

      const url = `/dashboard/project/${projectId}/catalogos/tools/edit/${toolId}/?popup=1`;
      window.open(
        url,
        "Editar Herramienta",
        `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`
      );
    } catch (err) {
      console.error("[tools_formset] openEditToolPopup error", err);
    }
  };

  // ---- TOOLS: funciones que invoca el popup en el padre ----
  // Añadir (o seleccionar) una herramienta recién creada en el select activo
  window.closePopupAndAddTool = function (id, label) {
    // Usa el select activo; si no hay, toma el último de la página
    let sel = window._toolActiveSelect;
    if (!sel) {
      const all = document.querySelectorAll('select[name$="-tool"]');
      sel = all.length ? all[all.length - 1] : null;
    }
    if (!sel) return;

    const vid = String(id);
    let opt = _findOption(sel, vid);

    if (!opt) {
      // crear y seleccionar
      opt = new Option(label, vid, true, true);
      sel.add(opt);
    } else {
      // actualizar texto y seleccionar
      opt.text = label;
      sel.value = vid;
    }

    // Garantiza que quede seleccionado ese value
    sel.value = vid;
    _refreshSelect2(sel);
  };

  // Actualizar el texto de la herramienta editada en TODOS los selects que la tengan
  window.updateToolInSelect = function (id, label) {
    const vid = String(id);
    const selects = document.querySelectorAll('select[name$="-tool"]');

    selects.forEach(sel => {
      // 1) Busca (o crea) la opción
      let opt = _findOption(sel, vid);
      if (!opt) {
        opt = new Option(label, vid, false, false);
        sel.add(opt);
      }

      // 2) Actualiza el texto SIEMPRE (seleccionada o no)
      opt.text = label;

      // 3) Si está seleccionada en este select, re-asigna el valor para asegurar estado
      const wasSelected = String(sel.value) === vid;
      if (wasSelected) {
        sel.value = vid; // reafirma selección
      }

      // 4) Dispara el cambio para que Select2 repinte
      _ensureSelect2Change(sel);

      // 5) (Opcional) Si por alguna razón no repintó (algunas versiones de Select2 cachean),
      //    fuerza un reinit rápido SOLO cuando estaba seleccionada y el texto visible no cambió.
      if (isSelect2Available() && jQuery(sel).data('select2') && wasSelected) {
        const $sel = jQuery(sel);
        // Chequeo simple del render actual
        const rendered = $sel.next('.select2').find('.select2-selection__rendered');
        if (rendered.length && rendered.text().trim() !== label.trim()) {
          // re-init suave
          $sel.select2('destroy');
          initSelect2On(sel);
          $sel.val(vid).trigger('change');
        }
      }
    });
  };


  // ---- LABOUR: (dejamos tus funciones tal como estaban) ----
  window.openLabourPopup = function (projectId) {
    const width = 600;
    const height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);
    const url = `/dashboard/project/${projectId}/catalogos/mano_obra/?popup=1`;
    window.open(
      url,
      "Agregar Mano de Obra",
      `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`
    );
  };

  window.openEditLabourPopup = function (projectId, btnElement) {
    const width = 600;
    const height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    try {
      const row = btnElement.closest(".row") || btnElement.closest(".labour-form");
      if (!row) { alert("No se pudo localizar la fila de la mano de obra."); return; }
      const select = row.querySelector('select[name$="-labour"]');
      const labourId = select ? select.value : null;
      if (!labourId) { alert("Selecciona una mano de obra para editar."); return; }
      const url = `/dashboard/project/${projectId}/catalogos/mano_obra/edit/${labourId}/?popup=1`;
      window.open(
        url,
        "Editar Mano de Obra",
        `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`
      );
    } catch (err) {
      console.error("[tools_formset] openEditLabourPopup error", err);
    }
  };

  // ====== Estado: select activo de mano de obra ======
  window._labourActiveSelect = null;

  const _rememberActiveLabourSelectFromButton = (btnEl) => {
    try {
      const row = (btnEl && btnEl.closest(".labour-form")) || null;
      window._labourActiveSelect = row ? row.querySelector('select[name$="-labour"]') : null;
    } catch {
      window._labourActiveSelect = null;
    }
  };

  const _rememberActiveLabourSelectFromRow = (btnEl) => {
    try {
      const row = (btnEl && (btnEl.closest(".labour-form") || btnEl.closest(".row"))) || null;
      window._labourActiveSelect = row ? row.querySelector('select[name$="-labour"]') : null;
    } catch {
      window._labourActiveSelect = null;
    }
  };

  // ====== DOM ready (bloque adicional para Mano de Obra) ======
  document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("labours-formset");
    if (!container) return; // puede no estar en todas las páginas

    const addButton = document.getElementById("add-labour");
    const templateEl = document.getElementById("labour-empty-form");
    const totalFormsInput = container.querySelector('input[name$="-TOTAL_FORMS"]');

    if (!addButton || !templateEl || !totalFormsInput) {
      console.error("[labours_formset] faltan elementos (botón/template/TOTAL_FORMS)");
      return;
    }

    // init Select2 en selects existentes
    container.querySelectorAll('select[name$="-labour"]').forEach(s => initSelect2On(s));

    // Agregar fila
    addButton.addEventListener("click", function () {
      const formIndex = Number.parseInt(totalFormsInput.value, 10) || container.querySelectorAll('.labour-form').length;
      const html = templateEl.innerHTML.replace(/__prefix__/g, String(formIndex));
      addButton.insertAdjacentHTML("beforebegin", html);
      totalFormsInput.value = String(formIndex + 1);

      // init Select2 en el nuevo select
      const rows = container.querySelectorAll(".labour-form");
      const newRow = rows[rows.length - 1] || null;
      if (newRow) {
        const newSelect = newRow.querySelector('select[name$="-labour"]');
        initSelect2On(newSelect);
      }
    });

    // Opacidad si se marca DELETE
    container.addEventListener("change", function (e) {
      if (e.target && e.target.type === "checkbox" && e.target.name && e.target.name.endsWith("-DELETE")) {
        const row = e.target.closest(".labour-form");
        if (row) row.classList.toggle("opacity-50", e.target.checked);
      }
    });
  });

  // ====== POPUPS Mano de Obra ======
  window.openLabourPopup = function (projectId) {
    const width = 600, height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    const btn = document.activeElement;
    _rememberActiveLabourSelectFromButton(btn);

    const url = `/dashboard/project/${projectId}/catalogos/mano_obra/?popup=1`;
    window.open(url, "Agregar Mano de Obra",
      `width=${width},height=${height},resizable=yes,scrollbars=yes,left=${left},top=${top}`);
  };

  window.openEditLabourPopup = function (projectId, btnElement) {
    const width = 600, height = 400;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

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

  // ====== Callbacks desde el popup (Mano de Obra) ======
  window.closePopupAndAddLabour = function (id, label) {
    // Usa el select activo; si no hay, toma el último
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

      // Re-init suave si hiciera falta (texto visible no coincide)
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

})(); // IIFE
