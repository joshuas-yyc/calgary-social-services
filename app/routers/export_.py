from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from app.database import db
from app.services.export_ import export_json, export_geojson, export_csv

router = APIRouter(prefix="/export", tags=["export"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def export_page(request: Request):
    with db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM services WHERE status='active' AND verified_at IS NOT NULL"
        ).fetchone()[0]
    return templates.TemplateResponse(request, "export.html", {"verified_count": count})


@router.get("/json")
def get_json(request: Request):
    with db() as conn:
        data = export_json(conn)
    return Response(content=data, media_type="application/json",
                    headers={"Content-Disposition": "attachment; filename=calgary-services.json"})


@router.get("/geojson")
def get_geojson(request: Request):
    with db() as conn:
        data = export_geojson(conn)
    return Response(content=data, media_type="application/geo+json",
                    headers={"Content-Disposition": "attachment; filename=calgary-services.geojson"})


@router.get("/csv")
def get_csv(request: Request):
    with db() as conn:
        data = export_csv(conn)
    return Response(content=data, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=calgary-services.csv"})
