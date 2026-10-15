# Configuration

SSD1680Configuration fields, register breakouts, properties, circuits.ssd1680-bw / -bwr keys and the publish tag.

## SSD1680Configuration

| Field | Default |
|---|---|
| `width` / `height` | 122 / 250 (≤ 176 / ≤ 296) |
| `gate_setting` | 0 (0x01 byte 3: TB, SM, GD) |
| `border_waveform` | `SSD1680BorderWaveform` → 0x05 |
| `display_update_control` | `SSD1680DisplayUpdateControl1` → 00 80 |
| `temperature_sensor` | `INTERNAL` (0x80) |
| `max_packet_size` | 4096 |
| `busy_timeout_ms` | 30 000 (BWR full refresh ≈ 15 s) |

Breakouts range-check every field, never mask.[^breakouts] Properties: any key reads; `border_waveform`, `display_update_control`, `temperature_sensor` write the chip then config.[^config]

## Config files

`config/ssd1680-bw.php`, `config/ssd1680-bwr.php` → `circuits.ssd1680-bw` / `-bwr`; tag `ssd1680-config`; catalog both.[^provider] Keys: `default_config` 'spi'; `driver`, `device`, `chip_select`, `mode`, `speed` (10 MHz), `width`, `height` (null → 122 × 250), `dc` / `rst` / `busy` (`{driver, device, pin}`), `pwr` (`enabled` false), `boot_now`.

[^config]: SSD1680Configuration
[^provider]: SSD1680ServiceProvider
[^breakouts]: register breakouts
