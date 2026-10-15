# Pair with protocol peers

ext-posi below; uart / gpio / spi siblings; ftdi/mpsse beside for USB; gpio-framework above.

## Composition boundary

`microscrap/i2c` is **bindings only** — open `/dev/i2c-N`, bind a slave address, raw read/write, adapter ioctls, emulated SMBus helpers, and `I2C_RDWR` combined transactions. It does not register Chassis providers or orchestrate multi-bus GPIO apps.[^readme][^agents]

| Concern | Package |
|---------|---------|
| POSIX FD / syscall / memory functions | `ext-posi` `^0.10.0` (**below** — the only requirement)[^readme][^bus] |
| I²C / SMBus device API | `microscrap/i2c` (this package) |
| UART | `microscrap/uart` `^0.10` (sibling) |
| GPIO | `microscrap/gpio` `^0.10` (sibling) |
| SPI | `microscrap/spi` `^0.10` (sibling) |
| USB MPSSE / FTDI | `microscrap/ftdi` / `microscrap/mpsse` (sit **beside** — USB path, not an i2c child) |
| Higher GPIO orchestration | `scrapyard-io/framework` `^0.10.0` (**above** the microscrap protocol packages) |

## Typical flow

1. Depend on this package (requires **ext-posi** `^0.10.0`).
2. Ensure `/dev/i2c-N` exists (`modprobe i2c-dev`) and the process can open it (see [Need i2c group /dev permissions](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/need-i2c-group-permissions)).
3. Call `i2c_open` / helpers (or `Bus::*`) — do not invent framework providers inside this package.[^agents]
4. Application / `gpio-framework` composes this peer with uart / gpio / spi as needed.

## Caveats

- SMBus convenience helpers are **not** the kernel `I2C_SMBUS` ioctl path — see [SMBus helpers ≠ I2C_SMBUS ioctl](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/smbus-helpers-i2c-smbus-ioctl).
- `I2CBus::$addr` is snapshot-at-open — see [`I2CBus::$addr` stale after set_slave](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/i2cbusaddr-stale-after-set-slave).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/package-010)
* [Helpers → Bus → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/i2c/architecture/helpers-bus-posix)

[^readme]: Bindings role and ext-posi requirement
[^agents]: Bindings-only role; no Chassis
[^bus]: Bus uses posix_open / ioctl / posi_mem_*
