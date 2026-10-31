# Wasdale MRT stats - start here

Public call-out stats and map for Wasdale Mountain Rescue Team, updated nightly
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
- **Where we are vs last year**: running total line. After the current month,
  a dotted projection line = where we end up if the rest of the year runs like
  last year.
- Call-outs by month (this year beside last year).
- **Root cause**: from the tags picked on each call-out in D4H.
- **Where**: from the location tag, and the incident grid ref / lat-long.
- Call-out spots plot (small, no base map) plus a link to the full map.
- Day of the week.

A design mock-up with sample data lives in Claude as an artifact called
"Wasdale MRT Dashboard". The public version will be rebuilt as a page here.

## Next steps

1. Lee saves the D4H token as a GitHub secret (`D4H_TOKEN`).
2. Claude adds a **discovery job** (run by hand from the Actions tab) that
   prints D4H incident field names, tag lists and counts. It prints values
   only for dates, references, tags and position - no casualty or member
   details, because Actions logs on a public repository are public.
3. From that output, Claude writes the nightly stats job and the pages.
4. Turn on GitHub Pages.

## Files

| Path | What it is |
|---|---|
| `site/map.html` | The OpenTopoMap call-out map. Shows sample data until `callouts.json` exists beside it. |

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
