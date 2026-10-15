# Drawing frames

FormatSpec, packing frames with a Surface framebuffer, transmit() windows per addressing mode, live timings on both benches.

## FormatSpec

`formatSpec()` → `MONO_VERTICAL_PAGE`, `B1`, `TOP_TO_BOTTOM`, `LSB_FIRST`, `PageAxis::VERTICAL`. One spec for every addressing mode; caller packs the same bytes whatever the mode.[^panel] Type from `venusian-surface/contracts`.[^formatspec] Surface 0.10 has no `FormatSpecification` interface; the panel keeps `formatSpec()` / `setFormatSpec()` / `generateFormatSpec()` as plain methods.

## Packing

1 byte = 1 column × 1 page (8 rows). Bit 0 = page's top row. Order: page 0..N, within page column 0..W. 128×64 = 1024 bytes.

A Surface framebuffer (`venusian-surface/framebuffers`) packs it:[^native]

```php
$spec = $panel->formatSpec();
$fb = (new NativeFramebufferDriver)->full($spec, $panel->width(), $panel->height());
$fb->setSegment(2, 2, 8, 8, 1);
$panel->transmit(0, 0, $fb->flush($spec, true));

$region = new Region(48, 24, 32, 16);
$panel->transmit($region->x, $region->y, $fb->flushRegion($region, $spec, true), $region->width, $region->height);
```

`flushRegion()` answers page-major rows, the order `transmit()` takes.

## transmit()

`transmit(int $origin_x, int $origin_y, array $raw_data, ?int $frame_width = null, ?int $frame_height = null)`, per addressing mode:[^panel]

| Mode | Traffic |
|---|---|
| horizontal | `setAddressWindow()` → `data(bytes)` |
| vertical | `setAddressWindow()` → `data(bytes reordered column-major)` |
| page | per page: `setPagePosition(x, page)` (`0x0L`, `0x1H`, `0xB0 \| page`) → `data(row)` |

Window:[^api] `21 x, x+w-1` · `22 y>>3, (y+h-1)>>3`. Rows page-aligned. Byte count = w × pages. `INVALID` mode refused by `setMemoryAddressingMode()`.

## Live reference

2026-10-04, 128×64, 1024-byte packets, picture checked by eye in all three modes:

| Bench | Boot | Full frame | 32×16 region | 20 frames |
|---|---|---|---|---|
| Pi 5, I2C bus 1, 0x3C, `native` | 8.3 ms | 28.8 ms | 2.5 ms | 34.8 fps |
| FT232H SPI, CS D4, DC D5, RST D6, `usb`, 10 MHz | 93–98 ms (RST pulse) | 5.8–9.3 ms | 6.6–7.8 ms | 168–173 fps |

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/connecting-an-ssd1306) · [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/panel-settings) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/runbooks/hardware-smoke)

[^panel]: SSD1306::transmit() / formatSpec()
[^api]: SSD1306API::setAddressWindow() / setPagePosition()
[^formatspec]: Surface FormatSpec
[^native]: Surface NativeFramebufferDriver
