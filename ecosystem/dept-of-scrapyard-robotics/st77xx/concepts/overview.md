# Overview

ST7735, ST7789 and ST7796 TFT drivers for scrapyard-io/framework 0.10 — identity, requires, shared class shape, errors.

## Identity

| Field | Value |
|---|---|
| Composer | `dept-of-scrapyard-robotics/st77xx` **0.10.0**, alias `dev-main` → `0.10.x-dev` |
| PHP | `^8.4\|^8.5\|^8.6` |
| Namespace | `DeptOfScrapyardRobotics\Displays\ST77xx\` → `src/` |
| Provider | `Providers\ST77xxServiceProvider` (`extra.venusian.providers`) |
| Catalog slugs | `st7735`, `st7789`, `st7796` |

## Requires

Split components only.[^composer]

| Package | Why |
|---|---|
| `gpio/contracts` | SPI + digital-out transport, `DisplayPanel` + children, `DataCommander`; exception root |
| `gpio/integrated-circuits` | `Bootable`, `DataRegister` |
| `gpio/nuts-and-bolts` | `byte2bits()` in breakouts |
| `venusian-surface/contracts` | `FormatSpec` + framebuffer enums |
| `venusian-voyager/nuts-and-bolts` | `ServiceProvider` |
| `venusian-voyager/vessel` | `ControlPanel` — `spi()` resolves `gpio.spi` / `gpio.digital` |

Suggests: `gpio/spi`, `gpio/digital`, `microscrap/scrapyard-usb` (driver `usb`, ext-ftdi), `microscrap/scrapyard-linux` (driver `native`, ext-posi).

## Shape (same for each chip)

| Piece | ST7735 / ST7789 / ST7796 |
|---|---|
| panel | `ST77xx\{Chip}\{Chip}` — `Bootable` + `DisplayPanel` + `WindowAddressable` + `Switchable`; uses `ConjuresOverSPI`, `ST77xxOrientation`, `ST77xxFills`[^st7789] |
| settings | `{Chip}Configuration` — `get()` / `set()`, unknown key → `invalidProperty` |
| setters | `Concerns\{Chip}API` — write chip, then configuration |
| lifecycle | `Concerns\{Chip}Bootstrap` — `__get` (any config key), `__set` (keys with setters), `_boot()` |
| registers | `Breakouts\*`, `Enums\*` (incl. `{Chip}OpCode`, `{Chip}ColorMode`) |

Shared: `Transports\ST77xxSPITransport`, `ST77xxFills`, `ST77xxException`, `Providers\ST77xxServiceProvider`.

Build: `conjure('{chip}')` / `{Chip}::spi(...)` → booted panel. By hand: `new {Chip}(ST77xxDataTransport $transport, {Chip}Configuration $props, bool $boot_now = false)`. `close()` → transport releases DC + RST; bus slave stays with its driver.

`formatSpec()` / `generateFormatSpec()` / `setFormatSpec()` are plain methods: Surface 0.10 has no `FormatSpecification` interface.

Every SPI write checked: short or failed → `spiWriteFailed`.[^transport] SPI has no acknowledge: absent panel boots without error.

Colour mode: 12 / 16 / 18-bit, switchable any time; FormatSpec + `fill()` follow.[^fill]

## Errors

`ST77xxException` → `CircuitException` → `GPIOLevelException`.[^exception]

| Factory | When |
|---|---|
| `notConnected` | protocol driver handed back no bus or pin |
| `invalidSpiMode` | `mode` not 0–3 |
| `invalidSpiClock` | `speed` < 1 |
| `wrongSpiMode` | bus already open in another mode than configured |
| `incompletePin` | `dc` / `rst` missing `driver`, `device` or `pin` |
| `spiWriteFailed` | bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` < 1 |
| `invalidRegisterValue` | breakout field (gamma bytes included; ST7735 gamma 0–63) or fill channel out of range |
| `invalidColorMode` | `setPixelFormat()` int not 12 / 16 / 18 |
| `invalidProperty` | unknown key, or write to key without setter |

## Related

* [controllers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/controllers-boot-and-configuration) · [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/connecting-an-st77xx-panel) · [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames) · [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/runbooks/hardware-smoke)

[^composer]: Package manifest
[^st7789]: ST7789
[^transport]: ST77xxDataTransport
[^exception]: ST77xxException
[^fill]: ST77xxFills
