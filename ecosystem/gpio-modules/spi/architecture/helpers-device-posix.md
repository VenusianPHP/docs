# Helpers → Device → posix

Global spi_* helpers call Device; Device uses ext-posi posix_open/read/write/close/ioctl and posi_mem_*; native spi_transfer(int) fast path optional.

## Call stack

```
app / peers / tests
    │
    └─ spi_open / spi_read / spi_write / spi_transfer / …
            └─► Device::spi*                    # this package
                    ├─ posix_open / posix_read / posix_write / posix_close / ioctl   # ext-posi functions
                    │
                    └─ spi_transfer paths
                            ├─ native spi_transfer(int $fd, …)   # optional low-level ext
                            └─ posi_mem_alloc / write / read / free + ioctl(SPI_IOC_MESSAGE)   # ext-posi functions
```

Rules:[^agents][^readme][^helpers][^device]

1. Global helpers call `Microscrap\Bindings\SPI\Device` only.
2. `Device` uses the native ext-posi functions (`posix_open`, `posix_read`, `posix_write`, `posix_close`, `ioctl`, `posi_mem_*`) — do not invent parallel APIs.
3. Keep 1:1 coverage with helpers already in `src/Helpers/spi-device.php`.

## Autoload

Composer `autoload.files` registers:[^composer]

- `src/Helpers/spi-device.php`

Each function is wrapped in `if (! function_exists(...))` so a prior definition wins.[^helpers]

## Helper groups (0.10 surface)

| Group | Examples | Device / lower target |
|-------|----------|------------------------|
| Lifecycle | `spi_open`, `spi_close` | `posix_open` / `posix_close` + mode/speed/bits ioctl |
| Half-duplex I/O | `spi_read`, `spi_write` | `posix_read` / `posix_write` |
| Config | `spi_get_*` / `spi_set_*` | `ioctl` via `SPIOpCode` |
| Full-duplex | `spi_transfer` | Native `spi_transfer(int)` **or** `posi_mem_*` + `SPI_IOC_MESSAGE` |

## `spi_transfer` paths

`Device::spiTransfer` prefers a **native** `spi_transfer(int $fd, …)` when Reflection shows the first parameter is `int` (avoids recursing into this package’s procedural helper, which takes `SPIDevice`). Otherwise it uses the **ext-posi** `posi_mem_*` path (one `SPI_IOC_MESSAGE(N)` for every segment); `posi_mem_*` always exists because `ext-posi` is required. `false` means the transfer failed.[^device][^readme]

See [Native `spi_transfer` vs `posi_mem`](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/native-spi-transfer-vs-posi-mem).

## Errors / style

- C-style return codes (`null` / `-1` / `false` on failure) — no exceptions from the wrap surface.[^readme]
- Prefer `is_null($var)` over `$var === null` in package code.[^agents]

## Related

* [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/11-extension-wrap)
* [Enums for spidev flags](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/enums-for-spidev-flags)
* [Half-duplex vs full-duplex](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/half-duplex-vs-full-duplex)

[^helpers]: Helper file delegating to Device
[^device]: Device facade; posix and transfer paths
[^composer]: Autoload files list; require ext-posi
[^readme]: Helper API and transfer path notes
[^agents]: Helpers → Device → posix only
