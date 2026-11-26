# news-image-20261126 entrypoint (Python 3.13, standard library only).
#
# entry.png next to this file is the finished newspaper, painted by draw.py
# from stories.json with PIL (every letter and picture is drawn in code, so
# nothing can come out garbled). This script checks the picture against the
# competition limits (1024x1024, 1 MiB) and leaves a copy at
# /output/entry.png for the grader.
#
# Local stand-in for /output:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PICTURE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_HEAD = b"\x89PNG\r\n\x1a\n"


def png_dims(path):
    """Read width and height out of a PNG header; reject anything else."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if head[:8] != PNG_HEAD:
        raise SystemExit("entry.png is not a PNG file")
    wide = int.from_bytes(head[16:20], "big")
    tall = int.from_bytes(head[20:24], "big")
    return wide, tall


def check_picture(path):
    """Make sure the finished page fits the competition limits."""
    if not os.path.exists(path):
        raise SystemExit("entry.png missing — run draw.py first")
    wide, tall = png_dims(path)
    if wide > MAX_SIDE or tall > MAX_SIDE:
        raise SystemExit("image is %dx%d, over the 1024 cap" % (wide, tall))
    nbytes = os.path.getsize(path)
    if nbytes > MAX_BYTES:
        raise SystemExit("image is %d bytes, over the 1 MiB cap" % nbytes)
    return wide, tall, nbytes


def main():
    wide, tall, nbytes = check_picture(PICTURE)
    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "entry.png")
    shutil.copyfile(PICTURE, dest)
    os.chmod(dest, 0o644)
    print("copied %s -> %s (%dx%d, %d bytes)" % (PICTURE, dest, wide, tall, nbytes))


if __name__ == "__main__":
    main()
