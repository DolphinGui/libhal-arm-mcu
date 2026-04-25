#pragma once

#include "rp.hpp"
#include <libhal/serial.hpp>

namespace hal::rp::inline v4 {
/**
 * @brief A serial device that uses the picosdk serial functions.
 * The RP-series chips have native USB, which means certain functionality
 * such as DTR reset do not work. The current implementation is not
 * guaranteed to be asynchronous, and may block spurously.
 */
struct stdio_serial final : public hal::serial
{
  stdio_serial();
  stdio_serial(stdio_serial&&) = delete;

private:
  /**
   * @brief Does nothing.
   */
  void driver_configure(settings const&) override;
  write_t driver_write(std::span<byte const>) override;
  /**
   * @brief Reads bytes from stdin
   * picosdk does not provide an interface to get how many bytes are
   * left, so this always returns 0 bytes left.
   */
  read_t driver_read(std::span<byte>) override;
  void driver_flush() override;
};

/**
 * @brief A physical serial device
 * This uses the physical uart peripherals, which has a 32-byte
 * FIFO buffer in both directions.
 */
struct uart final : public hal::serial
{

  uart(bus_param auto bus,
       pin_param auto tx,
       pin_param auto rx,
       settings const& options = {})
    : uart(bus(), tx(), rx(), options)
  {
    static_assert(bus() == 0 || bus() == 1, "Invalid UART bus selected!");
    static_assert(tx() % 4 == 0, "UART TX pin is invalid!");
    static_assert(rx() % 4 == 1, "UART TX pin is invalid!");
    static_assert(((tx() + 4) / 8) % 2 == bus(),
                  "UART TX pin and bus do not match!");
    static_assert(((rx() + 4) / 8) % 2 == bus(),
                  "UART RX pin and bus do not match!");
  }
  uart(uart&&) = delete;
  ~uart() override;

private:
  uart(u8 bus, u8 tx, u8 rx, settings const&);
  void driver_configure(settings const&) override;
  write_t driver_write(std::span<byte const>) override;
  /**
   * @brief Reads bytes in fifo buffer until span is full.
   * If there are more bytes available, then it returns a 1 since there
   * is no way to determine how many bytes are in the FIFO
   */
  read_t driver_read(std::span<byte>) override;
  void driver_flush() override;
  u8 m_tx, m_rx, m_bus;
};

}  // namespace hal::rp::inline v4
