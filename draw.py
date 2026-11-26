#!/usr/bin/env python3
"""Paint the 26 November 2026 one-page newspaper into entry.png.

Every mark is drawn with PIL from the story data in stories.json, so the
page comes out byte-identical on each run. No network, no clock, no
randomness: this file and stories.json are the only inputs.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "stories.json")
OUT_PATH = os.path.join(BASE_DIR, "entry.png")

PAGE_WIDTH = 1024
PAGE_HEIGHT = 1024
EDGE = 26

PAPER_COL = (246, 241, 227)
INK_COL = (24, 24, 20)
SOFT_COL = (90, 86, 74)
RULE_COL = (24, 24, 20)
FAINT_COL = (205, 198, 178)
PANEL_COL = (255, 252, 240)
SEA_COL = (214, 226, 232)
LAND_COL = (232, 222, 196)
LAND_EDGE_COL = (168, 156, 128)
RED_COL = (163, 31, 31)
BLUE_COL = (29, 78, 137)
GOLD_COL = (176, 124, 12)
GREEN_COL = (30, 107, 52)
AMBER_COL = (176, 124, 12)

SERIF_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Split text into lines that fit max_w pixels, word by word."""
    parts = text.split()
    out = []
    line = ""
    for w in parts:
        cand = w if not line else line + " " + w
        if fnt.getlength(cand) <= max_w:
            line = cand
        else:
            if line:
                out.append(line)
            line = w
    if line:
        out.append(line)
    return out


def center(drw, cx, y, text, fnt, fill=INK_COL):
    w = fnt.getlength(text)
    drw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def tag(drw, x, y, label, h=13):
    """Small filled tag; returns its width. Colour follows the label."""
    fnt = load_font(SANS_BOLD_PATH, 8)
    pad = 5
    w = int(fnt.getlength(label)) + pad * 2
    if label == "OFFICIAL":
        fill, fg = BLUE_COL, (255, 255, 255)
    elif label == "CLAIM":
        fill, fg = (232, 196, 80), INK_COL
    else:
        fill, fg = GREEN_COL, (255, 255, 255)
    drw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    drw.text((x + pad, y + 2), label, font=fnt, fill=fg)
    return w


def rule(drw, y, x0, x1, width=1, fill=RULE_COL):
    drw.line([(x0, y), (x1, y)], fill=fill, width=width)


class TrimCounter:
    """Counts lines that had to be cut to fit their box."""

    def __init__(self):
        self.trims = 0
        self.overs = 0

    def check(self, text, fnt, max_w):
        if fnt.getlength(text) > max_w:
            self.overs += 1
        return text


def bank_art(drw, x, y, w, h):
    """Bank building with a rising rate arrow for the Seoul lead."""
    drw.rectangle([x, y, x + w, y + h], fill=(219, 232, 240), outline=RULE_COL)
    px, py = x + 18, y + 34
    pw, ph = w - 36, h - 52
    drw.polygon([(px, py), (px + pw, py), (px + pw / 2, py - 16)], fill=(70, 90, 110))
    drw.rectangle([px, py, px + pw, py + 8], fill=(70, 90, 110))
    for k in range(5):
        cx = px + 8 + k * ((pw - 16) / 4)
        drw.rectangle([cx, py + 8, cx + 7, py + ph - 14], fill=(240, 244, 248), outline=(70, 90, 110))
    drw.rectangle([px - 4, py + ph - 14, px + pw + 4, py + ph - 8], fill=(70, 90, 110))
    drw.rectangle([px - 8, py + ph - 8, px + pw + 8, py + ph - 4], fill=(70, 90, 110))
    drw.line([(x + w - 78, y + h - 22), (x + w - 52, y + 26), (x + w - 30, y + 44), (x + w - 12, y + 16)],
             fill=GREEN_COL, width=4)
    drw.polygon([(x + w - 12, y + 16), (x + w - 12, y + 30), (x + w + 2, y + 16)], fill=GREEN_COL)
    big = load_font(SANS_BOLD_PATH, 26)
    drw.text((x + 12, y + 6), "3.25%", font=big, fill=INK_COL)


def summit_art(drw, x, y, w, h):
    """Ring of gold stars on EU blue, with the loan figure (Brussels)."""
    drw.rectangle([x, y, x + w, y + h], fill=(18, 52, 110), outline=RULE_COL)
    import math
    cx, cy, r = x + w / 2 - 52, y + h / 2, 44
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        drw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 204, 0))
    drw.text((cx - 34, cy - 9), "€45bn", font=load_font(SANS_BOLD_PATH, 17), fill=(255, 255, 255))
    drw.text((x + w - 108, y + 12), "27 FLAGS", font=load_font(SANS_BOLD_PATH, 10), fill=(255, 204, 0))
    drw.text((x + w - 108, y + 28), "1 TABLE", font=load_font(SANS_BOLD_PATH, 10), fill=(255, 255, 255))
    drw.text((x + w - 108, y + 44), "2 DAYS", font=load_font(SANS_BOLD_PATH, 10), fill=(255, 255, 255))
    drw.line([(x + 12, y + h - 14), (x + w - 12, y + h - 14)], fill=(255, 204, 0), width=2)


def chart_art(drw, x, y, w, h):
    """Rising green candlesticks with a climbing trend line (oil lead)."""
    drw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=RULE_COL)
    gx, gy, gw, gh = x + 10, y + 34, w - 20, h - 48
    for i in range(1, 5):
        gy_line = gy + gh * i / 5
        drw.line([(gx, gy_line), (gx + gw, gy_line)], fill=(228, 228, 228), width=1)
    closes = [0.88, 0.74, 0.58, 0.48, 0.30, 0.22, 0.10]
    opens = [0.80, 0.64, 0.50, 0.38, 0.24, 0.14, 0.04]
    n = len(closes)
    step = gw / n
    for i in range(n):
        cx = gx + step * i + step / 2
        top = gy + gh * opens[i]
        bot = gy + gh * closes[i]
        drw.line([(cx, gy + gh * opens[i] - 6), (cx, gy + gh * closes[i] + 6)], fill=GREEN_COL, width=2)
        drw.rectangle([cx - 9, top, cx + 9, bot], fill=GREEN_COL)
    for i in range(n - 1):
        x0 = gx + step * i + step / 2
        x1 = gx + step * (i + 1) + step / 2
        y0 = gy + gh * closes[i]
        y1 = gy + gh * closes[i + 1]
        drw.line([(x0, y0), (x1, y1)], fill=INK_COL, width=2)
    drw.text((x + 12, y + 6), "Brent $91", font=load_font(SANS_BOLD_PATH, 24), fill=GREEN_COL)


def masthead(drw, data, ov):
    cx = PAGE_WIDTH / 2
    f_title = load_font(SERIF_BOLD_PATH, 44)
    center(drw, cx, 8, data["masthead"], f_title)
    rule(drw, 58, EDGE, PAGE_WIDTH - EDGE, width=2)
    f_date = load_font(SANS_BOLD_PATH, 13)
    center(drw, cx, 63, data["dateline"], f_date)
    f_note = load_font(SANS_PATH, 11)
    center(drw, cx, 80, data["edition_note"], f_note, fill=SOFT_COL)
    return 96


def chips(drw, data, y):
    regions = ["ASIA-PACIFIC", "SOUTH ASIA", "MIDDLE EAST", "EUROPE",
               "AFRICA", "NORTH AMERICA", "LATIN AMERICA", "GLOBAL"]
    fields = ["Politics", "Markets", "Economy", "War", "Diplomacy",
              "Tech", "Science", "Sports", "Culture"]
    counts_r = {}
    counts_f = {}
    for b in data["briefs"]:
        counts_r[b["region"]] = counts_r.get(b["region"], 0) + 1
        counts_f[b["field"]] = counts_f.get(b["field"], 0) + 1
    lead_region = {"SEOUL": "ASIA-PACIFIC", "BRUSSELS": "EUROPE", "NEW YORK": "NORTH AMERICA"}
    lead_field = {"bank": "Economy", "summit": "Diplomacy", "chart": "Markets"}
    for lead in data["leads"]:
        counts_r[lead_region[lead["city"]]] = counts_r.get(lead_region[lead["city"]], 0) + 1
        counts_f[lead_field[lead["art"]]] = counts_f.get(lead_field[lead["art"]], 0) + 1
    f_chip = load_font(SANS_BOLD_PATH, 10)
    line_r = "   ".join("%s %d" % (r, counts_r.get(r, 0)) for r in regions)
    line_f = "   ".join("%s %d" % (f, counts_f.get(f, 0)) for f in fields)
    center(drw, PAGE_WIDTH / 2, y, line_r, f_chip)
    center(drw, PAGE_WIDTH / 2, y + 15, line_f, load_font(SANS_PATH, 10), fill=SOFT_COL)
    rule(drw, y + 30, EDGE, PAGE_WIDTH - EDGE, width=1, fill=FAINT_COL)
    return y + 34


def stats(drw, data, y):
    col_w = (PAGE_WIDTH - 2 * EDGE) / 6
    f_val = load_font(SANS_BOLD_PATH, 25)
    f_cap = load_font(SANS_PATH, 10)
    for i, st in enumerate(data["stats"]):
        cx = EDGE + col_w * i + col_w / 2
        center(drw, cx, y, st["value"], f_val)
        center(drw, cx, y + 30, st["caption"], f_cap, fill=SOFT_COL)
        if i:
            drw.line([(EDGE + col_w * i, y + 2), (EDGE + col_w * i, y + 42)], fill=FAINT_COL, width=1)
    rule(drw, y + 46, EDGE, PAGE_WIDTH - EDGE, width=1, fill=FAINT_COL)
    return y + 50


def leads(drw, data, y, ov):
    col_w = (PAGE_WIDTH - 2 * EDGE - 2 * 14) / 3
    art_h = 104
    f_kick = load_font(SANS_BOLD_PATH, 11)
    f_head = load_font(SERIF_BOLD_PATH, 19)
    f_deck = load_font(SERIF_PATH, 12)
    painters = {"bank": bank_art, "summit": summit_art, "chart": chart_art}
    for i, lead in enumerate(data["leads"]):
        x = EDGE + i * (col_w + 14)
        drw.text((x, y), lead["city"], font=f_kick, fill=RED_COL)
        tag(drw, x + f_kick.getlength(lead["city"]) + 8, y - 1, lead["badge"])
        ay = y + 16
        painters[lead["art"]](drw, x, ay, col_w, art_h)
        hy = ay + art_h + 8
        head_lines = wrap(lead["headline"], f_head, col_w)
        for ln in head_lines[:2]:
            ov.check(ln, f_head, col_w)
            drw.text((x, hy), ln, font=f_head, fill=INK_COL)
            hy += 21
        if len(head_lines) > 2:
            ov.trims += 1
        dy = hy + 2
        deck_lines = wrap(lead["deck"], f_deck, col_w)
        for ln in deck_lines[:3]:
            ov.check(ln, f_deck, col_w)
            drw.text((x, dy), ln, font=f_deck, fill=SOFT_COL)
            dy += 15
        if len(deck_lines) > 3:
            ov.trims += 1
    return y + 16 + art_h + 8 + 42 + 2 + 45


LAND_POLYS = [
    [(7, 21), (42, 7), (105, 4), (154, 21), (161, 39), (133, 56),
     (126, 70), (105, 80), (91, 77), (63, 60), (63, 38), (3, 84)],
    [(150, 6), (162, 4), (166, 12), (154, 16)],
    [(120, 82), (145, 76), (172, 95), (162, 128), (140, 148),
     (122, 122), (112, 96)],
    [(215, 35), (245, 15), (275, 25), (270, 50), (240, 55), (220, 48)],
    [(205, 55), (245, 45), (275, 60), (270, 100), (245, 140),
     (225, 120), (210, 85)],
    [(275, 15), (330, 5), (420, 10), (455, 30), (430, 60), (390, 75),
     (350, 60), (310, 50), (280, 35)],
    [(385, 112), (430, 108), (445, 128), (400, 134)],
]

PIN_POS = {
    "SEOUL": (380, 60),
    "BRUSSELS": (227, 34),
    "NEW YORK": (125, 48),
    "GAZA": (266, 62),
    "HORMUZ": (295, 67),
    "ADDIS ABABA": (273, 92),
    "QUITO": (120, 105),
    "TOKYO": (410, 48),
}

PIN_OFF = {
    "SEOUL": (-52, 8),
    "BRUSSELS": (-58, -6),
    "NEW YORK": (-62, -6),
    "GAZA": (10, -14),
    "HORMUZ": (10, -14),
    "ADDIS ABABA": (10, -6),
    "QUITO": (-52, 8),
    "TOKYO": (10, -6),
}


def map_band(drw, data, y, ov):
    map_x, map_y = EDGE, y
    map_w, map_h = 470, 174
    f_title = load_font(SANS_BOLD_PATH, 11)
    drw.text((map_x, map_y), "THE WORLD — 8 PLACES THAT MATTER TODAY", font=f_title, fill=INK_COL)
    my = map_y + 18
    drw.rectangle([map_x, my, map_x + map_w, my + map_h - 18], fill=SEA_COL, outline=RULE_COL)
    ox, oy = map_x, my
    for poly in LAND_POLYS:
        pts = [(ox + px, oy + py) for px, py in poly]
        drw.polygon(pts, fill=LAND_COL, outline=LAND_EDGE_COL)
    f_pin = load_font(SANS_BOLD_PATH, 9)
    f_lab = load_font(SANS_BOLD_PATH, 8)
    for pin in data["map_pins"]:
        px, py = PIN_POS[pin["city"]]
        cx, cy = ox + px, oy + py
        drw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED_COL, outline=(255, 255, 255), width=1)
        num = str(pin["n"])
        tw = f_pin.getlength(num)
        drw.text((cx - tw / 2, cy - 5), num, font=f_pin, fill=(255, 255, 255))
        dx, dy = PIN_OFF[pin["city"]]
        drw.text((cx + dx, cy + dy), pin["city"], font=f_lab, fill=INK_COL)
    rx = map_x + map_w + 18
    rw = PAGE_WIDTH - EDGE - rx
    drw.text((rx, map_y), "THE DAY IN UTC", font=f_title, fill=INK_COL)
    f_time = load_font(SANS_BOLD_PATH, 11)
    f_tl = load_font(SANS_PATH, 11)
    ty = map_y + 16
    for item in data["timeline"]:
        drw.text((rx, ty), item["utc"], font=f_time, fill=RED_COL)
        lines = wrap(item["text"], f_tl, rw - 52)
        ly = ty
        for ln in lines[:1]:
            ov.check(ln, f_tl, rw - 52)
            drw.text((rx + 50, ly), ln, font=f_tl, fill=INK_COL)
            ly += 13
        if len(lines) > 1:
            ov.trims += 1
        ty += 16
    return map_y + map_h + 8


def briefs(drw, data, y, ov):
    col_w = (PAGE_WIDTH - 2 * EDGE - 16) / 2
    f_num = load_font(SANS_BOLD_PATH, 11)
    f_city = load_font(SANS_BOLD_PATH, 10)
    f_head = load_font(SANS_PATH, 11)
    pitch = 16
    left = data["briefs"][:21]
    right = data["briefs"][21:]
    for col_i, group in enumerate((left, right)):
        x = EDGE + col_i * (col_w + 16)
        cy = y
        for b in group:
            num = str(b["n"])
            drw.text((x, cy), num, font=f_num, fill=RED_COL)
            nx = x + 22
            city = b["city"]
            drw.text((nx, cy + 1), city, font=f_city, fill=INK_COL)
            hx = nx + f_city.getlength(city) + 8
            head = b["headline"]
            avail = x + col_w - 62 - hx
            ov.check(head, f_head, avail)
            if f_head.getlength(head) > avail:
                ov.trims += 1
                while head and f_head.getlength(head + "…") > avail:
                    head = head[:-1]
                head += "…"
            drw.text((hx, cy + 1), head, font=f_head, fill=INK_COL)
            tag(drw, x + col_w - 58, cy, b["badge"])
            cy += pitch
    return y + 21 * pitch


def footer(drw, data, y, ov):
    rule(drw, y, EDGE, PAGE_WIDTH - EDGE, width=2)
    f_h = load_font(SANS_BOLD_PATH, 11)
    f_t = load_font(SANS_PATH, 10)
    drw.text((EDGE, y + 6), "DATE CHECK", font=f_h, fill=RED_COL)
    w = PAGE_WIDTH - 2 * EDGE
    lines = []
    for key in ("included", "excluded", "not_yet", "sources"):
        lines += wrap(data["date_check"][key], f_t, w)
    cy = y + 22
    for ln in lines:
        drw.text((EDGE, cy), ln, font=f_t, fill=SOFT_COL)
        cy += 13
    return cy


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    ov = TrimCounter()
    img = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), PAPER_COL)
    drw = ImageDraw.Draw(img)
    y = masthead(drw, data, ov)
    y = chips(drw, data, y)
    y = stats(drw, data, y)
    y = leads(drw, data, y, ov)
    y = map_band(drw, data, y, ov)
    y = briefs(drw, data, y, ov)
    y = footer(drw, data, y, ov)
    img.save(OUT_PATH, format="PNG")
    size = os.path.getsize(OUT_PATH)
    print("drew %s (%dx%d, %d bytes)" % (OUT_PATH, PAGE_WIDTH, PAGE_HEIGHT, size))
    print("layout: trims=%d overflows=%d bottom_y=%d" % (ov.trims, ov.overs, y))
    print("stories: %d briefs + %d leads = %d" % (
        len(data["briefs"]), len(data["leads"]),
        len(data["briefs"]) + len(data["leads"])))


if __name__ == "__main__":
    main()
