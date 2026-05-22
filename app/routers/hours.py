from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.database import db

router = APIRouter(prefix="/hours", tags=["hours"])


@router.post("/")
def add_hour(
    service_id: int = Form(...),
    day_of_week: int = Form(...),
    opens: str = Form(""),
    closes: str = Form(""),
    is_24_7: str = Form("0"),
    note: str = Form(""),
):
    with db() as conn:
        svc = conn.execute("SELECT id FROM services WHERE id=?", (service_id,)).fetchone()
        if not svc:
            raise HTTPException(404)
        conn.execute(
            "INSERT INTO hours(service_id, day_of_week, opens, closes, is_24_7, note) VALUES(?,?,?,?,?,?)",
            (service_id, day_of_week, opens or None, closes or None,
             1 if is_24_7 == "1" else 0, note or None),
        )
    return RedirectResponse(f"/services/{service_id}", status_code=303)


@router.post("/{hour_id}/delete")
def delete_hour(hour_id: int):
    with db() as conn:
        row = conn.execute("SELECT service_id FROM hours WHERE id=?", (hour_id,)).fetchone()
        if not row:
            raise HTTPException(404)
        conn.execute("DELETE FROM hours WHERE id=?", (hour_id,))
    return RedirectResponse(f"/services/{row['service_id']}", status_code=303)
