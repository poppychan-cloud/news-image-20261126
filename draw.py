#!/usr/bin/env python3
"""Render the news-image-20261126 front page (1024x1024) from stories.json.

Layout (top to bottom): masthead, region/field taxonomy, big-number stat
strip, UTC timeline, three illustrated leads, large numbered map + one
numbered brief list, DATE CHECK footer. Deterministic: fixed seed, no clock,
no network. Prints a layout report naming any trimmed or clipped text.
"""
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 12
RIGHT = W - MARGIN
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

# ---------------------------------------------------------------- palette
INK = (22, 22, 22)
PAPER = (250, 248, 243)
RED = (190, 10, 10)
BLUE = (0, 55, 130)
GREY = (105, 105, 105)
RULE = (196, 192, 184)
BADGE = {"OFFICIAL": (0, 110, 60), "REPORTED": (0, 60, 150), "CLAIM": (178, 84, 0)}
REGION_COLOR = {
    "ASIA-PACIFIC": (0, 120, 120),
    "SOUTH ASIA": (200, 110, 0),
    "MIDDLE EAST": (150, 40, 40),
    "EUROPE": (0, 55, 130),
    "AFRICA": (40, 130, 60),
    "NORTH AMERICA": (110, 60, 150),
    "LATIN AMERICA": (200, 60, 110),
    "GLOBAL": (90, 90, 90),
}
REGION_ORDER = ["ASIA-PACIFIC", "SOUTH ASIA", "MIDDLE EAST", "EUROPE",
                "AFRICA", "NORTH AMERICA", "LATIN AMERICA", "GLOBAL"]

# ------------------------------------------------------------ font helpers
def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif.ttf", s)  # no italic file on this VM
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(text, fnt, max_w, draw):
    """Greedy word wrap; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(text, fnt, max_w, draw):
    """Clip text to max_w with an ellipsis; returns (text, was_trimmed)."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text, False
    clipped = text
    while clipped and draw.textlength(clipped + "…", font=fnt) > max_w:
        clipped = clipped[:-1]
    return clipped + "…", True


def badge(draw, x, y, word, height=15):
    """Filled badge with white word; returns width used."""
    fnt = SANS_B(9)
    w = int(draw.textlength(word, font=fnt)) + 12
    draw.rounded_rectangle([x, y, x + w, y + height], radius=3,
                           fill=BADGE[word])
    draw.text((x + 6, y + 3), word, font=fnt, fill=(255, 255, 255))
    return w


def chip(draw, x, y, label, color, height=22):
    """Filled region chip; returns width used."""
    fnt = SANS_B(11)
    w = int(draw.textlength(label, font=fnt)) + 16
    draw.rounded_rectangle([x, y, x + w, y + height], radius=4, fill=color)
    draw.text((x + 8, y + 4), label, font=fnt, fill=(255, 255, 255))
    return w


# ------------------------------------------------------- procedural drawings
def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_bank(draw, x, y, w, h):
    """Central-bank facade on the left, rising rate chart on the right."""
    draw.rectangle([x, y, x + w, y + h], fill=(233, 236, 241))
    # facade, left half
    fx = x + 12
    fw = 158
    draw.polygon([(fx, y + 78), (fx + fw, y + 78), (fx + fw // 2, y + 52)],
                 fill=(28, 48, 92))
    draw.rectangle([fx + 4, y + 78, fx + fw - 4, y + 82], fill=(28, 48, 92))
    for cx in (fx + 14, fx + 52, fx + 90, fx + 128):
        draw.rectangle([cx, y + 84, cx + 12, y + 116], fill=(28, 48, 92))
    draw.rectangle([fx, y + 116, fx + fw, y + 122], fill=(28, 48, 92))
    draw.rectangle([fx - 4, y + 122, fx + fw + 4, y + h], fill=(20, 36, 70))
    # rising chart, right half
    cx0 = x + 190
    pts = [(cx0, y + 104), (cx0 + 26, y + 92), (cx0 + 52, y + 80),
           (cx0 + 78, y + 58), (cx0 + 104, y + 36), (cx0 + 122, y + 18)]
    draw.line(pts, fill=RED, width=3, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    hx, hy = pts[-1]
    draw.polygon([(hx + 2, hy - 6), (hx + 12, hy + 2), (hx - 2, hy + 6)],
                 fill=RED)
    draw.text((cx0 - 2, y + 2), "3.25%", font=SANS_B(22), fill=RED)


def draw_eu(draw, x, y, w, h):
    """EU blue panel, circle of twelve gold stars, EUR45bn below."""
    draw.rectangle([x, y, x + w, y + h], fill=(0, 45, 100))
    cx, cy, r = x + w // 2, y + 52, 34
    for k in range(12):
        ang = math.pi / 2 + k * math.pi / 6
        star(draw, cx + r * math.cos(ang), cy - r * math.sin(ang), 5,
             (255, 205, 0))
    draw.text((cx - 42, y + 92), "€45bn", font=SANS_B(26), fill=(255, 205, 0))


def draw_asteroid(draw, x, y, w, h):
    """Black space, cratered asteroid, small Hera spacecraft."""
    draw.rectangle([x, y, x + w, y + h], fill=(10, 12, 22))
    rng = random.Random(7)
    for _ in range(42):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(4, h - 4)
        r = rng.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r],
                     fill=(200, 200, 220) if rng.random() < 0.8 else (255, 220, 120))
    ax, ay, ar = x + 208, y + 70, 48
    draw.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(122, 120, 114))
    draw.ellipse([ax - ar, ay - ar, ax + ar, ay + ar],
                 outline=(70, 68, 64), width=2)
    for (cx, cy, cr, shade) in [(ax - 14, ay - 18, 12, (84, 82, 78)),
                                (ax + 10, ay + 8, 18, (72, 70, 66)),
                                (ax - 26, ay + 16, 8, (92, 90, 86)),
                                (ax + 24, ay - 22, 7, (96, 94, 90))]:
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=shade)
    draw.arc([ax - ar + 6, ay - ar + 4, ax + ar - 10, ay + ar - 16],
             start=200, end=330, fill=(190, 188, 182), width=3)
    # spacecraft, left
    sx, sy = x + 34, y + 42
    draw.rectangle([sx, sy, sx + 34, sy + 18], fill=(210, 210, 214))
    draw.rectangle([sx - 26, sy + 4, sx - 2, sy + 14], fill=(60, 90, 180))
    draw.rectangle([sx + 36, sy + 4, sx + 60, sy + 14], fill=(60, 90, 180))
    draw.line([sx + 62, sy + 9, ax - ar + 4, ay - 6], fill=(220, 220, 230),
              width=1)
    draw.text((sx - 6, sy + 24), "HERA", font=SANS_B(11), fill=(255, 255, 255))


# ------------------------------------------------------------------- map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
     (-55, 52), (-65, 44), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-90, 14), (-85, 12), (-80, 9), (-90, 20), (-100, 25), (-110, 30),
     (-120, 35), (-125, 48), (-135, 58), (-155, 58), (-168, 60)],
    # Greenland
    [(-55, 60), (-40, 64), (-30, 68), (-20, 74), (-30, 80), (-50, 78),
     (-58, 74)],
    # South America
    [(-80, 9), (-72, 2), (-78, -4), (-80, -12), (-75, -18), (-70, -30),
     (-65, -40), (-68, -52), (-60, -50), (-55, -35), (-48, -28), (-40, -22),
     (-35, -8), (-42, 0), (-52, 5), (-62, 9), (-72, 11)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (2, 51), (8, 55), (10, 59),
     (18, 56), (24, 58), (30, 62), (20, 70), (12, 68), (5, 60), (0, 55),
     (-8, 43)],
    # Africa
    [(-17, 15), (-10, 28), (0, 35), (10, 37), (20, 32), (32, 31), (35, 24),
     (40, 15), (48, 11), (51, 5), (42, -5), (38, -15), (32, -25), (22, -35),
     (15, -28), (10, -12), (8, 4), (-8, 4), (-17, 12)],
    # Asia
    [(30, 36), (40, 42), (50, 46), (60, 50), (70, 58), (80, 72), (95, 76),
     (110, 76), (130, 71), (150, 70), (170, 66), (175, 62), (160, 55),
     (150, 42), (140, 35), (130, 31), (122, 32), (115, 22), (108, 12),
     (100, 8), (96, 15), (90, 22), (80, 14), (76, 10), (70, 22), (60, 25),
     (50, 29), (40, 33), (30, 36)],
    # Australia
    [(113, -22), (115, -33), (122, -34), (130, -32), (137, -35), (144, -38),
     (150, -36), (153, -28), (147, -20), (142, -13), (136, -12), (130, -13),
     (124, -16), (118, -21)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (144, 44),
     (141, 40), (136, 35), (132, 33)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53)],
    # Indonesia
    [(95, 5), (100, 0), (105, -4), (110, -7), (116, -9), (122, -10),
     (128, -8), (134, -3), (140, -5), (135, -8), (128, -9), (120, -10),
     (112, -8), (104, -5), (98, 2)],
    # New Zealand
    [(167, -45), (171, -41), (175, -38), (174, -40), (170, -44)],
    # Madagascar
    [(43, -12), (47, -15), (50, -18), (46, -24), (43, -22), (42, -15)],
]

# markers that would collide with a neighbour get a small offset + leader
MARKER_OFFSET = {3: (16, 12), 5: (14, -16)}


def project(lon, lat, mx, my, mw, mh):
    return (mx + (lon + 180) / 360 * mw, my + (78 - lat) / 136 * mh)


def draw_map(draw, x, y, w, h, markers):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 242, 246),
                   outline=(160, 165, 170), width=1)
    for lon in range(-150, 181, 30):
        px = x + (lon + 180) / 360 * w
        draw.line([px, y, px, y + h], fill=(222, 226, 231), width=1)
    for lat in (-30, 0, 30, 60):
        py = y + (78 - lat) / 136 * h
        draw.line([x, py, x + w, py], fill=(222, 226, 231), width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, x, y, w, h) for lon, lat in poly]
        draw.polygon(pts, fill=(198, 206, 196), outline=(120, 128, 116))
    for m in markers:
        px, py = project(m["lon"], m["lat"], x, y, w, h)
        dx, dy = MARKER_OFFSET.get(m["n"], (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            draw.line([px, py, qx, qy], fill=GREY, width=1)
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        draw.ellipse([qx - 9, qy - 9, qx + 9, qy + 9], fill=RED,
                     outline=(255, 255, 255), width=1)
        num = str(m["n"])
        tw = draw.textlength(num, font=SANS_B(10))
        draw.text((qx - tw / 2, qy - 7), num, font=SANS_B(10),
                  fill=(255, 255, 255))


# ------------------------------------------------------------------ render
def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    report = {"trims": [], "overflows": []}
    leads = data["leads"]
    briefs = data["briefs"]
    stories = leads + briefs

    def region_counts():
        counts = {r: 0 for r in REGION_ORDER}
        for s in stories:
            counts[s["region"]] += 1
        return {r: c for r, c in counts.items() if c}

    def field_counts():
        counts = {}
        for s in stories:
            counts[s["field"]] = counts.get(s["field"], 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1]))

    # ---- masthead ------------------------------------------------------
    d.text((MARGIN, 4), data["masthead"], font=SANS_B(13), fill=INK)
    meta = (f"{len(stories)} STORIES  •  {len(region_counts())} REGIONS  •  "
            f"ALL FIRST REPORTED ON THURSDAY 26 NOVEMBER 2026")
    d.text((RIGHT - d.textlength(meta, font=SANS_B(10)), 7), meta,
           font=SANS_B(10), fill=GREY)
    d.text((MARGIN, 20), data["date_line"], font=SERIF_B(44), fill=INK)
    d.text((MARGIN, 70), data["ticker"], font=SERIF_I(13), fill=RED)
    d.line([MARGIN, 88, RIGHT, 88], fill=RULE, width=2)

    # ---- taxonomy chips + fields ---------------------------------------
    y = 96
    cx = MARGIN
    rc = region_counts()
    for r in REGION_ORDER:
        if r not in rc:
            continue
        cx += chip(d, cx, y, f"{r} {rc[r]}", REGION_COLOR[r]) + 6
    fc = field_counts()
    fields_line = "FIELDS — " + "  ·  ".join(f"{k} {v}" for k, v in fc.items())
    fields_line, trimmed = fit(fields_line, SANS(11), RIGHT - MARGIN, d)
    if trimmed:
        report["trims"].append("fields line")
    d.text((MARGIN, 126), fields_line, font=SANS(11), fill=INK)
    d.line([MARGIN, 146, RIGHT, 146], fill=RULE, width=1)

    # ---- stat strip ------------------------------------------------------
    stats = data["stats"]
    col_w = (RIGHT - MARGIN) / len(stats)
    for i, st in enumerate(stats):
        sx = MARGIN + i * col_w
        d.text((sx, 152), st["num"], font=SANS_B(28), fill=RED)
        d.text((sx, 184), st["cap"], font=SANS(10), fill=INK)
        if i:
            d.line([sx - 6, 154, sx - 6, 196], fill=RULE, width=1)
    d.line([MARGIN, 200, RIGHT, 200], fill=RULE, width=1)

    # ---- UTC timeline -----------------------------------------------------
    tl = data["timeline"]
    d.text((MARGIN, 208), tl["title"], font=SANS_B(11), fill=RED)
    ev = tl["events"]
    line1 = "   •   ".join(ev[:3])
    line2 = "   •   ".join(ev[3:])
    for line, ly in ((line1, 208), (line2, 222)):
        tx, trimmed = fit(line, SANS(10), RIGHT - 150, d)
        if trimmed:
            report["trims"].append(f"timeline {line[:30]}")
        d.text((150, ly), tx, font=SANS(10), fill=INK)
    d.line([MARGIN, 238, RIGHT, 238], fill=RULE, width=1)

    # ---- three illustrated leads ------------------------------------------
    lead_y = 246
    lead_w, lead_h = 322, 128
    lead_x = [MARGIN, 350, 688]
    drawers = {"bank": draw_bank, "eu": draw_eu, "asteroid": draw_asteroid}
    for i, lead in enumerate(leads):
        lx = lead_x[i]
        drawers[lead["draw"]](d, lx, lead_y, lead_w, lead_h)
        # kicker with full-word badge first
        ky = lead_y + lead_h + 8
        bw = badge(d, lx, ky - 1, lead["badge"])
        d.text((lx + bw + 6, ky), lead["kicker"], font=SANS_B(11), fill=RED)
        # headline, up to 2 lines
        hy = ky + 20
        hl = wrap(lead["headline"], SERIF_B(19), lead_w, d)
        if len(hl) > 2:
            report["overflows"].append(f"lead {i+1} headline {len(hl)} lines")
            hl = hl[:2]
        for j, ln in enumerate(hl):
            d.text((lx, hy + j * 22), ln, font=SERIF_B(19), fill=INK)
        # summary, up to 4 lines
        sy = hy + len(hl) * 22 + 4
        sl = wrap(lead["summary"], SANS(11), lead_w, d)
        if len(sl) > 4:
            report["overflows"].append(f"lead {i+1} summary {len(sl)} lines")
            sl = sl[:4]
            sl[-1], _ = fit(sl[-1] + "…", SANS(11), lead_w, d)
        for j, ln in enumerate(sl):
            d.text((lx, sy + j * 14), ln, font=SANS(11), fill=INK)
        # fact line
        fy = sy + len(sl) * 14 + 4
        fact, trimmed = fit(lead["fact"], SANS(10), lead_w, d)
        if trimmed:
            report["trims"].append(f"lead {i+1} fact")
        d.text((lx, fy), fact, font=SANS(10), fill=GREY)
        # why it matters, up to 2 lines (first line leaves room for prefix)
        wy = fy + 16
        prefix = "WHY IT MATTERS  "
        pw = d.textlength(prefix, font=SANS_B(11))
        words = lead["why"].split()
        wl, cur, first = [], "", True
        for w in words:
            avail = lead_w - pw if first else lead_w
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=SANS(11)) <= avail or not cur:
                cur = trial
            else:
                wl.append(cur)
                cur = w
                first = False
        if cur:
            wl.append(cur)
        if len(wl) > 2:
            report["overflows"].append(f"lead {i+1} why {len(wl)} lines")
            wl = wl[:2]
        for j, ln in enumerate(wl):
            if j == 0:
                d.text((lx, wy), prefix, font=SANS_B(11), fill=INK)
                d.text((lx + pw, wy), ln, font=SANS(11), fill=INK)
            else:
                d.text((lx, wy + j * 13), ln, font=SANS(11), fill=INK)

    # ---- map + numbered brief list ---------------------------------------
    sec_y = 552
    d.text((MARGIN, sec_y), data["map"]["title"], font=SANS_B(13), fill=RED)
    d.text((350, sec_y), "ALSO ON THURSDAY 26 NOVEMBER — 42 MORE STORIES",
           font=SANS_B(13), fill=RED)
    map_x, map_y, map_w, map_h = MARGIN, sec_y + 24, 318, 200
    draw_map(d, map_x, map_y, map_w, map_h, data["map"]["markers"])
    ly = map_y + map_h + 8
    marks = data["map"]["markers"]
    for row in (marks[:4], marks[4:]):
        txt = "   ".join(f"{m['n']} {m['label']}" for m in row)
        d.text((map_x, ly), txt, font=SANS(10), fill=INK)
        ly += 14
    d.text((map_x, ly + 2), "Numbers match the stories",
           font=SERIF_I(10), fill=GREY)
    # regional roundup box
    ry = ly + 20
    d.rectangle([map_x, ry, map_x + map_w, 950], outline=RULE, width=1)
    d.text((map_x + 8, ry + 6), "REGIONAL ROUNDUP", font=SANS_B(11), fill=RED)
    first = {}
    for s in briefs:
        first.setdefault(s["region"], s["headline"])
    for s in leads:
        if s.get("short"):
            first[s["region"]] = s["short"]
    rlines = []
    for r in REGION_ORDER:
        if r == "GLOBAL" or r not in first:
            continue
        rlines.append((r, first[r]))
    by = ry + 22
    for r, head in rlines:
        label = r + ": "
        d.text((map_x + 8, by), label, font=SANS_B(10), fill=INK)
        lx0 = map_x + 8 + d.textlength(label, font=SANS_B(10))
        txt, trimmed = fit(head, SANS(10), map_x + map_w - 8 - lx0, d)
        if trimmed:
            report["trims"].append(f"roundup {r}")
        d.text((lx0, by), txt, font=SANS(10), fill=INK)
        by += 13
    if by > 950:
        report["overflows"].append("roundup box past 950")

    # briefs: two columns, one line each
    col_x = [350, 688]
    col_w = 322
    row_h = (950 - (sec_y + 24)) / 21
    for idx, b in enumerate(briefs):
        col = idx // 21
        row = idx % 21
        bx = col_x[col]
        by = sec_y + 24 + row * row_h + 3
        # 1-letter badge square
        sq = 11
        d.rectangle([bx, by, bx + sq, by + sq], fill=BADGE[b["badge"]])
        letter = b["badge"][0]
        lw = d.textlength(letter, font=SANS_B(8))
        d.text((bx + (sq - lw) / 2, by + 1), letter, font=SANS_B(8),
               fill=(255, 255, 255))
        nx = bx + sq + 4
        num = f"{b['n']}"
        d.text((nx, by), num, font=SANS_B(11), fill=RED)
        tx = nx + d.textlength(num + " ", font=SANS_B(11))
        line = f"{b['dateline']} — {b['headline']}"
        txt, trimmed = fit(line, SANS(11), bx + col_w - tx, d)
        if trimmed:
            report["trims"].append(f"brief {b['n']} {b['headline'][:30]}")
        d.text((tx, by), txt, font=SANS(11), fill=INK)

    # ---- DATE CHECK + footer ----------------------------------------------
    dc = data["datecheck"]
    d.text((MARGIN, 960), "DATE CHECK — ", font=SANS_B(10), fill=RED)
    intro = "Every story above happened or was first reported on Thursday 26 November 2026."
    d.text((MARGIN + d.textlength("DATE CHECK — ", font=SANS_B(10)), 960),
           intro, font=SANS(10), fill=INK)
    for j, ln in enumerate(wrap(dc["left_out"], SANS(10), RIGHT - MARGIN, d)):
        d.text((MARGIN, 974 + j * 12), ln, font=SANS(10), fill=INK)
    d.text((MARGIN, 998), dc["not_yet"], font=SANS(10), fill=INK)
    d.text((MARGIN, 1012), data["footer"], font=SANS(9), fill=GREY)
    leg = data["legend"]
    d.text((RIGHT - d.textlength(leg, font=SANS(9)), 1012), leg,
           font=SANS(9), fill=GREY)
    return img, report, region_counts(), field_counts()


def main():
    data = json.loads((HERE / "stories.json").read_text())
    img, report, rc, fc = render(data)
    img.save(HERE / "entry.png")
    total = len(data["leads"]) + len(data["briefs"])
    print(f"stories: {total} (leads {len(data['leads'])} + briefs "
          f"{len(data['briefs'])})")
    print(f"regions: {rc}")
    print(f"fields: {fc}")
    print(f"size: {img.size}, bytes: {(HERE / 'entry.png').stat().st_size}")
    print(f"trims ({len(report['trims'])}): {report['trims']}")
    print(f"overflows ({len(report['overflows'])}): {report['overflows']}")


if __name__ == "__main__":
    main()
