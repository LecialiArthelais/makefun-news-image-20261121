#!/usr/bin/env python3
"""Render the news-image-20261121 front page v2 (1024x1024) from stories_v2.json.

Fresh implementation written in this session for the v2 rebuild (jalur A).
All illustrations are flat-vector shapes drawn in code with Pillow; no raster
assets, no network, no AI generation. Deterministic output.

v2 fixes vs v1: Iran strike is hero #1; Peru hero carries the corrected
00:09 UTC time and the updated INDECI toll (1 dead, 16 hurt); Friday's
Nasdaq close is demoted to DATE CHECK; "Trump weighs new strikes on Iran"
is dropped (superseded by the actual strike); light dotted map so pins
read; confidence badges on every card; HOW WE CHECKED box; bigger medium
art; 9-region bar with a full legend; 35 stories, all event-dated.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.expanduser("~/workspace/custom-skills/canvas-design/canvas-fonts")

# Palette — cream paper, navy ink, one red accent.
PAPER    = (246, 239, 221)
INK      = (24, 48, 88)
INK_SOFT = (58, 74, 102)
RED      = (180, 35, 24)
RED_LT   = (226, 82, 62)
GOLD     = (196, 141, 38)
TEAL     = (23, 120, 110)
GREEN    = (46, 125, 62)
PURPLE   = (104, 78, 150)
AMBER    = (178, 118, 20)
GREY     = (110, 110, 105)
LINE     = (203, 192, 172)
CARD     = (255, 252, 244)
MAPBG    = (233, 229, 211)
MAPDOT   = (24, 48, 88)
MAPDOT_LT = (150, 148, 138)
WHITE    = (255, 255, 255)
BLACK    = (20, 20, 20)

W, H = 1024, 1024
M = 16                      # page margin
CW = W - 2 * M              # content width = 992

BADGE_FILL = {
    "CONFIRMED": GREEN,
    "OFFICIAL": INK,
    "REPORTED": AMBER,
    "CLAIM": RED,
}
BADGE_MARK = {
    "CONFIRMED": "✓ CONFIRMED",
    "OFFICIAL": "OFFICIAL",
    "REPORTED": "REPORTED",
    "CLAIM": "CLAIM",
}

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

F = {
    "mast":   lambda s: font("Gloock-Regular.ttf", s),
    "serif":  lambda s: font("CrimsonPro-Regular.ttf", s),
    "serif_b": lambda s: font("CrimsonPro-Bold.ttf", s),
    "serif_i": lambda s: font("CrimsonPro-Italic.ttf", s),
    "sans":   lambda s: font("InstrumentSans-Regular.ttf", s),
    "sans_b": lambda s: font("InstrumentSans-Bold.ttf", s),
    "sans_i": lambda s: font("InstrumentSans-Italic.ttf", s),
    "mono":   lambda s: font("IBMPlexMono-Regular.ttf", s),
    "mono_b": lambda s: font("IBMPlexMono-Bold.ttf", s),
}

def wrap(d, s, f, max_w):
    """Greedy word wrap; returns list of lines."""
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def trunc(d, s, f, max_w):
    """Shorten s with an ellipsis until it fits max_w."""
    if d.textlength(s, font=f) <= max_w:
        return s
    while s and d.textlength(s + "…", font=f) > max_w:
        s = s[:-1]
    return s + "…"

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def hline(d, x0, x1, y, color=LINE, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)

# ---------------------------------------------------------------- map
# Simplified continent outlines (lon, lat), drawn as a dot matrix.
# Hand-written for this entry; coarse shapes are fine at 5px dot spacing.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-75, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 44), (-75, 39),
     (-80, 32), (-81, 26), (-87, 30), (-90, 21), (-97, 16), (-105, 20),
     (-110, 24), (-117, 33), (-124, 40), (-125, 49), (-135, 58),
     (-150, 61), (-158, 58), (-165, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-32, 68), (-22, 70), (-25, 76), (-40, 76),
     (-55, 74), (-58, 64)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-41, -3),
     (-35, -8), (-39, -15), (-41, -23), (-48, -28), (-57, -35), (-65, -41),
     (-69, -47), (-73, -50), (-73, -40), (-71, -30), (-70, -18),
     (-76, -14), (-80, -5), (-81, 1), (-79, 9)],
    # Africa
    [(-17, 15), (-16, 24), (-10, 31), (-2, 35), (10, 37), (20, 32),
     (32, 31), (35, 28), (39, 21), (43, 12), (51, 11), (46, 4),
     (41, -4), (40, -11), (36, -18), (33, -26), (27, -33), (19, -34),
     (15, -27), (12, -17), (13, -10), (9, 4), (0, 6), (-8, 5),
     (-13, 9), (-17, 15)],
    # Europe
    [(-10, 37), (-9, 43), (-2, 48), (0, 50), (4, 53), (8, 57), (6, 62),
     (13, 66), (19, 70), (26, 71), (31, 70), (38, 67), (42, 65), (35, 62),
     (28, 59), (24, 58), (19, 55), (14, 54), (9, 55), (5, 58), (2, 55),
     (-2, 51), (-5, 48), (-4, 44), (-9, 38), (-10, 37)],
    # Asia
    [(30, 36), (36, 36), (43, 39), (48, 37), (51, 29), (57, 26), (62, 25),
     (68, 23), (72, 20), (77, 13), (80, 8), (84, 19), (89, 22), (93, 18),
     (97, 15), (100, 9), (103, 2), (106, 9), (109, 14), (108, 18),
     (111, 21), (116, 23), (120, 27), (122, 32), (124, 39), (127, 40),
     (131, 43), (136, 45), (141, 50), (143, 56), (150, 60), (158, 63),
     (165, 66), (172, 67), (178, 66), (170, 69), (160, 70), (150, 72),
     (140, 73), (130, 72), (120, 73), (110, 74), (100, 76), (90, 75),
     (80, 73), (70, 72), (60, 69), (50, 68), (40, 68), (32, 68),
     (30, 66), (30, 36)],
    # Australia
    [(113, -22), (115, -32), (118, -35), (124, -33), (130, -32), (135, -35),
     (140, -38), (146, -39), (150, -37), (153, -31), (151, -24),
     (147, -19), (143, -14), (141, -12), (136, -12), (131, -12),
     (126, -14), (122, -17), (117, -20), (113, -22)],
    # New Zealand
    [(167, -45), (170, -43), (174, -41), (177, -38), (178, -37),
     (175, -38), (172, -41), (168, -44), (167, -45)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (1, 51), (-1, 50),
     (-5, 50)],
    # Japan
    [(130, 31), (133, 34), (136, 35), (139, 36), (141, 39), (142, 43),
     (141, 44), (139, 40), (137, 36), (134, 34), (131, 32), (130, 31)],
    # Madagascar
    [(44, -16), (48, -15), (50, -17), (48, -22), (45, -25), (43, -21),
     (44, -16)],
    # Indonesia
    [(95, 5), (100, -2), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -8), (130, -3), (135, -4), (140, -8), (95, 5)],
]

def _point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xint = (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi
            if x < xint:
                inside = not inside
        j = i
    return inside

def draw_map(d, box, pins, grey_dots):
    """Dot-matrix world map on a light panel. pins: list of (lon, lat, n)."""
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    # equirectangular, lat range 74..-56
    def proj(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * mw
        py = y0 + (74.0 - lat) / 130.0 * mh
        return px, py
    step = 5
    for poly in CONTINENTS:
        lons = [p[0] for p in poly]
        lats = [p[1] for p in poly]
        gx0, gy0 = proj(min(lons), max(lats))
        gx1, gy1 = proj(max(lons), min(lats))
        gy = gy0
        while gy <= gy1:
            gx = gx0
            while gx <= gx1:
                lon = (gx - x0) / mw * 360.0 - 180.0
                lat = 74.0 - (gy - y0) / mh * 130.0
                if _point_in_poly(lon, lat, poly):
                    r = 1.4
                    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=MAPDOT)
                gx += step
            gy += step
    # grey dots for brief stories
    for lon, lat in grey_dots:
        px, py = proj(lon, lat)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=MAPDOT_LT)
    # numbered pins: spiral search for a free slot, leader line to true spot
    placed = []
    for lon, lat, n in pins:
        px, py = proj(lon, lat)
        dx, dy = 0, 0
        for radius in (0, 14, 20, 27, 34, 42):
            done = False
            for ang in range(0, 360, 45):
                ox = radius * math.cos(math.radians(ang))
                oy = radius * math.sin(math.radians(ang))
                nx, ny = px + ox, py + oy
                if not (x0 + 9 <= nx <= x1 - 9 and y0 + 9 <= ny <= y1 - 9):
                    continue
                if all((nx - qx) ** 2 + (ny - qy) ** 2 >= 17 ** 2
                       for qx, qy in placed):
                    dx, dy = ox, oy
                    done = True
                    break
            if done:
                break
        cx, cy = px + dx, py + dy
        placed.append((cx, cy))
        if dx or dy:
            d.line([(px, py), (cx, cy)], fill=INK, width=1)
        r = 7.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=1)
        f = F["sans_b"](9)
        tw = d.textlength(str(n), font=f)
        d.text((cx - tw / 2, cy - 6), str(n), font=f, fill=WHITE)

# ------------------------------------------------------- illustrations
# Each draws one flat-vector illustration inside box (x0,y0,x1,y1).
# No raster assets, no text inside the art except single glyphs.

def art_iran(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(28, 42, 74))
    # stars
    for sx, sy, r in [(0.12, 0.15, 1.5), (0.35, 0.08, 1), (0.6, 0.18, 1.5),
                      (0.85, 0.1, 1), (0.92, 0.35, 1.5), (0.05, 0.4, 1)]:
        d.ellipse([x0 + (x1 - x0) * sx - r, y0 + (y1 - y0) * sy - r,
                   x0 + (x1 - x0) * sx + r, y0 + (y1 - y0) * sy + r], fill=WHITE)
    # moon
    d.ellipse([x0 + 8, y0 + 8, x0 + 24, y0 + 24], fill=(240, 230, 180))
    # gulf sea
    sy = y1 - 22
    d.rectangle([x0, sy, x1, y1], fill=(36, 90, 110))
    for i in range(3):
        wy = sy + 6 + i * 5
        d.arc([x0 - 8 + i * 5, wy - 4, x1 + 8, wy + 5], 0, 180, fill=(140, 190, 205), width=2)
    # tanker on the sea
    tx0, tx1 = x0 + (x1 - x0) * 0.55, x0 + (x1 - x0) * 0.92
    d.rectangle([tx0, sy - 8, tx1, sy + 2], fill=(180, 60, 40))
    d.rectangle([tx0 + 6, sy - 16, tx0 + 16, sy - 8], fill=(200, 200, 200))
    d.line([(tx0 + 10, sy - 16), (tx0 + 10, sy - 22)], fill=(200, 200, 200), width=2)
    # missile streaks arcing down to the bases
    for (sx, sy2, ex, ey) in [(0.15, 0.12, 0.30, 0.62), (0.45, 0.08, 0.60, 0.62),
                              (0.75, 0.15, 0.82, 0.62)]:
        px, py = x0 + (x1 - x0) * sx, y0 + (y1 - y0) * sy2
        qx, qy = x0 + (x1 - x0) * ex, y0 + (y1 - y0) * ey
        d.line([(px, py), (qx, qy)], fill=RED_LT, width=3)
        d.line([(px, py), (qx, qy)], fill=WHITE, width=1)
        d.ellipse([qx - 3, qy - 3, qx + 3, qy + 3], fill=WHITE)
        d.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], outline=GOLD, width=2)
    # base blocks on the shore
    for bx in (0.22, 0.52, 0.74):
        bx0 = x0 + (x1 - x0) * bx
        d.rectangle([bx0, sy - 12, bx0 + 12, sy], fill=(58, 74, 110))

def art_peru(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 214, 176))
    # sun
    d.ellipse([x0 + 12, y0 + 8, x0 + 28, y0 + 24], fill=GOLD)
    # mountains
    base = y1 - 10
    d.polygon([(x0, base), (x0 + (x1 - x0) * 0.28, y0 + 22), (x0 + (x1 - x0) * 0.55, base)],
              fill=(96, 84, 66))
    d.polygon([(x0 + (x1 - x0) * 0.35, base), (x0 + (x1 - x0) * 0.68, y0 + 10),
               (x1, base)], fill=(66, 58, 44))
    d.polygon([(x0 + (x1 - x0) * 0.60, y0 + 24), (x0 + (x1 - x0) * 0.68, y0 + 10),
               (x0 + (x1 - x0) * 0.76, y0 + 24)], fill=WHITE)
    # crack in the slope
    cx = x0 + (x1 - x0) * 0.30
    d.line([(cx, y0 + 40), (cx + 6, y0 + 52), (cx - 2, y0 + 64), (cx + 4, y0 + 76)],
           fill=RED, width=2)
    # seismograph zigzag
    zy = y1 - 26
    pts = [(x0 + 8, zy), (x0 + 20, zy), (x0 + 26, zy - 8), (x0 + 32, zy + 8),
           (x0 + 38, zy - 14), (x0 + 44, zy + 12), (x0 + 52, zy),
           (x1 - 8, zy)]
    d.line(pts, fill=RED, width=2, joint="curve")

def art_cop31(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(206, 228, 224))
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2 + 4, min(x1 - x0, y1 - y0) * 0.42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    for k, ry in enumerate((0.45, 0.75, 1.05)):
        d.arc([cx - r, cy - r * ry, cx + r, cy + r * ry], 200, 340, fill=WHITE, width=2)
    d.arc([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r], 90, 270, fill=WHITE, width=2)
    # thermometer rising over the globe
    tx = x1 - 16
    d.rounded_rectangle([tx - 5, y0 + 8, tx + 5, y1 - 14], radius=5, fill=WHITE, outline=INK, width=2)
    d.ellipse([tx - 8, y1 - 20, tx + 8, y1 - 4], fill=RED, outline=INK, width=2)
    d.rectangle([tx - 2, y0 + 14, tx + 2, y1 - 14], fill=RED)
    # sun rays
    sx, sy = x0 + 14, y0 + 12
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(sx + dx * 6, sy + dy * 6), (sx + dx * 11, sy + dy * 11)], fill=GOLD, width=2)
    d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=GOLD)

def art_riyadh(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(30, 38, 66))
    # moon
    d.ellipse([x0 + 10, y0 + 8, x0 + 26, y0 + 24], fill=(240, 230, 180))
    # skyline
    base = y1 - 8
    towers = [(0.05, 0.55, 0.16), (0.20, 0.75, 0.30), (0.34, 0.45, 0.44),
              (0.48, 0.85, 0.58), (0.62, 0.55, 0.72), (0.76, 0.70, 0.86),
              (0.88, 0.40, 0.97)]
    for a, h, b in towers:
        tx0, tx1 = x0 + (x1 - x0) * a, x0 + (x1 - x0) * b
        ty = base - (y1 - y0) * h
        d.rectangle([tx0, ty, tx1, base], fill=(58, 74, 110))
        for wy in range(int(ty) + 6, int(base) - 4, 10):
            d.rectangle([tx0 + 3, wy, tx0 + 6, wy + 3], fill=GOLD)
    # intercept streaks: three red lines with white heads
    for i, (sx, sy) in enumerate([(0.18, 0.30), (0.45, 0.18), (0.72, 0.28)]):
        px, py = x0 + (x1 - x0) * sx, y0 + (y1 - y0) * sy
        d.line([(px - 26, py + 14), (px, py)], fill=RED_LT, width=3)
        d.line([(px - 26, py + 14), (px, py)], fill=WHITE, width=1)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=WHITE)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], outline=RED, width=1)

def art_sparta(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 40, 62))
    # gulls / drones overhead
    for dx, dy in [(0.2, 0.18), (0.35, 0.10), (0.8, 0.15)]:
        cx, cy = x0 + (x1 - x0) * dx, y0 + (y1 - y0) * dy
        d.line([(cx - 7, cy), (cx, cy - 4), (cx + 7, cy)], fill=WHITE, width=2)
    # sea
    sy = y1 - 26
    d.rectangle([x0, sy, x1, y1], fill=(36, 90, 110))
    for i in range(2):
        wy = sy + 7 + i * 6
        d.arc([x0 - 8 + i * 5, wy - 4, x1 + 8, wy + 5], 0, 180, fill=(140, 190, 205), width=2)
    # cargo ship
    hx0, hx1 = x0 + (x1 - x0) * 0.12, x0 + (x1 - x0) * 0.88
    d.polygon([(hx0, sy - 14), (hx1, sy - 14), (hx1 - 8, sy + 4), (hx0 + 8, sy + 4)],
              fill=(70, 70, 70))
    for i, col in enumerate([(180, 60, 40), (40, 110, 70), (196, 141, 38)]):
        cx0 = hx0 + 8 + i * 20
        d.rectangle([cx0, sy - 26, cx0 + 16, sy - 14], fill=col, outline=INK, width=1)
    d.rectangle([hx1 - 16, sy - 30, hx1 - 6, sy - 14], fill=(200, 200, 200))
    # fire plume + smoke
    fx = x0 + (x1 - x0) * 0.42
    d.polygon([(fx - 8, sy - 26), (fx - 2, sy - 44), (fx + 4, sy - 30),
               (fx + 10, sy - 44), (fx + 12, sy - 26)], fill=(230, 120, 30))
    d.polygon([(fx - 4, sy - 26), (fx, sy - 36), (fx + 5, sy - 26)], fill=(250, 200, 60))
    for ox, oy, r in [(0.30, 0.30, 5), (0.42, 0.22, 7), (0.55, 0.28, 5)]:
        cx, cy = x0 + (x1 - x0) * ox, y0 + (y1 - y0) * oy
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 120))

def art_cepa(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 240, 234))
    # EU flag (blue + circle of gold stars)
    ex0, ey0, ex1, ey1 = x0 + 8, y0 + 12, x0 + 40, y0 + 34
    d.rectangle([ex0, ey0, ex1, ey1], fill=(0, 51, 153))
    ecx, ecy = (ex0 + ex1) / 2, (ey0 + ey1) / 2
    for a in range(0, 360, 30):
        sx = ecx + 10 * math.cos(math.radians(a))
        sy = ecy + 6 * math.sin(math.radians(a))
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=GOLD)
    # Indonesia flag (red over white)
    ix0, iy0, ix1, iy1 = x1 - 40, y0 + 12, x1 - 8, y0 + 34
    d.rectangle([ix0, iy0, ix1, (iy0 + iy1) / 2], fill=(200, 16, 46))
    d.rectangle([ix0, (iy0 + iy1) / 2, ix1, iy1], fill=WHITE, outline=INK, width=1)
    # gold trade arrows meeting in the middle
    mx = (x0 + x1) / 2
    d.line([(ex1 + 2, ey0 + 11), (mx - 4, ey0 + 11)], fill=GOLD, width=3)
    d.polygon([(mx - 4, ey0 + 6), (mx - 4, ey0 + 16), (mx + 3, ey0 + 11)], fill=GOLD)
    d.line([(ix0 - 2, iy0 + 11), (mx + 4, iy0 + 11)], fill=GOLD, width=3)
    d.polygon([(mx + 4, iy0 + 6), (mx + 4, iy0 + 16), (mx - 3, iy0 + 11)], fill=GOLD)
    # containers below
    by = y1 - 26
    for i, col in enumerate([(180, 60, 40), (23, 120, 110), (196, 141, 38), (24, 48, 88)]):
        cx0 = x0 + 10 + i * 20
        d.rectangle([cx0, by, cx0 + 16, by + 16], fill=col, outline=INK, width=1)
        d.line([(cx0 + 5, by), (cx0 + 5, by + 16)], fill=INK, width=1)
        d.line([(cx0 + 11, by), (cx0 + 11, by + 16)], fill=INK, width=1)

def art_mexico(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 234, 214))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # handcuffs
    for hx in (cx - 24, cx + 24):
        d.ellipse([hx - 13, cy - 13, hx + 13, cy + 13], outline=INK, width=4)
    d.line([(cx - 11, cy), (cx + 11, cy)], fill=INK, width=3)
    for i in range(3):
        lx = cx - 8 + i * 8
        d.line([(lx, cy - 4), (lx, cy + 4)], fill=INK, width=2)
    # star badge
    bx, by = x0 + (x1 - x0) * 0.82, y0 + (y1 - y0) * 0.20
    d.polygon([(bx, by - 8), (bx + 2.5, by - 2.5), (bx + 8, by - 2),
               (bx + 4, by + 2.5), (bx + 5.5, by + 8), (bx, by + 4.5),
               (bx - 5.5, by + 8), (bx - 4, by + 2.5), (bx - 8, by - 2),
               (bx - 2.5, by - 2.5)], fill=GOLD, outline=INK, width=1)

def art_robot(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(228, 232, 238))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 2
    # antenna
    d.line([(cx, cy - 26), (cx, cy - 36)], fill=INK, width=2)
    d.ellipse([cx - 4, cy - 42, cx + 4, cy - 34], fill=RED)
    # head
    d.rounded_rectangle([cx - 26, cy - 26, cx + 26, cy + 18], radius=8,
                        fill=(150, 160, 175), outline=INK, width=2)
    # eyes: one normal, one red X
    d.ellipse([cx - 18, cy - 12, cx - 6, cy], fill=WHITE, outline=INK, width=1)
    d.ellipse([cx - 15, cy - 9, cx - 9, cy - 3], fill=INK)
    d.line([(cx + 7, cy - 11), (cx + 17, cy - 1)], fill=RED, width=3)
    d.line([(cx + 17, cy - 11), (cx + 7, cy - 1)], fill=RED, width=3)
    # mouth grille
    for i in range(3):
        d.line([(cx - 12 + i * 9, cy + 8), (cx - 12 + i * 9, cy + 13)], fill=INK, width=2)
    # gear
    gx, gy = x1 - 16, y1 - 16
    d.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], fill=GOLD, outline=INK, width=2)
    d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=PAPER)

def art_bitcoin(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 242, 224))
    cx, cy, r = (x0 + x1) / 2 - 14, (y0 + y1) / 2 - 4, 24
    # coin
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=INK, width=2)
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=WHITE, width=1)
    f = F["sans_b"](30)
    tw = d.textlength("B", font=f)
    d.text((cx - tw / 2, cy - 19), "B", font=f, fill=WHITE)
    # chart: plunge then rebound
    pts = [(x0 + 8, y0 + 62), (x0 + 26, y0 + 58), (x0 + 44, y0 + 70),
           (x0 + 62, y0 + 76), (x0 + 78, y0 + 66), (x1 - 8, y0 + 56)]
    d.line(pts, fill=RED, width=2, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax - 7, ay + 2), (ax - 1, ay - 6), (ax + 2, ay + 5)], fill=GREEN)
    d.line([(x0 + 62, y0 + 76), (x1 - 8, y0 + 56)], fill=GREEN, width=2)

def art_basra(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(52, 44, 40))
    # smoke clouds
    for ox, oy, r in [(0.25, 0.2, 8), (0.45, 0.12, 10), (0.68, 0.22, 8)]:
        cx, cy = x0 + (x1 - x0) * ox, y0 + (y1 - y0) * oy
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 112, 104))
    # cooling towers
    base = y1 - 8
    for tx in (0.15, 0.45):
        tx0 = x0 + (x1 - x0) * tx
        d.polygon([(tx0, base), (tx0 + 6, y0 + 34), (tx0 + 22, y0 + 34),
                   (tx0 + 28, base)], fill=(90, 84, 78), outline=INK, width=1)
    # chimney with flame
    chx = x0 + (x1 - x0) * 0.78
    d.rectangle([chx, y0 + 26, chx + 10, base], fill=(120, 112, 104), outline=INK, width=1)
    d.polygon([(chx - 2, y0 + 26), (chx + 5, y0 + 12), (chx + 12, y0 + 26)],
              fill=(230, 120, 30))
    d.polygon([(chx + 1, y0 + 26), (chx + 5, y0 + 18), (chx + 9, y0 + 26)],
              fill=(250, 200, 60))
    # ground fire line
    d.line([(x0 + 6, base - 2), (x1 - 6, base - 2)], fill=(230, 120, 30), width=3)

def art_davao(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(196, 214, 226))
    # sun
    d.ellipse([x0 + 8, y0 + 8, x0 + 22, y0 + 22], fill=GOLD)
    # clouds
    for ox, oy in [(0.65, 0.15), (0.8, 0.3)]:
        cx, cy = x0 + (x1 - x0) * ox, y0 + (y1 - y0) * oy
        d.ellipse([cx - 10, cy - 4, cx + 10, cy + 4], fill=WHITE)
    # aircraft side view
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 8
    d.ellipse([cx - 34, cy - 8, cx + 34, cy + 8], fill=WHITE, outline=INK, width=2)
    d.polygon([(cx + 28, cy - 6), (cx + 42, cy - 14), (cx + 40, cy - 2)], fill=WHITE, outline=INK, width=1)
    d.polygon([(cx - 30, cy + 2), (cx - 40, cy + 12), (cx - 24, cy + 6)], fill=WHITE, outline=INK, width=1)
    d.polygon([(cx - 4, cy - 8), (cx + 8, cy - 20), (cx + 12, cy - 8)], fill=(180, 35, 24))
    for i in range(5):
        wx = cx - 20 + i * 9
        d.ellipse([wx, cy - 3, wx + 4, cy + 1], fill=INK)
    # engine fire spark + slide
    d.polygon([(cx + 18, cy + 8), (cx + 22, cy + 16), (cx + 26, cy + 8)], fill=(230, 120, 30))
    d.polygon([(cx - 8, cy + 8), (cx + 14, y1 - 16), (cx + 26, y1 - 16)],
              fill=(250, 200, 60), outline=INK, width=1)
    # runway
    d.rectangle([x0 + 4, y1 - 14, x1 - 4, y1 - 10], fill=(90, 90, 90))
    for i in range(4):
        d.line([(x0 + 14 + i * 20, y1 - 12), (x0 + 24 + i * 20, y1 - 12)],
               fill=WHITE, width=2)

def art_taiwan(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 240, 244))
    # falling candlesticks
    bw = (x1 - x0 - 16) / 5
    tops = [0.25, 0.35, 0.45, 0.58, 0.68]
    for i, t in enumerate(tops):
        bx0 = x0 + 8 + i * bw
        by = y0 + (y1 - y0) * t
        d.rectangle([bx0 + 3, by, bx0 + bw - 3, by + 14], fill=RED)
        d.line([(bx0 + bw / 2, by - 6), (bx0 + bw / 2, by + 20)], fill=RED, width=2)
    # descending trend arrow
    d.line([(x0 + 10, y0 + 20), (x1 - 14, y0 + 62)], fill=RED, width=3)
    ax, ay = x1 - 14, y0 + 62
    d.polygon([(ax, ay + 8), (ax - 8, ay - 2), (ax + 2, ay - 8)], fill=RED)
    # ban sign over the fall
    cx, cy, r = x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.30, 13
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=3)
    d.line([(cx - r + 3, cy + r - 3), (cx + r - 3, cy - r + 3)], fill=RED, width=3)
    # small green uptick at the end
    d.line([(x1 - 30, y1 - 12), (x1 - 12, y1 - 20)], fill=GREEN, width=2)
    d.polygon([(x1 - 12, y1 - 20), (x1 - 18, y1 - 18), (x1 - 13, y1 - 13)], fill=GREEN)

def art_rugby(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(64, 140, 74))
    # pitch lines
    d.line([(x0, y1 - 22), (x1, y1 - 22)], fill=WHITE, width=2)
    d.line([(x0, y0 + 18), (x1, y0 + 18)], fill=WHITE, width=1)
    for i in range(5):
        lx = x0 + 10 + i * 18
        d.line([(lx, y0 + 18), (lx, y1 - 22)], fill=(255, 255, 255), width=1)
    # goal posts
    px = x1 - 16
    d.line([(px, y0 + 8), (px, y0 + 30)], fill=WHITE, width=2)
    d.line([(px - 8, y0 + 8), (px - 8, y0 + 22)], fill=WHITE, width=2)
    d.line([(px + 8, y0 + 8), (px + 8, y0 + 22)], fill=WHITE, width=2)
    d.line([(px - 8, y0 + 22), (px + 8, y0 + 22)], fill=WHITE, width=2)
    # rugby ball
    cx, cy = (x0 + x1) / 2 - 6, (y0 + y1) / 2 + 6
    d.ellipse([cx - 26, cy - 13, cx + 26, cy + 13], fill=(150, 90, 40), outline=WHITE, width=2)
    d.arc([cx - 26, cy - 13, cx + 26, cy + 13], 250, 110, fill=WHITE, width=2)
    d.arc([cx - 26, cy - 13, cx + 26, cy + 13], 70, 290, fill=WHITE, width=2)
    # motion lines
    for wy in (cy - 20, cy - 26):
        d.line([(cx - 30, wy), (cx - 40, wy)], fill=WHITE, width=2)
    # score ticks: 5 tries
    for i in range(5):
        tx = x0 + 10 + i * 8
        d.line([(tx, y1 - 34), (tx, y1 - 28)], fill=GOLD, width=3)

ART = {
    "iran": art_iran, "peru": art_peru, "cop31": art_cop31,
    "riyadh": art_riyadh, "sparta": art_sparta, "cepa": art_cepa,
    "mexico": art_mexico, "robot": art_robot, "bitcoin": art_bitcoin,
    "basra": art_basra, "davao": art_davao, "taiwan": art_taiwan,
    "rugby": art_rugby,
}

ART_BG = {
    "iran": (28, 42, 74), "peru": (232, 214, 176), "cop31": (206, 228, 224),
    "riyadh": (30, 38, 66), "sparta": (24, 40, 62), "cepa": (238, 240, 234),
    "mexico": (240, 234, 214), "robot": (228, 232, 238), "bitcoin": (250, 242, 224),
    "basra": (52, 44, 40), "davao": (196, 214, 226), "taiwan": (238, 240, 244),
    "rugby": (64, 140, 74),
}

def draw_art(img, d, name, box):
    """Render an illustration at 96x96, then paste it scaled to fit box
    (square, centred) over a band filled with the art's background colour."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    tmp = Image.new("RGB", (96, 96), PAPER)
    td = ImageDraw.Draw(tmp)
    ART[name](td, (0, 0, 96, 96))
    s = min(w, h)
    art = tmp.resize((s, s), Image.LANCZOS)
    d.rectangle([x0, y0, x1, y1], fill=ART_BG[name])
    img.paste(art, (x0 + (w - s) // 2, y0 + (h - s) // 2))

# ---------------------------------------------------------------- layout
REGION_ORDER = [
    ("EUROPE", INK), ("MIDEAST", AMBER), ("AMERICAS", RED),
    ("AFRICA", GREEN), ("EAST ASIA", TEAL), ("SE ASIA", PURPLE),
    ("SOUTH ASIA", GOLD), ("OCEANIA", GREY), ("GLOBAL", (90, 90, 90)),
]

def section_label(d, x, y, text):
    f = F["mono_b"](10)
    d.text((x, y), text, font=f, fill=RED)
    tw = d.textlength(text, font=f)
    d.line([(x + tw + 8, y + 5), (M + CW, y + 5)], fill=LINE, width=1)
    return y + 13

def draw_check(d, x, y, color, s=8):
    """Hand-drawn check mark (no font dependency). Returns width used."""
    d.line([(x, y + s * 0.55), (x + s * 0.35, y + s * 0.9),
            (x + s, y + s * 0.1)], fill=color, width=2, joint="curve")
    return s + 3

def badge_pill(d, x_right, y, badge):
    """Filled badge pill, right-aligned at x_right. Returns left edge."""
    f = F["sans_b"](8)
    label = BADGE_MARK[badge]
    tw = d.textlength(label, font=f)
    w = tw + 12
    h = 13
    x0 = x_right - w
    rrect(d, [x0, y, x_right, y + h], 6, fill=BADGE_FILL[badge])
    d.text((x0 + 6, y + 2), label, font=f, fill=WHITE)
    return x0

def badge_text(d, x, y, badge):
    """Coloured badge word with a hand-drawn check; returns width used."""
    f = F["mono_b"](8)
    col = BADGE_FILL[badge]
    w = draw_check(d, x, y + 1, col, s=7)
    label = BADGE_MARK[badge]
    d.text((x + w, y), label, font=f, fill=col)
    return w + d.textlength(label, font=f)

def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10

    # eyebrow
    f_eye = F["mono"](10)
    left = "THE WORLD IN ONE PAGE"
    right = "35 STORIES  ·  9 REGIONS  ·  ALL TIMES UTC UNLESS MARKED"
    d.text((M, y), left, font=f_eye, fill=INK_SOFT)
    d.text((M + CW - d.textlength(right, font=f_eye), y), right,
           font=f_eye, fill=INK_SOFT)
    y += 14
    hline(d, M, M + CW, y, color=INK, width=2)
    y += 4

    # masthead — giant serif date
    f_mast = F["mast"](40)
    mast = data["masthead"]
    while d.textlength(mast, font=f_mast) > CW and f_mast.size > 28:
        f_mast = F["mast"](f_mast.size - 1)
    d.text((M, y), mast, font=f_mast, fill=INK)
    y += 42

    # red italic subline: the three leads
    f_sub = F["serif_i"](19)
    sub = data["subline"]
    while d.textlength(sub, font=f_sub) > CW and f_sub.size > 13:
        f_sub = F["serif_i"](f_sub.size - 1)
    d.text((M, y), sub, font=f_sub, fill=RED)
    y += 24

    # region bar with full legend
    f_rg = F["mono_b"](10)
    d.text((M, y), "REGIONS  ", font=f_rg, fill=RED)
    lx = M + d.textlength("REGIONS  ", font=f_rg)
    legend = "  ·  ".join(f"{n} {data['regions'][n]}" for n, _ in REGION_ORDER)
    d.text((lx, y), legend, font=F["sans"](9), fill=INK_SOFT)
    y += 12
    total = sum(data["regions"].values())
    bx = M
    bar_h = 16
    for name, col in REGION_ORDER:
        cnt = data["regions"][name]
        bw = CW * cnt / total
        d.rectangle([bx, y, bx + bw, y + bar_h], fill=col)
        f_lab = F["mono_b"](9)
        tw = d.textlength(str(cnt), font=f_lab)
        if tw + 4 <= bw:
            d.text((bx + (bw - tw) / 2, y + 3), str(cnt), font=f_lab, fill=WHITE)
        bx += bw
    y += bar_h + 4

    # THE DAY IN NUMBERS
    y = section_label(d, M, y, "THE DAY IN NUMBERS")
    nums = data["numbers"]
    col_w = CW / len(nums)
    f_val = F["sans_b"](20)
    f_lab = F["sans"](8)
    for i, it in enumerate(nums):
        cx = M + col_w * i
        d.text((cx, y), it["value"], font=f_val, fill=RED)
        for j, ln in enumerate(wrap(d, it["label"], f_lab, col_w - 8)[:2]):
            d.text((cx, y + 23 + j * 10), ln, font=f_lab, fill=INK_SOFT)
        if i:
            d.line([(cx - 6, y + 2), (cx - 6, y + 32)], fill=LINE, width=1)
    y += 34

    # timeline — one line, UTC
    f_t = F["mono_b"](10)
    f_tx = F["sans"](10)
    tx = M
    d.text((tx, y), "SATURDAY BY THE HOURS  ", font=f_t, fill=RED)
    tx += d.textlength("SATURDAY BY THE HOURS  ", font=f_t)
    for it in data["timeline"]:
        d.text((tx, y), it["time"], font=f_t, fill=RED)
        tx += d.textlength(it["time"], font=f_t) + 5
        d.text((tx, y), it["text"], font=f_tx, fill=INK)
        tx += d.textlength(it["text"], font=f_tx) + 14
    y += 14

    # hero cards
    y = section_label(d, M, y, "THE THREE BIG STORIES")
    gap = 10
    hw = (CW - 2 * gap) / 3
    hh = 148
    hy = y
    for i, s in enumerate(data["heroes"]):
        x0 = M + i * (hw + gap)
        x1 = x0 + hw
        rrect(d, [x0, hy, x1, hy + hh], 4, fill=CARD, outline=LINE, width=1)
        draw_art(img, d, s["art"], (x0 + 1, hy + 1, x1 - 1, hy + 59))
        ty = hy + 63
        f_pl = F["mono_b"](9)
        d.text((x0 + 10, ty), f"{s['n']} · {s['place']}", font=f_pl, fill=RED)
        badge_pill(d, x1 - 10, ty - 2, s["badge"])
        ty += 15
        f_h = F["serif_b"](15)
        for ln in wrap(d, s["headline"], f_h, hw - 20)[:2]:
            d.text((x0 + 10, ty), ln, font=f_h, fill=INK)
            ty += 17
        ty += 1
        f_dk = F["sans"](10)
        for ln in wrap(d, s["deck"], f_dk, hw - 20)[:2]:
            d.text((x0 + 10, ty), ln, font=f_dk, fill=INK_SOFT)
            ty += 11
        f_src = F["mono"](8)
        d.text((x0 + 10, hy + hh - 11), " · ".join(s["sources"]).upper(),
               font=f_src, fill=GREY)
    y = hy + hh + 6

    # medium cards
    y = section_label(d, M, y, "MORE OF THE DAY")
    mw = (CW - gap) / 2
    mh = 48
    for row in range(5):
        for col in range(2):
            s = data["mediums"][row * 2 + col]
            x0 = M + col * (mw + gap)
            x1 = x0 + mw
            ry = y + row * (mh + 3)
            rrect(d, [x0, ry, x1, ry + mh], 3, fill=CARD, outline=LINE, width=1)
            draw_art(img, d, s["art"], (x0 + 4, ry + 4, x0 + 44, ry + mh - 4))
            tx = x0 + 50
            f_h = F["sans_b"](12)
            d.text((tx, ry + 4), trunc(d, s["headline"], f_h, mw - 56),
                   font=f_h, fill=INK)
            f_dk = F["sans"](10)
            d.text((tx, ry + 19), trunc(d, s["deck"], f_dk, mw - 56),
                   font=f_dk, fill=INK_SOFT)
            f_src = F["mono"](8)
            meta = f"{s['place']}  ·  " + " · ".join(s["sources"]).upper() + "  ·  "
            d.text((tx, ry + 33), meta, font=f_src, fill=GREY)
            bx = tx + d.textlength(meta, font=f_src)
            badge_text(d, bx, ry + 33, s["badge"])
    y += 5 * (mh + 3) + 4

    # map — light dotted panel
    y = section_label(d, M, y, "WHERE IT HAPPENED  —  1–13 FEATURED, 14–35 IN BRIEFS")
    map_h = 88
    rrect(d, [M, y, M + CW, y + map_h], 4, fill=MAPBG)
    pins = [(s["lon"], s["lat"], s["n"]) for s in data["heroes"] + data["mediums"]]
    grey = [(s["lon"], s["lat"]) for s in data["briefs"]]
    draw_map(d, (M + 6, y + 6, M + CW - 6, y + map_h - 6), pins, grey)
    y += map_h + 6

    # briefs — numbered, two columns, headline + detail on one line
    y = section_label(d, M, y, "THE REST OF THE DAY")
    cols = 2
    col_w = (CW - 16) / cols
    f_n = F["mono_b"](10)
    f_h = F["sans_b"](10)
    f_dk = F["sans"](10)
    for i, s in enumerate(data["briefs"]):
        col = i % cols
        row = i // cols
        x0 = M + col * (col_w + 16)
        ay = y + row * 13
        d.text((x0, ay), str(s["n"]), font=f_n, fill=RED)
        hx = x0 + 24
        hl = s["headline"]
        d.text((hx, ay), hl, font=f_h, fill=INK)
        dx = hx + d.textlength(hl, font=f_h)
        detail = " — " + s["detail"]
        d.text((dx, ay), trunc(d, detail, f_dk, x0 + col_w - dx),
               font=f_dk, fill=INK_SOFT)
    y += 11 * 13 + 6

    # DATE CHECK + HOW WE CHECKED, side by side
    box_h = 70
    dc_w = 620
    rrect(d, [M, y, M + dc_w, y + box_h], 4, fill=CARD, outline=RED, width=1)
    f_dc = F["mono_b"](10)
    d.text((M + 10, y + 8), "DATE CHECK — NOT SATURDAY", font=f_dc, fill=RED)
    f_it = F["sans"](9)
    f_wh = F["mono_b"](8)
    items = data["date_check"]
    for i, it in enumerate(items):
        col = i % 2
        row = i // 2
        x0 = M + 10 + col * 300
        ay = y + 24 + row * 11
        d.text((x0, ay), "· " + trunc(d, it["text"], f_it, 300 - 52),
               font=f_it, fill=INK_SOFT)
        d.text((x0 + 300 - 48, ay), it["when"], font=f_wh, fill=RED)
    hx0 = M + dc_w + 10
    hx1 = M + CW
    rrect(d, [hx0, y, hx1, y + box_h], 4, fill=CARD, outline=LINE, width=1)
    d.text((hx0 + 10, y + 8), "HOW WE CHECKED", font=f_dc, fill=RED)
    d.text((hx1 - 10 - d.textlength("DATES ARE EVENT DATES", F["sans_i"](9)), y + 8),
           "DATES ARE EVENT DATES", font=F["sans_i"](9), fill=INK_SOFT)
    defs = [
        ("CONFIRMED", "two or more independent outlets"),
        ("OFFICIAL", "government, agency or on-the-record statement"),
        ("REPORTED", "one outlet"),
        ("CLAIM", "one side, unconfirmed"),
    ]
    for j, (badge, definition) in enumerate(defs):
        ay = y + 24 + j * 11
        w = badge_text(d, hx0 + 10, ay, badge)
        d.text((hx0 + 10 + w + 4, ay), "— " + definition,
               font=F["sans"](9), fill=INK_SOFT)
    y += box_h + 6

    # footer
    f_ny = F["sans_b"](10)
    d.text((M, y), data["not_yet"], font=f_ny, fill=INK)
    y += 13
    hline(d, M, M + CW, y, color=INK, width=1)
    y += 5
    f_fs = F["mono"](8)
    d.text((M, y), data["footer_sources"], font=f_fs, fill=GREY)
    y += 11
    f_ft = F["serif_i"](10)
    d.text((M, y), data["footer"], font=f_ft, fill=INK_SOFT)
    y += 12
    print(f"final y = {y} (canvas {H}, bottom margin {H - y})")
    return img

def main():
    with open(os.path.join(HERE, "stories_v2.json")) as fh:
        data = json.load(fh)
    img = render(data)
    out = os.path.join(HERE, "entry.png")
    img.save(out)
    print(f"wrote {out}  {os.path.getsize(out):,} bytes")

if __name__ == "__main__":
    main()
