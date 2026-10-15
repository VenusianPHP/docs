# Termios

The termios array shape, speeds carried in it, BOTHER round trips, posi_set_baud_rate and its hand-declared termios2.

## Functions

Bare POSIX names: `tcgetattr($fd): array|false`, `tcsetattr($fd, $action, $termios): int`, `cfsetispeed/cfsetospeed($termios, $speed): array|false` (array with speed applied; false = platform refuses), `cfgetispeed/cfgetospeed($termios): int`, `tcdrain($fd)`, `tcflush($fd, $queue)`, `tcflow($fd, $action)` → 0 / -1.[^termios-c]

## Array shape

| Key | Type |
|---|---|
| `c_iflag`, `c_oflag`, `c_cflag`, `c_lflag` | int |
| `c_cc` | list of int, indices 0 … `NCCS`-1, addressed by `VMIN`, `VTIME`, … |
| `c_ispeed`, `c_ospeed` | int, `cfgetispeed()`/`cfgetospeed()` of the struct |

Every key required on input; missing or non-int → `ValueError`. Speeds travel in the array because macOS stores them in own struct fields, not `c_cflag`; a round trip without them would apply `B0` and hang up the line. Linux: they mirror `c_cflag` speed bits.[^termios-c]

Array → struct applies a speed only where it differs from what the flags already carry. Linux custom rate (`BOTHER` in `c_cflag`, real rate in kernel `termios2`) survives `tcgetattr` → edit flags → `tcsetattr` untouched. Unsupported speed → `ValueError`.

## posi_set_baud_rate($fd, $baud): int

Both directions, `TCSANOW`. `$baud` 1–UINT32_MAX else `ValueError`.
- Rate with a `B*` constant (50 … 4000000, each `#ifdef`): `tcgetattr`, `cfsetispeed`, `cfsetospeed`, `tcsetattr`.
- Other rate on Linux: `TCGETS2`, clear `CBAUD`, set `BOTHER`, both speeds = number, `TCSETS2`.
- Other rate elsewhere: -1, `posi_errno()` = `EINVAL`.

## termios2 declaration

`posi_termios.c` writes out `struct posi_termios2`, `BOTHER` 0x1000, `CBAUD` 0x100F, `TCGETS2` 0x802C542A, `TCSETS2` 0x402C542B, and declares `ioctl()` by its POSIX prototype, including neither `<asm/termbits.h>` nor `<sys/ioctl.h>`. Reason: `<asm/termbits.h>` redefines `struct termios` against `<termios.h>`, and arm64 `<sys/ioctl.h>` defines `TCGETS2` via `sizeof` of incomplete `struct termios2`. Values hold for generic ioctl encoding; guard `POSI_HAVE_TERMIOS2` lists x86_64, i386, aarch64, arm, riscv, loongarch. New Linux arch: confirm its `asm-generic` termbits before adding.[^termios-c]

## Tests

`tests/TermiosTest.php` runs against a pty from `ptyPair()` in `tests/Pest.php`: `/dev/ptmx` master, then the slave, unlocked and named through `ioctl()` — macOS `TIOCPTYGRANT`, `TIOCPTYUNLK`, `TIOCPTYGNAME`; Linux `TIOCSPTLCK`, `TIOCGPTN`. Termios calls go to the slave: macOS `tcgetattr` on the master fails `ENOTTY`.

[^termios-c]: posi_termios.c
