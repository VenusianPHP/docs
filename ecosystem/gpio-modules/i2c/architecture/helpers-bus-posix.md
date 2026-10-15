# Helpers bus posix

Global i2c_* helpers call Bus; Bus calls ext-posi posix_open/read/write/close, ioctl, and posi_mem_*; posi_mem_* only for I2C_RDWR.

## Call stack

```
app / peers / tests
    │
    ├─ i2c_open / i2c_read / i2c_rdwr / …     # global helpers (exact names)
    │       └─► Bus::*                          # Microscrap\Bindings\I2C\Bus
    │               ├─► posix_open / posix_read / posix_write / posix_close
    │               ├─► ioctl (I2C_* opcodes via I2COpCode)
    │               └─► posi_mem_alloc / write / read / free   # I2C_RDWR only
    │
    └─ Bus::i2cOpen(...)                       # static style (same path)
            └─► (same posix / ioctl / posi_mem_*)
```

Rules:[^agents][^readme][^bus]

1. Helpers call `Microscrap\Bindings\I2C\Bus` only.
2. `Bus` is the only layer that calls `posix_*`, `ioctl`, and `posi_mem_*` for this package’s I²C surface.
3. Helpers never call ext-posi functions directly.
4. Do not invent a parallel PHP API or reimplement kernel i2c-dev ioctls outside `Bus`.

## Autoload

Composer `autoload.files` registers:[^composer]

- `src/Helpers/i2c-bus.php` — lifecycle, raw I/O, adapter ioctls, `i2c_rdwr`
- `src/Helpers/i2c-smbus.php` — SMBus convenience helpers

Each function is wrapped in `if (! function_exists(...))` so a prior definition wins.[^helpers-bus][^helpers-smbus]

## Helper groups

| Group | Examples | Bus / lower path |
|-------|----------|------------------|
| Lifecycle / I/O | `i2c_open`, `i2c_close`, `i2c_read`, `i2c_write` | `posix_open` (`O_RDWR` constant from ext-posi) + `I2C_SLAVE`; then `posix_read` / `posix_write` / `posix_close`[^bus] |
| Adapter config | `i2c_set_slave_addr`, `i2c_set_ten_bit`, `i2c_set_pec`, `i2c_set_retries`, `i2c_set_timeout`, `i2c_get_funcs` | `ioctl` with `I2COpCode`[^bus][^readme] |
| Combined xfer | `i2c_rdwr` | Pack `i2c_msg` / `i2c_rdwr_ioctl_data` via `posi_mem_*` + `I2C_RDWR` ioctl; `false` only when the ioctl fails (`posi_mem_*` always exist)[^bus] |
| SMBus convenience | `i2c_smbus_*` | Emulated with `posix_read` / `posix_write` — **not** `I2C_SMBUS` ioctl[^readme][^bus] |

## Handle object

`I2CBus` is a `final readonly` data object with `fd`, `path`, and `addr`.[^dto] Helpers pass it by value into `Bus`. After `i2c_set_slave_addr*`, see [`I2CBus::$addr` stale after set_slave](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/i2cbusaddr-stale-after-set-slave).

## Errors / style

- C-style return codes (`null` / `-1` / `false` on failure) — no exceptions from helpers / `Bus` in this package’s wrap.[^readme]
- Prefer `is_null($var)` over `$var === null` in package code.[^agents]

## Related

* [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/11-extension-wrap)
* [Enums for kernel constants](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/enums-for-kernel-constants)
* [SMBus helpers ≠ I2C_SMBUS ioctl](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/smbus-helpers-i2c-smbus-ioctl)
* [`function_exists` load order](/docs/{{version}}/ecosystem/gpio-modules/i2c/traps/function-exists-load-order)

[^bus]: Bus facade with posix / ioctl / posi_mem_* usage
[^helpers-bus]: Bus lifecycle and ioctl helpers
[^helpers-smbus]: SMBus convenience helpers
[^dto]: I2CBus data object
[^composer]: Autoload files list
[^readme]: Helper API and facade mapping
[^agents]: Helpers call Bus only
