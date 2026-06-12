/**
 * Bulk Actions — Password Injection
 *
 * Monkey-patcha $.ajax para interceptar requisições de bulk-action
 * e injetar `user_password` no payload antes de enviar.
 *
 * Endpoint alvo: POST /datatables/bulk-action/
 */

(function ($) {
  if (!$ || !$.ajax) return;

  const BULK_ACTION_URL_PATTERN = /\/datatables\/bulk-action\//;
  const originalAjax = $.ajax.bind($);

  $.ajax = function (urlOrSettings, settings) {
    let opts = (typeof urlOrSettings === 'string')
      ? Object.assign({ url: urlOrSettings }, settings)
      : Object.assign({}, urlOrSettings);

    if (opts.url && BULK_ACTION_URL_PATTERN.test(opts.url)) {
      opts = _injectPassword(opts);
    }

    return originalAjax(opts);
  };

  function _injectPassword(opts) {
    const password = _getPasswordFromModal();
    if (!password) return opts;

    if (opts.contentType && opts.contentType.includes('application/json')) {
      try {
        const body = JSON.parse(opts.data || '{}');
        body.user_password = password;
        opts.data = JSON.stringify(body);
      } catch (e) {}

    } else if (opts.data instanceof FormData) {
      opts.data.set('user_password', password);

    } else if (typeof opts.data === 'string') {
      opts.data += (opts.data ? '&' : '') + 'user_password=' + encodeURIComponent(password);

    } else if (opts.data && typeof opts.data === 'object') {
      opts.data.user_password = password;
    }

    return opts;
  }

  function _getPasswordFromModal() {
    const selectors = [
      '[id*="bulk_confirm_password"]',
      '[id*="bulk_action_password"]',
      '[name="user_password"]',
      '.bulk-action-password-field',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.value) return el.value;
    }
    return null;
  }

})(window.jQuery);