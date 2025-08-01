import re
import sqlite3
from sqlalchemy.exc import OperationalError
# ── FTS-query safety regex ───────────────────────────────────────────
SAFE_FTS_RE = re.compile(r"^[A-Za-z0-9 _\.\-:]{1,100}$")   # letters, digits, space, _ . - :
def _fts_query_is_safe(q: str) -> bool:
    """Return True only when q contains allowed characters for FTS5 MATCH."""
    return bool(SAFE_FTS_RE.fullmatch(q))

"""
Flask routes / REST endpoints – now includes /api/search for full-text lookup.
"""
import os, difflib, yaml
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from jsonschema import validate
from sqlalchemy import text

import config
from models import db, YAMLFile, YAMLVersion

editor_bp = Blueprint("editor", __name__, template_folder="templates")

# ––––– helpers –––––
def allowed_file(fn):
    return os.path.splitext(fn)[1].lower() in config.ALLOWED_EXTENSIONS

def yaml_to_lines(text_):
    """Normalise YAML into pretty formatted line list for diff."""
    try:
        obj = yaml.safe_load(text_)
        pretty = yaml.safe_dump(obj, sort_keys=False)
    except Exception:
        pretty = text_
    return pretty.splitlines(False)

# ––––– pages –––––
@editor_bp.route("/")
def index():
    files = YAMLFile.query.all()
    error = request.args.get("error")
    return render_template("index.html", files=files, error=error)

@editor_bp.route("/files/<int:file_id>")
def edit_file(file_id):
    file = YAMLFile.query.get_or_404(file_id)
    versions = (
        YAMLVersion.query.filter_by(file_id=file_id)
        .order_by(YAMLVersion.timestamp.desc())
        .all()
    )
    for v in versions:
        v.display_time = v.timestamp.strftime(config.TIME_FORMAT)

    latest = versions[0] if versions else None
    try:
        data = yaml.safe_load(latest.content) if latest else None
    except Exception:
        data = None
    error = request.args.get("error")
    return render_template("index.html", file=file, data=data, versions=versions, error=error)

# ––––– upload / delete –––––
@editor_bp.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("yaml_file")
    if not (f and f.filename):
        return redirect(url_for("editor.index", error="No file."))
    if not allowed_file(f.filename):
        return redirect(url_for("editor.index", error="Bad type."))

    raw = f.read()
    try:
        txt = raw.decode("utf-8")
        yaml.safe_load(txt)
    except Exception as e:
        return redirect(url_for("editor.index", error=f"YAML error: {e}"))

    yfile = YAMLFile(name=f.filename)
    db.session.add(yfile)
    db.session.commit()
    db.session.add(YAMLVersion(file_id=yfile.id, content=txt))
    db.session.commit()
    return redirect(url_for("editor.edit_file", file_id=yfile.id))



# ––––– REST: versions –––––




    data = fix(data)

    if config.SCHEMA:
        try:
            validate(data, config.SCHEMA)
        except Exception as e:
            return jsonify(success=False, error=str(e)), 400

    dump = yaml.safe_dump(data, sort_keys=False)
    ver = YAMLVersion(file_id=file_id, content=dump)
    db.session.add(ver)
    db.session.commit()
    return jsonify(
        success=True,
        version={"id": ver.id, "timestamp": ver.timestamp.strftime(config.TIME_FORMAT)},
    )

# ––––– REST: diff –––––


# ––––– REST: full-text search –––––

@editor_bp.route("/api/search")
def search():
    """
    GET /api/search?q=<text>
    Rejects malformed input, catches sqlite errors, always returns JSON 200/400.
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify(success=False, error="Empty query"), 400
    if not _fts_query_is_safe(q):
        return jsonify(success=False, error="Invalid search syntax"), 400

    sql = text(
        """
        SELECT v.id            AS version_id,
               v.file_id       AS file_id,
               f.name          AS file_name,
               v.timestamp     AS ts,
               snippet(yaml_versions_fts, 0, '<mark>', '</mark>', ' … ', 10) AS snippet
        FROM yaml_versions_fts
        JOIN yaml_versions v ON v.id = yaml_versions_fts.version_id
        JOIN yaml_files    f ON f.id = v.file_id
        WHERE yaml_versions_fts MATCH :q
        ORDER BY v.timestamp DESC
        LIMIT 20;
        """
    )
    try:
        rows = db.session.execute(sql, {"q": q}).mappings().all()
    except OperationalError:
        return jsonify(success=False, error="Invalid search syntax"), 400

    results = [
        {
            "version_id": r["version_id"],
            "file_id":    r["file_id"],
            "file_name":  r["file_name"],
            "timestamp":  r["ts"] if isinstance(r["ts"], str) else r["ts"].strftime(config.TIME_FORMAT),
            "snippet":    r["snippet"],
        }
        for r in rows
    ]
    return jsonify(success=True, results=results)

@editor_bp.route('/files/<int:file_id>/delete', methods=['POST'])
def delete_file(file_id):
    f = YAMLFile.query.get_or_404(file_id); db.session.delete(f); db.session.commit()
    return redirect(url_for('editor.index'))

# ---------- REST ----------
@editor_bp.route('/api/versions/<int:vid>')
def get_version(vid):
    v = YAMLVersion.query.get_or_404(vid)
    try: return jsonify(success=True, content=yaml.safe_load(v.content))
    except Exception: return jsonify(success=False, error='Corrupt YAML'), 500

@editor_bp.route('/api/files/<int:file_id>', methods=['POST'])
def save_file(file_id):
    file = YAMLFile.query.get_or_404(file_id)
    data = request.get_json()
    if data is None: return jsonify(success=False, error='No data'), 400

    # primitive conversion
    def fix(o):
        if isinstance(o, dict): return {k:fix(v) for k,v in o.items()}
        if isinstance(o, list): return [fix(v) for v in o]
        if isinstance(o, str):
            try:
                prim = yaml.safe_load(o)
                return prim if isinstance(prim,(bool,int,float,type(None))) else o
            except Exception: return o
        return o
    data = fix(data)

    if config.SCHEMA:
        try: validate(data, config.SCHEMA)
        except Exception as e: return jsonify(success=False, error=str(e)), 400

    dump = yaml.safe_dump(data, sort_keys=False)
    ver = YAMLVersion(file_id=file_id, content=dump); db.session.add(ver); db.session.commit()
    return jsonify(success=True,
                   version={'id':ver.id,'timestamp':ver.timestamp.strftime(config.TIME_FORMAT)})

@editor_bp.route('/api/diff')
def diff_versions():
    """
    GET /api/diff?left=<vid>&right=<vid>
    Returns unified diff lines between two version IDs (same file).
    """
    v_left  = YAMLVersion.query.get(request.args.get('left', type=int))
    v_right = YAMLVersion.query.get(request.args.get('right', type=int))
    if not (v_left and v_right):
        return jsonify(success=False, error='Version(s) not found'), 404
    if v_left.file_id != v_right.file_id:
        return jsonify(success=False, error='Versions belong to different files'), 400

    lines_left  = yaml_to_lines(v_left.content)
    lines_right = yaml_to_lines(v_right.content)
    diff = list(difflib.unified_diff(lines_left, lines_right,
                                     fromfile=v_left.timestamp.isoformat(),
                                     tofile=v_right.timestamp.isoformat(),
                                     lineterm=''))
    return jsonify(success=True, diff=diff)