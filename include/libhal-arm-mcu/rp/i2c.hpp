#pragma once

#include "rp.hpp"
#include <libhal/i2c.hpp>
#include <libhal/initializers.hpp>
#include <libhal/units.hpp>

namespace hal::rp::inline v4 {
/*
RP2350 supports a baud rate of up to 1 MHz
*/
struct i2c final : public hal::i2c
{
  i2c(pin_param auto p_sda,
      pin_param auto p_scl,
      bus_param auto p_bus,
      settings const& p_settings = {})
    : i2c(p_sda(), p_scl(), p_bus(), p_settings)
  {
    static_assert(p_bus() == 0 || p_bus() == 1, "Invalid bus selected!");
    static_assert(p_sda() % 4 == 0 || p_bus() != 0, "SDA pin for I2C0 is invalid!");
    static_assert(p_scl() % 4 == 1 || p_bus() != 0, "SCL pin for I2C0 is invalid!");
    static_assert(p_sda() % 4 == 2 || p_bus() != 1, "SDA pin for I2C1 is invalid!");
    static_assert(p_scl() % 4 == 3 || p_bus() != 1, "SCL pin for I2C1 is invalid!");
  }
  i2c(i2c&&) = delete;
  ~i2c() override;

private:
  i2c(u8 p_sda, u8 p_scl, u8 p_chan, settings const&);
  void driver_configure(settings const&) override;

  /*
  This function does not correctly use the timeout function, and will
  throw it's own timeout exceptions if a transaction takes any longer
  than 10 ms.
  */
  void driver_transaction(hal::byte p_addr,
                          std::span<hal::byte const> p_out,
                          std::span<hal::byte> p_in,
                          hal::function_ref<hal::timeout_function>) override;

  u8 m_sda, m_scl, m_chan;
};

}  // namespace hal::rp::inline v4
