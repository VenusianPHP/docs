# Connecting an SH1106

conjure() and the i2c() / spi() factories, sharing a bus, SPI mode and clock, DC and RST, building the transport by hand.

## conjure

`app('circuit')->conjure('sh1106')` → `circuits.sh1106` → named config (or `default_config`) → `SH1106::i2c()` / `spi()` with config keys as named args → booted panel. Keys: [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/wiring-config).

## i2c()

`SH1106::i2c(string $driver, string|int $device, int $slave = 0x3C, array $panel = [], bool $boot_now = true)`[^factories]

- Bus from `gpio.i2c`: `device()` if app already connected it, else `connectTo()->register()`.
- Address by SA0: `SAO_GROUNDED` 0x3C, `SAO_ENERGIZED` 0x3D.[^address]
- Command write `[0x00, register, ...args]`; data write `[0x40, ...packet]`, packet ≤ `max_packet_size` (≤ 8191: gpio/i2c message cap 8192 minus control byte).[^i2c]

## spi()

`SH1106::spi(string $driver, string|int $device, array $dc, array $rst, int $chip_select = 0, int $speed = 4_000_000, array $panel = [], bool $boot_now = true)`[^factories]

- `speed` outside 1 Hz – 4 MHz → refused before bus touched (datasheet: 250 ns clock cycle min).
- Bus not connected → opened mode 0 at `speed`. Already open → shared; mode 1 or 2 refused (chip shifts SDIN on rising SCLK edge; modes 0 and 3 both do).
- `$spi->speed($speed)` on this chip select whatever bus clock.
- `dc`, `rst` = `{driver, device, pin}` outputs from `gpio.digital`, opened after the bus: FT232H pins ride the SPI engine's context.[^conjure-tests]
- Command: DC low, `[register, ...args]`. Data: DC high, packets of `max_packet_size`; SPI adapters split long writes themselves, so no upper bound. `reset()`: RST high → low → high, 3 ms each (datasheet minimum low: 10 µs).[^spi]

FT232H (`microscrap/scrapyard-usb`): `chip_select` 0–3 = D4–D7, 4–11 = C0–C7; DigitalIO pin 1 = D5, pin 2 = D6.

## By hand

```php
$slave = app('gpio.i2c')->driver('native')->connectTo(1)->register()->device(1, 0x3C);
$panel = new SH1106(new SH1106I2CTransport($slave), new SH1106Configuration, boot_now: true);
```

## Related

* [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/overview) · [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/wiring-config) · [configuration-object](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/sh1106configuration)

[^factories]: ConjuresSH1106
[^i2c]: SH1106I2CTransport
[^spi]: SH1106SPITransport
[^address]: SH1106I2CAddress
[^conjure-tests]: conjure tests
