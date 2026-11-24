# Build, install, test

Build ext-raven into Homebrew PHP 8.4 NTS/ZTS or on Debian, run the suite, run the crash sweep.

## macOS

`./install-macos.sh` builds in a temporary copy for `php@8.4` and `php@8.4-zts`, installs `raven.so`, ad-hoc signs it, and writes `30-raven.ini` unless an ini in that scan directory already loads raven.[^mac] A full build compiles Raven's sources: about a minute per PHP. Showing windows needs a Vulkan loader at run time (`brew install molten-vk vulkan-loader`); the null backend always works.

## Debian

`./install-debian-trixie.sh` on Debian Trixie, Ubuntu 24.04+ or Raspberry Pi OS: needs `libx11-dev` and `pkg-config`. It builds in the checkout, writes `30-raven.ini` into each conf.d of that PHP, and cleans the build products afterwards.[^debian] Wayland, D-Bus and the Vulkan loader are opened at run time. Not yet run on the Pi.

## Suite

`XDEBUG_MODE=off php84 -d memory_limit=128M vendor/bin/pest`, then the same with `zhp`. Headless on `R_BACKEND_NULL`; gate a commit on the exit code. At v0.11.0: 75 passed (703 assertions). CI (`PHP 8.4` and `8.5`, NTS and ZTS, `ubuntu-24.04` and `macos-15`) enables the just-built module through an extra ini scan directory so the lifecycle tests' child processes load it too.

## Crash sweep

`php84 tools/sweep.php` calls every bound function with zero/null arguments, one child process each (about 10 minutes).[^sweep] At v0.11.0 (1,618 functions): no crash; `Rfile_dialog_open`, `Rfile_dialog_save` and `Rfile_dialog_select_folder` time out, because headless Raven runs its own modal file browser and waits for input; four device pickers (`Rfile_open_async`, `Rfile_save_async`, `Rfile_select_folder_async`, `Rphoto_pick`) time out waiting for a host result; ten `RActionContext` getters fail the sweep's `new` (private constructor).

[^mac]: macOS installer
[^debian]: Debian installer
[^sweep]: crash sweep
