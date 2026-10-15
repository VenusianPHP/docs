# Helpers → MPSSE → FTDI

Global helpers call Microscrap\Bindings\MPSSE\MPSSE; that wrapper calls ext-ftdi's global ftdi_* functions.

## Call stack

Helpers reach ext-ftdi through an intermediate static class:[^readme][^helpers][^mpsse]

```
app / tests
    │
    └─ mpsse_open(...) / mpsse_pin_high(...)   # global helpers (thin)
            └─► Microscrap\Bindings\MPSSE\MPSSE::*
                    └─► ftdi_* global functions (ext-ftdi / libftdi1)
```

Rules:[^agents][^readme]

1. Helpers call `MPSSE` static methods only (not `ftdi_*` directly).
2. Protocol / session logic lives on `MPSSE` — keep helpers thin.
3. Context type is package-owned `MPSSEContext` (may hold `?Ftdi\FTDIContext`); do not invent parallel DataObjects beyond this.[^context]
4. Do not remove the `MPSSE` wrapper unless Angel explicitly asks.

## Helper inventory (0.10.0)

Eight globals in `src/Helpers/mpsse.php`:[^helpers]

| Helper | Delegates to |
|--------|----------------|
| `mpsse_open(...)` | `MPSSE::open(...)` (returns `null` when not open) |
| `mpsse_close($ctx)` | `MPSSE::close(...)` |
| `mpsse_check_ftdi_device($device)` | Matches `Ftdi\FtdiProductId` case **name** |
| `mpsse_configure_pin_direction(...)` | `MPSSE::configurePinDirection(...)` |
| `mpsse_pin_high` / `mpsse_pin_low` | `MPSSE::pinHigh` / `pinLow` |
| `mpsse_pin_state` / `mpsse_read_pins` | `MPSSE::pinState` / `readPins` |

The full SPI/I2C session API (`start`, `write`, `read`, `transfer`, ACK helpers, …) is on `MPSSE` only — not duplicated as globals.[^readme][^mpsse]

## Autoload

Composer `autoload.files` registers a single helper module:[^composer]

- `src/Helpers/mpsse.php`

Each function is wrapped in `if (! function_exists(...))` so a prior definition wins.[^helpers]

## Objects and errors

- Session state is `Microscrap\Bindings\MPSSE\MPSSEContext` (libmpsse-style fields; embeds `?Ftdi\FTDIContext`, which owns its C pointer; no int handle).[^context]
- Prefer `is_null($ctx)` / `is_null($ctx->ftdi)` style checks over `=== null` in agent-authored code.[^agents]
- `ftdi_new()` returns `?FTDIContext`; on `null` the `open*` methods return an unopened `MPSSEContext` with `ftdi === null`. `ftdi_read_data` returns `string|false`.[^mpsse]
- Use `MPSSE::errorString($ctx)` after failed opens; helpers may populate optional `&$error`.[^helpers][^readme]
- No ServiceProvider-thrown framework exceptions from this package.[^readme]

## Related

* [1:1 libmpsse wrap](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/11-libmpsse-wrap)
* [Enums for MPSSE](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/enums-for-mpsse)
* [`function_exists` load order](/docs/{{version}}/ecosystem/gpio-modules/mpsse/traps/function-exists-load-order)
* [Mode mismatch workflows](/docs/{{version}}/ecosystem/gpio-modules/mpsse/traps/mode-mismatch-workflows)

[^helpers]: Helper file with function_exists guards
[^mpsse]: MPSSE static wrapper over FTDI
[^context]: Package-owned MPSSEContext
[^composer]: Autoload files list for helpers
[^readme]: Helpers delegate to MPSSE; MPSSE uses FTDI
[^agents]: Agent wrap rules
