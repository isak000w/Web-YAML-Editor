/**
• Full-text search UI – queries /api/search and shows results.
*/
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  if (!input || !results) return;
  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (!q) { results.classList.add('hidden'); results.innerHTML = ''; return; }
    timer = setTimeout(() => runSearch(q), 300);
  });
  function runSearch(q) {
    fetch(`/api/search?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(j => {
            if (!j.success) {                // server-side validation failed
                utils.showMessage(j.error || 'Search error', 'error');
                results.classList.add('hidden');   // hide previous list
                return;
            }
            display(j.results);
        })
        .catch(() => utils.showMessage('Search failed', 'error'));
  }
  function display(arr) {
    results.innerHTML = '';
    if (!arr.length) {
      results.textContent = 'No matches';
      results.classList.remove('hidden');
      return;
    }
    arr.forEach(r => {
      const div = document.createElement('div');
      div.className = 'search-result-item';
      div.innerHTML = `<strong>${r.file_name}</strong> @ ${r.timestamp}<br>${r.snippet}`;
      div.addEventListener('click', () => {
        window.location.href = `/files/${r.file_id}`;
      });
      results.appendChild(div);
    });
    results.classList.remove('hidden');
  }
});
