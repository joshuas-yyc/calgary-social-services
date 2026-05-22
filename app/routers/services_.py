from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.database import db
from app.services.provenance import log_edit, queue_review, resolve_queue, ensure_source

router = APIRouter(prefix="/services", tags=["services"])
templates = Jinja2Templates(directory="app/templates")


def _get_form_deps(conn):
    categories = conn.execute("SELECT * FROM categories ORDER BY sort_order, name").fetchall()
    populations = conn.execute("SELECT * FROM populations ORDER BY name").fetchall()
    locations = conn.execute("""
        SELECT l.id, l.label, l.address, o.name as org_name
        FROM locations l JOIN organizations o ON o.id=l.organization_id
        WHERE l.status='active' ORDER BY o.name, l.label
    """).fetchall()
    sources = conn.execute("SELECT id, title, source_type FROM sources ORDER BY retrieved_at DESC LIMIT 50").fetchall()
    return {"categories": categories, "populations": populations, "locations": locations, "sources": sources}


@router.get("/new", response_class=HTMLResponse)
def new_service_form(request: Request, location_id: str = ""):
    with db() as conn:
        deps = _get_form_deps(conn)
        selected_loc = None
        if location_id:
            selected_loc = conn.execute("""
                SELECT l.id, l.label, l.address, o.name as org_name
                FROM locations l JOIN organizations o ON o.id=l.organization_id WHERE l.id=?
            """, (location_id,)).fetchone()
    return templates.TemplateResponse(request, "services_/edit.html", {
        "service": None, "selected_loc": selected_loc,
        "service_cats": [], "service_pops": [], **deps,
    })


@router.post("/", response_class=HTMLResponse)
async def create_service(
    request: Request,
    location_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    primary_category_id: str = Form(""),
    recovery_subtype_id: str = Form(""),
    cost_model: str = Form("unknown"),
    access_mode: str = Form("walk_in"),
    referral_required: str = Form("0"),
    age_min: str = Form(""),
    age_max: str = Form(""),
    gender_restriction: str = Form("none"),
    capacity: str = Form(""),
    is_24_7: str = Form("0"),
    status: str = Form("active"),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("website"),
    reason: str = Form(...),
    editor: str = Form("user"),
):
    form_data = await request.form()
    category_ids = form_data.getlist("category_ids")
    population_ids = form_data.getlist("population_ids")

    with db() as conn:
        src_id = ensure_source(
            conn,
            int(source_id) if source_id else None,
            {"title": source_title, "url": source_url or None, "source_type": source_type} if source_title else None,
        )
        cur = conn.execute(
            """INSERT INTO services(location_id, name, description, primary_category_id,
               recovery_subtype_id, cost_model, access_mode, referral_required, age_min, age_max,
               gender_restriction, capacity, is_24_7, status)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (location_id, name, description or None,
             int(primary_category_id) if primary_category_id else None,
             int(recovery_subtype_id) if recovery_subtype_id else None,
             cost_model, access_mode,
             1 if referral_required == "1" else 0,
             int(age_min) if age_min else None,
             int(age_max) if age_max else None,
             gender_restriction,
             int(capacity) if capacity else None,
             1 if is_24_7 == "1" else 0,
             status),
        )
        svc_id = cur.lastrowid
        for cat_id in category_ids:
            conn.execute("INSERT OR IGNORE INTO service_categories VALUES(?,?)", (svc_id, int(cat_id)))
        for pop_id in population_ids:
            conn.execute("INSERT OR IGNORE INTO service_populations VALUES(?,?)", (svc_id, int(pop_id)))
        log_edit(conn, "service", svc_id, "create", editor, reason)
        queue_review(conn, "service", svc_id, "new", priority=40)
    return RedirectResponse(f"/services/{svc_id}", status_code=303)


@router.get("/{svc_id}", response_class=HTMLResponse)
def service_detail(request: Request, svc_id: int):
    with db() as conn:
        svc = conn.execute("SELECT * FROM services WHERE id=?", (svc_id,)).fetchone()
        if not svc:
            raise HTTPException(404)
        loc = conn.execute("""
            SELECT l.*, o.name as org_name, o.id as org_id
            FROM locations l JOIN organizations o ON o.id=l.organization_id WHERE l.id=?
        """, (svc["location_id"],)).fetchone()
        primary_cat = None
        if svc["primary_category_id"]:
            primary_cat = conn.execute("SELECT * FROM categories WHERE id=?", (svc["primary_category_id"],)).fetchone()
        recovery_sub = None
        if svc["recovery_subtype_id"]:
            recovery_sub = conn.execute("SELECT * FROM categories WHERE id=?", (svc["recovery_subtype_id"],)).fetchone()
        all_cats = conn.execute("""
            SELECT c.* FROM categories c JOIN service_categories sc ON sc.category_id=c.id WHERE sc.service_id=?
        """, (svc_id,)).fetchall()
        populations = conn.execute("""
            SELECT p.* FROM populations p JOIN service_populations sp ON sp.population_id=p.id WHERE sp.service_id=?
        """, (svc_id,)).fetchall()
        hours = conn.execute("SELECT * FROM hours WHERE service_id=? ORDER BY day_of_week", (svc_id,)).fetchall()
        contacts = conn.execute("SELECT * FROM contacts WHERE owner_type='service' AND owner_id=?", (svc_id,)).fetchall()
        provenance = conn.execute("""
            SELECT fp.*, s.title as source_title, s.url as source_url, s.source_type
            FROM field_provenance fp JOIN sources s ON s.id=fp.source_id
            WHERE fp.entity_type='service' AND fp.entity_id=?
            ORDER BY fp.verified_at DESC
        """, (svc_id,)).fetchall()
        edits = conn.execute(
            "SELECT * FROM edits WHERE entity_type='service' AND entity_id=? ORDER BY timestamp DESC LIMIT 20",
            (svc_id,)
        ).fetchall()
        queue = conn.execute(
            "SELECT * FROM review_queue WHERE entity_type='service' AND entity_id=? AND status='open'",
            (svc_id,)
        ).fetchall()
    return templates.TemplateResponse(request, "services_/detail.html", {
        "svc": svc, "loc": loc,
        "primary_cat": primary_cat, "recovery_sub": recovery_sub,
        "all_cats": all_cats, "populations": populations,
        "hours": hours, "contacts": contacts, "provenance": provenance,
        "edits": edits, "queue": queue,
    })


@router.get("/{svc_id}/edit", response_class=HTMLResponse)
def edit_service_form(request: Request, svc_id: int):
    with db() as conn:
        svc = conn.execute("SELECT * FROM services WHERE id=?", (svc_id,)).fetchone()
        if not svc:
            raise HTTPException(404)
        deps = _get_form_deps(conn)
        service_cats = [r["category_id"] for r in
                        conn.execute("SELECT category_id FROM service_categories WHERE service_id=?", (svc_id,)).fetchall()]
        service_pops = [r["population_id"] for r in
                        conn.execute("SELECT population_id FROM service_populations WHERE service_id=?", (svc_id,)).fetchall()]
    return templates.TemplateResponse(request, "services_/edit.html", {
        "service": svc, "service_cats": service_cats,
        "service_pops": service_pops, **deps,
    })


@router.post("/{svc_id}/edit", response_class=HTMLResponse)
async def update_service(
    request: Request,
    svc_id: int,
    location_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    primary_category_id: str = Form(""),
    recovery_subtype_id: str = Form(""),
    cost_model: str = Form("unknown"),
    access_mode: str = Form("walk_in"),
    referral_required: str = Form("0"),
    age_min: str = Form(""),
    age_max: str = Form(""),
    gender_restriction: str = Form("none"),
    capacity: str = Form(""),
    is_24_7: str = Form("0"),
    status: str = Form("active"),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("website"),
    reason: str = Form(...),
    editor: str = Form("user"),
):
    form_data = await request.form()
    category_ids = form_data.getlist("category_ids")
    population_ids = form_data.getlist("population_ids")

    with db() as conn:
        old = conn.execute("SELECT * FROM services WHERE id=?", (svc_id,)).fetchone()
        if not old:
            raise HTTPException(404)
        src_id = ensure_source(
            conn,
            int(source_id) if source_id else None,
            {"title": source_title, "url": source_url or None, "source_type": source_type} if source_title else None,
        )
        conn.execute(
            """UPDATE services SET location_id=?, name=?, description=?, primary_category_id=?,
               recovery_subtype_id=?, cost_model=?, access_mode=?, referral_required=?,
               age_min=?, age_max=?, gender_restriction=?, capacity=?, is_24_7=?, status=? WHERE id=?""",
            (location_id, name, description or None,
             int(primary_category_id) if primary_category_id else None,
             int(recovery_subtype_id) if recovery_subtype_id else None,
             cost_model, access_mode,
             1 if referral_required == "1" else 0,
             int(age_min) if age_min else None,
             int(age_max) if age_max else None,
             gender_restriction,
             int(capacity) if capacity else None,
             1 if is_24_7 == "1" else 0,
             status, svc_id),
        )
        conn.execute("DELETE FROM service_categories WHERE service_id=?", (svc_id,))
        conn.execute("DELETE FROM service_populations WHERE service_id=?", (svc_id,))
        for cat_id in category_ids:
            conn.execute("INSERT OR IGNORE INTO service_categories VALUES(?,?)", (svc_id, int(cat_id)))
        for pop_id in population_ids:
            conn.execute("INSERT OR IGNORE INTO service_populations VALUES(?,?)", (svc_id, int(pop_id)))
        log_edit(conn, "service", svc_id, "update", editor, reason)
    return RedirectResponse(f"/services/{svc_id}", status_code=303)


@router.post("/{svc_id}/verify", response_class=HTMLResponse)
def verify_service(
    request: Request,
    svc_id: int,
    editor: str = Form("user"),
    source_id: str = Form(""),
    source_title: str = Form(""),
    source_url: str = Form(""),
    source_type: str = Form("website"),
):
    with db() as conn:
        svc = conn.execute("SELECT * FROM services WHERE id=?", (svc_id,)).fetchone()
        if not svc:
            raise HTTPException(404)
        if source_id or source_title:
            src_id = ensure_source(
                conn,
                int(source_id) if source_id else None,
                {"title": source_title, "url": source_url or None, "source_type": source_type} if source_title else None,
            )
        conn.execute(
            "UPDATE services SET verified_at=CURRENT_TIMESTAMP, verified_by=? WHERE id=?",
            (editor, svc_id),
        )
        log_edit(conn, "service", svc_id, "verify", editor, "manual verification")
        resolve_queue(conn, "service", svc_id)
    return RedirectResponse(f"/services/{svc_id}", status_code=303)


@router.post("/{svc_id}/flag")
def flag_service(svc_id: int, note: str = Form("")):
    with db() as conn:
        queue_review(conn, "service", svc_id, "flagged", priority=70, note=note or None)
    return RedirectResponse(f"/services/{svc_id}", status_code=303)
