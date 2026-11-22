#!/usr/bin/env python3
"""build_frontpage_v3.py — News-21 v2 renderer (round 2).

Fresh implementation written in this session. Renders stories_v3.json
-> entry.png (1024x1024). Pillow + drawsvg/CairoSVG hero scenes +
Lucide icon stamps + a matplotlib mini-chart, all offline and
deterministic. No network at build time: Lucide SVGs are vendored
under vendor/lucide/ (lucide-static 1.77.0, ISC), fonts are local OFL.

Angle: the winners' skeleton at full scale — giant black serif
masthead, 9-region colour bar, 6 sourced numbers, all-Saturday UTC
timeline, 3 large illustrated hero panels (Gulf map / Peru depth
cross-section / COP31 thermometer+calendar), 10 illustrated medium
panels each anchored by a big numeral, region-coloured map pins,
22 sourced briefs in 2 columns, full DATE CHECK + confidence legend.
"""
import io
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 24
CW = W - 2 * MX  # 976

PAPER = (246, 239, 221)
INK = (24, 48, 88)
BLACK = (12, 12, 12)
RED = (180, 35, 24)
MUTED = (112, 106, 92)
RULE = (196, 188, 170)
GREEN = (28, 96, 60)
GREEN_BG = (214, 232, 220)
GREY_BG = (228, 224, 214)
TEAL = (38, 112, 104)
GOLD = (150, 110, 20)

FD = os.path.expanduser(
    "~/workspace/custom-skills/canvas-design/canvas-fonts")
HERE = os.path.dirname(os.path.abspath(__file__))


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
    d.polygon([(x, y - s), (x + s * 0.55, y - s * 0.1),
               (x + s * 0.35, y + s * 0.55), (x - s * 0.35, y + s * 0.55),
               (x - s * 0.55, y - s * 0.1)], fill=c1)
    d.polygon([(x, y - s * 0.55), (x + s * 0.3, y),
               (x + s * 0.18, y + s * 0.4), (x - s * 0.18, y + s * 0.4),
               (x - s * 0.3, y)], fill=c2)


# ---------------------------------------------------------------- fontTools
# Masthead size from exact advance widths (fontTools, audited skill):
# one pass instead of a shrink loop, and the glyph gate below.
def masthead_size(text, target_width, start=64):
    from fontTools.ttLib import TTFont
    path = os.path.join(FD, "Gloock-Regular.ttf")
    f = TTFont(path)
    cmap = f.getBestCmap()
    units = f["head"].unitsPerEm
    total = sum(f["hmtx"][cmap[ord(ch)]][0] for ch in text)
    size = int(target_width * units / total)
    return min(size, start)


def glyph_gate():
    """Assert every special char used on the page exists in its font."""
    from fontTools.ttLib import TTFont
    need = {
        "Gloock-Regular.ttf": "−·éáí–—’‘“”×÷°%*",
        "CrimsonPro-Regular.ttf": "−·éáí–—’‘“”×°%*",
        "CrimsonPro-Bold.ttf": "−·éáí–—’‘“”×°%*",
        "CrimsonPro-Italic.ttf": "−·éáí–—’‘“”×°%*",
        "InstrumentSans-Regular.ttf": "−·éáí–—’‘“”×°%*",
        "InstrumentSans-Bold.ttf": "−·éáí–—’‘“”×°%*",
        "IBMPlexMono-Regular.ttf": "−·éáí–—’‘“”×°%*",
        "IBMPlexMono-Bold.ttf": "−·éáí–—’‘“”×°%*",
    }
    bad = []
    for name, chars in need.items():
        cmap = TTFont(os.path.join(FD, name)).getBestCmap()
        miss = [ch for ch in chars if ord(ch) not in cmap]
        if miss:
            bad.append((name, miss))
    assert not bad, bad


# ---------------------------------------------------------------- Lucide icons
# Vendored under vendor/lucide/ (lucide-static 1.77.0, ISC). Rasterised
# with CairoSVG from a local bytestring only — never url=, never
# unsafe=True. Icons are a precision stamp over the hand-drawn scenes,
# never a replacement for them.
def icon_png(name, px, color, stroke_width=2.5):
    import cairosvg
    path = os.path.join(HERE, "vendor", "lucide", name + ".svg")
    svg = open(path, "rb").read()
    assert b"<script" not in svg.lower() and b"javascript" not in svg.lower()
    svg = svg.replace(b'stroke="currentColor"',
                      ('stroke="%s"' % color).encode())
    svg = svg.replace(b'stroke-width="2"',
                      ('stroke-width="%s"' % stroke_width).encode())
    png = cairosvg.svg2png(bytestring=svg, output_width=px,
                            output_height=px, background_color="transparent")
    return Image.open(io.BytesIO(png)).convert("RGBA")


# ---------------------------------------------------------------- matplotlib
# BTC mini-chart for the Bitcoin medium panel (Agg backend, headless,
# text-free so PIL draws the labels in the page fonts). Values are the
# verified Sat 21 Nov prints: Fri close 58,952 -> Sat low 55,130 ->
# midday 58,091 -> rebound 59,952 -> Sat close 60,216 (Finnhub daily
# candle + Reuters/CoinDesk).
def btc_chart(w, h):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    vals = [58952, 55130, 58091, 59952, 60216]
    fig, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=300)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.plot(range(len(vals)), vals, color="#b42318", linewidth=2.5,
            solid_capstyle="round", zorder=3)
    ax.fill_between(range(len(vals)), vals, 54000, color="#b42318",
                    alpha=0.10, zorder=2)
    ax.scatter([1], [55130], s=42, color="#b42318", zorder=4,
               edgecolor="white", linewidth=1)
    ax.scatter([4], [60216], s=42, color="#1c603c", zorder=4,
               edgecolor="white", linewidth=1)
    ax.set_xlim(-0.15, 4.15)
    ax.set_ylim(54000, 61500)
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True,
                bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA").resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- drawsvg heroes
# Real vector scenes (gradients, Bezier arcs, curves) rasterised via
# CairoSVG from a local bytestring. No embed_google_font(),
# no append_javascript(), no video paths. Text is added by PIL on top
# so every label uses the page fonts.
def _raster_svg(drawing, w, h):
    import cairosvg
    svg = drawing.as_svg().encode()
    png = cairosvg.svg2png(bytestring=svg, output_width=w,
                            output_height=h, background_color="transparent")
    return Image.open(io.BytesIO(png)).convert("RGBA")


def _poly(points, **kw):
    """Polygon via Path (drawsvg has no Polygon class)."""
    import drawsvg as dw
    p = dw.Path(**kw)
    p.M(*points[0])
    for pt in points[1:]:
        p.L(*pt)
    p.Z()
    return p

def scene_bahrain(w, h):
    """Gulf map: dark sea, sand land, Bahrain + 2 tankers hit, arcs."""
    import drawsvg as dw
    S = 3
    d = dw.Drawing(w * S, h * S)
    sea = dw.LinearGradient(0, 0, 0, 1)
    sea.add_stop(0, "#22355e")
    sea.add_stop(1, "#101c38")
    d.append(dw.Rectangle(0, 0, w * S, h * S, fill=sea))
    sand = "#d8cdb2"
    # Iran coast (top)
    d.append(_poly([(330, 0), (939, 0), (939, 66), (860, 78),
                         (760, 64), (660, 84), (560, 70), (470, 88),
                         (400, 70), (330, 78)], fill=sand))
    # Arabian peninsula (left + bottom)
    d.append(_poly([(0, 150), (150, 118), (280, 132), (360, 176),
                         (392, 210), (360, 264), (300, 264), (240, 220),
                         (150, 210), (60, 240), (0, 264)], fill=sand))
    # Qatar bump
    d.append(_poly([(392, 176), (430, 168), (442, 196), (420, 214),
                         (396, 204)], fill=sand))
    # Musandam / Oman tip (right, where Khasab sits)
    d.append(_poly([(700, 96), (770, 84), (830, 104), (820, 140),
                         (760, 150), (710, 132)], fill=sand))
    # Bahrain island
    d.append(dw.Ellipse(398, 196, 10, 14, fill="#f6efdd",
                        stroke="#b42318", stroke_width=3))
    # missile arcs (Iran -> Bahrain), dashed Bezier
    for (x0, y0, cx, cy, x1, y1) in [
            (620, 66, 520, 90, 398, 196),
            (700, 70, 580, 130, 398, 196),
            (540, 78, 470, 120, 398, 196)]:
        p = dw.Path(stroke="#ff9666", stroke_width=4, fill="none",
                    stroke_dasharray="14 10", stroke_linecap="round")
        p.M(x0, y0).Q(cx, cy, x1, y1)
        d.append(p)
    # strike burst over Bahrain
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x2 = 398 + 34 * math.cos(a)
        y2 = 196 + 34 * math.sin(a)
        d.append(dw.Line(398, 196, x2, y2, stroke="#ffb050",
                         stroke_width=5, stroke_linecap="round"))
    d.append(dw.Circle(398, 196, 16, fill="#ffbe50"))
    d.append(dw.Circle(398, 196, 8, fill="#fff0c8"))
    # two tankers near Khasab (small hulls + fire)
    for (tx, ty) in [(742, 168), (806, 132)]:
        d.append(dw.Rectangle(tx - 26, ty - 7, 52, 14, fill="#e8e2d2",
                              stroke="#101c38", stroke_width=2))
        d.append(dw.Rectangle(tx - 8, ty - 16, 16, 9, fill="#e8e2d2",
                              stroke="#101c38", stroke_width=2))
        d.append(dw.Circle(tx, ty - 24, 10, fill="#ff7a3c"))
        d.append(dw.Circle(tx, ty - 24, 5, fill="#ffd23c"))
    # Strait of Hormuz label arrow (text added by PIL)
    return _raster_svg(d, w, h)


def scene_peru(w, h):
    """Depth cross-section: sky, mountains, earth layers, hypocentre."""
    import drawsvg as dw
    S = 3
    d = dw.Drawing(w * S, h * S)
    sky = dw.LinearGradient(0, 0, 0, 0.55)
    sky.add_stop(0, "#c6d8e4")
    sky.add_stop(1, "#e8e2d2")
    d.append(dw.Rectangle(0, 0, w * S, h * S * 0.55, fill=sky))
    # sun
    d.append(dw.Circle(850, 42, 26, fill="#faf0d0"))
    # mountains
    d.append(_poly([(0, 165), (150, 66), (300, 165)], fill="#96a8b8"))
    d.append(_poly([(220, 165), (420, 48), (620, 165)], fill="#7a90a4"))
    d.append(_poly([(520, 165), (700, 78), (939, 165)], fill="#96a8b8"))
    # snow caps
    for (cx, cy, s) in [(150, 66, 26), (420, 48, 30), (700, 78, 24)]:
        d.append(_poly([(cx - s, cy + s * 0.7), (cx, cy),
                             (cx + s, cy + s * 0.7)], fill="#fafafa"))
    # ground line + earth layers
    d.append(dw.Rectangle(0, 165, w * S, h * S - 165, fill="#b09a7a"))
    d.append(dw.Rectangle(0, 205, w * S, h * S - 205, fill="#8a6f52"))
    d.append(dw.Rectangle(0, 240, w * S, h * S - 240, fill="#6e563e"))
    # fault line (diagonal crack from surface down to hypocentre)
    p = dw.Path(stroke="#4a3826", stroke_width=5, fill="none",
                stroke_linecap="round")
    p.M(470, 165).L(500, 200).L(486, 232).L(512, 258)
    d.append(p)
    # depth markers: horizontal dashed lines at 108 / 129 km band
    for yy, col in [(222, "#f6efdd"), (246, "#f6efdd")]:
        d.append(dw.Line(40, yy, 900, yy, stroke=col, stroke_width=2,
                         stroke_dasharray="10 8", opacity=0.7))
    # hypocentre star
    hx, hy = 500, 234
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x2 = hx + 26 * math.cos(a)
        y2 = hy + 26 * math.sin(a)
        d.append(dw.Line(hx, hy, x2, y2, stroke="#ff5a3c",
                         stroke_width=6, stroke_linecap="round"))
    d.append(dw.Circle(hx, hy, 13, fill="#ff5a3c", stroke="white",
                       stroke_width=3))
    # shaking lines at the surface above the hypocentre
    for dx in (-46, -28, 28, 46):
        d.append(dw.Line(470 + dx, 150, 470 + dx, 128, stroke="#b42318",
                         stroke_width=4, stroke_linecap="round"))
    # small houses on the surface
    for bx in (120, 210, 640, 730):
        d.append(dw.Rectangle(bx, 138, 34, 27, fill="#f6efdd",
                              stroke="#4a3826", stroke_width=2))
        d.append(_poly([(bx - 3, 138), (bx + 17, 122),
                             (bx + 37, 138)], fill="#b42318"))
    return _raster_svg(d, w, h)


def scene_cop31(w, h):
    """Thermometer 1.5C + Nov 9-21 calendar with +1 day."""
    import drawsvg as dw
    S = 3
    d = dw.Drawing(w * S, h * S)
    bg = dw.LinearGradient(0, 0, 1, 0)
    bg.add_stop(0, "#26706a")
    bg.add_stop(1, "#174f4a")
    d.append(dw.Rectangle(0, 0, w * S, h * S, fill=bg))
    # globe, left
    cx, cy, r = 150, 132, 96
    d.append(dw.Circle(cx, cy, r, fill="#eee8d6"))
    d.append(dw.Circle(cx, cy, r, fill="none", stroke="#174f4a",
                       stroke_width=4))
    d.append(dw.Ellipse(cx - 52, cy - 44, 34, 22, fill="#26706a"))
    d.append(dw.Ellipse(cx + 12, cy + 18, 40, 26, fill="#26706a"))
    d.append(dw.Ellipse(cx + 30, cy - 58, 24, 16, fill="#26706a"))
    d.append(dw.Line(cx - r, cy, cx + r, cy, stroke="#26706a",
                     stroke_width=3))
    d.append(dw.Line(cx, cy - r, cx, cy + r, stroke="#26706a",
                     stroke_width=3))
    # thermometer, centre
    tx = 330
    d.append(dw.Rectangle(tx - 22, 36, 44, 180, rx=22, fill="#eee8d6"))
    d.append(dw.Rectangle(tx - 12, 96, 24, 108, rx=12, fill="#b42318"))
    d.append(dw.Circle(tx, 228, 34, fill="#eee8d6"))
    d.append(dw.Circle(tx, 228, 22, fill="#b42318"))
    for yy in (48, 84, 120, 156, 192):
        d.append(dw.Line(tx + 22, yy, tx + 38, yy, stroke="#eee8d6",
                         stroke_width=3))
    # red mercury top marker line at 1.5C
    d.append(dw.Line(tx - 12, 96, tx + 12, 96, stroke="#7d130c",
                     stroke_width=3))
    # calendar grid Nov 9-21 (13 cells) + one "+1" cell, right
    gx, gy = 420, 40
    cw, ch, gap = 58, 52, 8
    for i in range(13):
        col, row = i % 5, i // 5
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        last = (i == 12)
        fill = "#b42318" if last else "#eee8d6"
        d.append(dw.Rectangle(x, y, cw, ch, rx=8, fill=fill,
                              stroke="#174f4a", stroke_width=2))
    # +1 day cell (outline, dashed)
    x = gx + 3 * (cw + gap)
    y = gy + 2 * (ch + gap)
    d.append(dw.Rectangle(x, y, cw, ch, rx=8, fill="none",
                          stroke="#ffd23c", stroke_width=4,
                          stroke_dasharray="12 8"))
    # overtime clock, far right top
    kx, ky, kr = 880, 66, 30
    d.append(dw.Circle(kx, ky, kr, fill="#eee8d6"))
    d.append(dw.Circle(kx, ky, kr, fill="none", stroke="#174f4a",
                       stroke_width=4))
    d.append(dw.Line(kx, ky, kx, ky - 20, stroke="#182038",
                     stroke_width=4, stroke_linecap="round"))
    d.append(dw.Line(kx, ky, kx + 14, ky + 8, stroke="#182038",
                     stroke_width=4, stroke_linecap="round"))
    d.append(dw.Circle(kx, ky, 4, fill="#b42318"))
    return _raster_svg(d, w, h)


# ---------------------------------------------------------------- medium art
# Each draws a flat-vector panel at 2x on a 124x112 canvas, downscaled
# to the card's art panel. A Lucide icon stamp (white, on a small
# accent disc) sits at the panel's top-right corner.
def _panel_base(bg):
    img = Image.new("RGBA", (124, 112), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 123, 111], radius=8, fill=bg)
    return img, d


def _finish_panel(img):
    return img.resize((62, 56), Image.LANCZOS)


def art_cepa():
    img, d = _panel_base((232, 228, 214))
    # document
    d.rounded_rectangle([14, 14, 78, 98], radius=4, fill=(250, 250, 248))
    d.polygon([(78, 14), (78, 28), (64, 14)], fill=(200, 200, 196))
    for yy in (30, 42, 54, 66, 78):
        d.line([(22, yy), (70, yy)], fill=(120, 130, 140), width=3)
    d.line([(22, 90), (52, 90)], fill=RED, width=4)
    # EU stars circle
    for k in range(12):
        a = math.radians(k * 30)
        x = 100 + 16 * math.cos(a)
        y = 40 + 16 * math.sin(a)
        d.polygon(star_points(x, y, 4, 2), fill=(212, 160, 40))
    d.rectangle([88, 62, 112, 86], fill=(0, 51, 153))
    d.rectangle([88, 74, 112, 86], fill=(250, 250, 248))
    d.rectangle([88, 62, 112, 74], fill=(200, 40, 40))
    return _finish_panel(img)


def art_sparta():
    img, d = _panel_base((238, 226, 210))
    d.rectangle([0, 88, 123, 111], fill=(96, 140, 176))
    d.arc([8, 94, 60, 108], 0, 180, fill=(240, 244, 248), width=2)
    d.arc([66, 94, 118, 108], 0, 180, fill=(240, 244, 248), width=2)
    d.polygon([(18, 88), (106, 88), (96, 68), (28, 68)], fill=(40, 52, 70))
    d.rectangle([32, 48, 48, 68], fill=(200, 60, 40))
    d.rectangle([50, 48, 66, 68], fill=(40, 90, 120))
    d.rectangle([68, 48, 84, 68], fill=(212, 160, 40))
    d.rectangle([88, 50, 102, 68], fill=(240, 244, 248))
    flame(d, 42, 44, 13, (255, 140, 40), (255, 210, 90))
    flame(d, 78, 44, 10, (255, 140, 40), (255, 210, 90))
    circle(d, 42, 22, 6, fill=(120, 120, 118))
    circle(d, 52, 14, 8, fill=(140, 140, 138))
    return _finish_panel(img)


def art_bepi():
    img, d = _panel_base((232, 228, 214))
    circle(d, 66, 70, 30, fill=(216, 164, 110))
    circle(d, 56, 60, 7, fill=(198, 142, 88))
    circle(d, 80, 82, 8, fill=(198, 142, 88))
    circle(d, 74, 54, 5, fill=(198, 142, 88))
    d.rectangle([20, 20, 50, 36], fill=INK)
    d.rectangle([6, 24, 20, 32], fill=(90, 110, 140))
    d.rectangle([50, 24, 66, 32], fill=(90, 110, 140))
    d.arc([50, 6, 74, 30], 270, 90, fill=INK, width=4)
    d.line([(50, 28), (64, 18)], fill=INK, width=3)
    d.arc([-18, 84, 116, 166], 300, 30, fill=MUTED, width=3)
    return _finish_panel(img)


def art_robot():
    img, d = _panel_base((228, 230, 238))
    gx, gy = 92, 88
    circle(d, gx, gy, 15, fill=(176, 184, 196))
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x0 = gx + 15 * math.cos(a)
        y0 = gy + 15 * math.sin(a)
        x1 = gx + 22 * math.cos(a)
        y1 = gy + 22 * math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=(176, 184, 196), width=7)
    circle(d, gx, gy, 6, fill=PAPER)
    d.rounded_rectangle([20, 26, 82, 76], radius=11, fill=INK)
    d.line([(51, 26), (51, 14)], fill=INK, width=4)
    circle(d, 51, 12, 5, fill=RED)
    circle(d, 37, 48, 6, fill=(250, 250, 248))
    circle(d, 65, 48, 6, fill=(250, 250, 248))
    d.line([(39, 63), (63, 63)], fill=(250, 250, 248), width=3)
    d.rectangle([14, 44, 20, 60], fill=INK)
    d.rectangle([82, 44, 88, 60], fill=INK)
    return _finish_panel(img)


def art_mexico():
    img, d = _panel_base((238, 232, 214))
    circle(d, 38, 62, 19, outline=INK, width=7)
    circle(d, 86, 62, 19, outline=INK, width=7)
    d.line([(55, 54), (69, 54)], fill=INK, width=4)
    d.line([(55, 70), (69, 70)], fill=INK, width=4)
    d.polygon(star_points(62, 30, 15, 6), fill=(212, 160, 40))
    circle(d, 62, 30, 4, fill=(250, 250, 248))
    return _finish_panel(img)


def art_bitcoin():
    # matplotlib chart as the panel background, gold coin on top.
    chart = btc_chart(124, 112)
    img = Image.new("RGBA", (124, 112), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 123, 111], radius=8, fill=(244, 238, 226))
    img.paste(chart, (0, 0), chart)
    # gold coin, top-left
    circle(d, 26, 26, 17, fill=(240, 180, 40), outline=(150, 110, 20),
           width=2)
    d.text((26 - 6, 15), "B", font=sans_b(20), fill=(120, 80, 10))
    return _finish_panel(img)


def art_davao():
    img, d = _panel_base((210, 226, 238))
    vgrad(d, 0, 0, 123, 70, (150, 190, 220), (220, 232, 240))
    circle(d, 104, 16, 10, fill=(250, 244, 214))
    # runway
    d.polygon([(0, 111), (123, 111), (123, 88), (0, 96)], fill=(70, 76, 84))
    for i in range(6):
        x = 8 + i * 20
        d.line([(x, 104), (x + 10, 103)], fill=(250, 250, 248), width=2)
    # plane (side view, descending)
    d.ellipse([22, 52, 92, 72], fill=INK)
    d.polygon([(86, 56), (108, 50), (108, 60), (86, 64)], fill=INK)
    d.rectangle([34, 72, 78, 80], fill=INK)
    d.polygon([(58, 72), (74, 72), (66, 88)], fill=INK)
    for wx in (38, 52, 66, 80):
        d.rectangle([wx, 57, wx + 6, 63], fill=(200, 220, 240))
    # emergency slide (yellow) + people dots
    d.polygon([(92, 72), (112, 96), (104, 96), (88, 76)], fill=(240, 200, 40))
    for (px, py) in [(100, 100), (108, 104), (90, 104)]:
        circle(d, px, py, 3, fill=RED)
    return _finish_panel(img)


def art_banda():
    img, d = _panel_base((200, 222, 232))
    # sea waves
    for yy in (66, 80, 94):
        pts = []
        for x in range(0, 125, 6):
            pts.append((x, yy + 5 * math.sin(x / 14)))
        d.line(pts, fill=(40, 90, 130), width=3)
    # island + palm
    d.polygon([(44, 66), (80, 66), (62, 44)], fill=(28, 96, 60))
    d.line([(62, 44), (62, 26)], fill=(90, 70, 40), width=3)
    for ang in (-50, -20, 10, 40):
        a = math.radians(ang - 90)
        d.line([(62, 26), (62 + 16 * math.cos(a), 26 + 16 * math.sin(a))],
               fill=(28, 96, 60), width=3)
    # seismograph spike
    d.line([(0, 30), (30, 30), (40, 18), (50, 44), (60, 22), (70, 36),
            (82, 30), (123, 30)], fill=RED, width=3, joint="curve")
    return _finish_panel(img)


def art_france():
    img, d = _panel_base((240, 228, 216))
    # crowd: rows of heads + shoulders
    for (hx, hy, r, c) in [(22, 78, 10, INK), (48, 72, 11, (90, 60, 40)),
                           (74, 80, 10, RED), (100, 74, 11, TEAL),
                           (36, 52, 9, TEAL), (62, 48, 10, INK),
                           (88, 54, 9, (90, 60, 40))]:
        circle(d, hx, hy, r, fill=c)
        d.arc([hx - r, hy + 2, hx + r, hy + r + 12], 0, 180, fill=c, width=9)
    # placards
    d.rectangle([14, 18, 46, 38], fill=(250, 250, 248),
                outline=INK, width=2)
    d.line([(30, 38), (30, 50)], fill=INK, width=3)
    d.rectangle([78, 14, 110, 34], fill=(250, 250, 248),
                outline=RED, width=2)
    d.line([(94, 34), (94, 46)], fill=INK, width=3)
    d.line([(20, 28), (40, 28)], fill=RED, width=3)
    d.line([(84, 24), (104, 24)], fill=INK, width=3)
    return _finish_panel(img)


def art_rugby():
    img, d = _panel_base((214, 232, 210))
    # pitch stripes
    for i in range(4):
        d.rectangle([0, i * 28, 123, (i + 1) * 28],
                    fill=(46, 125, 70) if i % 2 == 0 else (56, 140, 80))
    # goal posts
    d.line([(96, 12), (96, 58)], fill=(250, 250, 248), width=4)
    d.line([(116, 12), (116, 58)], fill=(250, 250, 248), width=4)
    d.line([(96, 52), (116, 52)], fill=(250, 250, 248), width=4)
    # ball (rotated ellipse on its own layer)
    ball = Image.new("RGBA", (72, 44), (0, 0, 0, 0))
    bd = ImageDraw.Draw(ball)
    bd.ellipse([2, 2, 70, 42], fill=(150, 90, 50),
               outline=(90, 50, 20), width=2)
    bd.line([(36, 4), (36, 40)], fill=(250, 250, 248), width=3)
    bd.line([(28, 14), (44, 14)], fill=(250, 250, 248), width=2)
    bd.line([(28, 30), (44, 30)], fill=(250, 250, 248), width=2)
    ball = ball.rotate(-24, expand=True, resample=Image.BICUBIC)
    img.paste(ball, (8, 52), ball)
    return _finish_panel(img)


MEDIUM_ART = {
    "cepa": (art_cepa, "scroll-text"),
    "sparta": (art_sparta, "ship"),
    "bepi": (art_bepi, "satellite"),
    "robot": (art_robot, "bot"),
    "mexico": (art_mexico, "shield"),
    "bitcoin": (art_bitcoin, "bitcoin"),
    "davao": (art_davao, "plane"),
    "banda": (art_banda, "activity"),
    "france": (art_france, "users"),
    "rugby": (art_rugby, "trophy"),
}
SCENES = {"bahrain": scene_bahrain, "peru": scene_peru, "cop31": scene_cop31}
# PIL labels drawn over the drawsvg hero scenes (panel coords, 313 wide).
HERO_LABELS = {
    # panel coords (317 x hero_art_h); INK on sand land, white on sea.
    "bahrain": [("IRAN", 248, 3, 9, INK),
                ("BAHRAIN", 150, 58, 9, (255, 255, 255)),
                ("2 TANKERS HIT", 196, 66, 9, (255, 210, 90))],
    "peru": [("M6.7", 182, 74, 9, (52, 38, 24)),
             ("LIMA", 228, 6, 9, INK)],
    "cop31": [("1.5°C", 96, 1, 10, (250, 250, 248)),
              ("NOV 9–21", 140, 1, 9, (250, 250, 248)),
              ("+1 DAY", 198, 70, 9, (255, 210, 60))],
}


# ---------------------------------------------------------------- land mask
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


REGION_COLOURS = {
    "EUROPE": (46, 72, 110),
    "AMERICAS": (24, 48, 88),
    "MIDDLE EAST": (180, 35, 24),
    "EAST ASIA": (38, 112, 104),
    "SE ASIA": (150, 110, 20),
    "OCEANIA": (90, 110, 140),
    "SOUTH ASIA": (120, 90, 140),
    "AFRICA": (28, 96, 60),
    "GLOBAL": (112, 106, 92),
}
REGION_SHORT = {
    "EUROPE": "EUROPE", "AMERICAS": "AMERICAS",
    "MIDDLE EAST": "MIDEAST", "EAST ASIA": "E ASIA",
    "SE ASIA": "SE ASIA", "OCEANIA": "OCEANIA",
    "SOUTH ASIA": "S ASIA", "AFRICA": "AFRICA", "GLOBAL": "GLOBAL",
}


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


def section_header(d, x, y, width, label):
    f = mono_b(9)
    tracked(d, x, y, label, f, RED, spacing=2)
    lw = tw(d, label, f) + 2 * len(label)
    d.line([(x + lw + 8, y + 5), (x + width, y + 5)], fill=RULE, width=1)
    return 12


# ---------------------------------------------------------------- map
def draw_map(d, x0, y0, w, h, stories):
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

    for s in stories["also"]:
        bx, by = proj(s["lat"], s["lon"])
        rng = random.Random(s["n"])
        jx = bx + rng.uniform(-3, 3)
        jy = by + rng.uniform(-3, 3)
        circle(d, jx, jy, 2.4, fill=(150, 158, 168))
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
        col = REGION_COLOURS[s["region"]]
        if (fx, fy) != (bx, by):
            d.line([(bx, by), (fx, fy)], fill=MUTED, width=1)
            circle(d, bx, by, 2.2, fill=col)
        circle(d, fx, fy, 7.5, fill=col)
        nf = mono_b(8)
        num = str(s["n"])
        d.text((fx - tw(d, num, nf) / 2, fy - 5), num, font=nf,
               fill=(250, 250, 248))


# ---------------------------------------------------------------- page build
def build(data, cfg):
    hero_art_h = cfg["hero_art"]
    med_h = cfg["med"]
    map_h = cfg["map"]
    brief_row = cfg["brief_row"]
    dc_row = cfg["dc_row"]
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    warns = []
    y = 6
    # eyebrow
    ef = mono_b(9)
    tracked(d, MX, y, "THE WORLD IN ONE DAY · DAY 325 OF 2026 · ALL TIMES UTC",
            ef, INK, spacing=2)
    rf = mono(8)
    rtxt = "35 STORIES · 9 REGIONS · DATED SATURDAY 21 NOV 2026"
    d.text((W - MX - tw(d, rtxt, rf), y + 1), rtxt, font=rf, fill=MUTED)
    y += 12
    # masthead: giant BLACK serif, no comma, full width (fontTools size)
    msize = masthead_size(data["masthead"], CW, start=62)
    mf = gloock(msize)
    d.text((MX, y), data["masthead"], font=mf, fill=BLACK)
    y += th(d, data["masthead"], mf) + 2
    # subline (centred, red italic)
    sf = crim_i(14)
    d.text(((W - tw(d, data["subline"], sf)) / 2, y), data["subline"],
           font=sf, fill=RED)
    y += th(d, data["subline"], sf) + 5
    # region bar: 9 colourful segments, widths proportional to counts
    order = ["EUROPE", "AMERICAS", "MIDDLE EAST", "EAST ASIA", "SE ASIA",
             "OCEANIA", "SOUTH ASIA", "AFRICA", "GLOBAL"]
    counts = data["regions"]
    total = sum(counts.values())
    unit = CW / total
    bx = MX
    for k in order:
        n = counts[k]
        bw = unit * n
        if k == order[-1]:
            bw = MX + CW - bx
        d.rectangle([bx, y, bx + bw, y + 16], fill=REGION_COLOURS[k])
        lab = f"{REGION_SHORT[k]} {n}"
        lf = mono_b(7)
        if tw(d, lab, lf) <= bw - 4:
            d.text((bx + (bw - tw(d, lab, lf)) / 2, y + 4), lab, font=lf,
                   fill=(250, 250, 248))
        else:
            warns.append(f"region label {k} does not fit")
        bx += bw
    y += 16 + 3
    # numbers strip: 6 huge figures, label + source on one line each
    y += section_header(d, MX, y, CW, "THE DAY IN NUMBERS")
    y += 2
    nums = data["numbers"]
    cell = CW / len(nums)
    labf = mono(7)
    srcf = mono(6)
    for i, it in enumerate(nums):
        cx = MX + i * cell
        val = it["value"]
        f2, _ = fit_size(d, val, crim_b, cell - 10, 23, 16)
        d.text((cx + (cell - tw(d, val, f2)) / 2, y), val, font=f2, fill=INK)
        lab = ellipsize(d, it["label"], labf, cell - 6)
        d.text((cx + (cell - tw(d, lab, labf)) / 2, y + 25), lab,
               font=labf, fill=MUTED)
        src = it["source"]
        d.text((cx + (cell - tw(d, src, srcf)) / 2, y + 34), src,
               font=srcf, fill=MUTED)
        if i < len(nums) - 1:
            d.line([(cx + cell, y + 2), (cx + cell, y + 40)], fill=RULE,
                   width=1)
    y += 44 + 4
    # timeline: all-Saturday UTC times
    y += section_header(d, MX, y, CW, "THE DAY IN UTC")
    y += 2
    tl = data["timeline"]
    tcell = CW / len(tl)
    tf = mono_b(9)
    ttf = sans(9)
    for i, it in enumerate(tl):
        cx = MX + i * tcell
        d.text((cx, y), it["time"], font=tf, fill=RED)
        lines = wrap(d, it["text"], ttf, tcell - 8)
        ly = y + 12
        for ln in lines[:1]:
            d.text((cx, ly), ln, font=ttf, fill=INK)
            ly += 11
        if len(lines) > 1:
            warns.append(f"timeline {it['time']} wraps to {len(lines)}")
    y += 23 + 5
    # heroes: 3 large illustrated panels
    hw = (CW - 2 * 12) // 3
    hh = hero_art_h + 5 + 12 + 34 + 24 + 9 + 3
    hf = crim_b(16)
    df = crim(11)
    sf2 = mono(7)
    for i, s in enumerate(data["heroes"]):
        hx = MX + i * (hw + 12)
        # Scenes are authored at a fixed 96px panel height (their
        # absolute coordinates assume it). Composite scene + PIL
        # labels at 96px, then downscale to the configured art height
        # so nothing is ever clipped by a shorter panel.
        scene = SCENES[s["art"]](hw, 96)
        panel = Image.new("RGBA", (hw, 96), (0, 0, 0, 0))
        panel.paste(scene, (0, 0), scene)
        pd = ImageDraw.Draw(panel)
        for (txt, lx, ly, lsz, col) in HERO_LABELS[s["art"]]:
            pd.text((lx, ly), txt, font=mono_b(lsz), fill=col)
        if hero_art_h != 96:
            panel = panel.resize((hw, hero_art_h), Image.LANCZOS)
        img.paste(panel, (hx, y), panel)
        d.rectangle([hx, y, hx + hw, y + hh], outline=RULE, width=1)
        d.rounded_rectangle([hx + 8, y + 8, hx + 30, y + 24], radius=4,
                            fill=PAPER)
        nf = mono_b(10)
        num = str(s["n"])
        d.text((hx + 19 - tw(d, num, nf) / 2, y + 10), num, font=nf,
               fill=RED)
        tx = hx + 10
        twid = hw - 20
        ty = y + hero_art_h + 5
        d.text((tx, ty), s["place"], font=mono_b(9), fill=RED)
        tag_pill(d, hx + hw - 10, ty - 1, s["confidence"])
        ty += 13
        hl = wrap(d, s["headline"], hf, twid)
        if len(hl) > 2:
            warns.append(f"hero {s['n']} headline {len(hl)} lines")
            hl = hl[:2]
        for ln in hl:
            d.text((tx, ty), ln, font=hf, fill=INK)
            ty += 17
        dl = wrap(d, s["deck"], df, twid)
        if len(dl) > 2:
            warns.append(f"hero {s['n']} deck {len(dl)} lines")
            dl = dl[:2]
        for ln in dl:
            d.text((tx, ty), ln, font=df, fill=INK)
            ty += 12
        src = " · ".join(s["sources"])
        d.text((tx, y + hh - 13), src, font=sf2, fill=MUTED)
    y += hh + 5
    # mediums: 2 cols x 5 rows, illustrated panel + big numeral
    y += section_header(d, MX, y, CW, "MORE OF THE DAY")
    y += 3
    mw = (CW - 12) // 2
    mhf = crim_b(13)
    numf = crim_b(19)
    mdf = sans(9)
    mpf = mono_b(8)
    msf = mono(7)
    for i, s in enumerate(data["mediums"]):
        col, row = i % 2, i // 2
        mx = MX + col * (mw + 12)
        my = y + row * (med_h + 2)
        art_fn, icon_name = MEDIUM_ART[s["art"]]
        art = art_fn()
        img.paste(art, (mx, my + (med_h - 56) // 2), art)
        # Lucide stamp on a small accent disc, top-right of the panel
        disc_cx, disc_cy = mx + 62 - 13, my + (med_h - 56) // 2 + 13
        circle(d, disc_cx, disc_cy, 11, fill=RED)
        ic = icon_png(icon_name, 15, "#ffffff", stroke_width=2.5)
        img.paste(ic, (disc_cx - 7, disc_cy - 7), ic)
        tx = mx + 68
        twid = mw - 68 - 6
        d.text((tx, my + 1), s["place"], font=mpf, fill=RED)
        src = " · " + " · ".join(s["sources"])
        sx = tx + tw(d, s["place"], mpf) + 5
        d.text((sx, my + 2), src, font=msf, fill=MUTED)
        tag_pill(d, mx + mw, my, s["confidence"])
        # numeral + headline on one line
        num_w = tw(d, s["numeral"], numf)
        d.text((tx, my + 13), s["numeral"], font=numf, fill=RED)
        hf2, _ = fit_size(d, s["headline"], crim_b, twid - num_w - 8, 13, 10)
        d.text((tx + num_w + 8, my + 16), s["headline"], font=hf2,
               fill=INK)
        deck = ellipsize(d, s["deck"], mdf, twid)
        d.text((tx, my + 37), deck, font=mdf, fill=INK)
        if row < 4:
            d.line([(mx, my + med_h + 1), (mx + mw, my + med_h + 1)],
                   fill=RULE, width=1)
    y += 5 * med_h + 4 * 2 + 5
    # map: region-coloured pins + legend in the header line
    y += section_header(d, MX, y, CW,
                        "WHERE IT HAPPENED — PINS 1–13 IN REGION COLOURS, DOTS 14–35")
    y += 3
    draw_map(d, MX, y, CW, map_h, data)
    y += map_h + 5
    # briefs: 22, 2 columns, source after every brief
    y += section_header(d, MX, y, CW, "ALSO ON SATURDAY 21 NOVEMBER 2026")
    y += 3
    bw2 = (CW - 16) // 2
    for i, s in enumerate(data["also"]):
        row, col = divmod(i, 2)
        ax = MX + col * (bw2 + 16)
        ay = y + row * brief_row
        nf = mono_b(9)
        num = str(s["n"])
        d.text((ax, ay), num, font=nf, fill=RED)
        src = " · " + " · ".join(s["sources"])
        srcf = mono(7)
        src_w = tw(d, src, srcf)
        hf3, _ = fit_size(d, s["headline"], crim_b, bw2 - 22 - src_w - 4,
                          10, 8)
        d.text((ax + 20, ay), s["headline"], font=hf3, fill=INK)
        hx = ax + 20 + tw(d, s["headline"], hf3) + 4
        d.text((hx, ay + 1), src, font=srcf, fill=MUTED)
    y += 11 * brief_row + 5
    # date check box: 18 exclusions, 4 cols x 5 rows
    box_h = 13 + 5 * dc_row + 5
    d.rectangle([MX, y, MX + CW, y + box_h], outline=INK, width=1)
    d.text((MX + 10, y + 4), "DATE CHECK — HELD BACK, NOT SATURDAY",
           font=mono_b(9), fill=RED)
    ncf = mono(7)
    nct = data["not_confirmed"]
    d.text((MX + CW - 10 - tw(d, nct, ncf), y + 5), nct, font=ncf,
           fill=MUTED)
    dcf = sans(8)
    items = data["date_check"]
    colw = (CW - 20) / 4
    for idx, it in enumerate(items):
        r, c = divmod(idx, 4)
        txt = f"{it['text']} — {it['when']}"
        txt = ellipsize(d, txt, dcf, colw - 6)
        d.text((MX + 10 + c * colw, y + 17 + r * dc_row), txt, font=dcf,
               fill=INK)
    y += box_h + 4
    # footer: not yet / claim / legend / sources
    nyf = sans_b(9)
    d.text((MX, y), data["not_yet"], font=nyf, fill=INK)
    y += 11
    ff2 = crim_i(10)
    d.text(((W - tw(d, data["footer"], ff2)) / 2, y), data["footer"],
           font=ff2, fill=INK)
    y += 11
    lgf = mono(7)
    d.text(((W - tw(d, data["legend"], lgf)) / 2, y), data["legend"],
           font=lgf, fill=MUTED)
    y += 9
    ff = mono(7)
    d.text(((W - tw(d, data["footer_sources"], ff)) / 2, y),
           data["footer_sources"], font=ff, fill=MUTED)
    y += 9
    return img, y, warns


CONFIGS = [
    {"hero_art": 80, "med": 52, "map": 76, "brief_row": 9.5, "dc_row": 9.5},
    {"hero_art": 76, "med": 51, "map": 74, "brief_row": 9.5, "dc_row": 9},
    {"hero_art": 72, "med": 50, "map": 72, "brief_row": 9, "dc_row": 9},
    {"hero_art": 68, "med": 49, "map": 70, "brief_row": 9, "dc_row": 8.5},
]


def main():
    glyph_gate()
    with open(os.path.join(HERE, "stories_v3.json")) as fh:
        data = json.load(fh)
    n_stories = (len(data["heroes"]) + len(data["mediums"])
                 + len(data["also"]))
    assert n_stories == 35, n_stories
    assert sum(data["regions"].values()) == 35
    assert len(data["regions"]) == 9
    assert len(data["date_check"]) == 18
    results = []
    for cfg in CONFIGS:
        img, final_y, warns = build(data, cfg)
        print(f"cfg={cfg} final_y={final_y} warns={warns}")
        results.append((img, final_y, cfg, warns))
    fitting = [r for r in results if r[1] <= 1016 and not r[3]]
    if fitting:
        img, final_y, cfg, warns = fitting[0]
    else:
        img, final_y, cfg, warns = min(results, key=lambda r: r[1])
        print("WARNING: no config fits in 1016px without warnings")
    print(f"PICKED cfg={cfg} final_y={final_y} warns={warns}")
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    import hashlib
    raw = open(out, "rb").read()
    print(f"entry.png bytes={len(raw)} md5={hashlib.md5(raw).hexdigest()}")
    print(f"stories={n_stories} regions={data['regions']}")


if __name__ == "__main__":
    main()
