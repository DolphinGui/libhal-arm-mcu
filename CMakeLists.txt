# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 3.15)

if(DEFINED ENV{PICO_SDK_PATH})
set(PICO_CXX_ENABLE_EXCEPTIONS 1)
set(CMAKE_ASM_FLAGS_INIT "-mcpu=cortex-m33 -mfloat-abi=hard")
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)
endif()

project(libhal-arm-mcu LANGUAGES CXX C ASM)

# Should probably refine this to actually not compile
# drivers for all platforms all the time, but for now this
# serves my purposes
if(NOT DEFINED ENV{PICO_SDK_PATH})
set(source_list
  src/system_controller.cpp
  src/dwt_counter.cpp
  src/interrupt.cpp
  src/systick_timer.cpp

  # lpc40
  src/lpc40/adc.cpp
  src/lpc40/can.cpp
  src/lpc40/clock.cpp
  src/lpc40/dac.cpp
  src/lpc40/dma.cpp
  src/lpc40/i2c.cpp
  src/lpc40/input_pin.cpp
  src/lpc40/interrupt_pin.cpp
  src/lpc40/interrupt.cpp
  src/lpc40/output_pin.cpp
  src/lpc40/pin.cpp
  src/lpc40/power.cpp
  src/lpc40/pwm.cpp
  src/lpc40/spi.cpp
  src/lpc40/dma_spi.cpp
  src/lpc40/stream_dac.cpp
  src/lpc40/uart.cpp

  # stm32_generic
  src/stm32_generic/i2c.cpp
  src/stm32_generic/pwm.cpp
  src/stm32_generic/quadrature_encoder.cpp
  src/stm32_generic/spi.cpp
  src/stm32_generic/timer.cpp
  src/stm32_generic/uart.cpp

  # stm32f1
  src/stm32f1/can.cpp
  src/stm32f1/clock.cpp
  src/stm32f1/gpio.cpp
  src/stm32f1/independent_watchdog.cpp
  src/stm32f1/input_pin.cpp
  src/stm32f1/interrupt.cpp
  src/stm32f1/output_pin.cpp
  src/stm32f1/pin.cpp
  src/stm32f1/power.cpp
  src/stm32f1/pwm.cpp
  src/stm32f1/quadrature_encoder.cpp
  src/stm32f1/timer.cpp
  src/stm32f1/uart.cpp
  src/stm32f1/spi.cpp
  src/stm32f1/adc.cpp
  src/stm32f1/usart.cpp
  src/stm32f1/usb.cpp

  # stm32f411
  src/stm32f411/clock.cpp
  src/stm32f411/dma.cpp
  src/stm32f411/i2c.cpp
  src/stm32f411/input_pin.cpp
  src/stm32f411/interrupt.cpp
  src/stm32f411/output_pin.cpp
  src/stm32f411/pin.cpp
  src/stm32f411/power.cpp
  src/stm32f411/spi.cpp
  src/stm32f411/uart.cpp

  # stm32f40
  src/stm32f40/output_pin.cpp
)

set(
  test_sources
  # cortex_m
  tests/dwt_counter.test.cpp
  tests/interrupt.test.cpp
  tests/main.test.cpp
  tests/systick_timer.test.cpp

  # lpc40
  tests/lpc40/adc.test.cpp
  tests/lpc40/can.test.cpp
  tests/lpc40/i2c.test.cpp
  tests/lpc40/input_pin.test.cpp
  tests/lpc40/interrupt_pin.test.cpp
  tests/lpc40/output_pin.test.cpp
  tests/lpc40/pwm.test.cpp
  tests/lpc40/spi.test.cpp
  tests/lpc40/stream_dac.test.cpp
  tests/lpc40/uart.test.cpp

  # stm32f1
  tests/stm32f1/can.test.cpp
  tests/stm32f1/output_pin.test.cpp
  tests/stm32f1/uart.test.cpp
  tests/stm32f1/spi.test.cpp
  tests/stm32f1/adc.test.cpp
  tests/stm32f1/usb.test.cpp

  # stm32f411
  tests/stm32f411/output_pin.test.cpp
  tests/stm32f411/spi.test.cpp
)

else()

set(source_list
  src/rp/gpio.cpp
  src/rp/serial.cpp
  src/rp/i2c.cpp
  src/rp/pwm.cpp
  src/rp/adc.cpp
  src/rp/spi.cpp
  src/rp/time.cpp
  src/system_controller.cpp
  src/dwt_counter.cpp
  src/interrupt.cpp
)

pico_sdk_init()
set(pico_dep 
  hardware_gpio 
  pico_time 
  pico_stdio 
  hardware_sync
  hardware_i2c
  hardware_pwm
  hardware_adc
  hardware_spi
  hardware_uart
  hardware_timer
  pico_standard_link
  pico_crt0
  pico_newlib_interface
  pico_runtime
)

# this required copious amounts of pain to try to extract
get_target_property(LDSCRIPT_DIR pico_standard_link RP_PICO_LINK_SCRIPT_DIR)
install(FILES ${CMAKE_BINARY_DIR}/pico_flash_region.ld DESTINATION linker_scripts)
install(FILES ${LDSCRIPT_DIR}/memmap_${PICO_DEFAULT_BINARY_TYPE}.ld DESTINATION linker_scripts RENAME rpdefault.ld)

if(DEFINED NOFLASH)
  target_compile_definitions()
endif()

if(ONLY_INCLUDE_PICO_HEADERS)
list(TRANSFORM pico_dep APPEND _headers)
endif()

libhal_test_and_make_library(
  LIBRARY_NAME rp-stdio-usb
  SOURCES
  src/rp/stdio/usb.cpp
  TEST_SOURCES
  PACKAGES
  LINK_LIBRARIES
  pico_stdio_usb
  pico_newlib_interface
)

foreach(iotype uart;rtt;semihosting)
libhal_test_and_make_library(
  LIBRARY_NAME rp-stdio-${iotype}
  SOURCES
  src/rp/stdio/${iotype}.cpp
  TEST_SOURCES
  PACKAGES
  LINK_LIBRARIES
  pico_stdio_${iotype}
)
endforeach()

endif()

libhal_test_and_make_library(
  LIBRARY_NAME libhal-arm-mcu

  SOURCES
  ${source_list}

  TEST_SOURCES
  ${test_sources}

  PACKAGES
  libhal
  libhal-util
  ring-span-lite
  scope-lite

  LINK_LIBRARIES
  libhal::libhal
  libhal::util
  nonstd::ring-span-lite
  nonstd::scope-lite
  ${pico_dep}
)
