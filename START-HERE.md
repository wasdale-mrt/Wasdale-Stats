# Wasdale MRT stats - start here

Public call-out stats and map for Wasdale Mountain Rescue Team, updated every 2 hours
from D4H. Repository: https://github.com/wasdale-mrt/Wasdale-Stats (public).

## What we are building

1. **A stats dashboard** that can be read at a glance and shared with people of
   interest. Call-out figures only (training exercises were taken out).
2. **A call-out map** on OpenTopoMap (Leaflet), with a dot per call-out,
   coloured by root cause. Exact positions are fine to show (Lee's decision).

Both will be plain web pages hosted free on **GitHub Pages** from this
repository.

## How it will work

- A **GitHub Actions job runs each night** in the cloud. It reads D4H, works out
  the figures, writes JSON files, and the pages read those files.
- No laptop or mini PC needs to be on. Lee manages everything from the laptop.
- The D4H token is stored as a **GitHub secret** called `D4H_TOKEN`. It is a
  separate token from the board's, named "WMRT stats - GitHub", 1-year expiry.
- The job **only reads** from D4H. It must never change any records.
- D4H API: `https://api.team-manager.eu.d4h.com/v3`, team id `141`. The board
  repository (`wasdale-attendance-board`, `board/BoardCommon.ps1`) shows the
  working pattern: Bearer token, pages from 0, `size` up to 250.
  `tools/Show-D4HIncidents.ps1` there is a read-only field check to reuse.

## What the dashboard shows

- Headline: call-outs up or down on last year, and the top root cause.
- Big numbers, each with change vs same point last year: call-outs, team hours
  on call-outs, average members per call-out.
- **Highest recorded year** box: the busiest full year in D4H (2024 at the
  moment), its total, and how many call-outs it had at this point in the year
  next to this year's figure.
- **Where we are vs last year**: running total line. After the current month,
  a dashed red projection line = where we end up if the rest of the year runs
  like last year. A dotted black line shows the highest recorded year.
- Call-outs by month (this year beside last year).
- **Root cause**: from the tags picked on each call-out in D4H.
- **Where**: from the location tag, and the incident grid ref / lat-long.
- Call-out spots plot (small, no base map) plus a link to the full map.
- Day of the week.
- Call-out type (Full Team, Limited, Alert).

## Decisions (31 Oct 2026)

- **Alerts count** as call-outs, with Full Team and Limited.
- **Sensitive root causes** (Suicide, Body Recovery) are **shown as tagged**.
- **Team hours** = members on the call-out (`countAttendance`) x how long it
  lasted (`startsAt` to `endsAt`). D4H has no hours field on incidents.
- **Every incident counts.** Training exercises are kept apart in D4H, so the
  incident list is call-outs only. One call-out has swiftwater course tags
  by mistake: it still counts, the tags are just not shown.
- **Injury and medical tags** (body parts, conditions) are casualty details.
  They are never written to the public files.
- **Map popups** show reference, month and year, type, place and causes.
  No exact date or time.
- **Highest recorded year (5 Nov 2026).** Never call it a "record" or a
  target. The team wants fewer call-outs, not more. No progress bar and no
  "to beat" wording. It is worked out each night, not typed in. 2024 is the
  busiest year, and it is in D4H, so the figure is right even though older
  years are not in D4H.
- **Footer (6 Nov 2026)** on both pages: copyright Wasdale Mountain Rescue
  Team (year updates itself), registered charity no. 1170178, links to
  wmrt.org.uk and the donate page, "Designed by Lee Tunstall". The dashboard
  also notes that figures may change as D4H records are updated.
- Which tag is which group lives in `tools/tag_groups.py`. A new D4H tag is
  left off the pages until it is added there. The stats job log lists any.

A design mock-up with sample data lives in Claude as an artifact called
"Wasdale MRT Dashboard". The public version will be rebuilt as a page here.

## Next steps

1. Lee saves the D4H token as a GitHub secret (`D4H_TOKEN`).
2. **Done (31 Oct 2026).** Claude adds a **discovery job** (run by hand from the Actions tab) that
   prints D4H incident field names, tag lists and counts. It prints values
   only for dates, references, tags and position - no casualty or member
   details, because Actions logs on a public repository are public.
   Lee runs it once and pastes the log into Claude.
3. **Done (31 Oct 2026).** Claude writes the nightly stats job and the pages.
4. Lee turns on GitHub Pages: Settings > Pages > Source = **GitHub Actions**.
   Then runs "Stats update" once by hand (it was called "Nightly stats") from the Actions tab.
   The pages will be at https://wasdale-mrt.github.io/Wasdale-Stats/

## Files

| Path | What it is |
|---|---|
| `site/index.html` | The stats dashboard. Reads `data/stats.json`. |
| `site/map.html` | The OpenTopoMap call-out map. Reads `callouts.json`. Shows sample data until it exists. Has a year picker. |
| `.github/workflows/nightly.yml` | Stats job, every 2 hours (about 17 minutes past). Reads D4H, builds both JSON files, publishes `site/` to GitHub Pages. Also runs by hand, or when files change. |
| `tools/build_stats.py` | The stats script. GET only. The JSON files are made fresh every run and are not kept in the repository. |
| `tools/tag_groups.py` | Which D4H tag is a call-out type, root cause, place, training, private (injury/medical) or not shown. |
| `.github/workflows/d4h-discovery.yml` | Discovery job. Run by hand: Actions tab > "D4H discovery (read only)" > Run workflow. |
| `tools/d4h_discovery.py` | The discovery script. GET only. Prints field names, and values only for dates, references, tags and position. |

## Rules

- Never put the D4H token, or any secret, in a file here.
- No member contact details or casualty details anywhere in this repository.
- Ask Lee before anything that would write to D4H.

## Working with Lee (for a new Claude chat)

- Lee is dyslexic: plain words, short steps, British English.
- Spell instructions out in full every time. Put copy-paste commands at the
  bottom of the message.
- New to GitHub: every change ends with GitHub Desktop - a **Summary** line and
  a short **Description**, then **Commit**, then **Push origin**. Give both
  ready to paste.
- Lee keeps to-dos in Google Tasks. When a job is agreed for later, end the
  reply with one line: "Add to Google Tasks: [short task name]".

## A new Claude chat, first message

> Read START-HERE.md in the Wasdale-Stats repository. Then carry on with the
> next job.

Then connect the laptop and give it access to the `Wasdale-Stats` folder.
