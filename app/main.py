from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import init_db
from app.routers import orgs, locations, services_, search, queue, export_, staging, contacts

app = FastAPI(title="Calgary Social Services Dashboard")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(search.router)
app.include_router(orgs.router)
app.include_router(locations.router)
app.include_router(services_.router)
app.include_router(queue.router)
app.include_router(export_.router)
app.include_router(staging.router)
app.include_router(contacts.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
