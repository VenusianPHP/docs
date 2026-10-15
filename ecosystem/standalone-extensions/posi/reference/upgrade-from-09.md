# Upgrade from 0.9

Zephir posi 0.9 plus microscrap/posix to C posi 0.10, call by call.

## What changed

0.9 = Zephir ext (`Posi\System`, `Posi\Termios`, `Posi\Memory` statics) + `microscrap/posix` (global helpers and int-backed enums over it). 0.10 = one C ext exposing the helper names natively. Consumers drop `microscrap/posix` from `require`, add `ext-posi: ^0.10.0`.

| 0.9 | 0.10 |
|---|---|
| `Posi\System::open/close/read/write/lseek/readv/recv(...)` | `posix_open/close/read/write/lseek/readv/recv(...)` |
| `Posi\System::fcntl(...)` → `['res', 'val']` | `fcntl($fd, $cmd, $arg, $value)`: returns res, fills `$value` |
| `Posi\System::ioctl(...)` → `['res', 'val']` | `ioctl($fd, $req, $arg, $value)`: same shape |
| `Posi\Termios::tcgetattr/tcsetattr/cfset*/cfget*/tcdrain/tcflush/tcflow` | bare POSIX names |
| `Posi\Termios::setBaudRate($fd, $baud)` | `posi_set_baud_rate($fd, $baud)` |
| `Posi\Memory::alloc/free/read/write` | `posi_mem_alloc/free/read/write` |
| `FileControlFlag::O_RDWR->value`, `FcntlCommand::F_GETFL`, `PollEvent::POLLIN`, … | `O_RDWR`, `F_GETFL`, `POLLIN` |
| `function_exists('posi_mem_alloc')` guards | gone: always present |
| termios array without speeds | `c_ispeed`/`c_ospeed` required |
| out-of-range ints truncated | `ValueError` |

0.9 enums carried x86 Linux numbers, wrong on macOS and arm64. 0.10 constants come from headers. See [constants](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/constants).

## Ported consumers

`microscrap/gpio`, `i2c`, `spi`, `uart` 0.10 and `microscrap/scrapyard-linux` 0.10 use the 0.10 names. Their CI installs `pie install php-io-extensions/posi:^0.10`.
