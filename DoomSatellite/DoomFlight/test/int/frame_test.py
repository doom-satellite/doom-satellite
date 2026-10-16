"""Integration tests for the DOOM frame path on DoomFlight

DoomFlight runs the engine (DoomSubtopology.doom) on its DOOM rate group (DOOM_RATE_HZ in DoomFlightTopology.cpp); each frame is downsampled by
DoomSubtopology.frameDownsampler and converted by DoomSubtopology.frameTlmProcessor into frame row and palette telemetry. DOOM must be
running (auto-started at boot, or started with DoomFlight.DoomSubtopology.doom.Start).

Run against a GDS loaded with the DoomFlight dictionary:
    pytest --dictionary DoomFlightTopologyDictionary.json frame_test.py
"""
from fprime_gds.common.testing_fw import predicates

TIMEOUT = 10
ENGINE = "DoomFlight.DoomSubtopology.doom"
DROP_CHANNELS = [
    f"{ENGINE}.FramesDropped",
    f"{ENGINE}.KeyEventsDropped",
]


def assert_counting(fprime_test_api, channel):
    """Asserts that a counter channel is positive and then increases"""
    first = fprime_test_api.assert_telemetry(
        fprime_test_api.get_telemetry_pred(channel, predicates.greater_than(0)), start="NOW", timeout=TIMEOUT
    )
    fprime_test_api.assert_telemetry(
        fprime_test_api.get_telemetry_pred(channel, predicates.greater_than(first.get_val())),
        start="NOW",
        timeout=TIMEOUT,
    )


def test_engine_running(fprime_test_api):
    """The engine reports RUNNING"""
    fprime_test_api.assert_telemetry(
        fprime_test_api.get_telemetry_pred(f"{ENGINE}.State", "RUNNING"), start="NOW", timeout=TIMEOUT
    )


def test_frames_generated(fprime_test_api):
    """The engine renders frames at a positive, non-zero rate"""
    assert_counting(fprime_test_api, f"{ENGINE}.FrameCount")
    fprime_test_api.assert_telemetry(
        fprime_test_api.get_telemetry_pred(f"{ENGINE}.FrameRateHz", predicates.greater_than(0)),
        start="NOW",
        timeout=TIMEOUT,
    )


def test_frame_rows_downlinked(fprime_test_api):
    """frameTlmProcessor converts frames into row telemetry, first to last row"""
    for channel in ["DoomFlight.DoomSubtopology.frameTlmProcessor.FrameRow000", "DoomFlight.DoomSubtopology.frameTlmProcessor.FrameRow049"]:
        fprime_test_api.assert_telemetry(channel, start="NOW", timeout=TIMEOUT)


def test_palette_downlinked(fprime_test_api):
    """frameTlmProcessor downlinks the palette"""
    fprime_test_api.assert_telemetry("DoomFlight.DoomSubtopology.frameTlmProcessor.PaletteOut", timeout=TIMEOUT)


def test_no_drops(fprime_test_api):
    """No frame or key event is dropped by the engine"""
    for channel in DROP_CHANNELS:
        fprime_test_api.assert_telemetry_count(
            0, fprime_test_api.get_telemetry_pred(channel, predicates.greater_than(0)), timeout=0
        )
