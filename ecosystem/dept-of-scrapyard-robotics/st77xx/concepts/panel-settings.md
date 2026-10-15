# Panel settings

Property reads and writes on ST77xx panels, the setters behind them, and orientation through MADCTL with size and offsets following.

## Properties

Read: any configuration key (`$panel->width`, `$panel->gamma_positive`, …).[^bootstrap]

Write (all chips): `display_on` → `setDisplay`; `sleep_mode_on` → `setSleepMode`; `invert_display` → `setDisplayInversion`; `mad_ctrl` → `setMADControl`; `color_mode` → `setPixelFormat`. Plus each chip's register keys → their setters (see [controllers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/controllers-boot-and-configuration)). Size, offsets, packet size → `invalidProperty`: size and offsets follow `mad_ctrl`.

State lives in configuration; driver never reads controller.

## MADCTL

`{Chip}MADControl(bottom_top_row_addresses, right_left_column_addresses, pixel_direction_vertical, bottom_top_refresh, bgr_order_mode, right_left_refresh)` → bits 7..2 = MY, MX, MV, ML, BGR, MH.[^mad]

## Orientation

Configured `width`, `height`, `x_offset`, `y_offset` and `mad_ctrl` describe one orientation together. A later `mad_ctrl` write moves all four:[^orientation] MX mirrors the column address, MY the row address, then MV exchanges them. Window at RAM column c0 (pw wide), row r0 (ph tall), RAM ram_cols × ram_rows:

| | x | width | y | height |
|---|---|---|---|---|
| MV off | MX ? ram_cols − pw − c0 : c0 | pw | MY ? ram_rows − ph − r0 : r0 | ph |
| MV on | MX ? ram_rows − ph − r0 : r0 | ph | MY ? ram_cols − pw − c0 : c0 | pw |

RAM: ST7735 132×162, ST7789 240×320, ST7796 320×480. Panel filling RAM → offsets stay 0. Checked against Adafruit's 135×240 ST7789 rotations: (52, 40), (40, 52), (53, 40), (40, 53).[^tests]

Quarter turn: toggle MV and MX together. Live: ST7789 240×320 → 320×240 and ST7796 480×320 → 320×480, pattern's top-left marker in the new top-left on both.

## Related

* [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/drawing-frames) · [controllers](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/controllers-boot-and-configuration)

[^bootstrap]: __get / __set
[^mad]: ST7789MADControl
[^orientation]: ST77xxOrientation
[^tests]: orientation tests
