import sqlite3
from datetime import datetime, timedelta
from app.services.provenance import queue_review

# Days since verified_at before flagging as stale
STALENESS_THRESHOLDS = {
    "crisis-services": 30,
    "housing": 60,
    "harm-reduction": 30,
    "detox": 45,
    "default": 180,
}


def get_threshold(category_slug: str | None) -> int:
    if not category_slug:
        return STALENESS_THRESHOLDS["default"]
    for key, days in STALENESS_THRESHOLDS.items():
        if key in (category_slug or ""):
            return days
    return STALENESS_THRESHOLDS["default"]


def run_staleness_audit(conn: sqlite3.Connection) -> dict:
    now = datetime.utcnow()
    flagged = 0
    skipped = 0

    rows = conn.execute("""
        SELECT s.id, s.verified_at, c.slug as cat_slug
        FROM services s
        LEFT JOIN categories c ON c.id = s.primary_category_id
        WHERE s.status != 'closed'
    """).fetchall()

    for row in rows:
        if not row["verified_at"]:
            skipped += 1
            continue
        threshold = get_threshold(row["cat_slug"])
        verified = datetime.fromisoformat(row["verified_at"])
        if (now - verified).days > threshold:
            queue_review(conn, "service", row["id"], "stale",
                         priority=80 if threshold <= 30 else 50)
            flagged += 1

    conn.commit()
    return {"flagged": flagged, "skipped_unverified": skipped, "total": len(rows)}
