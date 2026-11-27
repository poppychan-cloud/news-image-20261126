#!/usr/bin/env python3
"""Render entry.png for news-image-20261126 V2 from stories.json.
Deterministic: no network, no clock, no randomness. PIL only, stdlib only.
Usage: python3 draw.py   (writes entry.png next to this file, prints a report)
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
    DATA = json.load(f)

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (185, 28, 28)
NAVY = (22, 48, 84)
BLUE = (31, 95, 168)
GREY = (96, 96, 96)
LIGHT = (232, 226, 214)
GREEN = (27, 107, 58)
TEAL = (15, 118, 110)
AMBER = (180, 83, 9)
LAND = (216, 203, 176)
SEA = (233, 238, 242)
GOLD = (212, 175, 55)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def f_serif_b(s):
    return font("DejaVuSerif-Bold.ttf", s)


def f_serif(s):
    return font("DejaVuSerif.ttf", s)


def f_sans(s):
    return font("DejaVuSans.ttf", s)


def f_sans_b(s):
    return font("DejaVuSans-Bold.ttf", s)


PROBLEMS = {"trims": 0, "overflows": 0}


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, text, fnt, x, y, max_w, max_lines, leading, color=INK):
    """Draw wrapped text inside a box; count a trim if it does not fit."""
    lines = wrap(d, text, fnt, max_w)
    if len(lines) > max_lines:
        PROBLEMS["trims"] += 1
        print("TRIM: %r -> %d lines, max %d" % (text, len(lines), max_lines),
              file=sys.stderr)
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "\u2026", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "\u2026"
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=fnt, fill=color)
    return len(lines)


def one_line(d, text, fnt, x, y, max_w, color=INK):
    """Draw a single line; count an overflow if it does not fit."""
    if d.textlength(text, font=fnt) > max_w:
        PROBLEMS["overflows"] += 1
        print("OVERFLOW: %r width %.0f > %.0f" % (text, d.textlength(text, font=fnt), max_w),
              file=sys.stderr)
        while text and d.textlength(text + "\u2026", font=fnt) > max_w:
            text = text[:-1]
        text = text + "\u2026"
    d.text((x, y), text, font=fnt, fill=color)
    return text


def badge(d, text, x, y, h=16):
    """Badge box, right-aligned at x. Returns its left edge."""
    colors = {"OFFICIAL": GREEN, "REPORTED": BLUE, "CLAIM": AMBER,
              "CONFIRMED": TEAL, "ONGOING": (107, 33, 168)}
    fill = colors.get(text, BLUE)
    fnt = f_sans_b(9)
    tw = d.textlength(text, font=fnt)
    w = int(tw + 10)
    d.rounded_rectangle([x - w, y, x, y + h], radius=3, fill=fill)
    d.text((x - w + 5, y + 3), text, font=fnt, fill=(255, 255, 255))
    return x - w


def num_disc(d, cx, cy, n, r=11):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
              outline=(255, 255, 255), width=2)
    fnt = f_sans_b(12 if n < 10 else 10)
    t = str(n)
    tw = d.textlength(t, font=fnt)
    th = fnt.size
    d.text((cx - tw / 2, cy - th / 2 - 1), t, font=fnt, fill=(255, 255, 255))


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- map mask
# 64 cols x 32 rows, '#' = land. Col = lon -180..180, row = lat 90..-60.
MAP = [
    "................##....######....................................",
    "..............####....##########..#..............###############",
    "..........###########...########..#.....########################",
    "..#####################.....###.......##########################",
    "...######################....#......###.########################",
    "....." + "#" * 20 + "......" + "#" + ".." + "#" * 5 + "#" * 24 + ".",
    "." * 11 + "#" * 16 + "." * 5 + "#" + "." + "#" * 7 + "#" * 23,
    ".............###############.....##########################.##..",
    "..............##############.....########################..##...",
    "..............###############....#########.###########..#.###...",
    "...............###############...########.######..##########....",
    "................##############...########.#######.########......",
    "................#######....##....#########.#####..####.###......",
    ".................######...###....##########.###....###.####.....",
    "..................####...###.....###########........#..#####....",
    "...................###....#####...###########..........######...",
    ".........................#######...##########...........######..",
    ".........................#######....#########...........#######.",
    ".........................#######.....#######.............######.",
    ".........................######.......#####...............######",
    ".........................######.......####...............#####..",
    ".........................#####........####..............#######.",
    ".........................#####........###.#.............#######.",
    ".........................####.........###...............######..",
    ".........................####.........##.................####.#.",
    ".........................###..............................##..#.",
    ".........................##.....................................",
    ".........................#......................................",
    "................................................................",
    "................................................................",
    "................................................................",
    "................................................................",
]
assert len(MAP) == 32 and all(len(r) == 64 for r in MAP)

# story number -> (lon, lat, dx, dy) nudge for the pin
PINS = {
    1: (127.0, 37.5, -5, -3), 2: (-74.0, 40.7, -3, 0), 3: (4.4, 50.8, -7, 5),
    4: (72.8, 19.0, -4, 2), 5: (30.5, 50.4, 4, -6), 6: (139.7, 35.7, 5, 2),
    7: (90.4, 23.8, 2, -4), 8: (160.0, -9.4, 0, 0), 9: (48.0, 29.4, 5, 2),
    10: (8.7, 50.1, 7, -5), 11: (34.5, 31.5, -2, 7), 12: (15.3, -4.3, 0, 0),
    13: (100.5, 13.75, 4, 3),
}


# ---------------------------------------------------------------- art
def art_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 48, 84))
    # bank building, left
    bx, by, bw = x + 18, y + 58, 130
    d.polygon([(bx, by), (bx + bw, by), (bx + bw / 2, by - 26)], fill=(232, 226, 214))
    d.rectangle([bx, by, bx + bw, by + 8], fill=(232, 226, 214))
    for i in range(4):
        cx = bx + 12 + i * 32
        d.rectangle([cx, by + 8, cx + 14, by + 62], fill=(232, 226, 214))
    d.rectangle([bx - 6, by + 62, bx + bw + 6, by + 70], fill=(200, 192, 176))
    # rate bars, right
    base = y + h - 22
    bars = [("JUL", 34, (200, 192, 176)), ("AUG", 58, (212, 175, 55)),
            ("NOV", 84, (220, 60, 60))]
    bx0 = x + 178
    for i, (lab, bh, col) in enumerate(bars):
        bx = bx0 + i * 48
        d.rectangle([bx, base - bh, bx + 34, base], fill=col)
        d.text((bx + 2, base + 4), lab, font=f_sans_b(10), fill=(255, 255, 255))
    d.text((x + w - 118, y + 8), "3.25%", font=f_sans_b(30), fill=(255, 255, 255))
    d.text((x + w - 118, y + 42), "THIRD HIKE", font=f_sans_b(11), fill=(212, 175, 55))


def art_macys(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(44, 62, 85))
    # skyline
    import random
    rnd = random.Random(26)
    bx = x
    while bx < x + w - 20:
        bw = rnd.randint(18, 34)
        bh = rnd.randint(28, 66)
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(16, 22, 34))
        for wy in range(y + h - bh + 6, y + h - 4, 10):
            for wx in range(bx + 4, bx + bw - 3, 9):
                if rnd.random() < 0.55:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 205, 90))
        bx += bw + 3
    # rain
    for i in range(26):
        rx = x + rnd.randint(0, w)
        ry = y + rnd.randint(0, h - 40)
        d.line([rx, ry, rx - 6, ry + 12], fill=(150, 170, 195), width=1)
    # balloon
    d.ellipse([x + 96, y + 8, x + 234, y + 86], fill=(200, 40, 40))
    d.ellipse([x + 116, y + 18, x + 150, y + 44], fill=(235, 110, 110))
    d.line([x + 150, y + 86, x + 138, y + 108], fill=(255, 255, 255), width=2)
    d.line([x + 180, y + 86, x + 192, y + 108], fill=(255, 255, 255), width=2)
    # banner
    d.rectangle([x, y + h - 24, x + w, y + h], fill=RED)
    d.text((x + 10, y + h - 20), "POSTPONED TO SATURDAY",
           font=f_sans_b(13), fill=(255, 255, 255))


def art_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 58, 110))
    cx, cy = x + w // 2, y + 58
    import math
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        star(d, cx + 74 * math.cos(ang), cy + 40 * math.sin(ang), 7, GOLD)
    d.text((cx - 34, cy - 16), "EU 27", font=f_sans_b(26), fill=(255, 255, 255))
    # split bar: two halves pulling apart
    d.polygon([(x + 20, y + h - 26), (x + w // 2 - 8, y + h - 26),
               (x + w // 2 - 20, y + h - 8), (x + 20, y + h - 8)], fill=GOLD)
    d.polygon([(x + w // 2 + 8, y + h - 26), (x + w - 20, y + h - 26),
               (x + w - 20, y + h - 8), (x + w // 2 + 20, y + h - 8)],
              fill=(120, 160, 210))


def art_card(d, key, x, y, w, h):
    if key == "mumbai":
        d.rectangle([x, y, x + w, y + h], fill=(232, 150, 60))
        d.rectangle([x + 78, y + 14, x + 118, y + h], fill=(120, 60, 20))
        d.pieslice([x + 82, y + 2, x + 114, y + 30], 180, 360, fill=(120, 60, 20))
        for cx in (x + 30, x + 52, x + 148, x + 170):
            d.rectangle([cx, y + 34, cx + 5, y + h - 6], fill=(255, 240, 210))
            d.ellipse([cx - 2, y + 24, cx + 7, y + 34], fill=(255, 200, 60))
    elif key == "kyiv":
        d.rectangle([x, y, x + w, y + h], fill=(70, 90, 120))
        for i, bw in enumerate((34, 44, 30)):
            bx = x + 12 + i * 46
            d.rectangle([bx, y + 22, bx + bw, y + h], fill=(30, 40, 55))
        star(d, x + 150, y + 20, 12, (255, 150, 40))
        d.line([x + 150, y + 20, x + 176, y + 8], fill=(255, 200, 90), width=2)
    elif key == "stocks":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        pts = [(x + 8, y + 44), (x + 50, y + 38), (x + 90, y + 40),
               (x + 130, y + 22), (x + 170, y + 14), (x + 190, y + 8)]
        d.line(pts, fill=(27, 140, 60), width=3)
        d.polygon([(x + 182, y + 2), (x + 194, y + 4), (x + 186, y + 14)],
                  fill=(27, 140, 60))
        d.text((x + 8, y + 4), "+2%", font=f_sans_b(13), fill=(27, 140, 60))
    elif key == "dhaka":
        d.rectangle([x, y, x + w, y + h], fill=(15, 118, 110))
        d.rectangle([x + 12, y + 20, x + 70, y + h - 6], fill=(240, 240, 240))
        d.rectangle([x + 76, y + 30, x + 110, y + h - 6], fill=(200, 200, 200))
        d.text((x + 122, y + 8), "+36%", font=f_sans_b(20), fill=(255, 255, 255))
        d.line([x + 122, y + 34, x + 188, y + 12], fill=(255, 220, 90), width=3)
    elif key == "solomons":
        d.rectangle([x, y, x + w, y + h], fill=(40, 110, 170))
        d.rectangle([x, y + 34, x + w, y + h], fill=(20, 80, 140))
        d.polygon([(x + 60, y + 34), (x + 110, y + 12), (x + 160, y + 34)],
                  fill=(46, 125, 50))
        d.rectangle([x + 150, y + 8, x + 152, y + 30], fill=(255, 255, 255))
        d.rectangle([x + 152, y + 8, x + 176, y + 18], fill=(255, 215, 0))
        d.rectangle([x + 20, y + 8, x + 22, y + 30], fill=(255, 255, 255))
        d.rectangle([x + 22, y + 8, x + 46, y + 18], fill=(0, 40, 120))
    elif key == "kuwait":
        d.rectangle([x, y, x + w, y + h], fill=(214, 186, 140))
        d.ellipse([x + 140, y + 8, x + 172, y + 40], fill=(255, 150, 40))
        star(d, x + 156, y + 24, 10, (255, 220, 90))
        d.line([x + 40, y + 18, x + 70, y + 18], fill=(60, 60, 60), width=2)
        d.ellipse([x + 52, y + 12, x + 58, y + 18], fill=(60, 60, 60))
        d.ellipse([x + 30, y + 14, x + 36, y + 20], fill=(60, 60, 60))
        d.ellipse([x + 64, y + 14, x + 70, y + 20], fill=(60, 60, 60))
    elif key == "ecb":
        d.rectangle([x, y, x + w, y + h], fill=(22, 48, 84))
        d.text((x + 12, y + 6), "\u20ac", font=f_sans_b(30), fill=GOLD)
        for i in range(3):
            cx = x + 120 + i * 24
            d.rectangle([cx, y + 18, cx + 10, y + 44], fill=(232, 226, 214))
        d.rectangle([x + 112, y + 44, x + 188, y + 48], fill=(232, 226, 214))
    elif key == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(20, 20, 30))
        for i, bw in enumerate((30, 40, 26)):
            bx = x + 14 + i * 44
            d.rectangle([bx, y + 26, bx + bw, y + h], fill=(50, 50, 65))
        star(d, x + 150, y + 22, 13, (255, 140, 30))
        d.ellipse([x + 138, y + 10, x + 162, y + 34], fill=(255, 190, 80))
    elif key == "ebola":
        d.rectangle([x, y, x + w, y + h], fill=(240, 235, 225))
        for cx, cy, r in ((x + 40, y + 26, 7), (x + 70, y + 16, 5),
                          (x + 100, y + 30, 8), (x + 130, y + 18, 5),
                          (x + 160, y + 30, 6)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        d.text((x + 10, y + 34), "+", font=f_sans_b(16), fill=RED)
    elif key == "bangkok":
        d.rectangle([x, y, x + w, y + h], fill=(40, 40, 50))
        for i, bh in enumerate((26, 36, 22)):
            bx = x + 16 + i * 30
            d.rectangle([bx, y + h - bh, bx + 16, y + h], fill=(110, 110, 125))
        d.polygon([(x + 140, y + 8), (x + 152, y + 26), (x + 164, y + 8)],
                  fill=(255, 150, 40))
        d.ellipse([x + 138, y + 20, x + 166, y + 40], fill=(255, 190, 80))
    else:
        d.rectangle([x, y, x + w, y + h], fill=(200, 200, 200))


LEAD_ART = {"seoul": art_seoul, "macys": art_macys, "eu": art_eu}


# ---------------------------------------------------------------- render
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # top rule + masthead
    d.rectangle([0, 0, W, 3], fill=INK)
    mast = DATA["masthead"]
    mf = f_serif_b(40)
    d.text(((W - d.textlength(mast, font=mf)) / 2, 8), mast, font=mf, fill=INK)
    df = f_sans_b(15)
    dt = DATA["date"]
    d.text(((W - d.textlength(dt, font=df)) / 2, 52), dt, font=df, fill=INK)
    sf = f_serif(13)
    st = DATA["standfirst"]
    d.text(((W - d.textlength(st, font=sf)) / 2, 70), st, font=sf, fill=(60, 60, 60))

    # stat boxes
    stt = DATA["stats"]
    boxes = [("45", "STORIES"), (str(stt["regions"]), "REGIONS"),
             (str(stt["sources"]), "SOURCES \u00b7 " + str(stt["fields"]) + " FIELDS")]
    bx = [8, 348, 688]
    bw = [328, 328, 328]
    for (num, lab), x0, w0 in zip(boxes, bx, bw):
        d.rectangle([x0, 88, x0 + w0, 116], outline=INK, width=1)
        f1, f2 = f_sans_b(19), f_sans_b(12)
        tw = d.textlength(num, font=f1) + 6 + d.textlength(lab, font=f2)
        cx = x0 + (w0 - tw) / 2
        d.text((cx, 94), num, font=f1, fill=RED)
        d.text((cx + d.textlength(num, font=f1) + 6, 98), lab, font=f2, fill=INK)

    # region bar + labels
    regs = DATA["regions"]
    total = sum(r["count"] for r in regs)
    x = 8
    for r in regs:
        seg = int(round(1008 * r["count"] / total))
        d.rectangle([x, 122, x + seg, 132], fill=r["color"])
        x += seg
    rl = " \u00b7 ".join("%s %d" % (r["name"], r["count"]) for r in regs)
    rf = f_sans(10)
    d.text(((W - d.textlength(rl, font=rf)) / 2, 136), rl, font=rf, fill=INK)

    # leads
    leads = DATA["leads"]
    for i, lead in enumerate(leads):
        lx = 8 + i * 338
        lw = 330
        LEAD_ART[lead["art"]](d, lx, 152, lw, 138)
        num_disc(d, lx + 14, 152 + 14, lead["n"], r=11)
        block(d, lead["headline"], f_serif_b(16), lx, 294, lw, 3, 19)
        block(d, lead["deck"], f_sans(12), lx, 340, lw, 3, 15)
        sf2 = f_sans(9)
        d.text((lx, 382), "SOURCE: " + lead["source"], font=sf2, fill=GREY)
        badge(d, lead["badge"], lx + lw, 380)

    # cards, two rows of five
    cards = DATA["cards"]
    for i, card in enumerate(cards):
        row, col = divmod(i, 5)
        cx = 8 + col * 204
        cy = 404 + row * 128
        cw = 196
        art_card(d, card["art"], cx, cy, cw, 54)
        num_disc(d, cx + 12, cy + 12, card["n"], r=10)
        rf2 = f_sans_b(9)
        d.text((cx, cy + 58), card["city"] + " \u00b7 " + card["region"].upper(),
               font=rf2, fill=BLUE)
        block(d, card["headline"], f_sans_b(12), cx, cy + 72, cw, 2, 14)
        sf3 = f_sans(9)
        d.text((cx, cy + 102), card["source"], font=sf3, fill=GREY)
        badge(d, card["badge"], cx + cw, cy + 100)

    # UTC timeline
    d.text((8, 658), "THE DAY IN UTC", font=f_sans_b(11), fill=INK)
    d.line([8, 674, 1016, 674], fill=INK, width=1)
    tl = DATA["timeline"]
    for i, item in enumerate(tl):
        row, col = divmod(i, 4)
        tx = 8 + col * 254
        ty = 678 + row * 20
        tf = f_sans_b(10)
        d.text((tx, ty), item["time"] + " UTC", font=tf, fill=RED)
        tw = d.textlength(item["time"] + " UTC  ", font=tf)
        one_line(d, item["text"], f_sans(10), tx + tw, ty, 250 - tw)

    # map + briefs header
    d.text((8, 718), "WHERE IT HAPPENED \u2014 PINS 1\u201313",
           font=f_sans_b(11), fill=INK)
    rh = "ALSO ON THURSDAY 26 NOVEMBER 2026 \u2014 STORIES 14\u201345"
    rf3 = f_sans_b(11)
    d.text((1016 - d.textlength(rh, font=rf3), 718), rh, font=rf3, fill=INK)

    # map
    mx, my, mw, mh = 8, 736, 340, 170
    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA, outline=INK, width=1)
    cw, ch = mw / 64.0, mh / 32.0
    for ri, row in enumerate(MAP):
        for ci, ch_ in enumerate(row):
            if ch_ == "#":
                d.rectangle([mx + ci * cw, my + ri * ch,
                             mx + (ci + 1) * cw - 0.5, my + (ri + 1) * ch - 0.5],
                            fill=LAND)
    for n, (lon, lat, dx, dy) in PINS.items():
        px = mx + (lon + 180.0) / 360.0 * mw + dx
        py = my + (90.0 - lat) / 150.0 * mh + dy
        num_disc(d, px, py, n, r=7)
    d.text((mx, 912), "Pins mark leads and cards 1\u201313.",
           font=f_sans(9), fill=GREY)

    # briefs, two columns of sixteen
    briefs = DATA["briefs"]
    bf = f_sans(10)
    bfb = f_sans_b(10)
    for i, b in enumerate(briefs):
        col, row = divmod(i, 16)
        bx = 356 + col * 330
        by = 736 + row * 13
        num = "%d." % b["n"]
        d.text((bx, by), num, font=bfb, fill=RED)
        nw = d.textlength(num + " ", font=bfb)
        one_line(d, "%s \u2014 %s" % (b["city"], b["text"]), bf,
                 bx + nw, by, 322 - nw)

    # date check
    d.rectangle([8, 948, 1016, 990], outline=RED, width=1)
    d.text((20, 951), "DATE CHECK \u2014 THESE ARE NOT 26 NOVEMBER",
           font=f_sans_b(10), fill=RED)
    dc = DATA["datecheck"]
    for i, item in enumerate(dc):
        row, col = divmod(i, 3)
        ix = 20 + col * 336
        iy = 967 + row * 11
        one_line(d, "\u00d7 " + item, f_sans(10), ix, iy, 320)

    # footer
    ff = f_sans(9)
    fn = DATA["footer_note"]
    d.text(((W - d.textlength(fn, font=ff)) / 2, 994), fn, font=ff, fill=INK)
    fs = DATA["footer_sources"]
    d.text(((W - d.textlength(fs, font=ff)) / 2, 1004), fs, font=ff, fill=GREY)
    fl = DATA["footer_legend"]
    d.text(((W - d.textlength(fl, font=ff)) / 2, 1014), fl, font=ff, fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    raw = open(out, "rb").read()
    print(json.dumps({
        "file": "entry.png",
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "stories": len(DATA["leads"]) + len(DATA["cards"]) + len(DATA["briefs"]),
        "trims": PROBLEMS["trims"],
        "overflows": PROBLEMS["overflows"],
    }, indent=1))
    return 0 if (PROBLEMS["trims"] == 0 and PROBLEMS["overflows"] == 0) else 2


if __name__ == "__main__":
    sys.exit(main())
