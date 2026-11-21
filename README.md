# news-image-20261121 — Saturday 21 November 2026 in one image

Entry for the make.fun bounty **news-image-20261121**
("Sum up 21 November's world news in one image", $100).
Closes 23 Nov 2026 07:00 WIB.

## What it is

A single 1024×1024 front page covering **35 dated stories from
21 November 2026 across 7 regions**, built on the proven winner
template: giant serif date masthead, coloured region bar,
"THE DAY IN NUMBERS" strip, a Saturday timeline, 3 illustrated
hero cards, 10 illustrated medium cards, a dotted world map with
numbered pins, 22 numbered briefs, a DATE CHECK box and sources
per story.

Leads: COP31 talks slip into overtime with no deal · three Houthi
missiles intercepted over Riyadh · a M6.7 quake shakes Peru's Andes.

## Files

- `entry.png` — the rendered front page (the deliverable).
- `build_frontpage.py` — renders `entry.png` from `stories.json`
  with Pillow. All 13 illustrations are flat-vector shapes drawn
  in code; no raster assets, no network, no AI generation.
  Deterministic output.
- `stories.json` — the 35 stories (heroes, mediums, also-list),
  numbers strip, timeline, DATE CHECK and footer. Every story
  carries its event date, place, coordinates and sources.
- `main.ts` — harness entry point (Node 22, stdlib only):
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `DESIGN.md` — design decisions, competitor analysis and the
  skill audit behind this entry.

## Build

```sh
python3 build_frontpage.py   # writes entry.png (1024x1024)
```

Requires Python 3 + Pillow and the OFL fonts in
`~/workspace/custom-skills/canvas-design/canvas-fonts/`
(Gloock, Crimson Pro, Instrument Sans, IBM Plex Mono).

## Date rule

Every story is dated by the day its event happened, never the
article date. Friday 20 Nov evening events are carried as
Saturday leads only where they happened after the Friday close;
Thursday 19 Nov stories (Anthropic's $2tn debut, the Senate
48–51 Iran vote, Pete Rose's pardon, the PIF Tower hit,
GTA VI's $2.36bn launch day) are refused to DATE CHECK.
See `../research-2026-11-21.md` for the verification notes.

## Sources

Reuters · AP · AFP · The Guardian · BBC · NYT · CNN · Le Monde ·
USGS · ESA · WHO · IAEA · CISA · Nasdaq.
