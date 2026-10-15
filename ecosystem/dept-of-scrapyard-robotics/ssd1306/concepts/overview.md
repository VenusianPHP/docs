# Overview

SSD1306 OLED panel driver for scrapyard-io/framework 0.10 — identity, requires, classes, boot sequence, errors.

## Identity

| Field | Value |
|---|---|
| Composer | `dept-of-scrapyard-robotics/ssd1306` **0.10.0**, alias `dev-main` → `0.10.x-dev` |
| PHP | `^8.4\|^8.5\|^8.6` |
| Namespace | `DeptOfScrapyardRobotics\Displays\SSD1306\` → `src/` |
| Provider | `Providers\SSD1306ServiceProvider` (`extra.venusian.providers`) |
| Catalog slug | `ssd1306` (`Enums\SSD1306CatalogIc`) |

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
| `SSD1306` | panel; `Bootable` + `DisplayPanel` + `WindowAddressable` + `Switchable`; `formatSpec()` fixed for every addressing mode; `i2c()` / `spi()` factories[^panel] |
| `SSD1306Configuration` | geometry + every setting; the panel's state |
| `Transports\SSD1306I2CTransport` | wraps `I2CTransport`; control bytes 0x00 / 0x40 |
| `Transports\SSD1306SPITransport` | wraps `SPITransport` + DC + RST `DigitalOutTransport` |
| `Breakouts\{DataClock, ChargePump, COMPinsHWConfig, SegmentRemap, COMScanDirection}` | readonly register breakouts |
| `Enums\{OpCode, AddressingMode, VoltageCommonHigh, Precharge, StartLineCommand, I2CAddress, SPIClock, CatalogIc}` | typed register values |

## Construct + boot

`conjure('ssd1306')`, `SSD1306::i2c(...)`, `SSD1306::spi(...)` → booted panel. By hand: `new SSD1306(SSD1306DataTransport $transport, SSD1306Configuration $props, bool $boot_now = false)`.[^panel]

`boot()` once:[^bootstrap] packet size → transport; reset (SPI RST pulse, I2C no-op); `AE`; `D5 80`; `A8 height-1`; `D3 offset`; `40+start_line`; `8D 14`; `20 mode`; `A0|A1`; `C0|C8`; `DA com_pins`; `81 contrast`; `D9 F1|22`; `DB vcomh`; `A4`; `A6|A7`; `2E`; `AF`.[^tests]

Every bus write checked: short or failed write (NACK, bus error) → `writeFailed`. Missing or unpowered I2C panel fails on `AE`.[^transport] SPI has no acknowledge: absent SPI panel boots without error.

`close()` → SPI releases DC + RST; bus slave stays with its driver.

## Errors

`SSD1306Exception` → `CircuitException` → `GPIOLevelException`.[^exception]

| Factory | When |
|---|---|
| `notConnected` | protocol driver handed back no bus or pin |
| `spiClockOutOfRange` | `speed` outside 1 Hz – 10 MHz, before the bus is touched |
| `wrongSpiMode` | bus already open in mode 1 or 2 |
| `incompletePin` | `dc` / `rst` config missing `driver`, `device` or `pin` |
| `writeFailed` | bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` < 1, or > 8191 on I2C |
| `invalidMux` | multiplex outside 16–63 (height outside 17–64) |
| `invalidOffset` / `invalidStartLine` | outside 0–63 |
| `invalidContrast` | outside 0–255 |
| `invalidAddressingMode` | `SSD1306AddressingMode::INVALID` |
| `invalidProperty` | unknown magic property, configuration key, or `panel` key |

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/connecting-an-ssd1306) · [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/drawing-frames) · [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/panel-settings) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/runbooks/hardware-smoke)

[^composer]: Package manifest
[^panel]: SSD1306
[^bootstrap]: SSD1306Bootstrap
[^transport]: SSD1306DataTransport
[^exception]: SSD1306Exception
[^tests]: panel tests
