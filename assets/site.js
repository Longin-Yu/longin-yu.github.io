// Reading publications and opening BibTeX use native HTML; JS only adds copying.
if (navigator.clipboard && window.isSecureContext) {
  document.querySelectorAll('.citation-body').forEach((body) => {
    const button = body.querySelector('.copy-citation');
    const status = body.querySelector('.copy-status');
    button.hidden = false;
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(body.querySelector('code').textContent);
        status.textContent = 'Copied.';
      } catch {
        status.textContent = 'Please select the citation below to copy it.';
      }
    });
  });
}
