# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Revision**: 0.10.0 — [overview](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/overview), [index](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/overview): `gpio/*`, `microscrap/mpsse` and `ext-ftdi` ^0.10; `microscrap/ftdi` is gone (ext-ftdi 0.10 absorbed it, the VID/PID enums are `Ftdi\FtdiVendorId` / `Ftdi\FtdiProductId`). ext-ftdi 0.10 returns null from `ftdi_new()` and the submit functions on failure (no int `handle`), and false from `ftdi_read_data()`; the serial link still reads a lost device as "". [mpsse](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/mpsse): a named pool is refused with `offloadPoolUnsupported`.

### 2026-09-25
* **Creation**: bundle for 0.9 — [overview](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/overview), [ftdi-bridge](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/ftdi-bridge), [mpsse](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/mpsse), [digital](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/digital-io), [uart](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/uart), [testing](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/testing).
