# Changelog

What changed in this package, newest first.

### 2026-10-03
* **Update**: ported to **0.10.0**. `ext-posi` 0.10 is a C rewrite: `Posi\System` / `Posi\Termios` / `Posi\Memory` are gone, replaced by global functions (`posix_*`, `tcgetattr`, `tcsetattr`, `cf*speed`, `tcdrain` / `tcflush` / `tcflow`, `ioctl`, `posi_set_baud_rate`). `microscrap/posix` dropped (absorbed by ext-posi); the package requires only `php` and `ext-posi` `^0.10.0`. `Serial` opens with `O_RDWR | O_NOCTTY | O_CLOEXEC` constants; modem-line methods use `ioctl(..., ['value' => ...], $value)`. Termios arrays carry `c_ispeed` / `c_ospeed` (all seven keys required). Docs URLs and branch alias moved to 0.10.x; suggest `scrapyard-io/framework` `^0.10.0`. README, AGENTS.md and the bundle updated.

### 2026-09-24
* **Update**: relabeled 0.8.0 → 0.9.0 with `ext-posi` / `microscrap/posix` ^0.9.0. No code change.

### 2026-09-14
* **Update**: relabeled 0.7.0 → 0.8.0 with `ext-posi` / `ext-ftdi` 0.8.0. No code change.

## Log

### 2026-08-10

* **Update**: `composer.json` reconciled to **0.7.0** (`php` `^8.4|^8.5|^8.6`, `ext-posi` / `microscrap/posix` `^0.7.0`, `suggest` gpio-framework, homepage/support, branch-alias). README rewritten to open-gl style + `src/` drift fixes (`uart_set_baud_rate`, `BaudRate|int`, `UARTPort::$baud` int, `CSIZE` omission).
* **Creation**: Initial OKF v0.2 bundle for `microscrap/uart` **0.7.0** (gpio microscrap stack; shape mirrored from `microscrap/posix`) from package sources + `okf/SPEC.md` (GoogleCloudPlatform/knowledge-catalog).
* **Creation**: Orientation — [Package (0.7)](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/package-010), [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/ecosystem-docs), [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/uart/orientation/pair-with-protocol-peers).
* **Creation**: Architecture — [Helpers → Termios / posix](/docs/{{version}}/ecosystem/gpio-modules/uart/architecture/helpers-termios-ext).
* **Creation**: Conventions — [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/11-extension-wrap), [Enums for termios flags](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/enums-for-termios-flags).
* **Creation**: Traps — [BaudRate value vs numeric](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/baudrate-value-vs-numeric), [Serial device permissions](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/serial-device-permissions).
* **Creation**: Subdirectory indexes under `orientation/`, `architecture/`, `conventions/`, `traps/`; root [index.md](/docs/{{version}}/ecosystem/gpio-modules/uart/overview).
* **Note**: Root `AGENTS.md` Quick OKF map already matches these concept paths (extra convention + dialout trap are progressive-disclosure additions); all concepts left `status: draft` pending human verification.
