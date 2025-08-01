let savedToast;
document.addEventListener('DOMContentLoaded', () => {
    const bar   = document.getElementById('message');
    const close = document.getElementById('msg-close');
    if (!bar || !close) return;

    close.addEventListener('click', () => {
        // hide banner
        bar.textContent = '';
        bar.className   = 'message';

        // drop `error` from URL so it stays gone after reload
        const url = new URL(window.location);
        url.searchParams.delete('error');
        window.history.replaceState({}, '', url);
    });
});
/**
 * Shared utility helpers for the YAML editor UI.
 * ----------------------------------------------
 * 1. toggle(el)               – expand/collapse a subtree.
 * 2. showMessage(txt[, type]) – status banner.
 * 3. copyToClipboard(text)    – copy arbitrary string.
 */

/**
 * Expand or collapse a YAML subtree.
 * @param {HTMLElement} el  – The clicked <span class="toggle-btn"> element.
 */
function toggle(el) {
    const box = el.parentNode.querySelector(':scope > .children');
    if (!box) return;

    const hidden = box.classList.toggle('hidden');
    el.textContent = hidden ? '[+]' : '[-]';
}

/**
 * Display a transient message banner.
 * @param {string} txt
 * @param {"success"|"error"} [type]
 */
function showMessage(txt, type) {
    const bar = document.getElementById('message');
    if (!bar) return;

    bar.textContent = txt;
    bar.className = 'message' + (type ? ' ' + type : '');

    clearTimeout(bar._timer);
    bar._timer = setTimeout(() => { bar.textContent = ''; }, 4000);
}

/**
 * Copy text to clipboard and notify user.
 * @param {string} text
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => showMessage('Copied to clipboard', 'success'))
        .catch(() => showMessage('Copy failed', 'error'));
}

const utils = { toggle, showMessage, copyToClipboard };