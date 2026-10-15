# Pair with protocol peers

ext-posi below for FDs and termios; gpio / i2c / spi sit beside; ftdi/mpsse beside for USB; framework above.

## Composition boundary

`microscrap/uart` is **bindings only** — serial open/configure/read/write, modem lines, and termios helpers. It does not implement GPIO chip APIs, I2C/SPI transfers, USB MPSSE, or Chassis registration.[^readme][^agents]

| Concern | Package |
|---------|---------|
| POSIX FD / termios / ioctl | **ext-posi** `^0.10.0` (below — global functions: `posix_*`, `tcgetattr`, `ioctl`, ...)[^serial] |
| UART / serial (this package) | `microscrap/uart` |
| GPIO | `microscrap/gpio` `^0.10` |
| I2C | `microscrap/i2c` `^0.10` |
| SPI | `microscrap/spi` `^0.10` |
| USB MPSSE / FTDI | `microscrap/ftdi` (sits **beside** — USB path, not a uart child) |
| Higher GPIO orchestration | `scrapyard-io/framework` `^0.10.0` (suggested; above the microscrap protocol packages) |

## Typical flow

1. Depend on this package (requires **ext-posi** `^0.10.0`).
2. Open `/dev/tty*` via `uart_open` (internally `posix_open`, `tcgetattr`, `tcsetattr`, `posi_set_baud_rate`).
3. Application / framework may compose uart with other peers — do not invent framework providers inside this package.[^agents]

## Caveats

- `UARTPort::$baud` is a numeric rate — see [BaudRate value vs numeric](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/baudrate-value-vs-numeric).
- Device node access often needs group membership — see [Serial device permissions](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/serial-device-permissions).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/package-010)
* [Helpers → Termios / posix](/docs/{{version}}/ecosystem/gpio-modules/uart/architecture/helpers-termios-ext)

[^readme]: Bindings role; requires ext-posi
[^agents]: Bindings-only role; no Chassis
[^serial]: Uses ext-posi posix_open / posix_read / posix_write / posix_close
