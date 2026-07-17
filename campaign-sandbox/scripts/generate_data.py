# TechFlow sandbox demo - synthetic data generator
# First Marketing Ladies AI Meetup, 19.7.2026
# All data is SYNTHETIC. No real people, companies, or domains.
# Deterministic: fixed seed so re-runs produce the same dataset.

import csv
import math
import random
from pathlib import Path

random.seed(20260719)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TOTAL = 350

# --- registration date quotas: 7.7-18.7, spike on 11.7 (announcement), second spike 16.7 (reminder)
DAY_QUOTAS = {
    "2026-07-07": 12, "2026-07-08": 15, "2026-07-09": 14, "2026-07-10": 16,
    "2026-07-11": 78, "2026-07-12": 40, "2026-07-13": 26, "2026-07-14": 20,
    "2026-07-15": 18, "2026-07-16": 52, "2026-07-17": 34, "2026-07-18": 25,
}
assert sum(DAY_QUOTAS.values()) == TOTAL

CHANNELS = {
    "WhatsApp Community": 157,
    "LinkedIn Organic": 70,
    "Personal Outreach": 53,
    "Referral": 35,
    "Amplemarket Outbound": 35,
}
assert sum(CHANNELS.values()) == TOTAL

# day-specific channel affinity (weights for drawing from the remaining channel pool)
def channel_weights(day):
    w = {"WhatsApp Community": 1.0, "LinkedIn Organic": 0.8, "Personal Outreach": 0.8,
         "Referral": 0.6, "Amplemarket Outbound": 0.7}
    if day == "2026-07-11":          # community announcement day
        w["WhatsApp Community"] = 3.0
        w["LinkedIn Organic"] = 1.5
    elif day == "2026-07-16":        # reminder day
        w["WhatsApp Community"] = 2.2
        w["LinkedIn Organic"] = 1.3
    return w

def weighted_draw_from_pool(pool_counts, weights):
    items = [k for k, c in pool_counts.items() if c > 0]
    ws = [weights.get(k, 1.0) * pool_counts[k] for k in items]
    pick = random.choices(items, weights=ws, k=1)[0]
    pool_counts[pick] -= 1
    return pick

# --- property option labels (exactly as in the brief)
ROLE = {
    "manager": "מנהלת שיווק או ראש צוות",
    "ops": "מרקטינג אופס או רבאופס",
    "demand": "דמנד גן, קמפיינים או תוכן",
    "pmm": "פרודקט מרקטינג",
    "freelance": "עצמאית או יועצת",
}
ROLE_QUOTA = {"manager": 193, "freelance": 70, "pmm": 35, "ops": 35, "demand": 17}

BUDGET = {
    "team_and_budget": "מנהלת צוות וגם תקציב",
    "team_only": "רק צוות",
    "budget_only": "רק תקציב או חלק ממנו",
    "none": "לא, זה בשבילי",
}
BUDGET_QUOTA = {"team_and_budget": 88, "team_only": 35, "budget_only": 140, "none": 87}

FEELING = {
    "curious": "מסוקרנת אבל לא יודעת מאיפה להתחיל",
    "scratching": "משתמשת אבל מרגישה שאני מגרדת את הקצה",
    "worried": "חוששת שזה משנה את המקצוע שלי",
    "advanced": "כבר בפנים ורוצה להתקדם לרמה הבאה",
}
FEELING_QUOTA = {"scratching": 192, "advanced": 88, "curious": 52, "worried": 18}

PEEVE = {
    "vision": "הכל חזון ואין תכלס",
    "irrelevant": "מראים כלים שלא רלוונטיים לעבודה שלי",
    "too_basic": "רמה בסיסית מדי",
    "too_advanced": "רמה גבוהה מדי",
    "pitches": "פיצ'ים מכירתיים במסווה של תוכן",
}
PEEVE_QUOTA = {"vision": 192, "pitches": 105, "irrelevant": 18, "too_basic": 18, "too_advanced": 17}

AI_TOOLS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "gemini_copilot": "Gemini או Copilot",
    "ai_in_martech": "כלי AI בתוך מערכות שיווק",
    "automation": "כלים לאוטומציות (Make, Zapier, n8n)",
    "almost_none": "כמעט כלום",
    "other": "אחר",
}

AI_TOOLS_OTHER = ["Perplexity", "Midjourney", "Gamma", "Notion AI", "Lovable",
                  "HeyGen", "ElevenLabs", "Synthesia", "Fireflies"]

TIME_WASTERS = [
    "בניית scope of work לכל ספק מחדש",
    "כתיבת scope of work ותיאומים מול פרילנסרים",
    "ריפורטינג קמפיינים ידני בסוף כל חודש",
    "להרכיב דוח ביצועים מחמש מערכות שונות",
    "ריפורטינג שבועי להנהלה",
    "טיוב דאטהבייס וניקוי כפילויות בקונטקטים",
    "טיוב רשימות תפוצה ישנות",
    "תכנון תקציבים ועדכון גיליונות אקסל",
    "התאמות תקציב באמצע רבעון",
    "כתיבת תוכניות שיווק רבעוניות",
    "כתיבה מחדש של תוכנית שיווק אחרי כל שינוי בהנהלה",
    "עריכת מצגות להנהלה",
    "עיצוב מצגות במקום עבודה אסטרטגית",
    "סנכרון בין מערכות שלא מדברות אחת עם השנייה",
    "סנכרון ידני בין הסיארם למערכת הדיוור",
    "מציאת לידים רלוונטיים בלינקדאין",
    "מחקר לידים ידני לפני כל קמפיין אאוטבאונד",
    "העברת דאטה ידנית מטפסים לגיליונות",
    "בניית דוחות UTM ידניים",
    "מעקב ידני אחרי תקציב מדיה",
]

# --- names: mixed Hebrew and English Israeli names, all synthetic
# (display, translit) pairs
FIRST_NAMES = [
    ("נועה", "noa"), ("שירה", "shira"), ("מיכל", "michal"), ("טל", "tal"),
    ("רותם", "rotem"), ("דנה", "dana"), ("הילה", "hila"), ("יעל", "yael"),
    ("מאיה", "maya"), ("עדי", "adi"), ("ליאור", "lior"), ("אור", "or"),
    ("שני", "shani2"), ("גלי", "gali"), ("ענבר", "inbar"), ("מור", "mor"),
    ("קרן", "keren"), ("אפרת", "efrat"), ("סיון", "sivan"), ("נטע", "neta"),
    ("רוני", "roni"), ("עדן", "eden"), ("אלה", "ella"), ("תמר", "tamar"),
    ("אביב", "aviv"), ("חן", "chen"), ("דפנה", "dafna"), ("אורית", "orit"),
    ("מירב", "meirav"), ("איילת", "ayelet"), ("ליטל", "lital"), ("שרון", "sharon"),
    ("ניצן", "nitzan"), ("אסנת", "osnat"), ("יובל", "yuval"), ("אורנה", "orna"),
    ("Noya", "noya"), ("Shir", "shir"), ("Romi", "romi"), ("Lia", "lia"),
    ("Danielle", "danielle"), ("Michelle", "michelle"), ("Amit", "amit"),
    ("Karin", "karin"), ("Yarden", "yarden"), ("Stav", "stav"), ("Agam", "agam"),
    ("Alona", "alona"), ("Vered", "vered"), ("Tzlil", "tzlil"),
]
LAST_NAMES = [
    ("כהן", "cohen"), ("לוי", "levi"), ("מזרחי", "mizrahi"), ("פרץ", "peretz"),
    ("ביטון", "biton"), ("אברהם", "avraham"), ("פרידמן", "friedman"), ("שפירא", "shapira"),
    ("רוזן", "rozen"), ("גולן", "golan"), ("ברק", "barak"), ("שרעבי", "sharabi"),
    ("אזולאי", "azoulay"), ("חדד", "hadad"), ("עמר", "amar"), ("גבאי", "gabay"),
    ("אוחיון", "ohayon"), ("דיין", "dayan"), ("אלבז", "elbaz"), ("סגל", "segal"),
    ("ברנע", "barnea"), ("שקד", "shaked"), ("הראל", "harel"), ("אורן", "oren"),
    ("Katz", "katz"), ("Berger", "berger"), ("Adler", "adler"), ("Stern", "stern"),
    ("Landau", "landau"), ("Regev", "regev"), ("Dagan", "dagan"), ("Almog", "almog"),
    ("Sela", "sela"), ("Navon", "navon"), ("Doron", "doron"), ("Tavor", "tavor"),
]

# invented Israeli B2B companies (display, email domain) - clearly fake demo domains
COMPANIES = [
    ("DataSprout", "datasprout-demo.com"), ("CloudNagar", "cloudnagar-demo.com"),
    ("PixelPeak", "pixelpeak-demo.com"), ("FlowTeva", "flowteva-demo.com"),
    ("LeadGolan", "leadgolan-demo.com"), ("SyncSabra", "syncsabra-demo.com"),
    ("BitCarmel", "bitcarmel-demo.com"), ("NextArava", "nextarava-demo.com"),
    ("SignalNegev", "signalnegev-demo.com"), ("StackGalil", "stackgalil-demo.com"),
    ("PipeDekel", "pipedekel-demo.com"), ("GrowthAlon", "growthalon-demo.com"),
    ("CyberTamar", "cybertamar-demo.com"), ("QuantaHof", "quantahof-demo.com"),
    ("VerticaLev", "verticalev-demo.com"), ("OpsHarel", "opsharel-demo.com"),
    ("BrightRimon", "brightrimon-demo.com"), ("NimbusYam", "nimbusyam-demo.com"),
    ("ScaleZafon", "scalezafon-demo.com"), ("TrackShaked", "trackshaked-demo.com"),
    ("FunnelDor", "funneldor-demo.com"), ("MetricsGefen", "metricsgefen-demo.com"),
    ("RouteMoran", "routemoran-demo.com"), ("StreamKineret", "streamkineret-demo.com"),
    ("CoreEshkol", "coreeshkol-demo.com"), ("LogicBarak", "logicbarak-demo.com"),
    ("VectorNir", "vectornir-demo.com"), ("AtlasSharon", "atlassharon-demo.com"),
    ("PulseYarden", "pulseyarden-demo.com"), ("OrbitSaar", "orbitsaar-demo.com"),
    ("FusionErez", "fusionerez-demo.com"), ("DeltaHermon", "deltahermon-demo.com"),
    ("PrismTavor", "prismtavor-demo.com"), ("EchoMasada", "echomasada-demo.com"),
    ("NovaArbel", "novaarbel-demo.com"), ("ZenithGilboa", "zenithgilboa-demo.com"),
    ("HyperNahal", "hypernahal-demo.com"), ("SmartWadi", "smartwadi-demo.com"),
    ("RapidTsuk", "rapidtsuk-demo.com"), ("SolidEilat", "solideilat-demo.com"),
]

def build_pool(quota):
    pool = dict(quota)
    return pool

def draw(pool, weights=None):
    items = [k for k, c in pool.items() if c > 0]
    if weights:
        ws = [weights.get(k, 1.0) * pool[k] for k in items]
    else:
        ws = [pool[k] for k in items]
    pick = random.choices(items, weights=ws, k=1)[0]
    pool[pick] -= 1
    return pick

def main():
    # 1) assign dates and channels
    contacts = []
    channel_pool = dict(CHANNELS)
    for day, n in DAY_QUOTAS.items():
        for _ in range(n):
            ch = weighted_draw_from_pool(channel_pool, channel_weights(day))
            contacts.append({"registration_date": day, "lead_source_channel": ch})
    random.shuffle(contacts)

    # 2) roles and budget with Amplemarket seniority skew, exact overall quotas
    role_pool = build_pool(ROLE_QUOTA)
    budget_pool = build_pool(BUDGET_QUOTA)
    feeling_pool = build_pool(FEELING_QUOTA)
    peeve_pool = build_pool(PEEVE_QUOTA)
    # process Amplemarket contacts first so the skew weights have full pools to draw from
    contacts.sort(key=lambda c: 0 if c["lead_source_channel"] == "Amplemarket Outbound" else 1)
    for c in contacts:
        outbound = c["lead_source_channel"] == "Amplemarket Outbound"
        role_w = {"manager": 3.0, "ops": 2.0, "freelance": 0.2} if outbound else None
        budget_w = {"team_and_budget": 3.0, "budget_only": 1.2, "none": 0.2} if outbound else None
        c["ml_role_type"] = draw(role_pool, role_w)
        # freelancers manage no team; force budget accordingly
        if c["ml_role_type"] == "freelance":
            fw = {"none": 3.0, "budget_only": 1.0, "team_and_budget": 0.0, "team_only": 0.0}
            c["ml_team_budget"] = draw(budget_pool, fw)
        else:
            c["ml_team_budget"] = draw(budget_pool, budget_w)
        c["ml_ai_feeling"] = draw(feeling_pool)
        c["ml_meetup_pet_peeve"] = draw(peeve_pool)
    random.shuffle(contacts)

    # 3) ai tools
    none_idx = set(random.sample(range(TOTAL), 35))  # 10 percent almost nothing
    for i, c in enumerate(contacts):
        if i in none_idx:
            tools = ["almost_none"]
            c["ml_ai_tools_other"] = ""
        else:
            tools = ["chatgpt"]
            if random.random() < 0.55:
                tools.append("claude")
            if random.random() < 0.37:
                tools.append("gemini_copilot")
            if random.random() < 0.25:
                tools.append("ai_in_martech")
            if random.random() < 0.165:
                tools.append("automation")
            if random.random() < 0.08:
                tools.append("other")
                c["ml_ai_tools_other"] = random.choice(AI_TOOLS_OTHER)
            else:
                c["ml_ai_tools_other"] = ""
        c["ml_ai_tools"] = tools
        c["ml_time_waster"] = random.choice(TIME_WASTERS)
        c["ml_desired_outcome"] = random.choice(DESIRED_OUTCOMES)

    # 4) identities
    used_emails = set()
    for c in contacts:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        if c["ml_role_type"] == "freelance":
            company = f"{first[1].capitalize()} Marketing"
            domain = f"{first[1]}-marketing-demo.com"
        else:
            company, domain = random.choice(COMPANIES)
        email = f"{first[1]}.{last[1]}@{domain}"
        n = 2
        while email in used_emails:
            email = f"{first[1]}.{last[1]}{n}@{domain}"
            n += 1
        used_emails.add(email)
        c["firstname"] = first[0]
        c["lastname"] = last[0]
        c["company"] = company
        c["email"] = email

    # 5) contacts_export.csv (labels, human readable - the file Shachar joins against)
    out = DATA_DIR / "contacts_export.csv"
    cols = ["email", "firstname", "lastname", "company", "ml_role_type", "ml_team_budget",
            "ml_ai_tools", "ml_ai_tools_other", "ml_ai_feeling", "ml_time_waster",
            "ml_meetup_pet_peeve", "ml_desired_outcome", "lead_source_channel",
            "registration_date"]
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in contacts:
            row = dict(c)
            row["ml_role_type"] = ROLE[c["ml_role_type"]]
            row["ml_team_budget"] = BUDGET[c["ml_team_budget"]]
            row["ml_ai_feeling"] = FEELING[c["ml_ai_feeling"]]
            row["ml_meetup_pet_peeve"] = PEEVE[c["ml_meetup_pet_peeve"]]
            row["ml_ai_tools"] = ";".join(AI_TOOLS[t] for t in c["ml_ai_tools"])
            w.writerow({k: row[k] for k in cols})

    # 6) internal-values CSV for the HubSpot upload script
    out2 = DATA_DIR / "contacts_internal.csv"
    with out2.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in contacts:
            row = dict(c)
            row["ml_ai_tools"] = ";".join(c["ml_ai_tools"])
            w.writerow({k: row[k] for k in cols})

    # 7) campaign_touchpoints.csv - aggregated from the contacts, so it always reconciles
    agg = {}
    for c in contacts:
        agg.setdefault((c["registration_date"], c["lead_source_channel"]), 0)
        agg[(c["registration_date"], c["lead_source_channel"])] += 1
    tp = DATA_DIR / "campaign_touchpoints.csv"
    with tp.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["date", "channel", "sends_or_posts", "clicks", "landing_page_views", "registrations"])
        for day in DAY_QUOTAS:
            for ch in CHANNELS:
                reg = agg.get((day, ch), 0)
                if reg == 0:
                    continue
                conv = random.uniform(0.35, 0.45)
                views = max(reg, math.ceil(reg / conv))
                clicks = math.ceil(views / random.uniform(0.82, 0.92))
                if ch == "WhatsApp Community":
                    sends = 5 if day in ("2026-07-11", "2026-07-16") else random.randint(1, 3)
                elif ch == "LinkedIn Organic":
                    sends = 1 if day in ("2026-07-11", "2026-07-16") or random.random() < 0.4 else 0
                elif ch == "Personal Outreach":
                    sends = clicks + random.randint(8, 25)
                elif ch == "Referral":
                    sends = 0
                else:  # Amplemarket Outbound
                    sends = clicks * random.randint(8, 14) + random.randint(10, 40)
                w.writerow([day, ch, sends, clicks, views, reg])

    # 8) costs.csv
    costs = DATA_DIR / "costs.csv"
    with costs.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["channel", "cost_type", "amount_usd", "period", "notes"])
        w.writerow(["WhatsApp Community", "organic", 0, "2026-07", "community management time only"])
        w.writerow(["LinkedIn Organic", "organic", 0, "2026-07", "founder-led posts"])
        w.writerow(["Personal Outreach", "organic", 0, "2026-07", "manual DMs and emails"])
        w.writerow(["Referral", "organic", 0, "2026-07", "word of mouth"])
        w.writerow(["Amplemarket Outbound", "seat_license", 600, "2026-07", "fixed monthly seat cost"])
        w.writerow(["LinkedIn Organic", "paid_boost", 120, "2026-07", "small boost on announcement post"])

    # sanity report
    from collections import Counter
    print("contacts:", len(contacts))
    print("channels:", Counter(c["lead_source_channel"] for c in contacts))
    print("roles:", Counter(c["ml_role_type"] for c in contacts))
    print("budget:", Counter(c["ml_team_budget"] for c in contacts))
    print("feeling:", Counter(c["ml_ai_feeling"] for c in contacts))
    print("peeve:", Counter(c["ml_meetup_pet_peeve"] for c in contacts))
    tools_counter = Counter(t for c in contacts for t in c["ml_ai_tools"])
    print("tools:", tools_counter)
    amp = [c for c in contacts if c["lead_source_channel"] == "Amplemarket Outbound"]
    print("amplemarket managers:", sum(1 for c in amp if c["ml_role_type"] in ("manager", "ops")), "/", len(amp))
    print("dates:", dict(sorted(Counter(c["registration_date"] for c in contacts).items())))
    print("unique emails:", len(used_emails))

DESIRED_OUTCOMES = [
    "לצאת עם שלושה דברים שאני מיישמת כבר השבוע",
    "וורקפלואו אחד מלא שאפשר להעתיק",
    "להבין איך לחבר את הכלים שכבר יש לי",
    "לראות איך צוות קטן עובד עם AI בלי תקציב ענק",
    "רעיונות לאוטומציה של הריפורטינג",
    "להכיר נשים שמתמודדות עם אותם אתגרים",
    "להבין מה הצעד הבא אחרי הפרומפטים הבסיסיים",
    "דוגמאות אמיתיות מקמפיינים ולא סלייד של חזון",
    "איך למכור את זה פנימה להנהלה",
    "לבנות תהליך עבודה עם קלוד לכתיבת תוכן",
    "להפסיק לפחד מהצד הטכני של אינטגרציות",
    "בנצ'מרקים של מה עובד לצוותים בגודל שלי",
]

if __name__ == "__main__":
    main()
