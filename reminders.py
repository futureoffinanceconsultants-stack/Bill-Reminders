import json, os, calendar, urllib.request
from datetime import datetime, date
from zoneinfo import ZoneInfo

today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
cfg = json.load(open("bills.json"))
lead = cfg["remind_days_before"]

def next_due(day):
    y, m = today.year, today.month
    for _ in range(2):
        d = date(y, m, min(day, calendar.monthrange(y, m)[1]))
        if d >= today:
            return d
        m += 1
        if m > 12:
            m, y = 1, y + 1

lines = []
for b in cfg["bills"]:
    n = (next_due(b["day_of_month"]) - today).days
    if n in lead:
        when = "today" if n == 0 else f"in {n} day{'s' if n > 1 else ''}"
        lines.append(f"{b['name']} (${b['amount']}) due {when}")

manual = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
if not lines and manual:
    lines = ["Test: reminders are working. No bills due right now."]

if lines:
    req = urllib.request.Request(
        "https://ntfy.sh/" + os.environ["NTFY_TOPIC"],
        data="\n".join(lines).encode(),
        headers={"Title": "Bills due", "Priority": "high"},
    )
    urllib.request.urlopen(req)
    print("Sent:", lines)
else:
    print("Nothing due today.")
