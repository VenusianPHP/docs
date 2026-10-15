# Half-duplex vs full-duplex

spi_read / spi_write are half-duplex via posix_read/write; use spi_transfer for byte-correlated full-duplex MOSI/MISO.

## Symptom

Register reads or JEDEC-style transactions look wrong: MISO bytes do not line up with what was clocked on MOSI, or a “read” only clocks dummy traffic without a proper full-duplex message.

## Cause

`spi_read` / `spi_write` go through ext-posi's `posix_read` / `posix_write` on the spidev FD — the kernel’s **half-duplex** path (dummy bytes out on read; MISO ignored on write).[^device][^readme]

True **full-duplex** (byte-for-byte correspondence between TX and RX) requires `spi_transfer` with one or more `SPITransfer` segments (`SPI_IOC_MESSAGE`).[^readme]

## Mitigation

- Use `spi_transfer($dev, new SPITransfer(...), …)` for sensor register reads, JEDEC ID, and any protocol where RX must match TX clocks.
- Reserve `spi_read` / `spi_write` for simple half-duplex bulk I/O where the kernel dummy / ignore semantics are acceptable.
- See transfer-path requirements in [Native `spi_transfer` vs `posi_mem`](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/native-spi-transfer-vs-posi-mem).

## Related

* [Helpers → Device → posix](/docs/{{version}}/ecosystem/gpio-modules/spi/architecture/helpers-device-posix)
* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/package-010)

[^readme]: Half-duplex vs full-duplex notes
[^device]: spiRead/spiWrite vs spiTransfer
[^helpers]: Global helper surface
