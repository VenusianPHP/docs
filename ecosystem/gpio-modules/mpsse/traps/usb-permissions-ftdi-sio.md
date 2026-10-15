# Usb permissions ftdi sio

Linux ftdi_sio / missing udev rules commonly block MPSSE open even when ext-ftdi is loaded (ext-ftdi family issue).

## Symptom

`mpsse_open` / `MPSSE::open*` fails even though `php -m | grep ftdi` shows the extension and the device is plugged in. `MPSSE::errorString` (or the optional `&$error` from `mpsse_open`) may report access, busy, or driver-related failures.[^readme][^helpers]

## Cause

On Linux, the in-kernel `ftdi_sio` serial driver often claims FTDI devices first. Without a detach / blacklist / udev rule, userspace libftdi (via **ext-ftdi**) cannot open the device. Separately, insufficient USB permissions (no udev `MODE`/`GROUP` for the VID/PID) produce permission denials.[^readme]

This package only wraps MPSSE on top of FTDI — it does not install udev rules or unload kernel modules.[^composer][^mpsse]

## Mitigation

- Confirm **ext-ftdi**, and host libftdi are installed (see README OS packages).[^readme]
- On Linux: ensure the device is available to libusb/libftdi (unbind `ftdi_sio` / appropriate udev rules for `0x0403` products as needed).
- Check `$ctx->open` and `MPSSE::errorString($ctx)` after open attempts; `mpsse_open` returns `null` when open fails.[^helpers]
- Higher-level adapters may live in `scrapyard-io/framework` — still expect host USB setup to be correct.

## Related

* [Helpers → MPSSE → FTDI](/docs/{{version}}/ecosystem/gpio-modules/mpsse/architecture/helpers-mpsse-ftdi)
* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/mpsse/orientation/package-010)

[^readme]: Requirements and open usage
[^mpsse]: Open path uses FTDI / ftdi_* under the hood
[^helpers]: mpsse_open failure path and error string
[^composer]: Requires ext-ftdi
