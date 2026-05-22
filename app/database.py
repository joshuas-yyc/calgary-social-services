import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

_data_dir = os.environ.get("CALGARY_DATA_DIR")
DB_PATH = Path(_data_dir) / "calgary.sqlite" if _data_dir else Path(__file__).parent.parent / "data" / "calgary.sqlite"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    legal_name TEXT,
    parent_org_id INTEGER REFERENCES organizations(id),
    indigenous_led BOOLEAN NOT NULL DEFAULT 0,
    description TEXT,
    website TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','closed','merged')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    slug TEXT NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS populations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    label TEXT,
    address TEXT,
    quadrant TEXT CHECK(quadrant IN ('NW','NE','SW','SE')),
    community TEXT,
    latitude REAL,
    longitude REAL,
    wheelchair_accessible BOOLEAN DEFAULT 0,
    transit_note TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL REFERENCES locations(id),
    name TEXT NOT NULL,
    description TEXT,
    primary_category_id INTEGER REFERENCES categories(id),
    recovery_subtype_id INTEGER REFERENCES categories(id),
    cost_model TEXT DEFAULT 'unknown' CHECK(cost_model IN ('free','sliding_scale','fee','unknown')),
    access_mode TEXT DEFAULT 'walk_in' CHECK(access_mode IN ('walk_in','referral','appointment','mixed')),
    referral_required BOOLEAN DEFAULT 0,
    age_min INTEGER,
    age_max INTEGER,
    gender_restriction TEXT DEFAULT 'none' CHECK(gender_restriction IN ('none','women','men','other')),
    capacity INTEGER,
    is_24_7 BOOLEAN DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','waitlist','closed')),
    verified_at TIMESTAMP,
    verified_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_categories (
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    PRIMARY KEY (service_id, category_id)
);

CREATE TABLE IF NOT EXISTS service_populations (
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    population_id INTEGER NOT NULL REFERENCES populations(id),
    PRIMARY KEY (service_id, population_id)
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_type TEXT NOT NULL CHECK(owner_type IN ('org','location','service')),
    owner_id INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('phone','email','intake_line','crisis_line','web','facebook','instagram','twitter','linkedin','youtube','tiktok')),
    value TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6),
    opens TEXT,
    closes TEXT,
    is_24_7 BOOLEAN DEFAULT 0,
    note TEXT,
    season TEXT
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('website','pdf','phone_call','in_person','govt_registry','211')),
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS field_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    verified_by TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence TEXT DEFAULT 'med' CHECK(confidence IN ('high','med','low'))
);

CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_org_id INTEGER NOT NULL REFERENCES organizations(id),
    to_org_id INTEGER NOT NULL REFERENCES organizations(id),
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('refers_to','partners_with','operated_by','funds')),
    note TEXT
);

CREATE TABLE IF NOT EXISTS edits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    field_name TEXT,
    old_value TEXT,
    new_value TEXT,
    action TEXT NOT NULL CHECK(action IN ('create','update','delete','verify')),
    editor TEXT DEFAULT 'user',
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('new','stale','conflict','flagged')),
    priority INTEGER DEFAULT 50,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','resolved')),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_json TEXT NOT NULL,
    source_id INTEGER REFERENCES sources(id),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','accepted','rejected')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS entity_tags (
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    PRIMARY KEY (tag_id, entity_type, entity_id)
);

-- FTS5 virtual table for search
CREATE VIRTUAL TABLE IF NOT EXISTS services_fts USING fts5(
    service_id UNINDEXED,
    service_name,
    service_description,
    org_name,
    location_address,
    community,
    content='',
    contentless_delete=1
);

CREATE TRIGGER IF NOT EXISTS services_fts_insert
AFTER INSERT ON services BEGIN
    INSERT INTO services_fts(rowid, service_id, service_name, service_description, org_name, location_address, community)
    SELECT NEW.id, NEW.id, NEW.name, COALESCE(NEW.description,''),
           (SELECT o.name FROM organizations o JOIN locations l ON l.organization_id=o.id WHERE l.id=NEW.location_id),
           (SELECT l.address FROM locations l WHERE l.id=NEW.location_id),
           (SELECT l.community FROM locations l WHERE l.id=NEW.location_id);
END;

CREATE TRIGGER IF NOT EXISTS services_fts_update
AFTER UPDATE ON services BEGIN
    DELETE FROM services_fts WHERE rowid=OLD.id;
    INSERT INTO services_fts(rowid, service_id, service_name, service_description, org_name, location_address, community)
    SELECT NEW.id, NEW.id, NEW.name, COALESCE(NEW.description,''),
           (SELECT o.name FROM organizations o JOIN locations l ON l.organization_id=o.id WHERE l.id=NEW.location_id),
           (SELECT l.address FROM locations l WHERE l.id=NEW.location_id),
           (SELECT l.community FROM locations l WHERE l.id=NEW.location_id);
END;

CREATE TRIGGER IF NOT EXISTS services_fts_delete
AFTER DELETE ON services BEGIN
    DELETE FROM services_fts WHERE rowid=OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS orgs_updated
AFTER UPDATE ON organizations BEGIN
    UPDATE organizations SET updated_at=CURRENT_TIMESTAMP WHERE id=NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS locations_updated
AFTER UPDATE ON locations BEGIN
    UPDATE locations SET updated_at=CURRENT_TIMESTAMP WHERE id=NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS services_updated
AFTER UPDATE ON services BEGIN
    UPDATE services SET updated_at=CURRENT_TIMESTAMP WHERE id=NEW.id;
END;
"""

SEED_CATEGORIES = [
    (1, "Housing", None, "housing", 10),
    (2, "Mental Health", None, "mental-health", 20),
    (3, "Addiction Recovery", None, "addiction-recovery", 30),
    (4, "Detox / Withdrawal Management", 3, "detox", 31),
    (5, "Residential / Inpatient Treatment", 3, "residential-inpatient", 32),
    (6, "Harm Reduction", 3, "harm-reduction", 33),
    (7, "Indigenous Healing / Land-based", 3, "indigenous-healing", 34),
    (8, "Youth Recovery", 3, "youth-recovery", 35),
    (9, "Outpatient / Day Program", 3, "outpatient", 36),
    (10, "Recovery Community / Aftercare / Sober Living", 3, "recovery-community", 37),
    (11, "Youth Services", None, "youth-services", 40),
    (12, "Indigenous Services", None, "indigenous-services", 50),
    (13, "Newcomer / Refugee Services", None, "newcomer-refugee", 60),
    (14, "Poverty Reduction", None, "poverty-reduction", 70),
    (15, "Crisis Services", None, "crisis-services", 80),
]

SEED_POPULATIONS = [
    ("Youth", "youth"),
    ("Adults", "adults"),
    ("Women", "women"),
    ("Men", "men"),
    ("Indigenous", "indigenous"),
    ("Newcomers / Refugees", "newcomers-refugees"),
    ("LGBTQ2S+", "lgbtq2s"),
    ("Families", "families"),
    ("Seniors", "seniors"),
    ("Veterans", "veterans"),
    ("People Experiencing Homelessness", "experiencing-homelessness"),
]


CONTACT_KINDS = "('phone','email','intake_line','crisis_line','web','facebook','instagram','twitter','linkedin','youtube','tiktok')"


def _migrate_contacts_kinds(conn):
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='contacts'"
    ).fetchone()
    if row and "facebook" not in row["sql"]:
        conn.executescript(f"""
            CREATE TABLE contacts_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_type TEXT NOT NULL CHECK(owner_type IN ('org','location','service')),
                owner_id INTEGER NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN {CONTACT_KINDS}),
                value TEXT NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            INSERT INTO contacts_new SELECT * FROM contacts;
            DROP TABLE contacts;
            ALTER TABLE contacts_new RENAME TO contacts;
        """)


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        _migrate_contacts_kinds(conn)
        for row in SEED_CATEGORIES:
            conn.execute(
                "INSERT OR IGNORE INTO categories(id,name,parent_id,slug,sort_order) VALUES(?,?,?,?,?)",
                row,
            )
        for name, slug in SEED_POPULATIONS:
            conn.execute(
                "INSERT OR IGNORE INTO populations(name,slug) VALUES(?,?)",
                (name, slug),
            )
        conn.commit()
    finally:
        conn.close()
