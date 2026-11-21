#!/usr/bin/env python3
"""Render the news-image-20261121 front page (1024x1024) from stories.json.

Fresh implementation written for this entry. All illustrations are
flat-vector shapes drawn in code with Pillow; no raster assets, no
network, no AI generation. Deterministic output.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.expanduser("~/workspace/custom-skills/canvas-design/canvas-fonts")

# Palette — cream paper, navy ink, one red accent.
PAPER  = (246, 239, 221)
INK    = (24, 48, 88)
INK_SOFT = (58, 74, 102)
RED    = (180, 35, 24)
RED_LT = (226, 82, 62)
GOLD   = (196, 141, 38)
TEAL   = (23, 120, 110)
GREEN  = (46, 125, 62)
PURPLE = (104, 78, 150)
AMBER  = (178, 118, 20)
GREY   = (110, 110, 105)
LINE   = (203, 192, 172)
CARD   = (255, 252, 244)
MAPBG  = (24, 48, 88)
MAPDOT = (132, 158, 196)
MAPDOT_LT = (96, 122, 164)
WHITE  = (255, 255, 255)
BLACK  = (20, 20, 20)

W, H = 1024, 1024
M = 28                      # page margin
CW = W - 2 * M              # content width = 968

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

F = {
    "mast":  lambda s: font("Gloock-Regular.ttf", s),
    "serif": lambda s: font("CrimsonPro-Regular.ttf", s),
    "serif_b": lambda s: font("CrimsonPro-Bold.ttf", s),
    "serif_i": lambda s: font("CrimsonPro-Italic.ttf", s),
    "sans":  lambda s: font("InstrumentSans-Regular.ttf", s),
    "sans_b": lambda s: font("InstrumentSans-Bold.ttf", s),
    "sans_i": lambda s: font("InstrumentSans-Italic.ttf", s),
    "mono":  lambda s: font("IBMPlexMono-Regular.ttf", s),
    "mono_b": lambda s: font("IBMPlexMono-Bold.ttf", s),
}

def text_w(draw, s, f):
    return draw.textlength(s, font=f)

def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines."""
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(draw, s, f, max_w, min_size=None):
    """Shrink font until the string fits; returns (font, size)."""
    size = f.size
    while draw.textlength(s, font=f) > max_w and size > (min_size or 8):
        size -= 1
        f = font(f.path, size) if hasattr(f, "path") else f
    return f

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def hline(d, x0, x1, y, color=LINE, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)

# ---------------------------------------------------------------- map
# Simplified continent outlines (lon, lat), drawn as a dot matrix.
CONTINENTS = [
    # North America
    [(-168,66),(-150,70),(-130,70),(-120,71),(-105,68),(-90,66),(-80,68),
     (-70,62),(-60,55),(-55,47),(-60,44),(-70,42),(-75,38),(-80,32),
     (-81,26),(-85,29),(-90,21),(-95,17),(-100,17),(-105,21),(-110,24),
     (-115,29),(-120,34),(-124,42),(-128,50),(-135,58),(-145,60),
     (-155,58),(-162,55),(-168,66)],
    # Greenland
    [(-55,60),(-45,60),(-35,65),(-25,70),(-20,74),(-30,76),(-45,76),
     (-55,73),(-58,68),(-55,60)],
    # South America
    [(-79,9),(-72,12),(-62,10),(-52,5),(-48,0),(-40,-5),(-35,-9),
     (-38,-16),(-41,-23),(-48,-28),(-55,-34),(-62,-40),(-68,-47),
     (-71,-52),(-74,-48),(-73,-38),(-71,-28),(-70,-18),(-75,-15),
     (-79,-6),(-81,0),(-79,9)],
    # Africa
    [(-17,15),(-15,25),(-10,31),(-2,35),(9,37),(15,32),(25,32),(32,31),
     (35,27),(38,20),(43,12),(51,11),(48,5),(41,-3),(39,-12),(35,-20),
     (32,-27),(25,-34),(18,-33),(14,-24),(12,-14),(9,4),(0,6),(-8,5),
     (-13,9),(-17,15)],
    # Europe
    [(-10,37),(-9,43),(-3,44),(-2,48),(0,50),(3,53),(7,55),(8,58),
     (6,62),(12,65),(18,69),(25,71),(30,70),(35,67),(40,66),(38,64),
     (32,62),(28,59),(23,58),(19,55),(14,54),(8,55),(5,58),(2,55),
     (-2,51),(-5,48),(-3,44),(-9,38),(-10,37)],
    # Asia
    [(30,36),(36,36),(40,39),(45,38),(48,33),(52,29),(57,26),(63,25),
     (68,23),(72,20),(76,14),(78,8),(81,10),(86,20),(90,22),(94,17),
     (98,14),(101,8),(104,2),(106,8),(109,13),(108,18),(110,20),
     (115,22),(119,26),(121,31),(123,38),(127,40),(131,43),(136,45),
     (141,50),(142,55),(146,59),(152,60),(158,62),(165,66),(172,67),
     (178,66),(172,68),(163,70),(155,71),(145,72),(135,72),(125,72),
     (115,73),(105,76),(95,76),(85,74),(75,73),(65,70),(55,68),
     (45,68),(35,67),(30,68),(30,36)],
    # Australia
    [(113,-22),(115,-32),(118,-35),(124,-33),(130,-32),(135,-35),
     (140,-38),(145,-38),(150,-37),(153,-31),(151,-24),(147,-19),
     (143,-14),(141,-12),(136,-12),(131,-12),(126,-14),(122,-17),
     (117,-20),(113,-22)],
    # New Zealand
    [(167,-45),(170,-43),(173,-41),(176,-38),(178,-37),(175,-38),
     (172,-41),(168,-44),(167,-45)],
    # UK
    [(-5,50),(-3,53),(-5,56),(-3,58),(0,53),(1,51),(-1,50),(-5,50)],
    # Japan
    [(130,31),(133,34),(136,35),(139,36),(141,39),(142,43),(141,44),
     (139,40),(137,36),(134,34),(131,32),(130,31)],
    # Madagascar
    [(44,-16),(48,-15),(50,-17),(48,-22),(45,-25),(43,-21),(44,-16)],
    # Indonesia
    [(95,5),(100,-2),(105,-5),(110,-7),(115,-8),(120,-9),(125,-8),
     (130,-3),(135,-4),(140,-8),(95,5)],
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
    """Dot-matrix world map. pins: list of (lon, lat, n)."""
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
        gx, gy = gx0, gy0
        while gy <= gy1:
            gx = gx0
            while gx <= gx1:
                lon = (gx - x0) / mw * 360.0 - 180.0
                lat = 74.0 - (gy - y0) / mh * 130.0
                if _point_in_poly(lon, lat, poly):
                    r = 1.5
                    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=MAPDOT)
                gx += step
            gy += step
    # grey dots for also-list stories
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
            d.line([(px, py), (cx, cy)], fill=WHITE, width=1)
        r = 7.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=1)
        f = F["sans_b"](9)
        tw = d.textlength(str(n), font=f)
        d.text((cx - tw / 2, cy - 6), str(n), font=f, fill=WHITE)
    return proj

# ------------------------------------------------------- illustrations
# Each draws one flat-vector illustration inside box (x0,y0,x1,y1).
# No raster assets, no text inside the art except single glyphs.

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
    # crack + seismograph zigzag
    cx = x0 + (x1 - x0) * 0.30
    d.line([(cx, y0 + 40), (cx + 6, y0 + 52), (cx - 2, y0 + 64), (cx + 4, y0 + 76)],
           fill=RED, width=2)
    zy = y1 - 26
    pts = [(x0 + 8, zy), (x0 + 20, zy), (x0 + 26, zy - 8), (x0 + 32, zy + 8),
           (x0 + 38, zy - 14), (x0 + 44, zy + 12), (x0 + 52, zy),
           (x1 - 8, zy)]
    d.line(pts, fill=RED, width=2, joint="curve")

def art_bepi(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 24, 44))
    for sx, sy, r in [(0.12, 0.2, 1.5), (0.3, 0.12, 1), (0.55, 0.3, 1.5),
                      (0.8, 0.14, 1), (0.92, 0.45, 1.5), (0.08, 0.6, 1)]:
        d.ellipse([x0 + (x1 - x0) * sx - r, y0 + (y1 - y0) * sy - r,
                   x0 + (x1 - x0) * sx + r, y0 + (y1 - y0) * sy + r], fill=WHITE)
    # Mercury
    mx, my, mr = x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.62, 20
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(168, 148, 128))
    for cx, cy, cr in [(mx - 8, my - 6, 4), (mx + 7, my + 3, 5), (mx - 2, my + 9, 3)]:
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(140, 122, 104))
    # orbit ellipse
    d.ellipse([x0 + 6, y0 + 14, x1 - 6, y1 - 14], outline=(120, 140, 180), width=1)
    # spacecraft: body + panels
    sx, sy = x0 + (x1 - x0) * 0.30, y0 + (y1 - y0) * 0.30
    d.rectangle([sx - 22, sy - 4, sx - 8, sy + 4], fill=(90, 110, 150), outline=WHITE, width=1)
    d.rectangle([sx + 8, sy - 4, sx + 22, sy + 4], fill=(90, 110, 150), outline=WHITE, width=1)
    d.rectangle([sx - 8, sy - 7, sx + 8, sy + 7], fill=GOLD, outline=WHITE, width=1)
    d.polygon([(sx + 8, sy - 5), (sx + 16, sy), (sx + 8, sy + 5)], fill=RED)

def art_nasdaq(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 240, 244))
    # bars
    bw = (x1 - x0 - 16) / 6
    heights = [0.35, 0.5, 0.42, 0.62, 0.55, 0.78]
    for i, h in enumerate(heights):
        bx0 = x0 + 8 + i * bw
        by = y1 - 10 - (y1 - y0 - 24) * h
        col = RED if i >= 4 else (120, 130, 145)
        d.rectangle([bx0 + 2, by, bx0 + bw - 2, y1 - 10], fill=col)
    # descending trend line with arrow
    pts = [(x0 + 10, y0 + 16), (x0 + (x1 - x0) * 0.35, y0 + 30),
           (x0 + (x1 - x0) * 0.6, y0 + 26), (x0 + (x1 - x0) * 0.85, y0 + 52)]
    d.line(pts, fill=RED, width=3, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax, ay + 8), (ax - 8, ay - 2), (ax + 2, ay - 8)], fill=RED)
    d.text((x0 + 10, y0 + 4), "−5.3%", font=F["sans_b"](13), fill=RED)

def art_drone(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(196, 214, 226))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 6
    # rotors
    for rx, ry in [(cx - 26, cy - 14), (cx + 26, cy - 14),
                   (cx - 26, cy + 12), (cx + 26, cy + 12)]:
        d.line([(rx - 12, ry), (rx + 12, ry)], fill=INK, width=3)
        d.line([(rx, ry - 10), (rx, ry + 10)], fill=INK, width=1)
    # arms + body
    d.line([(cx - 26, cy - 14), (cx, cy)], fill=INK, width=2)
    d.line([(cx + 26, cy - 14), (cx, cy)], fill=INK, width=2)
    d.line([(cx - 26, cy + 12), (cx, cy)], fill=INK, width=2)
    d.line([(cx + 26, cy + 12), (cx, cy)], fill=INK, width=2)
    d.rounded_rectangle([cx - 12, cy - 8, cx + 12, cy + 8], radius=4, fill=INK)
    d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=RED)
    # red X over it + down arrow
    d.line([(cx + 18, cy - 22), (cx + 30, cy - 10)], fill=RED, width=3)
    d.line([(cx + 30, cy - 22), (cx + 18, cy - 10)], fill=RED, width=3)
    d.line([(cx, cy + 22), (cx, cy + 34)], fill=RED, width=3)
    d.polygon([(cx - 5, cy + 30), (cx + 5, cy + 30), (cx, cy + 38)], fill=RED)
    # sea
    for i, wy in enumerate((y1 - 16, y1 - 9)):
        d.arc([x0 - 10 + i * 6, wy - 4, x1 + 10, wy + 6], 0, 180, fill=TEAL, width=2)

def art_denmark(d, box):
    x0, y0, x1, y1 = box
    # Danish flag
    d.rectangle(box, fill=(200, 16, 46))
    d.rectangle([x0 + (x1 - x0) * 0.30, y0, x0 + (x1 - x0) * 0.42, y1], fill=WHITE)
    d.rectangle([x0, y0 + (y1 - y0) * 0.44, x1, y0 + (y1 - y0) * 0.56], fill=WHITE)
    # exit arrow + door
    dx0, dy0 = x0 + (x1 - x0) * 0.58, y0 + (y1 - y0) * 0.62
    d.rounded_rectangle([dx0, dy0, dx0 + 26, dy0 + 30], radius=3,
                        fill=WHITE, outline=INK, width=2)
    d.line([(dx0 + 6, dy0 + 15), (dx0 + 20, dy0 + 15)], fill=RED, width=3)
    d.polygon([(dx0 + 20, dy0 + 10), (dx0 + 20, dy0 + 20), (dx0 + 26, dy0 + 15)], fill=RED)

def art_pill(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 242, 236))
    # shrinking cells
    cells = [(0.18, 0.28, 9, (120, 140, 160)), (0.30, 0.55, 7, (140, 155, 170)),
             (0.80, 0.30, 8, (120, 140, 160)), (0.88, 0.62, 6, (140, 155, 170))]
    for fx, fy, r, col in cells:
        cx, cy = x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.line([(cx - r * 0.5, cy - r * 0.5), (cx + r * 0.5, cy + r * 0.5)], fill=RED, width=2)
    # capsule, tilted
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.rounded_rectangle([cx - 30, cy - 10, cx + 30, cy + 10], radius=10,
                        fill=WHITE, outline=INK, width=2)
    d.rounded_rectangle([cx - 30, cy - 10, cx, cy + 10], radius=10, fill=RED)
    d.rectangle([cx - 2, cy - 10, cx + 2, cy + 10], fill=INK)
    d.ellipse([cx - 30, cy - 10, cx - 10, cy + 10], fill=RED)
    d.ellipse([cx + 10, cy - 10, cx + 30, cy + 10], fill=WHITE, outline=INK, width=2)

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

def art_fbi(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(226, 230, 238))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # shield
    d.polygon([(cx - 22, cy - 24), (cx + 22, cy - 24), (cx + 22, cy + 2),
               (cx, cy + 24), (cx - 22, cy + 2)], fill=INK)
    d.polygon([(cx - 22, cy - 24), (cx + 22, cy - 24), (cx + 22, cy + 2),
               (cx, cy + 24), (cx - 22, cy + 2)], outline=GOLD, width=2)
    # magnifier
    mx, my = cx + 2, cy - 2
    d.ellipse([mx - 10, my - 10, mx + 10, my + 10], outline=WHITE, width=3)
    d.line([(mx + 7, my + 7), (mx + 15, my + 15)], fill=WHITE, width=3)
    # binary bits
    f = F["mono_b"](9)
    for i, (fx, fy) in enumerate([(0.12, 0.15), (0.85, 0.18), (0.10, 0.75), (0.88, 0.72)]):
        d.text((x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy), "01"[i % 2],
               font=f, fill=INK_SOFT)

def art_tennis(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 240, 220))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 2
    # court lines
    d.rectangle([x0 + 6, y1 - 14, x1 - 6, y1 - 10], fill=TEAL)
    # ball
    r = 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(190, 214, 60), outline=INK, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=WHITE, width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 120, 240, fill=WHITE, width=3)
    # motion lines
    for i, wy in enumerate((cy - 30, cy - 36)):
        d.line([(cx - 34, wy), (cx - 44, wy)], fill=INK_SOFT, width=2)
    # racket handle
    d.line([(x1 - 12, y0 + 8), (x1 - 26, y0 + 26)], fill=(150, 90, 40), width=4)

def art_whitehouse(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(226, 232, 240))
    cx = (x0 + x1) / 2
    base = y1 - 8
    # dome
    d.pieslice([cx - 16, y0 + 8, cx + 16, y0 + 40], 180, 360, fill=WHITE, outline=INK, width=2)
    d.line([(cx, y0 + 6), (cx, y0 + 12)], fill=INK, width=2)
    # entablature + columns
    d.rectangle([cx - 30, y0 + 40, cx + 30, y0 + 48], fill=WHITE, outline=INK, width=2)
    for i in range(5):
        colx = cx - 26 + i * 13
        d.rectangle([colx, y0 + 48, colx + 6, base], fill=WHITE, outline=INK, width=1)
    d.rectangle([cx - 32, base, cx + 32, base + 4], fill=WHITE, outline=INK, width=1)
    # flag
    d.line([(cx + 34, y0 + 10), (cx + 34, y0 + 34)], fill=INK, width=2)
    d.polygon([(cx + 34, y0 + 10), (cx + 50, y0 + 15), (cx + 34, y0 + 20)], fill=RED)

ART = {
    "cop31": art_cop31, "riyadh": art_riyadh, "peru": art_peru,
    "bepi": art_bepi, "nasdaq": art_nasdaq, "drone": art_drone,
    "denmark": art_denmark, "pill": art_pill, "robot": art_robot,
    "mexico": art_mexico, "fbi": art_fbi, "tennis": art_tennis,
    "whitehouse": art_whitehouse,
}


ART_BG = {
    "cop31": (206, 228, 224), "riyadh": (30, 38, 66), "peru": (232, 214, 176),
    "bepi": (18, 24, 44), "nasdaq": (238, 240, 244), "drone": (196, 214, 226),
    "denmark": (200, 16, 46), "pill": (232, 242, 236), "robot": (228, 232, 238),
    "mexico": (240, 234, 214), "fbi": (226, 230, 238), "tennis": (238, 240, 220),
    "whitehouse": (226, 232, 240),
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
REGION_COLORS = [
    ("EUROPE", "EUROPE 9", INK),
    ("ASIA-PACIFIC", "APAC 2", TEAL),
    ("AMERICAS", "AMERICAS 15", RED),
    ("MIDEAST", "MIDEAST 3", AMBER),
    ("AFRICA", "AFRICA 3", GREEN),
    ("OCEANIA", "OCEANIA 2", PURPLE),
    ("WORLD", "W 1", GREY),
]

def section_label(d, x, y, text):
    f = F["mono_b"](10)
    d.text((x, y), text, font=f, fill=RED)
    tw = d.textlength(text, font=f)
    d.line([(x + tw + 8, y + 5), (M + CW, y + 5)], fill=LINE, width=1)
    return y + 14

def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 16

    # eyebrow
    f_eye = F["mono"](10)
    left = "THE WORLD IN ONE PAGE"
    right = "SATURDAY EDITION  ·  35 STORIES  ·  7 REGIONS"
    d.text((M, y), left, font=f_eye, fill=INK_SOFT)
    d.text((M + CW - d.textlength(right, font=f_eye), y), right,
           font=f_eye, fill=INK_SOFT)
    y += 16
    hline(d, M, M + CW, y, color=INK, width=2)
    y += 8

    # masthead — giant serif date
    f_mast = F["mast"](42)
    mast = data["masthead"]
    while d.textlength(mast, font=f_mast) > CW and f_mast.size > 30:
        f_mast = F["mast"](f_mast.size - 1)
    d.text((M, y), mast, font=f_mast, fill=INK)
    y += 54

    # red italic subline
    f_sub = F["serif_i"](20)
    sub = data["subline"]
    while d.textlength(sub, font=f_sub) > CW and f_sub.size > 14:
        f_sub = F["serif_i"](f_sub.size - 1)
    d.text((M, y), sub, font=f_sub, fill=RED)
    y += 26

    # region bar
    total = sum(data["regions"].values())
    bx = M
    bar_h = 20
    for name, label, col in REGION_COLORS:
        cnt = data["regions"][name]
        bw = CW * cnt / total
        d.rectangle([bx, y, bx + bw, y + bar_h], fill=col)
        f_lab = F["sans_b"](8)
        tw = d.textlength(label, font=f_lab)
        if tw + 6 <= bw:
            d.text((bx + (bw - tw) / 2, y + 6), label, font=f_lab, fill=WHITE)
        bx += bw
    y += bar_h + 6

    # THE DAY IN NUMBERS
    y = section_label(d, M, y, "THE DAY IN NUMBERS")
    nums = data["numbers"]
    col_w = CW / len(nums)
    f_val = F["sans_b"](22)
    f_lab = F["sans"](8)
    for i, it in enumerate(nums):
        cx = M + col_w * i
        d.text((cx, y), it["value"], font=f_val, fill=RED)
        for j, ln in enumerate(wrap(d, it["label"], f_lab, col_w - 8)):
            d.text((cx, y + 26 + j * 10), ln, font=f_lab, fill=INK_SOFT)
        if i:
            d.line([(cx - 6, y + 2), (cx - 6, y + 44)], fill=LINE, width=1)
    y += 42

    # timeline
    f_t = F["mono_b"](10)
    f_tx = F["sans"](10)
    tx = M
    d.text((tx, y), "SATURDAY BY THE HOURS  ", font=f_t, fill=RED)
    tx += d.textlength("SATURDAY BY THE HOURS  ", font=f_t)
    for it in data["timeline"]:
        t = it["time"]
        d.text((tx, y), t, font=f_t, fill=RED)
        tx += d.textlength(t, font=f_t) + 6
        d.text((tx, y), it["text"], font=f_tx, fill=INK)
        tx += d.textlength(it["text"], font=f_tx) + 22
        if tx > M + CW - 120:
            break
    y += 18

    # hero cards
    y = section_label(d, M, y, "THE THREE BIG STORIES")
    gap = 10
    hw = (CW - 2 * gap) / 3
    hh = 150
    hy = y
    for i, s in enumerate(data["heroes"]):
        x0 = M + i * (hw + gap)
        x1 = x0 + hw
        rrect(d, [x0, hy, x1, hy + hh], 4, fill=CARD, outline=LINE, width=1)
        draw_art(img, d, s["art"], (x0 + 1, hy + 1, x1 - 1, hy + 52))
        ty = hy + 58
        f_pl = F["mono_b"](9)
        d.text((x0 + 10, ty), f"{s['n']} · {s['place']}", font=f_pl, fill=RED)
        ty += 14
        f_h = F["serif_b"](15)
        for ln in wrap(d, s["headline"], f_h, hw - 20)[:2]:
            d.text((x0 + 10, ty), ln, font=f_h, fill=INK)
            ty += 18
        ty += 2
        f_dk = F["sans"](10)
        for ln in wrap(d, s["deck"], f_dk, hw - 20)[:2]:
            d.text((x0 + 10, ty), ln, font=f_dk, fill=INK_SOFT)
            ty += 12
        f_src = F["mono"](8)
        d.text((x0 + 10, hy + hh - 14), " · ".join(s["sources"]).upper(),
               font=f_src, fill=GREY)
    y = hy + hh + 8

    # medium cards
    y = section_label(d, M, y, "MORE OF THE DAY")
    mw = (CW - gap) / 2
    mh = 43
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
            hl = wrap(d, s["headline"], f_h, mw - 56)
            ty = ry + 5
            for ln in hl[:1]:
                d.text((tx, ty), ln, font=f_h, fill=INK)
                ty += 14
            f_dk = F["sans"](10)
            dk = wrap(d, s["deck"], f_dk, mw - 56)
            for ln in dk[:1]:
                d.text((tx, ty), ln, font=f_dk, fill=INK_SOFT)
                ty += 12
            f_src = F["mono"](8)
            d.text((tx, ty), f"{s['place']}  ·  " + " · ".join(s["sources"]).upper(),
                   font=f_src, fill=GREY)
    y += 5 * (mh + 3) + 4

    # map
    y = section_label(d, M, y, "WHERE IT HAPPENED  —  1–13 FEATURED, 14–35 IN ALSO TODAY")
    map_h = 112
    rrect(d, [M, y, M + CW, y + map_h], 4, fill=MAPBG)
    pins = [(s["lon"], s["lat"], s["n"]) for s in data["heroes"] + data["mediums"]]
    grey = [(s["lon"], s["lat"]) for s in data["also"]]
    draw_map(d, (M + 6, y + 6, M + CW - 6, y + map_h - 6), pins, grey)
    y += map_h + 8

    # also today
    y = section_label(d, M, y, "ALSO TODAY")
    cols = 3
    col_w = (CW - 2 * 12) / cols
    f_n = F["mono_b"](10)
    f_a = F["sans"](10)
    for i, s in enumerate(data["also"]):
        col = i % cols
        row = i // cols
        x0 = M + col * (col_w + 12)
        ay = y + row * 14
        d.text((x0, ay), str(s["n"]), font=f_n, fill=RED)
        d.text((x0 + 22, ay), s["headline"], font=f_a, fill=INK)
    y += 8 * 14 + 4

    # DATE CHECK
    dc_h = 58
    rrect(d, [M, y, M + CW, y + dc_h], 4, fill=CARD, outline=RED, width=1)
    f_dc = F["mono_b"](10)
    d.text((M + 10, y + 8), "DATE CHECK — NOT SATURDAY", font=f_dc, fill=RED)
    f_it = F["sans"](10)
    items = data["date_check"]
    for i, it in enumerate(items):
        col = i % 3
        row = i // 3
        x0 = M + 10 + col * ((CW - 20) / 3)
        ay = y + 26 + row * 12
        d.text((x0, ay), f"{it['text']} — {it['when']}", font=f_it, fill=INK_SOFT)
    y += dc_h + 6

    # not yet + footer
    f_ny = F["sans_b"](10)
    d.text((M, y), data["not_yet"], font=f_ny, fill=INK)
    y += 14
    hline(d, M, M + CW, y, color=INK, width=1)
    y += 6
    f_fs = F["mono"](8)
    d.text((M, y), data["footer_sources"], font=f_fs, fill=GREY)
    y += 10
    f_ft = F["serif_i"](10)
    d.text((M, y), data["footer"], font=f_ft, fill=INK_SOFT)
    y += 12
    print(f"final y = {y} (canvas {H}, bottom margin {H - y})")
    return img

def main():
    with open(os.path.join(HERE, "stories.json")) as fh:
        data = json.load(fh)
    img = render(data)
    out = os.path.join(HERE, "entry.png")
    img.save(out)
    print(f"wrote {out}  {os.path.getsize(out):,} bytes")

if __name__ == "__main__":
    main()
