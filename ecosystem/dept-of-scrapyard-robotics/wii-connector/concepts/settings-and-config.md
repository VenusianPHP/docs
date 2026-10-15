# Settings and config

WiiConnectorConfiguration and WiiNunchuckConfiguration, magic properties, the circuits.wii-connector config file and its publish tag.

## Configuration

| Key | Default | Class |
|---|---|---|
| `hold_ms` | 500 | all |
| `invert_y` | true | all |
| `init_wait_ms` | 100 | all |
| `read_delay_us` | 3000 | all |
| `accel_zero` | 512 | `WiiNunchuckConfiguration` |
| `accel_counts_per_g` | 256 | `WiiNunchuckConfiguration` |

[^configuration] [^nunchuck-configuration] `get()` / `set()`; unknown key throws. `WiiNunchuck` constructor requires the Nunchuck configuration.

## Properties

All: `identifier`, `extension_id` (bus), `report`, `buttons`, `hold_ms` / `invert_y` (writable). Classic family: `d_pad`. Wii Classic: `left_stick`, `right_stick`, `left_trigger`, `right_trigger`, `axes`. Nunchuck: `stick`, `raw_acceleration`, `acceleration`, `x`, `y`, `z`. Subclass `__get` falls back to parent.

## Config file

Merged under `circuits.wii-connector`, published to `config/circuits/wii-connector.php`, tag `wii-connector-config`; `circuit` bound → `addCircuit('wii-connector', WiiExtension::class)`.[^provider] Keys: `default_config`; `configs.i2c.driver` / `device` / `slave` (0x52) / `controller` (class, default `WiiClassicController`); `boot_now`. `conjure()` passes them to `i2c()`. An app's `configs.i2c` replaces the package's whole entry, so it names `controller` itself.

[^configuration]: WiiConnectorConfiguration
[^nunchuck-configuration]: WiiNunchuckConfiguration
[^provider]: WiiConnectorServiceProvider
