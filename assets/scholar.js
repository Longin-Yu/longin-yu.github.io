// The build-time snapshot keeps all counts available without JavaScript.
(() => {
  const script = document.currentScript;
  const localPreview = ['localhost', '127.0.0.1', '[::1]', '::1'].includes(location.hostname);
  const url = localPreview ? script.dataset.snapshotUrl : script.dataset.remoteUrl;
  const snapshotTime = Date.parse(script.dataset.updated) || 0;
  const count = value => Number.isInteger(value) && value >= 0;

  async function refresh() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(url, {signal: controller.signal});
      if (!response.ok) return;
      const data = await response.json();
      const updated = Date.parse(data.updated);
      if (data.scholar_id !== script.dataset.scholarId || !count(data.citedby) ||
          !Number.isFinite(updated) || updated < snapshotTime) return;
      const total = document.getElementById('total_cit');
      if (total) total.textContent = data.citedby.toLocaleString('en-US');
      const date = document.getElementById('scholar-updated');
      if (date) {
        date.dateTime = data.updated;
        date.textContent = new Date(updated).toISOString().slice(0, 10);
      }
    } catch {
      // Keep the last successful snapshot if Scholar/CDN is unavailable.
    } finally {
      clearTimeout(timeout);
    }
  }
  refresh();
})();
