/**
 * Handles fetching and displaying unified diffs between two versions.
 */
document.addEventListener('DOMContentLoaded', () => {
    const diffBtn   = document.getElementById('diff-btn');
    const leftSel   = document.getElementById('left-ver');
    const rightSel  = document.getElementById('right-ver');
    const diffOut   = document.getElementById('diff-output');

    if (!diffBtn) return;   // not on editor page

    diffBtn.addEventListener('click', () => {
        const l = leftSel.value, r = rightSel.value;
        if (l === r) { showMessage('Select two different versions.', 'error'); return; }

        fetch(`/api/diff?left=${l}&right=${r}`)
            .then(res => res.json())
            .then(j => {
                if (!j.success) return showMessage(j.error, 'error');
                diffOut.textContent = j.diff.join('\n') || 'No differences.';
                diffOut.classList.remove('hidden');
                showMessage('Diff loaded.', 'success');
            })
            .catch(() => showMessage('Diff request failed.', 'error'));
    });
});