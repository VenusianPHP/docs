# Helpers → gpiod facades → posi

Global gpiod_* helpers call package facades (Chip, LineRequest, …); facades call ext-posi global functions (posix_*, ioctl) for FD and ioctl work.

## Call stack

This package **does** have intermediate facade classes (like `microscrap/mpsse`, unlike the thin ext-posi function layer):[^readme][^helpers-chip][^chip]

```
app / peers / tests
    │
    └─ gpiod_chip_open(...) / gpiod_line_request_set_value(...)   # global helpers (thin)
            └─► Microscrap\Bindings\GPIO\{Chip, LineRequest, LineSettings, …}
                    └─► ext-posi global functions — posix_open / posix_close / posix_read / posix_ppoll / posix_lstat / ioctl
```

Rules:[^agents][^readme]

1. Helpers call package facades only (`Chip`, `LineRequest`, `LineSettings`, `LineConfig`, `RequestConfig`, `ChipInfo`, `LineInfo`, `InfoEvent`, `EdgeEvent`, `EdgeEventBuffer`, `Misc`, `Internal` as needed).
2. Facades own chip/line/uAPI logic — keep helpers thin one-liners.[^helpers-chip][^helpers-line-request]
3. Do not invent parallel APIs that bypass facades into ad-hoc ioctl scripts from helpers.[^agents]
4. DataObjects under `src/DataObjects/` hold state (FDs, configs, events); do not invent a second object model.[^readme]

## Facade inventory (0.10.0)

| Facade | Typical helpers | Role |
|--------|-----------------|------|
| `Chip` | `gpiod_chip_*` | Open/close chip, info, watch, request lines[^chip] |
| `ChipInfo` | `gpiod_chip_info_*` | Chip info getters |
| `LineInfo` | `gpiod_line_info_*` | Line metadata getters / copy |
| `LineSettings` | `gpiod_line_settings_*` | Mutable per-line settings builder |
| `LineConfig` | `gpiod_line_config_*` | Offset → settings map / uAPI serialize |
| `RequestConfig` | `gpiod_request_config_*` | Consumer label / event buffer size |
| `LineRequest` | `gpiod_line_request_*` | Value I/O, reconfigure, edge wait/read[^line-request] |
| `InfoEvent` | `gpiod_info_event_*` | Chip info-event getters |
| `EdgeEvent` | `gpiod_edge_event_*` | Edge event getters / copy |
| `EdgeEventBuffer` | `gpiod_edge_event_buffer_*` | Batch edge-event buffer |
| `Misc` | `gpiod_is_gpiochip_device`, `gpiod_api_version` | Device check / version string[^misc] |
| `Internal` | (internal helpers) | Shared checks used by Misc / facades |

## Autoload

Composer `autoload.files` registers helper modules under `src/Helpers/`:[^composer]

- `gpio-chip.php`, `gpio-chip-info.php`, `gpio-info-event.php`
- `gpio-edge-event.php`, `gpio-edge-event-buffer.php`
- `gpio-line-info.php`, `gpio-line-request.php`, `gpio-line-config.php`, `gpio-line-settings.php`
- `gpio-request-config.php`, `gpio-misc.php`, `gpio-internal.php`

Each function is wrapped in `if (! function_exists(...))` so a prior definition wins.[^helpers-chip]

## Objects and errors

- Chip / request state lives in DataObjects such as `GPIOChip`, `GPIOLineRequest`, `GPIOLineSettings`, `GPIOEdgeEventBuffer`.[^readme]
- Prefer `is_null($var)` over `$var === null` in agent-authored code.[^agents]
- C-style return codes (`null` / `-1` / `0`) — no ServiceProvider-thrown framework exceptions from this package.[^readme]
- Example open path: `Chip::gpioChipOpen` verifies the device, then `posix_open` with the ext-posi constants `O_RDWR | O_CLOEXEC`.[^chip]

## Related

* [1:1 libgpiod wrap](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/11-libgpiod-wrap)
* [Enums for gpiod](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/enums-for-gpiod)
* [`function_exists` load order](/docs/{{version}}/ecosystem/gpio-modules/gpio/traps/function-exists-load-order)
* [GPIO device permissions](/docs/{{version}}/ecosystem/gpio-modules/gpio/traps/gpio-device-permissions)

[^helpers-chip]: Helper file with function_exists guards → Chip
[^helpers-line-request]: Helpers → LineRequest
[^chip]: Chip facade uses posix_open / posix_ppoll / posix_read and ioctl path
[^line-request]: LineRequest facade uses posix_close / posix_ppoll / posix_read
[^misc]: Misc facade for device check / api version
[^composer]: Autoload files list for helpers
[^readme]: Helpers delegate to facade classes
[^agents]: Agent wrap rules
