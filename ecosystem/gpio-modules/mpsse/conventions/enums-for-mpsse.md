# Enums for MPSSE

MPSSE mode/pin/command/device enums are int- or string-backed with FULLY UPPERCASE cases; no class constants.

## Why enums live here

Typed tokens for MPSSE modes, interfaces, endianness, clock rates, FTDI MPSSE command bytes, ACK/NACK, pin bitmasks, GPIO pin indexes, and supported device shortcuts. Keep new constants as enum cases — never class-level `const`.[^readme][^agents]

## Rules

- Use **int-backed** or **string-backed** enums under `Microscrap\Bindings\MPSSE\Enums\`.[^mode][^device]
- Case names are **FULLY UPPERCASE** (e.g. `MPSSEMode::SPI0`, `MPSSEClockRate::ONE_MHZ`).[^agents][^readme]
- No class-level constants in `src/`.[^agents]
- Pass `->value` (or accept the enum at typed call sites) into APIs that take raw `int` / `string`.[^readme]

## Enum inventory (0.10.0)

| Enum | Backing | Cases (summary) |
|------|---------|-----------------|
| `MPSSEMode` | int | `SPI0`–`SPI3`, `I2C`, `GPIO`, `BITBANG`[^mode] |
| `MPSSEInterface` | int | `IFACE_ANY`, `IFACE_A`–`IFACE_D`[^iface] |
| `MPSSEEndianness` | int | `MSB`, `LSB`[^endian] |
| `MPSSEClockRate` | int | `ONE_HUNDRED_KHZ` … `SIXTY_MHZ`[^clock] |
| `MPSSECommand` | int | FTDI MPSSE opcodes (`SET_BITS_LOW`, `TCK_DIVISOR`, …)[^command] |
| `MPSSEAck` | int | `ACK`, `NACK`[^ack] |
| `MPSSEPin` | int | Bitmask pins `SK`, `DO`, `DI`, `CS`, `GPIO0`–`GPIO3`[^pin] |
| `MPSSEGpioPin` | int | Index pins `GPIOL0`–`GPIOH7`[^gpio-pin] |
| `MpsseSupportedDevice` | string | `FT232H`, `FT2232H_A`/`_B`, `FT4232H_A`–`_D`[^device] |

## Related

* [1:1 libmpsse wrap](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/11-libmpsse-wrap)
* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/mpsse/orientation/package-010)
* [Mode mismatch workflows](/docs/{{version}}/ecosystem/gpio-modules/mpsse/traps/mode-mismatch-workflows)

[^readme]: Enum namespaces and UPPERCASE note
[^mode]: MPSSEMode enum
[^iface]: MPSSEInterface enum
[^endian]: MPSSEEndianness enum
[^clock]: MPSSEClockRate enum
[^command]: MPSSECommand enum
[^ack]: MPSSEAck enum
[^pin]: MPSSEPin enum
[^gpio-pin]: MPSSEGpioPin enum
[^device]: MpsseSupportedDevice enum
[^agents]: Enum case naming rule
