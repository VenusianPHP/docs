# Wiring config

circuits.st7735, circuits.st7789 and circuits.st7796 config keys, how conjure() reads them, provider merge, and the st77xx-config publish tag.

## Merge + publish

`register()`: `config/{chip}.php` → `circuits.{chip}` for st7735, st7789, st7796; app values win. `boot()`: tag `st77xx-config` → `config/circuits/{chip}.php`; `circuit` bound → `addCircuit()` for all three.[^provider]

## Schema

Same for all three.[^config]

| Key | Default |
|---|---|
| `default_config` | `'spi'` |
| `configs.<name>.protocol` | the config's name |
| `configs.spi.driver` / `device` | `'none'` / `''` |
| `configs.spi.chip_select` | 0 |
| `configs.spi.mode` | 0 |
| `configs.spi.speed` | 10 000 000 |
| `configs.spi.width` / `height` | null → controller default |
| `configs.spi.mad_ctrl` | `[]` → controller default |
| `configs.spi.x_offset` / `y_offset` | null → 0 |
| `configs.spi.invert_display` | null → controller default |
| `configs.spi.dc` / `rst` | `{driver, device, pin}`, pins 0 / 1 |
| `configs.*.boot_now` | true (factory default) |

Width, height, offsets and `mad_ctrl` describe one orientation together; see [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings#orientation).

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/connecting-an-st77xx-panel)

[^provider]: ST77xxServiceProvider
[^config]: st7789 config
