# Drawing frames

FormatSpec, packing with a Surface framebuffer, transmit() windows, fill(), colour modes, piping from memory, MADCTL, live timings.

## FormatSpec

`ROW_MAJOR`, `BitDepth::from(color_mode->bitsPerPixel())`, `TOP_TO_BOTTOM`, `Endianness::MSB`.[^panel] Built in ctor; rebuilt by `setPixelFormat()`.

16-bit: 2 bytes/pixel, high first (red = `F8 00`). 18-bit: 3 bytes, channel left-aligned (`FC 00 00`). 12-bit: two pixels per three bytes. 240×240 at 16-bit = 115 200 bytes.

## Packing

```php
$spec = $panel->formatSpec();
$fb = (new NativeFramebufferDriver)->full($spec, 240, 240);
$fb->writeRgba8($rgba, 240, 240);
$panel->transmit(0, 0, $fb->flush($spec, true));
```

Flush in panel's spec = bytes copied, no conversion.

## transmit

`transmit($x, $y, $bytes, $w, $h)`: CASET + RASET (16-bit big-endian, no offsets), `2C`, then data in `max_packet_size` chunks (default 4092).[^api] `$w` / `$h` default 240. Window write leaves rest of RAM alone.

## fill

`fill($r, $g, $b)` 0–255 each, any other → `invalidRegisterValue`. Packs for current mode, whole panel, no frame built.[^fill]

## Piping

`PipeablePanel`: `openWindow()` = window + `2C` + DC high; bytes then via `pixelBus()` (`WritesFromMemory`). `null` on FT232H / MPSSE.[^pipes]

## Orientation

MADCTL changes RAM → glass map only. Panel square, RAM = glass: size stays 240×240, windows from 0. MX mirrors columns, MY rows, MV swaps axes; all three checked on hardware.

Round glass: square corners never visible.

## Live reference

FT232H, `usb` driver, 10 MHz, 16-bit, picture checked by eye (2026-10-06):

| | |
|---|---|
| boot via `conjure()` | 331 ms |
| flush + transmit full frame | 139 ms |
| 10 frames incl. `writeRgba8` | 2.40 s (4.2 fps) |

## Related

* [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/overview) · [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/connecting) · [registers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/registers) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/runbooks/hardware-smoke)

[^panel]: GC9A01::transmit() / generateFormatSpec()
[^api]: setAddressWindow()
[^fill]: GC9A01Fills
[^pipes]: GC9A01Pipes
