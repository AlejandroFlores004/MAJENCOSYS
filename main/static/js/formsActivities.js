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
  window.openToolPopup = function (projectId) {
    const width = 600;
    const height = 400;
    // Calcula el centro
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

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

  window.openLabourPopup = function (projectId) {
    const width = 600;
    const height = 400;
    // Calcula el centro
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
})(); // IIFE
