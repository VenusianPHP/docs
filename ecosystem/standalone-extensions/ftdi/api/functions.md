# Functions

Every bound libftdi call by group, return conventions, out parameters, argument ranges, empty-string-as-NULL, what is not bound.

## Groups

Signatures in `ftdi.stub.php`. First argument `FTDIContext` unless noted.[^stub]

| Group | Functions |
|---|---|
| Context | `ftdi_new(): ?FTDIContext`, `ftdi_init`, `ftdi_deinit`, `ftdi_free`, `ftdi_set_interface`, `ftdi_get_library_version(): FTDIVersionInfo` (no ctx), `ftdi_get_error_string` |
| Devices | `ftdi_usb_find_all`, `ftdi_usb_get_strings`, `ftdi_usb_get_strings2`, `ftdi_usb_open_dev`, `ftdi_usb_open`, `ftdi_usb_open_desc`, `ftdi_usb_open_desc_index`, `ftdi_usb_open_bus_addr`, `ftdi_usb_open_string`, `ftdi_usb_close`, `ftdi_usb_reset` |
| Flushes | `ftdi_tci_flush`, `ftdi_tco_flush`, `ftdi_tcio_flush`; deprecated `ftdi_usb_purge_rx_buffer`, `_tx_buffer`, `_buffers` (bound with `-Wdeprecated-declarations` silenced) |
| Line | `ftdi_convert_baudrate_ut_export`, `ftdi_set_baudrate`, `ftdi_set_line_property`, `ftdi_set_line_property2`, `ftdi_set_bitmode`, `ftdi_disable_bitbang`, `ftdi_read_pins`, `ftdi_set_latency_timer`, `ftdi_get_latency_timer`, `ftdi_set_timeouts`, `ftdi_poll_modem_status`, `ftdi_setflowctrl`, `ftdi_setflowctrl_xonxoff`, `ftdi_setdtr`, `ftdi_setrts`, `ftdi_setdtr_rts`, `ftdi_set_event_char`, `ftdi_set_error_char` |
| Sync data | `ftdi_write_data`, `ftdi_read_data`, `ftdi_{write,read}_data_{set,get}_chunksize` |
| Async + pump | see [async](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/async-transfers-and-the-libusb-pump) |
| EEPROM | see [EEPROM](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/eeprom) |

## Return conventions

- int = libftdi return code; negative explained by `ftdi_get_error_string()` (also live `errorStr` property).
- Out-parameter calls return the value on success, the negative code on failure (`FTDI_CTX_OUT_FUNCTION`): `ftdi_read_pins`, `ftdi_get_latency_timer`, `ftdi_poll_modem_status`, `ftdi_write_data_get_chunksize`, `ftdi_read_data_get_chunksize`, `ftdi_get_eeprom_value`, `ftdi_read_eeprom_location`.
- Multi-output calls return arrays: `ftdi_usb_find_all` → `['count', 'devices' => list<FTDIDevice>]`; `ftdi_usb_get_strings[2]` → `['result', 'manufacturer', 'description', 'serial']` (256-byte buffers); `ftdi_convert_baudrate_ut_export(baud, ctx)` → `['result', 'value', 'index']`.
- `ftdi_read_chip_id(ctx, &$chip_id)` keeps the by-ref shape `microscrap/ftdi` had; `$chip_id` written only on 0.
- Object-or-nothing: `ftdi_new()`, submits → null. Bytes-or-nothing: `ftdi_read_data`, `ftdi_transfer_read_done`, `ftdi_get_eeprom_buf` → false. `ftdi_read_data` returns "" when nothing has arrived yet; poll until enough bytes.[^ftdi-c]

## Arguments

Checked against C types before the call; outside → `ValueError` naming the argument:
- vendor/product 0–0xFFFF; bus/address 0–255; `index` 0–UINT_MAX.
- bytes 0–255: bitmask, bitmode, latency, event/error char and its enable flag.
- enums: interface `INTERFACE_ANY`–`INTERFACE_D`; bits `BITS_7`/`BITS_8` only; stop bits `STOP_BIT_1`–`STOP_BIT_2`; parity `NONE`–`SPACE`; break `BREAK_OFF`/`BREAK_ON`; `enum ftdi_eeprom_value` `VENDOR_ID`–`USER_DATA_ADDR`.
- booleans 0/1: `ftdi_setdtr`, `ftdi_setrts`, `ftdi_setdtr_rts`, `ftdi_eeprom_decode` verbose.
- baud rate 1–INT_MAX; timeouts 0–INT_MAX ms; flow control 0–0xFFFF; chunk sizes 1–UINT_MAX.
- `size` with data: 0–`strlen(data)`, ≤ `INT_MAX`; read sizes 1–INT_MAX.
- `ftdi_handle_events_timeout` µs ≥ 0; EEPROM word 0–0xFFFF; EEPROM address 0–INT_MAX.

Optional C strings (`ftdi_usb_open_desc*` description/serial, EEPROM strings): "" → NULL = "any"/"unset", as libftdi reads NULL. `ftdi_usb_open_string` takes its descriptor string verbatim (`d:`, `i:`, `s:` forms).[^ftdi-c]

## Not bound

- `ftdi_list_free`, `ftdi_list_free2`: `ftdi_usb_find_all` frees its list; each `FTDIDevice` holds own libusb reference.
- `ftdi_set_usbdev`: PHP cannot obtain a `libusb_device_handle`.

[^stub]: ftdi.stub.php
[^ftdi-c]: ftdi.c
