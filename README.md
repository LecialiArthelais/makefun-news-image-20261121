# news-image-20261121 — Saturday 21 November 2026 in one image

Entry for the make.fun bounty **news-image-20261121**
("Sum up 21 November's world news in one image", $100).
Closes 23 Nov 2026 07:00 WIB.

## What it is

A single 1024×1024 front page covering **35 dated stories from
21 November 2026 across 9 regions**, built on the proven winner
template: giant serif date masthead, coloured region bar,
"THE DAY IN NUMBERS" strip, a Saturday UTC timeline, 3 illustrated
hero cards, 10 illustrated medium cards, a light dotted world map
with numbered pins, 22 numbered briefs, a DATE CHECK box, a
HOW WE CHECKED box and sources per story. Every card carries a
confidence badge (✓ CONFIRMED / OFFICIAL / REPORTED / CLAIM).

Leads: Iran strikes US bases in Bahrain and two tankers are hit
off Oman · a M6.7 quake shakes Peru's Andes (1 dead, 16 hurt) ·
COP31 talks slip into overtime with no deal.

## Files

- `entry.png` — the rendered front page (the deliverable).
- `build_frontpage_v2.py` — renders `entry.png` from
  `stories_v2.json` with Pillow. All 13 illustrations are
  flat-vector shapes drawn in code; no raster assets, no network,
  no AI generation. Deterministic output. (v2 rebuild, branch
  `news21-a`; v1 files `build_frontpage.py` / `stories.json`
  kept for history.)
- `stories_v2.json` — the 35 stories (heroes, mediums, briefs),
  numbers strip, timeline, DATE CHECK and footer. Every story
  carries its event date, place, coordinates, badge and sources.
- `main.ts` — harness entry point (Node 22, stdlib only):
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `DESIGN.md` — design decisions, competitor analysis and the
  skill audit behind this entry.

## Build

```sh
python3 build_frontpage_v2.py   # writes entry.png (1024x1024)
```

Requires Python 3 + Pillow and the OFL fonts in
`~/workspace/custom-skills/canvas-design/canvas-fonts/`
(Gloock, Crimson Pro, Instrument Sans, IBM Plex Mono).

## Date rule

Every story is dated by the day its event happened, never the
article date. The Peru quake is 19:09 Friday in Lima but 00:09
UTC Saturday — carried as a Saturday hero at its UTC time.
Friday 20 Nov evening events are carried only where they
happened after the Friday close (El Chapo Isidro capture,
Kryvyi Rih strike, FBI breach, N. Korea enrichment); the
Friday Nasdaq close (−5.3%) and Trump's data-centre tax threat
are demoted to DATE CHECK. Thursday 19 Nov stories (Anthropic's
$2tn debut, the Senate 48–51 Iran vote, Pete Rose's pardon,
the PIF Tower hit, GTA VI's $2.36bn launch day) are refused
to DATE CHECK. See `../research-2026-11-21.md` for the v1
verification notes; v2 facts were re-verified 22 Nov ~13:00 WIB
against Reuters, AP, AFP, Al Jazeera, ESA, IGP, USGS, INDECI,
UKMTO, European Commission, Focus Taiwan, CAAP and others.

## Sources

Reuters · AP · AFP · Al Jazeera · ESA · IGP · USGS · INDECI ·
UKMTO · European Commission · Focus Taiwan · CAAP · WHO · IAEA ·
CNN · NYT · Press TV · Ukrinform · Kyiv Post · Daily Trust.
