# Overview

> Docs (production): ScrapyardIO · microscrap/uart 0.10.x

> **Docs (production):** [ScrapyardIO · microscrap/uart 0.10.x](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/uart/0.10.x/overview)

[![Docs](https://img.shields.io/badge/docs-ScrapyardIO-0ea5e9?logo=readthedocs&logoColor=white)](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/uart/0.10.x/overview)
[![Packagist Version](https://img.shields.io/packagist/v/microscrap/uart.svg?label=packagist)](https://packagist.org/packages/microscrap/uart)
[![PHP Version Require](https://img.shields.io/packagist/php-v/microscrap/uart.svg)](https://packagist.org/packages/microscrap/uart)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/microscrap/uart/tree/HEAD/LICENSE)
[![Requires ext-posi](https://img.shields.io/badge/ext--posi-%5E0.10-777bb4?logo=php&logoColor=white)](https://github.com/php-io-extensions/posi)

PHP library that wraps the [**posi**](https://github.com/php-io-extensions/posi) extension's global functions (`posix_*` FD calls, `tcgetattr`, `tcsetattr`, `posi_set_baud_rate`, ...) with global helpers, enums, and data objects. Every helper delegates to a facade class under `Microscrap\Bindings\UART`.

This is the **bindings** package — not the native extension. Ecosystem docs: [`0.10.x`](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/uart/0.10.x/overview).

## Highlights

* Open a serial device (`/dev/ttyUSB0`, `/dev/ttyAMA0`, etc.) and configure it in one call
* Automatic raw-mode setup (`cfmakeraw` semantics) — no line buffering, no character processing
* Typed `BaudRate` enum covers the full `speed_t` range from `B50` to `B4000000`
* `uart_open` / `uart_set_baud_rate` also accept plain `int` rates (Linux BOTHER / termios2 path)
* Enum-typed termios flag sets for `c_iflag`, `c_oflag`, `c_cflag`, `c_lflag`, and `c_cc`
* Full termios attribute inspection and mutation via `uart_tcgetattr` / `uart_tcsetattr`
* Drain, flush, and flow control through `uart_drain`, `uart_flush`, `uart_flow`
* Thin global `uart_*` helper API — all functions are `function_exists`-guarded

## Requirements

* PHP `^8.4|^8.5|^8.6`
* Linux kernel (any modern version with `/dev/tty*` devices)
* **ext-posi** `^0.10.0` — install from [php-io-extensions/posi](https://github.com/php-io-extensions/posi)

## Installation

Confirm **ext-posi** is loaded:

```bash
php -m | grep posi
```

```bash
composer require microscrap/uart:^0.10.0
```

The package requires only `php` and **ext-posi**. Autoloads `src/Helpers/uart-serial.php` and `src/Helpers/uart-termios.php`, registering the global `uart_*` functions.

## Usage

Serial I/O is controlled through **global helper functions** (`uart_open`, `uart_write`, `uart_read`, `uart_set_baud_rate`, etc.). All helpers delegate to facade classes and are only defined once (`function_exists` guard).

Enums live under `Microscrap\Bindings\UART\Enums` — cases are **FULLY UPPERCASE**. The port handle is `Microscrap\Bindings\UART\DataObjects\UARTPort` (`int $fd`, `string $path`, `int $baud`).

---

### Example — send a command and read the response

```php
<?php

use Microscrap\Bindings\UART\Enums\BaudRate;
use Microscrap\Bindings\UART\Enums\TermiosQueue;

// Open /dev/ttyUSB0 at 115200 baud, configured for raw byte I/O.
$port = uart_open('/dev/ttyUSB0', BaudRate::B115200);
if (is_null($port)) {
    exit("Failed to open port\n");
}

// Discard stale data before starting.
uart_flush($port, TermiosQueue::TCIOFLUSH);

// Send a command.
uart_write($port, "AT\r\n");

// Block until all bytes have been clocked out.
uart_drain($port);

// Wait briefly then read the response.
usleep(50_000);
$response = uart_read($port, 128);
echo "Response: " . trim($response) . "\n";

uart_close($port);
```

---

### Example — non-standard baud (Linux BOTHER)

```php
<?php

use Microscrap\Bindings\UART\Enums\BaudRate;

// Plain integers use the Linux BOTHER / termios2 path inside ext-posi.
$port = uart_open('/dev/ttyUSB0', 256000);
if (is_null($port)) {
    exit("Failed to open port\n");
}

uart_set_baud_rate($port, BaudRate::B115200);
uart_close($port);
```

---

### Example — manual termios configuration

```php
<?php

use Microscrap\Bindings\UART\Enums\BaudRate;
use Microscrap\Bindings\UART\Enums\ControlChar;
use Microscrap\Bindings\UART\Enums\ControlFlag;
use Microscrap\Bindings\UART\Enums\TermiosAction;

$port = uart_open('/dev/ttyAMA0', BaudRate::B9600);

// Read, mutate, and reapply termios attributes.
$t = uart_tcgetattr($port);

// Enable hardware flow control.
$t['c_cflag'] |= ControlFlag::CRTSCTS->value;

// Require at least 4 bytes per read() call.
$t['c_cc'][ControlChar::VMIN->value] = 4;

uart_tcsetattr($port, $t, TermiosAction::TCSADRAIN);

uart_close($port);
```

---

## API Reference

### Serial port lifecycle

| Helper | Facade method | Description |
|---|---|---|
| `uart_open(string $path, BaudRate\|int $baud = BaudRate::B9600)` | `Serial::uartOpen` | Open and configure a port; returns `UARTPort\|null` |
| `uart_set_baud_rate(UARTPort $port, BaudRate\|int $baud)` | `Serial::uartSetBaudRate` | Change baud on an open port |
| `uart_close(UARTPort $port)` | `Serial::uartClose` | Close the file descriptor; returns 0 or -1 |
| `uart_read(UARTPort $port, int $bytes)` | `Serial::uartRead` | Read up to `$bytes` bytes; returns `string\|false` |
| `uart_write(UARTPort $port, string $data)` | `Serial::uartWrite` | Write `$data`; returns bytes written |
| `uart_drain(UARTPort $port)` | `Serial::uartDrain` | Block until TX FIFO is empty (`tcdrain`) |
| `uart_flush(UARTPort $port, TermiosQueue $queue = TermiosQueue::TCIOFLUSH)` | `Serial::uartFlush` | Discard queued I/O (`tcflush`) |
| `uart_flow(UARTPort $port, TermiosFlow $action)` | `Serial::uartFlow` | Suspend / resume I/O (`tcflow`) |
| `uart_make_raw(array $termios)` | `Serial::makeRaw` | Apply `cfmakeraw` semantics to a termios array |
| `uart_set_modem_line(UARTPort $port, ModemLine $line)` | `Serial::uartSetModemLine` | Assert a modem line (`TIOCMBIS`); returns 0 or -1 |
| `uart_clear_modem_line(UARTPort $port, ModemLine $line)` | `Serial::uartClearModemLine` | Release a modem line (`TIOCMBIC`); returns 0 or -1 |
| `uart_modem_lines(UARTPort $port)` | `Serial::uartModemLines` | Modem line state as `TIOCM_*` bits (`TIOCMGET`), or -1 |

### Termios attribute access

| Helper | Facade method | Description |
|---|---|---|
| `uart_tcgetattr(UARTPort $port)` | `Termios::uartTcgetattr` | Read current attributes; returns `array\|false` |
| `uart_tcsetattr(UARTPort $port, array $t, TermiosAction $a = TermiosAction::TCSANOW)` | `Termios::uartTcsetattr` | Apply attributes; returns 0 or -1 |
| `uart_cfsetispeed(array $t, BaudRate $baud)` | `Termios::uartCfsetispeed` | Set input baud; returns new `array\|false` |
| `uart_cfsetospeed(array $t, BaudRate $baud)` | `Termios::uartCfsetospeed` | Set output baud; returns new `array\|false` |
| `uart_cfgetispeed(array $t)` | `Termios::uartCfgetispeed` | Decode input baud; returns `BaudRate\|null` |
| `uart_cfgetospeed(array $t)` | `Termios::uartCfgetospeed` | Decode output baud; returns `BaudRate\|null` |

### `UARTPort` data object

```php
final readonly class UARTPort {
    public int    $fd;    // open file descriptor
    public string $path;  // device path (/dev/ttyUSB0)
    public int    $baud;  // numeric rate (e.g. 115200), not BaudRate::value
}
```

---

## Termios array format

`uart_tcgetattr` returns — and `uart_tcsetattr` / `uart_cfset*speed` consume — a plain PHP array:

```php
[
    'c_iflag' => int,       // InputFlag bitmask
    'c_oflag' => int,       // OutputFlag bitmask
    'c_cflag' => int,       // ControlFlag bitmask (includes baud rate bits)
    'c_lflag' => int,       // LocalFlag bitmask
    'c_cc'    => int[],     // ControlChar indexed array (NCCS elements)
    'c_ispeed' => int,      // input speed
    'c_ospeed' => int,      // output speed
]
```

All seven keys are required by every ext-posi function that takes a termios array; a missing key throws `ValueError`. Edit the array `uart_tcgetattr` returns rather than building one by hand. A Linux `BOTHER` custom rate survives a `uart_tcgetattr` → `uart_tcsetattr` round trip.

---

## Enum quick reference

### `BaudRate`

`B0`, `B50`, `B75`, `B110`, `B134`, `B150`, `B200`, `B300`, `B600`, `B1200`, `B1800`, `B2400`, `B4800`, `B9600`, `B19200`, `B38400`, `B57600`, `B115200`, `B230400`, `B460800`, `B500000`, `B576000`, `B921600`, `B1000000`, `B1152000`, `B1500000`, `B2000000`, `B2500000`, `B3000000`, `B3500000`, `B4000000`

Enum **values** are POSIX `speed_t` constants. `uart_open` / `uart_set_baud_rate` convert cases to numeric rates via the case name (strip leading `B`).

### `TermiosAction`

| Case | Value | When settings take effect |
|---|---|---|
| `TCSANOW` | 0 | Immediately |
| `TCSADRAIN` | 1 | After all output is transmitted |
| `TCSAFLUSH` | 2 | After output drained and input discarded |

### `TermiosQueue`

| Case | Value | What `tcflush` discards |
|---|---|---|
| `TCIFLUSH` | 0 | Received but unread input |
| `TCOFLUSH` | 1 | Written but untransmitted output |
| `TCIOFLUSH` | 2 | Both queues |

### `TermiosFlow`

| Case | Value | Effect |
|---|---|---|
| `TCOOFF` | 0 | Suspend output |
| `TCOON` | 1 | Resume output |
| `TCIOFF` | 2 | Send STOP character to device |
| `TCION` | 3 | Send START character to device |

### `InputFlag` — `c_iflag` bits

`IGNBRK`, `BRKINT`, `IGNPAR`, `PARMRK`, `INPCK`, `ISTRIP`, `INLCR`, `IGNCR`, `ICRNL`, `IUCLC`, `IXON`, `IXANY`, `IXOFF`, `IMAXBEL`, `IUTF8`

### `OutputFlag` — `c_oflag` bits

`OPOST`, `OLCUC`, `ONLCR`, `OCRNL`, `ONOCR`, `ONLRET`, `OFILL`, `OFDEL`

### `ControlFlag` — `c_cflag` bits

`CBAUD`, `CBAUDEX`, `CS5`, `CS6`, `CS7`, `CS8`, `CSTOPB`, `CREAD`, `PARENB`, `PARODD`, `HUPCL`, `CLOCAL`, `CRTSCTS`

`CSIZE` is omitted (same integer as `CS8`); use `CS8->value` to clear/set the character-size field.

### `LocalFlag` — `c_lflag` bits

`ISIG`, `ICANON`, `XCASE`, `ECHO`, `ECHOE`, `ECHOK`, `ECHONL`, `NOFLSH`, `TOSTOP`, `ECHOCTL`, `ECHOPRT`, `ECHOKE`, `FLUSHO`, `PENDIN`, `IEXTEN`, `EXTPROC`

### `ControlChar` — `c_cc` indices

`VINTR`, `VQUIT`, `VERASE`, `VKILL`, `VEOF`, `VTIME`, `VMIN`, `VSWTC`, `VSTART`, `VSTOP`, `VSUSP`, `VEOL`, `VREPRINT`, `VDISCARD`, `VWERASE`, `VLNEXT`, `VEOL2`

---

## Notes on `uart_open` defaults

`uart_open` applies the following configuration automatically:

* **`O_RDWR | O_NOCTTY | O_CLOEXEC`** — read/write access; device does not become the controlling terminal; never inherited by a child process
* **`cfmakeraw` semantics** — no input/output processing, 8N1, no parity
* **`VMIN=1`, `VTIME=0`** — `read()` blocks until at least one byte arrives
* **`TCSANOW`** — settings applied immediately
* **Baud via `posi_set_baud_rate`** — standard `BaudRate` cases and non-standard ints

To override any of these defaults, call `uart_tcgetattr`, mutate the returned array with the flag enums, and reapply with `uart_tcsetattr`.

## License

MIT. See [LICENSE](https://github.com/microscrap/uart/tree/HEAD/LICENSE).
