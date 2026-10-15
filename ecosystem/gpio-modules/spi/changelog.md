# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Update**: `SPITransfer::$txAddress` points `tx_buf` at memory with no copy (rx discarded); `Device::spiTransferStructs()` packs the structs on its own. Pinned by `tests/TransferStructsTest.php`.

### 2026-10-03
* **Update**: ported to 0.10.0 against `ext-posi` ^0.10.0, a C rewrite where `posix_*`, `ioctl`, `posi_mem_*` are native global functions. `microscrap/posix` is gone from `require`; `spi_open` opens with the `O_RDWR | O_CLOEXEC` constants the extension registers. The `posi_mem_*` transfer path lost its `function_exists` guard. Docs URLs now `0.10.x`; suggest is `scrapyard-io/framework` ^0.10.0.

### 2026-09-24
* **Fix**: the posi path sends every segment in one `SPI_IOC_MESSAGE(N)`; it used to send one message per segment, dropping chip select between them. Zero-length segments allowed. `spi_open` opens with `O_CLOEXEC`. [Native vs posi_mem](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/native-spi-transfer-vs-posi-mem) updated.
* **Update**: relabeled 0.8.0 → 0.9.0 with `ext-posi` / `microscrap/posix` ^0.9.0. No code change.

### 2026-09-14
* **Update**: relabeled 0.7.0 → 0.8.0 with `ext-posi` / `ext-ftdi` 0.8.0. No code change.

## Log

### 2026-08-10

* **Creation**: Initial OKF v0.2 bundle for `microscrap/spi` **0.7.0** (gpio microscrap stack → 0.7) from package sources + `okf/SPEC.md` (GoogleCloudPlatform/knowledge-catalog).
* **Creation**: Orientation — [Package (0.7)](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/package-010), [Ecosystem docs](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/ecosystem-docs), [Pair with protocol peers](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/pair-with-protocol-peers).
* **Creation**: Architecture — [Helpers → Device → posix](/docs/{{version}}/ecosystem/gpio-modules/spi/architecture/helpers-device-posix).
* **Creation**: Conventions — [1:1 extension wrap](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/11-extension-wrap), [Enums for spidev flags](/docs/{{version}}/ecosystem/gpio-modules/spi/conventions/enums-for-spidev-flags).
* **Creation**: Traps — [Native `spi_transfer` vs `posi_mem`](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/native-spi-transfer-vs-posi-mem), [Half-duplex vs full-duplex](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/half-duplex-vs-full-duplex).
* **Creation**: Subdirectory indexes under `orientation/`, `architecture/`, `conventions/`, `traps/`; root [index.md](/docs/{{version}}/ecosystem/gpio-modules/spi/overview).
* **Note**: Root `AGENTS.md` already maps these concept paths; all concepts left `status: draft` pending human verification.
