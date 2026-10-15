# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: [spi](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/spi) — `PosixSPITransport` implements `WritesFromMemory`: `writeFrom()` sends memory spans as transfers pointing at them. Both message planners count each transfer rounded up to 128 bytes, as spidev does, so a message of many short transfers is no longer refused with EMSGSIZE. Pinned by `tests/SPI/SpidevMemoryMessagesTest.php`, `SpidevMessagesTest.php`; suite 60/60 on the Pi.
* **Revision**: 0.10.0 — [overview](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/overview) requires `gpio/*` and `ext-posi` ^0.10; `microscrap/posix` is gone (ext-posi 0.10 absorbed it), so the adapters use the extension's constants (`O_*`, `F_GETFL`/`F_SETFL`, `POLLIN`/`POLLOUT`). [i2c](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/i2c), [spi](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/spi): offloaded gigs run on a 0.10 worker pool. [testing](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/testing): CI installs posi ^0.10 and resolves the 0.10 splits.

### 2026-09-25
* **Creation**: bundle for 0.9 — [overview](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/overview), [digital](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/digital-io), [i2c](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/i2c), [spi](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/spi), [uart](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/uart), [pwm](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/pwm), [testing](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/testing).
