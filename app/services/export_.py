import json
import csv
import io
import sqlite3


def _base_query(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("""
        SELECT
            s.id, s.name as service_name, s.description, s.cost_model, s.access_mode,
            s.referral_required, s.age_min, s.age_max, s.gender_restriction,
            s.capacity, s.is_24_7, s.status, s.verified_at,
            l.address, l.quadrant, l.community, l.latitude, l.longitude,
            l.wheelchair_accessible, l.transit_note,
            o.name as org_name, o.website as org_website, o.indigenous_led,
            c.name as primary_category, c.slug as category_slug
        FROM services s
        JOIN locations l ON l.id = s.location_id
        JOIN organizations o ON o.id = l.organization_id
        LEFT JOIN categories c ON c.id = s.primary_category_id
        WHERE s.status = 'active' AND s.verified_at IS NOT NULL AND o.status = 'active'
    """).fetchall()


def export_json(conn: sqlite3.Connection) -> str:
    rows = _base_query(conn)
    records = []
    for r in rows:
        d = dict(r)
        pops = conn.execute("""
            SELECT p.name FROM populations p
            JOIN service_populations sp ON sp.population_id = p.id
            WHERE sp.service_id = ?
        """, (r["id"],)).fetchall()
        d["populations"] = [p["name"] for p in pops]
        contacts = conn.execute("""
            SELECT kind, value FROM contacts WHERE owner_type='service' AND owner_id=?
        """, (r["id"],)).fetchall()
        d["contacts"] = [dict(c) for c in contacts]
        records.append(d)
    return json.dumps(records, indent=2, default=str)


def export_geojson(conn: sqlite3.Connection) -> str:
    rows = _base_query(conn)
    features = []
    for r in rows:
        if r["latitude"] is None or r["longitude"] is None:
            continue
        pops = conn.execute("""
            SELECT p.name FROM populations p
            JOIN service_populations sp ON sp.population_id = p.id
            WHERE sp.service_id = ?
        """, (r["id"],)).fetchall()
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
            "properties": {
                "id": r["id"],
                "service_name": r["service_name"],
                "org_name": r["org_name"],
                "category": r["primary_category"],
                "quadrant": r["quadrant"],
                "community": r["community"],
                "cost_model": r["cost_model"],
                "access_mode": r["access_mode"],
                "is_24_7": bool(r["is_24_7"]),
                "populations": [p["name"] for p in pops],
                "verified_at": str(r["verified_at"]),
            }
        })
    return json.dumps({"type": "FeatureCollection", "features": features}, indent=2)


def _primary_contact(conn, service_id: int, kind: str) -> str:
    row = conn.execute(
        "SELECT value FROM contacts WHERE owner_type='service' AND owner_id=? AND kind=? ORDER BY is_primary DESC LIMIT 1",
        (service_id, kind),
    ).fetchone()
    if row:
        return row["value"]
    # Fall back to org-level contact
    row = conn.execute("""
        SELECT c.value FROM contacts c
        JOIN services s ON s.id=?
        JOIN locations l ON l.id=s.location_id
        WHERE c.owner_type='org' AND c.owner_id=l.organization_id AND c.kind=?
        ORDER BY c.is_primary DESC LIMIT 1
    """, (service_id, kind)).fetchone()
    return row["value"] if row else ""


def export_csv(conn: sqlite3.Connection) -> str:
    rows = _base_query(conn)
    if not rows:
        return ""
    buf = io.StringIO()
    extra_cols = ["phone", "email", "website", "facebook", "populations"]
    cols = list(dict(rows[0]).keys()) + extra_cols
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    for r in rows:
        d = dict(r)
        pops = conn.execute("""
            SELECT p.name FROM populations p
            JOIN service_populations sp ON sp.population_id = p.id
            WHERE sp.service_id = ?
        """, (r["id"],)).fetchall()
        d["populations"] = "; ".join(p["name"] for p in pops)
        d["phone"] = _primary_contact(conn, r["id"], "phone") or _primary_contact(conn, r["id"], "intake_line")
        d["email"] = _primary_contact(conn, r["id"], "email")
        d["website"] = _primary_contact(conn, r["id"], "web")
        d["facebook"] = _primary_contact(conn, r["id"], "facebook")
        writer.writerow(d)
    return buf.getvalue()
