# Controllers — boot and configuration

Per-controller boot sequences as sent, configuration fields and defaults for ST7735, ST7789 and ST7796.

## ST7735

Boot:[^st7735-boot] RST 150 ms ×3; `01` +150 ms; `11` +120 ms; `B1`/`B2` `01 2C 2D`; `B3` `01 2C 2D 01 2C 2D`; `B4 07`; `C0 A2 02 84`; `C1 C5`; `C2 0A 00`; `C3 8A 2A`; `C4 8A EE`; `C5 0E`; `20|21`; `36 C8`; `3A 05`; `E0`/`E1` 16 bytes; `13`; +10 ms; `29`; +100 ms. = Adafruit ST7735R.[^tests]

Config: `width` 128, `height` 128, `max_packet_size` 2048, `x_offset`/`y_offset` 0, `invert_display` false, `nfc` `ifc` `pfc`, `inversion_control` 0x07, `power_control_1`..`5`, `v_com_ctrl`, `mad_ctrl` (0xC8), `color_mode` COLOR16 (0x05), `gamma_positive`/`negative`.

## ST7789

Boot:[^st7789-boot] RST 3 ms ×3; `28`; `11` +120 ms; `36 mad`; `3A 55`; `B2 0C 0C 00 33 33`; `B7 35`; `BB 19`; `C0 2C`; `C2 01 FF`; `C3 12`; `C4 20`; `C6 0F`; `D0 A4 A1`; `E0`/`E1` 14 bytes; `21|20`; `13`; `29`.

Config: `width`/`height` 240, `max_packet_size` 2048, offsets 0, `mad_ctrl` (0x00), `color_mode` COLOR16 (0x55), `porch_ctrl`, `gate_ctrl`, `v_com_ctrl`, `lcm_ctrl`, `vdv_vrh_enable`, `vrh`, `vdv`, `frame_rate_ctrl`, `power_control_1`, gammas, `invert_display` **true** (IPS).

## ST7796

Boot:[^st7796-boot] RST 10 ms ×3; `28`; `11` +120 ms; `F0 C3`; `F0 96`; `36 28`; `3A 55`; `B4 01`; `B6 80 02 3B`; `E8 40 8A 00 00 29 19 A5 33`; `C1 06`; `C2 A7`; `C5 18`; `E0`/`E1` 14 bytes; `F0 3C`; `F0 69`; `20|21`; `13`; `29`. Extended registers only between the F0 unlock/lock pairs.

Config: `width` 480, `height` 320, `max_packet_size` 4092, offsets 0, `mad_ctrl` (0x28: MV + BGR), `color_mode` COLOR16, `inversion_ctrl`, `display_fn_ctrl`, `output_adjust`, `power_control_2`, `power_control_3`, `v_com_ctrl`, gammas, `invert_display` false.

## All three

Internal keys: `display_on`, `sleep_mode_on`. Null register args → breakout defaults in config ctor. Width, height, offsets follow later `mad_ctrl` writes ([settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings#orientation)).

## Related

* [settings](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/panel-settings) · [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/concepts/overview)

[^st7735-boot]: ST7735Bootstrap
[^st7789-boot]: ST7789Bootstrap
[^st7796-boot]: ST7796Bootstrap
[^tests]: boot-sequence tests
