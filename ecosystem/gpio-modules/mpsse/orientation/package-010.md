# Package (0.10)

microscrap/mpsse 0.10.0 — bindings-only MPSSE SPI/I2C/GPIO helpers; helpers → MPSSE → FTDI; no ServiceProvider.

## What it is

Composer package `microscrap/mpsse` at **0.10.0** — pure-PHP MPSSE SPI / I²C / GPIO helpers modeled on [libmpsse](https://github.com/devttys0/libmpsse), built on **ext-ftdi**'s native `ftdi_*` functions.[^composer][^readme]

| Field | Value |
|-------|-------|
| Name | `microscrap/mpsse` |
| Version | `0.10.0` |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Microscrap\Bindings\MPSSE\` → `src/`[^composer] |
| Require | `ext-ftdi` `^0.10.0`[^composer] |
| Suggest | `scrapyard-io/framework` `^0.10.0`[^composer] |
| Homepage | Ecosystem docs overview (see [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/mpsse/orientation/ecosystem-docs))[^composer] |
| Discovery | **None** — no provider / Chassis registration in this package[^readme] |
| Role | Bindings layer only (helpers + `MPSSE` wrapper + enums + `MPSSEContext`)[^helpers][^mpsse][^readme] |

Autoloads `src/Helpers/mpsse.php` global `mpsse_*` helpers, each guarded with `function_exists`.[^composer][^helpers]

## What it is not

- Not the native **ext-ftdi** extension — that is `php-io-extensions/ftdi`.[^readme]
- Not a wrapper over `microscrap/ftdi` — that package no longer exists; ext-ftdi 0.10 absorbed it, and its enums are `Ftdi\FtdiVendorId` / `Ftdi\FtdiProductId`.[^composer]
- Not higher UART/USB/MPSSE adapters — those belong in `scrapyard-io/framework` (suggested peer).[^composer]
- Not a ServiceProvider package — no Chassis/Core/Fabricate/Machine coupling.[^readme][^agents]

## Public surface (summary)

| Layer | Location | Role |
|-------|----------|------|
| Helpers | `src/Helpers/mpsse.php` | Thin globals (`mpsse_open`, pin helpers, …) over `MPSSE` |
| Wrapper | `src/MPSSE.php` | Static API — pure-PHP libmpsse port |
| Context | `src/MPSSEContext.php` | Package-owned session object (holds `?Ftdi\FTDIContext`) |
| Enums | `src/Enums/*` | Mode, interface, endianness, clock, command, ACK, pins, devices |
| FTDI | ext-ftdi `ftdi_*` global functions | Used underneath by `MPSSE` |

## Related

| Topic | Concept |
|-------|---------|
| Call stack | [Helpers → MPSSE → FTDI](/docs/{{version}}/ecosystem/gpio-modules/mpsse/architecture/helpers-mpsse-ftdi) |
| Wrap rules | [1:1 libmpsse wrap](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/11-libmpsse-wrap) |
| Enums | [Enums for MPSSE](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/enums-for-mpsse) |
| Docs site | [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/mpsse/orientation/ecosystem-docs) |
| Peers | `microscrap/gpio`, `i2c`, `spi`, `uart` 0.10.0 |

[^composer]: Package name, version, PHP, require, autoload helpers
[^readme]: Package README
[^helpers]: Global mpsse_* helpers
[^mpsse]: Package MPSSE static wrapper
[^agents]: Agent rules for this package
