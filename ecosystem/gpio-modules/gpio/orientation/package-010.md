# Package (0.10)

microscrap/gpio 0.10.0 — bindings-only libgpiod v2 / GPIO uAPI v2 helpers; helpers → facades → posi; no ServiceProvider.

## What it is

Composer package `microscrap/gpio` at **0.10.0** — pure-PHP bindings that mirror [libgpiod v2](https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/) over Linux GPIO character-device uAPI v2, built on **ext-posi**, whose global functions (`posix_open`, `posix_read`, `ioctl`, …) do the FD and ioctl work.[^composer][^readme]

| Field | Value |
|-------|-------|
| Name | `microscrap/gpio` |
| Version | `0.10.0` |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Microscrap\Bindings\GPIO\` → `src/`[^composer] |
| Require | `ext-posi` `^0.10.0` (only dependency besides PHP)[^composer] |
| Suggest | `scrapyard-io/framework` `^0.10.0`[^composer] |
| Homepage | Ecosystem docs overview (see [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/ecosystem-docs))[^composer] |
| Discovery | **None** — no provider / Chassis registration in this package[^readme][^agents] |
| Role | Bindings layer only (helpers + facades + enums + DataObjects)[^helpers-chip][^chip][^readme] |

Autoloads helper files under `src/Helpers/` registering global `gpiod_*` functions, each guarded with `function_exists`.[^composer]

## What it is not

- Not the native **ext-posi** extension — that is `php-io-extensions/posi`.[^readme]
- Not a POSIX helper layer — FD / syscall functions (`posix_*`, `ioctl`, `fcntl`) are native **ext-posi** functions; this package adds GPIO chip / line APIs on top.[^composer]
- Not higher GPIO orchestration / chip drivers — those belong in `scrapyard-io/gpio-framework` (suggested peer).[^composer][^agents]
- Not a ServiceProvider package — no Chassis/Core/Fabricate/Machine coupling.[^readme][^agents]

## Public surface (summary)

| Layer | Location | Role |
|-------|----------|------|
| Helpers | `src/Helpers/gpio-*.php` | Thin globals (`gpiod_chip_open`, `gpiod_line_request_set_value`, …) over facades |
| Facades | `src/Chip.php`, `LineRequest.php`, `LineSettings.php`, … | Static API implementing libgpiod-style operations |
| DataObjects | `src/DataObjects/*` | Chip / line / request / event / uAPI structs |
| Enums | `src/Enums/*` | Direction, edge, bias, drive, clock, value, ioctl opcodes, flags |
| ext-posi | `posix_*` / `ioctl` global functions | FD open/close/read/poll and ioctl underneath facades |

## Related

| Topic | Concept |
|-------|---------|
| Call stack | [Helpers → gpiod facades → posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi) |
| Wrap rules | [1:1 libgpiod wrap](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/11-libgpiod-wrap) |
| Enums | [Enums for gpiod](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/enums-for-gpiod) |
| Peer stack | [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/pair-with-protocol-peers) |
| Docs site | [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/ecosystem-docs) |
| Extension | `ext-posi` 0.10 |

[^composer]: Package name, version, PHP, require, suggest, autoload helpers
[^readme]: Package README
[^helpers-chip]: Global gpiod_chip_* helpers
[^chip]: Chip facade
[^agents]: Agent rules for this package
