# Connecting an ST77xx panel

conjure() and the spi() factory, SPI mode and clock, sharing a bus, DC and RST, building the transport by hand.

## conjure

`app('circuit')->conjure('st7789')` → `circuits.st7789` → named config (or `default_config`) → `ST7789::spi()` with config keys as named args → booted panel. Same for `st7735`, `st7796`. Keys: [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/wiring-config).

## spi()

`{Chip}::spi(string $driver, string|int $device, array $dc, array $rst, int $chip_select = 0, int $mode = 0, int $speed = 10_000_000, ?int $width = null, ?int $height = null, array $mad_ctrl = [], ?int $x_offset = null, ?int $y_offset = null, ?bool $invert_display = null, bool $boot_now = true)`[^factory]

- `mode` not 0–3 or `speed` < 1 → refused before bus touched.
- Bus not connected → opened in `mode` at `speed`. Already open → shared; another mode refused.
- `$spi->speed($speed)` on this chip select whatever bus clock. Default 10 MHz, not the adapter's (FT232H adapter default 400 kHz).
- `dc`, `rst` = `{driver, device, pin}` outputs from `gpio.digital`, opened after the bus: FT232H pins ride the SPI engine's context.[^conjure-tests]
- Null `width` / `height` / offsets / `invert_display` → controller defaults. `mad_ctrl` = named flags of `{Chip}MADControl`.

## Transport

`new ST77xxSPITransport(SPITransport $transport, DigitalOutTransport $dc, DigitalOutTransport $rst, int $max_packet_size = 2048)`[^transport]

- `command(reg, params)`: DC low → `[reg]` → params as data, DC high.
- `data(array|string)`: DC high, packets ≤ `max_packet_size`; SPI adapters split long writes themselves.
- `reset(us)`: RST high → low → high, `us` each. `close()`: DC + RST `close()`.

## Benches

| Bench | `device` | `chip_select` | DC | RST |
|---|---|---|---|---|
| Pi 5, driver `native` | 0 (spidev0) | 0 (CE0) | device 0 pin 22 | device 0 pin 24 |
| FT232H, driver `usb` | `ft232h` | 0 (D4) | pin 1 (D5) | pin 2 (D6) |

FT232H `chip_select` 0–3 = D4–D7, 4–11 = C0–C7.

## By hand

```php
$spi = app('gpio.spi')->driver('native')->connectTo(0)->mode(0)->speed(10_000_000)->register()->device(0, 0);
$pins = app('gpio.digital')->driver('native')->connectTo(0)->register();
$panel = new ST7796(new ST77xxSPITransport($spi, $pins->output(0, 22), $pins->output(0, 24)), new ST7796Configuration, boot_now: true);
```

## Related

* [wiring-config](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/wiring-config) · [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview)

[^factory]: ConjuresOverSPI
[^transport]: ST77xxSPITransport
[^conjure-tests]: conjure tests
