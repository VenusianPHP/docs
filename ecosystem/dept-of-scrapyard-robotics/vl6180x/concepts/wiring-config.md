# Wiring config

circuits.vl6180x keys merged by the provider and the vl6180x-config publish tag.

## Merge + publish

`register()` merges `config/vl6180x.php` under `circuits.vl6180x`; app values win.[^provider][^config] `boot()` publishes to `config/circuits/vl6180x.php`, tag `vl6180x-config`; `circuit` bound → `addCircuit('vl6180x')`. `conjure()` passes the keys to `i2c()`.

## Keys

| Key | Default |
|---|---|
| `default_config` | `'i2c'` |
| `configs.i2c.driver` / `device` | `'none'` / `''` |
| `configs.i2c.slave` | 0x29 |
| `configs.i2c.gpio1` | `enabled` false, `driver` none, `device` '', `pin` 0 |
| `configs.i2c.xshut` | same, `pin` 1 |
| `configs.i2c.boot_now` | true (factory default) |

[^provider]: VL6180XServiceProvider
[^config]: config/vl6180x.php
