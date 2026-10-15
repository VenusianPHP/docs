# Package (0.10)

microscrap/spi 0.10.0 — Linux spidev PHP bindings over ext-posi; no ServiceProvider.

## What it is

Composer package `microscrap/spi` at **0.10.0** — PHP helpers, enums, and data objects wrapping Linux `spidev` over [**php-io-extensions/posi**](https://github.com/php-io-extensions/posi) (`ext-posi`).[^readme][^composer]

| Field | Value |
|-------|-------|
| Name | `microscrap/spi`[^composer] |
| Version | `0.10.0`[^composer] |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Microscrap\Bindings\SPI\` → `src/`[^composer] |
| Require | `ext-posi` `^0.10.0` (only requirement besides `php`)[^composer] |
| Suggest | `scrapyard-io/framework` `^0.10.0`[^composer] |
| Homepage | Ecosystem docs overview (see [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/ecosystem-docs))[^readme] |
| Discovery | **None** — no provider / Chassis registration in this package[^agents] |
| Role | Bindings layer only (global helpers + enums + data objects)[^agents][^readme] |

Autoloads `src/Helpers/spi-device.php` (each helper guarded with `function_exists`).[^composer][^helpers]

## What it is not

- Not `php-io-extensions/posi` (the native extension) — this package *uses* that extension via its native `posix_*` / `ioctl` / `posi_mem_*` functions.[^readme]
- Not a ServiceProvider package — no Chassis / Core / Machine coupling; no Fabricate remaps.[^agents]
- Not `scrapyard-io/framework` — application orchestration sits above (see [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/pair-with-protocol-peers)).
- Not the FTDI / MPSSE SPI path — that lives beside in `microscrap/ftdi` / `microscrap/mpsse`.

## Public surface (summary)

| Layer | Location | Role |
|-------|----------|------|
| Helpers | `src/Helpers/spi-device.php` | Global `spi_*` functions |
| Facade | `src/Device.php` | Static methods; `posix_*` / ioctl / transfer paths |
| Enums | `src/Enums/*` | `SPIMode`, `SPIOpCode` from linux spidev.h |
| Data objects | `src/DataObjects/*` | `SPIDevice`, `SPITransfer` |

## Related

| Topic | Concept |
|-------|---------|
| Call stack | [Helpers → Device → posix](/docs/{{version}}/ecosystem/gpio-modules/spi/architecture/helpers-device-posix) |
| Wrap rules | [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/11-extension-wrap) |
| Enums | [Enums for spidev flags](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/enums-for-spidev-flags) |
| Protocol peers | [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/pair-with-protocol-peers) |
| Docs site | [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/ecosystem-docs) |
| Transfer trap | [Native `spi_transfer` vs `posi_mem`](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/native-spi-transfer-vs-posi-mem) |

[^composer]: Package name, namespace, require, suggest, autoload
[^readme]: Package README (0.10.x requirements and surface)
[^helpers]: Global helper autoload file
[^agents]: Agent rules for this package
