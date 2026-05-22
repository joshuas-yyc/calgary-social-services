from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.database import db
from app.services.provenance import log_edit, queue_review, ensure_source

router = APIRouter(prefix="/locations", tags=["locations"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/new", response_class=HTMLResponse)
def new_location_form(request: Request, org_id: str = ""):
    with db() as conn:
        orgs = conn.execute("SELECT id, name FROM organizations WHERE status='active' ORDER BY name").fetchall()
        sources = conn.execute("SELECT id, title, source_type FROM sources ORDER BY retrieved_at DESC LIMIT 50").fetchall()
        selected_org = None
        if org_id:
            selected_org = conn.execute("SELECT id, name FROM organizations WHERE id=?", (org_id,)).fetchone()
    return templates.TemplateResponse(request, "locations/edit.html", {
        "location": None, "orgs": orgs, "sources": sources,
        "selected_org": selected_org,
    })


@router.post("/", response_class=HTMLResponse)
async def create_location(
    request: Request,
    organization_id: int = Form(...),
    label: str = Form(""),
    address: str = Form(""),
    quadrant: str = Form(""),
    community: str = Form(""),
    latitude: str = Form(""),
    longitude: str = Form(""),
    wheelchair_accessible: str = Form("0"),
    transit_note: str = Form(""),
    status: str = Form("active"),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("website"),
    reason: str = Form(...),
    editor: str = Form("user"),
):
    with db() as conn:
        src_id = ensure_source(
            conn,
            int(source_id) if source_id else None,
            {"title": source_title, "url": source_url or None, "source_type": source_type} if source_title else None,
        )
        cur = conn.execute(
            """INSERT INTO locations(organization_id, label, address, quadrant, community,
               latitude, longitude, wheelchair_accessible, transit_note, status)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (organization_id, label or None, address or None,
             quadrant or None, community or None,
             float(latitude) if latitude else None,
             float(longitude) if longitude else None,
             1 if wheelchair_accessible == "1" else 0,
             transit_note or None, status),
        )
        loc_id = cur.lastrowid
        log_edit(conn, "location", loc_id, "create", editor, reason)
        queue_review(conn, "location", loc_id, "new", priority=40)
    return RedirectResponse(f"/orgs/{organization_id}", status_code=303)


@router.get("/{loc_id}", response_class=HTMLResponse)
def location_detail(request: Request, loc_id: int):
    with db() as conn:
        loc = conn.execute("SELECT * FROM locations WHERE id=?", (loc_id,)).fetchone()
        if not loc:
            raise HTTPException(404)
        org = conn.execute("SELECT id, name FROM organizations WHERE id=?", (loc["organization_id"],)).fetchone()
        services = conn.execute("""
            SELECT s.*, c.name as category_name
            FROM services s LEFT JOIN categories c ON c.id=s.primary_category_id
            WHERE s.location_id=? ORDER BY s.name
        """, (loc_id,)).fetchall()
        contacts = conn.execute(
            "SELECT * FROM contacts WHERE owner_type='location' AND owner_id=?", (loc_id,)
        ).fetchall()
        edits = conn.execute(
            "SELECT * FROM edits WHERE entity_type='location' AND entity_id=? ORDER BY timestamp DESC LIMIT 20",
            (loc_id,)
        ).fetchall()
    return templates.TemplateResponse(request, "locations/detail.html", {
        "location": loc, "org": org,
        "services": services, "contacts": contacts, "edits": edits,
    })


@router.get("/{loc_id}/edit", response_class=HTMLResponse)
def edit_location_form(request: Request, loc_id: int):
    with db() as conn:
        loc = conn.execute("SELECT * FROM locations WHERE id=?", (loc_id,)).fetchone()
        if not loc:
            raise HTTPException(404)
        orgs = conn.execute("SELECT id, name FROM organizations WHERE status='active' ORDER BY name").fetchall()
        sources = conn.execute("SELECT id, title, source_type FROM sources ORDER BY retrieved_at DESC LIMIT 50").fetchall()
    return templates.TemplateResponse(request, "locations/edit.html", {
        "location": loc, "orgs": orgs, "sources": sources,
    })


@router.post("/{loc_id}/edit", response_class=HTMLResponse)
async def update_location(
    request: Request,
    loc_id: int,
    organization_id: int = Form(...),
    label: str = Form(""),
    address: str = Form(""),
    quadrant: str = Form(""),
    community: str = Form(""),
    latitude: str = Form(""),
    longitude: str = Form(""),
    wheelchair_accessible: str = Form("0"),
    transit_note: str = Form(""),
    status: str = Form("active"),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("website"),
    reason: str = Form(...),
    editor: str = Form("user"),
):
    with db() as conn:
        old = conn.execute("SELECT * FROM locations WHERE id=?", (loc_id,)).fetchone()
        if not old:
            raise HTTPException(404)
        src_id = ensure_source(
            conn,
            int(source_id) if source_id else None,
            {"title": source_title, "url": source_url or None, "source_type": source_type} if source_title else None,
        )
        conn.execute(
            """UPDATE locations SET organization_id=?, label=?, address=?, quadrant=?,
               community=?, latitude=?, longitude=?, wheelchair_accessible=?,
               transit_note=?, status=? WHERE id=?""",
            (organization_id, label or None, address or None,
             quadrant or None, community or None,
             float(latitude) if latitude else None,
             float(longitude) if longitude else None,
             1 if wheelchair_accessible == "1" else 0,
             transit_note or None, status, loc_id),
        )
        log_edit(conn, "location", loc_id, "update", editor, reason)
    return RedirectResponse(f"/locations/{loc_id}", status_code=303)
