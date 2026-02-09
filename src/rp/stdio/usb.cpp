#include "../stdio_init.hpp"

#include <pico/stdio_usb.h>

namespace hal::rp::internal {
void init_stdio()
{
  stdio_usb_init();
}
}  // namespace hal::rp::internal
