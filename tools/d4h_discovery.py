"""
D4H discovery - READ ONLY.

Prints what the D4H incident records look like, so the nightly stats job
can be written. Run by hand from the GitHub Actions tab.

Actions logs on a public repository are public. So this script:
  - prints field NAMES for every field,
  - prints VALUES only for dates, references, tags and position,
  - never prints names, descriptions, casualty or member details.

It only ever sends GET requests. It never changes anything in D4H.
"""

import collections
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.team-manager.eu.d4h.com/v3"
TEAM = "141"
PAGE_SIZE = 250
SAMPLE_COUNT = 5

# A field's value is printed only if its name matches one of these.
SAFE_VALUE = re.compile(
    r"(^id$|date|At$|time|year|ref|tag|lat|lng|lon|grid|coord|position|point)",
    re.IGNORECASE,
)
# ...and never if it matches one of these (wins over the list above).
NEVER_VALUE = re.compile(
    r"(name|desc|note|plan|casualt|subject|patient|member|person|people|"
    r"phone|email|address|comment|text|summary|detail|by$|owner|author)",
    re.IGNORECASE,
)


def get(path, params=None):
    """GET one page from D4H. Read only."""
    token = os.environ.get("D4H_TOKEN", "").strip()
    if not token:
        sys.exit("No D4H_TOKEN secret found. Save it in GitHub first "
                 "(Settings > Secrets and variables > Actions).")
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"D4H said {e.code} for {path}. "
                 f"401/403 usually means the token is wrong or expired.")


def get_all(path):
    """Get every page of a list, pages from 0."""
    rows, page = [], 0
    while True:
        data = get(path, {"page": page, "size": PAGE_SIZE})
        batch = data.get("results", data if isinstance(data, list) else [])
        rows.extend(batch)
        total = data.get("totalSize") if isinstance(data, dict) else None
        if not batch or len(batch) < PAGE_SIZE or (total and len(rows) >= total):
            return rows, data
        page += 1


def walk(obj, prefix=""):
    """Yield (field path, value) for every leaf field."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        if not obj:
            yield prefix + "[]", obj
        for item in obj:
            yield from walk(item, prefix + "[]")
    else:
        yield prefix, obj


def safe(field):
    leaf = field.replace("[]", "").split(".")
    if any(NEVER_VALUE.search(part) for part in leaf):
        return False
    return bool(SAFE_VALUE.search(leaf[-1]))


def type_name(v):
    return "null" if v is None else type(v).__name__


def main():
    print("=== D4H discovery (read only) ===\n")

    incidents, raw = get_all(f"/team/{TEAM}/incidents")
    print(f"Incidents found: {len(incidents)}")
    if isinstance(raw, dict):
        print("Top-level keys in a list reply:", sorted(raw.keys()))
    if not incidents:
        sys.exit("No incidents came back. Check the token's permissions.")

    # 1. Every field name, how often it is filled, and its type.
    filled = collections.Counter()
    types = collections.defaultdict(set)
    for inc in incidents:
        seen = set()
        for field, value in walk(inc):
            types[field].add(type_name(value))
            if value not in (None, "", []) and field not in seen:
                filled[field] += 1
                seen.add(field)
    print("\n--- Field names (filled count / types / value shown?) ---")
    for field in sorted(types):
        shown = "values shown" if safe(field) else "hidden"
        print(f"  {field:<45} {filled[field]:>5}  "
              f"{'/'.join(sorted(types[field])):<20} {shown}")

    # 2. A few sample records: safe values only.
    print(f"\n--- {SAMPLE_COUNT} sample incidents (safe fields only) ---")
    for inc in incidents[:SAMPLE_COUNT]:
        print("  -")
        for field, value in walk(inc):
            if safe(field) and value not in (None, "", []):
                print(f"      {field}: {value}")

    # 3. Count per year, from the first date-like field we can find.
    date_fields = [f for f in types if re.search(r"(startsAt|date|At$)", f)]
    print("\nDate-like fields:", date_fields)
    if date_fields:
        key = next((f for f in date_fields if "start" in f.lower()), date_fields[0])
        years = collections.Counter()
        for inc in incidents:
            for field, value in walk(inc):
                if field == key and isinstance(value, str) and len(value) >= 4:
                    years[value[:4]] += 1
                    break
        print(f"\n--- Incidents per year (using {key}) ---")
        for y in sorted(years):
            print(f"  {y}: {years[y]}")

    # 4. How often each tag value appears on incidents.
    tag_counts = collections.Counter()
    for inc in incidents:
        for field, value in walk(inc):
            if ("tag" in field.lower()
                    and not re.search(r"(desc|note|comment|text|by$|owner)",
                                      field, re.IGNORECASE)
                    and isinstance(value, (str, int))):
                tag_counts[f"{field} = {value}"] += 1
    print("\n--- Tag values on incidents (most common first) ---")
    for tag, n in tag_counts.most_common(200):
        print(f"  {n:>5}  {tag}")

    # 5. The team's tag list, if the endpoint exists.
    print("\n--- Team tag list ---")
    try:
        tags, _ = get_all(f"/team/{TEAM}/tags")
        for t in tags:
            print("  ", {k: v for k, v in t.items()
                         if not NEVER_VALUE.search(k) or k.lower() in ("title", "name")})
    except SystemExit as e:
        print(f"  Could not read the tag list: {e}")

    print("\nDone. Nothing in D4H was changed.")


if __name__ == "__main__":
    main()
