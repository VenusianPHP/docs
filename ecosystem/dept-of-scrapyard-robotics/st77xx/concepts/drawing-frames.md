# Drawing frames

FormatSpec, packing with a Surface framebuffer, transmit() windows and offsets, mode-neutral fill(), colour-mode switching, piping from memory, live timings.

## FormatSpec

`ROW_MAJOR`, `BitDepth::from(color_mode->bitsPerPixel())`, `TOP_TO_BOTTOM`, `Endianness::MSB`.[^panel] Built in ctor; rebuilt by `setPixelFormat()`.

16-bit: 2 bytes/pixel, high first (red = `F8 00`). 18-bit: 3 bytes, each channel left-aligned (`FC 00 00`). Row by row, left → right. 320×240 at 16-bit = 153 600 bytes.

## Packing

Surface framebuffer in the panel's spec (`venusian-surface/framebuffers`):[^native]

```php
$spec = $panel->formatSpec();
$fb = (new NativeFramebufferDriver)->full($spec, $panel->width(), $panel->height());
$fb->writeRgba8($rgba, $panel->width(), $panel->height());
$panel->transmit(0, 0, $fb->flush($spec, true));
```

Same spec in and out → flush copies, no conversion.

## transmit()

`transmit(int $origin_x, int $origin_y, array $raw_data, ?int $frame_width = null, ?int $frame_height = null)` → `setAddressWindow()` → `2C` → `data()`.[^panel]

Window:[^api] `2A x0h x0l x1h x1l`, `2B y0h y0l y1h y1l`; `x0 = x + x_offset`, `x1 = x0 + w − 1`, same for y.

## Piping

All three chips implement gpio/contracts `PipeablePanel` via `ST77xxPipes`.[^pipes] `openWindow(x, y, w, h)` → `setAddressWindow()` → `2C` → DC high (`beginData()`). Bytes then go on `pixelBus()->writeFrom([[address, length], …])`, read straight from memory. `pixelBus()` = the SPI transport when it implements `WritesFromMemory` (Pi spidev, `PosixSPITransport`), else `null` (FT232H). Surface's `DirectEDisplay` drives it: one window + one `writeFrom()` per changed region.

## fill()

`fill(int $red, int $green, int $blue)`, channels 0–255 else `invalidRegisterValue`. Unit from current `formatSpec()->bit_depth`:[^fill]

| Depth | Unit | Bytes |
|---|---|---|
| B12 | pixel pair | `RG BR GB` nibbles; odd count padded |
| B16 | pixel | RGB565 high, low |
| B18 | pixel | `R&FC G&FC B&FC` |

Full window, `2C`, chunks of whole units ≤ `max_packet_size`.

## Mode switching

`setPixelFormat()` / `color_mode` any time → COLMOD + FormatSpec rebuilt → next `fill()` / packer follows.

## Live reference

2026-10-04, 16-bit, 10 MHz, picture checked by eye:

| Bench | Boot | fill() | Full frame | 64×64 region | 10 frames |
|---|---|---|---|---|---|
| FT232H, ST7789 240×320, 2048-byte packets | 228 ms | 280–370 ms | 182–229 ms (153 600 B) | 17 ms | 5.4 fps |
| Pi 5 spidev0.0, ST7796 480×320, 4092-byte packets | 163 ms | 273–278 ms | 273–277 ms (307 200 B) | 8 ms | 3.7 fps |

Pi frame ≈ 307 200 B × 8 / 10 MHz = 246 ms: clock-bound. Packing a 480×320 RGBA8 pattern through the native framebuffer: ~175 ms on the Pi.

## Related

* [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings) · [controllers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/controllers-boot-and-configuration) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/runbooks/hardware-smoke)

[^panel]: ST7789::transmit() / generateFormatSpec()
[^api]: setAddressWindow()
[^fill]: ST77xxFills
[^native]: Surface NativeFramebufferDriver
[^pipes]: ST77xxPipes
