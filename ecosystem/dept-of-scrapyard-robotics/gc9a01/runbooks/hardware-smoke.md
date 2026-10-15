# Hardware smoke

Proving a change on the FT232H bench — scratch script booted through the real providers with a Surface framebuffer.

## Rule

Pest suite hardware-free. Panel proven by scratch script outside repo, never committed. Someone watches panel: run with no eyes proves only bus took bytes. Announce with `say` before panel lights, from the shell, not from inside PHP.

## Bench

| Bench | Panel | Bus | DC | RST |
|---|---|---|---|---|
| Mac + FT232H (0403:6014), driver `usb` | GC9A01 240×240 | `ft232h`, `chip_select` 0 = D4 | pin 1 = D5 | pin 2 = D6 |

## Scratch project

Composer project outside repo: this package by path repo, `venusian-surface/framebuffers` (path repos to `venusian/surface/src/Surface/{Contracts,NutsAndBolts,Framebuffers}` until Surface 0.10 is on Packagist), `microscrap/scrapyard-usb`, `gpio/digital`, `gpio/spi`, `gpio/i2c`, `gpio/uart`, `venusian-voyager/io-pools`, `venusian-voyager/config`. Needs `ext-ftdi` 0.10 and `ext-fb`.

Boot like an app: stub `FrameworkCore` container with `config`, `register()` then `boot()` (where defined) of `DigitalIOServiceProvider`, `SPIServiceProvider`, `I2CServiceProvider`, `UARTServiceProvider`, `IntegratedCircuitsServiceProvider`, `ScrapyardUSBServiceProvider`, `GC9A01ServiceProvider`. Define `config()` over container's repository. Then `app('circuit')->conjure('gc9a01')`.

## Checks

Pause a few seconds per step so watcher can confirm each.

1. `conjure()` → `hasBooted()`, size, depth, boot time.
2. `fill()` red, green, blue, white: colours right.
3. RGBA8 pattern → framebuffer in `formatSpec()` → `flush($spec, true)` → `transmit()`: quadrants R top-left, G top-right, B bottom-left, W bottom-right; yellow marker at 12 o'clock, cyan at 3, black centre dot. Square corners are off the glass.
4. 64×64 magenta window at centre: rest unchanged.
5. MADCTL MX, MY, MV one at a time: pattern redrawn mirrored / swapped. Back to default, redraw.
6. 10 full frames timed; `invert_display` off / on; `display_on` off / on (picture kept); black fill; `close()`.

Expected numbers: [drawing live reference](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/drawing-frames#live-reference).

## Related

* [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/drawing-frames) · [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/connecting)
