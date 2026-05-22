from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import db
from app.services.scraper import SOURCES, run_scrape

router = APIRouter(prefix="/scrape", tags=["scraper"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def scrape_page(request: Request):
    return templates.TemplateResponse(request, "scraper/index.html", {"sources": SOURCES})


@router.post("/run")
def run_scraper(source: str = Form(...)):
    with db() as conn:
        result = run_scrape(source, conn)
    params = f"scraped={result['staged']}&skipped={result['skipped']}"
    if result.get("errors"):
        params += f"&scrape_errors={len(result['errors'])}"
    return RedirectResponse(f"/staging/?{params}", status_code=303)
