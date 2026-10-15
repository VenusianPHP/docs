# EEPROM

Reading, decoding, editing and writing the EEPROM image; the FTDIEeprom snapshot; string presence tracking; FT232H CBUS bytes.

## Flow

libftdi keeps one EEPROM image per context. Typical: `ftdi_read_eeprom` (device → raw image) → `ftdi_eeprom_decode(ctx, 0)` (raw → fields) → `ftdi_get_eeprom(ctx)` snapshot, or edit with `ftdi_set_eeprom_value`/`ftdi_eeprom_set_strings` → `ftdi_eeprom_build` → `ftdi_write_eeprom`. `ftdi_eeprom_initdefaults(ctx, $manufacturer, $product, $serial)` resets the image to chip defaults.

| Function | Returns |
|---|---|
| `ftdi_get_eeprom(ctx): FTDIEeprom` | snapshot; each value via `ftdi_get_eeprom_value`, 0 where the chip type lacks it |
| `ftdi_get_eeprom_value(ctx, $name)` / `ftdi_set_eeprom_value(ctx, $name, $value)` | value or code / code; `$name` an `enum ftdi_eeprom_value` constant |
| `ftdi_eeprom_get_strings(ctx)` | `['manufacturer', 'product', 'serial']` |
| `ftdi_eeprom_set_strings(ctx, $m, $p, $s)` | code; "" = leave that string |
| `ftdi_get_eeprom_buf(ctx, $size): string\|false` | raw image bytes |
| `ftdi_set_eeprom_buf(ctx, $bytes)`, `ftdi_set_eeprom_user_data(ctx, $bytes)` | code |
| `ftdi_read_eeprom_location(ctx, $addr)` / `ftdi_write_eeprom_location(ctx, $addr, $word)` | word or code / code |
| `ftdi_read_eeprom`, `ftdi_write_eeprom`, `ftdi_erase_eeprom`, `ftdi_eeprom_build` | code |
| `ftdi_read_chip_id(ctx, &$id)` | code; `$id` on 0 |
| `ftdi_set_ft232h_cbus(ctx): string` | 5 bytes: image offsets 0x18–0x1C as `set_ft232h_cbus()` encodes the context's CBUS functions |

`ftdi_set_ft232h_cbus` encodes into a zeroed 256-byte buffer (libftdi's `FTDI_MAX_EEPROM_SIZE`, private `ftdi_i.h`, so written as a literal) and returns the slice. Read-only towards the device.[^ftdi-c]

## String presence

libftdi 1.5 `ftdi_eeprom_get_strings()` `strncpy`s from each image string with no NULL check; fresh context, `ftdi_deinit`, `initdefaults` or `decode` can leave any NULL. Context keeps `strings[3]` and asks libftdi only for strings it holds; others come back "".

| Event | `strings[]` after |
|---|---|
| `ftdi_new`, `ftdi_init`, `ftdi_deinit` | all false |
| `initdefaults` | manufacturer = device open && given; product = device open && rc 0; serial = device open && rc 0 && given |
| `set_strings` rc 0 | each given string → true, others unchanged |
| `decode` | each = image length byte (0x0F, 0x11, 0x13) / 2 > 0, matching libftdi's NULL rule |

Rules derived from libftdi 1.5 `ftdi.c`. A newer libftdi that NULL-checks makes this redundant but stays correct.[^ftdi-c]

Writing EEPROM changes stored USB IDs; see `SECURITY.md`. Tests never write EEPROM.

[^ftdi-c]: ftdi.c
