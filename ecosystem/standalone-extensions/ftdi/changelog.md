# Changelog

What changed in this package, newest first.

### 2026-10-28

* **Version**: 0.11.0 in `composer.json` and `PHP_FTDI_VERSION` (`php_ftdi.h`); `branch-alias` `dev-main` is `0.11.x-dev`. Promoted with the Venusian 0.11 ecosystem. No API or behaviour change. 12 passed on Homebrew PHP 8.4 NTS and ZTS and the Pi on 8.4 ZTS.
* **Open — x86_64 box**: not built on the x86_64 Ubuntu-family 8.4 NTS box; it lacks `pkg-config libftdi1-dev`.

### 2026-10-12

* **Version**: 0.10.5 in `composer.json` and `PHP_FTDI_VERSION`. No API change. Steps past 0.10.1 through 0.10.4 to line up with the sibling extensions.
* **README**: rewritten on the php-io-extensions template (header badges, two-part basic usage, requirements table, PIE / install script / phpize install paths, API, OKF section, suite run). Suite count (12 passed, 85 assertions) run against a scratch build on Homebrew PHP 8.4 NTS, libftdi1 1.5.

### 2026-10-09

* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.

### 2026-10-04

* **Creation**: Bundle created for ext-ftdi 0.10.0, the plain-C rewrite: [module](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/guide/module), [libftdi 1.5 guards](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/guide/libftdi-15-guards), [objects](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/objects), [functions](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/functions), [async](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/async-transfers-and-the-libusb-pump), [EEPROM](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/eeprom), [constants](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/api/constants), [build](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/runbooks/build-install-test), [upgrade from 0.9](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/reference/upgrade-from-09).
* **Update**: libftdi1 floor raised to 1.5 in `config.m4` and both installers; 1.4 lacks bound functions and constants. [module](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/guide/module)
