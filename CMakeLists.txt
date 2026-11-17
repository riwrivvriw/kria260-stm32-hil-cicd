cmake_minimum_required(VERSION 3.20.0)

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
