# news-image-20261121 — Saturday 21 November 2026 in one image (v2, round 2)

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/LecialiArthelais/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/LecialiArthelais/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Entry for the make.fun bounty **news-image-20261121**
("Sum up 21 November's world news in one image", $100) — see the
[bounty page](https://make.fun/bounty/news-image-20261121).
Closes 23 Nov 2026 07:00 WIB.

Referral code: `3554s5p5` — try make.fun and build your own entry.

Round 2 (v2): a full rebuild against the top-10 competitor analysis
(`../analysis-competitor-v2.md`). See `DESIGN_v3.md` for the punch-list,
verification log and honest odds.

## What it is

A single 1024×1024 front page covering **35 dated stories from
21 November 2026 across 9 regions**, built on the proven winner
template: giant black serif date masthead, coloured 9-region bar,
"THE DAY IN NUMBERS" strip (6 sourced figures), an all-Saturday UTC
timeline (7 items), 3 large illustrated hero panels (Gulf map, Peru
depth cross-section, COP31 thermometer + calendar), 10 illustrated
medium panels each anchored by a big numeral, a dotted world map with
region-coloured numbered pins, 22 numbered briefs with a source after
every brief, a DATE CHECK box (18 exclusions) and a 4-level confidence
legend. Every featured card carries a CONFIRMED tag.

Leads: **Iran strikes US bases in Bahrain** (Saturday night) · a M6.7
quake shakes Peru's Andes (depth 108–129 km; 1 dead, 16 injured, 152
homes uninhabitable) · COP31 still without a deal after 24+ hours in
overtime. New in v2: the EU–Indonesia trade pact (98.5%), Davao jet
landing (146 safe), Bitcoin's two-year low ($55,130), Banda Sea M6.8,
France marches (82,500), England 37–12 — the consensus stories v1 missed.

## Files

- `entry.png` — the rendered front page (the deliverable).
- `build_frontpage_v3.py` — renders `entry.png` from
  `stories_v3.json`. Written from scratch in this session. Pillow +
  drawsvg hero scenes + CairoSVG/Lucide icon stamps + a matplotlib
  mini-chart; all 13 illustrations are original flat-vector work drawn
  in code; no raster assets, no network, no AI generation.
  Deterministic output.
- `stories_v3.json` — the 35 stories (heroes, mediums, also-list),
  numbers strip, timeline, DATE CHECK and footer. Every story carries
  its event date, place, coordinates, sources and a confidence tag.
- `vendor/lucide/` — 17 vendored Lucide icons (lucide-static 1.77.0,
  ISC), bytes re-verified.
- `main.ts` — harness entry point (Node 22, stdlib only):
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `DESIGN_v3.md` — punch-list compliance, verification log, skill
  audit and QA log.
- `build_frontpage.py`, `stories.json`, `DESIGN.md`,
  `build_frontpage_v2.py`, `stories_v2.json`, `DESIGN_v2.md` — the v1
  and evening-update editions, kept for reference; the submitted entry
  is built by `build_frontpage_v3.py` from `stories_v3.json`.

## Build

```sh
python3 build_frontpage_v3.py   # writes entry.png (1024x1024)
```

Requires Python 3 + Pillow, drawsvg 2.5.1, CairoSVG 2.9.1,
matplotlib and fontTools, and the OFL fonts in
`~/workspace/custom-skills/canvas-design/canvas-fonts/`
(Gloock, Crimson Pro, Instrument Sans, IBM Plex Mono).

## Date rule

Every story is dated by the day its event happened, never the
article date. Friday 20 Nov stories are refused to DATE CHECK —
including the Denmark attaché expulsion, the Kryvyi Rih strike, the
missiles in Poland, Wall Street's fall into correction, Cyclone
Akvan's landfall and the WHO Ebola emergency. Thursday 19 Nov stories
(Denmark–Greenland vote 109-0, Gaza 22,000 children, Mongolia's
president resigning, GTA VI launch) are in DATE CHECK too, plus
Voyager 1's light-day (Wed 18 Nov). See `DESIGN_v3.md` for the
verification notes and sources.

## Sources

Reuters · AP · AFP · BBC · USGS · ESA · UN · EU Commission · UKMTO ·
CAAP · Al Jazeera · ISW · NWS · AFL · CAF · MAMA Awards.
