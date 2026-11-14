# Build, install, test

Build ext-vlc into Homebrew PHP 8.4 NTS/ZTS and on the Pi, regenerate the binding, build for probes, run the suite.

## macOS

Install VLC.app 3.0 (`brew install --cask vlc`): it ships the headers in `Contents/MacOS/include` and universal `libvlc.dylib` / `libvlccore.dylib` in `Contents/MacOS/lib`, with no pkg-config file. `./install-macos.sh`: a fresh disposable copy per PHP (default Homebrew php@8.4 + php@8.4-zts), `vlc.so` linked with an rpath to VLC.app's `lib`, ad-hoc signed, `30-vlc.ini` unless an ini already loads it. Every process needs `VLC_PLUGIN_PATH=/Applications/VLC.app/Contents/MacOS/plugins`; `tests/Pest.php` sets it when unset.

## Regenerate

After changing `tools/generate.php`: `php84 tools/generate.php <group>` for each of `player`, `lists`, `discovery`, `vlm`, `dialog` (writes `stubs/gen_<group>.stub.php` and `src/gen_<group>.c`; never edit them), then `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php -f stubs`, then `php84 scripts/support.php`. Constants: `php84 tools/constants.php`.

## Probe build

`VLC_CONFIGURE="--enable-vlc-probes" ./install-macos.sh`. In that build, env `VLC_PROBE_OFF=<site>` switches one refusal off; the probe tests run it in a child process and expect the crash. Reinstall the release build afterwards; never ship a probe build.

## Pi (Debian trixie)

`sudo apt install libvlc-dev vlc-plugin-base build-essential php8.4-dev`. Copy the tree with `COPYFILE_DISABLE=1 tar` (else `._*` files break gen_stub), then `./install-debian-trixie.sh`. Pi OS's libvlc 3.0.24 knows its plugin directory.

## Suite

`php -d memory_limit=128M vendor/bin/pest`. Instances use `--aout=dummy --vout=dummy`: nothing plays or opens a window. Probe halves skip on a release build; the video test skips without ext-ffi.
