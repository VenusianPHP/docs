# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: 0.10 port. [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/overview): 0.10 split requires, `conjure()` through the new `i2c()` factory, catalog slug; Surface HumanInput gone in 0.10, chip enums only; reset write refused by the restarting firmware is ignored.
* **Update**: [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/polling-the-gamepad): `every(Loop)` timer and `stop()` replace the dock; live reference from the Pi. [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/settings-and-config): settings keys in the config file, catalog. [seesaw-protocol](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/seesaw-protocol): SWRST note.
* **Removal**: the three 0.8 warning notes (one-poll edges, reset wait, IRQ priming), folded into [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/polling-the-gamepad) and [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/overview).

### 2026-09-17
* **Update**: [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/overview) — `SeesawMiniGamepad` implements `Surface\Contracts\HumanInput\Circuits\GameController` in place; chip API untouched, parameters widened. `require`: `surface/contracts`; `require-dev`: `surface/human-input`.

### 2026-09-16
* **Update**: [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/polling-the-gamepad) stick directions checked on hardware (right +X, up −Y).
* **Creation**: bundle seeded for 0.8.0 — [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/overview), [seesaw-protocol](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/seesaw-protocol), [polling](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/polling-the-gamepad), [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/seesaw-mini-gamepad/concepts/settings-and-config), three traps.
