# Build, install, test

gen_stub after a stub edit, builds per PHP, the installers, Pest on NTS and ZTS, CI, and PIE.

## Needs

A C compiler, `pkg-config`, the libcurl headers (7.69.0 or newer) and php-dev (phpize, php-config) for the target PHP, with ext-curl loaded in it. Debian family: `build-essential pkg-config libcurl4-openssl-dev php8.4-dev`. macOS: Xcode Command Line Tools and Homebrew `php@8.4`, `php@8.4-zts`, `curl`, `pkgconf`; Homebrew's curl is keg-only, so `PKG_CONFIG_PATH="$(brew --prefix curl)/lib/pkgconfig"`. PHP 8.4 or newer: the generated class registration uses `zend_register_internal_class_with_flags`.

## Stub → arginfo

Edit `multicurl.stub.php`, never `multicurl_arginfo.h`. Regenerate with the target PHP's gen_stub and commit both:

```bash
php "$(php-config --prefix)/lib/php/build/gen_stub.php" multicurl.stub.php
```

`$multi` is `mixed` on purpose: the method checks for exactly `CurlMultiHandle` itself and throws `Exception("expected a CurlMultiHandle")`, which the suite pins.

## Build

phpize builds in the repo root; `.gitignore` covers every artifact. A module only loads in the PHP whose `phpize` built it, so build once per target:

```bash
phpize && ./configure --enable-multicurl && make -j"$(sysctl -n hw.ncpu)"
Z=/opt/homebrew/opt/php@8.4-zts/bin; $Z/phpize && ./configure --enable-multicurl --with-php-config=$Z/php-config && make -j"$(sysctl -n hw.ncpu)"
```

To clean an in-place build, use `make distclean` and `git clean -fdX -e '!vendor' -e '!composer.lock'`. `phpize --clean` also deletes `tests/*.php`, the Pest suite.

## Test

Pest v4, no network: `tests/Pest.php` starts PHP's built-in server on `tests/fixtures` at a free port and drives transfers through the socket API, `curlSocketStream()` and `stream_select()`.

```bash
composer install
php -n -d extension="$PWD/modules/multicurl.so" vendor/bin/pest
```

`-n` keeps an installed `multicurl.so` from loading first. Where ext-curl is shared, add `-d extension=curl` before it. One test skips below libcurl 8.16.0, and the `CURLM_ABORTED_BY_CALLBACK` assertions skip below 7.81.0.

Results for the C port (0.11.1):[^c-port-run]

| PHP | OS | libcurl | Result |
|---|---|---|---|
| 8.4.27 NTS and ZTS (Homebrew) | macOS arm64 | 8.23.0 | 73 passed, 383 assertions |
| 8.4.27 NTS, 8.4.28 ZTS | Debian aarch64 | 8.14.1 | 72 passed, 1 skipped, 368 assertions |

All four builds compile with no warnings and link no libcurl.

## CI

`ubuntu-24.04` and `macos-15` × PHP `8.4`, `8.5` × `nts`, `zts`. Steps: libcurl headers, phpize/configure/make in the root, load check with `php -n -d extension=…` (adding `-d extension=curl` where curl is shared), `--ri multicurl`, then `composer install` and Pest.[^ci]

## Installers

`install-macos.sh [php …]`: default targets Homebrew `php@8.4` and `php@8.4-zts`. Per PHP: require ext-curl loaded, point `pkg-config` at the libcurl the PHP binary links (`otool -L`, Homebrew `curl` as fallback), build in a temp copy with that PHP's `phpize`/`php-config`, copy `multicurl.so` into `extension_dir`, `codesign --force --sign -`, write `40-multicurl.ini`, verify `Multicurl\Multi` exists. Refuses to run on anything but Darwin.[^mac]

`install-debian-trixie.sh [php …]`: default targets the `php` on `PATH`. Per PHP: find `phpize`/`php-config` next to it, require `cc`, `pkg-config`, libcurl 7.69.0+ headers and ext-curl loaded, build in a temp copy, install `multicurl.so` and `40-multicurl.ini` (with `sudo` when not root; `40-` sorts after Debian's `20-curl.ini`), verify `Multicurl\Multi` exists.

## PIE

`composer.json` `type: php-ext`, `extension-name: multicurl`, priority 40, NTS + ZTS, Windows excluded, configure option `--enable-multicurl`, built from the repo root. `.gitattributes` export-ignores tests, `phpunit.xml`, `.okf`, `AGENTS.md`, `CLAUDE.md`.[^composer]

## Version

`PHP_MULTICURL_VERSION` in `php_multicurl.h` and `version` in `composer.json` move together.

[^mac]: [install-macos.sh](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/install-macos.sh)
[^ci]: [ci.yml](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/.github/workflows/ci.yml)
[^composer]: [composer.json](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/composer.json)
[^c-port-run]: Builds and Pest runs of the C port, 2026-11-23
