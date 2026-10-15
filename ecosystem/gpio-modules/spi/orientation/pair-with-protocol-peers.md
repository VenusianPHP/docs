# Pair with protocol peers

ext-posi below; uart / i2c / gpio peers; ftdi/mpsse alternate SPI path; scrapyard-io/framework above.

## Composition boundary

`microscrap/spi` is **bindings only** — Linux `spidev` helpers, enums, and data objects. It does not register Chassis providers or implement higher GPIO orchestration.[^readme][^agents]

| Concern | Package |
|---------|---------|
| POSIX FD / ioctl / memory primitives | `ext-posi` `^0.10.0` (**below** — required; registers `posix_*`, `ioctl`, `posi_mem_*`) |
| SPI / spidev (this package) | `microscrap/spi` |
| UART | `microscrap/uart` `^0.10` (peer) |
| I2C | `microscrap/i2c` `^0.10` (peer) |
| GPIO | `microscrap/gpio` `^0.10` (peer) |
| USB MPSSE / FTDI SPI path | `microscrap/ftdi` / `microscrap/mpsse` (**beside** — alternate SPI transport, not a spidev child) |
| Higher GPIO orchestration | `scrapyard-io/framework` `^0.10.0` (**above**)[^composer] |

## Typical flow

1. Depend on this package (pulls **ext-posi** `^0.10.0`).
2. Open `/dev/spidev*` via `spi_open` and transfer with `spi_transfer` / half-duplex helpers.
3. Application / `scrapyard-io/framework` composes peers — do not invent framework providers inside this package.[^agents]

## Caveats

- Full-duplex needs `spi_transfer` — see [Half-duplex vs full-duplex](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/half-duplex-vs-full-duplex).
- Transfer path is native `spi_transfer(int $fd, …)` when loaded, otherwise `posi_mem_*` — see [Native `spi_transfer` vs `posi_mem`](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/native-spi-transfer-vs-posi-mem).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/package-010)
* [Helpers → Device → posix](/docs/{{version}}/ecosystem/gpio-modules/spi/architecture/helpers-device-posix)

[^readme]: Bindings role; ext-posi dependency
[^agents]: Bindings-only role; no Chassis
[^composer]: require ext-posi; suggest scrapyard-io/framework
