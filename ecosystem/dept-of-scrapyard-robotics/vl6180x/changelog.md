# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: 0.10 port. [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/overview): 0.10 split requires, catalog slug, `notConnected`. [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/connecting-a-vl6180x) rewritten for `conjure()` and `VL6180X::i2c()`. [configuration](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/wiring-config): catalog, `boot_now`.
* **Update**: [ranging](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/ranging): live reference on the FT232H with GPIO1 and XSHUT.
* **Removal**: the four 0.8 warning notes (fresh out of reset, GPIO1 polarity, range error first, wait-path fallback), folded into [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/overview), [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/connecting-a-vl6180x) and [ranging](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/ranging).

### 2026-09-16
* **Update**: [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/connecting-a-vl6180x) FT232H pins GPIO1 → GPIOL1, XSHUT → GPIOL2; [ranging](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/ranging) measured status-read counts per path.
* **Creation**: bundle seeded for 0.8.0 — [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/overview), [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/connecting-a-vl6180x), [ranging](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/ranging), [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/settings), [configuration](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/concepts/wiring-config), four traps.
