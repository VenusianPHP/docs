# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: 0.10 port. [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/overview): 0.10 split requires, `conjure('wii-connector')` through `WiiExtension::i2c()` building the configured controller, catalog slug; Surface HumanInput gone in 0.10, chip enums only.
* **Update**: [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/polling-a-controller): `every(Loop)` timer and `stop()` replace the dock; live reference from the Pi. [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/settings-and-config): catalog, `boot_now`, whole-entry config replacement.
* **Removal**: the four 0.8 warning notes (high-res leftover, identifier prefix, one-poll edges, SNES shoulders on triggers), folded into [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/overview) and [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/polling-a-controller).

### 2026-09-17
* **Update**: [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/overview) — every extension implements Surface `Circuits\ButtonPad`; `WiiClassicController`/`WiiNunchuck` also `Circuits\GameController`. Chip API untouched, widened params only. New require: `surface/contracts`.

### 2026-09-16
* **Update**: [protocol](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/extension-protocol) identifier byte 4 = data format; family check uses bytes 2, 3, 5 (bench SNES stuck at format 3 answered `A4 20 03 01`).
* **Creation**: bundle seeded for 0.8.0 — [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/overview), [protocol](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/extension-protocol), [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/polling-a-controller), [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/wii-connector/concepts/settings-and-config), four traps.
