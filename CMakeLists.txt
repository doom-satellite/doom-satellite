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
    # Unused fprime-zephyr drivers; LoRa also asserts against the Zephyr 4.4 lora enum (this tree is on 4.3)
    set_target_properties(fprime-zephyr_Drv_ZephyrSpiDriver fprime-zephyr_Drv_LoRa PROPERTIES EXCLUDE_FROM_ALL TRUE)
    set_target_properties(Drv_TcpClient Drv_TcpServer PROPERTIES EXCLUDE_FROM_ALL TRUE)
else()
    # fprime-zephyr is a library location for every toolchain (settings.ini) and its modules need the Zephyr headers,
    # so on native builds keep everything it registers out of the default target (nothing there is selected anyway).
    function(doom_exclude_directory_targets dir)
        get_property(dir_targets DIRECTORY "${dir}" PROPERTY BUILDSYSTEM_TARGETS)
        foreach(dir_target IN LISTS dir_targets)
            set_target_properties("${dir_target}" PROPERTIES EXCLUDE_FROM_ALL TRUE)
        endforeach()
        get_property(sub_dirs DIRECTORY "${dir}" PROPERTY SUBDIRECTORIES)
        foreach(sub_dir IN LISTS sub_dirs)
            doom_exclude_directory_targets("${sub_dir}")
        endforeach()
    endfunction()
    foreach(zephyr_dir default/zephyr-config fprime-zephyr/Os fprime-zephyr/Fw fprime-zephyr/Drv fprime-zephyr/Svc
                       fprime-zephyr/Fs)
        doom_exclude_directory_targets("${CMAKE_CURRENT_LIST_DIR}/lib/fprime-zephyr/${zephyr_dir}")
    endforeach()
endif()
