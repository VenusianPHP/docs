# Overview

JD79661 ePaper driver for scrapyard-io/framework 0.10 — identity, requires, boot, errors.

## Identity

`dept-of-scrapyard-robotics/jd79661` **0.10.0**, alias `dev-main` → `0.10.x-dev`, namespace `DeptOfScrapyardRobotics\Displays\JD79661\`, provider `Providers\JD79661ServiceProvider`, catalog slug `jd79661`. New in 0.10, from the 0.4.3 driver[^old] and Adafruit's tested driver.[^adafruit]

Requires split components only: `gpio/contracts`, `gpio/integrated-circuits`, `venusian-surface/contracts`, `venusian-voyager/nuts-and-bolts`, `venusian-voyager/vessel`.

## Shape

`JD79661` = `Bootable` + `DisplayPanel` + `RefreshesOnCommand`.[^panel] Not `WindowAddressable` (whole frames), not `Switchable`. Full refresh only.

## Boot

RST high 20 / low 40 / high 50 ms → BUSY → 10 ms → `4D 78` (magic init, first) → `00 8F 29` → `01 07 00` → `03 10 54 44` → `06 05 00 3F 0A 25 12 1A` → `50 37` → `60 02 02` → `61` sources rounded to 8, height (`00 80 00 FA`) → `E7 1C` `E3 22` `B4 D0` `B5 03` `E9 01` → `30 08` → `04` → BUSY.[^bootstrap] BUSY low = busy. PSR `8F` is Adafruit's; the 0.4.3 driver used `0F`. FT232H: 309 ms.

## Errors

`JD79661Exception` → `CircuitException`: `busyTimeout`, `spiWriteFailed`, `wholeFrameOnly`, `wrongByteCount`, `unsupportedRefreshMode`, `invalidGeometry` (TRES 16-bit), `invalidRegisterValue`, `invalidProperty`, `notConnected`, `incompletePin`, `invalidSpiMode`, `invalidSpiClock`, `wrongSpiMode`, `invalidPacketSize`.

[^panel]: JD79661
[^bootstrap]: JD79661Bootstrap
[^adafruit]: Adafruit_JD79661
[^old]: 0.4.3 driver
