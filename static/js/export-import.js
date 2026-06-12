/**
 * DataTable Export / Import
 * POST /datatables/export/  |  POST /datatables/import/
 */
window.DatatableExportImport = (function ($) {

  function init(options) {
    const opts = Object.assign({
      datatableKey: null,
      exportButtonSelector: '[data-export-datatable]',
      importFormSelector:   '#importForm',
      importFileSelector:   '#importFile',
      exportUrl:            '/datatables/export/',
      importUrl:            '/datatables/import/',
    }, options);
    initExport(opts);
    initImport(opts);
  }

  function initExport(opts) {
    $(document).on('click', opts.exportButtonSelector, function (e) {
      e.preventDefault();
      const datatableKey = $(this).data('exportDatatable') || opts.datatableKey;
      const format       = $(this).data('format') || 'xlsx';
      processExport(datatableKey, format, opts.exportUrl);
    });
  }

  function processExport(datatableKey, format, exportUrl) {
    if (!datatableKey) { console.warn('DatatableExportImport: datatableKey required'); return; }
    const csrfToken = _getCsrfToken();
    const $btn = $('[data-export-datatable="' + datatableKey + '"]');
    _setLoading($btn, true);

    $.ajax({
      url:    exportUrl,
      method: 'POST',
      data:   JSON.stringify({ datatable_key: datatableKey, format: format }),
      contentType: 'application/json',
      headers: { 'X-CSRFToken': csrfToken },
      xhrFields: { responseType: 'blob' },
      success: function (blob, status, xhr) {
        const disposition = xhr.getResponseHeader('Content-Disposition') || '';
        const match    = disposition.match(/filename[^;=\n]*=((['"]).+?\2|[^;\n]*)/);
        const filename = match ? match[1].replace(/['"]/g, '') : ('export.' + format);
        const url  = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url; link.download = filename;
        document.body.appendChild(link); link.click();
        document.body.removeChild(link); URL.revokeObjectURL(url);
      },
      error: function (xhr) {
        const msg = xhr.responseJSON ? xhr.responseJSON.message : 'Erro ao exportar dados';
        if (typeof window.showToast === 'function') window.showToast(msg, 'error');
      },
      complete: function () { _setLoading($btn, false); }
    });
  }

  function initImport(opts) {
    $(document).on('submit', opts.importFormSelector, function (e) {
      e.preventDefault();
      const $form       = $(this);
      const datatableKey = $form.data('datatableKey') || opts.datatableKey;
      const $fileInput  = $form.find(opts.importFileSelector);
      if (!$fileInput[0] || !$fileInput[0].files.length) {
        if (typeof window.showToast === 'function') window.showToast('Selecione um arquivo', 'warning');
        return;
      }
      processImport(datatableKey, $fileInput[0].files[0], opts.importUrl, $form);
    });
  }

  function processImport(datatableKey, file, importUrl, $form) {
    if (!datatableKey) { console.warn('DatatableExportImport: datatableKey required'); return; }
    const csrfToken = _getCsrfToken();
    const formData  = new FormData();
    formData.append('datatable_key', datatableKey);
    formData.append('file', file);
    const $submitBtn = $form ? $form.find('[type=submit]') : $();
    _setLoading($submitBtn, true);

    $.ajax({
      url: importUrl, method: 'POST', data: formData,
      processData: false, contentType: false,
      headers: { 'X-CSRFToken': csrfToken },
      success: function (response) {
        if (response.success) {
          if (typeof window.showToast === 'function') window.showToast(response.message || 'Importacao concluida', 'success');
          const $table = $('[data-datatable-key="' + datatableKey + '"]');
          if ($table.length && $.fn.DataTable && $.fn.DataTable.isDataTable($table)) $table.DataTable().ajax.reload(null, false);
          const $modal = $form ? $form.closest('.modal') : $();
          if ($modal.length) $modal.modal('hide');
        } else {
          if (typeof window.showToast === 'function') window.showToast(response.message || 'Erro na importacao', 'error');
        }
      },
      error: function (xhr) {
        const msg = xhr.responseJSON ? xhr.responseJSON.message : 'Erro ao importar dados';
        if (typeof window.showToast === 'function') window.showToast(msg, 'error');
      },
      complete: function () { _setLoading($submitBtn, false); }
    });
  }

  function _getCsrfToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }

  function _setLoading($el, loading) {
    if (!$el || !$el.length) return;
    if (loading) {
      $el.data('original-html', $el.html());
      $el.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span>Aguarde...');
    } else {
      $el.prop('disabled', false).html($el.data('original-html') || $el.html());
    }
  }

  return { init, processExport, processImport };
})(window.jQuery);