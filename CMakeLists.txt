####
# This sets up the build system for the 'doom-satellite' project, including components and deployments from
# DoomSatellite/. It also imports the core F Prime components.
#
# Deployments:
#   DoomFlight:      Teensy 4.1 / RP2040 (Zephyr) flight software. Built with the default 'zephyr' toolchain.
#   DoomCoprocessor: arm-linux coprocessor software. Built with the 'aarch64-linux' toolchain.
####
cmake_minimum_required(VERSION 3.24.2)
# Zephyr is loaded only for the Zephyr toolchain and not when testing (F Prime unit tests run on Linux)
if (NOT BUILD_TESTING AND CMAKE_TOOLCHAIN_FILE MATCHES "/zephyr\\.cmake$")
    find_package(Zephyr HINTS "${CMAKE_CURRENT_LIST_DIR}/lib/zephyr-workspace")
endif()
project(doom-satellite C CXX)

###
# F' Core Setup
# This includes all of the F prime core components, and imports the make-system.
###
include("${CMAKE_CURRENT_LIST_DIR}/lib/fprime/cmake/FPrime.cmake")
# NOTE: register custom targets between these two lines
fprime_setup_included_code()

# This includes project-wide objects
add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/DoomSatellite")

if (FPRIME_PLATFORM STREQUAL "Zephyr")
    # Upstream DOOM's config.h defines VERSION, which the NXP SoC headers (reached through the POSIX headers DOOM
    # includes after config.h) use as a register name. Pull the kernel headers in first: later includes are guarded,
    # so VERSION is never expanded inside them and the upstream sources stay untouched.
    target_compile_options(fprime_stress_doomgeneric PRIVATE -include zephyr/kernel.h)
    set_target_properties(Svc_FatalHandler PROPERTIES EXCLUDE_FROM_ALL TRUE)
    set_target_properties(fprime-zephyr_Drv_ZephyrSpiDriver PROPERTIES EXCLUDE_FROM_ALL TRUE)
    set_target_properties(Drv_TcpClient Drv_TcpServer PROPERTIES EXCLUDE_FROM_ALL TRUE)
endif()
