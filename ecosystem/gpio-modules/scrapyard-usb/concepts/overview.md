# Overview

What scrapyard-usb 0.10 ships, where it sits, how the provider wires the four drivers together, how devices are named, and what rides the loop.

## Stack position

```
ext-ftdi                         1:1 libftdi1 + libmpsse calls
  → microscrap/{ftdi,mpsse}      PHP bindings: FtdiProductId, MPSSE, MPSSERecording
    → microscrap/scrapyard-usb   this package: the `usb` driver per protocol
      → scrapyard-io/framework (gpio/*)   managers, transports, loop and via() machinery
```

Requires `gpio/{contracts,digital,i2c,spi,uart,nuts-and-bolts}` ^0.10, `microscrap/mpsse` ^0.10 and `ext-ftdi` ^0.10. No PWM.

## Provider

`ScrapyardUSBServiceProvider::boot()` extends `usb` on four managers. I2C and SPI drivers are built with the manager's `usb` DigitalIO driver instance, so a context opened for I2C or SPI is registered on DigitalIO too and its spare lines are pins at once:

| Manager | Driver | Built with |
|---|---|---|
| DigitalIO | `MpsseDigitalIOConnectionDriver` | — |
| I2C | `MpsseI2CConnectionDriver` | the `usb` DigitalIO driver |
| SPI | `MpsseSPIConnectionDriver` | the `usb` DigitalIO driver |
| UART | `FtdiUARTConnectionDriver` | — |

## Device names

- **MPSSE (DigitalIO, I2C, SPI):** `MpsseSupportedDevice` values — `ft232h`, `ft2232hl-a`, `ft2232hl-b`, `ft4232hl-a` … `ft4232hl-d`. An int or unknown name throws.
- **UART:** `FtdiProductId` case name, case-insensitive (`ft232h`, `ft2232h`, `ft4232h`, `ft232r`, `ft230x`, …), or the USB product id as decimal or `0x` hex. libftdi opens interface A.

Both name spaces meet in [ftdi-bridge.md](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/ftdi-bridge).

## Loop

Nothing here has an fd `stream_select` can watch: libusb completions arrive as write-readiness on usbfs (Linux) or on libusb's own pipe (macOS). So everything that waits on the loop is timer-driven:

- MPSSE pump: 1 ms timer while a turn is held or waiting ([mpsse.md](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/mpsse)).
- Digital input: sampled every `pollEvery()` ms, default 10 ([digital.md](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/digital-io)).
- UART intake: sampled every 10 ms ([uart.md](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/uart)).

## via()

MPSSE jobs never leave the process — libusb holds the device claim — so `via()` runs a job in a loop fiber against the real slave, and a named worker pool is refused (`offloadPoolUnsupported`). See [mpsse.md](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/mpsse).
