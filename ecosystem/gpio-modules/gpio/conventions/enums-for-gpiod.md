# Enums for gpiod

GPIO direction/edge/bias/drive/clock/value and ioctl enums are int-backed with FULLY UPPERCASE cases; no class constants.

## Why enums live here

Typed tokens for libgpiod-style line settings, event types, kernel ioctl opcodes, and `gpio_v2_line_flag` bitmasks. Keep new constants as enum cases — never class-level `const`.[^readme][^agents]

## Rules

- Use **int-backed** enums under `Microscrap\Bindings\GPIO\Enums\`.[^direction][^opcode]
- Case names are **FULLY UPPERCASE** (e.g. `LineDirection::OUTPUT`, `LineEdge::RISING`).[^agents][^readme]
- No class-level constants in `src/`.[^agents]
- Pass enum instances (or `->value` where a raw `int` is required) into typed helper / facade APIs.[^readme]

## Enum inventory (0.10.0)

| Enum | Backing | Cases (summary) |
|------|---------|-----------------|
| `LineDirection` | int | `AS_IS`, `INPUT`, `OUTPUT`[^direction] |
| `LineEdge` | int | `NONE`, `RISING`, `FALLING`, `BOTH`[^edge] |
| `LineBias` | int | `AS_IS`, `UNKNOWN`, `DISABLED`, `PULL_UP`, `PULL_DOWN`[^bias] |
| `LineDrive` | int | `PUSH_PULL`, `OPEN_DRAIN`, `OPEN_SOURCE`[^drive] |
| `LineClock` | int | `MONOTONIC`, `REALTIME`, `HTE`[^clock] |
| `LineValue` | int | `ERROR` (-1), `INACTIVE` (0), `ACTIVE` (1)[^value] |
| `InfoEventType` | int | `LINE_REQUESTED`, `LINE_RELEASED`, `LINE_CONFIG_CHANGED`[^info-event] |
| `EdgeEventType` | int | `RISING_EDGE`, `FALLING_EDGE`[^edge-event] |
| `GPIOOpCode` | int | GPIO ioctl opcodes from `linux/gpio.h` macros[^opcode] |
| `GPIOV2LineFlag` | int | 13 `gpio_v2_line_flag` bitmask values[^flags] |
| `GPIOV2LineAttrId` | int | `FLAGS`, `OUTPUT_VALUES`, `DEBOUNCE`[^attr-id] |
| `StatMode` | int | `S_IFMT`, `S_IFLNK`, `S_IFCHR` (device-node checks)[^stat-mode] |

## Related

* [1:1 libgpiod wrap](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/11-libgpiod-wrap)
* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/package-010)
* [Helpers → gpiod facades → posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi)

[^readme]: Enum table and UPPERCASE note
[^direction]: LineDirection enum
[^edge]: LineEdge enum
[^bias]: LineBias enum
[^drive]: LineDrive enum
[^clock]: LineClock enum
[^value]: LineValue enum
[^info-event]: InfoEventType enum
[^edge-event]: EdgeEventType enum
[^opcode]: GPIOOpCode enum
[^flags]: GPIOV2LineFlag enum
[^attr-id]: GPIOV2LineAttrId enum
[^stat-mode]: StatMode enum
[^agents]: Enum case naming rule
