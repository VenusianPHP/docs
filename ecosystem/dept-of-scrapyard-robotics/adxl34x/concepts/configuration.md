# Configuration

circuits.adxl343 / circuits.adxl345 keys, how conjure() reads them, publish tag.

## Merge + publish

`register()`: `config/adxl343.php` → `circuits.adxl343`, `config/adxl345.php` → `circuits.adxl345`. `array_merge(package, app)` at that key: app's `configs` replaces the package's whole.[^provider]

`boot()`: tag `adxl34x-config` → `config/circuits/adxl343.php`, `config/circuits/adxl345.php`; catalog `adxl343` / `adxl345` when `circuit` bound.

```bash
php computer vendor:publish --tag=adxl34x-config
```

## Schema

Both files same shape.[^config] Each `configs` entry = arguments of the factory it names. Entry key = factory (`i2c`, `spi`) unless entry sets `protocol`, so an app keeps `left` / `right` beside `spi`. Unknown keys dropped by the catalog; a factory param without default missing from the entry → `CircuitException`.

| Key | Type | Default |
|---|---|---|
| `default_config` | string | `'i2c'` |
| `configs.i2c.driver` | string | `'none'` |
| `configs.i2c.device` | string\|int | `''` |
| `configs.i2c.slave` | int | `0x53` |
| `configs.spi.driver` | string | `'none'` |
| `configs.spi.device` | string\|int | `''` |
| `configs.spi.chip_select` | int | `0` |
| `configs.spi.speed` | int Hz | `5_000_000` |
| `configs.{i2c,spi}.int1` / `int2` | `{enabled: bool, driver, device, pin: int}` | disabled, pins 0 / 1 |
| `configs.*.boot_now` | bool | factory default `true` |

Driver `none` (package default) → the framework's none driver throws on connect: app must fill in its bench. See [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/connecting).

## Related

* [connecting](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/connecting) · [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/concepts/overview)

[^provider]: ADXL34xServiceProvider
[^config]: config/adxl345.php
