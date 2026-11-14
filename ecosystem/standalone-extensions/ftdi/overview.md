# Overview

![CI](https://github.com/php-io-extensions/ftdi/actions/workflows/ci.yml) ![Packagist](https://packagist.org/packages/php-io-extensions/ftdi)…

<div align="center" id="header">

<h2>ext-ftdi</h2>

<h4><code>libftdi1</code> bindings for PHP 8.4+: FTDI USB chips, MPSSE, async transfers and EEPROM</h4>


[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/ftdi/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/ftdi/actions/workflows/ci.yml)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/ftdi?style=flat-square)](https://packagist.org/packages/php-io-extensions/ftdi)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/ftdi/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/ftdi)
[![License](https://img.shields.io/github/license/php-io-extensions/ftdi?style=flat-square)](https://github.com/php-io-extensions/ftdi/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://www.intra2net.com/en/developer/libftdi/)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

An FTDI board turns any laptop into a hardware bench. One USB cable gives you a UART, or an MPSSE engine that clocks I2C and SPI and drives GPIO pins: an FT232H, FT2232H or FT232R on a desk is a bus master for every sensor, display and radio that speaks those protocols, with no Raspberry Pi in between. On Linux the kernel's `ftdi_sio` driver makes the UART side a `/dev/ttyUSB*` node, and that's where PHP's reach ends: a serial port it cannot configure, and no MPSSE at all, because MPSSE isn't a serial protocol. It's a vendor command set spoken over raw USB bulk transfers.

<b>libftdi1</b> is the C library that speaks it. It opens the chip through libusb, switches it into bit-bang or MPSSE mode, moves bytes synchronously or as asynchronous transfers that libusb completes in the background, and reads and writes the EEPROM that holds the chip's USB identity. Every FTDI tool on Linux and macOS that isn't FTDI's own proprietary driver is built on it, and its documentation and examples are the reference for how these chips are driven.

<b>The only problem?</b> PHP has no binding to it. The route until now was FFI: parse `ftdi.h`, declare the structs by hand, keep the enum values in step with the installed library, and run with `ffi.enable` on. This extension binds libftdi one to one under libftdi's own function names, in C against the Zend API, so the C documentation applies unchanged. It adds PHP objects that own the C pointers, so a PHP program cannot free a context twice or touch memory libusb has already released, and it carries every enum member and numeric define from `ftdi.h` with the values of the library it was built against. No event loop, no MPSSE helpers, no opinions: those live one layer up.

```
ext-ftdi                        libftdi1 calls, 1:1                    ← this package
  → microscrap/mpsse            MPSSE I2C, SPI and GPIO in PHP
    → microscrap/scrapyard-usb  the `usb` driver
      → scrapyard-io/framework  protocol managers, transports, circuits
```

### Basic usage

Most ways you will interface with ext-ftdi are in two parts -

Make a context with `ftdi_new()`, find the device you want with `ftdi_usb_find_all()`, and open it. Here an FT232H is opened by its USB IDs, reset, and switched into MPSSE mode; every call returns libftdi's own code, and `ftdi_get_error_string()` explains a negative one.

```php
use Ftdi\FtdiProductId;
use Ftdi\FtdiVendorId;

$ftdi = ftdi_new() ?? throw new RuntimeException('ftdi_new() failed');

// What is on the bus? Each device comes back as an FTDIDevice the context can open or describe.
$found = ftdi_usb_find_all($ftdi, FtdiVendorId::FTDI->value, FtdiProductId::FT232H->value);
foreach ($found['devices'] as $device) {
    $strings = ftdi_usb_get_strings($ftdi, $device);
    printf("%s, serial %s\n", $strings['description'], $strings['serial']);
}

// Open the first FT232H and put its engine into MPSSE mode.
if (ftdi_usb_open($ftdi, FtdiVendorId::FTDI->value, FtdiProductId::FT232H->value) < 0) {
    throw new RuntimeException(ftdi_get_error_string($ftdi));
}
ftdi_usb_reset($ftdi);
ftdi_set_bitmode($ftdi, 0x00, BITMODE_RESET);
ftdi_set_bitmode($ftdi, 0x00, BITMODE_MPSSE);
ftdi_tcio_flush($ftdi);
```

Talk to it: write MPSSE opcodes with `ftdi_write_data()` and read the answer with `ftdi_read_data()`, exactly as C would. Here the `GET_BITS_LOW` opcode reads the eight ADBUS pins. Close and free the context yourself when you're done.

```php
// SEND_IMMEDIATE makes the chip answer now instead of when its buffer fills.
ftdi_write_data($ftdi, chr(GET_BITS_LOW) . chr(SEND_IMMEDIATE), 2);

$reply = '';
while (strlen($reply) < 1) {
    $chunk = ftdi_read_data($ftdi, 1);      // "" until the answer arrives
    if ($chunk === false) {
        throw new RuntimeException(ftdi_get_error_string($ftdi));
    }
    $reply .= $chunk;
}
printf("ADBUS 0b%08b\n", ord($reply));

ftdi_usb_close($ftdi);
ftdi_free($ftdi);
```

#### Examples

##### Submit transfers and pump libusb

The submit functions return at once with an `FTDITransferControl`. libusb completes the transfer while its events are handled, either by calling `ftdi_handle_events_timeout()` as here, or by adding the descriptors from `ftdi_get_pollfds()` to your own event loop and calling `ftdi_handle_events_timeout($ftdi, 0)` when any of them fires:

```php
$tx = ftdi_write_data_submit($ftdi, chr(GET_BITS_LOW) . chr(SEND_IMMEDIATE), 2)
    ?? throw new RuntimeException(ftdi_get_error_string($ftdi));
$rx = ftdi_read_data_submit($ftdi, 1)
    ?? throw new RuntimeException(ftdi_get_error_string($ftdi));

while (! ftdi_transfer_completed($rx)) {
    ftdi_handle_events_timeout($ftdi, 10_000);      // microseconds
}

$written = ftdi_transfer_data_done($tx);            // 2
$pins = ftdi_transfer_read_done($rx);               // the byte read

ftdi_usb_close($ftdi);
ftdi_free($ftdi);
```

### Requirements

| | |
|---|---|
| OS | Linux or macOS. Windows is excluded in `composer.json`. |
| PHP | 8.4 or newer, NTS or ZTS. |
| Libraries | libftdi1 1.5 or newer and libusb-1.0 1.0.16 or newer, with their headers, found through `pkg-config`. 1.4 lacks functions and constants this extension binds; `configure` stops below 1.5. |
| Device access | Read-write access to the USB device. On Linux, run as root or add a udev rule such as `SUBSYSTEM=="usb", ATTR{idVendor}=="0403", MODE="0660", GROUP="plugdev"` and join that group. libftdi detaches the kernel's `ftdi_sio` serial driver from the interface it opens. |

To build it you need a C compiler, `pkg-config`, the two libraries' headers and the development files of the PHP you intend to load it into:

```bash
 # Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential pkg-config libftdi1-dev libusb-1.0-0-dev php8.4-dev

 # macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
brew install php@8.4 libftdi libusb pkgconf
```

`venusian build` reads the same packages from `extra.venusian.system` in `composer.json`.

### Installation

#### With PHP PIE (recommended)

[PIE](https://github.com/php/pie) is the PHP Foundation's installer for extensions. It downloads the tagged source from Packagist, builds it against the PHP on your `PATH`, installs the module and enables it. The libraries above must be installed first, since `configure` looks them up. `sudo` where your PHP's extension directory is root-owned, as on Debian; not on a Homebrew Mac:

```bash
pie install php-io-extensions/ftdi
```

#### Manually (install script)

The repository ships two installers, one per platform. Each one checks for libftdi1 and libusb, then for each PHP it targets builds in a temporary copy of the sources, installs `ftdi.so` into that PHP's `extension_dir`, writes `30-ftdi.ini` into its `conf.d` scan directory, checks the module loads, and leaves the checkout clean. The macOS one also ad-hoc signs the module so the system loads it on first use.

```bash
git clone https://github.com/php-io-extensions/ftdi.git
cd ftdi

./install-debian-trixie.sh             # Debian Trixie, Ubuntu 24.04+, Raspberry Pi OS: the php on PATH
./install-macos.sh                     # Homebrew php@8.4 and php@8.4-zts
./install-macos.sh /path/to/bin/php    # either script takes specific PHP binaries
```

#### Manually (phpize)

```bash
git clone https://github.com/php-io-extensions/ftdi.git
cd ftdi
phpize
./configure --enable-ftdi
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
```

Then enable it: add `extension=ftdi.so` to your `php.ini`, or drop that line into a file in the scan directory that `php --ini` reports.

#### Verify

```console
$ php --ri ftdi

ftdi

ftdi support => enabled
Version => 0.11.x
libftdi1 => 1.5
```

### API

The names are libftdi's. Four are spelt as `microscrap/ftdi` exported them: `ftdi_tci_flush`, `ftdi_tco_flush`, `ftdi_tcio_flush` and `ftdi_read_chip_id`. Every function is global; the objects and the two USB ID enums live in the `Ftdi` namespace. Return codes are libftdi's, never thrown; `ftdi_get_error_string()` explains a negative one.

#### Objects

| Class | Wraps | Lifetime |
|---|---|---|
| `Ftdi\FTDIContext` | `struct ftdi_context *` | Created by `ftdi_new()`; released by `ftdi_free()` or garbage collection. Its read-only properties read the struct live: `chipType`, `usbReadTimeout`, `usbWriteTimeout`, `interfaceIndex`, `baudrate`, `bitbangEnabled`, `bitbangMode`, `channel`, `inEndpoint`, `outEndpoint`, `readBufferChunkSize`, `writeBufferChunkSize`, `maxPacketSize`, `moduleDetachMode`, `errorStr`. `toArray()` returns them all. |
| `Ftdi\FTDIDevice` | `struct libusb_device *`, referenced | Listed by `ftdi_usb_find_all()`; usable with the context that found it until that context is deinitialised. |
| `Ftdi\FTDITransferControl` | `struct ftdi_transfer_control *` and its buffer | Returned by `ftdi_write_data_submit()` and `ftdi_read_data_submit()`; owns the buffer until the transfer is collected or cancelled. Live read-only `completed`, `size`, `offset`, and `toArray()`. |
| `Ftdi\FTDIVersionInfo` | `struct ftdi_version_info` | Readonly snapshot: `major`, `minor`, `micro`, `versionStr`, `snapshotStr`. |
| `Ftdi\FTDIEeprom` | the context's EEPROM image | Readonly snapshot from `ftdi_get_eeprom()`: every `enum ftdi_eeprom_value` as a camelCase int, `vendorId` through `userDataAddr`, 0 where the chip has no such value, plus `manufacturer`, `product` and `serial`. Meaningful after `ftdi_read_eeprom()` and `ftdi_eeprom_decode()`. |

None of them can be created with `new`, cloned or serialised.

A context keeps track of the transfers and devices made from it, so nothing ever reaches freed libusb memory:

- `ftdi_usb_close()`, `ftdi_deinit()`, `ftdi_free()`, `ftdi_init()` over an initialised context, and the context's release all cancel its pending transfers first.
- `ftdi_deinit()`, `ftdi_free()` and the context's release also drop its device references before libusb shuts down.
- A transfer object released while its transfer is pending cancels the transfer.

#### Functions

| Group | Functions |
|---|---|
| Context | `ftdi_new(): ?FTDIContext`, `ftdi_init`, `ftdi_deinit`, `ftdi_free`, `ftdi_set_interface`, `ftdi_get_library_version(): FTDIVersionInfo`, `ftdi_get_error_string` |
| Devices | `ftdi_usb_find_all(ctx, vendor, product): array{count, devices: list<FTDIDevice>}`, `ftdi_usb_get_strings` / `ftdi_usb_get_strings2(ctx, device): array{result, manufacturer, description, serial}`, `ftdi_usb_open_dev`, `ftdi_usb_open`, `ftdi_usb_open_desc`, `ftdi_usb_open_desc_index`, `ftdi_usb_open_bus_addr`, `ftdi_usb_open_string`, `ftdi_usb_close`, `ftdi_usb_reset` |
| Flushes | `ftdi_tci_flush`, `ftdi_tco_flush`, `ftdi_tcio_flush`, and the `ftdi_usb_purge_*` calls that ftdi.h deprecates |
| Line | `ftdi_convert_baudrate_ut_export(baud, ctx): array{result, value, index}`, `ftdi_set_baudrate`, `ftdi_set_line_property`, `ftdi_set_line_property2`, `ftdi_set_bitmode`, `ftdi_disable_bitbang`, `ftdi_read_pins`, `ftdi_set_latency_timer`, `ftdi_get_latency_timer`, `ftdi_set_timeouts`, `ftdi_poll_modem_status`, `ftdi_setflowctrl`, `ftdi_setflowctrl_xonxoff`, `ftdi_setdtr`, `ftdi_setrts`, `ftdi_setdtr_rts`, `ftdi_set_event_char`, `ftdi_set_error_char` |
| Synchronous data | `ftdi_write_data(ctx, data, size): int`, `ftdi_read_data(ctx, size): string\|false`, `ftdi_write_data_set_chunksize`, `ftdi_write_data_get_chunksize`, `ftdi_read_data_set_chunksize`, `ftdi_read_data_get_chunksize` |
| Asynchronous data | `ftdi_write_data_submit(ctx, data, size)` and `ftdi_read_data_submit(ctx, size): ?FTDITransferControl`, `ftdi_transfer_data_done(tc): int`, `ftdi_transfer_read_done(tc): string\|false`, `ftdi_transfer_data_cancel`, `ftdi_transfer_completed` |
| libusb event pump | `ftdi_get_pollfds(ctx): list<array{fd, events}>`, `ftdi_pollfds_handle_timeouts`, `ftdi_get_next_timeout(ctx): array{result, usec}`, `ftdi_handle_events_timeout(ctx, timeout_us)` |
| EEPROM | `ftdi_get_eeprom(ctx): FTDIEeprom`, `ftdi_eeprom_initdefaults`, `ftdi_eeprom_set_strings`, `ftdi_eeprom_get_strings`, `ftdi_eeprom_build`, `ftdi_eeprom_decode`, `ftdi_get_eeprom_value`, `ftdi_set_eeprom_value`, `ftdi_get_eeprom_buf(ctx, size): string\|false`, `ftdi_set_eeprom_buf`, `ftdi_set_eeprom_user_data`, `ftdi_set_ft232h_cbus(ctx): string`, `ftdi_read_eeprom_location`, `ftdi_read_eeprom`, `ftdi_read_chip_id(ctx, &chip_id)`, `ftdi_write_eeprom_location`, `ftdi_write_eeprom`, `ftdi_erase_eeprom` |

#### Behaviour

- **Return codes** are libftdi's. `ftdi_get_error_string()` explains a negative one.
- **Out parameters**: a call that reads one value through a C out parameter returns that value, or the negative code on failure. These are `ftdi_read_pins`, `ftdi_get_latency_timer`, `ftdi_poll_modem_status`, the chunk size getters, `ftdi_get_eeprom_value` and `ftdi_read_eeprom_location`.
- **Arguments** are checked against the C type: bytes 0–255, vendor and product IDs 0–0xFFFF, sizes within the data given, enum arguments within the enum. Anything outside throws `ValueError` instead of being truncated.
- **Failure without a value** is null where an object is returned (`ftdi_new()` and the two submit functions) and false where bytes are returned (`ftdi_read_data`, `ftdi_transfer_read_done`, `ftdi_get_eeprom_buf`).
- **Misuse** throws `Error`: calling into a context that `ftdi_free()` released (a second `ftdi_free()` does nothing), calling into a deinitialised context before `ftdi_init()`, or passing a device from another context or from before a deinit.
- **Transfers**:
  - With no device open, the submit functions return null and set the error string to "USB device unavailable", as libftdi's synchronous calls do. libftdi 1.5's submit functions return NULL there without setting any error string.
  - `ftdi_transfer_data_done()` and `ftdi_transfer_read_done()` wait for the transfer, free it, and return the bytes moved. Called again on a transfer that was already collected or cancelled, they return -1 and false.
  - Cancelling a transfer that was already collected or cancelled does nothing.
- **Re-initialising**: `ftdi_init()` over an initialised context deinitialises it first. Plain libftdi would leak the old libusb context.
- **EEPROM strings**: libftdi 1.5's `ftdi_eeprom_get_strings()` copies each string without a NULL check, and a fresh context, `ftdi_eeprom_initdefaults()` or `ftdi_eeprom_decode()` can leave any of the three NULL. The context records which strings libftdi holds and asks only for those; the others come back as "".
- **Not bound**: `ftdi_list_free` and `ftdi_list_free2`, because `ftdi_usb_find_all()` frees the list itself and each `FTDIDevice` holds its own libusb reference; and `ftdi_set_usbdev`, because PHP has no way to obtain a libusb device handle.

#### Constants

Every member of every enum in `ftdi.h`, under libftdi's own unprefixed names:

| Enum | Constants |
|---|---|
| chip and line | `TYPE_*`, `NONE`, `ODD`, `EVEN`, `MARK`, `SPACE`, `STOP_BIT_*`, `BITS_*`, `BREAK_*` |
| modes | `BITMODE_*`, `INTERFACE_*`, `AUTO_DETACH_SIO_MODULE`, `DONT_DETACH_SIO_MODULE`, `AUTO_DETACH_REATACH_SIO_MODULE` |
| EEPROM | the `enum ftdi_eeprom_value` names (`VENDOR_ID` … `USER_DATA_ADDR`), `CBUS_*`, `CBUSH_*`, `CBUSX_*` |

And every numeric `#define` in `ftdi.h`:

| Group | Constants |
|---|---|
| MPSSE opcodes and flags | `MPSSE_*`, `SET_BITS_LOW`, `SET_BITS_HIGH`, `GET_BITS_LOW`, `GET_BITS_HIGH`, `TCK_DIVISOR`, `SEND_IMMEDIATE`, `WAIT_ON_HIGH`, `WAIT_ON_LOW`, … |
| control requests and flags | `SIO_*`, `FTDI_DEVICE_OUT_REQTYPE`, `FTDI_DEVICE_IN_REQTYPE` |
| EEPROM bits | `INVERT_*`, `CHANNEL_IS_*`, `DRIVE_*`, … |

Every value comes from `ftdi.h` at build time. `SIO_RESET_PURGE_RX` and `SIO_RESET_PURGE_TX` are left out: ftdi.h deprecates them with a compile warning in favour of `SIO_TCIFLUSH` and `SIO_TCOFLUSH`.

Enums: `Ftdi\FtdiVendorId::FTDI` (0x0403) and `Ftdi\FtdiProductId::{FT232R, FT2232H, FT4232H, FT232H, FT230X, FT4232HP, FT4232HA}`.

### Extensions you might use with this one

* [ext-epoll](https://github.com/php-io-extensions/epoll): Linux. The descriptors `ftdi_get_pollfds()` returns register with `epoll_ctl()`, so libusb's transfers complete inside your own loop: when one fires, call `ftdi_handle_events_timeout($ftdi, 0)`. When `ftdi_pollfds_handle_timeouts()` returns `0`, libusb's own descriptors don't cover its timeouts, and `ftdi_get_next_timeout()` is the `epoll_wait()` timeout to honour.
* [ext-kqueue](https://github.com/php-io-extensions/kqueue): macOS. The same with `EV_SET()` and `kevent()`.
* [ext-posi](https://github.com/php-io-extensions/posi): the serial side. When a chip stays on the kernel's `ftdi_sio` driver as `/dev/ttyUSB0`, posi's `posix_open()` and termios calls drive it as a plain UART, with no libftdi and no detach.

### AI-assisted development

This codebase was built with LLM assistance under human direction. Prompts, reviews, and architectural decisions were owned by a professional software engineer — the model accelerates drafting and exploration; it does not replace judgment on APIs, dependency direction, or what ships.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/ftdi/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records what the README doesn't: how the module is laid out and linked, every place libftdi 1.5 would crash, leak or mislead from PHP and the guard that prevents it, how the objects own their pointers and tear down in order, the async pump, the EEPROM image, how the constant list is kept in step with `ftdi.h`, the 0.9 to 0.10 call map, and a log of every change that altered behaviour.

Start at [`.okf/index.md`](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/overview). [`AGENTS.md`](https://github.com/php-io-extensions/ftdi/blob/HEAD/AGENTS.md) is the short rule sheet an agent reads before touching the C, the stub, or packaging; each rule points into the bundle for the reason behind it.

Point your agent at the repo and it has the same context the maintainer has. Point yourself at it when the README's answer is "it does X" and you want "because".

### Resources

* [libftdi1](https://www.intra2net.com/en/developer/libftdi/) and its [API reference](https://www.intra2net.com/en/developer/libftdi/documentation/): the library this extension binds. Its documentation is the manual; this README only adds what PHP changes.
* [ftdi.h](https://github.com/lipro/libftdi/blob/master/src/ftdi.h): the header every constant here comes from, and where each MPSSE opcode and EEPROM bit is defined.
* [Upgrading from 0.9](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/reference/upgrade-from-09): the Zephir `Ftdi\FTDI::ftdi*` statics and `microscrap/ftdi` helpers mapped call by call onto 0.10.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`ftdi.stub.php`](https://github.com/php-io-extensions/ftdi/blob/HEAD/ftdi.stub.php) is the API declaration; `ftdi_arginfo.h` is generated from it.
* [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): the spec the [`.okf/`](https://github.com/php-io-extensions/ftdi/tree/HEAD/.okf) bundle follows.

### Running the test suite

The suite is Pest v4 and needs no device: constants, enums, the version snapshot, construction refusals, live properties, the codes a missing device produces, `ValueError` ranges, the EEPROM snapshot shape, released and deinitialised contexts, and an idle libusb pump. It runs on Linux and macOS. Build the module in a copy of the four sources, then point `php` at it:

```bash
git clone https://github.com/php-io-extensions/ftdi.git
cd ftdi
mkdir ../ftdi-build && cp config.m4 ftdi.c php_ftdi.h ftdi_arginfo.h ../ftdi-build/
(cd ../ftdi-build && phpize && ./configure --enable-ftdi && make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)")
composer install
php -n -d extension="$PWD/../ftdi-build/modules/ftdi.so" vendor/bin/pest
```

```console
Tests:    12 passed (85 assertions)
Duration: 0.08s
```

`-n` skips your `php.ini`, so the suite tests the build and not an installed `ftdi.so`; without it, a PHP that already loads ftdi (the 0.9 Zephir extension carried the same module name) warns `Module "ftdi" is already loaded` and keeps the installed one. A module only loads in the PHP whose `phpize` built it: for Homebrew's ZTS build, run `phpize` and pass `--with-php-config` from `/opt/homebrew/opt/php@8.4-zts/bin`. Checks against a real FT232H are scratch scripts run by hand and never part of the suite; the suite never writes EEPROM.

### Contributing

Open an issue first for anything beyond a typo. Pull requests change `ftdi.stub.php` and `ftdi.c` together, regenerate `ftdi_arginfo.h` with gen_stub, and add a Pest test for the behaviour. A constant new in a later libftdi raises the `config.m4` floor and both installers' check with it. CI must be green on every cell of the matrix. Read [`AGENTS.md`](https://github.com/php-io-extensions/ftdi/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

ext-ftdi gives PHP code raw access to USB devices it can open, including writing their EEPROM. See [SECURITY.md](https://github.com/php-io-extensions/ftdi/blob/HEAD/SECURITY.md) for what that means and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/ftdi/tree/HEAD/LICENSE).
