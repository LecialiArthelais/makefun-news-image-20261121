# DESIGN.md — news-image-20261121

## Competitor analysis (leaderboard 22 Nov 00:12 WIB, 7,840 entries)

| Rank | Entry | Score | Title pattern |
| --- | --- | --- | --- |
| 1 | samatch-we | 99.1923% | "Saturday 21 November 2026: 35 dated stories, 7 regions — COP31 overtime, Saudi missiles, Peru quake" |
| 2 | kakek-zeus | 99.1188% | same "35 dated stories, 7 regions" format |
| 3 | asell | 99.0918% | same format |
| 4 | sipa | 99.0621% | 33 stories |
| 5 | madsrepo | 99.0593% | same format |
| 50 | (line) | 98.8172% | 50 stories |
| 100 | — | 98.6379% | — |

**Strengths of the top 5:** all use the winner template (giant
serif date masthead → region bar → numbers strip → 3 illustrated
heroes → ~10 illustrated mediums → dotted map + numbered pins →
numbered briefs → DATE CHECK → sources per story); all carry
35 dated stories in 7 regions; all lead with the same three
consensus stories (COP31 overtime, Riyadh missiles, Peru quake);
all are source_withheld, so their pages cannot be read directly.

**Weaknesses / openings:** the gap rank 1 → rank 50 is only
0.375 points and their confidence intervals overlap heavily — the
judge cannot reliably separate #1 from #50, so the contest is a
lottery among ~50 pages in the 98.8–99.2 band. More stories does
not help (rank 50 has 50 stories and scores lower than the 35-
story leaders). The only lever is maximal execution of the
template: 13 original code-drawn illustrations, correct event
dates, no factual slips, clean layout with zero overlap.

**Our path to top 1:** match the consensus exactly (35 stories,
7 regions, same three heroes in the same order), then beat the
field on execution — verified facts with a research file, the
DATE CHECK trap avoided (UK-EU reset was Friday, not Saturday;
Florida's 28-inch rain is from 2/17–19 Nov, not Saturday),
spiral de-collision so all 13 map pins stay legible, and a
zoom-QA pass that fixed the two defects found (COP31 art band
had no background; Europe map pins overlapped).

**Honest odds:** top-50 is realistic; top-1 needs a max-quality
page AND pairwise luck among ~50 near-identical pages — roughly
1-in-30 to 1-in-50. Do not promise top-1.

## Layout (1024×1024, final y = 1010)

Eyebrow → Gloock 42pt date masthead → red italic subline →
7-segment region bar (widths ∝ story counts) → THE DAY IN
NUMBERS (6 figures) → SATURDAY BY THE HOURS timeline →
3 hero cards (52px art band + place + headline + deck + source)
→ MORE OF THE DAY, 10 medium cards (2 cols × 5, 43px rows,
40px icon) → dark-navy dotted world map (pins 1–13, grey dots
14–35) → ALSO TODAY, 22 numbered briefs (3 cols) → DATE CHECK
box (9 refused stories) → NOT YET line → sources footer.

Palette: cream paper (246,239,221), navy ink (24,48,88), one red
accent (180,35,24). Fonts (OFL): Gloock masthead, Crimson Pro
headlines/decks, Instrument Sans UI, IBM Plex Mono labels.

## Illustrations

13 flat-vector illustrations drawn in code with Pillow, each
rendered once at 96×96 and pasted scaled onto its own background
colour, so hero bands and 40px medium icons share one source:
COP31 globe + thermometer · Riyadh night skyline + intercept
streaks · Peru mountains + seismograph · BepiColombo spacecraft
+ Mercury · Nasdaq falling chart · MQ-9 drone + red X ·
Danish flag + exit door · daraxonrasib capsule + shrinking
cells · killer-robot head + gear · Mexico handcuffs + star badge
· FBI shield + magnifier · tennis ball + racket · White House
+ flag. No raster assets, no AI images — the winner template's
#1 differentiator is original code-drawn art, and AI images
would be non-deterministic and (via the usual generators) paid.

## Skills used (audited, actually used — not just installed)

- **news_image_page** (local skill): the method + winner
  template. Followed end to end.
- **makefun_bounty_submission** (local skill): quota-first,
  fresh kit, bundle flags, Node 24 network / Node 22 local,
  review-before-submit.
- **canvas-design** (local skill): OFL fonts used for all type.
- **Pillow (python-pillow/Pillow)** — **14,004 stars** on GitHub
  (verified via `gh api` 22 Nov), licence HPND (OSI-approved;
  the API returns NOASSERTION because the licence field is not
  SPDX-detected). Pure imaging library, already installed
  (10.2.0), no network, no credentials, no untrusted input —
  SAFE. It is the renderer for the whole page.

## Skills searched and rejected

- `news-front-page` (pipecat-ai/gradient-bang): **420 stars** —
  fails the >500-star rule; also built for a fictional game
  world, not real news. Not installed.
- `infographics` (local): generates via Nano Banana 2 through
  OpenRouter — needs a paid API key. Rejected: no-spend rule,
  and AI images break the code-drawn-art method.
- `content-image-suite` infographic-generator: needs a fal.ai
  API key (FAL_KEY), proprietary licence, paid. Rejected.
- `hermes-paper-agent` / `vaelkeep`: personal newspaper
  generators, not skills for this task; no fit.
- Daily HTML Newspaper Generator (agensi.io): paid skill, HTML
  output — wrong format. Rejected.

Conclusion: no new external GitHub skill above 500 stars fits
this task better than the proven local method; the >500★
dependency actually used is Pillow (14,004★, audited, safe).

## QA log

1. First render overflowed (final y 1171) — tightened the
   layout budget (masthead 42pt, heroes 150px, mediums 43px,
   map 112px, also rows 14px, date-check 58px) → final y 1010.
2. Zoom-QA found COP31's art band had a paper background, so
   the globe read as a lost icon — fixed with a tinted teal
   background and a larger globe.
3. Zoom-QA found map pins 8/12 and 11/5 merged into unreadable
   blobs — fixed with spiral de-collision (radii 0/14/20/27/34/42,
   45° steps, 17px minimum separation, leader lines, 7.5px pins).
   All 13 pins verified legible at 3× zoom.
4. Numbers-strip labels verified clean at 1.5× zoom (the
   apparent jam in the small preview was a scaling artefact).
