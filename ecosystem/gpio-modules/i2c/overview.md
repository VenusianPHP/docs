# Overview

> Docs (production): ScrapyardIO · microscrap/i2c 0.10.x

> **Docs (production):** [ScrapyardIO · microscrap/i2c 0.10.x](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/i2c/0.10.x/overview)

[![Docs](https://img.shields.io/badge/docs-ScrapyardIO-0ea5e9?logo=readthedocs&logoColor=white)](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/i2c/0.10.x/overview)
[![Packagist Version](https://img.shields.io/packagist/v/microscrap/i2c.svg?label=packagist)](https://packagist.org/packages/microscrap/i2c)
[![PHP Version Require](https://img.shields.io/packagist/php-v/microscrap/i2c.svg)](https://packagist.org/packages/microscrap/i2c)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/microscrap/i2c/tree/HEAD/LICENSE)
[![Requires ext-posi](https://img.shields.io/badge/ext--posi-%5E0.10-777bb4?logo=php&logoColor=white)](https://github.com/php-io-extensions/posi)

PHP library that wraps the [**posi**](https://github.com/php-io-extensions/posi) extension (`ext-posi`) with global helpers, enums, and data objects. Every helper delegates to a facade class under `Microscrap\Bindings\I2C`.

This project provides PHP bindings to the Linux i2c-dev character device API, mirroring the public surface of the userspace [`i2c-tools`](https://git.kernel.org/pub/scm/utils/i2c-tools/i2c-tools.git/) / `<linux/i2c-dev.h>` family.

This is the **bindings** package — not the native extension. Ecosystem docs: [`0.10.x`](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/i2c/0.10.x/overview).

## Highlights

* Open an I²C bus (`/dev/i2c-0`, `/dev/i2c-1`, etc.) and bind it to a slave address in one call
* Raw byte-stream I/O via `i2c_read` / `i2c_write`
* Configure the kernel adapter — slave address, 10-bit addressing, PEC, retries, timeout
* Query controller capabilities through the `I2CFuncFlag` bitmask (`I2C_FUNCS` ioctl)
* SMBus convenience helpers: quick, byte, byte-data, word-data, and block transfers
* `I2C_RDWR` combined transactions — chain multiple read/write messages with repeated-START in a single ioctl
* Thin global `i2c_*` helper API — all functions are `function_exists`-guarded

## Requirements

* PHP `^8.4|^8.5|^8.6`
* Linux kernel with `i2c-dev` (`modprobe i2c-dev`) and a populated `/dev/i2c-N` device
* **ext-posi** `^0.10.0` — install from [php-io-extensions/posi](https://github.com/php-io-extensions/posi). It provides the `posix_*` / `ioctl` / `posi_mem_*` functions and the `O_*` constants this package calls; nothing else is required.

## Installation

Confirm **ext-posi** is loaded:

```bash
php -m | grep posi
```

Confirm the bus is visible (and that your user is in the `i2c` group, or run as root):

```bash
ls /dev/i2c-*
i2cdetect -y 1
```

```bash
composer require microscrap/i2c:^0.10.0
```

Autoloads `src/Helpers/i2c-bus.php` and `src/Helpers/i2c-smbus.php`, registering the global `i2c_*` functions.

## Usage

I²C transactions are driven through **global helper functions** (`i2c_open`, `i2c_read`, `i2c_write`, `i2c_smbus_*`, `i2c_rdwr`, etc.). All helpers delegate to the `Bus` facade and are only defined once (`function_exists` guard).

Enums live under `Microscrap\Bindings\I2C\Enums` — cases are **FULLY UPPERCASE**. The bus handle is `Microscrap\Bindings\I2C\DataObjects\I2CBus`.

---

### Example — read temperature and humidity from an AHT20

```php
<?php

use Microscrap\Bindings\I2C\DataObjects\I2CBus;

$bus = i2c_open('/dev/i2c-1', 0x38);
if (is_null($bus)) {
    exit("Failed to open bus or bind slave address\n");
}

// Soft init/calibration command.
i2c_write($bus, pack('C*', 0xBE, 0x08, 0x00));
usleep(20_000);

// Trigger a measurement and wait for the typical 80 ms conversion time.
i2c_write($bus, pack('C*', 0xAC, 0x33, 0x00));
usleep(80_000);

// Read back 7 status+data bytes.
$raw = i2c_read($bus, 7);
$bytes = array_values(unpack('C7', $raw));

$rawHumidity = (($bytes[1] << 12) | ($bytes[2] << 4) | ($bytes[3] >> 4)) & 0xFFFFF;
$rawTemp     = ((($bytes[3] & 0x0F) << 16) | ($bytes[4] << 8) | $bytes[5]) & 0xFFFFF;

printf(
    "Temp: %.2f C  RH: %.2f %%\n",
    ($rawTemp / 1048576.0) * 200.0 - 50.0,
    ($rawHumidity / 1048576.0) * 100.0,
);

i2c_close($bus);
```

---

### Example — combined transaction with `i2c_rdwr`

Read register `0x00` from a 24LC256 EEPROM at address `0x50` using a write-then-read transaction with a repeated-START in between:

```php
<?php

use Microscrap\Bindings\I2C\Enums\I2CMsgFlag;

$bus = i2c_open('/dev/i2c-1', 0x50);

$result = i2c_rdwr($bus, [
    ['flags' => 0,                          'data' => "\x00\x00"], // write register address
    ['flags' => I2CMsgFlag::M_RD->value,    'len'  => 16],         // read 16 bytes
]);

if ($result === false) {
    exit("RDWR transaction failed\n");
}

echo bin2hex($result), "\n";

i2c_close($bus);
```

---

## API Reference

### Bus lifecycle and I/O

| Helper | Facade method | Description |
|---|---|---|
| `i2c_open(string $path, int $addr = 0x00)` | `Bus::i2cOpen` | Open `/dev/i2c-N` and bind slave address; returns `I2CBus\|null` |
| `i2c_close(I2CBus $bus)` | `Bus::i2cClose` | Close the file descriptor; returns 0 or -1 |
| `i2c_read(I2CBus $bus, int $len)` | `Bus::i2cRead` | Read up to `$len` bytes; returns `string\|false` |
| `i2c_write(I2CBus $bus, string $data)` | `Bus::i2cWrite` | Write `$data`; returns bytes written |

### Adapter configuration (ioctl)

| Helper | Facade method | Underlying ioctl |
|---|---|---|
| `i2c_set_slave_addr(I2CBus $bus, int $addr)` | `Bus::i2cSetSlaveAddr` | `I2C_SLAVE` |
| `i2c_set_slave_addr_force(I2CBus $bus, int $addr)` | `Bus::i2cSetSlaveAddrForce` | `I2C_SLAVE_FORCE` |
| `i2c_set_ten_bit(I2CBus $bus, bool $enable)` | `Bus::i2cSetTenBit` | `I2C_TENBIT` |
| `i2c_set_pec(I2CBus $bus, bool $enable)` | `Bus::i2cSetPec` | `I2C_PEC` |
| `i2c_set_retries(I2CBus $bus, int $retries)` | `Bus::i2cSetRetries` | `I2C_RETRIES` |
| `i2c_set_timeout(I2CBus $bus, int $timeout)` | `Bus::i2cSetTimeout` | `I2C_TIMEOUT` (10 ms units) |
| `i2c_get_funcs(I2CBus $bus)` | `Bus::i2cGetFuncs` | `I2C_FUNCS` — returns `I2CFuncFlag` bitmask |

All setters return `0` on success and `-1` on failure. `i2c_get_funcs` returns the raw 64-bit bitmask; mask it against the `I2CFuncFlag` enum cases to test individual capabilities.

### SMBus convenience helpers

These helpers are emulated on top of `posix_read` / `posix_write` against the bound slave address; they do **not** issue the `I2C_SMBUS` ioctl, so PEC computation, banked addressing, and the SMBus block-length byte are not performed automatically. They are convenient for the common register-access patterns used by most sensor datasheets.

| Helper | Facade method | Description |
|---|---|---|
| `i2c_smbus_write_quick(I2CBus $bus, SMBusReadWrite $rw)` | `Bus::i2cSmbusWriteQuick` | Address-only transaction; selects R/W bit |
| `i2c_smbus_read_byte(I2CBus $bus)` | `Bus::i2cSmbusReadByte` | Read one byte; returns `int\|false` |
| `i2c_smbus_write_byte(I2CBus $bus, int $value)` | `Bus::i2cSmbusWriteByte` | Write one byte |
| `i2c_smbus_read_byte_data(I2CBus $bus, int $reg)` | `Bus::i2cSmbusReadByteData` | Write register, read one byte back |
| `i2c_smbus_write_byte_data(I2CBus $bus, int $reg, int $value)` | `Bus::i2cSmbusWriteByteData` | Write register then byte |
| `i2c_smbus_read_word_data(I2CBus $bus, int $reg)` | `Bus::i2cSmbusReadWordData` | Write register, read little-endian 16-bit word |
| `i2c_smbus_write_word_data(I2CBus $bus, int $reg, int $value)` | `Bus::i2cSmbusWriteWordData` | Write register and little-endian 16-bit word |
| `i2c_smbus_read_i2c_block(I2CBus $bus, int $reg, int $len)` | `Bus::i2cSmbusReadI2cBlock` | Write register, read up to 32 bytes |
| `i2c_smbus_write_i2c_block(I2CBus $bus, int $reg, string $data)` | `Bus::i2cSmbusWriteI2cBlock` | Write register followed by up to 32 bytes |

Block transfers are capped at 32 bytes — the SMBus protocol limit — and return `false` / `-1` when out of range.

### Combined transactions

#### `i2c_rdwr(I2CBus $bus, array $messages): string|false`

Issues a single `I2C_RDWR` ioctl bundling one or more I²C messages with repeated-START between them (no STOP in between). Each `$messages[$i]` is an associative array:

| Key | Type | Description |
|---|---|---|
| `flags` | `int` | `I2CMsgFlag` bitmask (`0` for write, `I2CMsgFlag::M_RD->value` for read) |
| `data` | `string` | Bytes to write (write messages only) |
| `len` | `int` | Number of bytes to read (read messages only) |

Returns the concatenated bytes from every read message in the transaction (empty string if there are none), or `false` if the ioctl fails.

The Linux kernel limits a single combined transaction to **42 messages** (`I2C_RDWR_IOCTL_MAX_MSGS`).

---

## `I2CBus` data object

```php
final readonly class I2CBus {
    public int    $fd;   // open file descriptor
    public string $path; // device path (/dev/i2c-1)
    public int    $addr; // currently bound 7-bit slave address
}
```

The `$addr` field reflects the address bound at `i2c_open` time and is used by `i2c_rdwr` when populating each message's `addr` field. After calling `i2c_set_slave_addr` or `i2c_set_slave_addr_force`, the kernel's binding changes but the data object's `$addr` does **not** — reopen the bus if you need a matching record, or build the message list manually.

---

## Enums

All enums are `int`-backed with **FULLY UPPERCASE** cases that map directly to kernel constants.

### `I2COpCode` — ioctl request numbers (`<linux/i2c-dev.h>`)

| Case | Value |
|---|---|
| `I2C_RETRIES` | `0x0701` |
| `I2C_TIMEOUT` | `0x0702` |
| `I2C_SLAVE` | `0x0703` |
| `I2C_TENBIT` | `0x0704` |
| `I2C_FUNCS` | `0x0705` |
| `I2C_SLAVE_FORCE` | `0x0706` |
| `I2C_RDWR` | `0x0707` |
| `I2C_PEC` | `0x0708` |
| `I2C_SMBUS` | `0x0720` |

### `I2CMsgFlag` — `i2c_msg.flags` bitmask

| Case | Value | Meaning |
|---|---|---|
| `M_RD` | `0x0001` | Read transaction (otherwise write) |
| `M_TEN` | `0x0010` | 10-bit slave address |
| `M_STOP` | `0x8000` | Force STOP at end of message |
| `M_NOSTART` | `0x4000` | Skip START + address byte (chained writes) |
| `M_REV_DIR_ADDR` | `0x2000` | Toggle R/W bit on address byte |
| `M_IGNORE_NAK` | `0x1000` | Continue past a NACK |
| `M_NO_RD_ACK` | `0x0800` | Skip the master ACK on reads |

### `I2CFuncFlag` — values returned by `i2c_get_funcs`

| Case | Value |
|---|---|
| `I2C_FUNC` | `0x00000001` |
| `TENBIT_ADDR` | `0x00000002` |
| `PROTOCOL_MANGLING` | `0x00000004` |
| `SMBUS_PEC` | `0x00000008` |
| `NOSTART` | `0x00000010` |
| `SLAVE` | `0x00000020` |
| `SMBUS_BLOCK_PROC_CALL` | `0x00008000` |
| `SMBUS_QUICK` | `0x00010000` |
| `SMBUS_READ_BYTE` | `0x00020000` |
| `SMBUS_WRITE_BYTE` | `0x00040000` |
| `SMBUS_READ_BYTE_DATA` | `0x00080000` |
| `SMBUS_WRITE_BYTE_DATA` | `0x00100000` |
| `SMBUS_READ_WORD_DATA` | `0x00200000` |
| `SMBUS_WRITE_WORD_DATA` | `0x00400000` |
| `SMBUS_PROC_CALL` | `0x00800000` |
| `SMBUS_READ_BLOCK_DATA` | `0x01000000` |
| `SMBUS_WRITE_BLOCK_DATA` | `0x02000000` |
| `SMBUS_READ_I2C_BLOCK` | `0x04000000` |
| `SMBUS_WRITE_I2C_BLOCK` | `0x08000000` |
| `SMBUS_HOST_NOTIFY` | `0x10000000` |
| `SMBUS_BYTE` | `0x00060000` *(read + write)* |
| `SMBUS_BYTE_DATA` | `0x00180000` |
| `SMBUS_WORD_DATA` | `0x00600000` |
| `SMBUS_BLOCK_DATA` | `0x03000000` |
| `SMBUS_I2C_BLOCK` | `0x0C000000` |
| `SMBUS_EMUL` | `0x0EFF0008` *(emulatable in software)* |
| `SMBUS_EMUL_ALL` | `0x0FFF8008` |

```php
use Microscrap\Bindings\I2C\Enums\I2CFuncFlag;

$caps = i2c_get_funcs($bus);
if ($caps & I2CFuncFlag::I2C_FUNC->value) {
    echo "Plain I2C messages supported\n";
}
```

### `SMBusReadWrite` — direction for `i2c_smbus_write_quick`

| Case | Value |
|---|---|
| `WRITE` | `0` |
| `READ` | `1` |

### `SMBusSize` — transaction sizes (used by the underlying `I2C_SMBUS` ioctl)

| Case | Value |
|---|---|
| `QUICK` | `0` |
| `BYTE` | `1` |
| `BYTE_DATA` | `2` |
| `WORD_DATA` | `3` |
| `PROC_CALL` | `4` |
| `BLOCK_DATA` | `5` |
| `I2C_BLOCK_BROKEN` | `6` |
| `BLOCK_PROC_CALL` | `7` |
| `I2C_BLOCK_DATA` | `8` |

---

## Quick reference

| Helper | Signature |
|---|---|
| `i2c_open` | `(string $path, int $addr = 0x00): ?I2CBus` |
| `i2c_close` | `(I2CBus $bus): int` |
| `i2c_read` | `(I2CBus $bus, int $len): string\|false` |
| `i2c_write` | `(I2CBus $bus, string $data): int` |
| `i2c_set_slave_addr` | `(I2CBus $bus, int $addr): int` |
| `i2c_set_slave_addr_force` | `(I2CBus $bus, int $addr): int` |
| `i2c_set_ten_bit` | `(I2CBus $bus, bool $enable): int` |
| `i2c_set_pec` | `(I2CBus $bus, bool $enable): int` |
| `i2c_set_retries` | `(I2CBus $bus, int $retries): int` |
| `i2c_set_timeout` | `(I2CBus $bus, int $timeout): int` |
| `i2c_get_funcs` | `(I2CBus $bus): int` |
| `i2c_rdwr` | `(I2CBus $bus, array $messages): string\|false` |
| `i2c_smbus_write_quick` | `(I2CBus $bus, SMBusReadWrite $rw): int` |
| `i2c_smbus_read_byte` | `(I2CBus $bus): int\|false` |
| `i2c_smbus_write_byte` | `(I2CBus $bus, int $value): int` |
| `i2c_smbus_read_byte_data` | `(I2CBus $bus, int $reg): int\|false` |
| `i2c_smbus_write_byte_data` | `(I2CBus $bus, int $reg, int $value): int` |
| `i2c_smbus_read_word_data` | `(I2CBus $bus, int $reg): int\|false` |
| `i2c_smbus_write_word_data` | `(I2CBus $bus, int $reg, int $value): int` |
| `i2c_smbus_read_i2c_block` | `(I2CBus $bus, int $reg, int $len): string\|false` |
| `i2c_smbus_write_i2c_block` | `(I2CBus $bus, int $reg, string $data): int` |

---

## Notes

* **Slave address width.** `i2c_open` and `i2c_set_slave_addr` accept the 7-bit address (e.g. `0x38` for AHT20, `0x50` for 24LC256). The kernel composes the R/W bit during the transaction. For 10-bit devices, call `i2c_set_ten_bit($bus, true)` and pass the 10-bit address.
* **Word ordering.** `i2c_smbus_read_word_data` / `i2c_smbus_write_word_data` use little-endian byte order, matching the SMBus specification. Big-endian devices need a `bswap` after the read.
* **PEC.** Enabling `i2c_set_pec($bus, true)` only affects the kernel's `I2C_SMBUS` ioctl path. The SMBus helpers in this library emulate transactions through `posix_read` / `posix_write`, so the PEC byte (if required) must be appended manually.
* **Combined transactions vs sequential writes.** Most sensors are happy with a single `i2c_write` followed by an `i2c_read` (each a separate ioctl, each with its own STOP). Use `i2c_rdwr` when a device specifically requires a repeated-START between the register write and the data read.

## License

MIT. See [LICENSE](https://github.com/microscrap/i2c/tree/HEAD/LICENSE).
