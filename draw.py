#!/usr/bin/env python3
"""Draw the 26 November 2026 one-page newspaper, entry.png.

Every glyph is rendered with PIL from the story data in stories.json, so
the page is byte-identical on every run. No network, no clock, no random
numbers: the only inputs are this file and stories.json.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "stories.json")
OUT = os.path.join(HERE, "entry.png")

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 26

PAPER = (246, 241, 227)
INK = (24, 24, 20)
SOFT = (90, 86, 74)
RULE = (24, 24, 20)
FAINT = (205, 198, 178)
PANEL = (255, 252, 240)
SEA = (214, 226, 232)
LAND = (232, 222, 196)
LAND_EDGE = (168, 156, 128)
RED = (163, 31, 31)
BLUE = (29, 78, 137)
GOLD = (176, 124, 12)
GREEN = (30, 107, 52)
AMBER = (176, 124, 12)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(text, fnt, max_w):
    """Split text into lines that fit max_w pixels, word by word."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_center(drw, cx, y, text, fnt, fill=INK):
    w = fnt.getlength(text)
    drw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def badge(drw, x, y, label, h=13):
    """Small filled tag; returns its width. Colours by label."""
    fnt = font(SANS_B, 8)
    pad = 5
    w = int(fnt.getlength(label)) + pad * 2
    if label == "OFFICIAL":
        fill, fg = BLUE, (255, 255, 255)
    elif label == "CLAIM":
        fill, fg = (232, 196, 80), INK
    else:
        fill, fg = GREEN, (255, 255, 255)
    drw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    drw.text((x + pad, y + 2), label, font=fnt, fill=fg)
    return w


def hline(drw, y, x0, x1, width=1, fill=RULE):
    drw.line([(x0, y), (x1, y)], fill=fill, width=width)


class Overflow:
    """Counts every line that had to be cut to fit its box."""

    def __init__(self):
        self.trims = 0
        self.overs = 0

    def check(self, text, fnt, max_w):
        if fnt.getlength(text) > max_w:
            self.overs += 1
        return text


def draw_bank_panel(drw, x, y, w, h):
    """Central-bank building with a rising rate arrow (Seoul lead)."""
    drw.rectangle([x, y, x + w, y + h], fill=(219, 232, 240), outline=RULE)
    bx, by = x + 18, y + 34
    bw, bh = w - 36, h - 52
    drw.polygon([(bx, by), (bx + bw, by), (bx + bw / 2, by - 16)], fill=(70, 90, 110))
    drw.rectangle([bx, by, bx + bw, by + 8], fill=(70, 90, 110))
    for i in range(5):
        cx = bx + 8 + i * ((bw - 16) / 4)
        drw.rectangle([cx, by + 8, cx + 7, by + bh - 14], fill=(240, 244, 248), outline=(70, 90, 110))
    drw.rectangle([bx - 4, by + bh - 14, bx + bw + 4, by + bh - 8], fill=(70, 90, 110))
    drw.rectangle([bx - 8, by + bh - 8, bx + bw + 8, by + bh - 4], fill=(70, 90, 110))
    drw.line([(x + w - 78, y + h - 22), (x + w - 52, y + 26), (x + w - 30, y + 44), (x + w - 12, y + 16)],
             fill=GREEN, width=4)
    drw.polygon([(x + w - 12, y + 16), (x + w - 12, y + 30), (x + w + 2, y + 16)], fill=GREEN)
    big = font(SANS_B, 26)
    drw.text((x + 12, y + 6), "3.25%", font=big, fill=INK)


def draw_summit_panel(drw, x, y, w, h):
    """Circle of gold stars on EU blue, with the loan figure (Brussels)."""
    drw.rectangle([x, y, x + w, y + h], fill=(18, 52, 110), outline=RULE)
    import math
    cx, cy, r = x + w / 2 - 52, y + h / 2, 44
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        drw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 204, 0))
    drw.text((cx - 34, cy - 9), "€45bn", font=font(SANS_B, 17), fill=(255, 255, 255))
    drw.text((x + w - 108, y + 12), "27 FLAGS", font=font(SANS_B, 10), fill=(255, 204, 0))
    drw.text((x + w - 108, y + 28), "1 TABLE", font=font(SANS_B, 10), fill=(255, 255, 255))
    drw.text((x + w - 108, y + 44), "2 DAYS", font=font(SANS_B, 10), fill=(255, 255, 255))
    drw.line([(x + 12, y + h - 14), (x + w - 12, y + h - 14)], fill=(255, 204, 0), width=2)


def draw_chart_panel(drw, x, y, w, h):
    """Falling candlesticks with a dashed downtrend (New York lead)."""
    drw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=RULE)
    gx, gy, gw, gh = x + 10, y + 34, w - 20, h - 48
    for i in range(1, 5):
        gy_line = gy + gh * i / 5
        drw.line([(gx, gy_line), (gx + gw, gy_line)], fill=(228, 228, 228), width=1)
    closes = [0.10, 0.22, 0.30, 0.48, 0.58, 0.74, 0.88]
    opens = [0.04, 0.14, 0.24, 0.38, 0.50, 0.64, 0.80]
    n = len(closes)
    step = gw / n
    for i in range(n):
        cx = gx + step * i + step / 2
        top = gy + gh * opens[i]
        bot = gy + gh * closes[i]
        drw.line([(cx, gy + gh * opens[i] - 6), (cx, gy + gh * closes[i] + 6)], fill=RED, width=2)
        drw.rectangle([cx - 9, top, cx + 9, bot], fill=RED)
    for i in range(n - 1):
        x0 = gx + step * i + step / 2
        x1 = gx + step * (i + 1) + step / 2
        y0 = gy + gh * closes[i]
        y1 = gy + gh * closes[i + 1]
        drw.line([(x0, y0), (x1, y1)], fill=INK, width=2)
    drw.text((x + 12, y + 6), "-4.6%", font=font(SANS_B, 24), fill=RED)


def draw_masthead(drw, data, ov):
    cx = PAGE_W / 2
    f_title = font(SERIF_B, 44)
    draw_center(drw, cx, 8, data["masthead"], f_title)
    hline(drw, 58, MARGIN, PAGE_W - MARGIN, width=2)
    f_date = font(SANS_B, 13)
    draw_center(drw, cx, 63, data["dateline"], f_date)
    f_note = font(SANS, 11)
    draw_center(drw, cx, 80, data["edition_note"], f_note, fill=SOFT)
    return 96


def draw_chips(drw, data, y):
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
    f_chip = font(SANS_B, 10)
    line_r = "   ".join("%s %d" % (r, counts_r.get(r, 0)) for r in regions)
    line_f = "   ".join("%s %d" % (f, counts_f.get(f, 0)) for f in fields)
    draw_center(drw, PAGE_W / 2, y, line_r, f_chip)
    draw_center(drw, PAGE_W / 2, y + 15, line_f, font(SANS, 10), fill=SOFT)
    hline(drw, y + 30, MARGIN, PAGE_W - MARGIN, width=1, fill=FAINT)
    return y + 34


def draw_stats(drw, data, y):
    col_w = (PAGE_W - 2 * MARGIN) / 6
    f_val = font(SANS_B, 25)
    f_cap = font(SANS, 10)
    for i, st in enumerate(data["stats"]):
        cx = MARGIN + col_w * i + col_w / 2
        draw_center(drw, cx, y, st["value"], f_val)
        draw_center(drw, cx, y + 30, st["caption"], f_cap, fill=SOFT)
        if i:
            drw.line([(MARGIN + col_w * i, y + 2), (MARGIN + col_w * i, y + 42)], fill=FAINT, width=1)
    hline(drw, y + 46, MARGIN, PAGE_W - MARGIN, width=1, fill=FAINT)
    return y + 50


def draw_leads(drw, data, y, ov):
    col_w = (PAGE_W - 2 * MARGIN - 2 * 14) / 3
    art_h = 104
    f_kick = font(SANS_B, 11)
    f_head = font(SERIF_B, 19)
    f_deck = font(SERIF, 12)
    painters = {"bank": draw_bank_panel, "summit": draw_summit_panel, "chart": draw_chart_panel}
    for i, lead in enumerate(data["leads"]):
        x = MARGIN + i * (col_w + 14)
        drw.text((x, y), lead["city"], font=f_kick, fill=RED)
        badge(drw, x + f_kick.getlength(lead["city"]) + 8, y - 1, lead["badge"])
        ay = y + 16
        painters[lead["art"]](drw, x, ay, col_w, art_h)
        hy = ay + art_h + 8
        head_lines = wrap_text(lead["headline"], f_head, col_w)
        for ln in head_lines[:2]:
            ov.check(ln, f_head, col_w)
            drw.text((x, hy), ln, font=f_head, fill=INK)
            hy += 21
        if len(head_lines) > 2:
            ov.trims += 1
        dy = hy + 2
        deck_lines = wrap_text(lead["deck"], f_deck, col_w)
        for ln in deck_lines[:3]:
            ov.check(ln, f_deck, col_w)
            drw.text((x, dy), ln, font=f_deck, fill=SOFT)
            dy += 15
        if len(deck_lines) > 3:
            ov.trims += 1
    return y + 16 + art_h + 8 + 42 + 2 + 45


CONTINENTS = [
    [(7, 21), (42, 7), (105, 4), (154, 21), (161, 39), (133, 56), (126, 70), (105, 80), (91, 77), (63, 60), (63, 38), (3, 84)],
    [(150, 6), (162, 4), (166, 12), (154, 16)],
    [(120, 82), (145, 76), (172, 95), (162, 128), (140, 148), (122, 122), (112, 96)],
    [(215, 35), (245, 15), (275, 25), (270, 50), (240, 55), (220, 48)],
    [(205, 55), (245, 45), (275, 60), (270, 100), (245, 140), (225, 120), (210, 85)],
    [(275, 15), (330, 5), (420, 10), (455, 30), (430, 60), (390, 75), (350, 60), (310, 50), (280, 35)],
    [(385, 112), (430, 108), (445, 128), (400, 134)],
]

PIN_XY = {
    "SEOUL": (380, 60), "BRUSSELS": (227, 34), "NEW YORK": (125, 48),
    "GAZA": (266, 62), "HORMUZ": (295, 67), "ADDIS ABABA": (273, 92),
    "QUITO": (120, 105), "TOKYO": (410, 48),
}

PIN_LABEL = {
    "SEOUL": (-52, 8), "BRUSSELS": (-58, -6), "NEW YORK": (-62, -6),
    "GAZA": (10, -14), "HORMUZ": (10, -14), "ADDIS ABABA": (10, -6),
    "QUITO": (-52, 8), "TOKYO": (10, -6),
}


def draw_map_band(drw, data, y, ov):
    map_x, map_y = MARGIN, y
    map_w, map_h = 470, 174
    f_title = font(SANS_B, 11)
    drw.text((map_x, map_y), "THE WORLD — 8 PLACES THAT MATTER TODAY", font=f_title, fill=INK)
    my = map_y + 18
    drw.rectangle([map_x, my, map_x + map_w, my + map_h - 18], fill=SEA, outline=RULE)
    ox, oy = map_x, my
    for poly in CONTINENTS:
        pts = [(ox + px, oy + py) for px, py in poly]
        drw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_pin = font(SANS_B, 9)
    f_lab = font(SANS_B, 8)
    for pin in data["map_pins"]:
        px, py = PIN_XY[pin["city"]]
        cx, cy = ox + px, oy + py
        drw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=(255, 255, 255), width=1)
        num = str(pin["n"])
        tw = f_pin.getlength(num)
        drw.text((cx - tw / 2, cy - 5), num, font=f_pin, fill=(255, 255, 255))
        dx, dy = PIN_LABEL[pin["city"]]
        drw.text((cx + dx, cy + dy), pin["city"], font=f_lab, fill=INK)
    rx = map_x + map_w + 18
    rw = PAGE_W - MARGIN - rx
    drw.text((rx, map_y), "THE DAY IN UTC", font=f_title, fill=INK)
    f_time = font(SANS_B, 11)
    f_tl = font(SANS, 11)
    ty = map_y + 16
    for item in data["timeline"]:
        drw.text((rx, ty), item["utc"], font=f_time, fill=RED)
        lines = wrap_text(item["text"], f_tl, rw - 52)
        ly = ty
        for ln in lines[:1]:
            ov.check(ln, f_tl, rw - 52)
            drw.text((rx + 50, ly), ln, font=f_tl, fill=INK)
            ly += 13
        if len(lines) > 1:
            ov.trims += 1
        ty += 16
    return map_y + map_h + 8


def draw_briefs(drw, data, y, ov):
    col_w = (PAGE_W - 2 * MARGIN - 16) / 2
    f_num = font(SANS_B, 11)
    f_city = font(SANS_B, 10)
    f_head = font(SANS, 11)
    pitch = 16
    left = data["briefs"][:21]
    right = data["briefs"][21:]
    for col_i, group in enumerate((left, right)):
        x = MARGIN + col_i * (col_w + 16)
        cy = y
        for b in group:
            num = str(b["n"])
            drw.text((x, cy), num, font=f_num, fill=RED)
            nx = x + 22
            city = b["city"]
            drw.text((nx, cy + 1), city, font=f_city, fill=INK)
            hx = nx + f_city.getlength(city) + 8
            head = b["headline"]
            avail = x + col_w - 62 - hx
            ov.check(head, f_head, avail)
            if f_head.getlength(head) > avail:
                ov.trims += 1
                while head and f_head.getlength(head + "…") > avail:
                    head = head[:-1]
                head += "…"
            drw.text((hx, cy + 1), head, font=f_head, fill=INK)
            badge(drw, x + col_w - 58, cy, b["badge"])
            cy += pitch
    return y + 21 * pitch


def draw_footer(drw, data, y, ov):
    hline(drw, y, MARGIN, PAGE_W - MARGIN, width=2)
    f_h = font(SANS_B, 11)
    f_t = font(SANS, 10)
    drw.text((MARGIN, y + 6), "DATE CHECK", font=f_h, fill=RED)
    w = PAGE_W - 2 * MARGIN
    lines = []
    for key in ("included", "excluded", "not_yet", "sources"):
        lines += wrap_text(data["date_check"][key], f_t, w)
    cy = y + 22
    for ln in lines:
        drw.text((MARGIN, cy), ln, font=f_t, fill=SOFT)
        cy += 13
    return cy


def main():
    with open(DATA, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    ov = Overflow()
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    drw = ImageDraw.Draw(img)
    y = draw_masthead(drw, data, ov)
    y = draw_chips(drw, data, y)
    y = draw_stats(drw, data, y)
    y = draw_leads(drw, data, y, ov)
    y = draw_map_band(drw, data, y, ov)
    y = draw_briefs(drw, data, y, ov)
    y = draw_footer(drw, data, y, ov)
    img.save(OUT, format="PNG")
    size = os.path.getsize(OUT)
    print("drew %s (%dx%d, %d bytes)" % (OUT, PAGE_W, PAGE_H, size))
    print("layout: trims=%d overflows=%d bottom_y=%d" % (ov.trims, ov.overs, y))
    print("stories: %d briefs + %d leads = %d" % (
        len(data["briefs"]), len(data["leads"]),
        len(data["briefs"]) + len(data["leads"])))


if __name__ == "__main__":
    main()
