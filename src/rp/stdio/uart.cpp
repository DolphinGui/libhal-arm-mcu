#include "../stdio_init.hpp"

#include <pico/stdio_uart.h>

namespace hal::rp::internal {
void init_stdio()
{
  stdio_uart_init();
}
}  // namespace hal::rp::internal
