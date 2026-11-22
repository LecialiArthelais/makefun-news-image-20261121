# news-image-20261121 — Saturday 21 November 2026 in one image (v2-alt, path B)

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/LecialiArthelais/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/LecialiArthelais/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Entry for the make.fun bounty **news-image-20261121**
("Sum up 21 November's world news in one image", $100) — see the
[bounty page](https://make.fun/bounty/news-image-20261121).
Closes 23 Nov 2026 07:00 WIB.

Referral code: `3554s5p5` — try make.fun and build your own entry.

Branch `news21-b`: the alternative maximisation (path B). See
`DESIGN_v2.md` for the full audit of v1 and the design notes.

## What it is

A single 1024×1024 front page covering **35 dated stories from
21 November 2026 across 7 regions**, built on the proven winner
template: giant serif date masthead, coloured region bar,
"THE DAY IN NUMBERS" strip (8 figures), a Saturday timeline
(6 items), 3 illustrated hero cards, 10 illustrated medium
cards, a dotted world map with numbered pins, 22 numbered briefs,
a DATE CHECK box and sources per story. Every featured card
carries a CONFIRMED / CLAIMED / REPORTED confidence tag.

Angle — "the Saturday that kept escalating": the evening-update
edition. Leads: **Iran strikes US bases in Bahrain** (Saturday
night, after v1's research window) · a M6.7 quake shakes Peru's
Andes (1 dead, 16 injured, 152 homes uninhabitable per the later
INDECI report) · COP31 still without a deal after 24+ hours in
overtime.

## Files

- `entry.png` — the rendered front page (the deliverable).
- `build_frontpage_v2.py` — renders `entry.png` from
  `stories_v2.json` with Pillow. Written from scratch in this
  session. All 13 illustrations are flat-vector shapes drawn in
  code; no raster assets, no network, no AI generation.
  Deterministic output.
- `stories_v2.json` — the 35 stories (heroes, mediums,
  also-list), numbers strip, timeline, DATE CHECK and footer.
  Every story carries its event date, place, coordinates,
  sources and a confidence tag.
- `main.ts` — harness entry point (Node 22, stdlib only):
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `DESIGN_v2.md` — audit of v1 (missed stories, date errors,
  figure corrections), design decisions and the skill audit.
- `build_frontpage.py`, `stories.json`, `DESIGN.md` — the v1
  entry, kept on this branch for reference; the submitted entry
  is built by `build_frontpage_v2.py` from `stories_v2.json`.

## Build

```sh
python3 build_frontpage_v2.py   # writes entry.png (1024x1024)
```

Requires Python 3 + Pillow and the OFL fonts in
`~/workspace/custom-skills/canvas-design/canvas-fonts/`
(Gloock, Crimson Pro, Instrument Sans, IBM Plex Mono).

## Date rule

Every story is dated by the day its event happened, never the
article date. Friday 20 Nov evening events are carried as
Saturday leads only where they happened after the Friday close.
Thursday 19 Nov stories are refused to DATE CHECK — including
three v1 wrongly carried as Saturday: the Denmark–Greenland
deal vote 109-0, the Gaza 22,000 children statement and
Mongolia's president resigning. See `DESIGN_v2.md` for the
verification notes and sources.

## Sources

Reuters · AP · AFP · The Guardian · BBC · NYT · CNN · Le Monde ·
USGS · ESA · WHO · IAEA · CISA · Nasdaq · Al Jazeera · ISW.
