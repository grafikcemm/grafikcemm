"""Fetch the public contribution calendar (no token) into data/contributions.json.

Standard library only, so the daily workflow needs nothing but Python.
Usage: python scripts/fetch_contributions.py [username]
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser

USER = sys.argv[1] if len(sys.argv) > 1 else "grafikcemm"


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}      # id -> (date, level)
        self.tips = {}       # id -> text
        self._tip_for = None
        self._tip_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and a.get("data-date") and "data-level" in a:
            self.cells[a.get("id", a["data-date"])] = (a["data-date"], int(a["data-level"]))
        elif tag == "tool-tip" and a.get("for"):
            self._tip_for = a["for"]
            self._tip_text = []

    def handle_data(self, data):
        if self._tip_for:
            self._tip_text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self._tip_for:
            self.tips[self._tip_for] = "".join(self._tip_text).strip()
            self._tip_for = None


def count_from_tip(text):
    if not text or text.lower().startswith("no contribution"):
        return 0
    match = re.match(r"([\d,]+)\s+contribution", text)
    return int(match.group(1).replace(",", "")) if match else 0


def streaks(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for day in reversed(days):
        if day["count"] > 0:
            current += 1
        elif current == 0 and day["date"] == date.today().isoformat():
            continue  # today may simply not have happened yet
        else:
            break
    return current, longest


def main():
    request = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "grafikcemm-profile-art"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8")
    parser = Calendar()
    parser.feed(html)
    days = sorted(
        ({"date": d, "level": lvl, "count": count_from_tip(parser.tips.get(cid, ""))}
         for cid, (d, lvl) in parser.cells.items()),
        key=lambda x: x["date"],
    )
    if not days:
        raise SystemExit("no calendar cells found; GitHub markup may have changed")
    current, longest = streaks(days)
    best = max(days, key=lambda x: x["count"])
    data = {
        "user": USER,
        "fetched": date.today().isoformat(),
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "days": days,
    }
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "data", "contributions.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=1)
        handle.write("\n")
    print(f"{out}: {data['total']} contributions, {len(days)} days")


if __name__ == "__main__":
    main()
