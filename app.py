"""
Flask application entry-point. Creates the app, DB, blueprints,
and now ensures the FTS5 search index + triggers exist.
"""
from flask import Flask
import os
import config
from models import db, ensure_fts  # ← new helper
from routes import editor_bp

def create_app() -> Flask:
    """Factory – returns a fully configured Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise SQLAlchemy
    db.init_app(app)


    # Register blueprints
    app.register_blueprint(editor_bp)

    @app.errorhandler(404)
    def not_found(_):
        # Renders a friendly page instead of Werkzeug’s default
        from flask import render_template
        return render_template("404.html"), 404

    # Create tables + FTS virtual table / triggers
    with app.app_context():
        db.create_all()
        ensure_fts(db.engine)  # ← make sure FTS infra exists
        # Backfill FTS table from existing versions (one-time)
        from models import backfill_fts
        backfill_fts(db.engine)

    return app

app = create_app()

if __name__ == "__main__":  # pragma: no cover
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5003))
    app.run(host=host, port=port)