# DESIGN_v2.md — news-image-20261121, path B ("evening-update edition")

## Angle (different from v1 and from path A)

**"The Saturday that kept escalating."** v1 was built on Saturday
afternoon's news (research window ~17:30–18:00 UTC). This edition is
the Saturday-evening update: the day's biggest story happened AFTER
v1's research window — Iran's missile-and-drone strike on US bases
in Bahrain on Saturday night — so it leads the page. Same winner
skeleton, different news judgement: Bahrain hero 1, Peru hero 2,
COP31 hero 3; Riyadh demoted from hero to medium; two brand-new
stories (Bahrain, Sparta II) and one Friday story v1 missed entirely
(Kryvyi Rih).

## Audit of v1 (all verified by web search, 22 Nov 2026)

### Stories v1 MISSED
| Story | When | Evidence |
| --- | --- | --- |
| Iran strikes US bases in Bahrain (IRGC missiles + drones on al-Riffa and Awali; Tehran claims 2 Patriot radars destroyed; Bahrain: civilian site hit, no injuries) | Sat night 21 Nov | Reuters, Al Jazeera, IRNA/Sepah News, Bahrain MoI/Defence Force. New rank-1 entry leads with it. |
| Russian cargo ship Sparta II hit by 2 Ukrainian drones, ablaze in Gulf of Finland; 16 crew evacuated; Finland says likely Ukraine | Sat 21 Nov ~09:00 local | Reuters, CNN, ISW, AP. Ship owned by US-sanctioned Oboronlogistika. |
| Kryvyi Rih "triple-tap": 2 ballistic missiles then drones on rescuers; 7-year-old boy + 20-year-old paramedic killed, ~60 wounded, 25 buildings damaged | Fri evening 20 Nov | AP, CNN, Ukrainian officials. A Friday-evening story v1 missed entirely — not even in DATE CHECK. |

### Date errors in v1 (event date, not article date — the hard rule)
| v1 story | v1 said | Actually | Fix in v2 |
| --- | --- | --- | --- |
| Denmark backs US-Greenland deal 109-0 | Sat 21 Nov | **Thu 19 Nov** (Folketing vote) | Moved to DATE CHECK |
| Gaza: 22,000 children killed | Sat 21 Nov | **Thu 19 Nov** (Foreign Ministry statement ahead of World Children's Day; source was the Foreign Ministry, not the Health Ministry) | Moved to DATE CHECK |
| Mongolia's president resigns | Sat 21 Nov | **Thu 19 Nov** (parliament approved; announced Tue 17 Nov) | Moved to DATE CHECK |
| Poland asks NATO for more air defences | Sat 21 Nov | **Fri 20 Nov** (Defence Minister's Friday press conference) | Date fixed, kept as Friday-carried |
| WHO: Congo Ebola still global emergency | Sat 21 Nov | **Fri 20 Nov** (WHO Disease Outbreak News published 20 Nov; data as of 17 Nov) | Date fixed, kept as Friday-carried |
| Italy clears Tesla self-driving | Sat 21 Nov | **Fri 20 Nov** (Salvini announced Friday; Reuters 20 Nov) | Date fixed, kept as Friday-carried |
| Judge backs $7.25bn Roundup payout | Sat 21 Nov | **Fri 20 Nov** (Missouri judge approved Friday; Reuters/AP 20 Nov) | Date fixed, kept as Friday-carried |
| Peru quake | Sat 21 Nov | **Fri 19:09 local** (00:09 UTC Sat) | Date fixed to 2026-11-20 |
| Spain heads to 29 Nov election | Sat 21 Nov | Election was **called 5 Oct**; the Saturday event is Sánchez's Canary Islands campaign rally | Headline reframed to the rally (Sat 21 Nov) |

### Figure / deck corrections
- **Peru:** v1's "no deaths, 1 injured, 34 houses damaged" was the
  preliminary overnight tally. Later INDECI report (18:00, 21 Nov):
  **1 dead, 16 injured, 152 homes uninhabitable** (Minsa COES
  confirms the hospital death in Huánuco). v2 uses the later figures.
- **COP31 overtime:** v1 "21+" → v2 **"24+"** (Health Policy Watch:
  "more than 24 hours into overtime" Saturday evening; a compromise
  text was tabled at a late-night plenary, approval session Sunday).
- **Geneva killer robots:** v1's deck said "rules … eyed by 2028".
  The 128 nations agreed to *elaborate* an instrument over two
  years; no binding treaty was agreed and campaigners called the
  mandate watered down. v2 deck says so.
- **Riyadh:** core verified (3 missiles, 02:41 AST, 2 blasts heard,
  drone downed 04:24 AST; second attack in days after the PIF Tower
  hit Thu 19 Nov).

### Facts re-verified and kept
- Markets Friday close: S&P **6,910.39, −3.70%**, seventh straight
  loss, correction territory; Nasdaq **−5.28%** to 22,617.73, 2026
  gains wiped out; Nvidia **−14.01%** on the Reuters SEC-probe
  report (Motley Fool, investinglive, AInvest).
- Daraxonrasib (presented Fri 20 Nov, ENA Barcelona): 61 patients,
  **60.7%** objective response, **8.2%** complete response (5 of 61),
  **90.2%** disease control, median PFS 12.8 months (ecancer,
  OncoDaily, Fox News).
- WHO Ebola: **11,613** confirmed cases, **5,678** deaths, CFR 48.9%
  (WHO Disease Outbreak News, 20 Nov 2026).
- Geneva: 128 nations, agreement reached **04:45 CET Saturday**,
  two-year mandate (Swiss FDFA, TechXplore, AP).
- Florida floods: Saturday story is the ongoing flood + more rain
  expected (NWS); the "28 inches" figure is from 2/17–19 Nov, not
  Saturday — not used.

### Visual weaknesses in v1 (fixed in v2)
- Hero art bands thin (52px) → **56px**, wider scenes.
- Medium icons small (40px) → **44px**.
- Numbers strip only 6 figures → **8 figures** (added "2 US Patriot
  radars IRGC claims hit" and "16 Sparta II crew evacuated").
- Timeline 5 items → **6 items** (added Geneva 03:45 UTC, Sparta II
  07:00 UTC, Bahrain Sat night).
- Map 112px → **100px** with an isotropic dot grid (v1's grid
  rendered as vertical stripes at this aspect ratio — fixed) and
  spiral de-collision for all 13 pins. On-map region labels were
  tried and dropped in QA: they collided with pins; the region bar
  already carries all 7 regions.
- No confidence information → **CONFIRMED / CLAIMED / REPORTED
  tag on all 13 featured cards** (rank-5 quiet-panda-11 tags
  certainty per story; this matches that feature).
- Also-list: Alcaraz and Trump-Iran demoted from mediums (Trump-Iran
  is superseded by the actual Bahrain strike; Alcaraz is a sports
  result) to make room for Riyadh and Sparta II as mediums.

## Layout (1024×1024, final y = 1008)

Eyebrow → Gloock 38pt date masthead → red italic subline → 7-segment
region bar (widths ∝ story counts, 42px minimum for 1-story
segments so every label fits) → THE DAY IN NUMBERS (8 figures) →
SATURDAY BY THE HOURS timeline (6 items) → 3 hero cards (56px art
band + place + confidence tag + headline + deck + source) → MORE OF
THE DAY, 10 medium cards (2 cols × 5, 44px rows, 44px icon) →
dotted world map (pins 1–13, grey dots 14–35) → ALSO TODAY, 22
numbered briefs (3 cols) → DATE CHECK box (12 refused stories) →
NOT YET line → sources footer.

Palette: cream paper (246,239,221), navy ink (24,48,88), one red
accent (180,35,24). Fonts (OFL): Gloock masthead, Crimson Pro
headlines/decks, Instrument Sans UI, IBM Plex Mono labels.

## Illustrations (all code-drawn, Pillow; 2 brand-new)

13 flat-vector illustrations, each rendered at 2–3× and downscaled:
Bahrain night strike (NEW: radar dish, missile streaks, explosion
burst, interceptor) · Peru mountains + clean seismograph waveform ·
COP31 globe + thermometer + overtime clock · BepiColombo spacecraft
+ Mercury · Nasdaq falling chart · MQ-9 drone + red X · Danish flag
+ exit door · daraxonrasib capsule + shrinking cells · killer-robot
head + gear · Mexico handcuffs + star badge · FBI shield +
magnifier · Riyadh night skyline + intercept streaks · Sparta II
ship + fire (NEW). No raster assets, no AI images.

## Story inventory (35 stories, 7 regions)

Heroes: Bahrain (MIDEAST), Peru (AMERICAS), COP31 (WORLD).
Mediums: BepiColombo, Nasdaq, MQ-9, Denmark attaché, Daraxonrasib,
Geneva, Mexico, FBI, Riyadh, Sparta II.
Also-list 14–35: Poland, Kryvyi Rih, Trump-defund-Ukraine,
Palisades, Florida, Anthropic, IAEA Yongbyon, Sánchez rally,
Italy Tesla, Roundup, contractor gag order, arch blocked, cyber
director fired, CISA VMware, port watchmen, Nigeria Gombe, WHO
Ebola, S. Africa, APEC ceasefire, North Melbourne AFLW, Alcaraz,
Trump-Iran.
Regions: AMERICAS 15, EUROPE 10, MIDEAST 3, AFRICA 3, OCEANIA 2,
ASIA-PACIFIC 1, WORLD 1.

## Skills used (audited, actually used — not just installed)

- **news_image_page** (local skill): the method + winner template.
  Followed end to end.
- **makefun_bounty_submission** (local skill): quota-first, fresh
  kit, bundle flags, Node 24 network, review-before-submit
  (auto-submit authorised by the user 22 Nov 12:38 WIB for
  News-21; this subagent does NOT submit — the parent bundles,
  checks and submits).
- **canvas-design** (local skill): OFL fonts used for all type.
- **Pillow (python-pillow/Pillow)** — **14,004 stars** on GitHub
  (verified via `gh api` 22 Nov by the v1 builder), licence HPND
  (OSI-approved). Pure imaging library, already installed
  (10.2.0), no network, no credentials, no untrusted input —
  SAFE. It is the renderer for the whole page.

## Skills searched and rejected

Same conclusion as v1 (see DESIGN.md): no new external GitHub
skill above 500 stars fits this task better than the proven local
method; the >500★ dependency actually used is Pillow (14,004★,
audited, safe). No other skill was installed or used in this
session.

## QA log (v2-alt)

1. First render: final_y=1000, no warnings. Full-size view: layout
   clean, all sections legible.
2. Zoom-QA found the map's dot grid rendered as vertical stripes
   (24 rows over 92px: dots merged vertically). Fixed with an
   isotropic 8px square grid sampling the landmask per dot; map
   height 92→100px. Re-checked: continents read clearly.
3. Zoom-QA found the Peru seismograph was a dense red scribble
   covering the band. Fixed: one clean waveform (baseline + ~20
   points, S-wave spike in the middle), darker mountain ranges.
   Re-checked: mountains + waveform read clearly.
4. Zoom-QA found the Bahrain radar dish unreadable. Fixed:
   brightened and thickened the dish. Re-checked: dish, streaks
   and explosion burst all read.
5. Zoom-QA found on-map region labels colliding with pins and
   washed out over dots. Dropped the labels (region bar already
   carries all 7 regions with counts).
6. Zoom-QA found the BepiColombo spacecraft too small in its
   icon. Enlarged body/panels/dish. Re-checked.
7. Final render: final_y=1008, 232,522 bytes, md5
   bb58d46101e8523532bc890de0a3815e. Full-size + 2× crops of the
   map, both hero bands, mediums and the bottom verified: zero
   defects (no cut-off text, no pin/brief number mismatch, all
   figures match the verified sources, DATE CHECK complete).
8. `main.ts` tested locally (Node v24, MAKEFUN_OUTPUT_DIR set):
   writes entry.png byte-identical (same md5). The
   MODULE_TYPELESS_PACKAGE_JSON warning is the same harmless one
   noted in the v1 check report.

## Honest odds

v1's honest assessment stands: the contest is a lottery among ~50
pages in the 98.8–99.2 band, and top-1 needs a max-quality page
AND pairwise luck. v2-alt's edge over v1: it carries the Saturday
night's biggest story (Bahrain) that v1 and most early entries
missed, it fixes three Thursday stories v1 wrongly carried as
Saturday (the exact date-rule trap the judge penalises), it
updates the Peru toll to the later official figures, and it adds
confidence tags + a denser numbers strip. If the judge rewards
freshness and date discipline, v2-alt should beat v1; top-50 is
realistic, top-1 is still roughly 1-in-30 to 1-in-50.
