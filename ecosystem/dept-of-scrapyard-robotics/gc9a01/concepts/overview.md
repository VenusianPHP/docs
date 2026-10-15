# Overview

GC9A01 240×240 round TFT driver for scrapyard-io/framework 0.10 — identity, requires, class shape, errors.

## Identity

| Field | Value |
|---|---|
| Composer | `dept-of-scrapyard-robotics/gc9a01` **0.10.0**, alias `dev-main` → `0.10.x-dev` |
| PHP | `^8.4\|^8.5\|^8.6` |
| Namespace | `DeptOfScrapyardRobotics\Displays\GC9A01\` → `src/` |
| Provider | `Providers\GC9A01ServiceProvider` (`extra.venusian.providers`) |
| Catalog slug | `gc9a01` |

## Requires

Split components only.[^composer]

| Package | Why |
|---|---|
| `gpio/contracts` | SPI + digital-out transport, `DisplayPanel` + children, `DataCommander`; exception root |
| `gpio/integrated-circuits` | `Bootable`, `DataRegister` |
| `venusian-surface/contracts` | `FormatSpec` + framebuffer enums |
| `venusian-voyager/nuts-and-bolts` | `ServiceProvider` |
| `venusian-voyager/vessel` | `ControlPanel` — `spi()` resolves `gpio.spi` / `gpio.digital` |

Suggests: `gpio/spi`, `gpio/digital`, `microscrap/scrapyard-usb` (driver `usb`, ext-ftdi), `microscrap/scrapyard-linux` (driver `native`, ext-posi).

## Shape

| Piece | Where |
|---|---|
| panel | `GC9A01` — `Bootable` + `DisplayPanel` + `PipeablePanel` + `Switchable`; uses `ConjuresOverSPI`, `GC9A01Bootstrap`, `GC9A01Fills`, `GC9A01Pipes`[^panel] |
| settings | `GC9A01Configuration` — `get()` / `set()`, unknown key → `invalidProperty` |
| setters | `Concerns\GC9A01API` — write chip, then configuration for keys boot writes |
| lifecycle | `Concerns\GC9A01Bootstrap` — `__get` (any config key), `__set` (keys with setters), `_boot()` |
| registers | `Breakouts\*`, `Enums\GC9A01OpCode`, `GC9A01VendorRegister`, `GC9A01ColorMode` |
| transport | `Transports\GC9A01SPITransport` over `GC9A01DataTransport` |

Fixed 240 × 240: `width()` / `height()` constant. RAM = glass, no offsets, MADCTL never changes size.

Build: `conjure('gc9a01')` / `GC9A01::spi(...)` → booted panel. By hand: `new GC9A01(GC9A01DataTransport $transport, GC9A01Configuration $props, bool $boot_now = false)`. `close()` → transport releases DC + RST; bus slave stays with its driver.

`formatSpec()` / `generateFormatSpec()` / `setFormatSpec()` plain methods: Surface 0.10 has no `FormatSpecification` interface.

Every SPI write checked: short or failed → `spiWriteFailed`.[^transport] SPI has no acknowledge: absent panel boots without error.

Colour mode: 12 / 16 / 18-bit, switchable any time; FormatSpec + `fill()` follow.[^fill]

## Errors

`GC9A01Exception` → `CircuitException` → `GPIOLevelException`.[^exception]

| Factory | When |
|---|---|
| `notConnected` | protocol driver handed back no bus or pin |
| `invalidSpiMode` | `mode` not 0–3 |
| `invalidSpiClock` | `speed` < 1 |
| `wrongSpiMode` | bus already open in another mode than configured |
| `incompletePin` | `dc` / `rst` missing `driver`, `device` or `pin` |
| `spiWriteFailed` | bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` < 1 |
| `invalidRegisterValue` | breakout field or fill channel out of range; byte naming no defined enum value |
| `invalidColorMode` | `setPixelFormat()` int not 12 / 16 / 18 |
| `invalidProperty` | unknown key, or write to key without setter |

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/connecting) · [registers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/registers) · [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/drawing-frames) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/runbooks/hardware-smoke)

[^composer]: Package manifest
[^panel]: GC9A01
[^transport]: GC9A01DataTransport
[^exception]: GC9A01Exception
[^fill]: GC9A01Fills
