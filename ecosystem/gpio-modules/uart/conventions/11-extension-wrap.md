# 1:1 extension wrap

Helpers delegate to Serial / Termios only; keep coverage aligned with uart-serial.php and uart-termios.php.

## Rule

Match peer bindings packages (`microscrap/open-gl`, …) in spirit — thin wrap over the native / FD stack:[^agents][^readme]

1. Global helpers use the names callers expect (`uart_open`, `uart_tcgetattr`, …).
2. Helpers call **`Serial`** or **`Termios`** only — never invent parallel APIs.[^helpers-serial][^helpers-termios][^agents]
3. Facades call ext-posi global functions (`posix_*`, `tc*`, `cf*`, `ioctl`, `posi_set_baud_rate`) only for I/O / termios work.
4. Keep 1:1 coverage with helpers already in `src/Helpers/uart-serial.php` and `uart-termios.php`; document drift in README / ecosystem docs.[^agents]
5. Termios / baud integers live in backed enums — see [Enums for termios flags](/docs/{{version}}/ecosystem/gpio-modules/uart/conventions/enums-for-termios-flags).
6. No ServiceProvider, Chassis/Core coupling, or Fabricate remaps in this package.[^agents]
7. Prefer `is_null($var)` over `$var === null`; no class-level constants.[^agents]

## Architecture link

Full call-stack diagram: [Helpers → Termios / posix](/docs/{{version}}/ecosystem/gpio-modules/uart/architecture/helpers-termios-ext).

[^agents]: Agent wrap rules
[^readme]: Package README wrap description
[^helpers-serial]: Helper → Serial delegation
[^helpers-termios]: Helper → Termios delegation
