from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.database import db
from app.services.provenance import log_edit, queue_review, ensure_source

router = APIRouter(prefix="/orgs", tags=["orgs"])
templates = Jinja2Templates(directory="app/templates")


def _get_form_deps(conn):
    orgs = conn.execute("SELECT id, name FROM organizations WHERE status='active' ORDER BY name").fetchall()
    return {"all_orgs": orgs}


@router.get("/", response_class=HTMLResponse)
def list_orgs(request: Request):
    with db() as conn:
        orgs = conn.execute("""
            SELECT o.*, COUNT(l.id) as location_count
            FROM organizations o
            LEFT JOIN locations l ON l.organization_id=o.id
            GROUP BY o.id ORDER BY o.name
        """).fetchall()
    return templates.TemplateResponse(request, "orgs/list.html", {"orgs": orgs})


@router.get("/new", response_class=HTMLResponse)
def new_org_form(request: Request):
    with db() as conn:
        deps = _get_form_deps(conn)
        sources = conn.execute("SELECT id, title, source_type FROM sources ORDER BY retrieved_at DESC LIMIT 50").fetchall()
    return templates.TemplateResponse(request, "orgs/edit.html", {
        "org": None, "sources": sources, **deps
    })


@router.post("/", response_class=HTMLResponse)
async def create_org(
    request: Request,
    name: str = Form(...),
    legal_name: str = Form(""),
    parent_org_id: str = Form(""),
    indigenous_led: str = Form("0"),
    description: str = Form(""),
    website: str = Form(""),
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
            """INSERT INTO organizations(name, legal_name, parent_org_id, indigenous_led, description, website, status)
               VALUES(?,?,?,?,?,?,?)""",
            (name, legal_name or None, int(parent_org_id) if parent_org_id else None,
             1 if indigenous_led == "1" else 0,
             description or None, website or None, status),
        )
        org_id = cur.lastrowid
        log_edit(conn, "org", org_id, "create", editor, reason)
        queue_review(conn, "org", org_id, "new", priority=40)
    return RedirectResponse(f"/orgs/{org_id}", status_code=303)


@router.get("/{org_id}", response_class=HTMLResponse)
def org_detail(request: Request, org_id: int):
    with db() as conn:
        org = conn.execute("SELECT * FROM organizations WHERE id=?", (org_id,)).fetchone()
        if not org:
            raise HTTPException(404)
        locations = conn.execute(
            "SELECT * FROM locations WHERE organization_id=? ORDER BY label", (org_id,)
        ).fetchall()
        contacts = conn.execute(
            "SELECT * FROM contacts WHERE owner_type='org' AND owner_id=?", (org_id,)
        ).fetchall()
        edits = conn.execute(
            "SELECT * FROM edits WHERE entity_type='org' AND entity_id=? ORDER BY timestamp DESC LIMIT 20",
            (org_id,)
        ).fetchall()
        queue = conn.execute(
            "SELECT * FROM review_queue WHERE entity_type='org' AND entity_id=? AND status='open'",
            (org_id,)
        ).fetchall()
        parent = None
        if org["parent_org_id"]:
            parent = conn.execute("SELECT id, name FROM organizations WHERE id=?", (org["parent_org_id"],)).fetchone()
    return templates.TemplateResponse(request, "orgs/detail.html", {
        "org": org, "locations": locations,
        "contacts": contacts, "edits": edits, "queue": queue, "parent": parent,
    })


@router.get("/{org_id}/edit", response_class=HTMLResponse)
def edit_org_form(request: Request, org_id: int):
    with db() as conn:
        org = conn.execute("SELECT * FROM organizations WHERE id=?", (org_id,)).fetchone()
        if not org:
            raise HTTPException(404)
        deps = _get_form_deps(conn)
        sources = conn.execute("SELECT id, title, source_type FROM sources ORDER BY retrieved_at DESC LIMIT 50").fetchall()
    return templates.TemplateResponse(request, "orgs/edit.html", {
        "org": org, "sources": sources, **deps
    })


@router.post("/{org_id}/edit", response_class=HTMLResponse)
async def update_org(
    request: Request,
    org_id: int,
    name: str = Form(...),
    legal_name: str = Form(""),
    parent_org_id: str = Form(""),
    indigenous_led: str = Form("0"),
    description: str = Form(""),
    website: str = Form(""),
    status: str = Form("active"),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("website"),
    reason: str = Form(...),
    editor: str = Form("user"),
):
    with db() as conn:
        old = conn.execute("SELECT * FROM organizations WHERE id=?", (org_id,)).fetchone()
        if not old:
            raise HTTPException(404)
        src_id = ensure_source(
            conn,
            int(source_id) if source_id else None,
            {"title": source_title, "url": source_url or None, "source_type": source_type} if source_title else None,
        )
        conn.execute(
            """UPDATE organizations SET name=?, legal_name=?, parent_org_id=?, indigenous_led=?,
               description=?, website=?, status=? WHERE id=?""",
            (name, legal_name or None, int(parent_org_id) if parent_org_id else None,
             1 if indigenous_led == "1" else 0,
             description or None, website or None, status, org_id),
        )
        log_edit(conn, "org", org_id, "update", editor, reason)
    return RedirectResponse(f"/orgs/{org_id}", status_code=303)


@router.post("/{org_id}/flag")
def flag_org(org_id: int, note: str = Form("")):
    with db() as conn:
        queue_review(conn, "org", org_id, "flagged", priority=70, note=note or None)
    return RedirectResponse(f"/orgs/{org_id}", status_code=303)
