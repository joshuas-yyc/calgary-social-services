import sqlite3
from datetime import datetime


def bind_source(
    conn: sqlite3.Connection,
    source_id: int,
    entity_type: str,
    entity_id: int,
    fields: list[str],
    editor: str = "user",
    confidence: str = "med",
) -> None:
    now = datetime.utcnow().isoformat()
    conn.executemany(
        """INSERT INTO field_provenance(entity_type, entity_id, field_name, source_id, verified_by, verified_at, confidence)
           VALUES(?, ?, ?, ?, ?, ?, ?)""",
        [(entity_type, entity_id, f, source_id, editor, now, confidence) for f in fields],
    )


def log_edit(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: int,
    action: str,
    editor: str = "user",
    reason: str = "",
    field_name: str = None,
    old_value=None,
    new_value=None,
) -> None:
    conn.execute(
        """INSERT INTO edits(entity_type, entity_id, field_name, old_value, new_value, action, editor, reason)
           VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
        (entity_type, entity_id, field_name,
         str(old_value) if old_value is not None else None,
         str(new_value) if new_value is not None else None,
         action, editor, reason),
    )


def queue_review(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: int,
    reason: str,
    priority: int = 50,
    note: str = None,
) -> None:
    existing = conn.execute(
        "SELECT id FROM review_queue WHERE entity_type=? AND entity_id=? AND status='open' AND reason=?",
        (entity_type, entity_id, reason),
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO review_queue(entity_type, entity_id, reason, priority, note) VALUES(?,?,?,?,?)",
            (entity_type, entity_id, reason, priority, note),
        )


def resolve_queue(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: int,
) -> None:
    conn.execute(
        """UPDATE review_queue SET status='resolved', resolved_at=CURRENT_TIMESTAMP
           WHERE entity_type=? AND entity_id=? AND status='open'""",
        (entity_type, entity_id),
    )


def ensure_source(conn: sqlite3.Connection, source_id: int | None, new_source: dict | None) -> int:
    if source_id:
        return source_id
    if new_source:
        cur = conn.execute(
            "INSERT INTO sources(url, title, source_type, notes) VALUES(?,?,?,?)",
            (new_source.get("url"), new_source["title"], new_source.get("source_type","website"), new_source.get("notes")),
        )
        return cur.lastrowid
    raise ValueError("Must provide source_id or new_source")
