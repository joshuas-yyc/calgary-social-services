from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.database import db

router = APIRouter(tags=["search"])
templates = Jinja2Templates(directory="app/templates")


def build_search_query(
    q: str, category_id: int, recovery_subtype_id: int, population_id: int,
    quadrant: str, cost_model: str, access_mode: str, is_24_7: bool,
    wheelchair_accessible: bool, status: str, limit: int, offset: int,
) -> tuple[str, list]:
    conditions = []
    params = []

    if status:
        conditions.append("s.status = ?")
        params.append(status)

    if category_id:
        conditions.append("(s.primary_category_id = ? OR s.recovery_subtype_id = ? OR EXISTS (SELECT 1 FROM service_categories sc WHERE sc.service_id=s.id AND sc.category_id=?))")
        params.extend([category_id, category_id, category_id])

    if recovery_subtype_id:
        conditions.append("s.recovery_subtype_id = ?")
        params.append(recovery_subtype_id)

    if population_id:
        conditions.append("EXISTS (SELECT 1 FROM service_populations sp WHERE sp.service_id=s.id AND sp.population_id=?)")
        params.append(population_id)

    if quadrant:
        conditions.append("l.quadrant = ?")
        params.append(quadrant)

    if cost_model:
        conditions.append("s.cost_model = ?")
        params.append(cost_model)

    if access_mode:
        conditions.append("s.access_mode = ?")
        params.append(access_mode)

    if is_24_7 is not None:
        conditions.append("s.is_24_7 = ?")
        params.append(1 if is_24_7 else 0)

    if wheelchair_accessible is not None:
        conditions.append("l.wheelchair_accessible = ?")
        params.append(1 if wheelchair_accessible else 0)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    if q:
        sql = f"""
            SELECT s.id, s.name as service_name, s.status, s.cost_model, s.access_mode,
                   s.is_24_7, s.verified_at, s.age_min, s.age_max, s.gender_restriction,
                   l.address, l.quadrant, l.community, l.wheelchair_accessible,
                   o.name as org_name, o.id as org_id, o.indigenous_led,
                   c.name as category_name, c.slug as category_slug
            FROM services s
            JOIN locations l ON l.id=s.location_id
            JOIN organizations o ON o.id=l.organization_id
            LEFT JOIN categories c ON c.id=s.primary_category_id
            WHERE s.id IN (
                SELECT CAST(service_id AS INTEGER) FROM services_fts WHERE services_fts MATCH ?
            )
            {('AND ' + ' AND '.join(conditions)) if conditions else ''}
            ORDER BY s.name LIMIT ? OFFSET ?
        """
        fts_term = q.replace('"', '""')
        return sql, [f'"{fts_term}"'] + params + [limit, offset]
    else:
        sql = f"""
            SELECT s.id, s.name as service_name, s.status, s.cost_model, s.access_mode,
                   s.is_24_7, s.verified_at, s.age_min, s.age_max, s.gender_restriction,
                   l.address, l.quadrant, l.community, l.wheelchair_accessible,
                   o.name as org_name, o.id as org_id, o.indigenous_led,
                   c.name as category_name, c.slug as category_slug
            FROM services s
            JOIN locations l ON l.id=s.location_id
            JOIN organizations o ON o.id=l.organization_id
            LEFT JOIN categories c ON c.id=s.primary_category_id
            {where}
            ORDER BY s.name LIMIT ? OFFSET ?
        """
        return sql, params + [limit, offset]


@router.get("/", response_class=HTMLResponse)
def search(
    request: Request,
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    recovery_subtype_id: Optional[int] = Query(None),
    population_id: Optional[int] = Query(None),
    quadrant: Optional[str] = Query(None),
    cost_model: Optional[str] = Query(None),
    access_mode: Optional[str] = Query(None),
    is_24_7: Optional[bool] = Query(None),
    wheelchair_accessible: Optional[bool] = Query(None),
    status: str = Query("active"),
    limit: int = Query(50),
    offset: int = Query(0),
):
    with db() as conn:
        categories = conn.execute("SELECT * FROM categories ORDER BY sort_order, name").fetchall()
        populations = conn.execute("SELECT * FROM populations ORDER BY name").fetchall()

        try:
            sql, params = build_search_query(
                q, category_id, recovery_subtype_id, population_id,
                quadrant, cost_model, access_mode, is_24_7,
                wheelchair_accessible, status, limit, offset,
            )
            results = conn.execute(sql, params).fetchall()
        except Exception as e:
            results = []

        # Attach populations to each result
        enriched = []
        for r in results:
            pops = conn.execute("""
                SELECT p.name FROM populations p
                JOIN service_populations sp ON sp.population_id=p.id WHERE sp.service_id=?
            """, (r["id"],)).fetchall()
            enriched.append({"row": r, "populations": [p["name"] for p in pops]})

    filters_active = any([q, category_id, recovery_subtype_id, population_id,
                          quadrant, cost_model, access_mode, is_24_7, wheelchair_accessible])

    return templates.TemplateResponse(request, "search.html", {
        "results": enriched,
        "categories": categories,
        "populations": populations,
        "q": q or "",
        "category_id": category_id,
        "recovery_subtype_id": recovery_subtype_id,
        "population_id": population_id,
        "quadrant": quadrant or "",
        "cost_model": cost_model or "",
        "access_mode": access_mode or "",
        "is_24_7": is_24_7,
        "wheelchair_accessible": wheelchair_accessible,
        "status": status,
        "filters_active": filters_active,
        "count": len(results),
    })


@router.get("/map", response_class=HTMLResponse)
def map_view(request: Request):
    with db() as conn:
        points = conn.execute("""
            SELECT s.id, s.name as service_name, s.cost_model, s.access_mode, s.is_24_7,
                   l.latitude, l.longitude, l.address, l.quadrant, l.community,
                   o.name as org_name,
                   c.name as category_name, c.slug as category_slug
            FROM services s
            JOIN locations l ON l.id=s.location_id
            JOIN organizations o ON o.id=l.organization_id
            LEFT JOIN categories c ON c.id=s.primary_category_id
            WHERE s.status='active' AND l.latitude IS NOT NULL AND l.longitude IS NOT NULL
        """).fetchall()
        categories = conn.execute("SELECT * FROM categories WHERE parent_id IS NULL ORDER BY sort_order").fetchall()
    import json
    points_json = json.dumps([dict(p) for p in points])
    return templates.TemplateResponse(request, "map.html", {
        "points_json": points_json, "categories": categories,
    })
