# Overview

![Latest Version on Packagist](https://packagist.org/packages/dept-of-scrapyard-robotics/st77xx) ![License](LICENSE)

[![Latest Version on Packagist](https://img.shields.io/packagist/v/dept-of-scrapyard-robotics/st77xx.svg)](https://packagist.org/packages/dept-of-scrapyard-robotics/st77xx)
[![License](https://img.shields.io/packagist/l/dept-of-scrapyard-robotics/st77xx.svg)](https://github.com/DeptOfScrapyardRobotics/ST77xx/tree/HEAD/LICENSE)

Drive ST7735, ST7789 and ST7796 colour TFT displays from PHP over SPI, using the ScrapyardIO GPIO framework.

`dept-of-scrapyard-robotics/st77xx` boots each controller with its datasheet init sequence and writes frames into its RAM, whole or a window at a time. Describe the wiring in a config file, ask the circuit catalog for the panel, and send it bytes packed the way its `formatSpec()` describes, which is what a Surface framebuffer produces. Orientation, colour mode, inversion and every power, gamma and timing register are typed settings.

```
ext-posi / ext-ftdi            1:1 system and libftdi calls
  → microscrap/*               libgpiod, spidev, libmpsse in PHP
    → microscrap/scrapyard-*   adapters: the `native` and `usb` drivers
      → scrapyard-io/framework protocol managers, transports, the circuit catalog
        → dept-of-scrapyard-robotics/st77xx   ← this package
```

## Requirements

- PHP 8.4 or newer
- A Venusian 0.10 application with the `scrapyard-io/framework` 0.10 components (`gpio/spi`, `gpio/digital`, `gpio/integrated-circuits`)
- `venusian-surface/contracts` 0.10, for the `FormatSpec` each panel describes its bytes with
- An adapter for your hardware:
  - `microscrap/scrapyard-linux` (driver `native`) for a Raspberry Pi or other Linux board: `spidev` and `libgpiod`, needs `ext-posi`
  - `microscrap/scrapyard-usb` (driver `usb`) for FTDI MPSSE boards such as the FT232H, needs `ext-ftdi`
- `venusian-surface/framebuffers` 0.10 if you want Surface to pack your frames

## Installation

```bash
composer require dept-of-scrapyard-robotics/st77xx
```

The service provider is discovered automatically. It merges the package's wiring config under `circuits.st7735`, `circuits.st7789` and `circuits.st7796`, and registers all three controllers with the circuit catalog. To publish the configs into your app, run:

```bash
php computer vendor:publish --tag=st77xx-config
```

That writes `config/circuits/st7735.php`, `st7789.php` and `st7796.php`, each with `driver => 'none'` until you fill in your bench.

## Quick start

A 480×320 ST7796 on a Raspberry Pi's SPI bus 0, chip select CE0, DC on GPIO22 and RST on GPIO24:

```php
// config/circuits/st7796.php
return [
    'default_config' => 'spi',
    'configs' => [
        'spi' => [
            'driver' => 'native',
            'device' => 0,
            'chip_select' => 0,
            'speed' => 10_000_000,
            'width' => 480,
            'height' => 320,
            'dc' => ['driver' => 'native', 'device' => 0, 'pin' => 22],
            'rst' => ['driver' => 'native', 'device' => 0, 'pin' => 24],
        ],
    ],
];
```

```php
use Surface\Framebuffers\Native\NativeFramebufferDriver;

$panel = app('circuit')->conjure('st7796');   // connected, reset and booted

$panel->fill(0, 0, 255);                       // solid blue

$spec = $panel->formatSpec();                  // row-major, 16-bit, high byte first
$fb = (new NativeFramebufferDriver)->full($spec, $panel->width(), $panel->height());
$fb->writeRgba8($rgba, $panel->width(), $panel->height());   // any RGBA8 image of that size

$panel->transmit(0, 0, $fb->flush($spec, true));
```

On a Raspberry Pi 5 at 10 MHz the panel boots in about 160 ms and takes a full 480×320 frame (307,200 bytes) in about 275 ms; 10 MHz alone needs 246 ms for those bytes.

## Connecting

`conjure('st7789')` reads `circuits.st7789`, picks `default_config` (or the config you name), and calls the controller's `spi()` factory with that entry's keys. You can call `spi()` directly too. Either way you get a booted panel unless you pass `boot_now: false`.

A 240×320 ST7789 on an FT232H, chip select on GPIO0 (D4), DC on GPIO1 (D5), RST on GPIO2 (D6):

```php
use DeptOfScrapyardRobotics\Displays\ST77xx\ST7789\ST7789;

$panel = ST7789::spi(
    'usb', 'ft232h',
    dc: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
    rst: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
    chip_select: 0,
    width: 240,
    height: 320,
);
```

A bus or pin device that isn't connected yet is connected by the factory. One your app already connected is shared as it is, so the panel can sit on a bus with other chips. The factory opens an unconnected bus in `mode` (0 by default) and refuses a bus your app already opened in a different mode. It sets this chip select's clock to `speed`, 10 MHz by default, whatever the bus runs at; without that, the FT232H adapter would run at its 400 kHz default. DC and RST are opened after the bus, so on an FT232H they ride the same USB context as its SPI engine. The FT232H's `chip_select` numbers are its GPIO pins: 0–3 are D4–D7, 4–11 are C0–C7.

On the FT232H at 10 MHz the ST7789 boots in about 230 ms and takes a full 240×320 frame in about 185 ms.

### Building the transport yourself

```php
use DeptOfScrapyardRobotics\Displays\ST77xx\ST7796\ST7796;
use DeptOfScrapyardRobotics\Displays\ST77xx\ST7796\ST7796Configuration;
use DeptOfScrapyardRobotics\Displays\ST77xx\Transports\ST77xxSPITransport;

$spi = app('gpio.spi')->driver('native')->connectTo(0)->mode(0)->speed(10_000_000)->register()->device(0, 0);
$pins = app('gpio.digital')->driver('native')->connectTo(0)->register();

$panel = new ST7796(new ST77xxSPITransport($spi, $pins->output(0, 22), $pins->output(0, 24)), new ST7796Configuration, boot_now: true);
```

## Configuration objects

Each controller has its own configuration class. Every argument is optional, and the defaults reproduce the common init sequence for that controller.

Shared by all three:

| Argument | Meaning |
|---|---|
| `width`, `height` | panel size in the orientation `mad_ctrl` sets |
| `max_packet_size` | largest data write, in bytes |
| `x_offset`, `y_offset` | where the visible area starts in controller memory, in that orientation |
| `mad_ctrl` | orientation and colour order (MADCTL) |
| `color_mode` | 12-, 16- or 18-bit pixels; defaults to 16-bit RGB565 |
| `invert_display` | display inversion at boot |
| `gamma_positive`, `gamma_negative` | gamma tables |

| Controller | Defaults | Controller-specific arguments |
|---|---|---|
| `ST7735Configuration` | 128×128, 2048-byte packets, MADCTL `0xC8`, inversion off | `nfc`, `ifc`, `pfc` (frame rate), `inversion_control`, `power_control_1` to `power_control_5`, `v_com_ctrl` |
| `ST7789Configuration` | 240×240, 2048-byte packets, MADCTL `0x00`, inversion on | `porch_ctrl`, `gate_ctrl`, `v_com_ctrl`, `lcm_ctrl`, `vdv_vrh_enable`, `vrh`, `vdv`, `frame_rate_ctrl`, `power_control_1` |
| `ST7796Configuration` | 480×320, 4092-byte packets, MADCTL `0x28`, inversion off | `inversion_ctrl`, `display_fn_ctrl`, `output_adjust`, `power_control_2`, `power_control_3`, `v_com_ctrl` |

Each register argument is a breakout object from that controller's `Breakouts` namespace, such as `ST7789MADControl` or `ST7735PowerControl1`. The `spi()` factory and the config files take `width`, `height`, `mad_ctrl` (as named flags), `x_offset`, `y_offset` and `invert_display`; leave any of them `null` for the controller's default.

### Orientation

`mad_ctrl` sets the scan direction: `pixel_direction_vertical` (MV) exchanges rows and columns, `right_left_column_addresses` (MX) and `bottom_top_row_addresses` (MY) mirror them, and `bgr_order_mode` switches RGB to BGR. Give the size and offsets for the orientation you configure:

```php
// 240×320 panel, portrait
new ST7789Configuration(width: 240, height: 320);

// same panel, landscape
new ST7789Configuration(width: 320, height: 240, mad_ctrl: new ST7789MADControl(right_left_column_addresses: true, pixel_direction_vertical: true));
```

When you change `mad_ctrl` on a running panel, the width, height and offsets move with it, so `width()`, `height()` and every window match what the panel now shows. A quarter turn toggles MV and MX together:

```php
$m = $panel->mad_ctrl;

$panel->mad_ctrl = new ST7789MADControl(
    bottom_top_row_addresses: $m->bottom_top_row_addresses,
    right_left_column_addresses: ! $m->right_left_column_addresses,
    pixel_direction_vertical: ! $m->pixel_direction_vertical,
    bgr_order_mode: $m->bgr_order_mode,
);

$panel->width();   // 320 on a 240×320 panel
```

### Offsets

Some panels show only part of the controller's memory. A 135×240 ST7789 sits 52 columns and 40 rows in:

```php
new ST7789Configuration(width: 135, height: 240, x_offset: 52, y_offset: 40, mad_ctrl: new ST7789MADControl(bottom_top_row_addresses: true, right_left_column_addresses: true));
```

The offsets are added to every window the panel opens. Rotating that panel moves them with the rest: a quarter turn puts the window at (40, 52), a half turn at (53, 40). A panel that fills its controller's memory, such as a 240×320 ST7789 or a 480×320 ST7796, keeps zero offsets in every orientation.

## Drawing

The panel does not keep pixels. You send it bytes already packed the way `formatSpec()` describes: rows top to bottom, pixels left to right, and in 16-bit mode each pixel two bytes, high byte first. A 320×240 frame is 153,600 bytes. A Surface framebuffer created with the panel's spec packs them for you, and flushing it in that same spec copies the bytes with no conversion:

```php
$spec = $panel->formatSpec();
$fb = (new NativeFramebufferDriver)->full($spec, $panel->width(), $panel->height());
$fb->writeRgba8($rgba, $panel->width(), $panel->height());

$panel->transmit(0, 0, $fb->flush($spec, true));
```

`transmit($x, $y, $bytes, $width, $height)` opens a window over that rectangle, starts a memory write, and streams the bytes. Width and height default to the whole panel. To redraw part of the screen, send only that window:

```php
use Surface\Contracts\Framebuffers\Region;

$region = new Region(208, 128, 64, 64);
$panel->transmit($region->x, $region->y, $fb->flushRegion($region, $spec, true), $region->width, $region->height);
```

`fill($red, $green, $blue)` paints the whole panel one colour without building a frame. Channels are 0 to 255, and the fill packs them for the colour mode the panel is in right now:

| Mode | Bytes per pixel | Packing |
|---|---|---|
| 12-bit | 1.5 | RGB444, two pixels per three bytes |
| 16-bit | 2 | RGB565, high byte first |
| 18-bit | 3 | RGB666, each channel in the top six bits of its byte |

Measured at 10 MHz, 16-bit, with the picture checked on the panel:

| | FT232H, ST7789 240×320 | Pi 5 spidev, ST7796 480×320 |
|---|---|---|
| Boot | 228 ms | 163 ms |
| `fill()` | 280–370 ms | 273–278 ms |
| Full frame | 182–229 ms | 273–277 ms |
| 64×64 window | 17 ms | 8 ms |

### Piping from memory

All three chips are `PipeablePanel`s (gpio/contracts), so pixel bytes can reach the panel without passing through PHP. `openWindow($x, $y, $width, $height)` sends the column and row window and the memory write command, then raises DC. The window's bytes then go out on `pixelBus()`, a bus that reads them straight from memory:

```php
$panel->openWindow(0, 0, $panel->width(), $panel->height());
$panel->pixelBus()->writeFrom([[$framebuffer->pointer(), $panel->width() * $panel->height() * 2]]);
```

`pixelBus()` is `null` unless the SPI connection can write from memory. Today that is the Pi's spidev (`PosixSPITransport` in microscrap/scrapyard-linux); FT232H connections answer `null`. You rarely call these yourself: attach the panel to Surface with `app('displays')->panel('st7796', direct: true)`, and its `DirectEDisplay` opens a window for each changed region and pipes the rows out of the framebuffer's ext-fb memory.

## Settings

```php
use DeptOfScrapyardRobotics\Displays\ST77xx\ST7789\Enums\ST7789ColorMode;

$panel->display_on = false;             // blank; RAM keeps the picture
$panel->display_on = true;
$panel->sleep_mode_on = true;           // low power
$panel->sleep_mode_on = false;          // waits 120 ms
$panel->invert_display = false;
$panel->color_mode = ST7789ColorMode::COLOR18;
```

Any configuration key reads as a property: `$panel->width`, `$panel->x_offset`, `$panel->gamma_positive` and so on. Every register argument listed under [Configuration objects](#configuration-objects) can also be written as a property, and the panel sends it straight away. Size, offsets and packet size are read-only; size and offsets follow `mad_ctrl`. The driver never reads the controller, so reads return what the configuration holds.

Changing `color_mode` also rebuilds the `FormatSpec`, so take it again before packing the next frame. `fill()` and the `FormatSpec` always follow the mode in force.

The same settings are available as methods, such as `setDisplay()`, `setSleepMode()`, `setDisplayInversion()`, `setPixelFormat()` (which also takes 12, 16 or 18), `setMADControl()` and `setAddressWindow()`, plus one setter per register breakout.

## Errors

Everything throws `ST77xxException`, which descends from `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitException`.

Every SPI write is checked: a write the bus refuses or cuts short throws `spiWriteFailed`. SPI has no acknowledge, so a missing panel can't be detected from the bus.

| Factory | When |
|---|---|
| `notConnected` | the protocol driver handed back no bus or pin |
| `invalidSpiMode` | `mode` isn't 0 to 3 |
| `invalidSpiClock` | `speed` below 1 Hz |
| `wrongSpiMode` | the bus is already open in a different mode than configured |
| `incompletePin` | a `dc` or `rst` config is missing `driver`, `device` or `pin` |
| `spiWriteFailed` | the bus wrote fewer bytes than asked |
| `invalidPacketSize` | `max_packet_size` below 1 |
| `invalidRegisterValue` | a register value or fill channel out of range |
| `invalidColorMode` | a colour mode other than 12, 16 or 18 bits |
| `invalidProperty` | an unknown property or configuration key, or a write to a read-only one |

## Closing

```php
$panel->close();
```

`close()` releases the DC and RST pins. The SPI connection belongs to the protocol driver and stays open for other chips. The panel keeps showing its last frame; set `display_on = false` first to blank it.

## Configuration files

`config/circuits/st7735.php`, `st7789.php` and `st7796.php` share this shape:

| Key | Default | Meaning |
|---|---|---|
| `default_config` | `'spi'` | which entry under `configs` `conjure()` uses |
| `configs.<name>.protocol` | the entry's name | `spi`, so an app can keep `left` and `right` panels |
| `configs.spi.driver` | `'none'` | SPI adapter: `native` or `usb` |
| `configs.spi.device` | `''` | SPI bus number, or `ft232h` |
| `configs.spi.chip_select` | `0` | chip select |
| `configs.spi.mode` | `0` | SPI mode |
| `configs.spi.speed` | `10_000_000` | this chip select's clock in Hz |
| `configs.spi.width` / `height` | `null` | panel size; null keeps the controller's default |
| `configs.spi.mad_ctrl` | `[]` | named MADControl flags |
| `configs.spi.x_offset` / `y_offset` | `null` | memory offsets |
| `configs.spi.invert_display` | `null` | inversion at boot |
| `configs.spi.dc` / `rst` | pins 0 / 1 | `driver`, `device`, `pin` for each line |
| `configs.*.boot_now` | `true` | boot during `conjure()` |

## Upgrading from 0.8

| 0.8 | 0.10 |
|---|---|
| `scrapyard-io/framework` 0.8 components, `surface/contracts` | the 0.10 components, `venusian-surface/contracts` |
| `Circuit::conjure()`, `SPI::driver(...)`, `DigitalIO::driver(...)` | `app('circuit')->conjure()`, `{Chip}::spi()`, `app('gpio.spi')->driver(...)` |
| panels implemented Surface's `FormatSpecification` | Surface 0.10 has no such interface; `formatSpec()` is unchanged |
| `speed: null` ran the FT232H at 400 kHz | `speed` defaults to 10 MHz and is applied to the chip select |
| a bus open in another mode was used as it was | refused with `wrongSpiMode` |
| failed writes were ignored | failed writes throw `spiWriteFailed` |
| gamma and ST7796 output-adjust bytes were masked to fit | out-of-range bytes throw `invalidRegisterValue` |
| changing `mad_ctrl` left width, height and offsets as they were | they move to the new orientation |
| offsets and inversion only through a configuration object | also `x_offset`, `y_offset`, `invert_display` in config and `spi()` |

## Testing

```bash
composer install
vendor/bin/pest
```

The suite runs against recording fake buses and pins, so it needs no hardware. The panels were also checked on hardware for this release, with someone watching: a 480×320 ST7796 on a Raspberry Pi 5's SPI and a 240×320 ST7789 on an FT232H's SPI. Both showed the right solid colours, a test pattern, a window write, a quarter turn and back, inversion and display off and on.

## Security

The driver writes commands and pixel data to hardware the PHP process can open. See [SECURITY.md](https://github.com/DeptOfScrapyardRobotics/ST77xx/blob/HEAD/SECURITY.md) for the support policy and how to report a vulnerability.

## License

MIT. See [LICENSE](https://github.com/DeptOfScrapyardRobotics/ST77xx/tree/HEAD/LICENSE).
