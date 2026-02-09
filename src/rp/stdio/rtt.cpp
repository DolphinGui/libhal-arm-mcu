#include "../stdio_init.hpp"

#include <pico/stdio_rtt.h>

namespace hal::rp::internal {
void init_stdio()
{
  stdio_rtt_init();
}
}  // namespace hal::rp::internal
