cmake_minimum_required(VERSION 3.20.0)

# Only disable &ucpd1 in app.overlay when the installed Zephyr board DTS defines it
# (nucleo_h563zi added &ucpd1 in Zephyr 4.5+; older Zephyr releases on CI lack it).
set(_zephyr_base "${ZEPHYR_BASE}")
if(NOT _zephyr_base)
    set(_zephyr_base "$ENV{ZEPHYR_BASE}")
endif()
if(EXISTS "${_zephyr_base}/boards/st/nucleo_h563zi/nucleo_h563zi-common.dtsi")
    file(READ "${_zephyr_base}/boards/st/nucleo_h563zi/nucleo_h563zi-common.dtsi" _nucleo_dtsi)
    string(FIND "${_nucleo_dtsi}" "&ucpd1" _has_ucpd1)
    if(NOT _has_ucpd1 EQUAL -1)
        list(APPEND DTS_EXTRA_CPPFLAGS "-DHAS_NUCLEO_UCPD1=1")
    endif()
endif()

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(hil_stm32_firmware)

target_include_directories(app PRIVATE src)

target_sources(app PRIVATE 
    src/main.c
    src/gi_state_machine.c
    src/audio_leak.c
    src/io_controller.c
    src/kr260/kr260_pwm_receiver.c
)
