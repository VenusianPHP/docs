# Overview

![Latest Version on Packagist](https://packagist.org/packages/dept-of-scrapyard-robotics/gc9a01) ![License](LICENSE)

[![Latest Version on Packagist](https://img.shields.io/packagist/v/dept-of-scrapyard-robotics/gc9a01.svg)](https://packagist.org/packages/dept-of-scrapyard-robotics/gc9a01)
[![License](https://img.shields.io/packagist/l/dept-of-scrapyard-robotics/gc9a01.svg)](https://github.com/DeptOfScrapyardRobotics/GC9A01/tree/HEAD/LICENSE)

Drive the GC9A01 240×240 round colour display from PHP over SPI, using the ScrapyardIO GPIO framework.

`dept-of-scrapyard-robotics/gc9a01` boots the controller with its reference bring-up sequence and writes frames into its RAM, whole or a window at a time. Describe the wiring in a config file, ask the circuit catalog for the panel, and send it bytes packed the way its `formatSpec()` describes, which is what a Surface framebuffer produces. Orientation, colour mode, inversion and every power, gamma and timing register the datasheet describes are typed settings.

```
ext-posi / ext-ftdi            1:1 system and libftdi calls
  → microscrap/*               libgpiod, spidev, libmpsse in PHP
    → microscrap/scrapyard-*   adapters: the `native` and `usb` drivers
      → scrapyard-io/framework protocol managers, transports, the circuit catalog
        → dept-of-scrapyard-robotics/gc9a01   ← this package
```

## Requirements

- PHP 8.4 or newer
- A Venusian 0.10 application with the `scrapyard-io/framework` 0.10 components (`gpio/spi`, `gpio/digital`, `gpio/integrated-circuits`)
- `venusian-surface/contracts` 0.10, for the `FormatSpec` the panel describes its bytes with
- An adapter for your hardware:
  - `microscrap/scrapyard-linux` (driver `native`) for a Raspberry Pi or other Linux board: `spidev` and `libgpiod`, needs `ext-posi`
  - `microscrap/scrapyard-usb` (driver `usb`) for FTDI MPSSE boards such as the FT232H, needs `ext-ftdi`
- `venusian-surface/framebuffers` 0.10 if you want Surface to pack your frames

## Installation

```bash
composer require dept-of-scrapyard-robotics/gc9a01
```

The service provider is discovered automatically. It merges the package's wiring config under `circuits.gc9a01` and registers the panel with the circuit catalog. To publish the config into your app, run:

```bash
php computer vendor:publish --tag=gc9a01-config
```

That writes `config/circuits/gc9a01.php` with `driver => 'none'` until you fill in your bench.

## Quick start

A GC9A01 on an FT232H, chip select on GPIO0 (D4), DC on GPIO1 (D5), RST on GPIO2 (D6):

```php
// config/circuits/gc9a01.php
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
        ],
    ],
];
```

```php
use Surface\Framebuffers\Native\NativeFramebufferDriver;

$panel = app('circuit')->conjure('gc9a01');   // connected, reset and booted

$panel->fill(0, 0, 255);                       // solid blue

$spec = $panel->formatSpec();                  // row-major, 16-bit, high byte first
$fb = (new NativeFramebufferDriver)->full($spec, 240, 240);
$fb->writeRgba8($rgba, 240, 240);              // any RGBA8 image of that size

$panel->transmit(0, 0, $fb->flush($spec, true));
```

On the FT232H at 10 MHz the panel boots in about 330 ms. Flushing and sending a full 240×240 frame (115,200 bytes) takes about 140 ms, and ten frames including packing take about 2.4 s.

## Connecting

`conjure('gc9a01')` reads `circuits.gc9a01`, picks `default_config` (or the config you name), and calls `GC9A01::spi()` with that entry's keys. You can call `spi()` directly too. Either way you get a booted panel unless you pass `boot_now: false`.

```php
use DeptOfScrapyardRobotics\Displays\GC9A01\GC9A01;

$panel = GC9A01::spi(
    'usb', 'ft232h',
    dc: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
    rst: ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
    chip_select: 0,
);
```

A bus or pin device that isn't connected yet is connected by the factory. One your app already connected is shared as it is, so the panel can sit on a bus with other chips. The factory opens an unconnected bus in `mode` (0 by default) and refuses a bus your app already opened in a different mode. It sets this chip select's clock to `speed`, 10 MHz by default, whatever the bus runs at; without that, the FT232H adapter would run at its 400 kHz default. DC and RST are opened after the bus, so on an FT232H they ride the same USB context as its SPI engine. The FT232H's `chip_select` numbers are its GPIO pins: 0–3 are D4–D7, 4–11 are C0–C7.

On a Raspberry Pi the same panel is `driver => 'native'`, `device` the SPI bus number, and DC and RST on `libgpiod` lines.

### Building the transport yourself

```php
use DeptOfScrapyardRobotics\Displays\GC9A01\GC9A01;
use DeptOfScrapyardRobotics\Displays\GC9A01\GC9A01Configuration;
use DeptOfScrapyardRobotics\Displays\GC9A01\Transports\GC9A01SPITransport;

$spi = app('gpio.spi')->driver('native')->connectTo(0)->mode(0)->speed(10_000_000)->register()->device(0, 0);
$pins = app('gpio.digital')->driver('native')->connectTo(0)->register();

$panel = new GC9A01(new GC9A01SPITransport($spi, $pins->output(0, 22), $pins->output(0, 24)), new GC9A01Configuration, boot_now: true);
```

## Drawing

The panel does not keep pixels. You send it bytes already packed the way `formatSpec()` describes: rows top to bottom, pixels left to right, and in 16-bit mode each pixel two bytes, high byte first. A Surface framebuffer created with the panel's spec packs them for you, and flushing it in that same spec copies the bytes with no conversion.

`transmit($x, $y, $bytes, $width, $height)` opens a window over that rectangle, starts a memory write, and streams the bytes. Width and height default to the whole panel. To redraw part of the screen, send only that window:

```php
$magenta = (new NativeFramebufferDriver)->full($spec, 64, 64);
$magenta->fill(0xFF00FFFF);

$panel->transmit(88, 88, $magenta->flush($spec, true), 64, 64);   // the centre; the rest is untouched
```

`fill($red, $green, $blue)` paints the whole panel one colour without building a frame. Channels are 0 to 255, and the fill packs them for the colour mode the panel is in right now:

| Mode | Bytes per pixel | Packing |
|---|---|---|
| 12-bit | 1.5 | RGB444, two pixels per three bytes |
| 16-bit | 2 | RGB565, high byte first |
| 18-bit | 3 | RGB666, each channel in the top six bits of its byte |

The glass is round, so the corners of the 240×240 square are never visible; draw what matters inside the circle.

### Piping from memory

The panel is a `PipeablePanel` (gpio/contracts). `openWindow($x, $y, $width, $height)` sends the column and row window and the memory write command, then raises DC. The window's bytes then go out on `pixelBus()`, a bus that reads them straight from memory:

```php
$panel->openWindow(0, 0, 240, 240);
$panel->pixelBus()->writeFrom([[$framebuffer->pointer(), 240 * 240 * 2]]);
```

`pixelBus()` is `null` unless the SPI connection can write from memory. Today that is the Pi's spidev (`PosixSPITransport` in microscrap/scrapyard-linux); FT232H connections answer `null`.

## Settings

```php
use DeptOfScrapyardRobotics\Displays\GC9A01\Breakouts\GC9A01MADControl;
use DeptOfScrapyardRobotics\Displays\GC9A01\Enums\GC9A01ColorMode;

$panel->display_on = false;             // blank; RAM keeps the picture
$panel->display_on = true;
$panel->sleep_mode_on = true;           // low power
$panel->sleep_mode_on = false;          // waits 120 ms
$panel->invert_display = false;
$panel->color_mode = GC9A01ColorMode::COLOR18;
$panel->mad_ctrl = new GC9A01MADControl(right_left_column_addresses: true);   // mirror the columns
```

`mad_ctrl` sets how RAM maps to the glass: `bottom_top_row_addresses` (MY) and `right_left_column_addresses` (MX) mirror it, `pixel_direction_vertical` (MV) exchanges rows and columns, and `bgr_order_mode` switches RGB to BGR. The panel is square and its RAM is its glass, so the size is always 240×240 and every window is addressed from zero.

Any configuration key reads as a property: `$panel->mad_ctrl`, `$panel->frame_rate`, `$panel->gamma_1` and so on. The keys that boot writes can also be written as properties, and the panel sends them straight away. The driver never reads the controller, so reads return what the configuration holds.

Changing `color_mode` also rebuilds the `FormatSpec`, so take it again before packing the next frame.

The same settings are available as methods, such as `setDisplay()`, `setSleepMode()`, `setDisplayInversion()`, `setPixelFormat()` (which also takes 12, 16 or 18), `setMADControl()` and `setAddressWindow()`, plus one setter per register.

## Registers

Every register the GC9A01A datasheet describes is a typed, range-checked breakout in `Breakouts/`: a `DataRegister` when it is one byte, a `toBytes()` object when it is several. Field names and widths are the datasheet's. A value that does not fit its bits throws `invalidRegisterValue`; nothing is masked.

| Register | Setter | Fields |
|---|---|---|
| `B0` RGB interface signal control | `setRGBInterfaceSignalControl()` | `rcm`, VSYNC / HSYNC / DOTCLK / DE polarity |
| `B5` blanking porch | `setBlankingPorch()` | `vfp`, `vbp`, `hbp` |
| `B6` display function control | `setDisplayFunctionControl()` | gate and source scan direction, gate arrangement, optional `lines` |
| `BA` tearing effect control | `setTearingEffectControl()` | pulse polarity and width |
| `F6` interface control | `setInterfaceControl()` | operation mode, RGB RAM access, 6-bit RGB |
| `C1` power control 1 | `setPowerControl1()` | external or internal reference |
| `C3` power control 2 | `setPowerControl2()` | `vbp_d`, the top grayscale reference |
| `C4` power control 3 | `setPowerControl3()` | `vbn_d`, the bottom grayscale reference |
| `C9` power control 4 | `setPowerControl4()` | `vrh`, the offset both references share |
| `A7` power control 7 | `setPowerControl7()` | `vdd_ad`, the VCORE level |
| `E8` frame rate | `setFrameRate()` | inversion mode, `rtn1`, optional `rtn2` |
| `E9` SPI 2DATA control | `setSPI2DataControl()` | two-data-line enable and pixel format |
| `EC` charge pump frequency | `setChargePumpFrequency()` | `avdd`, `avee`, `vcl`, `vgh`, `vgl` |
| `F0`–`F3` gamma 1–4 | `setGamma1()`–`setGamma4()` | the datasheet's `dig2gam_*` nodes: `j0`, `vr1`, `vr2`, … `vr63` |

```php
use DeptOfScrapyardRobotics\Displays\GC9A01\Breakouts\GC9A01FrameRate;
use DeptOfScrapyardRobotics\Displays\GC9A01\Breakouts\GC9A01PowerControl2;
use DeptOfScrapyardRobotics\Displays\GC9A01\Enums\GC9A01InversionMode;

$panel->setFrameRate(new GC9A01FrameRate(GC9A01InversionMode::DOT_4, rtn1: 0x4));   // sends 0x34
$panel->setPowerControl2(new GC9A01PowerControl2(vbp_d: 0x13));
```

The defaults reproduce the reference bring-up bytes (Waveshare, Adafruit, TFT_eSPI and Arduino_GFX agree), which differ from the datasheet's power-on values: `C3` and `C4` are `0x13`, `C9` is `0x22`, `E8` is `0x34`.

The power, frame rate, gamma, SPI 2DATA and charge pump registers are the datasheet's Inter registers. They accept writes only after `interRegisterEnable()` has written FEh and EFh, which boot does; a hardware or software reset locks them again.

### Vendor registers

The boot sequence also writes 31 registers the datasheet never mentions (`0x62`–`0x67`, `0x70`, `0x74`, `0x84`–`0x90`, `0x98`, `0xAE`, `0xBC`–`0xBE`, `0xCD`, `0xDF`, `0xE1`, `0xEB`, `0xED`, `0xFF`). Nothing public says what their bits mean, so they do not break down into fields: `GC9A01VendorRegister` names each by address and carries the one payload the reference sequence gives it. `$panel->writeVendorRegister(GC9A01VendorRegister::VENDOR_98)` sends one.

## Errors

Everything throws `GC9A01Exception`, which descends from `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitException`.

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
| `invalidRegisterValue` | a register field or fill channel out of range, or a byte that names no defined value |
| `invalidColorMode` | a colour mode other than 12, 16 or 18 bits |
| `invalidProperty` | an unknown property or configuration key, or a write to a read-only one |

## Closing

```php
$panel->close();
```

`close()` releases the DC and RST pins. The SPI connection belongs to the protocol driver and stays open for other chips. The panel keeps showing its last frame; set `display_on = false` first to blank it.

## Configuration file

`config/circuits/gc9a01.php`:

| Key | Default | Meaning |
|---|---|---|
| `default_config` | `'spi'` | which entry under `configs` `conjure()` uses |
| `configs.<name>.protocol` | the entry's name | `spi`, so an app can keep `left` and `right` panels |
| `configs.spi.driver` | `'none'` | SPI adapter: `native` or `usb` |
| `configs.spi.device` | `''` | SPI bus number, or `ft232h` |
| `configs.spi.chip_select` | `0` | chip select |
| `configs.spi.mode` | `0` | SPI mode |
| `configs.spi.speed` | `10_000_000` | this chip select's clock in Hz |
| `configs.spi.mad_ctrl` | `[]` | named MADControl flags |
| `configs.spi.invert_display` | `null` | inversion at boot; null keeps the controller's default (on) |
| `configs.spi.dc` / `rst` | pins 0 / 1 | `driver`, `device`, `pin` for each line |
| `configs.*.boot_now` | `true` | boot during `conjure()` |

## Upgrading from 0.6

| 0.6 | 0.10 |
|---|---|
| `fabricate/*` packages and `scrapyard-io` 0.6 | the 0.10 components, `venusian-surface/contracts` |
| `Circuit::addCircuit()` magic alias, `GC9A01::spi(spi_device, chip_select, digital_device, …)` | `app('circuit')->conjure('gc9a01')`, `GC9A01::spi($driver, $device, dc: …, rst: …)` |
| `GC9A01::fromSPIBus()`, `GC9A01CarrierTransport` | `new GC9A01(new GC9A01SPITransport(...), new GC9A01Configuration)` |
| `GC9A01OpCode::MYSTERY_REGISTER_1` … `31`, numbered in boot order | `GC9A01VendorRegister::VENDOR_EB` … `VENDOR_FF`, named by address |
| `GC9A01PowerControl2/3/4` and `FrameRate` took any byte | `vbp_d`, `vbn_d` and `vrh` are 7, 7 and 6 bits; `E8` is `DINV` and `RTN1` |
| `GC9A01DisplayFunctionControl(scan_control, gate_scan)` raw bytes | `gate_scan_reversed`, `source_scan_reversed`, `gate_arrangement`, optional `lines` |
| gamma banks were six loose bytes | the datasheet's `j0`, `vr1` … `vr63` fields |
| the SPI clock was fixed at 40 MHz | `speed` defaults to 10 MHz and is applied to the chip select |
| failed writes were ignored | failed writes throw `spiWriteFailed` |
| reset pulses of 3 ms | 10 ms |

## Testing

```bash
composer install
vendor/bin/pest
```

The suite runs against recording fake buses and pins, so it needs no hardware, and pins the boot sequence byte for byte against the reference bring-up. The panel was also checked on hardware for this release, with someone watching: a GC9A01 on an FT232H's SPI showed the right solid colours, a test pattern, a window write, each MADCTL mirror and the axis swap, inversion, and display off and on.

## Security

The driver writes commands and pixel data to hardware the PHP process can open. See [SECURITY.md](https://github.com/DeptOfScrapyardRobotics/GC9A01/blob/HEAD/SECURITY.md) for the support policy and how to report a vulnerability.

## License

MIT. See [LICENSE](https://github.com/DeptOfScrapyardRobotics/GC9A01/tree/HEAD/LICENSE).
