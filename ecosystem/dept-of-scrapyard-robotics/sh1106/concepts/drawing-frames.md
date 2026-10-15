# Drawing frames

FormatSpec, packing frames with a Surface framebuffer, page-only transmit(), column offset, live timings.

## FormatSpec

`formatSpec()` → `MONO_VERTICAL_PAGE`, `B1`, `TOP_TO_BOTTOM`, `LSB_FIRST`, `PageAxis::VERTICAL`.[^panel] Type from `venusian-surface/contracts`.[^formatspec] Surface 0.10 has no `FormatSpecification` interface; the panel keeps `formatSpec()` / `setFormatSpec()` / `generateFormatSpec()` as plain methods.

## Packing

1 byte = 1 column × 1 page (8 rows). Bit 0 = page's top row. Order: page 0..N, within page column 0..W. 128×64 = 1024 bytes.

A Surface framebuffer (`venusian-surface/framebuffers`) packs it:[^native]

```php
$spec = $panel->formatSpec();
$fb = (new NativeFramebufferDriver)->full($spec, $panel->width(), $panel->height());
$fb->setSegment(4, 4, 16, 16, 1);
$panel->transmit(0, 0, $fb->flush($spec, true));

$region = new Region(48, 24, 32, 16);
$panel->transmit($region->x, $region->y, $fb->flushRegion($region, $spec, true), $region->width, $region->height);
```

`flushRegion()` answers page-major rows, the order `transmit()` takes.

## transmit()

`transmit(int $origin_x, int $origin_y, array $raw_data, ?int $frame_width = null, ?int $frame_height = null)`.[^panel] SH1106 addresses RAM by page only: no addressing modes, no column/page window. Per page of the region: `setPagePosition(x, page)` → `0x0L`, `0x1H` of `x + column_offset`, `0xB0 | page` → `data(row of w bytes)`.[^api] Rows page-aligned; stops after the region's last page; rest of the panel untouched (`WindowAddressable`).

## Column offset

132 RAM columns; 128-pixel glass centred → panel x 0 = RAM column 2. `column_offset` (default 2) added in `setPagePosition()`. Wrong offset shows as a missing or shifted side edge; a full border is the check. Module with glass at column 0 → `column_offset: 0`.

## Live reference

2026-10-04, 128×64, 1024-byte packets, picture checked by eye (border all four edges, X, square, region bar):

| Bench | Boot | Full frame | 16×8 region |
|---|---|---|---|
| FT232H I2C, 0x3C, `usb` | 170 ms (100 ms DC-DC settle) | 194 ms | 15 ms |

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/connecting-an-sh1106) · [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/panel-settings) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/runbooks/hardware-smoke)

[^panel]: SH1106::transmit() / formatSpec()
[^api]: SH1106API::setPagePosition()
[^formatspec]: Surface FormatSpec
[^native]: Surface NativeFramebufferDriver
