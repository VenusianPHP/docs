# BaudRate value vs numeric

BaudRate::value is POSIX speed_t; uart_open / UARTPort::$baud use numeric rates (case name or plain int).

## Symptom

Baud is wrong after open/set (e.g. you pass `BaudRate::B115200->value` expecting 115200, but `speed_t` is `4098`), or you store `BaudRate::value` on `UARTPort::$baud` and later treat it as bits-per-second.

## Cause

Two different integers share the word “baud” in this package:[^agents][^readme][^baud]

| Symbol | Meaning | Example (`B115200`) |
|--------|---------|---------------------|
| `BaudRate::value` | POSIX / Linux **`speed_t`** constant | `4098` |
| Numeric rate | Actual bits/sec (or BOTHER rate) | `115200` |
| `UARTPort::$baud` | **Numeric** rate stored at open | `115200`[^port] |

`uart_open` / `uart_set_baud_rate` accept `BaudRate|int` and convert enum cases by stripping the leading `B` from the **case name**, then call `posi_set_baud_rate($fd, $baudInt)`. Plain `int` arguments take the Linux **BOTHER** / termios2 path.[^serial][^readme]

By contrast, `uart_cfsetispeed` / `uart_cfsetospeed` pass **`BaudRate::value`** (`speed_t`) into `cfsetispeed` / `cfsetospeed`.[^termios-facade]

`uart_cfgetispeed` / `uart_cfgetospeed` return `BaudRate|null` via `BaudRate::tryFrom(speed_t)` — non-standard BOTHER rates may not decode to an enum case.[^termios-facade]

## Mitigation

- Prefer passing `BaudRate::B115200` (or a plain numeric `int`) into `uart_open` / `uart_set_baud_rate` — do **not** pass `BaudRate::B115200->value` expecting 115200 bps.[^serial]
- Treat `UARTPort::$baud` as numeric bps for application logic.[^agents][^port]
- Use `uart_cfset*` / `uart_cfget*` when working with classic `speed_t` fields inside a termios array; use the `posi_set_baud_rate` path for BOTHER / arbitrary rates.[^readme]

## Related

* [Helpers → Termios / posix](/docs/{{version}}/ecosystem/gpio-modules/uart/architecture/helpers-termios-ext)
* [Enums for termios flags](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/enums-for-termios-flags)

[^agents]: UARTPort::$baud vs BaudRate::value
[^readme]: BaudRate values are speed_t; open accepts int for BOTHER
[^serial]: BaudRate → numeric via case name strip; posi_set_baud_rate path
[^termios-facade]: cfset* uses BaudRate::value
[^port]: UARTPort::$baud is int numeric rate
[^baud]: speed_t case values
