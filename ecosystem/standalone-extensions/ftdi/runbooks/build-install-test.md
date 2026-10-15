# Build, install, test

libftdi1/libusb prerequisites, gen_stub after a stub edit, scratch builds, the two installers, Pest, FT232H smoke, PIE.

## Needs

php-dev per target PHP, C compiler, pkg-config, libftdi1 ≥ 1.5 and libusb-1.0 ≥ 1.0.16 with headers. macOS `brew install libftdi pkg-config`; Debian/Pi `apt install pkg-config libftdi1-dev`.[^config]

## Stub → arginfo

Edit `ftdi.stub.php`, never `ftdi_arginfo.h`:

```bash
php "$(php-config --prefix)/lib/php/build/gen_stub.php" ftdi.stub.php
```

Stub rules: no `use` statements, so class names are fully qualified (`\Ftdi\FTDIContext`); classes and enums inside `namespace Ftdi { }`, functions and constants in the global block; `@generate-class-entries`. Commit stub and arginfo together.

## Scratch build

```bash
mkdir -p "$TMP/ftdi" && cp config.m4 ftdi.c php_ftdi.h ftdi_arginfo.h "$TMP/ftdi/"
cd "$TMP/ftdi" && phpize && ./configure --enable-ftdi && make -j
```

Pest from the repo: `php -n -d extension=$TMP/ftdi/modules/ftdi.so vendor/bin/pest`. `-n` because a PHP may already load the 0.9 Zephir ext, also named `ftdi` (`Module "ftdi" is already loaded`, old one wins). A module built for NTS fails to load in ZTS (`_executor_globals` not found) and the reverse: build once per PHP.

## Installers

Both check `pkg-config --exists 'libftdi1 >= 1.5' 'libusb-1.0 >= 1.0.16'`, then per PHP binary: build in `mktemp -d` copy, install `ftdi.so` into `extension_dir`, write `30-ftdi.ini`, verify `extension_loaded('ftdi')`, delete the copy.[^mac][^debian]

- `install-macos.sh [php …]`: default Homebrew `php@8.4` + `php@8.4-zts`; ad-hoc `codesign`.
- `install-debian-trixie.sh [php …]`: default `php` on PATH; versioned `phpize8.4`/`php-config8.4` fallback; `sudo` when not root; writes through a Debian `mods-available` symlink when present.

## Tests

`tests/SurfaceTest.php`, Pest v4, no device: constants, enums, version snapshot, construction refusals, live properties, missing-device codes, `ValueError` ranges, EEPROM snapshot shape, released/deinitialised contexts, idle pump. Runs NTS + ZTS on the Mac and on the Pi (same `tar | fnk` loop as ext-posi, sources `config.m4 ftdi.c php_ftdi.h ftdi_arginfo.h`).

Hardware proof stays out of the suite: scratch scripts against the Mac's FT232H (0403:6014), never committed. README examples (device list, MPSSE `GET_BITS_LOW`, async submit + pump) were run that way on libftdi 1.5.

## PIE

`composer.json` `type: php-ext`, `extension-name: ftdi`, priority 30, NTS + ZTS, Windows excluded, `--enable-ftdi`. PIE runs `config.m4`, so the build host needs libftdi1-dev and pkg-config first. `.gitattributes` export-ignores tests, `phpunit.xml`, `.okf`, `AGENTS.md`, `CLAUDE.md`. Version in `composer.json` `version` and `PHP_FTDI_VERSION` (`php_ftdi.h`); bump both, only past a published tag.

[^mac]: install-macos.sh
[^debian]: install-debian-trixie.sh
[^config]: config.m4
