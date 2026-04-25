#pragma once

#include "rp.hpp"
#include <libhal/interrupt_pin.hpp>
#include <libhal/units.hpp>

namespace hal::rp::inline v4 {
/**
 * @brief A class that enables registering interrupts for gpio changes.
 * The RP2350 has only 1 interrupt for all GPIO changes, per core, so the
 * interrupt pin class must create a core-local global to register all
 * all interrupts. This becomes a 1.5kB global variable allocated via malloc.
 * ISRs registered must be reentrant.
 */
struct interrupt_pin final : public hal::interrupt_pin
{
  interrupt_pin(pin_param auto pin, settings const& options = {})
    : interrupt_pin(pin(), options)
  {
  }
  interrupt_pin(interrupt_pin&&) = delete;
  ~interrupt_pin() override;

private:
  interrupt_pin(u8 pin, settings const&);
  void driver_configure(settings const&) override;
  void driver_on_trigger(hal::callback<handler>) override;
  u8 m_pin;
};
}  // namespace hal::rp::inline v4
