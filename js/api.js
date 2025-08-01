/**
• API helper functions for AJAX requests to the Flask server.
• (Search uses fetch directly in search.js.)
*/
function getVersion(versionId) {
  return fetch(`/api/versions/${versionId}`).then(r => r.json());
}

function saveFile(fileId, data) {
  return fetch(`/api/files/${fileId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json());
}

const api = { getVersion, saveFile } // optional export for future use