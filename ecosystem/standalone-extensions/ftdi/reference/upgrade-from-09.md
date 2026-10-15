# Upgrade from 0.9

Zephir ext-ftdi 0.9 plus microscrap/ftdi to C ext-ftdi 0.10, call by call.

## What changed

0.9 = Zephir ext (`Ftdi\FTDI::ftdi*` statics, objects carrying int `handle` fields) + `microscrap/ftdi` (global `ftdi_*` helpers and enums). 0.10 = one C ext: helpers are native functions, objects own pointers. Consumers drop `microscrap/ftdi`, require `ext-ftdi: ^0.10.0`.

| 0.9 | 0.10 |
|---|---|
| `Ftdi\FTDI::ftdiNew()`, `FTDI::ftdiUSBOpen(...)`, … | `ftdi_new()`, `ftdi_usb_open(...)`, … |
| `new FTDIContext` worked | private constructor; `ftdi_new()` only |
| `$context->handle <= 0` after `ftdiNew()` | `ftdi_new() === null` |
| `$tc->handle === 0` after submit | submit returned null |
| `ftdi_read_data()`, `ftdi_get_eeprom_buf()` → `""` on error | false |
| `ftdi_usb_find_all()` → `['count', 'listHandle']`, ints for devices | `['count', 'devices' => list<FTDIDevice>]` |
| `FTDI::setFT232HCbus(FTDIEeprom)` | `ftdi_set_ft232h_cbus(FTDIContext)` |
| `Microscrap\Bindings\FTDI\Enums\FtdiVendorId`, `FtdiProductId` | `Ftdi\FtdiVendorId`, `Ftdi\FtdiProductId` |
| `handle`, `contextHandle`, `bufHandle`, `eepromHandle` | gone |
| out-of-range sizes clamped | `ValueError` |
| libftdi1, no version checked | ≥ 1.5, checked by `config.m4` and the installers |

## Ported consumers

`microscrap/mpsse` 0.10 and `microscrap/scrapyard-usb` 0.10 use these names, null-check `ftdi_new()` and submits, map `ftdi_read_data()` false. Their CI installs `pie install php-io-extensions/ftdi:^0.10`.
