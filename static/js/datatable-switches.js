/**
 * Sistema de Switches para DataTables
 */

function toggleDatatableField(switchElement) {
  const fieldName         = switchElement.dataset.field;
  const objectId          = switchElement.dataset.objectId;
  const datatableKey      = switchElement.dataset.datatableKey;
  const confirmMessage    = switchElement.dataset.confirmMessage;
  const confirmOnActivate = switchElement.dataset.confirmOnActivate === 'true';
  const confirmOnDisable  = switchElement.dataset.confirmOnDisable  === 'true';
  const customMethod      = switchElement.dataset.method;
  const newValue          = switchElement.checked;
  const needsConfirmation = (newValue && confirmOnActivate) || (!newValue && confirmOnDisable);

  if (needsConfirmation && confirmMessage) {
    showSwitchConfirmModal(confirmMessage,
      () => executeSwitchToggle(switchElement, fieldName, objectId, datatableKey, newValue, customMethod),
      () => { switchElement.checked = !newValue; }
    );
  } else {
    executeSwitchToggle(switchElement, fieldName, objectId, datatableKey, newValue, customMethod);
  }
}

function executeSwitchToggle(switchElement, fieldName, objectId, datatableKey, newValue, customMethod) {
  switchElement.disabled = true;
  const requestData = { datatable_key: datatableKey, object_id: objectId, field_name: fieldName, new_value: newValue };
  if (customMethod) requestData.custom_method = customMethod;
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  $.ajax({
    url: '/datatables/toggle-field/',
    method: 'POST',
    data: JSON.stringify(requestData),
    contentType: 'application/json',
    headers: {'X-CSRFToken': csrfToken},
    success: function (response) {
      if (!response.success) {
        switchElement.checked = !newValue;
        if (typeof window.showToast === 'function') window.showToast(response.message || 'Erro ao atualizar campo', 'error');
      }
    },
    error: function () {
      switchElement.checked = !newValue;
      if (typeof window.showToast === 'function') window.showToast('Erro de comunicacao com o servidor', 'error');
    },
    complete: function () { switchElement.disabled = false; }
  });
}

function showSwitchConfirmModal(message, onConfirm, onCancel) {
  const confirmModals = document.querySelectorAll('[id*="bulk_action_confirm_modal"]');
  if (confirmModals.length === 0) return;
  const modal = confirmModals[0];
  modal.dataset.switchMode = 'true';
  window.switchConfirmCallback = onConfirm;
  window.switchCancelCallback  = onCancel;

  const messageElement  = modal.querySelector('[id*="bulk_confirm_message"]');
  const countElement    = modal.querySelector('[id*="bulk_confirm_count"]');
  const scopeElement    = modal.querySelector('[id*="bulk_confirm_scope"]');
  const passwordSection = modal.querySelector('[id*="bulk_confirm_password_section"]');
  const confirmButton   = modal.querySelector('[id*="bulk_confirm_execute"]');

  if (messageElement)  messageElement.textContent = message;
  if (countElement)    countElement.style.display  = 'none';
  if (scopeElement)    scopeElement.style.display   = 'none';
  if (passwordSection) passwordSection.classList.add('d-none');
  if (confirmButton)  { confirmButton.disabled = false; confirmButton.classList.remove('disabled'); }

  $(modal).off('click.switch', '[id*="bulk_confirm_execute"]')
    .on('click.switch', '[id*="bulk_confirm_execute"]', function (e) {
      if (modal.dataset.switchMode !== 'true') return;
      e.preventDefault(); e.stopPropagation();
      modal.dataset.switchOnConfirm = 'confirmed';
      $(modal).modal('hide');
      setTimeout(() => { if (typeof window.switchConfirmCallback === 'function') window.switchConfirmCallback(); }, 100);
    });

  $(modal).off('hidden.bs.modal.switch').on('hidden.bs.modal.switch', function () {
    if (modal.dataset.switchMode !== 'true') return;
    if (modal.dataset.switchOnConfirm !== 'confirmed')
      if (typeof window.switchCancelCallback === 'function') window.switchCancelCallback();
    setTimeout(() => cleanupSwitchModal(modal), 100);
  });

  try { $(modal).modal('show'); } catch (e) {}
}

function cleanupSwitchModal(modal) {
  const countElement = modal.querySelector('[id*="bulk_confirm_count"]');
  const scopeElement = modal.querySelector('[id*="bulk_confirm_scope"]');
  if (countElement) countElement.style.display = '';
  if (scopeElement) scopeElement.style.display = '';
  delete modal.dataset.switchMode;
  delete modal.dataset.switchOnConfirm;
  delete window.switchConfirmCallback;
  delete window.switchCancelCallback;
  $(modal).off('.switch');
}