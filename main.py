#!/usr/bin/env python3
"""Entry program for news-image-20261126 V2.

Validates the pre-rendered entry.png (PNG header, 1024x1024, at most 1 MiB)
and copies it to the output directory. Standard library only, no network.
The image is drawn by draw.py from stories.json; this program only checks
and copies it, so two runs write the same bytes.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    try:
        with open(src, "rb") as f:
            data = f.read()
    except OSError as exc:
        print("entry.png missing: %s" % exc)
        return 1
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG")
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        print("entry.png is %dx%d, need 1024x1024" % (width, height))
        return 1
    if len(data) > 1024 * 1024:
        print("entry.png is %d bytes, over 1 MiB" % len(data))
        return 1
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    shutil.copyfile(src, os.path.join(outdir, "entry.png"))
    print("ok: entry.png %d bytes, 1024x1024 -> %s"
          % (len(data), os.path.join(outdir, "entry.png")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
