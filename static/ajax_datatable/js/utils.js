/**
 * AjaxDatatableViewUtils
 * Utilitarios para inicializar DataTables conectadas ao backend Django.
 */
var AjaxDatatableViewUtils = (function ($) {
  'use strict';

  function initialize_table(element, url, extra_options, extra_data) {
    extra_options = extra_options || {};
    extra_data    = extra_data    || {};

    var $table = $(element);
    if (!$table.length) { console.warn('AjaxDatatableViewUtils: elemento nao encontrado:', element); return null; }

    if ($.fn.DataTable && $.fn.DataTable.isDataTable($table)) { return $table.DataTable(); }

    var options = $.extend(true, {
      serverSide:  true,
      processing:  true,
      ajax: {
        url:  url,
        type: 'GET',
        data: function (d) { return $.extend(d, extra_data); }
      },
      language: {
        url:            '',
        decimal:        ',',
        thousands:      '.',
        processing:     '<span class="spinner-border spinner-border-sm"></span>',
        emptyTable:     'Nenhum registro encontrado',
        zeroRecords:    'Nenhum registro encontrado',
        info:           'Mostrando _START_ a _END_ de _TOTAL_ registros',
        infoEmpty:      'Mostrando 0 a 0 de 0 registros',
        infoFiltered:   '(filtrado de _MAX_ registros no total)',
        lengthMenu:     'Exibir _MENU_ registros',
        loadingRecords: 'Carregando...',
        search:         'Buscar:',
        paginate: { first: 'Primeiro', last: 'Ultimo', next: 'Proximo', previous: 'Anterior' }
      },
      pageLength: 10,
      dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>><'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
    }, extra_options);

    var dt = $table.DataTable(options);
    _initColumnFilters($table, dt);
    _initDaterangeWidget($table, dt);
    _initRowTools($table, dt);
    return dt;
  }

  function _initColumnFilters($table, dt) {
    var $filters = $table.closest('.datatable-wrapper').find('[data-column-filter]');
    if (!$filters.length) return;
    $filters.on('input change', function () {
      var colIndex = parseInt($(this).data('columnFilter'), 10);
      dt.column(colIndex).search(this.value).draw();
    });
  }

  function _initDaterangeWidget($table, dt) {
    var $wrapper = $table.closest('.datatable-wrapper');
    var $start = $wrapper.find('[data-daterange-start]');
    var $end   = $wrapper.find('[data-daterange-end]');
    if (!$start.length || !$end.length) return;
    function applyDateRange() {
      var colIndex = parseInt($start.data('daterangeStart'), 10);
      var search = ($start.val() || $end.val()) ? ($start.val() + '|' + $end.val()) : '';
      dt.column(colIndex).search(search).draw();
    }
    $start.on('change', applyDateRange);
    $end.on('change', applyDateRange);
  }

  function _initRowTools($table, dt) {
    $table.on('click', '[data-row-action]', function (e) {
      e.preventDefault();
      var action   = $(this).data('rowAction');
      var objectId = $(this).closest('tr').data('id') || $(this).data('objectId');
      if (typeof window.handleRowAction === 'function') window.handleRowAction(action, objectId, $(this));
    });
  }

  return { initialize_table: initialize_table };
})(window.jQuery);