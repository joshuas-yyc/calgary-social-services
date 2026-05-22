from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import db
from app.services.audit import run_staleness_audit

router = APIRouter(prefix="/queue", tags=["queue"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def queue_list(request: Request):
    with db() as conn:
        items = conn.execute("""
            SELECT q.*,
                CASE q.entity_type
                    WHEN 'org' THEN (SELECT name FROM organizations WHERE id=q.entity_id)
                    WHEN 'location' THEN (SELECT COALESCE(label, address) FROM locations WHERE id=q.entity_id)
                    WHEN 'service' THEN (SELECT name FROM services WHERE id=q.entity_id)
                    ELSE NULL
                END as entity_name
            FROM review_queue q
            WHERE q.status='open'
            ORDER BY q.priority DESC, q.created_at ASC
        """).fetchall()
        counts = {
            "new": sum(1 for i in items if i["reason"] == "new"),
            "stale": sum(1 for i in items if i["reason"] == "stale"),
            "conflict": sum(1 for i in items if i["reason"] == "conflict"),
            "flagged": sum(1 for i in items if i["reason"] == "flagged"),
        }
    return templates.TemplateResponse(request, "queue/list.html", {
        "items": items, "counts": counts,
    })


@router.post("/resolve/{item_id}")
def resolve_item(item_id: int, note: str = Form("")):
    with db() as conn:
        conn.execute(
            "UPDATE review_queue SET status='resolved', resolved_at=CURRENT_TIMESTAMP WHERE id=?",
            (item_id,),
        )
    return RedirectResponse("/queue", status_code=303)


@router.post("/audit")
def run_audit(request: Request):
    with db() as conn:
        result = run_staleness_audit(conn)
    return RedirectResponse(f"/queue?audit_flagged={result['flagged']}", status_code=303)
