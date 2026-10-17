# Display Panels

A display panel is an integrated circuit that holds pixels: an OLED, a TFT, an ePaper sheet. ScrapyardIO describes one with the `DisplayPanel` contract and a handful of small capability interfaces layered on top of it, so a consumer can tell exactly what a panel can do (write a window, refresh on command, switch its output off) without knowing which chip it is. This page covers those contracts, the panels the Dept of Scrapyard Robotics ships, and how Venusian Surface's embedded displays drive them.

## Introduction

Every panel contract lives in `gpio/contracts`, in the `GeneralPurposeIO\Contracts\IntegratedCircuits` namespace. The base is `DisplayPanel`, which extends the empty `IntegratedCircuit` marker. Each capability is its own interface that extends `DisplayPanel`, and a chip driver implements the ones that match its hardware:

| Interface | Adds | Means |
| --- | --- | --- |
| `DisplayPanel` | `width()`, `height()`, `transmit()` | The panel takes packed pixel bytes into its RAM. |
| `WindowAddressable` | nothing | `transmit()` honours its origin and size: a region write leaves the rest of the panel alone. |
| `PipeablePanel` | `openWindow()`, `pixelBus()` | A `WindowAddressable` panel that can be fed straight from memory. |
| `RefreshesOnCommand` | `refresh()` | Writing RAM and updating the visible image are separate steps. |
| `Switchable` | `setDisplay()` | The panel's output can be turned on and off while RAM keeps its contents. |

Capabilities are separate interfaces because panels really do differ. A TFT or OLED shows what you write the moment it lands, so it never implements `RefreshesOnCommand`. An ePaper panel takes seconds to redraw, so writing and showing must be separate calls. A strip or chain with no address window has to receive the whole frame every time, so it implements the base contract alone and a consumer sends whole frames.

## The DisplayPanel Contract

`DisplayPanel` declares three methods:

```php
namespace GeneralPurposeIO\Contracts\IntegratedCircuits;

interface DisplayPanel extends IntegratedCircuit
{
    public function width(): int;

    public function height(): int;

    /**
     * @param  list<int>  $raw_data
     */
    public function transmit(int $origin_x, int $origin_y, array $raw_data, ?int $frame_width = null, ?int $frame_height = null): void;
}
```

`transmit()` writes bytes into the rectangle whose top-left corner is `($origin_x, $origin_y)`. A `null` width or height means the whole panel. On a panel that is not `WindowAddressable`, the origin and size cover the whole panel on every call.

The contract deliberately says nothing about how the bytes are packed. Pixel formats belong to Surface, so `gpio/contracts` never imports a Surface class. That is what lets a PWM fan board or an accelerometer install `gpio/contracts` without pulling a graphics package along. A panel driver therefore also answers `formatSpec(): FormatSpec`, using Surface's `Surface\Contracts\Framebuffers\FormatSpec`, and that is why every panel package in the Dept of Scrapyard Robotics requires `venusian-surface/contracts` alongside the GPIO splits. The SSD1306, for example, describes its one-bit vertical pages like this:

```php
use Surface\Contracts\Framebuffers\BitDepth;
use Surface\Contracts\Framebuffers\BitOrder;
use Surface\Contracts\Framebuffers\FormatSpec;
use Surface\Contracts\Framebuffers\PageAxis;
use Surface\Contracts\Framebuffers\PixelFormat;
use Surface\Contracts\Framebuffers\ScanDirection;

public function formatSpec(): FormatSpec
{
    return new FormatSpec(
        PixelFormat::MONO_VERTICAL_PAGE,
        BitDepth::B1,
        ScanDirection::TOP_TO_BOTTOM,
        BitOrder::LSB_FIRST,
        page_axis: PageAxis::VERTICAL,
    );
}
```

The dependency only ever points one way: Surface may require `gpio/contracts`, and no ScrapyardIO split requires Surface.

## Panel Capabilities

### WindowAddressable

`WindowAddressable` adds no methods. It is a promise about `transmit()`: when you pass an origin and a frame size, the panel writes only that rectangle. A consumer that tracks damage can then send just the regions that changed instead of the whole frame.

### PipeablePanel

`PipeablePanel` extends `WindowAddressable` for panels whose pixel bytes can be handed to the bus straight out of memory, with no PHP array in between:

```php
use GeneralPurposeIO\Contracts\SPI\WritesFromMemory;

interface PipeablePanel extends WindowAddressable
{
    public function openWindow(int $x, int $y, int $width, int $height): void;

    public function pixelBus(): ?WritesFromMemory;
}
```

`openWindow()` sets the address window, starts the memory write and leaves the panel taking data. The window's bytes, packed per the chip's `formatSpec()`, then go out on `pixelBus()`. `pixelBus()` returns `null` when the chip's bus cannot write from memory, which is the case for I2C, for an offloaded bus and for MPSSE over an FTDI bridge; on a native spidev bus it returns the SPI transport.

### RefreshesOnCommand

`RefreshesOnCommand` separates the RAM write from the visible update:

```php
interface RefreshesOnCommand extends DisplayPanel
{
    public function refresh(RefreshMode $mode = RefreshMode::FULL): void;
}
```

`transmit()` writes, `refresh()` shows. The `RefreshMode` enum is string-backed with two cases, `RefreshMode::FULL` (`'full'`) and `RefreshMode::PARTIAL` (`'partial'`). Which modes a chip accepts is the chip's business: the JD79661, the Spectra 6 and the three-colour SSD1680 accept `FULL` only and throw for `PARTIAL`, while the black-and-white SSD1680 accepts `PARTIAL` once it has shown one full refresh.

### Switchable

`Switchable` turns the panel's output on or off. The panel keeps its RAM, so switching back on shows the same image:

```php
interface Switchable extends DisplayPanel
{
    public function setDisplay(bool $on): void;
}
```

## Panel Chip Packages

The Dept of Scrapyard Robotics panel drivers each extend `GeneralPurposeIO\IntegratedCircuits\Bootable` and implement the capabilities below. Every one also registers itself in the [circuit catalog](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits) under the slugs listed, so `app('circuit')->conjure($slug)` builds a wired, booted panel from your config.

| Package | Class | Catalog slugs | Capabilities |
| --- | --- | --- | --- |
| [ssd1306](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/overview) | `SSD1306` | `ssd1306` | `WindowAddressable`, `Switchable` |
| [sh1106](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/overview) | `SH1106` | `sh1106` | `WindowAddressable`, `Switchable` |
| [st77xx](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/overview) | `ST7735`, `ST7789`, `ST7796` | `st7735`, `st7789`, `st7796` | `PipeablePanel`, `Switchable` |
| [gc9a01](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/overview) | `GC9A01` | `gc9a01` | `PipeablePanel`, `Switchable` |
| [ssd1680](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1680/overview) | `SSD1680BW`, `SSD1680BWR` | `ssd1680-bw`, `ssd1680-bwr` | `WindowAddressable`, `RefreshesOnCommand` |
| [jd79661](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/jd79661/overview) | `JD79661` | `jd79661` | `RefreshesOnCommand` |
| [spectra6](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/spectra6/overview) | `Spectra6` | `spectra6` | `RefreshesOnCommand` |

Because `PipeablePanel` extends `WindowAddressable`, the ST77xx and GC9A01 panels are window addressable too. The JD79661 and Spectra 6 take whole frames only.

You can drive a panel yourself, without Surface, through the same contracts:

```php
$oled = app('circuit')->conjure('ssd1306');

$oled->transmit(0, 0, $bytes);   // a whole 128×64 frame, packed per $oled->formatSpec()
$oled->setDisplay(false);        // output off; RAM keeps the image
```

## The Consumer Rule

Code that draws for a panel decides what to send from the capabilities alone. This is the rule Surface's embedded displays follow, and any other consumer should follow it too:

- When the panel is `WindowAddressable`, send only the damaged regions. Otherwise, send the whole frame whenever anything changed.
- When the panel is a `PipeablePanel` and you want no PHP bytes at all, call `openWindow()` for each region, then write the region straight out of memory with `pixelBus()->writeFrom()`.
- When the panel is `RefreshesOnCommand`, call `refresh()` once per frame, after the last `transmit()` of that frame, and only when something was sent.
- When the panel is `Switchable`, call `setDisplay(false)` when you are done with it. Showing and hiding the display map to `setDisplay(true)` and `setDisplay(false)`.

Before drawing, a consumer that needs a live chip should also check `hasBooted()`, which every `Bootable` panel answers.

## Venusian Surface Embedded Displays

Venusian Surface's `venusian-surface/embedded-displays` package requires `gpio/contracts` and turns any `DisplayPanel` into a drawing output. Its `displays` manager either conjures a panel through the circuit catalog or attaches one you built:

```php
$oled = app('displays')->panel('ssd1306');         // conjured from config/circuits/ssd1306.php
$tft = app('displays')->attach($st7789, 'tft');    // a panel you conjured yourself
```

`attach()` refuses a panel that does not answer `formatSpec()`, and refuses a `Bootable` panel that has not booted. From there Surface applies the consumer rule:

- `framebuffer()` picks the framebuffer kind from the capabilities: `epaper` for a `RefreshesOnCommand` panel, `dirty` for a `WindowAddressable` one, and `full` otherwise. The defaults live in Surface's `embedded-displays.defaults` config.
- `present()` sends the whole frame the first time and after a `show()` or a new framebuffer. After that a `WindowAddressable` panel receives each damaged region, snapped to what the panel can address, while any other panel receives the whole frame. A `RefreshesOnCommand` panel then gets one `refresh()` with the display's refresh mode, which you set with `refreshMode(RefreshMode::PARTIAL)`.
- `show()`, `hide()` and `close()` call `setDisplay()` on a `Switchable` panel. `show()` and `hide()` throw on a panel that is not switchable.
- `panel('st7796', direct: true)` builds a `DirectEDisplay`, which requires a `PipeablePanel` whose `pixelBus()` is not `null` and pipes the framebuffer's memory onto the bus.

If a panel call throws, the display latches the fault and sends nothing more. The full behaviour, including framebuffer kinds and the direct path's requirements, is documented on Surface's [EmbeddedDisplays](https://venusian.projectsaturnstudios.com/docs/surface/architecture/embeddeddisplays) page, and the package's place among the Surface splits on the [Components](https://venusian.projectsaturnstudios.com/docs/surface/guide/components) page.

## Writing a Panel Driver

A new panel driver is a chip package like any other; see [Writing a Chip Driver](/docs/{{version}}/scrapyard-io/digging-deeper/writing-a-chip-driver). On top of that guide, a panel driver:

- implements `DisplayPanel` and each capability its hardware has, and no more, since consumers act on the interfaces it claims;
- answers `formatSpec()` with the byte layout `transmit()` expects, and requires `venusian-surface/contracts` for the `FormatSpec` class;
- returns a fresh `FormatSpec` whenever rotation or colour mode changes the layout, because Surface reads `formatSpec()` on every send;
- returns `null` from `pixelBus()` whenever the bus underneath cannot write from memory, when it is a `PipeablePanel`.
