# Registers

GC9A01A datasheet registers as breakouts — field layouts and defaults, the Inter unlock, vendor registers, boot order.

## Rule

Field names + widths from datasheet command tables.[^datasheet] Breakouts `readonly`: one byte → `DataRegister` (`toBits` / `fromByte` / `none`); several → `toBytes` / `fromBytes`. Ints range-checked via `ChecksRegisterFields` → `invalidRegisterValue`; never masked. `fromByte` of an undefined enum value → `invalidRegisterValue`. Defaults = reference bring-up bytes, not datasheet power-on; test pins them.[^tests]

## Layouts

| Reg | Class | Bits / bytes | Default |
|---|---|---|---|
| `36` | `GC9A01MADControl` | MY MX MV ML BGR MH, 2 zero bits | `08` (BGR) |
| `B0` | `GC9A01RGBInterfaceSignalControl` | `0 RCM[1:0] 0 VSPL HSPL DPL EPL` | `01` |
| `B5` | `GC9A01BlankingPorch` | `VFP[6:0]`, `VBP[6:0]`, `HBP[4:0]` (3rd must be written, no effect). VFP+VBP ≤ 254 | `08 08 14` |
| `B6` | `GC9A01DisplayFunctionControl` | byte 1 meaningless `00`; `X GS SS SM X X X X`; optional `NL[5:0]` (`1D` = 240 lines) | `00 00`, NL unsent |
| `BA` | `GC9A01TearingEffectControl` | `te_pol te_width[6:0]` | `00` |
| `F6` | `GC9A01InterfaceControl` | `1100 DM[1:0] RM RIM`; DM 3 disabled | `C0` |
| `C1` | `GC9A01PowerControl1` | bit 1 VCIRE (external Vci) | `00` |
| `C3` | `GC9A01PowerControl2` | `0 vreg1_vbp_d[6:0]`: VREG1A = (vrh+vbp_d)·0.02+4, VREG1B = vbp_d·0.02+0.3 | `13` (datasheet `3C`) |
| `C4` | `GC9A01PowerControl3` | `0 vreg1_vbn_d[6:0]`: VREG2A = (vbn_d−vrh)·0.02−3.4, VREG2B = vbn_d·0.02+0.3 | `13` (datasheet `3C`) |
| `C9` | `GC9A01PowerControl4` | `00 vrh[5:0]` | `22` (datasheet `28`) |
| `A7` | `GC9A01PowerControl7` | `0100 vdd_ad[3:0]`: VCORE 1.483 V (0) … 2.385 V (C); D–F 1.713 V | `48` |
| `E8` | `GC9A01FrameRate` | `0 DINV[2:0] RTN1[3:0]`; optional `RTN2[7:0]` | `34`, RTN2 unsent |
| `E9` | `GC9A01SPI2DataControl` | `0000 2DATA_EN 2DATA_MDT[2:0]` | `00` |
| `EC` | `GC9A01ChargePumpFrequency` | `0 avdd[2:0] 0 avee[2:0]`, `vcl[2:0]`, `vgh[3:0] vgl[3:0]` | `33 02 88` |
| `F0`/`F2` | `GC9A01Gamma1` / `Gamma3` | `j0[1:0]·vr1[5:0]`, `j1[1:0]·vr2[5:0]`, `vr4[4:0]`, `vr6[4:0]`, `vr0[3:0]·vr13[3:0]`, `vr20[6:0]` | `45 09 08 08 26 2A` |
| `F1`/`F3` | `GC9A01Gamma2` / `Gamma4` | `vr43[6:0]`, `vr27[2:0]·vr57[4:0]`, `vr36[2:0]·vr59[4:0]`, `vr61[5:0]`, `vr62[5:0]`, `vr50[3:0]·vr63[3:0]` | `43 70 72 36 37 6F` |

Gamma 1/2 = negative polarity (`_n`), 3/4 positive (`_p`); 3 and 4 extend 1 and 2.

Datasheet gaps: `E8` command table has two parameters, its text one, reference writes one → `RTN2` optional. `B6` text lists two bytes + NL in table. `EC` has names + defaults only: nibble positions are the ones `33 02 88` fits. COLMOD `3A` DBI: `03` 12-bit, `05` 16, `06` 18 (`GC9A01ColorMode`).

## Inter unlock

`C1 C3 C4 C9 A7 E8 E9 EC F0–F3` accept writes only after `FE` then `EF`: `interRegisterEnable()`. Boot does it. Only HW / SW reset locks again.

## Vendor registers

Not in datasheet: `62 63 64 66 67 70 74 84–90 98 AE BC BD BE CD DF E1 EB ED FF`. 31 cases of `GC9A01VendorRegister`, named `VENDOR_<addr>`, one payload each from reference sequence (Waveshare, Adafruit, TFT_eSPI, Arduino_GFX agree). No fields: meaning unpublished. `writeVendorRegister()` sends one. Documented later → move to a breakout.

## Boot order

Reset (RST high/low/high, 10 ms each) → `EF`, `EB`, `FE`, `EF`, `EB` → `84–8F` → `B6`, `36`, `3A` → `90 BD BC FF` → `C3 C4 C9` → `BE E1 DF` → `F0–F3` → `ED AE CD 70` → `E8` → `62 63 64 66 67 74 98` → `35` (no param) → `21|20` per `invert_display` → `11` +120 ms → `29` +20 ms.[^boot] Config keys the setters keep current: `mad_ctrl`, `color_mode`, `display_fn_ctrl`, `power_control_2..4`, `frame_rate`, `gamma_1..4`, `invert_display`, `display_on`, `sleep_mode_on`. Others send only.

## Related

* [overview](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/overview) · [drawing](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/gc9a01/concepts/drawing-frames)

[^datasheet]: Datasheet
[^tests]: register layout tests
[^boot]: GC9A01Bootstrap
