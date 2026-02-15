#!/usr/bin/env python3
"""
HubSpot MarTech Outreach Campaign - Feb 2026
=============================================
One-command setup:
  export HUBSPOT_API_KEY="pat-eu1-xxxx..."
  python3 hubspot_campaign.py

Creates:
  1. Active Contact List  (lead_intent=martech_audit, hs_lead_status=new)
  2. Email Template 1     (Initial Outreach)
  3. Email Template 2     (Follow Up - 2 days later)
  4. Sequence             (7 steps: emails, delays, tasks)
  5. Enrolls contacts from the list into the sequence

Portal ID: 147145202
Requirements: pip install requests
"""

import requests
import json
import sys
import time
import textwrap
import os

# ─── CONFIGURATION ──────────────────────────────────────────
API_KEY = os.environ.get("HUBSPOT_API_KEY", "")
if not API_KEY:
    print("❌ Set HUBSPOT_API_KEY environment variable first:")
    print('   export HUBSPOT_API_KEY="pat-eu1-xxxx..."')
    sys.exit(1)

PORTAL_ID = "147145202"
BASE_URL = "https://api.hubapi.com"
HUBSPOT_UI = "https://app-eu1.hubspot.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Track created resources for final summary
RESULTS = {
    "list_id": None,
    "template_1_id": None,
    "template_2_id": None,
    "sequence_id": None,
}


# ─── API HELPER ─────────────────────────────────────────────
def api(method, path, payload=None, label=""):
    """Make HubSpot API call with retry on network / rate-limit errors."""
    url = f"{BASE_URL}{path}"
    print(f"\n{'─'*56}")
    print(f"  {label}")
    print(f"  {method} {path}")
    print(f"{'─'*56}")

    for attempt in range(4):
        try:
            r = getattr(requests, method.lower())(
                url, headers=HEADERS, json=payload, timeout=30
            )
            print(f"  ← {r.status_code}")

            if r.status_code in (200, 201, 202, 204):
                data = r.json() if r.text.strip() else {}
                print("  ✅ OK")
                return data

            # Rate-limited → back off
            if r.status_code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  ⏳ Rate-limited. Retrying in {wait}s …")
                time.sleep(wait)
                continue

            # Other error → report and return None
            try:
                err = json.dumps(r.json(), ensure_ascii=False, indent=2)
            except Exception:
                err = r.text[:400]
            print(f"  ❌ {err}")
            return None

        except requests.RequestException as exc:
            wait = 2 ** (attempt + 1)
            print(f"  ⚠ Network error (attempt {attempt+1}/4): {exc}")
            if attempt < 3:
                print(f"  Retrying in {wait}s …")
                time.sleep(wait)

    print("  ❌ Max retries exceeded")
    return None


# ─── STEP 1 — ACTIVE CONTACT LIST ──────────────────────────
def create_list():
    print("\n" + "█"*56)
    print("  STEP 1 · Active Contact List")
    print("█"*56)

    # Try v1 Lists API first
    payload = {
        "name": "MarTech Outreach - Feb 2026",
        "dynamic": True,
        "filters": [[
            {"operator": "EQ", "property": "lead_intent",
             "value": "martech_audit", "type": "string"},
            {"operator": "EQ", "property": "hs_lead_status",
             "value": "new", "type": "string"},
        ]],
    }
    data = api("POST", "/contacts/v1/lists", payload,
               "Creating Active List (v1)")

    if data and data.get("listId"):
        lid = data["listId"]
        RESULTS["list_id"] = lid
        print(f"\n  🆔 List ID : {lid}")
        print(f"  🔗 {HUBSPOT_UI}/contacts/{PORTAL_ID}/lists/{lid}")
        return lid

    # Fallback — v3 ILS API
    payload_v3 = {
        "objectTypeId": "0-1",
        "processingType": "DYNAMIC",
        "name": "MarTech Outreach - Feb 2026",
        "filterBranch": {
            "filterBranchType": "AND",
            "filterBranches": [],
            "filters": [
                {"propertyName": "lead_intent", "operator": "IS_EQUAL_TO",
                 "value": "martech_audit", "filterType": "PROPERTY",
                 "type": "string"},
                {"propertyName": "hs_lead_status", "operator": "IS_EQUAL_TO",
                 "value": "new", "filterType": "PROPERTY",
                 "type": "string"},
            ],
        },
    }
    data = api("POST", "/crm/v3/lists", payload_v3,
               "Creating Active List (v3 fallback)")

    if data:
        lid = data.get("listId") or data.get("id")
        RESULTS["list_id"] = lid
        print(f"\n  🆔 List ID : {lid}")
        print(f"  🔗 {HUBSPOT_UI}/contacts/{PORTAL_ID}/lists/{lid}")
        return lid

    print("\n  ❌ List creation failed — see manual guide at the end")
    return None


# ─── STEP 2 — EMAIL TEMPLATES ──────────────────────────────

INITIAL_BODY = textwrap.dedent("""\
<div dir="rtl" style="text-align:right;font-family:Arial,sans-serif;line-height:1.8">
<p>היי {{contact.firstname}},</p>

<p>כן, זה outreach. ואת/ה בדיוק הפרופיל שאני מחפשת - {{contact.jobtitle}} ב-{{contact.company}}, כנראה עם stack של איזה 15 כלים שרק חלקם באמת מדברים אחד עם השני.</p>

<p>אני שני, ואני עושה משהו שנשמע פשוט אבל אף אחד לא באמת עושה - יושבת עם Marketing Leaders ובחצי שעה ממפה איפה הכסף הולך, מה מייצר pipeline ומה סתם יושב שם כי &quot;תמיד היה&quot;.</p>

<p>יש לי תהליך שאני בדרך כלל גובה עליו כסף, אבל בשבילך אני מציעה לעשות את זה בשיחה של 30 דקות - ואת/ה יוצא/ת עם:</p>
<ul style="text-align:right">
  <li>מפה ברורה של מה עובד ומה redundant</li>
  <li>לפחות 2-3 quick wins שאפשר ליישם מחר</li>
  <li>הבנה האם יש פה ROI leak שדורש טיפול</li>
</ul>

<p>אני יודעת שהתיבה שלך מלאה בהודעות &quot;let&#39;s connect&quot; ו-&quot;quick chat&quot;. זאת לא אחת מהן.</p>

<p>מה אומר/ת?</p>

<p>שני</p>
</div>""")

FOLLOWUP_BODY = textwrap.dedent("""\
<div dir="rtl" style="text-align:right;font-family:Arial,sans-serif;line-height:1.8">
<p>היי {{contact.firstname}},</p>

<p>רק בודקת שלא נקברתי בין &quot;just circling back&quot; ו-&quot;per my last email&quot;.</p>

<p>30 דקות. מפה ברורה של ה-stack. Quick wins שאפשר ליישם מיד.</p>

<p>שני</p>
</div>""")


def create_template(name, subject, body):
    """Create a HubSpot sales email template."""

    # Primary — CRM Sales Templates endpoint
    payload = {
        "properties": {
            "hs_name": name,
            "hs_subject": subject,
            "hs_body": body,
        }
    }
    data = api("POST", "/crm/v3/objects/2-5022389", payload,
               f"Creating template '{name}' (CRM Sales)")

    if data and data.get("id"):
        return data["id"]

    # Fallback — legacy templates endpoint
    payload2 = {"name": name, "subject": subject, "body": body}
    data = api("POST", "/email/public/v1/templates", payload2,
               f"Creating template '{name}' (legacy fallback)")

    if data and (data.get("id") or data.get("templateId")):
        return data.get("id") or data.get("templateId")

    return None


def create_templates():
    print("\n" + "█"*56)
    print("  STEP 2 · Email Templates")
    print("█"*56)

    t1 = create_template(
        "MarTech Outreach - Initial",
        "{{contact.firstname}}, שאלה מהירה על ה-stack שלכם",
        INITIAL_BODY,
    )
    if t1:
        RESULTS["template_1_id"] = t1
        print(f"\n  🆔 Template 1 ID : {t1}")

    t2 = create_template(
        "MarTech Outreach - Follow Up",
        "re: {{contact.firstname}}, שאלה מהירה",
        FOLLOWUP_BODY,
    )
    if t2:
        RESULTS["template_2_id"] = t2
        print(f"\n  🆔 Template 2 ID : {t2}")

    return t1, t2


# ─── STEP 3 — SEQUENCE ─────────────────────────────────────
def create_sequence(t1_id, t2_id):
    print("\n" + "█"*56)
    print("  STEP 3 · Sequence")
    print("█"*56)

    DAY_MS = 24 * 60 * 60 * 1000

    steps = [
        # Step 1: Email — Initial
        {"type": "EMAIL", "delay": 0,
         **({"templateId": t1_id} if t1_id else {})},
        # Step 2+3: Delay 2 business days → Email — Follow Up
        {"type": "EMAIL", "delay": 2 * DAY_MS,
         **({"templateId": t2_id} if t2_id else {})},
        # Step 4+5: Delay 2 business days → Task
        {"type": "TASK", "delay": 2 * DAY_MS,
         "taskBody": "בדקי LinkedIn - אין תגובה למיילים"},
        # Step 6+7: Delay 3 business days → Task
        {"type": "TASK", "delay": 3 * DAY_MS,
         "taskBody": "שלחי LinkedIn InMail או תעברי הלאה"},
    ]

    payload = {"name": "MarTech Outreach Sequence - Feb 2026", "steps": steps}

    # Try v4
    data = api("POST", "/automation/v4/sequences", payload,
               "Creating Sequence (v4)")
    if data:
        sid = data.get("id") or data.get("sequenceId")
        if sid:
            RESULTS["sequence_id"] = sid
            print(f"\n  🆔 Sequence ID : {sid}")
            print(f"  🔗 {HUBSPOT_UI}/sequences/{PORTAL_ID}/{sid}")
            return sid

    # Try v3 fallback
    data = api("POST", "/automation/v3/sequences", payload,
               "Creating Sequence (v3 fallback)")
    if data:
        sid = data.get("id") or data.get("sequenceId")
        if sid:
            RESULTS["sequence_id"] = sid
            print(f"\n  🆔 Sequence ID : {sid}")
            print(f"  🔗 {HUBSPOT_UI}/sequences/{PORTAL_ID}/{sid}")
            return sid

    print("\n  ❌ Sequence creation failed")
    print("  ℹ  Sequences API requires Sales Hub Professional or Enterprise")
    return None


# ─── STEP 5 — ENROLL CONTACTS ──────────────────────────────
def enroll_contacts(seq_id, list_id):
    print("\n" + "█"*56)
    print("  STEP 5 · Enroll Contacts")
    print("█"*56)

    if not seq_id or not list_id:
        print("  ⚠  Cannot auto-enroll (missing sequence or list ID)")
        print("  → Enroll manually — see instructions below")
        return

    # Fetch contact IDs from list
    data = api("GET", f"/contacts/v1/lists/{list_id}/contacts/all?count=200",
               label=f"Fetching contacts from list {list_id}")

    contacts = []
    if data and "contacts" in data:
        contacts = [c["vid"] for c in data["contacts"]]

    if not contacts:
        # v3 fallback
        data = api("GET", f"/crm/v3/lists/{list_id}/memberships",
                   label=f"Fetching contacts (v3)")
        if data and "results" in data:
            contacts = [r.get("id") for r in data["results"]]

    if not contacts:
        print("  ⚠  No contacts found or unable to fetch. Enroll manually.")
        return

    print(f"  Found {len(contacts)} contacts")

    enrolled = 0
    for cid in contacts:
        d = api("POST", f"/automation/v4/sequences/{seq_id}/enrollments",
                {"contactId": cid},
                f"Enrolling contact {cid}")
        if d is not None:
            enrolled += 1

    print(f"\n  ✅ Enrolled {enrolled}/{len(contacts)} contacts")


# ─── LINKEDIN TEMPLATE (printed for copy-paste) ────────────
LINKEDIN_MSG = """\
היי [FIRSTNAME],

אני אפילו לא אעמיד פנים - את/ה בדיוק ה-ICP שלי. [JOBTITLE], [COMPANY], \
כנראה יושב/ת על MarTech stack שעולה יותר ממה שהוא מחזיר.

אני עושה משהו שנשמע פשוט - יושבת עם אנשי שיווק ובחצי שעה ממפה \
איפה יש tool overlap, מה מייצר pipeline ומה סתם שורף budget.

בדרך כלל זה תהליך בתשלום. בשבילך - 30 דקות שיחה, \
ואת/ה יוצא/ת עם quick wins שאפשר ליישם מחר.

מה אומר/ת?"""


# ─── MANUAL GUIDE ───────────────────────────────────────────
def print_manual_guide():
    print(textwrap.dedent("""
    ╔══════════════════════════════════════════════════════╗
    ║           MANUAL SETUP GUIDE (if needed)            ║
    ╚══════════════════════════════════════════════════════╝

    1. ACTIVE LIST
       Contacts → Lists → Create list (Active)
       Name   : "MarTech Outreach - Feb 2026"
       Filter : lead_intent  = martech_audit
       AND    : hs_lead_status = new

    2. EMAIL TEMPLATES
       Conversations → Templates → New template
       ① "MarTech Outreach - Initial"
       ② "MarTech Outreach - Follow Up"
       (copy subject + body from the script source)

    3. SEQUENCE  (requires Sales Hub Professional)
       Automation → Sequences → Create sequence
       Name: "MarTech Outreach Sequence - Feb 2026"
       Step 1: Email  → "MarTech Outreach - Initial"
       Step 2: Delay  → 2 business days
       Step 3: Email  → "MarTech Outreach - Follow Up"
       Step 4: Delay  → 2 business days
       Step 5: Task   → "בדקי LinkedIn - אין תגובה למיילים"
       Step 6: Delay  → 3 business days
       Step 7: Task   → "שלחי LinkedIn InMail או תעברי הלאה"

    4. ENROLL CONTACTS
       Open the sequence → Enroll contacts
       Select list "MarTech Outreach - Feb 2026" → Activate
    """))


# ─── MAIN ───────────────────────────────────────────────────
def main():
    print("=" * 56)
    print("  🚀 HubSpot MarTech Outreach Campaign")
    print(f"  Portal {PORTAL_ID}  ·  Feb 2026")
    print("=" * 56)

    # Verify connectivity
    me = api("GET", "/integrations/v1/me", label="Verifying API key")
    if me:
        portal = me.get("portalId", "?")
        print(f"  Connected to portal {portal}")
    else:
        print("  ⚠  Could not verify API key — continuing anyway …")

    # Step 1
    list_id = create_list()

    # Step 2
    t1, t2 = create_templates()

    # Step 3
    seq_id = create_sequence(t1, t2)

    # Step 4 — LinkedIn template (just print)
    print("\n" + "█" * 56)
    print("  STEP 4 · LinkedIn Template (copy-paste)")
    print("█" * 56)
    print()
    print(LINKEDIN_MSG)

    # Step 5
    enroll_contacts(seq_id, list_id)

    # ─── SUMMARY ────────────────────────────────────────────
    print("\n" + "=" * 56)
    print("  📊  CAMPAIGN SUMMARY")
    print("=" * 56)

    ok = "✅"
    no = "❌ (manual)"

    lid = RESULTS["list_id"]
    print(f"  List         : {ok+' '+str(lid) if lid else no}")
    if lid:
        print(f"               : {HUBSPOT_UI}/contacts/{PORTAL_ID}/lists/{lid}")

    t1id = RESULTS["template_1_id"]
    print(f"  Template 1   : {ok+' '+str(t1id) if t1id else no}")

    t2id = RESULTS["template_2_id"]
    print(f"  Template 2   : {ok+' '+str(t2id) if t2id else no}")

    sid = RESULTS["sequence_id"]
    print(f"  Sequence     : {ok+' '+str(sid) if sid else no}")
    if sid:
        print(f"               : {HUBSPOT_UI}/sequences/{PORTAL_ID}/{sid}")

    print(f"  Portal       : {PORTAL_ID}")
    print("=" * 56)

    if not all(RESULTS.values()):
        print_manual_guide()
        return 1

    print("\n  🎉 Campaign is ready! Go to the sequence and hit Enroll.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
