# ======================================================================
# DoomConfig.fpp
# Single compile-time configuration file for the DOOM stress-test
# library. Deployments override this file (register_fprime_config) to
# retune the pipeline for their bandwidth and memory budgets.
# ======================================================================

module Doom {

  # ----------------------------------------------------------------------
  # Engine geometry: DOOM's native 320x200 (DOOM_FRAME_SCALE=1, the
  # fprime-stress CMake default). On the Teensy the frame lives in QSPI
  # PSRAM and the 640x400 upscale cost more per tick than the renderer.
  # ----------------------------------------------------------------------

  @ Width of the full-resolution DOOM frame in pixels.
  constant FRAME_WIDTH = 320

  @ Height of the full-resolution DOOM frame in scanlines.
  constant FRAME_HEIGHT = 200

  @ Number of palette bytes (256 entries * 3 bytes per RGB triple).
  constant PALETTE_BYTES = 768

  # ----------------------------------------------------------------------
  # Downsampling. The factor is fixed at build time so the FrameRow
  # pixel array (and therefore the on-wire row size) is exactly the
  # downsampled width: size for the available bandwidth here, and let
  # the com layer (e.g. ComQueue) shed frames if bandwidth drops.
  # ----------------------------------------------------------------------

  @ Downsample factor applied to each frame dimension. Must divide
  @ FRAME_WIDTH and FRAME_HEIGHT evenly. 4 keeps the 80 x 50 rows the
  @ 115200-baud USB UART downlink was sized for.
  constant DOWNSAMPLE_FACTOR = 4

  @ Width in pixels of the downsampled frame (and of each FrameRow).
  constant DOWNSAMPLED_WIDTH = FRAME_WIDTH / DOWNSAMPLE_FACTOR

  @ Height in scanlines of the downsampled frame: FrameRow channels
  @ 0 .. DOWNSAMPLED_HEIGHT-1 are emitted per frame.
  constant DOWNSAMPLED_HEIGHT = FRAME_HEIGHT / DOWNSAMPLE_FACTOR

  # ----------------------------------------------------------------------
  # Engine memory
  # ----------------------------------------------------------------------

  @ Capacity (in frames) of the screen-wipe melt playback ring. The
  @ melt animation spans roughly 40-70 engine draws; each slot costs
  @ FRAME_WIDTH * FRAME_HEIGHT bytes (80 -> ~20.5 MB). Reduce on
  @ memory-constrained systems: overflowing frames are dropped and
  @ counted, and the wipe cuts to the live frame early.
  constant MELT_QUEUE_CAPACITY = 1

}

module DoomSubtopologyConfig {

  @ Base ID for the Doom subtopology, which runs on DoomFlight. It must
  @ stay below DoomFlight's REMOTE_BASE_OPCODE (0x20000000): opcodes at
  @ or above it are forwarded through the hub to DoomCoprocessor.
  constant BASE_ID = 0x1D000000

  @ BufferManager pool sizing for the Doom subtopology.
  module BuffMgr {
    @ Per-buffer size of the general-purpose Doom pool.
    constant doomBuffSize  = 4096
    @ Number of buffers in the general-purpose Doom pool.
    constant doomBuffCount = 16
    @ BufferManager identifier (unique within the deployment).
    constant doomBuffMgrId = 0x0D
  }

}
