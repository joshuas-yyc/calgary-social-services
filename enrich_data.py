"""
Fills in missing contacts (web, phone) and hours for all seeded organizations.
Run: uv run python enrich_data.py
"""
from app.database import init_db, db

# ---------------------------------------------------------------------------
# Hours data — (service_id, day_of_week 0=Mon…6=Sun, opens, closes, is_24_7, note)
# ---------------------------------------------------------------------------
HOURS = [
    # 1 Emergency Overnight Shelter — Calgary Drop-In — 24/7
    (1, 0, None, None, 1, None), (1, 1, None, None, 1, None), (1, 2, None, None, 1, None),
    (1, 3, None, None, 1, None), (1, 4, None, None, 1, None), (1, 5, None, None, 1, None),
    (1, 6, None, None, 1, None),

    # 2 Day Program — Calgary Drop-In — Mon–Sun 7:00–21:00
    (2, 0, "07:00", "21:00", 0, None), (2, 1, "07:00", "21:00", 0, None),
    (2, 2, "07:00", "21:00", 0, None), (2, 3, "07:00", "21:00", 0, None),
    (2, 4, "07:00", "21:00", 0, None), (2, 5, "07:00", "21:00", 0, None),
    (2, 6, "07:00", "21:00", 0, None),

    # 3 Housing Support Services — Mon–Fri 8:30–16:30
    (3, 0, "08:30", "16:30", 0, None), (3, 1, "08:30", "16:30", 0, None),
    (3, 2, "08:30", "16:30", 0, None), (3, 3, "08:30", "16:30", 0, None),
    (3, 4, "08:30", "16:30", 0, None),

    # 4 Detox / Withdrawal Management — Alpha House — 24/7
    (4, 0, None, None, 1, None), (4, 1, None, None, 1, None), (4, 2, None, None, 1, None),
    (4, 3, None, None, 1, None), (4, 4, None, None, 1, None), (4, 5, None, None, 1, None),
    (4, 6, None, None, 1, None),

    # 5 DOAP Team — Alpha House — Mon–Sun 10:00–22:00
    (5, 0, "10:00", "22:00", 0, "Street outreach"), (5, 1, "10:00", "22:00", 0, "Street outreach"),
    (5, 2, "10:00", "22:00", 0, "Street outreach"), (5, 3, "10:00", "22:00", 0, "Street outreach"),
    (5, 4, "10:00", "22:00", 0, "Street outreach"), (5, 5, "10:00", "22:00", 0, "Street outreach"),
    (5, 6, "10:00", "22:00", 0, "Street outreach"),

    # 6 Primary Health Care — CUPS — Mon–Fri 9:00–17:00
    (6, 0, "09:00", "17:00", 0, None), (6, 1, "09:00", "17:00", 0, None),
    (6, 2, "09:00", "17:00", 0, None), (6, 3, "09:00", "17:00", 0, None),
    (6, 4, "09:00", "17:00", 0, None),

    # 7 Child Development Programs — CUPS — Mon–Fri 8:00–17:00
    (7, 0, "08:00", "17:00", 0, None), (7, 1, "08:00", "17:00", 0, None),
    (7, 2, "08:00", "17:00", 0, None), (7, 3, "08:00", "17:00", 0, None),
    (7, 4, "08:00", "17:00", 0, None),

    # 8 Housing Stability Support — CUPS — Mon–Fri 8:30–16:30
    (8, 0, "08:30", "16:30", 0, None), (8, 1, "08:30", "16:30", 0, None),
    (8, 2, "08:30", "16:30", 0, None), (8, 3, "08:30", "16:30", 0, None),
    (8, 4, "08:30", "16:30", 0, None),

    # 9 Emergency Food Bank — Mustard Seed — Mon–Sat 9:00–15:00
    (9, 0, "09:00", "15:00", 0, None), (9, 1, "09:00", "15:00", 0, None),
    (9, 2, "09:00", "15:00", 0, None), (9, 3, "09:00", "15:00", 0, None),
    (9, 4, "09:00", "15:00", 0, None), (9, 5, "09:00", "13:00", 0, None),

    # 10 Street Outreach — Mustard Seed — Mon–Sun 18:00–22:00
    (10, 0, "18:00", "22:00", 0, "Evening outreach"), (10, 1, "18:00", "22:00", 0, "Evening outreach"),
    (10, 2, "18:00", "22:00", 0, "Evening outreach"), (10, 3, "18:00", "22:00", 0, "Evening outreach"),
    (10, 4, "18:00", "22:00", 0, "Evening outreach"), (10, 5, "18:00", "22:00", 0, "Evening outreach"),
    (10, 6, "18:00", "22:00", 0, "Evening outreach"),

    # 11 Recovery Community — Mustard Seed — Mon–Fri 9:00–21:00, Sat 9:00–17:00
    (11, 0, "09:00", "21:00", 0, None), (11, 1, "09:00", "21:00", 0, None),
    (11, 2, "09:00", "21:00", 0, None), (11, 3, "09:00", "21:00", 0, None),
    (11, 4, "09:00", "21:00", 0, None), (11, 5, "09:00", "17:00", 0, None),

    # 12 24/7 Crisis Line — Distress Centre — 24/7
    (12, 0, None, None, 1, None), (12, 1, None, None, 1, None), (12, 2, None, None, 1, None),
    (12, 3, None, None, 1, None), (12, 4, None, None, 1, None), (12, 5, None, None, 1, None),
    (12, 6, None, None, 1, None),

    # 13 211 Alberta Helpline — 24/7
    (13, 0, None, None, 1, None), (13, 1, None, None, 1, None), (13, 2, None, None, 1, None),
    (13, 3, None, None, 1, None), (13, 4, None, None, 1, None), (13, 5, None, None, 1, None),
    (13, 6, None, None, 1, None),

    # 14 Family Emergency Shelter — Inn from the Cold — 24/7
    (14, 0, None, None, 1, None), (14, 1, None, None, 1, None), (14, 2, None, None, 1, None),
    (14, 3, None, None, 1, None), (14, 4, None, None, 1, None), (14, 5, None, None, 1, None),
    (14, 6, None, None, 1, None),

    # 15 Prevention and Diversion — Inn from the Cold — Mon–Fri 8:00–16:30
    (15, 0, "08:00", "16:30", 0, None), (15, 1, "08:00", "16:30", 0, None),
    (15, 2, "08:00", "16:30", 0, None), (15, 3, "08:00", "16:30", 0, None),
    (15, 4, "08:00", "16:30", 0, None),

    # 16 Emergency Food Hamper — Calgary Food Bank — Mon–Fri 9:00–16:00, Sat 8:00–12:00
    (16, 0, "09:00", "16:00", 0, "By appointment"), (16, 1, "09:00", "16:00", 0, "By appointment"),
    (16, 2, "09:00", "16:00", 0, "By appointment"), (16, 3, "09:00", "16:00", 0, "By appointment"),
    (16, 4, "09:00", "16:00", 0, "By appointment"), (16, 5, "08:00", "12:00", 0, "By appointment"),

    # 17 Youth Crisis Stabilization — Wood's Homes — 24/7
    (17, 0, None, None, 1, None), (17, 1, None, None, 1, None), (17, 2, None, None, 1, None),
    (17, 3, None, None, 1, None), (17, 4, None, None, 1, None), (17, 5, None, None, 1, None),
    (17, 6, None, None, 1, None),

    # 18 Outpatient Mental Health — Wood's Homes — Mon–Fri 8:30–16:30
    (18, 0, "08:30", "16:30", 0, None), (18, 1, "08:30", "16:30", 0, None),
    (18, 2, "08:30", "16:30", 0, None), (18, 3, "08:30", "16:30", 0, None),
    (18, 4, "08:30", "16:30", 0, None),

    # 19 Individual Counselling — Calgary Counselling — Mon–Fri 8:00–20:00, Sat 9:00–16:00
    (19, 0, "08:00", "20:00", 0, None), (19, 1, "08:00", "20:00", 0, None),
    (19, 2, "08:00", "20:00", 0, None), (19, 3, "08:00", "20:00", 0, None),
    (19, 4, "08:00", "20:00", 0, None), (19, 5, "09:00", "16:00", 0, None),

    # 20 Couples Counselling — Mon–Fri 9:00–17:00
    (20, 0, "09:00", "17:00", 0, None), (20, 1, "09:00", "17:00", 0, None),
    (20, 2, "09:00", "17:00", 0, None), (20, 3, "09:00", "17:00", 0, None),
    (20, 4, "09:00", "17:00", 0, None),

    # 21 Youth Counselling — Mon–Fri 9:00–17:00
    (21, 0, "09:00", "17:00", 0, None), (21, 1, "09:00", "17:00", 0, None),
    (21, 2, "09:00", "17:00", 0, None), (21, 3, "09:00", "17:00", 0, None),
    (21, 4, "09:00", "17:00", 0, None),

    # 22 Emergency Shelter for Women — YWCA — 24/7
    (22, 0, None, None, 1, None), (22, 1, None, None, 1, None), (22, 2, None, None, 1, None),
    (22, 3, None, None, 1, None), (22, 4, None, None, 1, None), (22, 5, None, None, 1, None),
    (22, 6, None, None, 1, None),

    # 23 Violence Prevention Counselling — YWCA — Mon–Fri 9:00–17:00
    (23, 0, "09:00", "17:00", 0, None), (23, 1, "09:00", "17:00", 0, None),
    (23, 2, "09:00", "17:00", 0, None), (23, 3, "09:00", "17:00", 0, None),
    (23, 4, "09:00", "17:00", 0, None),

    # 24 Transitional Housing — YWCA — 24/7 (staff on site)
    (24, 0, None, None, 1, "Support staff on site"), (24, 1, None, None, 1, "Support staff on site"),
    (24, 2, None, None, 1, "Support staff on site"), (24, 3, None, None, 1, "Support staff on site"),
    (24, 4, None, None, 1, "Support staff on site"), (24, 5, None, None, 1, "Support staff on site"),
    (24, 6, None, None, 1, "Support staff on site"),

    # 25 Kerby Rotary Shelter — 24/7
    (25, 0, None, None, 1, None), (25, 1, None, None, 1, None), (25, 2, None, None, 1, None),
    (25, 3, None, None, 1, None), (25, 4, None, None, 1, None), (25, 5, None, None, 1, None),
    (25, 6, None, None, 1, None),

    # 26 Elder Abuse Response — Kerby — Mon–Fri 9:00–17:00
    (26, 0, "09:00", "17:00", 0, None), (26, 1, "09:00", "17:00", 0, None),
    (26, 2, "09:00", "17:00", 0, None), (26, 3, "09:00", "17:00", 0, None),
    (26, 4, "09:00", "17:00", 0, None),

    # 27 Seniors Drop-In Programs — Kerby — Mon–Fri 8:00–17:00, Sat 9:00–15:00
    (27, 0, "08:00", "17:00", 0, None), (27, 1, "08:00", "17:00", 0, None),
    (27, 2, "08:00", "17:00", 0, None), (27, 3, "08:00", "17:00", 0, None),
    (27, 4, "08:00", "17:00", 0, None), (27, 5, "09:00", "15:00", 0, None),

    # 28 LGBTQ2S+ Peer Support — Calgary Outlink — Tue 14:00–21:00, Thu 14:00–21:00, Fri 14:00–19:00, Sat 12:00–17:00
    (28, 1, "14:00", "21:00", 0, "Drop-in"), (28, 3, "14:00", "21:00", 0, "Drop-in"),
    (28, 4, "14:00", "19:00", 0, "Drop-in"), (28, 5, "12:00", "17:00", 0, "Drop-in"),

    # 29 Information and Referrals — Outlink — Mon–Fri 10:00–17:00
    (29, 0, "10:00", "17:00", 0, None), (29, 1, "10:00", "17:00", 0, None),
    (29, 2, "10:00", "17:00", 0, None), (29, 3, "10:00", "17:00", 0, None),
    (29, 4, "10:00", "17:00", 0, None),

    # 30 Settlement and Orientation — Centre for Newcomers — Mon–Fri 8:30–17:00
    (30, 0, "08:30", "17:00", 0, None), (30, 1, "08:30", "17:00", 0, None),
    (30, 2, "08:30", "17:00", 0, None), (30, 3, "08:30", "17:00", 0, None),
    (30, 4, "08:30", "17:00", 0, None),

    # 31 Employment Services — Centre for Newcomers — Mon–Fri 8:30–17:00
    (31, 0, "08:30", "17:00", 0, None), (31, 1, "08:30", "17:00", 0, None),
    (31, 2, "08:30", "17:00", 0, None), (31, 3, "08:30", "17:00", 0, None),
    (31, 4, "08:30", "17:00", 0, None),

    # 32 Language Training (LINC) — Mon–Fri 9:00–15:00
    (32, 0, "09:00", "15:00", 0, None), (32, 1, "09:00", "15:00", 0, None),
    (32, 2, "09:00", "15:00", 0, None), (32, 3, "09:00", "15:00", 0, None),
    (32, 4, "09:00", "15:00", 0, None),

    # 33 Residential Treatment Youth — Hull Services — 24/7
    (33, 0, None, None, 1, None), (33, 1, None, None, 1, None), (33, 2, None, None, 1, None),
    (33, 3, None, None, 1, None), (33, 4, None, None, 1, None), (33, 5, None, None, 1, None),
    (33, 6, None, None, 1, None),

    # 34 Family Support Services — Hull Services — Mon–Fri 8:30–16:30
    (34, 0, "08:30", "16:30", 0, None), (34, 1, "08:30", "16:30", 0, None),
    (34, 2, "08:30", "16:30", 0, None), (34, 3, "08:30", "16:30", 0, None),
    (34, 4, "08:30", "16:30", 0, None),

    # 35 Harm Reduction Supplies — HIV Community Link — Mon–Fri 9:00–17:00, Tue/Thu 9:00–20:00
    (35, 0, "09:00", "17:00", 0, None), (35, 1, "09:00", "20:00", 0, "Extended hours"),
    (35, 2, "09:00", "17:00", 0, None), (35, 3, "09:00", "20:00", 0, "Extended hours"),
    (35, 4, "09:00", "17:00", 0, None),

    # 36 HIV Support and Navigation — Mon–Fri 9:00–17:00
    (36, 0, "09:00", "17:00", 0, None), (36, 1, "09:00", "17:00", 0, None),
    (36, 2, "09:00", "17:00", 0, None), (36, 3, "09:00", "17:00", 0, None),
    (36, 4, "09:00", "17:00", 0, None),

    # 37 Indigenous Healing Programs — Elbow River — Mon–Fri 8:30–16:30
    (37, 0, "08:30", "16:30", 0, None), (37, 1, "08:30", "16:30", 0, None),
    (37, 2, "08:30", "16:30", 0, None), (37, 3, "08:30", "16:30", 0, None),
    (37, 4, "08:30", "16:30", 0, None),

    # 38 Cultural Supports and Navigation — Mon–Fri 8:30–16:30
    (38, 0, "08:30", "16:30", 0, None), (38, 1, "08:30", "16:30", 0, None),
    (38, 2, "08:30", "16:30", 0, None), (38, 3, "08:30", "16:30", 0, None),
    (38, 4, "08:30", "16:30", 0, None),

    # 39 After-School Programs — Boys & Girls Clubs — Mon–Fri 14:30–18:30, Sat 9:00–15:00
    (39, 0, "14:30", "18:30", 0, None), (39, 1, "14:30", "18:30", 0, None),
    (39, 2, "14:30", "18:30", 0, None), (39, 3, "14:30", "18:30", 0, None),
    (39, 4, "14:30", "18:30", 0, None), (39, 5, "09:00", "15:00", 0, None),
]

# org_id → phone to add at org level (where currently missing)
ORG_PHONES_MISSING = {
    6: "403-266-1605",   # Distress Centre — main office line
}

# Org website contacts missing at org level (sync from org.website field)
# All orgs have websites stored but no `web` contact entry. We'll sync them.

def enrich():
    init_db()
    with db() as conn:
        # 1. Add missing org-level phone contacts
        for org_id, phone in ORG_PHONES_MISSING.items():
            exists = conn.execute(
                "SELECT 1 FROM contacts WHERE owner_type='org' AND owner_id=? AND kind='phone'",
                (org_id,)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO contacts(owner_type, owner_id, kind, value, is_primary) VALUES('org',?,?,?,1)",
                    (org_id, "phone", phone),
                )
                print(f"  Added phone for org {org_id}")

        # 2. Sync org.website → web contact for all orgs that have a website but no web contact
        orgs = conn.execute("SELECT id, name, website FROM organizations WHERE website IS NOT NULL").fetchall()
        for org in orgs:
            exists = conn.execute(
                "SELECT 1 FROM contacts WHERE owner_type='org' AND owner_id=? AND kind='web'",
                (org["id"],)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO contacts(owner_type, owner_id, kind, value, is_primary) VALUES('org',?,'web',?,0)",
                    (org["id"], org["website"]),
                )
                print(f"  Added web contact for org [{org['id']}] {org['name']}")

        # 3. Copy phone/web from location contacts to org where org is missing them
        locs = conn.execute(
            "SELECT id, organization_id FROM locations WHERE status='active'"
        ).fetchall()
        for loc in locs:
            for kind in ("phone", "intake_line", "crisis_line"):
                loc_contacts = conn.execute(
                    "SELECT value, is_primary FROM contacts WHERE owner_type='location' AND owner_id=? AND kind=?",
                    (loc["id"], kind)
                ).fetchall()
                for c in loc_contacts:
                    exists = conn.execute(
                        "SELECT 1 FROM contacts WHERE owner_type='org' AND owner_id=? AND kind=? AND value=?",
                        (loc["organization_id"], kind, c["value"])
                    ).fetchone()
                    if not exists:
                        conn.execute(
                            "INSERT INTO contacts(owner_type, owner_id, kind, value, is_primary) VALUES('org',?,?,?,?)",
                            (loc["organization_id"], kind, c["value"], c["is_primary"]),
                        )

        # 4. Insert hours (skip if service already has any hours)
        has_hours = {
            r[0] for r in conn.execute("SELECT DISTINCT service_id FROM hours").fetchall()
        }
        added = 0
        for svc_id, dow, opens, closes, is247, note in HOURS:
            if svc_id in has_hours:
                continue
            conn.execute(
                "INSERT INTO hours(service_id, day_of_week, opens, closes, is_24_7, note) VALUES(?,?,?,?,?,?)",
                (svc_id, dow, opens, closes, is247, note),
            )
            added += 1

        print(f"Inserted {added} hour records.")

        # Summary
        contact_count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        hour_count = conn.execute("SELECT COUNT(*) FROM hours").fetchone()[0]
        print(f"Total contacts: {contact_count}, Total hours: {hour_count}")


if __name__ == "__main__":
    enrich()
