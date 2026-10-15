# Pair with protocol peers

ext-posi below; uart / i2c / spi beside; gpio-framework sits above — this package is GPIO bindings only.

## Composition boundary

`microscrap/gpio` is **bindings only** — libgpiod-style chip / line / edge helpers over character devices. It does not register Chassis providers, invent chip board drivers, or own application GPIO orchestration.[^readme][^agents]

| Concern | Package |
|---------|---------|
| Native FD / syscall / ioctl | **ext-posi** `^0.10.0` (global `posix_*`, `ioctl`, `fcntl` functions; required) |
| GPIO chip / line uAPI v2 | `microscrap/gpio` (this package) |
| UART | `microscrap/uart` `^0.10` (sibling protocol) |
| I2C | `microscrap/i2c` `^0.10` (sibling protocol) |
| SPI | `microscrap/spi` `^0.10` (sibling protocol) |
| USB MPSSE / FTDI | `microscrap/ftdi` / `microscrap/mpsse` (beside — USB path, not a gpio child) |
| Higher GPIO orchestration | `scrapyard-io/framework` `^0.10` (suggested; above this package)[^composer] |

## Typical flow

1. Depend on this package (requires **ext-posi** `^0.10.0`).[^composer]
2. Open `/dev/gpiochipN`, configure lines, request ownership, read/write / edge-wait via `gpiod_*` helpers.[^readme][^chip]
3. Application / `gpio-framework` composes this peer — do not invent framework providers inside this package.[^agents]

## Caveats

- Host permissions on `/dev/gpiochip*` matter — see [GPIO device permissions](/docs/{{version}}/ecosystem/gpio-modules/gpio/traps/gpio-device-permissions).
- Helper globals use `function_exists` guards — see [`function_exists` load order](/docs/{{version}}/ecosystem/gpio-modules/gpio/traps/function-exists-load-order).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/package-010)
* [Helpers → gpiod facades → posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi)

[^composer]: Require ext-posi; suggest gpio-framework
[^readme]: Bindings role and requirements
[^agents]: Suggested peer only; no framework internals
[^chip]: Chip open uses posix_open with O_RDWR | O_CLOEXEC
