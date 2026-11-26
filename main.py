# news-image-20261126 entry (Python 3.13, standard library only).
#
# entry.png beside this file is the finished newspaper, produced by
# draw.py from stories.json with PIL (all text and pictures are drawn in
# code, so nothing can come out garbled). This program checks the image
# against the competition limits (1024x1024, 1 MiB) and drops a copy at
# /output/entry.png for the grader.
#
# Local stand-in for /output:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(BASE, "entry.png")
LIMIT_BYTES = 1024 * 1024
LIMIT_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def measure(path):
    """Pull width, height and size out of the file; reject bad input."""
    with open(path, "rb") as handle:
        prefix = handle.read(33)
    if prefix[:8] != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG file")
    wide = int.from_bytes(prefix[16:20], "big")
    tall = int.from_bytes(prefix[20:24], "big")
    if wide > LIMIT_SIDE or tall > LIMIT_SIDE:
        raise SystemExit("image is %dx%d, over the 1024 cap" % (wide, tall))
    nbytes = os.path.getsize(path)
    if nbytes > LIMIT_BYTES:
        raise SystemExit("image is %d bytes, over the 1 MiB cap" % nbytes)
    return wide, tall, nbytes


def run():
    if not os.path.exists(IMAGE):
        raise SystemExit("entry.png missing — run draw.py first")
    wide, tall, nbytes = measure(IMAGE)
    target = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target, exist_ok=True)
    dest = os.path.join(target, "entry.png")
    shutil.copyfile(IMAGE, dest)
    os.chmod(dest, 0o644)
    print("wrote %s (%dx%d, %d bytes)" % (dest, wide, tall, nbytes))


if __name__ == "__main__":
    run()
