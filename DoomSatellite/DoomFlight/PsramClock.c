// ======================================================================
// \title  PsramClock.c
// \brief  Teensy 4.1: run the FlexSPI2 (PSRAM) root clock at 120 MHz
//
// The i.MX RT1062 ROM leaves FlexSPI2 on PLL3 PFD0 (720 MHz) divided by 8, i.e. a 90 MHz root; the
// Zephyr memc driver can only divide that root further. Lowering the CCM divider to /6 gives a
// 120 MHz root, inside the APS6404L's 133 MHz rating but above Teensyduino's 88 MHz default.
// Runs in PRE_KERNEL_1, before the memc driver (POST_KERNEL) programs SERCLKDIV from the
// devicetree spi-max-frequency, which must be raised to 120 MHz to match.
// ======================================================================
#include <fsl_clock.h>
#include <zephyr/init.h>

static int doom_psram_clock_init(void) {
    CLOCK_SetDiv(kCLOCK_Flexspi2Div, 5U);  // 720 MHz / 6 = 120 MHz
    return 0;
}

SYS_INIT(doom_psram_clock_init, PRE_KERNEL_1, 10);
