#!/usr/bin/env python3
"""build_frontpage_v2.py — News-21 v2-alt renderer (path B).

Fresh implementation written in this session for the News-21
alternative maximisation. Renders stories_v2.json -> entry.png
(1024x1024). Pillow only; OFL fonts from canvas-fonts.
Angle: "the Saturday that kept escalating" — evening-update edition.
Heroes: Bahrain strike / Peru quake / COP31. 8-figure numbers strip,
6-item timeline, confidence tags on all 13 featured cards, bigger
hero art + map with region labels.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 28
CW = W - 2 * MX  # 968

PAPER = (246, 239, 221)
INK = (24, 48, 88)
RED = (180, 35, 24)
MUTED = (112, 106, 92)
RULE = (196, 188, 170)
GREEN = (28, 96, 60)
GREEN_BG = (214, 232, 220)
AMBER = (150, 90, 10)
AMBER_BG = (242, 228, 200)
GREY_BG = (228, 224, 214)

FD = os.path.expanduser(
    "~/workspace/custom-skills/canvas-design/canvas-fonts")


def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def gloock(s):
    return F("Gloock-Regular.ttf", s)


def crim_b(s):
    return F("CrimsonPro-Bold.ttf", s)


def crim(s):
    return F("CrimsonPro-Regular.ttf", s)


def crim_i(s):
    return F("CrimsonPro-Italic.ttf", s)


def sans_b(s):
    return F("InstrumentSans-Bold.ttf", s)


def sans(s):
    return F("InstrumentSans-Regular.ttf", s)


def mono_b(s):
    return F("IBMPlexMono-Bold.ttf", s)


def mono(s):
    return F("IBMPlexMono-Regular.ttf", s)


# ---------------------------------------------------------------- text utils
def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def th(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[3] - b[1]


def wrap(d, s, f, width):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(d, x, y, s, f, fill, spacing=2):
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += tw(d, ch, f) + spacing
    return cx


def fit_size(d, s, factory, width, start, minimum):
    """Largest font size (from factory) that fits s in width."""
    size = start
    while size > minimum:
        f = factory(size)
        if tw(d, s, f) <= width:
            return f, size
        size -= 1
    return factory(minimum), minimum


def ellipsize(d, s, f, width):
    if tw(d, s, f) <= width:
        return s
    while s and tw(d, s + "…", f) > width:
        s = s[:-1]
    return s + "…"


def vgrad(d, x0, y0, x1, y1, top, bottom, steps=24):
    for i in range(steps):
        t = i / (steps - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        yy0 = y0 + (y1 - y0) * i // steps
        yy1 = y0 + (y1 - y0) * (i + 1) // steps
        d.rectangle([x0, yy0, x1, yy1], fill=c)


# ---------------------------------------------------------------- land mask
# Coarse continent spans per row, lon ranges in degrees. Rows cover
# lat 82.5 down to -57.5 in 24 steps (~5.83 deg each). Authored by hand
# from world geography for the dotted map.
LAND = [
    [(-60, -20), (10, 25), (45, 60), (90, 110), (-85, -65)],
    [(-165, -140), (-125, -70), (-55, -20), (60, 180)],
    [(-165, -140), (-135, -60), (-55, -40), (-22, -14), (5, 30), (30, 180)],
    [(-165, -150), (-135, -55), (-5, 2), (5, 30), (30, 180)],
    [(-130, -55), (-5, 2), (0, 30), (30, 180)],
    [(-125, -55), (0, 30), (30, 140)],
    [(-125, -67), (-10, 30), (45, 90), (75, 122), (130, 145)],
    [(-125, -70), (-10, 36), (35, 60), (60, 90), (75, 122), (130, 142)],
    [(-120, -75), (-10, 35), (35, 60), (68, 88), (95, 108)],
    [(-115, -87), (-10, 35), (35, 58), (68, 88), (95, 108)],
    [(-110, -87), (-17, 35), (40, 58), (72, 88), (95, 108)],
    [(-95, -83), (-17, 42), (76, 80), (95, 105)],
    [(-90, -78), (-17, 45), (95, 105)],
    [(-78, -52), (-12, 45), (95, 105), (110, 130)],
    [(-78, -35), (-12, 40), (105, 135)],
    [(-78, -38), (10, 40), (110, 140)],
    [(-75, -40), (12, 35), (113, 142)],
    [(-72, -42), (12, 33), (113, 150)],
    [(-70, -48), (15, 32), (115, 153)],
    [(-70, -55), (17, 28), (115, 150), (167, 178)],
    [(-72, -62), (140, 150), (167, 175)],
    [(-73, -65), (167, 173)],
    [(-73, -66)],
    [(-70, -66)],
]
LAT_TOP, LAT_BOT = 82.5, -57.5


def is_land(lat, lon):
    r = int((LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * len(LAND))
    if r < 0 or r >= len(LAND):
        return False
    return any(lo <= lon <= hi for lo, hi in LAND[r])


# ---------------------------------------------------------------- draw utils
def circle(d, cx, cy, r, fill=None, outline=None, width=1):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=outline, width=width)


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def flame(d, x, y, s, c1, c2):
    """Simple flame: stacked teardrops."""
    d.polygon([(x, y - s), (x + s * 0.55, y - s * 0.1),
               (x + s * 0.35, y + s * 0.55), (x - s * 0.35, y + s * 0.55),
               (x - s * 0.55, y - s * 0.1)], fill=c1)
    d.polygon([(x, y - s * 0.55), (x + s * 0.3, y),
               (x + s * 0.18, y + s * 0.4), (x - s * 0.18, y + s * 0.4),
               (x - s * 0.3, y)], fill=c2)


# ---------------------------------------------------------------- hero scenes
# Each draws a wide flat-vector scene at 2x, downscaled to (w, h).
def scene_bahrain(w, h):
    S = 2
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vgrad(d, 0, 0, w * S, h * S, (30, 46, 82), (16, 26, 52))
    rng = random.Random(7)
    for _ in range(26):
        x = rng.uniform(4, w * S - 4)
        y = rng.uniform(4, h * S * 0.55)
        r = rng.uniform(0.8, 1.8)
        circle(d, x, y, r, fill=(235, 238, 245))
    # base skyline
    base = h * S
    for bx, bw, bh in [(0, 52, 26), (52, 40, 38), (92, 60, 22), (152, 46, 34),
                       (198, 70, 20), (268, 44, 30), (312, 58, 24),
                       (370, 48, 36), (418, 62, 22), (480, 50, 30),
                       (530, 56, 26), (586, 40, 32)]:
        d.rectangle([bx, base - bh, bx + bw, base], fill=(13, 21, 42))
    # radar dish, left (brightened so it reads at 52px)
    d.line([(58, base - 26), (58, base - 58)], fill=(220, 225, 235), width=5)
    d.arc([30, base - 88, 86, base - 32], 200, 340, fill=(220, 225, 235),
          width=5)
    d.line([(58, base - 58), (36, base - 30)], fill=(220, 225, 235), width=5)
    d.line([(58, base - 58), (80, base - 30)], fill=(220, 225, 235), width=5)
    # missile streaks (top-right -> bottom-left)
    for (x0, y0, x1, y1) in [(560, 8, 470, 66), (500, 2, 430, 52),
                             (610, 26, 540, 74)]:
        d.line([(x0, y0), (x1, y1)], fill=(255, 150, 60), width=7)
        d.line([(x0, y0), (x1, y1)], fill=(255, 240, 210), width=3)
        circle(d, x0, y0, 4, fill=(255, 240, 210))
    # explosion burst at the first streak's end
    ex, ey = 470, 66
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x2 = ex + 26 * math.cos(a)
        y2 = ey + 26 * math.sin(a)
        d.line([(ex, ey), (x2, y2)], fill=(255, 170, 60), width=4)
    circle(d, ex, ey, 13, fill=(255, 190, 80))
    circle(d, ex, ey, 7, fill=(255, 240, 200))
    # interceptor streak rising from the base
    d.line([(330, base - 20), (390, 26)], fill=(140, 200, 255), width=4)
    d.line([(330, base - 20), (390, 26)], fill=(230, 245, 255), width=2)
    return img.resize((w, h), Image.LANCZOS)


def scene_peru(w, h):
    S = 2
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vgrad(d, 0, 0, w * S, h * S, (198, 216, 228), (232, 230, 220))
    circle(d, w * S - 60, 26, 14, fill=(250, 244, 214))
    # mountain ranges, back to front
    base = h * S
    d.polygon([(0, base), (90, 30), (180, base)], fill=(150, 170, 186))
    d.polygon([(120, base), (240, 18), (360, base)], fill=(122, 144, 162))
    d.polygon([(300, base), (420, 26), (540, base)], fill=(150, 170, 186))
    d.polygon([(470, base), (560, 36), (626, base)], fill=(122, 144, 162))
    # snow caps
    for (cx, cy, s) in [(90, 30, 15), (240, 18, 17), (420, 26, 14)]:
        d.polygon([(cx - s, cy + s * 0.7), (cx, cy),
                   (cx + s, cy + s * 0.7)], fill=(250, 250, 248))
    # foreground ridge (dark)
    d.polygon([(0, base), (150, 70), (300, base)], fill=(84, 106, 126))
    d.polygon([(260, base), (430, 66), (626, base)], fill=(68, 90, 110))
    # seismograph: one clean waveform on a faint baseline
    y0 = 78
    d.line([(0, y0), (w * S, y0)], fill=(120, 130, 140), width=2)
    wave = [(30, 0), (60, -3), (85, 4), (110, -5), (135, 6), (160, -18),
            (185, 14), (210, -24), (235, 20), (260, -12), (285, 9),
            (310, -6), (335, 5), (360, -16), (385, 13), (410, -9),
            (435, 6), (460, -4), (485, 3), (510, -2), (540, 1), (570, 0),
            (626, 0)]
    pts = [(x, y0 + dy) for (x, dy) in wave]
    d.line(pts, fill=RED, width=3, joint="curve")
    # cracked ground
    d.line([(40, base - 6), (120, base - 14), (200, base - 4),
            (300, base - 12), (420, base - 5), (540, base - 11),
            (626, base - 6)], fill=(60, 70, 80), width=3)
    return img.resize((w, h), Image.LANCZOS)


def scene_cop31(w, h):
    S = 2
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vgrad(d, 0, 0, w * S, h * S, (38, 112, 104), (22, 80, 74))
    cx, cy, r = 150, 56, 44
    # globe
    circle(d, cx, cy, r, fill=(238, 232, 214))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(22, 80, 74), width=3)
    for k in (-0.55, 0, 0.55):
        d.arc([cx - r + abs(k) * r * 0.5, cy - r, cx + r - abs(k) * r * 0.5,
               cy + r], 270 if k >= 0 else 90, 90 if k >= 0 else 270,
              fill=(38, 112, 104), width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(38, 112, 104), width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=(38, 112, 104), width=2)
    # land blobs on the globe
    d.ellipse([cx - 30, cy - 26, cx - 8, cy - 8], fill=(38, 112, 104))
    d.ellipse([cx + 2, cy + 4, cx + 26, cy + 24], fill=(38, 112, 104))
    d.ellipse([cx + 10, cy - 30, cx + 28, cy - 14], fill=(38, 112, 104))
    # thermometer, right
    tx = 420
    d.rounded_rectangle([tx - 9, 14, tx + 9, 84], radius=9,
                        fill=(238, 232, 214))
    d.rounded_rectangle([tx - 5, 26, tx + 5, 80], radius=5, fill=RED)
    circle(d, tx, 92, 14, fill=(238, 232, 214))
    circle(d, tx, 92, 9, fill=RED)
    for yy in (24, 40, 56, 72):
        d.line([(tx + 9, yy), (tx + 18, yy)], fill=(238, 232, 214), width=2)
    # clock (overtime), far right
    kx, ky, kr = 540, 56, 26
    circle(d, kx, ky, kr, fill=(238, 232, 214))
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], outline=(22, 80, 74),
              width=3)
    d.line([(kx, ky), (kx, ky - 16)], fill=INK, width=3)
    d.line([(kx, ky), (kx + 12, ky + 6)], fill=INK, width=3)
    circle(d, kx, ky, 3, fill=RED)
    # small rising arrow between globe and thermometer
    d.line([(300, 84), (300, 34)], fill=(250, 244, 214), width=4)
    d.polygon([(300, 22), (290, 38), (310, 38)], fill=(250, 244, 214))
    return img.resize((w, h), Image.LANCZOS)

# ---------------------------------------------------------------- medium icons
# Each draws a flat-vector icon on a 132x132 canvas, downscaled to 44.
def _icon_base(bg):
    img = Image.new("RGBA", (132, 132), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 131, 131], radius=10, fill=bg)
    return img, d


def _finish_icon(img):
    return img.resize((44, 44), Image.LANCZOS)


def icon_bepi():
    img, d = _icon_base((232, 228, 214))
    # Mercury
    circle(d, 70, 74, 32, fill=(216, 164, 110))
    circle(d, 60, 64, 7, fill=(198, 142, 88))
    circle(d, 84, 86, 9, fill=(198, 142, 88))
    circle(d, 78, 58, 5, fill=(198, 142, 88))
    # spacecraft, enlarged so it reads: body + panels + dish
    d.rectangle([24, 22, 54, 38], fill=INK)
    d.rectangle([8, 26, 24, 34], fill=(90, 110, 140))
    d.rectangle([54, 26, 70, 34], fill=(90, 110, 140))
    d.arc([54, 8, 78, 32], 270, 90, fill=INK, width=4)
    d.line([(54, 30), (68, 20)], fill=INK, width=3)
    # trajectory
    d.arc([-20, 88, 120, 174], 300, 30, fill=MUTED, width=3)
    return _finish_icon(img)


def icon_nasdaq():
    img, d = _icon_base((244, 224, 218))
    # axes
    d.line([(18, 18), (18, 108)], fill=MUTED, width=2)
    d.line([(18, 108), (114, 108)], fill=MUTED, width=2)
    # bars
    for i, h in enumerate([22, 34, 28, 44, 38, 58]):
        x = 28 + i * 14
        d.rectangle([x, 108 - h, x + 9, 108], fill=(176, 184, 196))
    # falling line
    pts = [(24, 34), (40, 44), (54, 40), (68, 62), (82, 74), (96, 96),
           (110, 100)]
    d.line(pts, fill=RED, width=5, joint="curve")
    # down arrow
    d.polygon([(104, 88), (116, 88), (110, 100)], fill=RED)
    return _finish_icon(img)


def icon_drone():
    img, d = _icon_base((224, 228, 234))
    # MQ-9 silhouette (navy)
    d.ellipse([48, 52, 84, 76], fill=INK)  # fuselage
    d.rectangle([16, 58, 116, 64], fill=INK)  # wings
    d.rectangle([24, 76, 40, 84], fill=INK)  # tail L
    d.rectangle([92, 76, 108, 84], fill=INK)  # tail R
    d.line([(66, 52), (66, 40)], fill=INK, width=4)  # antenna
    circle(d, 66, 38, 3, fill=INK)
    # red X
    d.line([(88, 88), (116, 116)], fill=RED, width=7)
    d.line([(116, 88), (88, 116)], fill=RED, width=7)
    return _finish_icon(img)


def icon_denmark():
    img, d = _icon_base((244, 232, 226))
    # Danish flag
    d.rectangle([18, 26, 74, 70], fill=(200, 40, 40))
    d.rectangle([18, 44, 74, 52], fill=(250, 250, 248))
    d.rectangle([36, 26, 44, 70], fill=(250, 250, 248))
    # exit door + arrow
    d.rectangle([84, 30, 112, 78], fill=INK)
    d.rectangle([90, 36, 106, 72], fill=PAPER)
    d.line([(80, 54), (100, 54)], fill=RED, width=4)
    d.polygon([(100, 54), (92, 48), (92, 60)], fill=RED)
    # floor line
    d.line([(18, 108), (114, 108)], fill=MUTED, width=3)
    return _finish_icon(img)


def icon_pill():
    img, d = _icon_base((226, 238, 232))
    # capsule (drawn on its own layer, rotated)
    cap = Image.new("RGBA", (90, 40), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap)
    cd.rounded_rectangle([0, 0, 89, 39], radius=19, fill=(250, 250, 248))
    cd.rounded_rectangle([45, 0, 89, 39], radius=19, fill=RED)
    cd.line([(45, 0), (45, 39)], fill=(200, 200, 200), width=2)
    cap = cap.rotate(-28, expand=True, resample=Image.BICUBIC)
    img.paste(cap, (16, 18), cap)
    # shrinking cells + arrow
    for (cx, cy, r) in [(40, 96, 13), (70, 100, 9), (96, 102, 6)]:
        circle(d, cx, cy, r, fill=(38, 112, 104))
    d.line([(28, 84), (108, 92)], fill=MUTED, width=2)
    return _finish_icon(img)


def icon_robot():
    img, d = _icon_base((228, 230, 238))
    # gear behind
    gx, gy = 96, 96
    circle(d, gx, gy, 16, fill=(176, 184, 196))
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x0 = gx + 16 * math.cos(a)
        y0 = gy + 16 * math.sin(a)
        x1 = gx + 23 * math.cos(a)
        y1 = gy + 23 * math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=(176, 184, 196), width=7)
    circle(d, gx, gy, 7, fill=PAPER)
    # robot head
    d.rounded_rectangle([24, 30, 88, 82], radius=12, fill=INK)
    d.line([(56, 30), (56, 18)], fill=INK, width=4)
    circle(d, 56, 16, 5, fill=RED)
    circle(d, 42, 52, 6, fill=(250, 250, 248))
    circle(d, 70, 52, 6, fill=(250, 250, 248))
    d.line([(44, 68), (68, 68)], fill=(250, 250, 248), width=3)
    # ears
    d.rectangle([18, 48, 24, 64], fill=INK)
    d.rectangle([88, 48, 94, 64], fill=INK)
    return _finish_icon(img)


def icon_mexico():
    img, d = _icon_base((238, 232, 214))
    # handcuffs: two rings + chain
    circle(d, 42, 66, 20, outline=INK, width=7)
    circle(d, 92, 66, 20, outline=INK, width=7)
    d.line([(60, 58), (74, 58)], fill=INK, width=4)
    d.line([(60, 74), (74, 74)], fill=INK, width=4)
    # star badge
    d.polygon(star_points(66, 34, 16, 7), fill=(212, 160, 40))
    circle(d, 66, 34, 4, fill=(250, 250, 248))
    return _finish_icon(img)


def icon_fbi():
    img, d = _icon_base((222, 228, 240))
    # shield
    d.polygon([(66, 18), (102, 30), (102, 66), (66, 104), (30, 66),
               (30, 30)], fill=INK)
    d.polygon([(66, 26), (94, 36), (94, 64), (66, 94), (38, 64),
               (38, 36)], outline=(250, 250, 248), width=2)
    # magnifier over the shield
    circle(d, 60, 58, 16, outline=(250, 250, 248), width=5)
    d.line([(72, 70), (88, 86)], fill=(250, 250, 248), width=5)
    # star
    d.polygon(star_points(66, 48, 7, 3), fill=(250, 250, 248))
    return _finish_icon(img)


def icon_riyadh():
    img, d = _icon_base((30, 44, 78))
    # skyline
    for (bx, bw, bh) in [(14, 16, 40), (32, 12, 58), (46, 18, 34),
                         (66, 10, 66), (78, 18, 44), (98, 14, 54)]:
        d.rectangle([bx, 118 - bh, bx + bw, 118], fill=(16, 26, 52))
    # tall tower with spire
    d.rectangle([66, 52, 76, 118], fill=(16, 26, 52))
    d.polygon([(66, 52), (76, 52), (71, 34)], fill=(16, 26, 52))
    # intercept streaks
    d.line([(96, 14), (70, 52)], fill=(255, 150, 60), width=5)
    d.line([(96, 14), (70, 52)], fill=(255, 240, 210), width=2)
    d.line([(118, 30), (96, 62)], fill=(140, 200, 255), width=4)
    circle(d, 96, 14, 4, fill=(255, 240, 210))
    # stars
    for (sx, sy) in [(24, 18), (52, 12), (84, 26), (112, 10), (40, 34)]:
        circle(d, sx, sy, 2, fill=(235, 238, 245))
    return _finish_icon(img)


def icon_sparta():
    img, d = _icon_base((238, 226, 210))
    # sea
    d.rectangle([0, 96, 131, 131], fill=(96, 140, 176))
    d.line([(0, 100), (131, 100)], fill=(240, 244, 248), width=2)
    d.arc([8, 104, 60, 118], 0, 180, fill=(240, 244, 248), width=2)
    d.arc([70, 104, 122, 118], 0, 180, fill=(240, 244, 248), width=2)
    # hull
    d.polygon([(22, 96), (110, 96), (100, 76), (32, 76)], fill=(40, 52, 70))
    # containers
    d.rectangle([36, 56, 52, 76], fill=(200, 60, 40))
    d.rectangle([54, 56, 70, 76], fill=(40, 90, 120))
    d.rectangle([72, 56, 88, 76], fill=(212, 160, 40))
    # bridge
    d.rectangle([92, 58, 106, 76], fill=(240, 244, 248))
    # fire on deck
    flame(d, 46, 52, 14, (255, 140, 40), (255, 210, 90))
    flame(d, 82, 52, 11, (255, 140, 40), (255, 210, 90))
    # smoke
    circle(d, 46, 28, 7, fill=(120, 120, 118))
    circle(d, 56, 20, 9, fill=(140, 140, 138))
    circle(d, 84, 26, 6, fill=(120, 120, 118))
    return _finish_icon(img)


ICONS = {
    "bepi": icon_bepi, "nasdaq": icon_nasdaq, "drone": icon_drone,
    "denmark": icon_denmark, "pill": icon_pill, "robot": icon_robot,
    "mexico": icon_mexico, "fbi": icon_fbi, "riyadh": icon_riyadh,
    "sparta": icon_sparta,
}
SCENES = {"bahrain": scene_bahrain, "peru": scene_peru, "cop31": scene_cop31}


# ---------------------------------------------------------------- confidence tag
def tag_pill(d, x_right, y, label):
    if label == "CONFIRMED":
        bg, fg, dot = GREEN_BG, GREEN, GREEN
    elif label == "CLAIMED":
        bg, fg, dot = (250, 224, 214), RED, RED
    else:  # REPORTED
        bg, fg, dot = GREY_BG, MUTED, (140, 134, 120)
    f = mono_b(7)
    w = tw(d, label, f) + 16
    h = 13
    x0 = x_right - w
    d.rounded_rectangle([x0, y, x_right, y + h], radius=6, fill=bg)
    circle(d, x0 + 7, y + h // 2 + 1, 3, fill=dot)
    d.text((x0 + 12, y + 2), label, font=f, fill=fg)
    return x0


# ---------------------------------------------------------------- section header
def section_header(d, x, y, width, label):
    f = mono_b(9)
    tracked(d, x, y, label, f, RED, spacing=2)
    lw = tw(d, label, f) + 2 * len(label)
    d.line([(x + lw + 8, y + 5), (x + width, y + 5)], fill=RULE, width=1)
    return 13

# ---------------------------------------------------------------- map
def draw_map(d, x0, y0, w, h, stories):
    # isotropic dot grid: one dot per land cell, square spacing, so the
    # continents read as a dotted map instead of vertical stripes.
    step = 8
    cols = int(w // step)
    rows = int(h // step)
    for r in range(rows):
        lat = LAT_TOP - (r + 0.5) * step / h * (LAT_TOP - LAT_BOT)
        for c in range(cols):
            lon = -180 + (c + 0.5) * step / w * 360
            if is_land(lat, lon):
                x = x0 + (c + 0.5) * step
                y = y0 + (r + 0.5) * step
                circle(d, x, y, 1.9, fill=(148, 156, 166))

    def proj(lat, lon):
        return (x0 + (lon + 180) / 360 * w,
                y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h)

    # grey dots for also-list stories 14-35 (deterministic jitter)
    for s in stories["also"]:
        bx, by = proj(s["lat"], s["lon"])
        rng = random.Random(s["n"])
        jx = bx + rng.uniform(-3, 3)
        jy = by + rng.uniform(-3, 3)
        circle(d, jx, jy, 2.4, fill=(150, 158, 168))
    # numbered pins 1-13 with spiral de-collision
    placed = []
    featured = stories["heroes"] + stories["mediums"]
    for s in featured:
        bx, by = proj(s["lat"], s["lon"])
        cand = [(0, 0)]
        for rad in (14, 20, 27, 34, 42):
            for ang in range(0, 360, 45):
                a = math.radians(ang)
                cand.append((rad * math.cos(a), rad * math.sin(a)))
        fx, fy = bx, by
        for (dx, dy) in cand:
            px, py = bx + dx, by + dy
            if not (x0 + 10 <= px <= x0 + w - 10):
                continue
            if not (y0 + 10 <= py <= y0 + h - 10):
                continue
            if all((px - qx) ** 2 + (py - qy) ** 2 >= 17 ** 2
                   for (qx, qy) in placed):
                fx, fy = px, py
                break
        placed.append((fx, fy))
        col = RED if s["n"] <= 3 else INK
        if (fx, fy) != (bx, by):
            d.line([(bx, by), (fx, fy)], fill=MUTED, width=1)
            circle(d, bx, by, 2.2, fill=col)
        circle(d, fx, fy, 7.5, fill=col)
        nf = mono_b(8)
        num = str(s["n"])
        d.text((fx - tw(d, num, nf) / 2, fy - 5), num, font=nf,
               fill=(250, 250, 248))


# ---------------------------------------------------------------- page build
def build(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    warns = []
    y = 14
    # eyebrow
    ef = mono_b(9)
    tracked(d, MX, y, "THE WORLD IN ONE DAY", ef, INK, spacing=2)
    rf = mono(8)
    rtxt = "35 STORIES · 7 REGIONS · ALL DATED BY EVENT"
    d.text((W - MX - tw(d, rtxt, rf), y + 1), rtxt, font=rf, fill=MUTED)
    y += 14
    # masthead
    mf, _ = fit_size(d, data["masthead"], gloock, CW, 38, 30)
    d.text((MX, y), data["masthead"], font=mf, fill=INK)
    y += th(d, data["masthead"], mf) + 2
    # subline (centred, red italic)
    sf = crim_i(15)
    d.text(((W - tw(d, data["subline"], sf)) / 2, y), data["subline"],
           font=sf, fill=RED)
    y += th(d, data["subline"], sf) + 4
    # region bar (min width 42 for 1-story segments)
    order = ["AMERICAS", "EUROPE", "AFRICA", "MIDEAST", "ASIA-PACIFIC",
             "OCEANIA", "WORLD"]
    cols = {"AMERICAS": INK, "EUROPE": (46, 72, 110), "AFRICA": (90, 110, 140),
            "MIDEAST": RED, "ASIA-PACIFIC": (120, 130, 150),
            "OCEANIA": (70, 90, 120), "WORLD": (150, 140, 120)}
    counts = data["regions"]
    rest = sum(counts[k] for k in order if counts[k] > 1)
    unit = (CW - 2 * 42) / rest
    bx = MX
    for k in order:
        n = counts[k]
        bw = 42 if n == 1 else unit * n
        d.rectangle([bx, y, bx + bw, y + 20], fill=cols[k])
        lab = ("ASIA-PAC 1" if k == "ASIA-PACIFIC"
               else f"{k} {n}")
        lf = mono_b(6) if bw <= 42 else mono_b(7)
        if tw(d, lab, lf) <= bw - 2:
            d.text((bx + (bw - tw(d, lab, lf)) / 2, y + 6), lab, font=lf,
                   fill=(250, 250, 248))
        bx += bw
    y += 20 + 5
    # numbers strip
    y += section_header(d, MX, y, CW, "THE DAY IN NUMBERS")
    y += 3
    nums = data["numbers"]
    cell = CW / len(nums)
    labf = mono(7)
    for i, it in enumerate(nums):
        cx = MX + i * cell
        val = it["value"]
        f2, _ = fit_size(d, val, crim_b, cell - 10, 22, 16)
        d.text((cx + (cell - tw(d, val, f2)) / 2, y), val, font=f2,
               fill=RED if val.startswith("−") else INK)
        lines = wrap(d, it["label"], labf, cell - 8)
        ly = y + 26
        for ln in lines[:2]:
            d.text((cx + (cell - tw(d, ln, labf)) / 2, ly), ln, font=labf,
                   fill=MUTED)
            ly += 10
        if i < len(nums) - 1:
            d.line([(cx + cell, y + 2), (cx + cell, y + 42)], fill=RULE,
                   width=1)
    y += 46 + 6
    # timeline
    y += section_header(d, MX, y, CW, "SATURDAY BY THE HOURS")
    y += 3
    tl = data["timeline"]
    tcell = CW / len(tl)
    tf = mono_b(9)
    ttf = sans(9)
    for i, it in enumerate(tl):
        cx = MX + i * tcell
        d.text((cx, y), it["time"], font=tf, fill=RED)
        lines = wrap(d, it["text"], ttf, tcell - 8)
        ly = y + 13
        for ln in lines[:2]:
            d.text((cx, ly), ln, font=ttf, fill=INK)
            ly += 11
    y += 33 + 6
    # heroes: 3 cards in one row
    hw = (CW - 2 * 14) // 3
    hh = 158
    hf = crim_b(17)
    df = crim(11)
    sf2 = mono(7)
    for i, s in enumerate(data["heroes"]):
        hx = MX + i * (hw + 14)
        scene = SCENES[s["art"]](hw, 52)
        img.paste(scene, (hx, y), scene)
        d.rectangle([hx, y, hx + hw, y + hh], outline=RULE, width=1)
        # number chip on the art band
        d.rounded_rectangle([hx + 8, y + 8, hx + 30, y + 24], radius=4,
                            fill=PAPER)
        nf = mono_b(10)
        num = str(s["n"])
        d.text((hx + 19 - tw(d, num, nf) / 2, y + 10), num, font=nf,
               fill=RED)
        tx = hx + 10
        twid = hw - 20
        ty = y + 52 + 7
        d.text((tx, ty), s["place"], font=mono_b(9), fill=RED)
        tag_pill(d, hx + hw - 10, ty - 1, s["confidence"])
        ty += 13
        hl = wrap(d, s["headline"], hf, twid)
        if len(hl) > 2:
            warns.append(f"hero {s['n']} headline {len(hl)} lines")
            hl = hl[:2]
        for ln in hl:
            d.text((tx, ty), ln, font=hf, fill=INK)
            ty += 20
        ty += 2
        dl = wrap(d, s["deck"], df, twid)
        if len(dl) > 3:
            warns.append(f"hero {s['n']} deck {len(dl)} lines")
            dl = dl[:3]
        for ln in dl:
            d.text((tx, ty), ln, font=df, fill=INK)
            ty += 15
        src = " · ".join(s["sources"])
        d.text((tx, y + hh - 15), src, font=sf2, fill=MUTED)
    y += hh + 7
    # mediums: 2 cols x 5 rows
    y += section_header(d, MX, y, CW, "MORE OF THE DAY")
    y += 3
    mw = (CW - 14) // 2
    mh = 44
    mhf = crim_b(13)
    mdf = sans(9)
    for i, s in enumerate(data["mediums"]):
        col, row = i % 2, i // 2
        mx = MX + col * (mw + 14)
        my = y + row * (mh + 5)
        icon = ICONS[s["art"]]()
        img.paste(icon, (mx, my + 1), icon)
        tx = mx + 50
        twid = mw - 50 - 6
        d.text((tx, my + 1), s["place"], font=mono_b(8), fill=RED)
        src = " · ".join(s["sources"])
        d.text((tx + tw(d, s["place"], mono_b(8)) + 6, my + 2), src,
               font=mono(7), fill=MUTED)
        tag_pill(d, mx + mw, my, s["confidence"])
        hf2, _ = fit_size(d, s["headline"], crim_b, twid, 13, 10)
        d.text((tx, my + 14), s["headline"], font=hf2, fill=INK)
        deck = ellipsize(d, s["deck"], mdf, twid)
        d.text((tx, my + 30), deck, font=mdf, fill=INK)
        if row < 4:
            d.line([(mx, my + mh + 3), (mx + mw, my + mh + 3)], fill=RULE,
                   width=1)
    y += 5 * mh + 4 * 5 + 7
    # map
    y += section_header(d, MX, y, CW, "WHERE IT HAPPENED — PINS 1–13, DOTS 14–35")
    y += 3
    map_h = 100
    draw_map(d, MX, y, CW, map_h, data)
    y += map_h + 7
    # also today: 22 briefs, 3 cols, row-major
    y += section_header(d, MX, y, CW, "ALSO TODAY")
    y += 3
    aw = (CW - 2 * 16) // 3
    for i, s in enumerate(data["also"]):
        row, col = divmod(i, 3)
        ax = MX + col * (aw + 16)
        ay = y + row * 12
        nf = mono_b(9)
        num = str(s["n"])
        d.text((ax, ay), num, font=nf, fill=RED)
        hf3, _ = fit_size(d, s["headline"], crim_b, aw - 22, 10, 8)
        d.text((ax + 20, ay), s["headline"], font=hf3, fill=INK)
    y += 8 * 12 + 7
    # date check box
    box_h = 58
    d.rectangle([MX, y, MX + CW, y + box_h], outline=INK, width=1)
    d.text((MX + 10, y + 5), "DATE CHECK — HELD BACK, NOT SATURDAY",
           font=mono_b(9), fill=RED)
    dcf = sans(8)
    items = data["date_check"]
    for r in range(3):
        for c in range(4):
            it = items[r * 4 + c]
            txt = f"{it['text']} — {it['when']}"
            txt = ellipsize(d, txt, dcf, 226)
            d.text((MX + 10 + c * 238, y + 22 + r * 11), txt, font=dcf,
                   fill=INK)
    y += box_h + 6
    # not yet
    nyf = sans_b(10)
    d.text((MX, y), data["not_yet"], font=nyf, fill=INK)
    y += 13 + 4
    # footers (centred)
    ff = mono(7)
    d.text(((W - tw(d, data["footer_sources"], ff)) / 2, y),
           data["footer_sources"], font=ff, fill=MUTED)
    y += 10
    ff2 = crim_i(10)
    d.text(((W - tw(d, data["footer"], ff2)) / 2, y), data["footer"],
           font=ff2, fill=INK)
    y += 11
    return img, y, warns


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "stories_v2.json")) as fh:
        data = json.load(fh)
    img, final_y, warns = build(data)
    out = os.path.join(here, "entry.png")
    img.save(out, optimize=True)
    import hashlib
    raw = open(out, "rb").read()
    print(f"final_y={final_y} (canvas {H})")
    print(f"entry.png bytes={len(raw)} md5={hashlib.md5(raw).hexdigest()}")
    print(f"stories={len(data['heroes']) + len(data['mediums']) + len(data['also'])}")
    print(f"regions={data['regions']} total={sum(data['regions'].values())}")
    for w in warns:
        print("WARN:", w)


if __name__ == "__main__":
    main()
