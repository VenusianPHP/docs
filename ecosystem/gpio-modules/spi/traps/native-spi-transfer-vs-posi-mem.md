# Native spi_transfer vs posi_mem

Device reflects on spi_transfer for an int-first native path; otherwise uses posi_mem_*; wrong signature would recurse into the procedural helper.

## Symptom

`spi_transfer(...)` returns `false`, recurses until a stack overflow, or never exercises the expected native / memory path.

## Cause

`Device::spiTransfer` has two supported paths:[^device][^readme]

1. **Native fast path** — if `function_exists('spi_transfer')` and Reflection shows the first parameter type is **`int`**, call `\spi_transfer($dev->fd, $transfers)`. That signature belongs to a low-level extension, not this package’s helper.
2. **`posi_mem_*` path** — otherwise pack every `spi_ioc_transfer` and issue one `SPI_IOC_MESSAGE(N)` via `ioctl`. Chip select stays asserted across the segments; `csChange` on the last one keeps it asserted after the message. A zero-length segment is allowed.

`posi_mem_*` always exists because `ext-posi` is required, so there is no third branch; `false` is a failed transfer.

This package’s procedural helper is `spi_transfer(SPIDevice $dev, …)`. Calling that from `Device` without the int-type check would **recurse** back into `Device::spiTransfer`.[^helpers][^device]

## Mitigation

- Ensure **ext-posi** `^0.10.0` is loaded; it provides `posi_mem_*` for when no native int-first `spi_transfer` exists.[^readme]
- When adding or diagnosing a native extension helper, keep the first argument as `int $fd` — that is what the Reflection gate looks for.[^device]
- Do not “fix” transfers by having `Device` call the global helper without the type check.

## Related

* [Helpers → Device → posix](/docs/{{version}}/ecosystem/gpio-modules/spi/architecture/helpers-device-posix)
* [Half-duplex vs full-duplex](/docs/{{version}}/ecosystem/gpio-modules/spi/traps/half-duplex-vs-full-duplex)

[^device]: spiTransfer native vs posi_mem paths
[^readme]: Transfer path documentation
[^helpers]: Procedural spi_transfer takes SPIDevice
[^agents]: Transfer-path OKF map entry
