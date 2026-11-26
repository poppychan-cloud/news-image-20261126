# news-image-20261126 v2 entrypoint (Python 3.13, standard library only).
#
# The finished newspaper is entry.png next to this file, rendered by
# draw.py from stories.json with PIL. Everything on the page is drawn in
# code, so the image cannot come out garbled. This program only checks
# the image against the competition caps (1024x1024, 1 MiB) and drops a
# copy where the grader looks for it, /output/entry.png.
#
# Local stand-in for /output:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(HERE, "entry.png")

MAX_SIDE = 1024
MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def check_image(path):
    """Read the PNG header and size; return (width, height, bytes)."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG file")
    wide, tall = struct.unpack(">II", head[16:24])
    if wide > MAX_SIDE or tall > MAX_SIDE:
        raise SystemExit("image is %dx%d, over the 1024 cap" % (wide, tall))
    nbytes = os.path.getsize(path)
    if nbytes > MAX_BYTES:
        raise SystemExit("image is %d bytes, over the 1 MiB cap" % nbytes)
    return wide, tall, nbytes


def main():
    if not os.path.exists(IMAGE):
        raise SystemExit("entry.png missing — run draw.py first")
    wide, tall, nbytes = check_image(IMAGE)
    target = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target, exist_ok=True)
    dest = os.path.join(target, "entry.png")
    shutil.copyfile(IMAGE, dest)
    os.chmod(dest, 0o644)
    print("wrote %s (%dx%d, %d bytes)" % (dest, wide, tall, nbytes))


if __name__ == "__main__":
    main()
