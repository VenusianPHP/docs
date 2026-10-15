# Settings and config

SeesawMiniGamepadConfiguration, magic properties, the circuits.seesaw-mini-gamepad config file and its publish tag.

## Configuration

| Key | Default |
|---|---|
| `hold_ms` | 500 |
| `invert_x` | true |
| `invert_y` | false |
| `button_interrupts` | false |
| `reset_wait_ms` | 500 |

`get()` / `set()`; unknown key throws.[^configuration] Chip can't report these → configuration is the truth. `setButtonInterrupts()` writes INTENSET / INTENCLR first.

## Properties

Read: `hardware_id`, `version`, `product_id` (bus), `hold_ms`, `invert_x`, `invert_y`, `button_interrupts`, `x`, `y`, `axes`. Write: `hold_ms`, `invert_x`, `invert_y`, `button_interrupts`.[^bootstrap]

## Config file

Merged under `circuits.seesaw-mini-gamepad`, published to `config/circuits/seesaw-mini-gamepad.php`, tag `seesaw-mini-gamepad-config`; `circuit` bound → `addCircuit('seesaw-mini-gamepad')`.[^provider] Keys: `default_config` 'i2c'; `configs.i2c.driver` / `device` / `slave` (0x50); `configs.i2c.irq` `enabled` / `driver` / `device` / `pin`; `hold_ms`, `invert_x`, `invert_y`, `button_interrupts`, `reset_wait_ms` (null → configuration default); `boot_now`. `conjure()` passes them to `i2c()`.

[^configuration]: SeesawMiniGamepadConfiguration
[^bootstrap]: SeesawMiniGamepadBootstrap
[^provider]: SeesawMiniGamepadServiceProvider
