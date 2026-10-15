# Overview

![Latest Version on Packagist](https://packagist.org/packages/dept-of-scrapyard-robotics/ssd1306) ![License](LICENSE)

[![Latest Version on Packagist](https://img.shields.io/packagist/v/dept-of-scrapyard-robotics/ssd1306.svg)](https://packagist.org/packages/dept-of-scrapyard-robotics/ssd1306)
[![License](https://img.shields.io/packagist/l/dept-of-scrapyard-robotics/ssd1306.svg)](https://github.com/DeptOfScrapyardRobotics/SSD1306/tree/HEAD/LICENSE)

Drive SSD1306 monochrome OLED displays from PHP over I2C or SPI, using the ScrapyardIO GPIO framework.

`dept-of-scrapyard-robotics/ssd1306` boots the panel with the datasheet init sequence and writes frames into its display RAM, whole or a window at a time. Describe the wiring in a config file, ask the circuit catalog for the panel, and send it bytes packed the way its `formatSpec()` describes, which is what a Surface framebuffer produces. Contrast, inversion, addressing mode, scan direction and the other chip settings are typed properties.

```
ext-posi / ext-ftdi            1:1 system and libftdi calls
  → microscrap/*               libgpiod, i2c-dev, spidev, termios, libmpsse in PHP
    → microscrap/scrapyard-*   adapters: the `native` and `usb` drivers
      → scrapyard-io/framework protocol managers, transports, the circuit catalog
        → dept-of-scrapyard-robotics/ssd1306   ← this package
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
composer require dept-of-scrapyard-robotics/ssd1306
```

The service provider is discovered automatically. It merges the package's wiring config under `circuits.ssd1306` and registers the panel with the circuit catalog. To publish the config into your app, run:

```bash
php computer vendor:publish --tag=ssd1306-config
```

That writes `config/circuits/ssd1306.php`, with `driver => 'none'` until you fill in your bench.

## Quick start

A 128×64 panel on a Raspberry Pi's I2C bus 1 at `0x3C`:

```php
// config/circuits/ssd1306.php
return [
    'default_config' => 'i2c',
    'configs' => [
        'i2c' => [
            'driver' => 'native',
            'device' => 1,
            'slave' => 0x3C,
            'panel' => ['width' => 128, 'height' => 64],
        ],
    ],
];
```

```php
use Surface\Framebuffers\Native\NativeFramebufferDriver;

$panel = app('circuit')->conjure('ssd1306');   // connected, reset and booted

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
$fb->setSegment(2, 2, 8, 8, 1);                 // a solid square in the corner

$panel->transmit(0, 0, $fb->flush($spec, true));
```

On a Raspberry Pi 5 that boots in about 8 ms and sends a full frame in about 29 ms.

## Connecting

`conjure('ssd1306')` reads `circuits.ssd1306`, picks `default_config` (or the config you name, `conjure('ssd1306', 'spi')`), and calls the panel's `i2c()` or `spi()` factory with that entry's keys. You can call the factories directly too. Either way you get a booted panel unless you pass `boot_now: false`.

A bus or pin device that isn't connected yet is connected by the factory. One your app already connected is shared as it is, so the panel can sit on a bus with other chips.

### I2C

```php
use DeptOfScrapyardRobotics\Displays\SSD1306\SSD1306;

$panel = SSD1306::i2c('native', 1, slave: 0x3C, panel: ['height' => 32]);
```

The address is `0x3C` with the SA0 pin grounded and `0x3D` with it pulled high (`SSD1306I2CAddress`).

### SPI

A panel on an FT232H's SPI, chip select on GPIO0 (D4), DC on GPIO1 (D5), RST on GPIO2 (D6):

```php
// config/circuits/ssd1306.php
return [
    'default_config' => 'spi',
    'configs' => [
        'spi' => [
            'driver' => 'usb',
            'device' => 'ft232h',
            'chip_select' => 0,
            'speed' => 10_000_000,
            'dc' => ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
            'rst' => ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
            'panel' => ['width' => 128, 'height' => 64],
        ],
    ],
];
```

```php
$panel = SSD1306::spi(
    'usb', 'ft232h',
    dc: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
    rst: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
    chip_select: 0,
);
```

The chip clocks data in on the rising edge of SCLK at up to 10 MHz. `spi()` opens an unconnected bus in mode 0 and sets this chip select's clock to `speed` whatever the bus runs at. It refuses a speed above 10 MHz before touching the bus, and refuses a bus your app already opened in mode 1 or 2. Mode 3 also samples on the rising edge, so a mode 3 bus is shared. DC and RST are opened after the bus, so on an FT232H they ride the same USB context as its SPI engine. The FT232H's `chip_select` numbers are its GPIO pins: 0–3 are D4–D7, 4–11 are C0–C7.

On the FT232H at 10 MHz the panel boots in about 95 ms, most of it the RST pulse, and sends a full frame in 6–9 ms.

### Building the transport yourself

```php
use DeptOfScrapyardRobotics\Displays\SSD1306\SSD1306;
use DeptOfScrapyardRobotics\Displays\SSD1306\SSD1306Configuration;
use DeptOfScrapyardRobotics\Displays\SSD1306\Transports\SSD1306I2CTransport;

$slave = app('gpio.i2c')->driver('native')->connectTo(1)->register()->device(1, 0x3C);

$panel = new SSD1306(new SSD1306I2CTransport($slave), new SSD1306Configuration(height: 32), boot_now: true);
```

`SSD1306SPITransport` takes the SPI slave, the DC output and the RST output.

## Drawing

`formatSpec()` returns `MONO_VERTICAL_PAGE`, one bit per pixel, least significant bit first, pages running vertically. Each byte is one column of one 8-row page, bit 0 at the top. The bytes run page by page and, within a page, column by column, so a 128×64 frame is 1024 bytes. The spec is the same in every addressing mode.

`transmit($x, $y, $bytes, $width, $height)` writes those bytes into the rectangle at `($x, $y)`. Leave `$width` and `$height` off for the whole panel. The panel is window-addressable, so a region write leaves the rest of the screen alone:

```php
use Surface\Contracts\Framebuffers\Region;

$fb->setSegment(48, 24, 32, 16, 1);
$region = new Region(48, 24, 32, 16);

$panel->transmit($region->x, $region->y, $fb->flushRegion($region, $spec, true), $region->width, $region->height);
```

`y` and `height` cover whole 8-row pages. A 32×16 region takes about 2.5 ms on the Pi's I2C bus.

Frames go out in packets of `max_packet_size` bytes (1024 by default). On I2C a packet can be up to 8191 bytes, the bus's 8192-byte message less the control byte. SPI adapters split long writes themselves, so SPI has no upper bound.

### Addressing modes

The panel takes the same bytes in horizontal, vertical and page addressing. In vertical mode it reorders them column by column before sending. In page mode it positions and sends each page on its own, because the chip ignores the column/page window in that mode.

```php
use DeptOfScrapyardRobotics\Displays\SSD1306\Enums\SSD1306AddressingMode;

$panel->addressing_mode = SSD1306AddressingMode::PAGE_ADDRESSING_MODE;
$panel->transmit(0, 0, $fb->flush($spec, true));   // same picture
```

## Settings

Every setting is a property under its configuration key name. Reading it returns the value the driver last wrote, and assigning it writes the chip and then the configuration:

```php
$panel->contrast = 0x01;          // dim
$panel->contrast = 0xFF;          // bright
$panel->invert_display = true;
$panel->display_on = false;       // display RAM keeps its contents
$panel->display_on = true;
```

| Property | Values | Command |
|---|---|---|
| `display_on` | bool | AF / AE |
| `display_offset` | 0–63 | D3 |
| `contrast` | 0–255 | 81 |
| `start_line` | 0–63 | 40–7F |
| `charge_pump` | bool | 8D 14 / 8D 10 |
| `addressing_mode` | `SSD1306AddressingMode` | 20 |
| `map_line_0_to_line_127` | bool, segment remap | A1 / A0 |
| `reverse_line_scan_direction` | bool, COM scan direction | C8 / C0 |
| `com_pins_config` | `SSD1306COMPinsHWConfig` | DA |
| `powered_by_host_device` | bool, pre-charge period | D9 F1 / D9 22 |
| `v_com_h` | `SSD1306VoltageCommonHigh` | DB |
| `fill_overlay_on` | bool, light every pixel | A5 / A4 |
| `invert_display` | bool | A7 / A6 |

Out-of-range values throw before anything is written. `setDisplay(bool)`, `setContrast()` and the other setter methods behind these properties are public too.

## Panel configuration

A config entry's `panel` array, or `new SSD1306Configuration(...)`, sets the geometry and the values the boot sequence writes:

| Key | Default |
|---|---|
| `width` / `height` | 128 / 64 |
| `contrast` | 191 |
| `start_line` / `display_offset` | 0 / 0 |
| `max_packet_size` | 1024 |
| `invert_display` | false |
| `enable_com_lr_remap` | false |
| `alternative_com_pins` | picked by height |
| `map_line_0_to_line_127` / `reverse_line_scan_direction` | false / false |
| `powered_by_host_device` | true |
| `v_com_h` | `LEVEL_077_ALT` |
| `addressing_mode` | `HORIZONTAL_ADDRESSING_MODE` |

`alternative_com_pins` is bit 4 of the COM pins command. Panels taller than 32 rows (128×64) wire their COM pins in the alternative layout and shorter ones (128×32, 96×16) in the sequential layout, so the default follows `height`. Set it yourself for a panel that differs. With the wrong layout every other row is blank or doubled. An unknown `panel` key throws, naming the key.

## Errors

Everything throws `SSD1306Exception`, which descends from `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitException`.

Every write to the panel is checked. A write the bus refuses or cuts short throws `writeFailed`. An I2C panel that is missing, unpowered or at another address doesn't acknowledge, so `conjure()` throws on the first boot command instead of returning a panel that shows nothing. SPI has no acknowledge, so a missing SPI panel can't be detected from the bus.

| Factory | When |
|---|---|
| `notConnected` | the protocol driver handed back no bus or pin |
| `spiClockOutOfRange` | `speed` outside 1 Hz – 10 MHz |
| `wrongSpiMode` | the SPI bus is already open in mode 1 or 2 |
| `incompletePin` | a `dc` or `rst` config is missing `driver`, `device` or `pin` |
| `writeFailed` | the bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` below 1, or above 8191 on I2C |
| `invalidMux` | `height` outside 17–64 |
| `invalidOffset`, `invalidStartLine` | outside 0–63 |
| `invalidContrast` | outside 0–255 |
| `invalidAddressingMode` | `SSD1306AddressingMode::INVALID` |
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
| `configs.spi.speed` | `10_000_000` | this chip select's clock in Hz, up to 10 MHz |
| `configs.spi.dc` / `rst` | pins 0 / 1 | `driver`, `device`, `pin` for each line |
| `configs.*.panel` | 128 × 64 | `SSD1306Configuration` arguments by name |
| `configs.*.boot_now` | `true` | boot during `conjure()` |

## Upgrading from 0.8

| 0.8 | 0.10 |
|---|---|
| `scrapyard-io/framework` 0.8 components, `surface/contracts` | the 0.10 components, `venusian-surface/contracts` |
| `I2C::driver(...)`, `SPI::driver(...)`, `DigitalIO::driver(...)` | `app('circuit')->conjure()`, the `i2c()` / `spi()` factories, or `app('gpio.i2c')->driver(...)` |
| the package merged config but never read it | `conjure()` builds the panel from it |
| `SSD1306` implemented Surface's `FormatSpecification` | Surface 0.10 has no such interface; `formatSpec()` is unchanged |
| failed writes returned `-1` and boot carried on | failed writes throw `writeFailed` |
| `sequential_com_pin_config: true` (which set the alternative layout) | `alternative_com_pins`, picked by height when left out |
| `$panel->offset` | `$panel->display_offset` |
| `toggle_fill_overlay` (write) / `fill_overlay_on` (read) | `fill_overlay_on` |
| `charge_pump_regulator` / `charge_pump` | `charge_pump` |
| `segment_remap` / `flip_line_0_and_127` | `map_line_0_to_line_127` |
| `reverse_com_scan_dir` / `flip_line_scan_dir` | `reverse_line_scan_direction` |
| `com_pins_hw_config` / `com_pins_config` | `com_pins_config` |
| `start_line` read-only, `invert_display` write-only | both read and write |

## Testing

```bash
composer install
vendor/bin/pest
```

The suite runs against recording fake buses and pins, so it needs no hardware. The panel was also checked on hardware for this release, with someone watching it: an SSD1306 on a Raspberry Pi 5's I2C bus and one on an FT232H's SPI. Both showed the same picture in all three addressing modes, a region write, contrast, inversion and display off and on.

## Security

The driver writes commands and display data to hardware the PHP process can open. See [SECURITY.md](https://github.com/DeptOfScrapyardRobotics/SSD1306/blob/HEAD/SECURITY.md) for the support policy and how to report a vulnerability.

## License

MIT. See [LICENSE](https://github.com/DeptOfScrapyardRobotics/SSD1306/tree/HEAD/LICENSE).
