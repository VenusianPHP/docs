# Build, install, test

Build ext-miniaudio into Homebrew PHP 8.4 NTS/ZTS and on the Pi, regenerate the binding, test a build without installing it, run the suite.

## macOS

`./install-macos.sh`: disposable copy per PHP (default Homebrew php@8.4 + php@8.4-zts), install `miniaudio.so`, ad-hoc sign, `30-miniaudio.ini` unless already loaded.[^mac] No system packages.

Test a build without installing: rsync `config.m4 php_miniaudio.h src stubs lib` to a scratch dir, `phpize && ./configure --enable-miniaudio --with-php-config=… && make`, then run Pest with `-d extension=<build>/modules/miniaudio.so` and `MINIAUDIO_SO=<same path>` (the lifecycle tests pass it to their child processes), or an ini scan directory. Suite at `-d memory_limit=128M`, `XDEBUG_MODE=off`; ~6 s; null backend only.

## Regenerate

After changing `tools/`: `php84 tools/generate.php` (must print `pending 0`), `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs`. After a new upstream tag: re-run the clang extraction first (see AGENTS.md).

## Pi (Debian trixie)

`COPYFILE_DISABLE=1 tar --no-xattrs -czf - <files> | fnk "… tar -xzf - -C ~/miniaudio"` (else `._*` stubs break gen_stub), then `fnk 'cd ~/miniaudio && ./install-debian-trixie.sh'` (needs build-essential, php8.4-dev; ALSA/PulseAudio are loaded at runtime).[^debian]

[^mac]: macOS installer
[^debian]: Debian trixie installer
