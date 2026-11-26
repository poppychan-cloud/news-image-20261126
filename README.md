# The World in One Day — Thursday 26 November 2026

A one-page newspaper front page for the make.fun `news-image-20261126`
bounty. 45 stories, all of which happened or were first reported on
Thursday 26 November 2026, laid out as a 1024×1024 image.

## What is on the page

- **Three illustrated leads** (top): the Bank of Korea's rate decision, the
  EU special summit on Ukraine's €45bn lifeline, and ESA Hera's first
  close-ups of the Dimorphos crater. Each has an original procedural
  drawing, a verification badge, a summary, a key fact, and a
  "WHY IT MATTERS" line.
- **Big-number stat strip**: 3.25%, €45bn, 166, $122bn, 31, 10.
- **Region + field taxonomy**: 8 regions and 11 fields, counted from the
  story data.
- **THE DAY IN UTC**: a timeline of the day's moments in UTC.
- **WHERE IT HAPPENED**: a large numbered world map (8 markers) plus ONE
  numbered brief list (42 briefs) whose numbers match the map.
- **Verification badges**: OFFICIAL / REPORTED / CLAIM on every story,
  with a legend at the bottom.
- **DATE CHECK footer**: every story is dated 26 November 2026, with the
  older news that was deliberately left out and the events that have not
  happened yet.

## Files

- `entry.png` — the rendered front page (1024×1024, under 1 MiB).
- `stories.json` — all 45 stories plus the stat strip, timeline, map
  markers, and footer text.
- `draw.py` — the renderer. Reads `stories.json`, writes `entry.png`.
  Deterministic: fixed seed, no clock, no network. Prints a layout report
  naming any trimmed or clipped text (the report is clean: zero trims,
  zero overflows).
- `main.py` — the entry point. Validates `entry.png` (PNG header,
  1024×1024, ≤ 1 MiB) and copies it to `/output` (or
  `$MAKEFUN_OUTPUT_DIR`).

## Rebuild

```sh
python3 draw.py
```

Rebuilt 2026-11-26 in a fresh post-opening session (v1.1 content
unchanged; the first build session predated the competition opening and
could not be submitted as-is).

## Sources

Reuters, AP, BBC, ESA, Consilium, Bank of Korea.
