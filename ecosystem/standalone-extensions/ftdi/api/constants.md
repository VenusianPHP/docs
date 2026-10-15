# Constants

Every ftdi.h enum member and numeric define as a header-valued constant, the two skipped, and keeping the list in step with libftdi.

## Rule

243 global constants in `ftdi.stub.php`, unprefixed as libftdi names them, each `@cvalue` of the `ftdi.h` symbol, so values follow the installed header.[^stub]

| Source in `ftdi.h` | Constants |
|---|---|
| `enum ftdi_chip_type` | `TYPE_AM` … `TYPE_230X` |
| `enum ftdi_parity_type`, `ftdi_stopbits_type`, `ftdi_bits_type`, `ftdi_break_type` | `NONE`, `ODD`, `EVEN`, `MARK`, `SPACE`, `STOP_BIT_*`, `BITS_7`, `BITS_8`, `BREAK_*` |
| `enum ftdi_mpsse_mode`, `ftdi_interface`, `ftdi_module_detach_mode` | `BITMODE_*`, `INTERFACE_*`, `*_SIO_MODULE` |
| `enum ftdi_eeprom_value` | `VENDOR_ID` … `USER_DATA_ADDR` (58) |
| `enum ftdi_cbus_func`, `ftdi_cbush_func`, `ftdi_cbusx_func` | `CBUS_*`, `CBUSH_*`, `CBUSX_*` |
| numeric `#define`s | MPSSE opcodes/flags (`MPSSE_*`, `SET_BITS_*`, `GET_BITS_*`, `TCK_DIVISOR`, `SEND_IMMEDIATE`, `WAIT_ON_*`, `CLK_*`, `DIS_*`/`EN_*`, `LOOPBACK_*`), `SIO_*` requests and flags, `FTDI_DEVICE_*_REQTYPE`, EEPROM bits (`INVERT_*`, `CHANNEL_IS_*`, `DRIVE_*`, `DRIVER_VCP*`, …) |

Skipped: `SIO_RESET_PURGE_RX`, `SIO_RESET_PURGE_TX`; ftdi.h wraps them in a deprecation that warns on use. `SIO_TCIFLUSH`/`SIO_TCOFLUSH` replace them.

Names like `NONE`, `ODD`, `MARK` are global as libftdi makes them; `microscrap/ftdi` exposed the same names. 1:1 keeps them.

## Enums

`Ftdi\FtdiVendorId`, `Ftdi\FtdiProductId`: int-backed, from `microscrap/ftdi`. Not in `ftdi.h`; values are FTDI's USB IDs. See [objects](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/objects).

## Keeping in step

Constants are written out in the stub, not scanned at build. On a libftdi release: open `$(pkg-config --variable=includedir libftdi1)/ftdi.h`, list every member of every `enum` and every `#define` with a numeric value, diff against `grep -o '@cvalue [A-Z0-9_]*' ftdi.stub.php`. Add each new name as a `@cvalue` block in its group, regenerate arginfo, extend `tests/SurfaceTest.php`. A name present only in newer libftdi raises the `config.m4` floor with it. See [build](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/runbooks/build-install-test).

[^stub]: ftdi.stub.php
