(function () {
  'use strict';

  const STORAGE_KEY = 'hc_seen_swal_messages_v1';

  function getSeen() {
    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]');
    } catch (e) {
      return [];
    }
  }

  function remember(messages) {
    const seen = getSeen();
    const merged = seen.concat(messages).slice(-30);
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    } catch (e) {
      /* ignore quota errors */
    }
  }

  function normalize(msg) {
    if (!msg) return '';
    const level = (msg.level || '').toString().trim().toLowerCase();
    const text = (msg.text || '').toString().trim();
    return `${window.location.pathname}|${level}|${text}`;
  }

  function pickIcon(level) {
    if (!level) return 'info';
    const norm = level.toString().toLowerCase();
    if (norm.includes('success')) return 'success';
    if (norm.includes('error')) return 'error';
    if (norm.includes('warning')) return 'warning';
    if (norm.includes('info')) return 'info';
    return 'info';
  }

  function showMessages(messages, opts = {}) {
    if (!window.Swal || !Array.isArray(messages) || !messages.length) return;

    const mapped = messages
      .filter(m => m && (m.text || m.title))
      .map(m => ({
        icon: pickIcon(m.level),
        title: m.title || m.text || 'Información',
        text: m.text,
        key: normalize(m),
        level: (m.level || '').toString().toLowerCase(),
      }));

    if (!mapped.length) return;

    const seenKeys = new Set(getSeen());
    const fresh = mapped.filter(m => m.key && !seenKeys.has(m.key));
    if (!fresh.length) return;

    const last = fresh[fresh.length - 1];
    const isInfo = last.level && last.level.includes('info');
    const defaultText = isInfo ? 'No modificaste ningún dato.' : undefined;
    Swal.fire({
      icon: last.icon,
      title: last.title,
      text: opts.showText ? last.text : (last.text || defaultText),
      timer: opts.timer || 2000,
      showConfirmButton: opts.showConfirmButton ?? false,
      toast: false,
      position: 'center',
    });

    remember(fresh.map(m => m.key));
  }

  window.showDjangoMessages = showMessages;
})();
