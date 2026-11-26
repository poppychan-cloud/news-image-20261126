#!/usr/bin/env python3
"""Entry point for the news-image-20261126 make.fun entry.

Validates entry.png (PNG header, 1024x1024, at most 1 MiB) and copies it to
the output directory. The harness runs this program twice and requires both
runs to write identical bytes, so this script does no rendering and touches
no clock, network, or randomness.
"""
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
WANT_SIZE = (1024, 1024)


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    return 1


def main():
    src = HERE / "entry.png"
    if not src.is_file():
        return fail("entry.png is missing")
    data = src.read_bytes()
    if data[:8] != PNG_MAGIC:
        return fail("entry.png is not a PNG file")
    if len(data) > MAX_BYTES:
        return fail(f"entry.png is {len(data)} bytes, over the 1 MiB cap")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != WANT_SIZE:
        return fail(f"entry.png is {width}x{height}, expected 1024x1024")
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out / "entry.png")
    print(f"wrote {out / 'entry.png'} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
