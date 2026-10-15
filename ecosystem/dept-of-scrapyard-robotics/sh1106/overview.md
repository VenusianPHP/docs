# Overview

![Latest Version on Packagist](https://packagist.org/packages/dept-of-scrapyard-robotics/sh1106) ![License](LICENSE)

[![Latest Version on Packagist](https://img.shields.io/packagist/v/dept-of-scrapyard-robotics/sh1106.svg)](https://packagist.org/packages/dept-of-scrapyard-robotics/sh1106)
[![License](https://img.shields.io/packagist/l/dept-of-scrapyard-robotics/sh1106.svg)](https://github.com/DeptOfScrapyardRobotics/SH1106/tree/HEAD/LICENSE)

Drive SH1106 monochrome OLED displays (the common 1.3" 128×64 modules) from PHP over I2C or SPI, using the ScrapyardIO GPIO framework.

`dept-of-scrapyard-robotics/sh1106` boots the panel with the datasheet init sequence and writes frames into its display RAM, whole or a region at a time. Describe the wiring in a config file, ask the circuit catalog for the panel, and send it bytes packed the way its `formatSpec()` describes, which is what a Surface framebuffer produces. Contrast, inversion, pump voltage, scan direction and the other chip settings are typed properties.

```
ext-posi / ext-ftdi            1:1 system and libftdi calls
  → microscrap/*               libgpiod, i2c-dev, spidev, termios, libmpsse in PHP
    → microscrap/scrapyard-*   adapters: the `native` and `usb` drivers
      → scrapyard-io/framework protocol managers, transports, the circuit catalog
        → dept-of-scrapyard-robotics/sh1106   ← this package
```

## Requirements

- PHP 8.4 or newer
- A Venusian 0.10 application with the `scrapyard-io/framework` 0.10 components (`gpio/i2c`, `gpio/spi`, `gpio/digital`, `gpio/integrated-circuits`)
- `venusian-surface/contracts` 0.10, for the `FormatSpec` the panel describes its bytes with
- An adapter for your hardware:
  - `microscrap/scrapyard-linux` (driver `native`) for a Raspberry Pi or other Linux board: `i2c-dev`, `spidev` and `libgpiod`, needs `ext-posi`
  - `microscrap/scrapyard-usb` (driver `usb`) for FTDI MPSSE boards such as the FT232H, needs `ext-ftdi`
- `venusian-surface/framebuffers` 0.10 if you want Surface to pack your frames

## Installation

```bash
composer require dept-of-scrapyard-robotics/sh1106
```

The service provider is discovered automatically. It merges the package's wiring config under `circuits.sh1106` and registers the panel with the circuit catalog. To publish the config into your app, run:

```bash
php computer vendor:publish --tag=sh1106-config
```

That writes `config/circuits/sh1106.php`, with `driver => 'none'` until you fill in your bench.

## Quick start

A 128×64 panel on an FT232H's I2C at `0x3C`:

```php
// config/circuits/sh1106.php
return [
    'default_config' => 'i2c',
    'configs' => [
        'i2c' => [
            'driver' => 'usb',
            'device' => 'ft232h',
            'slave' => 0x3C,
            'panel' => ['width' => 128, 'height' => 64],
        ],
    ],
];
```

```php
use Surface\Framebuffers\Native\NativeFramebufferDriver;

$panel = app('circuit')->conjure('sh1106');   // connected and booted

$spec = $panel->formatSpec();
$fb = (new NativeFramebufferDriver)->full($spec, $panel->width(), $panel->height());

for ($x = 0; $x < $panel->width(); $x++) {      // a border
    $fb->setPixel($x, 0, 1);
    $fb->setPixel($x, $panel->height() - 1, 1);
}
for ($y = 0; $y < $panel->height(); $y++) {
    $fb->setPixel(0, $y, 1);
    $fb->setPixel($panel->width() - 1, $y, 1);
}
$fb->setSegment(4, 4, 16, 16, 1);               // a solid square in the corner

$panel->transmit(0, 0, $fb->flush($spec, true));
```

On the FT232H's I2C that boots in about 170 ms, 100 ms of it the DC-DC converter settling, and sends a full frame in about 190 ms. On a Raspberry Pi use driver `native` with `device` set to the bus number.

## Connecting

`conjure('sh1106')` reads `circuits.sh1106`, picks `default_config` (or the config you name, `conjure('sh1106', 'spi')`), and calls the panel's `i2c()` or `spi()` factory with that entry's keys. You can call the factories directly too. Either way you get a booted panel unless you pass `boot_now: false`.

A bus or pin device that isn't connected yet is connected by the factory. One your app already connected is shared as it is, so the panel can sit on a bus with other chips.

### I2C

```php
use DeptOfScrapyardRobotics\Displays\SH1106\SH1106;

$panel = SH1106::i2c('usb', 'ft232h', slave: 0x3C);
```

The address is `0x3C` with the SA0 pin grounded and `0x3D` with it pulled high (`SH1106I2CAddress`). Each command goes out behind a `0x00` control byte and each data packet behind `0x40`.

### SPI

For a module wired for 4-wire SPI, with chip select on the FT232H's GPIO0 (D4), DC on GPIO1 (D5) and RST on GPIO2 (D6):

```php
// config/circuits/sh1106.php
return [
    'default_config' => 'spi',
    'configs' => [
        'spi' => [
            'driver' => 'usb',
            'device' => 'ft232h',
            'chip_select' => 0,
            'speed' => 4_000_000,
            'dc' => ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
            'rst' => ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
            'panel' => ['width' => 128, 'height' => 64],
        ],
    ],
];
```

```php
$panel = SH1106::spi(
    'usb', 'ft232h',
    dc: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
    rst: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
    chip_select: 0,
);
```

The chip clocks data in on the rising edge of SCLK, with a 250 ns minimum clock cycle, so up to 4 MHz. `spi()` opens an unconnected bus in mode 0 and sets this chip select's clock to `speed` whatever the bus runs at. It refuses a speed above 4 MHz before touching the bus, and refuses a bus your app already opened in mode 1 or 2. Mode 3 also samples on the rising edge, so a mode 3 bus is shared. DC and RST are opened after the bus, so on an FT232H they ride the same USB context as its SPI engine. The FT232H's `chip_select` numbers are its GPIO pins: 0–3 are D4–D7, 4–11 are C0–C7. Boot pulses RST low before the init sequence.

### Building the transport yourself

```php
use DeptOfScrapyardRobotics\Displays\SH1106\SH1106;
use DeptOfScrapyardRobotics\Displays\SH1106\SH1106Configuration;
use DeptOfScrapyardRobotics\Displays\SH1106\Transports\SH1106I2CTransport;

$slave = app('gpio.i2c')->driver('native')->connectTo(1)->register()->device(1, 0x3C);

$panel = new SH1106(new SH1106I2CTransport($slave), new SH1106Configuration, boot_now: true);
```

`SH1106SPITransport` takes the SPI slave, the DC output and the RST output.

## Drawing

`formatSpec()` returns `MONO_VERTICAL_PAGE`, one bit per pixel, least significant bit first, pages running vertically. Each byte is one column of one 8-row page, bit 0 at the top. The bytes run page by page and, within a page, column by column, so a 128×64 frame is 1024 bytes.

`transmit($x, $y, $bytes, $width, $height)` writes those bytes into the rectangle at `($x, $y)`. Leave `$width` and `$height` off for the whole panel. The SH1106 addresses its RAM by page only, so the panel places each 8-row page of the rectangle at its column and sends it on its own. A region write leaves the rest of the screen alone:

```php
use Surface\Contracts\Framebuffers\Region;

$fb->setSegment(48, 24, 32, 16, 1);
$region = new Region(48, 24, 32, 16);

$panel->transmit($region->x, $region->y, $fb->flushRegion($region, $spec, true), $region->width, $region->height);
```

`y` and `height` cover whole 8-row pages. A 16×8 region takes about 15 ms on the FT232H's I2C.

The chip has 132 RAM columns, and a 128-pixel glass is centred on them, so its first pixel is RAM column 2. `column_offset` (default 2) shifts every write by that much. Set it to 0 for a module whose glass starts at column 0.

Frames go out in packets of `max_packet_size` bytes (1024 by default). On I2C a packet can be up to 8191 bytes, the bus's 8192-byte message less the control byte. SPI adapters split long writes themselves, so SPI has no upper bound.

## Settings

Every setting is a property under its configuration key name. Reading it returns the value the driver last wrote, and assigning it writes the chip and then the configuration:

```php
use DeptOfScrapyardRobotics\Displays\SH1106\Enums\SH1106PumpVoltage;

$panel->contrast = 0x01;          // dim
$panel->contrast = 0xFF;          // bright
$panel->invert_display = true;
$panel->vpp = SH1106PumpVoltage::PUMP_VOLTAGE_800;
$panel->display_on = false;       // display RAM keeps its contents
$panel->display_on = true;
```

| Property | Values | Command |
|---|---|---|
| `display_on` | bool | AF / AE |
| `display_offset` | 0–63 | D3 |
| `contrast` | 0–255 | 81 |
| `start_line` | 0–63 | 40–7F |
| `charge_pump` | bool, DC-DC converter | AD 8B / AD 8A |
| `vpp` | `SH1106PumpVoltage`: 6.4, 7.4, 8.0 or 9.0 V | 30–33 |
| `map_line_0_to_line_127` | bool, segment remap | A1 / A0 |
| `reverse_line_scan_direction` | bool, COM scan direction | C8 / C0 |
| `com_pins_config` | `SH1106COMPinsHWConfig` | DA |
| `powered_by_host_device` | bool, pre-charge period | D9 F1 / D9 22 |
| `v_com_h` | `SH1106VoltageCommonHigh` | DB |
| `fill_overlay_on` | bool, light every pixel | A5 / A4 |
| `invert_display` | bool | A7 / A6 |

Out-of-range values throw before anything is written. `setDisplay(bool)`, `setContrast()`, `setPumpVoltage()` and the other setter methods behind these properties are public too.

## Panel configuration

A config entry's `panel` array, or `new SH1106Configuration(...)`, sets the geometry and the values the boot sequence writes:

| Key | Default |
|---|---|
| `width` / `height` | 128 / 64 |
| `column_offset` | 2 |
| `contrast` | 191 |
| `start_line` / `display_offset` | 0 / 0 |
| `max_packet_size` | 1024 |
| `invert_display` | false |
| `enable_com_lr_remap` | false |
| `alternative_com_pins` | picked by height |
| `map_line_0_to_line_127` / `reverse_line_scan_direction` | false / false |
| `powered_by_host_device` | true |
| `v_com_h` | `LEVEL_077_ALT` |
| `vpp` | `PUMP_VOLTAGE_900` |

`height` is whole pages from 16 to 64 rows, and `column_offset + width` fits the chip's 132 columns; anything else throws when the configuration is built. `alternative_com_pins` is bit 4 of the COM pins command. Panels taller than 32 rows (128×64) wire their COM pins in the alternative layout and shorter ones in the sequential layout, so the default follows `height`. Set it yourself for a panel that differs. With the wrong layout every other row is blank or doubled. An unknown `panel` key throws, naming the key.

## Errors

Everything throws `SH1106Exception`, which descends from `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitException`.

Every write to the panel is checked. A write the bus refuses or cuts short throws `writeFailed`. An I2C panel that is missing, unpowered or at another address doesn't acknowledge, so `conjure()` throws on the first boot command instead of returning a panel that shows nothing. SPI has no acknowledge, so a missing SPI panel can't be detected from the bus.

| Factory | When |
|---|---|
| `notConnected` | the protocol driver handed back no bus or pin |
| `spiClockOutOfRange` | `speed` outside 1 Hz – 4 MHz |
| `wrongSpiMode` | the SPI bus is already open in mode 1 or 2 |
| `incompletePin` | a `dc` or `rst` config is missing `driver`, `device` or `pin` |
| `writeFailed` | the bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` below 1, or above 8191 on I2C |
| `invalidGeometry` | `height` not a multiple of 8 from 16 to 64, or `width` below 1 |
| `invalidColumnOffset` | `column_offset` negative, or the row past column 131 |
| `invalidMux` | multiplex ratio outside 16–63 |
| `invalidOffset`, `invalidStartLine` | outside 0–63 |
| `invalidContrast` | outside 0–255 |
| `invalidProperty` | an unknown property, configuration key or `panel` key |

## Closing

```php
$panel->close();
```

On SPI this releases the DC and RST pins. The bus connection belongs to its driver and stays open for other chips. The panel keeps showing its last frame; set `display_on = false` first to blank it.

## Configuration

| Key | Default | Meaning |
|---|---|---|
| `default_config` | `'i2c'` | which entry under `configs` `conjure()` uses |
| `configs.<name>.protocol` | the entry's name | `i2c` or `spi`, so an app can keep `left` and `right` panels |
| `configs.i2c.driver` | `'none'` | I2C adapter: `native` or `usb` |
| `configs.i2c.device` | `''` | bus number, or `ft232h` |
| `configs.i2c.slave` | `0x3C` | panel address |
| `configs.spi.driver` | `'none'` | SPI adapter |
| `configs.spi.device` | `''` | SPI bus |
| `configs.spi.chip_select` | `0` | chip select |
| `configs.spi.speed` | `4_000_000` | this chip select's clock in Hz, up to 4 MHz |
| `configs.spi.dc` / `rst` | pins 0 / 1 | `driver`, `device`, `pin` for each line |
| `configs.*.panel` | 128 × 64 | `SH1106Configuration` arguments by name |
| `configs.*.boot_now` | `true` | boot during `conjure()` |

## Upgrading from 0.4

| 0.4 | 0.10 |
|---|---|
| `scrapyard-io/waveforms`, `reality-interface`, `bare-metal` 0.4 | the `scrapyard-io/framework` 0.10 components, `venusian-surface/contracts` |
| `SH1106::connection($driver)->i2c($bus, $address)->create()` | `app('circuit')->conjure('sh1106')` or `SH1106::i2c($driver, $bus, slave: $address)` |
| factory setters (`width()`, `startingContrast()`, `notPoweredByHostDevice()`, ...) | the config entry's `panel` array or `SH1106Configuration` arguments |
| I2C only | I2C or 4-wire SPI |
| `EmbeddedDisplay` / `MonochromeDisplayInterface` | `Bootable` + `DisplayPanel` + `WindowAddressable` + `Switchable` |
| `sendData($x, $y, $w, $h, $payload)` | `transmit($x, $y, $bytes, $w, $h)` |
| bus write results ignored | failed writes throw `writeFailed` |
| `sequential_com_pin_config: true` (which set the alternative layout) | `alternative_com_pins`, picked by height when left out |
| `offset` | `display_offset` |
| `flip_line_0_and_127` | `map_line_0_to_line_127` |
| `flip_line_scan_dir` | `reverse_line_scan_direction` |
| `start_line` and the rest read from private fields | every setting read and written under its configuration key |
| boot wrote `20 10`, an SSD1306 memory mode command the SH1106 does not have | not sent |

The boot sequence is otherwise the same, values included.

## Testing

```bash
composer install
vendor/bin/pest
```

The suite runs against recording fake buses and pins, so it needs no hardware. The panel was also checked on hardware for this release, with someone watching it: a 128×64 SH1106 on an FT232H's I2C at `0x3C` showed a border on all four edges, a diagonal cross, a filled square and a later region write in place.

## Security

The driver writes commands and display data to hardware the PHP process can open. See [SECURITY.md](https://github.com/DeptOfScrapyardRobotics/SH1106/blob/HEAD/SECURITY.md) for the support policy and how to report a vulnerability.

## License

MIT. See [LICENSE](https://github.com/DeptOfScrapyardRobotics/SH1106/tree/HEAD/LICENSE).
