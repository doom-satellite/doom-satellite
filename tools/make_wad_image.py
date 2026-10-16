#!/usr/bin/env python3
"""Merge a LittleFS image holding the DOOM WAD into a Teensy 4.1 DoomFlight zephyr.hex.

The partition geometry must match the 'wad' partition in boards/teensy41.overlay: offset 0x180000 in the 8 MB W25Q64
program flash, 4 KiB blocks, 6400 KiB. The output hex programs the firmware and the filesystem in one teensy_loader_cli
pass; the firmware mounts the partition at /lfs and the engine loads /lfs/doom1.wad.

usage: make_wad_image.py <zephyr.hex> <doom1.wad> <out.hex>
"""
import sys

from intelhex import IntelHex
from littlefs import LittleFS

FLASH_BASE = 0x60000000
PART_OFFSET = 0x180000
PART_BASE = FLASH_BASE + PART_OFFSET
BLOCK = 4096
COUNT = (6400 * 1024) // BLOCK
WAD_NAME = "doom1.wad"


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    src, wad_path, out = argv[1:4]
    fs = LittleFS(block_size=BLOCK, block_count=COUNT)
    with open(wad_path, "rb") as f:
        data = f.read()
    with fs.open(WAD_NAME, "wb") as f:
        f.write(data)
    print("lfs: wrote %s, %d bytes" % (WAD_NAME, len(data)))
    image = fs.context.buffer
    ih = IntelHex(src)
    print("firmware: 0x%08x..0x%08x" % (ih.minaddr(), ih.maxaddr()))
    if ih.maxaddr() >= PART_BASE:
        print("error: firmware overlaps the WAD partition at 0x%08x" % PART_BASE, file=sys.stderr)
        return 1
    nonblank = 0
    for b in range(COUNT):
        blk = image[b * BLOCK:(b + 1) * BLOCK]
        if any(x != 0xFF for x in blk):
            nonblank += 1
            ih.puts(PART_BASE + b * BLOCK, bytes(blk))
    print("lfs: %d/%d blocks written" % (nonblank, COUNT))
    ih.write_hex_file(out)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
