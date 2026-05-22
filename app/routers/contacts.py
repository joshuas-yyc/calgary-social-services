from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.database import db

router = APIRouter(prefix="/contacts", tags=["contacts"])

OWNER_REDIRECTS = {
    "org": lambda oid: f"/orgs/{oid}",
    "location": lambda oid: f"/locations/{oid}",
    "service": lambda oid: f"/services/{oid}",
}


@router.post("/")
def add_contact(
    owner_type: str = Form(...),
    owner_id: int = Form(...),
    kind: str = Form(...),
    value: str = Form(...),
    is_primary: str = Form("0"),
):
    if owner_type not in OWNER_REDIRECTS:
        raise HTTPException(400, "Invalid owner_type")
    with db() as conn:
        conn.execute(
            "INSERT INTO contacts(owner_type, owner_id, kind, value, is_primary) VALUES(?,?,?,?,?)",
            (owner_type, owner_id, kind, value, 1 if is_primary == "1" else 0),
        )
    return RedirectResponse(OWNER_REDIRECTS[owner_type](owner_id), status_code=303)


@router.post("/{contact_id}/delete")
def delete_contact(contact_id: int):
    with db() as conn:
        row = conn.execute("SELECT owner_type, owner_id FROM contacts WHERE id=?", (contact_id,)).fetchone()
        if not row:
            raise HTTPException(404)
        conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    return RedirectResponse(OWNER_REDIRECTS[row["owner_type"]](row["owner_id"]), status_code=303)
