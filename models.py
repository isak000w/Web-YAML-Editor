
"""
Data models + helper to create an SQLite FTS5 index on YAMLVersion.content.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class YAMLFile(db.Model):
    __tablename__ = "yaml_files"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512))
    versions = db.relationship(
        "YAMLVersion",
        back_populates="file",
        cascade="all, delete-orphan",
        order_by="YAMLVersion.timestamp.desc()",
    )

    def __repr__(self):
        return f"<YAMLFile id={self.id} name={self.name}>"

class YAMLVersion(db.Model):
    __tablename__ = "yaml_versions"

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("yaml_files.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    file = db.relationship("YAMLFile", back_populates="versions")

    def __repr__(self):
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"<YAMLVersion id={self.id} file_id={self.file_id} time={ts}>"

# —————————————————————————
# Full-text search support (SQLite FTS5)
# —————————————————————————
def ensure_fts(engine):
    """
    Create the virtual FTS5 table + triggers if they don’t exist.
    rowid == YAMLVersion.id so we can JOIN efficiently.
    """
    sqls = [
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS yaml_versions_fts
        USING fts5(content, version_id UNINDEXED, file_id UNINDEXED,
        tokenize='porter');
        """,
        """
        CREATE TRIGGER IF NOT EXISTS yaml_versions_ai
        AFTER INSERT ON yaml_versions BEGIN
        INSERT INTO yaml_versions_fts(rowid, content, version_id, file_id)
        VALUES (new.id, new.content, new.id, new.file_id);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS yaml_versions_ad
        AFTER DELETE ON yaml_versions BEGIN
        DELETE FROM yaml_versions_fts WHERE rowid = old.id;
        END;
        """,
    ]
    with engine.begin() as conn:  # AUTOCOMMIT
        for stmt in sqls:
            conn.exec_driver_sql(stmt)

def backfill_fts(engine):
    """
    One-time migration: backfill FTS table from existing yaml_versions.
    """
    sql = '''
    INSERT INTO yaml_versions_fts(rowid, content, version_id, file_id)
    SELECT id, content, id, file_id FROM yaml_versions
    WHERE id NOT IN (SELECT rowid FROM yaml_versions_fts);
    '''
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)