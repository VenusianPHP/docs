# 1:1 extension wrap

Helpers delegate to Bus only; Bus calls ext-posi functions (posix_*, ioctl, posi_mem_*); no parallel APIs or Fabricate wiring.

## Rule

Match peer bindings packages (`microscrap/open-gl`, …) in spirit — thin wrap over the native stack:[^agents][^readme]

1. Global helpers use the names callers expect (`i2c_open`, `i2c_rdwr`, `i2c_smbus_read_byte_data`, …).
2. Helpers call **`Microscrap\Bindings\I2C\Bus`** only — never invent parallel APIs or call ext-posi functions from helper files.[^helpers-bus][^agents]
3. `Bus` is the only layer that uses `posix_*`, `ioctl`, and `posi_mem_*` for this package.[^bus]
4. Keep helper ↔ `Bus` method coverage aligned with README tables; document drift in README / ecosystem docs.[^agents]
5. Kernel `#define` integers live in backed enums — see [Enums for kernel constants](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/enums-for-kernel-constants).
6. No ServiceProvider, Chassis/Core coupling, or Fabricate remaps in this package.[^agents]
7. Prefer `is_null($var)` over `$var === null`; no class-level constants.[^agents]

## Architecture link

Full call-stack diagram: [Helpers → Bus → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/i2c/architecture/helpers-bus-posix).

[^agents]: Agent wrap rules
[^readme]: Package README wrap description
[^helpers-bus]: Helper → Bus delegation
[^bus]: Bus → posix / ioctl / posi_mem_*
