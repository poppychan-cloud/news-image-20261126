# The World in One Day — 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/poppychan-cloud/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/poppychan-cloud/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261126): sum up 26 November's world news in one image.

The evening edition of Thursday 26 November 2026 in a single
1024×1024 image: 45 stories (3 illustrated leads + 42 numbered briefs)
across 8 regions and 9 fields, a big-number stat strip, a large numbered
world map, a full-width UTC timeline, and a DATE CHECK footer that names
what was left out and what had not happened yet.

The day's three leads: the Bank of Korea lifts its rate to 3.25%
(official, on a 5–2 vote), EU leaders open their budget and Ukraine-loan
summit in Brussels, and Brent crude nears $91 after Houthi strikes on
Saudi energy sites.

## Files

- `stories.json` — every story on the page: 3 leads, 42 briefs, 6 stats,
  7 timeline moments, 8 map pins, and the DATE CHECK copy.
- `draw.py` — the renderer. Pure PIL, no network, no clock, no random
  numbers: two runs produce the same bytes. Prints a layout report
  (trims / overflows) when it runs.
- `main.py` — the entrypoint. Validates `entry.png` (PNG header,
  1024×1024, at most 1 MiB) and copies it to `/output/entry.png`
  (`MAKEFUN_OUTPUT_DIR` stands in for `/output` outside the grader).
- `entry.png` — the finished page, drawn by `draw.py`.

## Reproduce

```sh
python3 draw.py        # renders entry.png, prints the layout report
python3 main.py        # validates and copies it to /output/entry.png
```

## Date discipline

Every story in this edition was first reported on Thursday 26 November
2026. The DATE CHECK footer on the page lists the older stories that
were deliberately left out (Shenzhou-24, Hera images, Cairo tanker fire,
the Netanyahu hearing, Venezuela's debt framework, the Solomon Islands
treaty, US Section 301 tariffs, BepiColombo) and the items that had not
happened yet at press time (the EU summit conclusions, Friday's
shortened US trading).

Badges on every story: OFFICIAL = issued by the body named, REPORTED =
carried by two or more wires, CLAIM = asserted, not verified.

## Licence

MIT — see `LICENSE`.
