import json
import csv
import io
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import db
from app.services.provenance import log_edit, queue_review, ensure_source

router = APIRouter(prefix="/staging", tags=["staging"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def staging_list(request: Request):
    with db() as conn:
        rows = conn.execute("""
            SELECT st.*, s.title as source_title
            FROM staging st LEFT JOIN sources s ON s.id=st.source_id
            WHERE st.status='pending'
            ORDER BY st.created_at DESC
        """).fetchall()
        sources = conn.execute("SELECT id, title, source_type FROM sources ORDER BY retrieved_at DESC LIMIT 50").fetchall()

    # Parse display label from raw JSON so the list is readable
    items = []
    for row in rows:
        try:
            d = json.loads(row["raw_json"])
            label = (d.get("org_name") or d.get("name") or d.get("service_name")
                     or d.get("organization") or None)
            shelters = d.get("shelters", [])
        except Exception:
            label = None
            shelters = []
        items.append({"row": row, "label": label, "shelter_count": len(shelters)})

    return templates.TemplateResponse(request, "staging/list.html", {
        "items": items, "sources": sources,
    })


@router.post("/upload")
async def upload_staging(
    file: UploadFile = File(...),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("211"),
):
    content = await file.read()
    filename = file.filename or ""

    records = []
    if filename.endswith(".json"):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON")
    elif filename.endswith(".csv"):
        try:
            text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            records = [dict(row) for row in reader]
        except Exception:
            raise HTTPException(400, "Invalid CSV")
    else:
        raise HTTPException(400, "Only .json and .csv files supported")

    with db() as conn:
        src_id = ensure_source(
            conn,
            int(source_id) if source_id else None,
            {"title": source_title or filename, "url": source_url or None, "source_type": source_type} if (source_title or filename) else None,
        )
        for record in records:
            conn.execute(
                "INSERT INTO staging(raw_json, source_id) VALUES(?,?)",
                (json.dumps(record), src_id),
            )
    return RedirectResponse("/staging", status_code=303)


def _similar_orgs(conn, name: str) -> list:
    """Return existing orgs sharing at least one significant word with `name`."""
    if not name:
        return []
    stop = {"the", "of", "and", "for", "in", "at", "a", "an", "calgary", "centre", "center"}
    words = [w.lower() for w in name.split() if len(w) > 2 and w.lower() not in stop]
    if not words:
        return []
    # Use LIKE for each significant word — SQLite, no FTS on org names
    matches = {}
    for word in words:
        rows = conn.execute(
            "SELECT id, name FROM organizations WHERE LOWER(name) LIKE ? AND status='active'",
            (f"%{word}%",),
        ).fetchall()
        for r in rows:
            if r["name"].lower() != name.lower():
                matches[r["id"]] = r["name"]
    return [{"id": k, "name": v} for k, v in matches.items()]


@router.get("/{item_id}", response_class=HTMLResponse)
def staging_review(request: Request, item_id: int):
    with db() as conn:
        item = conn.execute("SELECT * FROM staging WHERE id=?", (item_id,)).fetchone()
        if not item:
            raise HTTPException(404)
        raw = json.loads(item["raw_json"])
        orgs = conn.execute("SELECT id, name FROM organizations WHERE status='active' ORDER BY name").fetchall()
        categories = conn.execute("SELECT * FROM categories ORDER BY sort_order, name").fetchall()
        populations = conn.execute("SELECT * FROM populations ORDER BY name").fetchall()
        locations = conn.execute("""
            SELECT l.id, l.label, l.address, o.name as org_name
            FROM locations l JOIN organizations o ON o.id=l.organization_id
            WHERE l.status='active' ORDER BY o.name, l.label
        """).fetchall()
        similar = _similar_orgs(conn, raw.get("org_name") or raw.get("organization", ""))
    return templates.TemplateResponse(request, "staging/review.html", {
        "item": item, "raw": raw,
        "orgs": orgs, "categories": categories, "populations": populations,
        "locations": locations, "similar_orgs": similar,
    })


@router.post("/{item_id}/reject")
def reject_staging(item_id: int, note: str = Form("")):
    with db() as conn:
        conn.execute(
            "UPDATE staging SET status='rejected', notes=? WHERE id=?",
            (note or None, item_id),
        )
    return RedirectResponse("/staging", status_code=303)


@router.post("/{item_id}/accept")
async def accept_staging(
    request: Request,
    item_id: int,
    # Basic service creation fields
    org_action: str = Form("existing"),  # existing | new
    organization_id: str = Form(""),
    org_name: str = Form(""),
    location_id: str = Form(""),
    location_action: str = Form("existing"),  # existing | new
    loc_address: str = Form(""),
    loc_quadrant: str = Form(""),
    loc_community: str = Form(""),
    service_name: str = Form(...),
    description: str = Form(""),
    primary_category_id: str = Form(""),
    cost_model: str = Form("unknown"),
    access_mode: str = Form("walk_in"),
    reason: str = Form("Accepted from staging"),
    editor: str = Form("user"),
):
    with db() as conn:
        item = conn.execute("SELECT * FROM staging WHERE id=?", (item_id,)).fetchone()
        if not item:
            raise HTTPException(404)

        src_id = item["source_id"]

        # Resolve or create org
        if org_action == "new" and org_name:
            cur = conn.execute(
                "INSERT INTO organizations(name, status) VALUES(?,?)", (org_name, "active")
            )
            org_id = cur.lastrowid
            log_edit(conn, "org", org_id, "create", editor, reason + " (from staging)")
        else:
            org_id = int(organization_id) if organization_id else None

        # Resolve or create location
        if location_action == "new" and org_id:
            cur = conn.execute(
                "INSERT INTO locations(organization_id, address, quadrant, community, status) VALUES(?,?,?,?,?)",
                (org_id, loc_address or None, loc_quadrant or None, loc_community or None, "active"),
            )
            loc_id = cur.lastrowid
            log_edit(conn, "location", loc_id, "create", editor, reason + " (from staging)")
        else:
            loc_id = int(location_id) if location_id else None

        if not loc_id:
            raise HTTPException(400, "Location required")

        cur = conn.execute(
            """INSERT INTO services(location_id, name, description, primary_category_id, cost_model, access_mode, status)
               VALUES(?,?,?,?,?,?,?)""",
            (loc_id, service_name, description or None,
             int(primary_category_id) if primary_category_id else None,
             cost_model, access_mode, "active"),
        )
        svc_id = cur.lastrowid
        log_edit(conn, "service", svc_id, "create", editor, reason)
        queue_review(conn, "service", svc_id, "new", priority=60)

        conn.execute("UPDATE staging SET status='accepted' WHERE id=?", (item_id,))

    return RedirectResponse(f"/services/{svc_id}", status_code=303)
