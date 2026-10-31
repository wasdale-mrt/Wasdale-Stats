"""
Nightly stats - READ ONLY.

Reads call-outs from D4H and writes two public files:
  site/data/stats.json  - the figures for the dashboard (site/index.html)
  site/callouts.json    - one row per call-out for the map (site/map.html)

Rules (see START-HERE.md):
  - GET requests only. Nothing in D4H is ever changed.
  - No member details, no casualty details, no free text. Only: reference,
    month, position, call-out type, root cause tags and place tags.
  - The Actions log is public, so the log prints counts only.

Run by the GitHub Actions job .github/workflows/nightly.yml.
For a test without D4H:  python tools/build_stats.py --from-file incidents.json
"""

import argparse
import collections
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tag_groups as tg  # noqa: E402
from d4h_discovery import get_all  # noqa: E402  (same read-only GET helper)

TEAM = "141"
UK = ZoneInfo("Europe/London")
ROOT = Path(__file__).resolve().parent.parent
OUT_STATS = ROOT / "site" / "data" / "stats.json"
OUT_MAP = ROOT / "site" / "callouts.json"

# Positions outside this box are treated as missing (for example 0,0).
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 53.9, 55.2, -3.9, -2.4

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def parse_time(s):
    if not s:
        return None
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UK)


def same_point_last_year(today):
    """The same day last year (28 Feb if today is 29 Feb)."""
    try:
        return today.replace(year=today.year - 1)
    except ValueError:
        return today.replace(year=today.year - 1, day=28)


def clean(incidents, titles):
    """Turn raw D4H incidents into plain call-out rows. Drops everything private."""
    rows, unknown, dropped_training = [], collections.Counter(), []
    for inc in incidents:
        if inc.get("deletedAt"):
            continue
        start = parse_time(inc.get("startsAt"))
        if not start:
            continue
        end = parse_time(inc.get("endsAt"))
        tag_ids = [t.get("id") for t in (inc.get("tags") or []) if t.get("id")]
        groups = collections.defaultdict(list)
        for tid in tag_ids:
            g = tg.group_of(tid)
            if g == "unknown":
                unknown[titles.get(tid, str(tid))] += 1
            groups[g].append(tid)
        if groups["training"]:
            # Still a call-out (exercises are kept apart in D4H). Its training
            # tags are just not shown. Listed in the log so it can be checked.
            dropped_training.append(f'{inc.get("reference") or "no ref"} ({start:%d %b %Y})')

        causes = [tid for tid in tg.ROOT_CAUSE if tid in groups["cause"]]  # priority order
        hours = 0.0
        if end and end > start:
            hours = min((end - start).total_seconds() / 3600, 72)  # cap odd records
        members = int(inc.get("countAttendance") or 0)

        lat = lon = None
        coords = (inc.get("location") or {}).get("coordinates") or []
        if len(coords) == 2:
            x, y = float(coords[0]), float(coords[1])
            if LAT_MIN <= y <= LAT_MAX and LON_MIN <= x <= LON_MAX:
                lon, lat = round(x, 5), round(y, 5)

        rows.append({
            "ref": inc.get("reference") or "",
            "start": start,
            "type": next((tg.TYPE[t] for t in groups["type"]), "Not recorded"),
            "causes": [tg.ROOT_CAUSE[t] for t in causes],
            "places": [tg.PLACE[t] for t in groups["place"]],
            "members": members,
            "team_hours": members * hours,
            "lat": lat,
            "lon": lon,
        })
    rows.sort(key=lambda r: r["start"])
    return rows, unknown, dropped_training


def pct_change(now, before):
    if not before:
        return None
    return round((now - before) / before * 100)


def counter_rows(this_rows, last_rows, key, top=None):
    a = collections.Counter(v for r in this_rows for v in r[key])
    b = collections.Counter(v for r in last_rows for v in r[key])
    names = sorted(set(a) | set(b), key=lambda n: (-a[n], -b[n], n))
    if top:
        names = [n for n in names if a[n]][:top] or names[:top]
    return [{"name": n, "this_year": a[n], "last_year": b[n]} for n in names]


def build(rows, now):
    today = now.date()
    year, last = today.year, today.year - 1
    cutoff_last = same_point_last_year(today)

    this_ytd = [r for r in rows if r["start"].year == year and r["start"].date() <= today]
    last_all = [r for r in rows if r["start"].year == last]
    last_ytd = [r for r in last_all if r["start"].date() <= cutoff_last]

    def summary(rs):
        attended = [r for r in rs if r["members"] > 0]
        return {
            "callouts": len(rs),
            "team_hours": round(sum(r["team_hours"] for r in rs)),
            "avg_members": round(sum(r["members"] for r in attended) / len(attended), 1)
            if attended else None,
        }

    s_now, s_last = summary(this_ytd), summary(last_ytd)
    headline = []
    for key, label in [("callouts", "Call-outs"),
                       ("team_hours", "Team hours on call-outs"),
                       ("avg_members", "Average members per call-out")]:
        headline.append({
            "metric": key, "label": label,
            "this_year": s_now[key], "last_year": s_last[key],
            "change_pct": pct_change(s_now[key] or 0, s_last[key] or 0),
        })

    # Running total by month, with a projection after this month.
    by_month_now = collections.Counter(r["start"].month for r in this_ytd)
    by_month_last = collections.Counter(r["start"].month for r in last_all)
    cum_now = cum_last = 0
    running, monthly = [], []
    for m in range(1, 13):
        cum_last += by_month_last[m]
        if m <= today.month:
            cum_now += by_month_now[m]
        projected = None
        if m >= today.month:
            projected = len(this_ytd) + (cum_last - len(last_ytd))
        running.append({
            "month": MONTHS[m - 1],
            "this_year": cum_now if m <= today.month else None,
            "last_year": cum_last,
            "projected": projected,
        })
        monthly.append({
            "month": MONTHS[m - 1],
            "this_year": by_month_now[m] if m <= today.month else None,
            "last_year": by_month_last[m],
        })

    days_now = collections.Counter(r["start"].weekday() for r in this_ytd)
    days_last = collections.Counter(r["start"].weekday() for r in last_ytd)
    days = [{"day": DAYS[d], "this_year": days_now[d], "last_year": days_last[d]}
            for d in range(7)]

    types = counter_rows(this_ytd, last_ytd, "type_list")
    causes = counter_rows(this_ytd, last_ytd, "causes")
    places = counter_rows(this_ytd, last_ytd, "places", top=12)

    no_cause = sum(1 for r in this_ytd if not r["causes"])
    top_cause = causes[0]["name"] if causes and causes[0]["this_year"] else None

    per_year = collections.Counter(r["start"].year for r in rows)

    spots = [{"lat": r["lat"], "lon": r["lon"], "month": MONTHS[r["start"].month - 1],
              "cause": r["causes"][0] if r["causes"] else "Not recorded"}
             for r in this_ytd if r["lat"] is not None]

    return {
        "updated": now.isoformat(timespec="minutes"),
        "year": year,
        "last_year": last,
        "compared_to": cutoff_last.isoformat(),
        "headline": headline,
        "top_cause": top_cause,
        "running_total": running,
        "monthly": monthly,
        "types": types,
        "causes": causes,
        "callouts_without_cause": no_cause,
        "places": places,
        "days": days,
        "spots": spots,
        "per_year": [{"year": y, "callouts": per_year[y]} for y in sorted(per_year)],
        "notes": {
            "team_hours": "Members on the call-out x how long the call-out lasted.",
            "causes": "A call-out can have more than one root cause.",
        },
    }


def map_rows(rows):
    out = []
    for r in rows:
        if r["lat"] is None:
            continue
        out.append({
            "ref": r["ref"],
            "year": r["start"].year,
            "month": MONTHS[r["start"].month - 1],
            "type": r["type"],
            "location": ", ".join(r["places"]) or "Not recorded",
            "cause": r["causes"][0] if r["causes"] else "Not recorded",
            "causes": r["causes"],
            "lat": r["lat"],
            "lon": r["lon"],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-file", help="test: read incidents from a JSON file, not D4H")
    ap.add_argument("--tags-file", help="test: read the tag list from a JSON file")
    ap.add_argument("--now", help="test: pretend today is this ISO date")
    args = ap.parse_args()

    if args.from_file:
        incidents = json.loads(Path(args.from_file).read_text())
        tags = json.loads(Path(args.tags_file).read_text()) if args.tags_file else []
    else:
        incidents, _ = get_all(f"/team/{TEAM}/incidents")
        tags, _ = get_all(f"/team/{TEAM}/tags")
    titles = {t["id"]: t.get("title", "") for t in tags}

    now = dt.datetime.now(UK)
    if args.now:
        now = dt.datetime.fromisoformat(args.now).replace(tzinfo=UK)

    rows, unknown, dropped = clean(incidents, titles)
    for r in rows:
        r["type_list"] = [r["type"]]
    stats = build(rows, now)
    points = map_rows(rows)

    OUT_STATS.parent.mkdir(parents=True, exist_ok=True)
    OUT_STATS.write_text(json.dumps(stats, indent=1))
    OUT_MAP.write_text(json.dumps(points, separators=(",", ":")))

    # Counts only - this log is public.
    print(f"Incidents read: {len(incidents)}")
    print(f"Call-outs with training tags (counted, tags not shown): {len(dropped)}")
    for d in dropped:
        print(f"  {d}")
    print(f"Call-outs used: {len(rows)}")
    print("Call-outs per year (whole year):")
    for y in stats["per_year"]:
        print(f"  {y['year']}: {y['callouts']}")
    print(f"This year so far: {stats['headline'][0]['this_year']}")
    print(f"Last year to {stats['compared_to']}: {stats['headline'][0]['last_year']}")
    print(f"Map points: {len(points)}")
    if unknown:
        print("New tags not yet grouped (add to tools/tag_groups.py):")
        for name, n in unknown.most_common():
            print(f"  {n:>4}  {name}")
    print("Done. Nothing in D4H was changed.")


if __name__ == "__main__":
    main()
