# Changelog

What changed in this package, newest first.

### 2026-10-03
* **Update**: ported to 0.10.0 on `ext-posi` ^0.10.0 (C rewrite; global functions, no `Posi\*` classes). `microscrap/posix` dropped; `Bus::i2cOpen` opens with the extension's `O_RDWR` constant; `i2c_rdwr` no longer checks `function_exists('posi_mem_alloc')` and returns `false` only when the ioctl fails. Docs URLs now `0.10.x`; suggest `scrapyard-io/framework` ^0.10.0.

### 2026-09-24
* **Update**: relabeled 0.8.0 → 0.9.0 with `ext-posi` / `microscrap/posix` ^0.9.0. No code change.

### 2026-09-14
* **Update**: relabeled 0.7.0 → 0.8.0 with `ext-posi` / `ext-ftdi` 0.8.0. No code change.

## Log

### 2026-08-10

* **Creation**: Initial OKF v0.2 bundle for `microscrap/i2c` **0.7.0** (gpio microscrap stack promotion) from package sources + `okf/SPEC.md` (GoogleCloudPlatform/knowledge-catalog), format-matched to sibling `microscrap/posix`.
* **Creation**: Orientation — [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/package-010), [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/ecosystem-docs), [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/pair-with-protocol-peers).
* **Creation**: Architecture — [Helpers → Bus → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/i2c/architecture/helpers-bus-posix).
* **Creation**: Conventions — [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/11-extension-wrap), [Enums for kernel constants](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/enums-for-kernel-constants).
* **Creation**: Traps — [SMBus helpers ≠ I2C_SMBUS ioctl](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/smbus-helpers-i2c-smbus-ioctl), [`I2CBus::$addr` stale after set_slave](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/i2cbusaddr-stale-after-set-slave), [Need i2c group /dev permissions](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/need-i2c-group-permissions), [`function_exists` load order](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/function-exists-load-order).
* **Creation**: Subdirectory indexes under `orientation/`, `architecture/`, `conventions/`, `traps/`; root [index.md](/docs/{{version}}/ecosystem/gpio-modules/i2c/overview).
* **Creation**: Root `AGENTS.md` with quick OKF map (posix style).
* **Note**: All concepts left `status: draft` pending human verification.
* **Update**: `composer.json` reconciled to **0.7.0** (`php` `^8.4|^8.5|^8.6`, `ext-posi` / `microscrap/posix` `^0.7.0`, `suggest` gpio-framework, homepage/support, branch-alias).
