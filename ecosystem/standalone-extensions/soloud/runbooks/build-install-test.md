# Build, install, test

Build ext-soloud into Homebrew PHP 8.4 NTS/ZTS and on the Pi, regenerate the binding, build for probes, run the suite.

## macOS

`./install-macos.sh`: a fresh disposable copy per PHP (default Homebrew php@8.4 + php@8.4-zts), install `soloud.so`, ad-hoc sign, `30-soloud.ini` unless an ini already loads it. No system packages; Core Audio frameworks are linked.

## Regenerate

After changing `tools/bindings.php` or `tools/generate.php`: `php84 tools/generate.php`, then `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php -f stubs`, then `php84 scripts/support.php`. After a new upstream commit: replace `lib/soloud/`, rerun `tools/extract.php` (clang's AST into `tools/api.json`) first.

## Probe build

`SOLOUD_CONFIGURE="--enable-soloud-probes" ./install-macos.sh`. In that build, env `SOLOUD_PROBE_OFF=<site>` switches one refusal off; the probe tests run it under libgmalloc and expect the crash. Reinstall the release build afterwards; never ship a probe build.

## Pi (Debian trixie)

Copy the tree with `COPYFILE_DISABLE=1 tar --no-xattrs` (else `._*` stubs break gen_stub), then `./install-debian-trixie.sh` (needs build-essential and php8.4-dev; ALSA / PulseAudio / JACK are loaded at runtime).

## Suite

`XDEBUG_MODE=off php -d memory_limit=128M vendor/bin/pest`. Engines use the null backend; the real-mixer test plays zeros at volume 0 and skips without a device. Probe halves skip on a release build.
