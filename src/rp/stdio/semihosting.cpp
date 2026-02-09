#include "../stdio_init.hpp"

#include <pico/stdio_semihosting.h>

namespace hal::rp::internal {
void init_stdio()
{
  stdio_semihosting_init();
}
}  // namespace hal::rp::internal
