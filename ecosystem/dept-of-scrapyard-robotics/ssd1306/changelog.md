# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: 0.10 port. [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/overview): requires 0.10 split components plus `venusian-surface/contracts` and `venusian-voyager/vessel`; catalog slug; every bus write checked; new exceptions.
* **Update**: [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/connecting-an-ssd1306) rewritten for `conjure()` and the `i2c()` / `spi()` factories (SPI mode 0 or 3, ≤ 10 MHz, DC and RST after the bus). [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/wiring-config): `spi.speed`, `panel`, `protocol`, `boot_now`.
* **Update**: [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/panel-settings): one name per setting, read and write, equal to its configuration key. [configuration-object](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/ssd1306configuration): `alternative_com_pins` replaces `sequential_com_pin_config`, defaults from height; `fromArray()`.
* **Update**: [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/drawing-frames): packing through a Surface framebuffer; `FormatSpecification` gone from Surface 0.10; live reference from both benches.
* **Removal**: the three 0.8 warning notes (COM pins naming, read/write property name pairs, unchecked writes): the code now names bit 4 for what it does, uses one property name per setting, and throws on a failed write.
* **Creation**: [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/runbooks/hardware-smoke) runbook.

### 2026-09-18
* **Update**: [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/overview) — `SSD1306` also implements `WindowAddressable` (transmit honours the window) and `Switchable` (`setDisplay(bool)`), the new `DisplayPanel` children in gpio/contracts; `DisplayPanel` itself now carries `transmit()` and extends `FormatSpecification`. Pinned by a contract test in `tests/SSD1306Test.php`; suite 26 passed.

### 2026-09-16
* **Update**: [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/drawing-frames) transmit() works in horizontal, vertical and page addressing with one FormatSpec; [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/overview) `invalidAddressingMode` replaces the FormatSpec exception.
* **Removal**: traps/horizontal-addressing-only (no longer true).
* **Creation**: bundle seeded for 0.8.0 — [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/overview), [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/connecting-an-ssd1306), [configuration-object](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/ssd1306configuration), [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/drawing-frames), [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/panel-settings), [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/wiring-config), four traps.
