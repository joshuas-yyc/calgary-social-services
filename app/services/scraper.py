"""
Pluggable scraper sources. Each source returns a list of dicts that get
inserted into the staging table for human review.

To add a new source:
  1. Write a function that returns list[dict] (see _scrape_calgary_shelter_data).
  2. Register it in SOURCES and the dispatch in run_scrape().
"""
import json
import httpx

SOURCES = {
    "calgary_shelter_data": {
        "label": "Calgary Open Data — Emergency Shelter Occupancy",
        "url": "https://data.calgary.ca/resource/7u2t-3wxf",
        "description": "Unique shelter organizations from the provincial shelter occupancy dataset.",
    },
    "calgary_ca_housing": {
        "label": "Calgary.ca — Housing & Homelessness Programs",
        "url": "https://www.calgary.ca/social-services/housing.html",
        "description": "City of Calgary housing and homelessness program listings.",
    },
    "calgary_ca_mental_health": {
        "label": "Calgary.ca — Mental Health Resources",
        "url": "https://www.calgary.ca/social-services/mental-health.html",
        "description": "City of Calgary mental health program and partner listings.",
    },
}


# ---------------------------------------------------------------------------
# Source: Calgary Open Data — shelter occupancy (Socrata JSON API)
# ---------------------------------------------------------------------------

def _scrape_calgary_shelter_data() -> list[dict]:
    url = (
        "https://data.calgary.ca/resource/7u2t-3wxf.json"
        "?$select=organization,sheltername,sheltertype"
        "&$group=organization,sheltername,sheltertype"
        "&$order=organization"
        "&$limit=500"
    )
    resp = httpx.get(url, timeout=20, follow_redirects=True)
    resp.raise_for_status()
    rows = resp.json()

    orgs: dict[str, list[dict]] = {}
    for row in rows:
        org = (row.get("organization") or "").strip()
        if not org:
            continue
        # Skip COVID-era overflow/isolation sites — they're not permanent programs
        shelter_name = (row.get("sheltername") or "").strip()
        shelter_type = (row.get("sheltertype") or "").strip()
        skip_keywords = ("COVID", "Isolation Site", "Expanded Shelter", "Days Inn",
                         "Clarion", "First Alliance", "Lakeview Hotel", "Telus Convention")
        if any(kw.lower() in shelter_name.lower() or kw.lower() in shelter_type.lower()
               for kw in skip_keywords):
            continue
        orgs.setdefault(org, []).append({
            "shelter_name": shelter_name,
            "shelter_type": shelter_type,
        })

    records = []
    for org_name, shelters in sorted(orgs.items()):
        # Infer primary category from shelter types present
        types = {s["shelter_type"] for s in shelters}
        if any("Family" in t for t in types):
            category = "housing"
            population_hint = "Families"
        elif any("Women" in t for t in types):
            category = "housing"
            population_hint = "Women"
        elif "Transitional" in types:
            category = "housing"
            population_hint = "Adults"
        else:
            category = "housing"
            population_hint = "Adults, People Experiencing Homelessness"

        records.append({
            "org_name": org_name,
            "suggested_category": category,
            "suggested_populations": population_hint,
            "shelters": shelters,
            "notes": (
                f"Sourced from Calgary Open Data shelter occupancy dataset. "
                f"{len(shelters)} shelter program(s) on record. "
                "Address, phone, and website require manual verification."
            ),
        })

    return records


# ---------------------------------------------------------------------------
# Source: Calgary.ca pages (HTML scrape)
# ---------------------------------------------------------------------------

def _scrape_calgary_ca_page(page_url: str, source_label: str) -> list[dict]:
    """
    Generic Calgary.ca page scraper. Extracts linked program/org names and
    any phone numbers or emails found near headings.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise RuntimeError("beautifulsoup4 not installed. Run: uv add beautifulsoup4")

    import re
    resp = httpx.get(page_url, timeout=20, follow_redirects=True,
                     headers={"User-Agent": "Calgary Social Services Directory Bot/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    phone_re = re.compile(r"\b(\d{3}[-.\s]\d{3}[-.\s]\d{4}|\(\d{3}\)\s*\d{3}[-.\s]\d{4})\b")
    email_re = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

    records = []
    seen: set[str] = set()

    # Walk h2/h3/h4 headings — each one may be a program or org
    for heading in soup.find_all(["h2", "h3", "h4"]):
        name = heading.get_text(strip=True)
        if not name or len(name) < 5 or name.lower() in ("contact us", "related links",
                                                           "on this page", "search"):
            continue
        if name.lower() in seen:
            continue
        seen.add(name.lower())

        # Grab the next sibling paragraph(s) for description + contacts
        description_parts = []
        phones, emails, links = [], [], []
        node = heading.find_next_sibling()
        for _ in range(4):
            if node is None or node.name in ("h2", "h3", "h4"):
                break
            text = node.get_text(" ", strip=True)
            description_parts.append(text)
            phones += phone_re.findall(text)
            emails += email_re.findall(text)
            for a in node.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "calgary.ca" not in href:
                    links.append(href)
            node = node.find_next_sibling()

        records.append({
            "org_name": name,
            "description": " ".join(description_parts)[:500] or None,
            "suggested_category": "mental-health" if "mental" in page_url else "housing",
            "suggested_populations": "Adults",
            "contacts": (
                [{"kind": "phone", "value": p} for p in phones[:2]] +
                [{"kind": "email", "value": e} for e in emails[:2]] +
                [{"kind": "web", "value": l} for l in links[:1]]
            ),
            "notes": f"Scraped from {page_url}. Verify all details before accepting.",
        })

    return records


# ---------------------------------------------------------------------------
# Deduplication helpers
# ---------------------------------------------------------------------------

def _known_names(conn) -> set[str]:
    orgs = {r[0].lower() for r in conn.execute("SELECT name FROM organizations").fetchall()}
    staged = set()
    for r in conn.execute("SELECT raw_json FROM staging WHERE status='pending'").fetchall():
        try:
            d = json.loads(r[0])
            if name := d.get("org_name"):
                staged.add(name.lower())
        except Exception:
            pass
    return orgs | staged


def _ensure_source(conn, source_key: str) -> int:
    meta = SOURCES[source_key]
    row = conn.execute("SELECT id FROM sources WHERE title=?", (meta["label"],)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO sources(title, source_type, notes) VALUES(?,?,?)",
        (meta["label"], "website", meta["description"]),
    )
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_scrape(source_key: str, conn) -> dict:
    """
    Runs the named scrape source. Inserts new records into staging,
    skipping any org already in organizations or pending staging.
    Returns {"staged": int, "skipped": int, "errors": list[str]}.
    """
    if source_key not in SOURCES:
        raise ValueError(f"Unknown source key: {source_key!r}")

    errors: list[str] = []
    try:
        if source_key == "calgary_shelter_data":
            records = _scrape_calgary_shelter_data()
        elif source_key in ("calgary_ca_housing", "calgary_ca_mental_health"):
            records = _scrape_calgary_ca_page(
                SOURCES[source_key]["url"], SOURCES[source_key]["label"]
            )
        else:
            raise ValueError(f"No handler for source: {source_key!r}")
    except Exception as exc:
        return {"staged": 0, "skipped": 0, "errors": [str(exc)]}

    known = _known_names(conn)
    src_id = _ensure_source(conn, source_key)

    staged = skipped = 0
    for rec in records:
        name = rec.get("org_name", "")
        if not name or name.lower() in known:
            skipped += 1
            continue
        try:
            conn.execute(
                "INSERT INTO staging(raw_json, source_id) VALUES(?,?)",
                (json.dumps(rec), src_id),
            )
            known.add(name.lower())
            staged += 1
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    return {"staged": staged, "skipped": skipped, "errors": errors}
