"""doom-satellite-merge-wad: merge a LittleFS image holding the DOOM WAD into the Teensy 4.1 DoomFlight hex.

The partition geometry must match the 'wad' partition in boards/teensy41.overlay: offset 0x100000 in the 8 MB W25Q64
program flash, 4 KiB blocks, 6912 KiB (ending at 0x7C0000, the limit of what teensy_loader_cli programs). The output
hex programs the firmware and the filesystem in one teensy_loader_cli pass; the firmware mounts the partition at /lfs
and the engine loads /lfs/doom1.wad.
"""
import argparse
import sys

from intelhex import IntelHex
from littlefs import LittleFS

FLASH_BASE = 0x60000000
PART_OFFSET = 0x100000
PART_BASE = FLASH_BASE + PART_OFFSET
BLOCK = 4096
PART_SIZE = 6912 * 1024  # up to 0x7C0000, the end of the range teensy_loader_cli programs
COUNT = PART_SIZE // BLOCK
WAD_NAME = "doom1.wad"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="doom-satellite-merge-wad", description=__doc__.split("\n\n")[1])
    parser.add_argument("firmware", help="zephyr.hex produced by the teensy41 build (build-artifacts/zephyr.hex)")
    parser.add_argument("wad", help="doom1.wad (fprime-get-doom)")
    parser.add_argument("output", help="merged Intel HEX for teensy_loader_cli")
    parser.add_argument("--name", default=WAD_NAME, help="file name inside /lfs (default %(default)s)")
    args = parser.parse_args(argv)

    with open(args.wad, "rb") as f:
        data = f.read()
    fs = LittleFS(block_size=BLOCK, block_count=COUNT)
    with fs.open(args.name, "wb") as f:
        f.write(data)
    print("lfs: wrote %s, %d bytes (%d KiB of %d KiB free for uploads)"
          % (args.name, len(data), (PART_SIZE - len(data)) // 1024 - 64, PART_SIZE // 1024))
    image = fs.context.buffer
    ih = IntelHex(args.firmware)
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
    ih.write_hex_file(args.output)
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
