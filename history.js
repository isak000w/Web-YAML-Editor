/**
 * History dropdown interactions: loading selected version content.
 */

// Function to load a selected version and update the editor UI.
function loadVersion(versionId) {
    getVersion(versionId).then(res => {
        if (!res.success) {
            // Display error if retrieval failed
            showMessage(res.error || "Failed to load version.", 'error');
        } else {
            if (!res.content) {
                showMessage("Version content is empty or invalid.", 'error');
                return;
            }
            const editorDiv = document.getElementById('editor');
            if (!editorDiv) return;
            // Clear current editor content
            editorDiv.innerHTML = '';
            // Build and insert new content structure
            const contentElem = buildNode(res.content);
            editorDiv.appendChild(contentElem);
            // After loading an old version, user should click Save to make it current
            showMessage("Loaded version (not saved).", 'success');
        }
    }).catch(err => {
        showMessage("Error retrieving version.", 'error');
    });
}

// Set up event listener for the history dropdown
document.addEventListener('DOMContentLoaded', () => {
    const historySelect = document.getElementById('history-select');
    if (historySelect) {
        historySelect.addEventListener('change', (e) => {
            const verId = e.target.value;
            if (verId) {
                loadVersion(verId);
            }
        });
    }
});