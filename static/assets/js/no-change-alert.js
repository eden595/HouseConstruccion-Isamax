(function () {
  'use strict';

  const DEFAULT_TITLE = 'No se realizaron cambios.';
  const DEFAULT_TEXT = 'No modificaste ningún dato.';

  function captureFormState(form) {
    const data = new FormData(form);
    const snapshot = {};
    data.forEach((value, key) => {
      if (key === 'csrfmiddlewaretoken') return;
      if (value instanceof File) {
        snapshot[key] = value.name || '';
      } else {
        snapshot[key] = String(value);
      }
    });
    return snapshot;
  }

  function formHasChanged(initial, current) {
    const keys = new Set([
      ...Object.keys(initial),
      ...Object.keys(current)
    ]);
    for (const key of keys) {
      const before = initial[key] ?? '';
      const after = current[key] ?? '';
      if (before !== after) {
        return true;
      }
    }
    return false;
  }

  function showAlert(options = {}) {
    const title = options.title || DEFAULT_TITLE;
    const text = options.text || DEFAULT_TEXT;
    const timer = typeof options.timer === 'number' ? options.timer : 1800;

    if (typeof window.Swal !== 'function') {
      alert(`${title}\n${text}`);
      return Promise.resolve();
    }

    return Swal.fire({
      icon: 'info',
      title,
      text,
      position: 'center',
      toast: false,
      showConfirmButton: false,
      timer
    });
  }

  function attachWatcher(form, opts = {}) {
    if (!form || form.dataset.noChangeWatcher === '1') return;
    if (form.dataset.editMode === '0') return;
    form.dataset.noChangeWatcher = '1';

    const initialState = captureFormState(form);
    form.addEventListener('submit', (event) => {
      const currentState = captureFormState(form);
      if (!formHasChanged(initialState, currentState)) {
        event.preventDefault();
        showAlert(opts.message || {}).then(() => {
          if (typeof opts.onNoChange === 'function') {
            opts.onNoChange();
          }
        });
      }
    });
  }

  window.attachNoChangeSweetAlert = function (options = {}) {
    if (!options || !options.form) return;
    const target = typeof options.form === 'string'
      ? document.querySelector(options.form)
      : options.form;
    attachWatcher(target, options);
  };
})();
