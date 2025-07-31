# Local YAML Editor & Version Tracker

A lightweight Flask web app for viewing, editing, validating, diffing, and version-controlling YAML configuration files — all in the browser and fully self-hosted.

## Features
- Upload `.yaml` / `.yml` files (drag-and-drop or standard file picker)  
- Tree-style editor with **collapse / expand**, sticky key column, and indent guides  
- **Schema-aware save** – optional JSON-Schema validation before commit  
- Automatic **version history** (every save becomes a new snapshot)  
- One-click **unified diff** viewer between any two versions  
- **Full-text search** (SQLite FTS5) across the entire revision archive  
- Dark / light theme toggle, autosave indicator, friendly 404 & validation banners  
- Export current document as prettified **JSON** with copy-to-clipboard  
- Built-in YAML → JSON conversion and rollback to any prior version  

## Setup
```bash
git clone https://github.com/your-name/local-yaml-editor.git
cd local-yaml-editor

# Python ≥3.10 recommended
python -m venv .venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows

pip install -r requirements.txt
python app.py                    # default: http://127.0.0.1:5003
```

## Screenshots

Main UI (Light Mode)
<img width="1440" height="708" alt="1" src="https://github.com/user-attachments/assets/25bc383f-288b-48fa-bd11-b2fa75b219b8" />


Main UI (Dark Mode)
<img width="1440" height="708" alt="2" src="https://github.com/user-attachments/assets/03237c1e-bfd3-4a3e-92ce-bbc09996bb0f" />


Editor Page
<img width="1440" height="708" alt="3" src="https://github.com/user-attachments/assets/3230badf-549b-4e31-8b56-f0d8e4cd8050" />


Loading Diff
<img width="1440" height="708" alt="4" src="https://github.com/user-attachments/assets/d627bfc7-cc65-4457-a813-bdebd0a4ba3a" />


Diff View
<img width="1440" height="708" alt="5" src="https://github.com/user-attachments/assets/928232bb-cb53-4fec-8b2e-10ecec75c21a" />


Search Feature
<img width="1440" height="708" alt="6" src="https://github.com/user-attachments/assets/13c0e57b-3aef-4b46-ae4e-4981916efbc0" />
