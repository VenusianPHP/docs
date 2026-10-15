# Connecting

conjure() and the spi() factory, circuits.gc9a01 keys, SPI mode and clock, DC and RST, FT232H pin numbers, building the transport by hand.

## conjure

`app('circuit')->conjure('gc9a01')` reads `circuits.gc9a01`, picks `default_config` (or named), calls `GC9A01::spi()` with that entry's keys.[^factory] Booted unless `boot_now: false`.

Factory params = config keys: `driver`, `device`, `dc`, `rst`, `chip_select` 0, `mode` 0, `speed` 10 000 000, `mad_ctrl` `[]`, `invert_display` null, `boot_now` true. New key = new param, and reverse.

`dc` / `rst` = `{driver, device, pin}`; missing part → `incompletePin`.

## Bus rules

* Bus not connected → factory opens it in `mode`. Bus already open in another mode → `wrongSpiMode`.
* Chip select clocked at `speed` via transport `speed()`, whatever bus runs. Without it FT232H adapter runs 400 kHz.
* Bus first, DC + RST after: on FT232H pins ride bus's USB context.
* Bad `mode` / `speed` refused before bus touched.
* `invert_display` null → controller default (on). `mad_ctrl` flags → `GC9A01MADControl` named args.

## FT232H

`chip_select` numbers = GPIO pins: 0–3 D4–D7, 4–11 C0–C7. Digital pins same space. Bench: CS 0 = D4, DC 1 = D5, RST 2 = D6, `driver` `usb`, `device` `ft232h`, 10 MHz.

## Provider

Merges `config/gc9a01.php` under `circuits.gc9a01`: app's top-level keys win, `configs` is replaced whole when app sets it.[^provider] Publish tag `gc9a01-config` → `config/circuits/gc9a01.php`. Catalog `addCircuit('gc9a01', GC9A01::class)` only when `circuit` bound.

## By hand

`new GC9A01(new GC9A01SPITransport($spi, $dc, $rst), new GC9A01Configuration, boot_now: true)` with SPI + output transports from `gpio.spi` / `gpio.digital`.

## Related

* [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/overview) · [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/drawing-frames) · [hardware smoke](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/runbooks/hardware-smoke)

[^factory]: ConjuresOverSPI
[^provider]: GC9A01ServiceProvider
