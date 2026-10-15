# Build, install, test

Build ext-box2d into Homebrew PHP 8.4 NTS/ZTS and on the Pi, test a build without installing it, run the suite.

## macOS

`./install-macos.sh`: disposable copy per PHP (default Homebrew php@8.4 + php@8.4-zts), install `box2d.so`, ad-hoc sign, `30-box2d.ini` unless already loaded.[^mac] No system packages.

Test a build without installing: copy the PHP's conf.d to scratch, replace its `30-box2d.ini` with `extension=<build>/modules/box2d.so` (an ini, not `-d`, so the suite's subprocesses and built-in server load it too), run with `PHP_INI_SCAN_DIR=<scratch> XDEBUG_MODE=off`.

Suite: `composer install`, `php84 -d memory_limit=128M vendor/bin/pest` and `zhp`. Race check: loop `tests/WorkersTest.php tests/CallbackErrorsTest.php` 100× (Mac has no `timeout`; `perl -e 'alarm 60; exec @ARGV'`).

## Pi (Debian trixie)

`COPYFILE_DISABLE=1 tar --no-xattrs -czf - <files> | fnk "… tar -xzf - -C ~/box2d"` (else `._*` stubs break gen_stub), then `fnk 'cd ~/box2d && ./install-debian-trixie.sh'` (~25 s on a Pi 5; needs build-essential, php8.4-dev).[^debian]

[^mac]: macOS installer
[^debian]: Debian trixie installer
