# Changelog

What changed in this package, newest first.

### 2026-10-03
* **Update**: 0.10.0 port. ext-posi 0.10 is a C rewrite exposing global functions; `Posi\System` is gone and `microscrap/posix` is absorbed. `Chip` and `LineRequest` call `posix_open` / `posix_close` / `posix_read` / `posix_ppoll` directly; chips open with `O_RDWR | O_CLOEXEC` constants. Requires only `ext-posi` `^0.10.0`, version 0.10.0, branch alias `0.10.x-dev`, suggest `scrapyard-io/framework` `^0.10.0`, docs URLs `0.10.x`. README, AGENTS, [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/package-010), [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/ecosystem-docs), [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/pair-with-protocol-peers), [Enums for gpiod](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/enums-for-gpiod), [Helpers → gpiod facades → posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi) relabelled. Package enums unchanged. No public helper change.

### 2026-09-14
* **Update**: relabeled 0.7.0 → 0.8.0 with `ext-posi` / `ext-ftdi` 0.8.0. No code change.

## Log

### 2026-08-10

* **Creation**: Initial OKF v0.2 bundle for `microscrap/gpio` 0.7.0 from package sources + `okf/SPEC.md` (GoogleCloudPlatform/knowledge-catalog).
* **Creation**: [Package (0.7)](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/package-010), [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/ecosystem-docs), [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/pair-with-protocol-peers).
* **Creation**: [Helpers → gpiod facades → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi) — helpers → package facades (`Chip`, `LineRequest`, …) → `posix_*` / `Posi\System` ioctl path.
* **Creation**: Conventions — [1:1 libgpiod wrap](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/11-libgpiod-wrap), [Enums for gpiod](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/enums-for-gpiod).
* **Creation**: Traps — [GPIO device permissions](/docs/{{version}}/ecosystem/gpio-modules/gpio/traps/gpio-device-permissions), [`function_exists` load order](/docs/{{version}}/ecosystem/gpio-modules/gpio/traps/function-exists-load-order).
* **Creation**: Subdirectory indexes under `orientation/`, `architecture/`, `conventions/`, `traps/`; root [index.md](/docs/{{version}}/ecosystem/gpio-modules/gpio/overview).
* Pattern mirrored from `microscrap/posix` / `microscrap/mpsse` / `microscrap/open-gl` OKF layout; adapted for libgpiod-style facades + DataObjects over posix/posi.
* Root `AGENTS.md` already present with Quick OKF map — left in place; concept paths match that map.
* All new concepts left `status: draft` pending Angel human verification.

### 2026-09-24
* **Update**: 0.9.0 line. `composer.json` version, `ext-posi` / `microscrap/posix` requires `^0.9.0`, branch alias `0.9.x-dev`, suggest renamed to `scrapyard-io/framework` `^0.9.0`; README and AGENTS version references; [Package (0.9)](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/package-010), [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/ecosystem-docs), [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/pair-with-protocol-peers), [Enums for gpiod](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/enums-for-gpiod), [Helpers → gpiod facades → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi) relabelled. No API change. Needed by `microscrap/scrapyard-linux` 0.9.0, whose Posix DigitalIO driver calls the `gpiod_*` helpers.
