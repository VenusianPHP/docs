# libftdi 1.5 guards

Where libftdi 1.5 behaviour would crash, leak or mislead from PHP, and the binding code that prevents each case.

## Rule

Binding stays 1:1, yet no well-formed PHP call may crash, leak, or report a stale error. Where libftdi 1.5 allows that, `ftdi.c` checks first. Each row read from libftdi 1.5 `src/ftdi.c`.[^libftdi]

| libftdi 1.5 behaviour | Binding |
|---|---|
| `ftdi_eeprom_get_strings()` `strncpy`s from `eeprom->manufacturer/product/serial` with no NULL check; fresh context, `initdefaults`, `decode` can leave each NULL | context tracks `strings[3]`, passes NULL out-buffers for absent strings, returns "". Rules in [EEPROM](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/eeprom) |
| `ftdi_init()` resets `usb_ctx` and mallocs a new eeprom struct without freeing the old ones | `ftdi_init()` over an initialised context cancels transfers, drops devices, `ftdi_deinit()`s first |
| `ftdi_write_data_submit()`/`ftdi_read_data_submit()` return NULL with no device open, `error_str` untouched | `ftdi_has_device()` sets "USB device unavailable" first, so `ftdi_get_error_string()` explains the null |
| `ftdi_transfer_data_done()`/`_cancel()` free `tc`; a second call is a use after free | object nulls `tc` after either; repeat = -1 / false / no-op |
| `ftdi_free()`/`ftdi_deinit()` `libusb_exit` under live `libusb_device` refs and pending transfers | dependents registry cancels and unrefs first. See [objects](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/objects) |
| `ftdi_free()` twice = double free | object nulls `ctx`; second call no-op; other calls `Error` |
| calls after `ftdi_deinit()` use NULL `usb_ctx`/eeprom | `initialized` flag; `Error` "call ftdi_init() first" |
| `FTDI_MAX_EEPROM_SIZE` only in private `ftdi_i.h` | literal 256 with comment in `ftdi_set_ft232h_cbus` |

Newer libftdi fixing a row: guard stays, harmless. Re-read the row against the new source before removing anything.[^ftdi-c]

[^ftdi-c]: ftdi.c
[^libftdi]: libftdi1 1.5 source, src/ftdi.c
