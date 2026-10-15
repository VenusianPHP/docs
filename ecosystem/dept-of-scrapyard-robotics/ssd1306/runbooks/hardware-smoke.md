# Hardware smoke

Proving a change on the two benches — Pi 5 SSD1306 over I2C, FT232H SSD1306 over SPI — with a scratch script booted through the real providers and a Surface framebuffer.

## Rule

Pest suite stays hardware-free. Panels are proven by scratch scripts outside the repo, never committed. Someone watches the panel: a run with no eyes on it proves only that the bus took the bytes.

## Benches

| Bench | Bus | Lines |
|---|---|---|
| Raspberry Pi 5 (`fnk`), driver `native` | I2C bus 1, 0x3C | — |
| Mac + FT232H (0403:6014), driver `usb` | SPI, `chip_select` 0 = D4 (GPIO0) | DC → D5 (pin 1), RST → D6 (pin 2) |

FT232H breakout's I2C switch ties D1 to D2: off for SPI.

## Scratch project

Composer project outside the repo: this package by path repo, `venusian-surface/framebuffers` (for packing), the adapter (`microscrap/scrapyard-linux` or `microscrap/scrapyard-usb`), `gpio/digital`, `gpio/i2c`, `gpio/spi`, `venusian-voyager/io-pools`, `venusian-voyager/config`. Package or extension version not on Packagist yet → path repo / `--ignore-platform-req` in the scratch project only. Extension 0.10 not installed system-wide → build it in scratch, run `php -n -d extension=<scratch>/modules/<ext>.so`.

Boot like an app: stub `FrameworkCore` container with `config`, `registerInstance(Loop::class, $loop)`, then `register()` + `boot()` of `I2CServiceProvider`, `SPIServiceProvider`, `DigitalIOServiceProvider`, `UARTServiceProvider`, `PWMServiceProvider`, `IntegratedCircuitsServiceProvider`, the adapter's provider, `SSD1306ServiceProvider`. Define `config()` over the container's repository (`CircuitRegistry::conjure()` calls it). Then `app('circuit')->conjure('ssd1306')`.

Pi copy: `COPYFILE_DISABLE=1 tar --no-mac-metadata --no-xattrs --exclude vendor --exclude .git -czf - … | fnk 'tar -xzf - -C ~/ssd-smoke'`; remove `~/ssd-smoke` after. Announce each run with `say` before the panel lights.

## Checks

Pause a few seconds per step so the watcher can confirm each.

1. `conjure()` → `hasBooted()`, size, transport class, boot time.
2. Framebuffer from `formatSpec()`: border, both diagonals, 8×8 block top-left; `flush()` → `transmit(0, 0, …)`. First bytes `FF 01 FD FF`.
3. 32×16 block at the centre via `flushRegion()` → `transmit()` with origin and size: rest of picture unchanged.
4. Clear, switch `addressing_mode` to vertical, page, horizontal; same frame each time: identical picture.
5. `contrast` 0x01 then 0xFF, `invert_display` on/off, `display_on` off/on (picture kept).
6. 20 full frames, timed. Clear, `display_on = false`, `close()`.

Expected numbers: [drawing live reference](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/drawing-frames#live-reference).

## Related

* [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/drawing-frames) · [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/concepts/connecting-an-ssd1306)
