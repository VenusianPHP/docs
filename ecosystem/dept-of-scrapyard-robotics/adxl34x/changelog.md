# Changelog

What changed in this package, newest first.

### 2026-10-04

* **Update**: 0.10 port. [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/overview): requires the 0.10 split components plus `venusian-voyager/contracts` and `vessel`; boot waits for the first fresh sample; new exceptions.
* **Creation**: [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/connecting) rewritten for `conjure()` and the `i2c()` / `spi()` factories (SPI mode 3, ≤ 5 MHz, shared buses, INT pins after the bus).
* **Update**: [interrupts](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/interrupts): `every(Loop, interval)` loop timer and `stop()` replace the dock recurrence; shared-INT-line note resolved by gpio/digital's per-pin queue; live reference from both benches.
* **Update**: [chip-settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/chip-settings): `SLEEP_3HZ` renamed `SLEEP_1HZ`. [configuration](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/configuration): `spi.speed`, `protocol`, conjure semantics.
* **Deprecation**: `dock-sampling` removed: 0.10 has no dock. The 0.8 bundle's separate warning notes folded into [reading](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/reading), [chip-settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/chip-settings) and [interrupts](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/interrupts).
* **Creation**: [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/runbooks/hardware-smoke) runbook.
