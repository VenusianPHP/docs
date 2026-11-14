# Build, install, test

Build ext-sokol-audio into Homebrew PHP 8.4 NTS/ZTS and on Linux, the CI audio stack, test a build without installing it, run the suite without audible sound.

## macOS

`./install-macos.sh`: disposable copy per PHP (default Homebrew php@8.4 + php@8.4-zts), install `sokol_audio.so`, ad-hoc sign, `30-sokol_audio.ini` unless already loaded.[^mac] Links `-framework AudioToolbox` into the `.so` (shared) or PHP's link line (static); `PHP_ADD_FRAMEWORK` alone does not reach a shared module.

Test a build without installing: build in scratch (`phpize`, `./configure --enable-sokol-audio --with-php-config=…`, `make`), write `extension=<build>/modules/sokol_audio.so` into a scratch ini dir, run `PHP_INI_SCAN_DIR=":<dir>" XDEBUG_MODE=off <php> -d memory_limit=128M vendor/bin/pest` (an ini, not `-d`, so `LifecycleTest`'s subprocesses load it). `composer install` with Herd's composer.

The suite writes silence only. Never run code that plays real sound on the maintainer's Mac without asking.

## Linux / Pi (Debian trixie)

Needs `build-essential`, `php8.4-dev`, `libpulse-dev` (the installer installs it).[^debian] Copy to the Pi with `COPYFILE_DISABLE=1 tar --no-xattrs … | fnk …`, then `./install-debian-trixie.sh`. Verified on the fnk Pi 5 (PHP 8.4 ZTS under /usr/local/php84-zts, PipeWire pulse server, HDMI speaker; `composer` in /usr/local/bin): `cd ~/sokol-audio && php -d memory_limit=128M vendor/bin/pest`. Sound may be played there; there is a speaker. Device tests need a pulse server for the user (PipeWire's works); headless, `pulseaudio --start --exit-idle-time=-1` and `pactl load-module module-null-sink` under PipeWire, not PulseAudio (2 s blocks, see CI).

## CI

Ubuntu cells start PipeWire + WirePlumber + pipewire-pulse by hand (session dbus, `XDG_RUNTIME_DIR`, both exported through `GITHUB_ENV`) with a null sink, so the device tests run; a last step runs the audio-thread log test alone with `SAUDIO_TEST_KILL_PULSE=1` (it kills `pipewire-pulse`). Not PulseAudio's `module-null-sink`: sokol's `pa_simple_new` asks for no latency, so that sink stays at its 2 s maximum and each `pa_simple_write` blocks ~2 s (one stream callback per 2 s; 0.11.0's CI failed `StreamTest` on Ubuntu). Reproduce a Linux cell locally in `docker run ubuntu:24.04` with ondrej's php8.4 and the same bootstrap. macOS cells skip device tests if the runner has no output.[^ci]

[^mac]: macOS installer
[^debian]: Debian trixie installer
[^ci]: CI with a PulseAudio null sink
