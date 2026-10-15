# 1:1 extension wrap

Helpers call Device only; Device uses ext-posi functions; keep coverage aligned with spi-device.php.

## Rule

Match peer protocol bindings (`microscrap/uart`, `microscrap/i2c`, …) — thin wrap over spidev via ext-posi:[^agents][^readme]

1. Global helpers use the names callers expect (`spi_open`, `spi_transfer`, …).
2. Helpers call **`Microscrap\Bindings\SPI\Device` only** — never invent parallel APIs.[^helpers][^agents]
3. `Device` uses native ext-posi functions (`posix_open`, `posix_read`, `posix_write`, `posix_close`, `ioctl`, `posi_mem_*`) — do not reimplement FD I/O or ioctl packing elsewhere.[^device][^agents]
4. Keep 1:1 coverage with helpers already in `src/Helpers/spi-device.php`; document drift in README / ecosystem docs.[^agents]
5. Kernel `#define` flag / ioctl integers live in backed enums — see [Enums for spidev flags](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/enums-for-spidev-flags).
6. No ServiceProvider, Chassis/Core coupling, or Fabricate remaps in this package.[^agents]
7. Prefer `is_null($var)` over `$var === null`; no class-level constants.[^agents]

## Architecture link

Full call-stack diagram: [Helpers → Device → posix](/docs/{{version}}/ecosystem/gpio-modules/spi/architecture/helpers-device-posix).

[^agents]: Agent wrap rules
[^readme]: Package README wrap description
[^helpers]: Helper delegation to Device
[^device]: Device uses ext-posi functions and posi_mem_*
