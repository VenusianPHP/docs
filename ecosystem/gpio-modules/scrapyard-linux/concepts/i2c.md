# I2C

One i2c-dev fd per bus shared by every slave, slave address selected per call, writeRead and bulkWrite as I2C_RDWR messages, via() through a worker.

## Connection

`connectTo(N)` → `posix_open("/dev/i2c-N", O_RDWR|O_CLOEXEC)`. The int fd is the registered handle; every `device(N, addr)` transport shares it. `disconnect()` → `posix_close`. A transport's `close()` releases nothing — the fd belongs to the bus.

## Calls

Every call: `ensureOpen()`, `ensureFits()` (framework's 8192-byte message limit), `awaitTurn()` (waits for this slave's earlier `via()` jobs).

| Call | Wire |
|---|---|
| `probe()` | set slave addr, then SMBus quick write; empty `i2c_write` fallback when SMBus helpers are missing |
| `read()` / `write()` | `I2C_SLAVE` ioctl for this address, then plain read/write on the shared fd |
| `writeRead()` | one `I2C_RDWR`: write message + read message, repeated START, no STOP between |
| `bulkWrite()` | each chunk its own write message; batches of 42 (`I2C_RDWR_IOCTL_MAX_MSGS`), STOP between batches |

Plain read/write address the fd's current slave, so the address is re-selected before each — slaves sharing the fd never talk to the wrong device. A refused address → `read()` false, `write()` -1.

## via()

Base framework behaviour: a `BusGig` naming `PosixI2CConnectionDriver` runs on a worker pool. A pool worker builds its own driver and opens its own `/dev/i2c-N` (close-on-exec keeps the parent's fd out). The kernel serialises transfers per adapter across processes.
