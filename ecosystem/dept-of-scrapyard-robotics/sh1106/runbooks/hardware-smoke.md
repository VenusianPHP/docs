# Hardware smoke

Proving a change on the FT232H bench (SH1106 over I2C) with a scratch script booted through the real providers and a Surface framebuffer.

## Rule

Pest suite stays hardware-free. Panels are proven by scratch scripts outside the repo, never committed. Someone watches the panel: a run with no eyes on it proves only that the bus took the bytes.

## Benches

| Bench | Bus | Lines |
|---|---|---|
| Mac + FT232H (0403:6014), driver `usb` | I2C, 0x3C | — |

SPI path: suite only. SPI module on the FT232H: `chip_select` 0 = D4, DC pin 1 = D5, RST pin 2 = D6.

## Script

Scratch dir outside the repo: copy the package (no vendor) and Surface `Contracts`, `NutsAndBolts`, `Framebuffers` as path repos (`venusian-surface/*` 0.10 not on Packagist); require the package, `venusian-surface/framebuffers`, `microscrap/scrapyard-usb`, `gpio/{digital,i2c,spi}`, `venusian-voyager/{io-pools,config}`; `composer update --ignore-platform-req=ext-ftdi --ignore-platform-req=ext-posi`. Build ext-ftdi 0.10 from `php-io-extensions/ftdi` in scratch (`phpize`, `configure`, `make`) and run `php84 -n -d memory_limit=128M -d extension=…/modules/ftdi.so smoke.php`.

Boot like an app: stub `FrameworkCore` container with `config`, `registerInstance(Loop::class, $loop)`, then `register()` + `boot()` of `I2CServiceProvider`, `SPIServiceProvider`, `DigitalIOServiceProvider`, `UARTServiceProvider`, `IntegratedCircuitsServiceProvider`, `ScrapyardUSBServiceProvider`, `SH1106ServiceProvider`. No `PWMServiceProvider`: the USB adapter does not pull gpio/pwm. Define `config()` over the container's repository (`CircuitRegistry::conjure()` calls it). Then `app('circuit')->conjure('sh1106')`. Announce each run with `say` before the panel lights.

## Checks

Pause a few seconds per step so the watcher can confirm each.

1. `conjure()` → size, boot time.
2. Framebuffer from `formatSpec()` via `writeRgba8()` (white = lit): 1-pixel border on all four edges, both diagonals, 16×16 block top-left; `flush()` → `transmit(0, 0, …)`. Both side edges visible = `column_offset` right.
3. `transmit(104, 40, 16 × 0xFF, 16, 8)`: bar lower right, rest unchanged.
4. `close()`.

Expected numbers: [drawing live reference](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/drawing-frames#live-reference).

## Related

* [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/drawing-frames) · [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/connecting-an-sh1106)
