/**
 * DataTable Auto Refresh Helper
 */
(function (global, $) {
  const REGISTRY_KEY = '__datatableRefreshRegistry';

  if (!global[REGISTRY_KEY]) {
    Object.defineProperty(global, REGISTRY_KEY, {
      value: Object.create(null),
      writable: false,
      enumerable: false,
      configurable: false
    });
  }

  function normalizeSelector(idOrSelector) {
    if (typeof idOrSelector !== 'string') return null;
    const trimmed = idOrSelector.trim();
    if (!trimmed) return null;
    if (trimmed.startsWith('#') || trimmed.startsWith('.')) return trimmed;
    return '#' + trimmed;
  }

  function clearIntervalFor(selector) {
    const reg = global[REGISTRY_KEY];
    if (reg[selector]) {
      clearInterval(reg[selector]);
      delete reg[selector];
    }
  }

  function tick(selector) {
    const $table = $(selector);
    if ($table.length === 0) { clearIntervalFor(selector); return; }
    if (document.hidden) return;
    try {
      if ($ && $.fn && $.fn.DataTable && $.fn.DataTable.isDataTable($table)) {
        $table.DataTable().draw(false);
      }
    } catch (err) {}
  }

  function startDatatableAutoRefresh(idOrSelector, intervalMs = 10000) {
    const selector = normalizeSelector(idOrSelector);
    if (!selector) return;
    clearIntervalFor(selector);
    const id = setInterval(() => tick(selector), intervalMs);
    global[REGISTRY_KEY][selector] = id;
    return id;
  }

  function stopDatatableAutoRefresh(idOrSelector) {
    const selector = normalizeSelector(idOrSelector);
    if (!selector) return;
    clearIntervalFor(selector);
  }

  function stopAllDatatableAutoRefresh() {
    const reg = global[REGISTRY_KEY];
    Object.keys(reg).forEach((key) => { clearInterval(reg[key]); delete reg[key]; });
  }

  global.startDatatableAutoRefresh   = startDatatableAutoRefresh;
  global.stopDatatableAutoRefresh    = stopDatatableAutoRefresh;
  global.stopAllDatatableAutoRefresh = stopAllDatatableAutoRefresh;

  if (global.addEventListener) {
    global.addEventListener('beforeunload', stopAllDatatableAutoRefresh);
  }
})(window, window.jQuery);