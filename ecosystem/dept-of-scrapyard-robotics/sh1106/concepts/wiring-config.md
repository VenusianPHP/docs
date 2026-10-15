# Wiring config

circuits.sh1106 config keys, how conjure() reads them, how the provider merges them, and the sh1106-config publish tag.

## Merge + publish

`register()`: `config/sh1106.php` → `circuits.sh1106`; app values win. `boot()`: tag `sh1106-config` → `config/circuits/sh1106.php`; `circuit` bound → `addCircuit('sh1106', SH1106::class)`.[^provider]

```bash
php computer vendor:publish --tag=sh1106-config
```

## Schema

| Key | Type | Default |
|---|---|---|
| `default_config` | string | `'i2c'` |
| `configs.<name>.protocol` | `'i2c'` \| `'spi'` | the config's name |
| `configs.i2c.driver` / `device` | string / string\|int | `'none'` / `''` |
| `configs.i2c.slave` | int | 0x3C |
| `configs.spi.driver` / `device` | string / string\|int | `'none'` / `''` |
| `configs.spi.chip_select` | int | 0 |
| `configs.spi.speed` | int Hz | 4 000 000, max 4 MHz |
| `configs.spi.dc` / `rst` | `{driver, device, pin}` | pins 0 / 1 |
| `configs.*.panel` | `SH1106Configuration` ctor args by name | `{width: 128, height: 64}` |
| `configs.*.boot_now` | bool | true (factory default) |

`panel` key the constructor does not take → `invalidProperty`.[^config] `protocol` lets an app keep two panels: `left`, `right`, each `'protocol' => 'spi'`.

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/connecting-an-sh1106) · [configuration-object](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/sh1106/concepts/sh1106configuration)

[^provider]: SH1106ServiceProvider
[^config]: sh1106 config
