# Package (0.10)

microscrap/uart 0.10.0 — UART/serial PHP helpers over ext-posi global functions; no ServiceProvider.

## What it is

Composer package `microscrap/uart` at **0.10.0** — PHP helpers, facades, enums, and `UARTPort` over the global functions of [**php-io-extensions/posi**](https://github.com/php-io-extensions/posi) 0.10 (`posix_*`, `tcgetattr`, `tcsetattr`, `ioctl`, `posi_set_baud_rate`, ...).[^readme][^agents]

| Field | Value |
|-------|-------|
| Name | `microscrap/uart`[^composer] |
| Version | `0.10.0`[^composer] |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Microscrap\Bindings\UART\` → `src/`[^composer] |
| Require | `php`; `ext-posi` `^0.10.0`[^composer] |
| Suggest | `scrapyard-io/framework` `^0.10.0` |
| Homepage | Ecosystem docs overview (see [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/ecosystem-docs))[^readme] |
| Source | https://github.com/microscrap/uart |
| Discovery | **None** — no provider / Chassis registration in this package[^agents] |
| Role | Bindings layer only (global helpers + facades + enums + DTO)[^agents][^readme] |

Autoloads `src/Helpers/uart-serial.php` and `src/Helpers/uart-termios.php` (each helper guarded with `function_exists`).[^composer][^readme]

## What it is not

- Not `php-io-extensions/posi` (the native extension) — this package *wraps* its global functions.[^readme]
- Not a ServiceProvider package — no Chassis / Core / Machine coupling; no Fabricate remaps.[^agents]
- Not a POSIX FD package — FD open/read/write are native ext-posi functions (see [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/pair-with-protocol-peers)).
- Not GPIO / I2C / SPI — those are peer protocol packages.

## Public surface (summary)

| Layer | Location | Role |
|-------|----------|------|
| Helpers | `src/Helpers/uart-serial.php`, `uart-termios.php` | Global `uart_*` API |
| Facades | `src/Serial.php`, `src/Termios.php` | Static methods helpers call |
| Data object | `src/DataObjects/UARTPort.php` | `int $fd`, `string $path`, `int $baud` (numeric rate) |
| Enums | `src/Enums/*` | Baud / termios flag / action integers |
| Extension | ext-posi global functions (`posix_*`, `tcgetattr`, `ioctl`, ...) | Native targets — not reimplemented here |

## Related

| Topic | Concept |
|-------|---------|
| Call stack | [Helpers → Termios / posix](/docs/{{version}}/ecosystem/gpio-modules/uart/architecture/helpers-termios-ext) |
| Wrap rules | [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/11-extension-wrap) |
| Enums | [Enums for termios flags](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/enums-for-termios-flags) |
| Protocol peers | [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/pair-with-protocol-peers) |
| Docs site | [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/ecosystem-docs) |
| Baud trap | [BaudRate value vs numeric](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/baudrate-value-vs-numeric) |

[^composer]: Package name, namespace, autoload helpers
[^readme]: Package README (0.10.x requirements and surface)
[^agents]: Agent rules for this package
