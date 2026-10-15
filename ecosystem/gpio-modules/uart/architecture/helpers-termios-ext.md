# Helpers termios ext

Global uart_* helpers call Serial / Termios facades; those call ext-posi global functions.

## Call stack

```
app / peers / tests
    │
    ├─ uart_open / uart_read / uart_write / …   # uart-serial.php
    │       └─► Serial::*
    │               ├─► posix_open / posix_read / posix_write / posix_close
    │               ├─► tcgetattr / tcsetattr / posi_set_baud_rate / tcdrain / tcflush / tcflow
    │               └─► ioctl  (modem lines)
    │
    └─ uart_tcgetattr / uart_cfsetispeed / …   # uart-termios.php
            └─► Termios::*
                    └─► tcgetattr / tcsetattr / cfsetispeed / cfsetospeed / cfgetispeed / cfgetospeed
```

Rules:[^agents][^readme][^helpers-serial]

1. Helpers call `Serial` / `Termios` only.
2. Facades call ext-posi global functions only (`posix_*`, `tc*`, `cf*`, `ioctl`, `posi_set_baud_rate`) — do not invent parallel APIs.
3. Keep 1:1 coverage with helpers already in `uart-serial.php` / `uart-termios.php`; document drift in README / ecosystem docs.[^agents]

## Autoload

Composer `autoload.files` registers:[^composer]

- `src/Helpers/uart-serial.php`
- `src/Helpers/uart-termios.php`

Each function is wrapped in `if (! function_exists(...))` so a prior definition wins.[^helpers-serial][^helpers-termios]

## Helper groups (0.10 surface)

| Group | Helpers | Facade | Downstream |
|-------|---------|--------|------------|
| Lifecycle / I/O | `uart_open`, `uart_set_baud_rate`, `uart_close`, `uart_read`, `uart_write` | `Serial` | `posix_*` + `posi_set_baud_rate` / raw setup[^serial] |
| Queue / flow | `uart_drain`, `uart_flush`, `uart_flow` | `Serial` | `tcdrain` / `tcflush` / `tcflow`[^serial] |
| Modem lines | `uart_set_modem_line`, `uart_clear_modem_line`, `uart_modem_lines` | `Serial` | `ioctl($fd, $request, ['value' => ...], $value)` with `TIOCMBIS` / `TIOCMBIC` / `TIOCMGET`; the returned int is tested, `< 0` gives -1[^serial] |
| Raw mode | `uart_make_raw` | `Serial::makeRaw` | PHP-side `cfmakeraw` semantics on a `tcgetattr()` array, edited in place so `c_ispeed` / `c_ospeed` are kept[^serial] |
| Attributes | `uart_tcgetattr`, `uart_tcsetattr` | `Termios` | `tcgetattr` / `tcsetattr`[^termios-facade] |
| Speeds | `uart_cfsetispeed`, `uart_cfsetospeed`, `uart_cfgetispeed`, `uart_cfgetospeed` | `Termios` | `cfsetispeed` / `cfsetospeed` / `cfgetispeed` / `cfgetospeed` + `BaudRate`[^termios-facade] |

## `uart_open` defaults

Automatic configuration (override via `uart_tcgetattr` / mutate / `uart_tcsetattr`):[^readme][^serial]

- Open flags: `O_RDWR | O_NOCTTY | O_CLOEXEC` (constants registered by ext-posi)
- `cfmakeraw` semantics via `Serial::makeRaw`
- `VMIN=1`, `VTIME=0`
- Apply with `TCSANOW`
- Baud via `posi_set_baud_rate` (enum cases → numeric rate from case name; plain `int` uses Linux BOTHER path)

## Baud handling note

`uart_open` / `uart_set_baud_rate` accept `BaudRate|int`. Enum cases are converted to a **numeric** rate by stripping the leading `B` from the case name — **not** by using `BaudRate::value` (`speed_t`). See [BaudRate value vs numeric](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/baudrate-value-vs-numeric).[^serial]

`uart_cfsetispeed` / `uart_cfsetospeed` pass `BaudRate::value` (`speed_t`) into `cfsetispeed` / `cfsetospeed`.[^termios-facade]

## Termios array

ext-posi termios arrays carry seven keys: `c_iflag`, `c_oflag`, `c_cflag`, `c_lflag`, `c_cc` (all `NCCS` indices), `c_ispeed`, `c_ospeed`. Every ext-posi function taking one requires all seven and throws `ValueError` on a missing key. Edit the `tcgetattr()` result rather than building an array. A Linux `BOTHER` custom rate survives a `tcgetattr` → `tcsetattr` round trip.[^serial][^termios-facade]

## Errors / style

- C-style return codes (`null` / `-1` / `false` on failure) — no exceptions from helpers in this package’s wrap.[^readme]
- Prefer `is_null($var)` over `$var === null` in package code.[^agents]

## Related

* [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/11-extension-wrap)
* [Enums for termios flags](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/enums-for-termios-flags)
* [BaudRate value vs numeric](/docs/{{version}}/ecosystem/gpio-modules/uart/traps/baudrate-value-vs-numeric)

[^helpers-serial]: Serial helpers → Serial facade
[^helpers-termios]: Termios helpers → Termios facade
[^serial]: Serial facade (ext-posi functions)
[^termios-facade]: Termios facade (ext-posi functions)
[^composer]: Autoload files list
[^readme]: Helper API tables and defaults
[^agents]: Helpers call Serial / Termios only
