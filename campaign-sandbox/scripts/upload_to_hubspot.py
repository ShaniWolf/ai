# TechFlow sandbox demo - HubSpot uploader
# Creates the first_marketing_ladies property group, 10 contact properties,
# and 350 synthetic contacts (batches of 100) in the SANDBOX portal only.
#
# SAFETY: hard stop if the token belongs to production portal 147145202.
# Expected sandbox portal: 148918840 (override with EXPECTED_PORTAL_ID env var).
#
# Usage:
#   export HUBSPOT_SANDBOX_PAT=pat-eu1-...
#   python3 upload_to_hubspot.py

import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

PRODUCTION_PORTAL = 147145202
EXPECTED_PORTAL = int(os.environ.get("EXPECTED_PORTAL_ID", "148918840"))
BASE = "https://api.hubapi.com"
DATA = Path(__file__).resolve().parent.parent / "data" / "contacts_internal.csv"

TOKEN = os.environ.get("HUBSPOT_SANDBOX_PAT", "").strip()
if not TOKEN:
    sys.exit("HUBSPOT_SANDBOX_PAT is not set. Aborting.")


def api(method, path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def safety_check():
    status, info = api("GET", "/account-info/v3/details")
    if status != 200:
        sys.exit(f"Could not verify portal identity (HTTP {status}): {info}. Aborting.")
    portal = info.get("portalId")
    print(f"Token belongs to portal {portal} ({info.get('accountType')}, {info.get('dataHostingLocation', 'n/a')})")
    if portal == PRODUCTION_PORTAL:
        sys.exit("HARD STOP: token points to PRODUCTION portal 147145202. Nothing was written.")
    if portal != EXPECTED_PORTAL:
        sys.exit(f"HARD STOP: portal {portal} does not match expected sandbox {EXPECTED_PORTAL}. Nothing was written.")
    return portal


GROUP = "first_marketing_ladies"

ENUM = "enumeration"
PROPS = [
    {"name": "ml_role_type", "label": "ML Role Type", "type": ENUM, "fieldType": "select",
     "options": [("manager", "מנהלת שיווק או ראש צוות"), ("ops", "מרקטינג אופס או רבאופס"),
                 ("demand", "דמנד גן, קמפיינים או תוכן"), ("pmm", "פרודקט מרקטינג"),
                 ("freelance", "עצמאית או יועצת")]},
    {"name": "ml_team_budget", "label": "ML Team and Budget", "type": ENUM, "fieldType": "select",
     "options": [("team_and_budget", "מנהלת צוות וגם תקציב"), ("team_only", "רק צוות"),
                 ("budget_only", "רק תקציב או חלק ממנו"), ("none", "לא, זה בשבילי")]},
    {"name": "ml_ai_tools", "label": "ML AI Tools", "type": ENUM, "fieldType": "checkbox",
     "options": [("chatgpt", "ChatGPT"), ("claude", "Claude"), ("gemini_copilot", "Gemini או Copilot"),
                 ("ai_in_martech", "כלי AI בתוך מערכות שיווק"),
                 ("automation", "כלים לאוטומציות (Make, Zapier, n8n)"),
                 ("almost_none", "כמעט כלום"), ("other", "אחר")]},
    {"name": "ml_ai_tools_other", "label": "ML AI Tools Other", "type": "string", "fieldType": "text"},
    {"name": "ml_ai_feeling", "label": "ML AI Feeling", "type": ENUM, "fieldType": "radio",
     "options": [("curious", "מסוקרנת אבל לא יודעת מאיפה להתחיל"),
                 ("scratching", "משתמשת אבל מרגישה שאני מגרדת את הקצה"),
                 ("worried", "חוששת שזה משנה את המקצוע שלי"),
                 ("advanced", "כבר בפנים ורוצה להתקדם לרמה הבאה")]},
    {"name": "ml_time_waster", "label": "ML Time Waster", "type": "string", "fieldType": "textarea"},
    {"name": "ml_meetup_pet_peeve", "label": "ML Meetup Pet Peeve", "type": ENUM, "fieldType": "radio",
     "options": [("vision", "הכל חזון ואין תכלס"), ("irrelevant", "מראים כלים שלא רלוונטיים לעבודה שלי"),
                 ("too_basic", "רמה בסיסית מדי"), ("too_advanced", "רמה גבוהה מדי"),
                 ("pitches", "פיצ'ים מכירתיים במסווה של תוכן")]},
    {"name": "ml_desired_outcome", "label": "ML Desired Outcome", "type": "string", "fieldType": "textarea"},
    {"name": "lead_source_channel", "label": "Lead Source Channel", "type": ENUM, "fieldType": "select",
     "options": [("WhatsApp Community", "WhatsApp Community"), ("LinkedIn Organic", "LinkedIn Organic"),
                 ("Personal Outreach", "Personal Outreach"), ("Referral", "Referral"),
                 ("Amplemarket Outbound", "Amplemarket Outbound")]},
    {"name": "registration_date", "label": "Registration Date", "type": "date", "fieldType": "date"},
]


def create_group():
    status, body = api("POST", "/crm/v3/properties/contacts/groups",
                       {"name": GROUP, "label": "First Marketing Ladies"})
    if status in (200, 201):
        print(f"Created property group {GROUP}")
    elif status == 409:
        print(f"Property group {GROUP} already exists")
    else:
        sys.exit(f"Failed to create group (HTTP {status}): {body}")


def create_properties():
    created = 0
    for p in PROPS:
        payload = {"name": p["name"], "label": p["label"], "groupName": GROUP,
                   "type": p["type"], "fieldType": p["fieldType"]}
        if "options" in p:
            payload["options"] = [
                {"value": v, "label": l, "displayOrder": i, "hidden": False}
                for i, (v, l) in enumerate(p["options"])
            ]
        status, body = api("POST", "/crm/v3/properties/contacts", payload)
        if status in (200, 201):
            created += 1
            print(f"  created property {p['name']}")
        elif status == 409:
            print(f"  property {p['name']} already exists")
        else:
            sys.exit(f"Failed on property {p['name']} (HTTP {status}): {body}")
    return created


def load_contacts():
    with DATA.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def create_contacts(rows):
    total = 0
    for i in range(0, len(rows), 100):
        batch = rows[i:i + 100]
        inputs = []
        for r in batch:
            props = {
                "email": r["email"], "firstname": r["firstname"], "lastname": r["lastname"],
                "company": r["company"], "ml_role_type": r["ml_role_type"],
                "ml_team_budget": r["ml_team_budget"], "ml_ai_tools": r["ml_ai_tools"],
                "ml_ai_feeling": r["ml_ai_feeling"], "ml_time_waster": r["ml_time_waster"],
                "ml_meetup_pet_peeve": r["ml_meetup_pet_peeve"],
                "ml_desired_outcome": r["ml_desired_outcome"],
                "lead_source_channel": r["lead_source_channel"],
                "registration_date": r["registration_date"],
            }
            if r["ml_ai_tools_other"]:
                props["ml_ai_tools_other"] = r["ml_ai_tools_other"]
            inputs.append({"properties": props})
        status, body = api("POST", "/crm/v3/objects/contacts/batch/create", {"inputs": inputs})
        if status not in (200, 201):
            sys.exit(f"Batch {i // 100 + 1} failed (HTTP {status}): {json.dumps(body)[:2000]}")
        total += len(body.get("results", []))
        print(f"  batch {i // 100 + 1}: created {len(body.get('results', []))} contacts")
        time.sleep(0.5)
    return total


def main():
    portal = safety_check()
    create_group()
    n_props = create_properties()
    rows = load_contacts()
    n_contacts = create_contacts(rows)
    print("---")
    print(f"Portal: {portal}")
    print(f"Properties created this run: {n_props} (of {len(PROPS)} defined)")
    print(f"Contacts created this run: {n_contacts} (of {len(rows)} in file)")


if __name__ == "__main__":
    main()
