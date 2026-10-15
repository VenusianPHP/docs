# Hardware smoke

Proving a change on the two benches — Pi 5 ST7796 on spidev, FT232H ST7789 over MPSSE SPI — with a scratch script booted through the real providers and a Surface framebuffer.

## Rule

Pest suite stays hardware-free. Panels are proven by scratch scripts outside the repo, never committed. Someone watches the panel: a run with no eyes on it proves only that the bus took the bytes.

## Benches

| Bench | Panel | Bus | DC | RST |
|---|---|---|---|---|
| Raspberry Pi 5 (`fnk`), driver `native` | ST7796 480×320 | spidev0.0 (`device` 0, `chip_select` 0) | GPIO22 (device 0) | GPIO24 (device 0) |
| Mac + FT232H (0403:6014), driver `usb` | ST7789 240×320 | `ft232h`, `chip_select` 0 = D4 | pin 1 = D5 | pin 2 = D6 |

## Scratch project

Composer project outside the repo: this package by path repo, `venusian-surface/framebuffers` (path repos to `dev/venusian/surface/src/Surface/{Contracts,NutsAndBolts,Framebuffers}` until Surface 0.10 is on Packagist), the adapter, `gpio/digital`, `gpio/spi`, `gpio/i2c`, `venusian-voyager/io-pools`, `venusian-voyager/config`. Extension 0.10 not installed system-wide → build it in scratch, run `php -n -d extension=<scratch>/modules/<ext>.so`.

Boot like an app: stub `FrameworkCore` container with `config`, `registerInstance(Loop::class, $loop)`, then `register()` + `boot()` of `I2CServiceProvider`, `SPIServiceProvider`, `DigitalIOServiceProvider`, `UARTServiceProvider`, `PWMServiceProvider`, `IntegratedCircuitsServiceProvider`, the adapter's provider, `ST77xxServiceProvider`. Define `config()` over the container's repository. Then `app('circuit')->conjure('st7796' | 'st7789')`.

Pi copy: `COPYFILE_DISABLE=1 tar --no-mac-metadata --no-xattrs --exclude vendor -czf - … | fnk 'tar -xzf - -C ~/st-smoke'`; remove `~/st-smoke` after. Announce each run with `say` before the panel lights.

## Checks

Pause a few seconds per step so the watcher can confirm each.

1. `conjure()` → `hasBooted()`, size, spec depth, boot time.
2. `fill()` red, green, blue, white: colours right (BGR bit and inversion).
3. RGBA8 pattern → `writeRgba8()` into a framebuffer in `formatSpec()` → `flush($spec, true)` → `transmit()`: white border, R/G/B/W bars, grey ramp, yellow square top-left.
4. 64×64 magenta region at the centre: rest unchanged.
5. Quarter turn: new `{Chip}MADControl` with MV and MX toggled; `width()` / `height()` swap; redraw: yellow square in the new top-left. Turn back, redraw.
6. 10 full frames timed; `invert_display` toggle; `display_on` off / on (picture kept); black fill; `close()`.

Expected numbers: [drawing live reference](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames#live-reference).

## Related

* [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames) · [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/connecting-an-st77xx-panel) · [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings)
