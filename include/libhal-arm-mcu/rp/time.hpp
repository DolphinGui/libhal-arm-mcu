#pragma once

#include <chrono>
#include <libhal/steady_clock.hpp>

namespace hal::rp::inline v4 {

/**
 * @brief A 1 MHz timer
 * The default 1 MHz timer used frequently inside of picosdk itself.
 * On the RP2350, the timer is in the always-on domain, meaning it is
 * always available.
 */
struct clock final : public hal::steady_clock
{
  clock() = default;
  clock(clock const&) = default;
  /**
   * @brief Returns clock frequency, which is always 1 MHz
   */
  hertz driver_frequency() override;
  /**
   * @brief Returns clock uptime, which is always in us
   */
  u64 driver_uptime() override;
};

/**
 * @brief Returns SYS_CLK_HZ, intended to be used with dwt_counter
 */
hertz core_clock();

using microseconds = std::chrono::duration<u64, std::micro>;
/**
 * @brief A sleep function optimized for power.
 * Unlike hal::delay, which busy waits, sleep may cause a low-power
 * mode to be entered, reducing power consumption.
 */
void sleep(std::chrono::duration<u64, std::micro> time) noexcept;

}  // namespace hal::rp::inline v4
