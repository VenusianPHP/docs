# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames) piping: ST7735 / ST7789 / ST7796 implement `PipeablePanel` (`openWindow()`, `pixelBus()`) through `ST77xxPipes`; `ST77xxDataTransport` gains `beginData()` and `memoryBus()`. Pinned by `tests/PipeTest.php`.
* **Update**: 0.10 port. [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview): requires 0.10 split components plus `venusian-surface/contracts` and `venusian-voyager/vessel`; no `FormatSpecification` in Surface 0.10; every SPI write checked; new exceptions.
* **Update**: [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/connecting-an-st77xx-panel) rewritten for `conjure()` and `spi()`: container managers, 10 MHz default clock per chip select, configured mode refused on a bus in another, offsets and inversion from config, both benches. [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/wiring-config): `speed`, `x_offset`, `y_offset`, `invert_display`, `protocol`, `boot_now`.
* **Update**: [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings): a `mad_ctrl` write moves width, height and offsets to the new orientation. [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames): packing through a Surface framebuffer; live reference from both benches. [controllers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/controllers-boot-and-configuration): orientation note.
* **Update**: [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview) errors: gamma tables and ST7796 output adjust refuse out-of-range bytes (ST7735 gamma 0–63, others 0–255) instead of masking them.
* **Removal**: the three 0.8 warning notes (MPSSE clock, MADCTL size, unchecked writes): the 0.10 FT232H adapter honours `speed()` and the factory sets it, MADCTL writes carry size and offsets, writes throw on failure.
* **Creation**: [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/runbooks/hardware-smoke) runbook.

### 2026-09-18
* **Update**: [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview) — `ST7735` / `ST7789` / `ST7796` also implement `WindowAddressable` and `Switchable`, the new `DisplayPanel` children in gpio/contracts; `DisplayPanel` itself now carries `transmit()` and extends `FormatSpecification`. Pinned by `tests/ContractsTest.php`; suite 59 passed.

### 2026-09-16
* **Update**: [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames), [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview) — `fillRgb565()` replaced by mode-neutral `fill(r, g, b)` packed from the current FormatSpec; colour mode switching documented.
* **Removal**: traps/fill-is-rgb565 (fill no longer depth-bound); unused `ST77xxCatalogIc`, `ST77xxConsoleCommand`, `ST77xxSmokeColor` enums.
* **Creation**: bundle seeded for 0.8.0 — [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview), [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/connecting-an-st77xx-panel), [controllers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/controllers-boot-and-configuration), [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames), [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings), [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/wiring-config), four traps.
