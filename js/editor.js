/**
 * Core editor logic: render YAML, serialize edits, save, diff,
 * and now export JSON.
 * ------------------------------------------------------------
 * 1. buildNode(data) ➜ DOM
 * 2. readNode(el)    ➜ JS object
 * 3. Wire toggles + save + export on DOMContentLoaded
 */

/* -------- JS ➜ DOM (render) -------- */
function buildNode(data) {
    /* Mapping */
    if (data && typeof data === 'object' && !Array.isArray(data)) {
        const map = document.createElement('div');
        map.className = 'map';

        Object.entries(data).forEach(([k, v]) => {
            const item = document.createElement('div');
            item.className = 'map-item';

            if (v && typeof v === 'object') {
                const toggleBtn = document.createElement('span');
                toggleBtn.className = 'toggle-btn';
                toggleBtn.textContent = '[-]';

                const keyInput = document.createElement('input');
                keyInput.className = 'key-input';
                keyInput.type = 'text';
                keyInput.value = k;

                const childBox = document.createElement('div');
                childBox.className = 'children';
                childBox.appendChild(buildNode(v));

                item.append(toggleBtn, keyInput, childBox);
            } else {
                const keyInput = document.createElement('input');
                keyInput.className = 'key-input';
                keyInput.type = 'text';
                keyInput.value = k;

                const colon = document.createElement('span');
                colon.className = 'colon';
                colon.textContent = ':';

                const valField = (typeof v === 'string' && v.includes('\n'))
                    ? document.createElement('textarea')
                    : document.createElement('input');
                valField.className = 'value-input';
                if (valField.tagName === 'INPUT') valField.type = 'text';
                valField.value = v ?? '';

                item.append(keyInput, colon, valField);
            }
            map.appendChild(item);
        });
        return map;
    }

    /* Sequence */
    if (Array.isArray(data)) {
        const list = document.createElement('div');
        list.className = 'list';

        const countSpan = document.createElement('span');
        countSpan.className = 'list-count';
        countSpan.textContent = `(${data.length})`;
        list.appendChild(countSpan);

        data.forEach(v => {
            const item = document.createElement('div');
            item.className = 'list-item';

            if (v && typeof v === 'object') {
                const toggleBtn = document.createElement('span');
                toggleBtn.className = 'toggle-btn';
                toggleBtn.textContent = '[-]';

                const dash = document.createElement('span');
                dash.className = 'dash';
                dash.textContent = '-';

                const childBox = document.createElement('div');
                childBox.className = 'children';
                childBox.appendChild(buildNode(v));

                item.append(toggleBtn, dash, childBox);
            } else {
                const dash = document.createElement('span');
                dash.className = 'dash';
                dash.textContent = '- ';

                const valField = (typeof v === 'string' && v.includes('\n'))
                    ? document.createElement('textarea')
                    : document.createElement('input');
                valField.className = 'value-input';
                if (valField.tagName === 'INPUT') valField.type = 'text';
                valField.value = v ?? '';

                item.append(dash, valField);
            }
            list.appendChild(item);
        });
        return list;
    }

    /* Scalar */
    const input = document.createElement('input');
    input.className = 'value-input';
    input.type = 'text';
    input.value = data ?? '';
    return input;
}

/* -------- DOM ➜ JS (serialize) -------- */
function readNode(el) {
    if (!el) return null;
    if (el.classList.contains('children'))
        return readNode(el.firstElementChild);

    /* Mapping */
    if (el.classList.contains('map')) {
        const obj = {};
        el.querySelectorAll(':scope > .map-item').forEach(item => {
            const key = item.querySelector(':scope > .key-input')?.value.trim() || '';
            const child = item.querySelector(':scope > .children');
            if (child) {
                obj[key] = readNode(child);
            } else {
                const val = item.querySelector(':scope > .value-input, textarea.value-input')?.value ?? null;
                obj[key] = val;
            }
        });
        return obj;
    }

    /* Sequence */
    if (el.classList.contains('list')) {
        return [...el.querySelectorAll(':scope > .list-item')].map(item => {
            const child = item.querySelector(':scope > .children');
            if (child) return readNode(child);
            return item.querySelector(':scope > .value-input, textarea.value-input')?.value ?? null;
        });
    }
    return null;
}

/* -------- Init: toggles, save, export -------- */
document.addEventListener('DOMContentLoaded', () => {
    const editor      = document.getElementById('editor');
    const saveBtn     = document.getElementById('save-btn');
    const exportBtn   = document.getElementById('export-json-btn');
    const copyBtn     = document.getElementById('copy-json-btn');

    /* expand/collapse */
    editor?.addEventListener('click', e => {
        if (e.target.classList.contains('toggle-btn')) toggle(e.target);
    });

    /* save */
    if (saveBtn && editor) {
        saveBtn.addEventListener('click', () => {
            const data   = readNode(editor.firstElementChild);
            const fileId = saveBtn.dataset.fileId;
            if (!fileId) return showMessage('No file context', 'error');

            saveFile(fileId, data).then(res => {
                if (!res.success)
                    return showMessage(res.error || 'Save failed', 'error');

                // Update history dropdown
                const sel = document.getElementById('history-select');
                if (sel && res.version) {
                    sel.options[0].textContent = sel.options[0].textContent.replace(' (current)', '');
                    const opt = new Option(`${res.version.timestamp} (current)`, res.version.id, true, true);
                    sel.insertBefore(opt, sel.firstChild);
                }
                showMessage('Saved.', 'success');
            }).catch(() => showMessage('Network error', 'error'));
        });
    }

    /* export JSON */
    if (exportBtn && editor) {
        exportBtn.addEventListener('click', () => {
            if (!editor.firstElementChild) return showMessage('Nothing to export', 'error');

            const obj = readNode(editor.firstElementChild);
            try {
                const json = JSON.stringify(obj, null, 2);
                document.getElementById('json-output').textContent = json;
                document.getElementById('json-section').classList.remove('hidden');
                showMessage('JSON generated.', 'success');
            } catch (e) {
                showMessage('Failed to convert', 'error');
            }
        });
    }

    /* copy JSON */
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const txt = document.getElementById('json-output').textContent;
            utils.copyToClipboard(txt);
        });
    }
});