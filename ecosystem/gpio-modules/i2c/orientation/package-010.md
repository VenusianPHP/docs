# Package (0.10)

microscrap/i2c 0.10.0 — Linux i2c-dev / SMBus-style PHP helpers over Bus + ext-posi; no ServiceProvider.

## What it is

Composer package `microscrap/i2c` at **0.10.0** — PHP helpers, enums, and data objects over [**php-io-extensions/posi**](https://github.com/php-io-extensions/posi) (`ext-posi`). Mirrors the Linux i2c-dev / `<linux/i2c-dev.h>` userspace surface (i2c-tools family).[^readme][^composer]

| Field | Value |
|-------|-------|
| Name | `microscrap/i2c`[^composer] |
| Version | `0.10.0`[^composer] |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Microscrap\Bindings\I2C\` → `src/`[^composer] |
| Require | `php`, `ext-posi` `^0.10.0`[^composer] |
| Suggest | `scrapyard-io/framework` `^0.10.0`[^composer] |
| Homepage | Ecosystem docs overview (see [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/ecosystem-docs))[^readme] |
| Discovery | **None** — no provider / Chassis registration in this package[^agents] |
| Role | Bindings layer only (global helpers + `Bus` facade + enums + `I2CBus`)[^agents][^readme] |

Autoloads `src/Helpers/i2c-bus.php` and `src/Helpers/i2c-smbus.php` (each helper guarded with `function_exists`).[^composer][^helpers-bus][^helpers-smbus]

## What it is not

- Not `php-io-extensions/posi` — this package calls its functions for I²C device nodes.[^readme]
- Not a ServiceProvider package — no Chassis / Core / Machine coupling; no Fabricate remaps.[^agents]
- Not `scrapyard-io/gpio-framework` — higher GPIO / bus orchestration sits **above** this package (see [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/pair-with-protocol-peers)).
- Not a full kernel `I2C_SMBUS` ioctl client for the convenience helpers — those are emulated over posix read/write (see [SMBus helpers ≠ I2C_SMBUS ioctl](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/smbus-helpers-i2c-smbus-ioctl)).

## Public surface (summary)

| Layer | Location | Role |
|-------|----------|------|
| Helpers | `src/Helpers/i2c-bus.php`, `i2c-smbus.php` | Global `i2c_*` / `i2c_smbus_*` API |
| Facade | `src/Bus.php` | Static methods; helpers delegate here |
| Data object | `src/DataObjects/I2CBus.php` | `fd`, `path`, `addr` handle |
| Enums | `src/Enums/*` | Linux i2c-dev / SMBus integers as backed enums |
| Lower stack | `ext-posi` | `posix_*`, `ioctl`, `posi_mem_*`, `O_*` constants |

## Related

| Topic | Concept |
|-------|---------|
| Call stack | [Helpers → Bus → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/i2c/architecture/helpers-bus-posix) |
| Wrap rules | [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/11-extension-wrap) |
| Enums | [Enums for kernel constants](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/enums-for-kernel-constants) |
| Protocol peers | [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/pair-with-protocol-peers) |
| Docs site | [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/ecosystem-docs) |
| Extension | `php-io-extensions/posi` 0.10 (functions and constants; no `Posi\System` / `Termios` / `Memory` classes) |

[^composer]: Package name, namespace, autoload helpers
[^readme]: Package README (0.10.x requirements and surface)
[^helpers-bus]: Bus lifecycle / ioctl helper autoload file
[^helpers-smbus]: SMBus convenience helper autoload file
[^agents]: Agent rules for this package
