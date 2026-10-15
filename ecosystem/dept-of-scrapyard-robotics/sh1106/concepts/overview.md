# Overview

SH1106 OLED panel driver for scrapyard-io/framework 0.10 — identity, requires, classes, boot sequence, errors.

## Identity

| Field | Value |
|---|---|
| Composer | `dept-of-scrapyard-robotics/sh1106` **0.10.0**, alias `dev-main` → `0.10.x-dev` |
| PHP | `^8.4\|^8.5\|^8.6` |
| Namespace | `DeptOfScrapyardRobotics\Displays\SH1106\` → `src/` |
| Provider | `Providers\SH1106ServiceProvider` (`extra.venusian.providers`) |
| Catalog slug | `sh1106` (`Enums\SH1106CatalogIc`) |

## Requires

Split components only.[^composer]

| Package | Why |
|---|---|
| `gpio/contracts` | transport, `DisplayPanel` + children, `DataCommander`; exception root |
| `gpio/integrated-circuits` | `Bootable`, `DataRegister` |
| `gpio/nuts-and-bolts` | `byte2bits()` in breakouts |
| `venusian-surface/contracts` | `FormatSpec` + framebuffer enums |
| `venusian-voyager/nuts-and-bolts` | `ServiceProvider` |
| `venusian-voyager/vessel` | `ControlPanel` — factories resolve `gpio.i2c` / `gpio.spi` / `gpio.digital` |

Suggests: `gpio/i2c`, `gpio/spi`, `gpio/digital`, `microscrap/scrapyard-linux` (driver `native`, ext-posi), `microscrap/scrapyard-usb` (driver `usb`, ext-ftdi).

## Classes

| Class | Role |
|---|---|
| `SH1106` | panel; `Bootable` + `DisplayPanel` + `WindowAddressable` + `Switchable`; `formatSpec()` fixed; page-only `transmit()`; `i2c()` / `spi()` factories[^panel] |
| `SH1106Configuration` | geometry + every setting; the panel's state |
| `Transports\SH1106I2CTransport` | wraps `I2CTransport`; control bytes 0x00 / 0x40 |
| `Transports\SH1106SPITransport` | wraps `SPITransport` + DC + RST `DigitalOutTransport` |
| `Breakouts\{DataClock, ChargePump, COMPinsHWConfig, SegmentRemap, COMScanDirection}` | readonly register breakouts |
| `Enums\{OpCode, PumpVoltage, VoltageCommonHigh, Precharge, StartLineCommand, I2CAddress, SPIClock, CatalogIc}` | typed register values |

## Construct + boot

`conjure('sh1106')`, `SH1106::i2c(...)`, `SH1106::spi(...)` → booted panel. By hand: `new SH1106(SH1106DataTransport $transport, SH1106Configuration $props, bool $boot_now = false)`.[^panel]

`boot()` once:[^bootstrap] packet size → transport; reset (SPI RST pulse, I2C no-op); `AE`; `D5 80`; `A8 height-1`; `D3 offset`; `40+start_line`; `AD 8B` (DC-DC on); `A0|A1`; `C0|C8`; `DA com_pins`; `81 contrast`; `D9 F1|22`; `DB vcomh`; `30–33` pump voltage; `A4`; `A6|A7`; 100 ms DC-DC settle; `AF`. Same as the 0.4 driver less its `20 10`, an SSD1306 memory-mode command the SH1106 does not have.[^tests]

Every bus write checked: short or failed write (NACK, bus error) → `writeFailed`. Missing or unpowered I2C panel fails on `AE`.[^transport] SPI has no acknowledge: absent SPI panel boots without error.

`close()` → SPI releases DC + RST; bus slave stays with its driver.

## Errors

`SH1106Exception` → `CircuitException` → `GPIOLevelException`.[^exception]

| Factory | When |
|---|---|
| `notConnected` | protocol driver handed back no bus or pin |
| `spiClockOutOfRange` | `speed` outside 1 Hz – 4 MHz, before the bus is touched |
| `wrongSpiMode` | bus already open in mode 1 or 2 |
| `incompletePin` | `dc` / `rst` config missing `driver`, `device` or `pin` |
| `writeFailed` | bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` < 1, or > 8191 on I2C |
| `invalidGeometry` | `height` not whole pages in 16–64, or `width` < 1; at configuration build |
| `invalidColumnOffset` | `column_offset` < 0, or `column_offset + width` > 132 |
| `invalidMux` | multiplex outside 16–63 |
| `invalidOffset` / `invalidStartLine` | outside 0–63 |
| `invalidContrast` | outside 0–255 |
| `invalidProperty` | unknown magic property, configuration key, or `panel` key |

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/connecting-an-sh1106) · [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/drawing-frames) · [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/panel-settings) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/runbooks/hardware-smoke)

[^composer]: Package manifest
[^panel]: SH1106
[^bootstrap]: SH1106Bootstrap
[^transport]: SH1106DataTransport
[^exception]: SH1106Exception
[^tests]: panel tests
