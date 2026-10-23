# Constants

Header-valued constants,

## Rule

Every value comes from the platform header at build time, never a literal. A constant exists only where the header defines it.

## Stub constants

185 in `posi.stub.php`, each:

```php
 #ifdef O_DIRECT
/**
 * @var int
 * @cvalue O_DIRECT
 */
const O_DIRECT = UNKNOWN;
 #endif
```

gen_stub copies the `#ifdef` into `posi_arginfo.h`. Groups: `<fcntl.h>` (`F_*`, `FD_CLOEXEC`, lock types, `O_*` POSIX set plus `O_ASYNC`, `O_DIRECT`, `O_NOATIME`, `O_PATH`, `O_TMPFILE` where defined), `<poll.h>` `POLL*`, `<sys/stat.h>` `S_IF*` + mode bits, `<termios.h>` actions, queues, flow, `NCCS` + `V*`, iflag/oflag/cflag/lflag bits, every `B*` 0 … 4000000.[^stub]

Values differ per platform: `O_NONBLOCK` 4 macOS vs 0x800 Linux; `O_DIRECT` 0x4000 x86_64 vs 0x10000 arm64. Never hard-code in tests; compare against the constant.

## Registered in MINIT

| Names | Why not in stub |
|---|---|
| `MSG_OOB`, `MSG_PEEK`, `MSG_WAITALL`, `SOMAXCONN` | ext/sockets registers them |
| `WNOHANG`, `WUNTRACED`, `WCONTINUED` | ext/pcntl registers them |
| POSIX errno set `E2BIG` … `EXDEV` (each `#ifdef`) | ext-kqueue registers some |
| `ECHO` | PHP keyword; stub cannot declare it. Read with `constant('ECHO')` |

`posi_register_if_absent()` registers a name only when `EG(zend_constants)` lacks it. Same header, same value, so whichever extension registered it is correct. `ZEND_MOD_OPTIONAL` on pcntl, sockets, kqueue loads them first when present, so posi never collides and no "already defined" warning fires. Adding a constant another extension may own: put it here, not in the stub.[^posi-c]

[^stub]: posi.stub.php
[^posi-c]: posi.c
