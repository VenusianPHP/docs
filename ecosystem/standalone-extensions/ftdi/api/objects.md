# Objects

FTDIContext, FTDIDevice, FTDITransferControl, FTDIVersionInfo, FTDIEeprom; ownership, the dependents registry, teardown order, live properties.

## Classes

All `final` in namespace `Ftdi`. Context/device/transfer: private constructor, `clone_obj = NULL`, `@not-serializable`, `@strict-properties`. Only functions create them.[^stub]

| Class | C state |
|---|---|
| `FTDIContext` | `ctx` (NULL after `ftdi_free()`), `initialized` (false between `ftdi_deinit()` and `ftdi_init()`), `strings[3]` (see [EEPROM](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/eeprom)), `dependents` HashTable handle → object |
| `FTDIDevice` | `libusb_device *` with own `libusb_ref_device` reference; `context` (referenced, NULL once gone) |
| `FTDITransferControl` | `ftdi_transfer_control *` (NULL once collected/cancelled), owned `buf`, `size`, `offset`, `context` |
| `FTDIVersionInfo` | readonly `major`, `minor`, `micro`, `versionStr`, `snapshotStr` |
| `FTDIEeprom` | readonly snapshot: 58 ints (every `enum ftdi_eeprom_value`, camelCase) + `manufacturer`, `product`, `serial` |

Enums: `FtdiVendorId: int` (`FTDI` 0x0403), `FtdiProductId: int` (`FT232R` 0x6001, `FT2232H` 0x6010, `FT4232H` 0x6011, `FT232H` 0x6014, `FT230X` 0x6015, `FT4232HP`, `FT4232HA`).

## Dependents

Device and transfer each hold a counted reference to their context and sit in its `dependents` table (`ftdi_adopt`). Freeing one removes it and drops the reference (`ftdi_disown`). So a context normally outlives dependents.[^ftdi-c]

Teardown order, enforced in C:

| Event | Pending transfers | Device refs |
|---|---|---|
| `ftdi_usb_close()` | cancelled | kept |
| `ftdi_deinit()`, `ftdi_init()` over initialised ctx | cancelled | dropped |
| `ftdi_free()` | cancelled | dropped |
| context `free_obj` (GC cycle, shutdown) | cancelled | dropped; dependents told context is gone |
| transfer `free_obj` while pending | cancelled | — |

Cancel = `ftdi_transfer_data_cancel(tc, {0,0})`: waits for libusb to confirm, frees `tc`. Buffer `efree`d after. `offset` kept for later reads. Device refs drop before `libusb_exit`, so libusb never frees a device a PHP object still points at.[^ftdi-c]

## Misuse

| Call | Result |
|---|---|
| any call on context `ftdi_free()` released (except `ftdi_free`, no-op) | `Error` "released by ftdi_free()" |
| call needing libusb state on deinitialised context | `Error` "call ftdi_init() first" |
| `ftdi_init`, `ftdi_deinit`, `ftdi_get_error_string` on deinitialised context | allowed |
| device from another context | `ValueError` "must come from ftdi_usb_find_all() on the same FTDIContext" |
| device whose context was deinitialised since | `Error` |
| `new`, `clone`, `serialize` | `Error` / `Exception` from engine |

## Live properties

Context and transfer properties are no slots: `read_property` reads the C struct each access. Context: `chipType`, `usbReadTimeout`, `usbWriteTimeout`, `interfaceIndex`, `baudrate`, `bitbangEnabled`, `bitbangMode`, `channel`, `inEndpoint`, `outEndpoint`, `readBufferChunkSize`, `writeBufferChunkSize`, `maxPacketSize`, `moduleDetachMode`, `errorStr`. Transfer: `completed` (1 once finished, collected or cancelled), `size`, `offset`.

Write, unset, `&`-reference → `Error`. `isset()` real. `var_dump`, `(array)`, `var_export`, `json_encode` and `toArray()` show live values; released context → empty array from casts, `Error` from `toArray()`.[^ftdi-c]

[^ftdi-c]: ftdi.c
[^stub]: ftdi.stub.php
