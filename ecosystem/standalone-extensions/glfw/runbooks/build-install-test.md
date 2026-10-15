# Build, install, test

Build ext-glfw into Homebrew PHP 8.4 NTS/ZTS and on the Pi, and run the Pest suite on each.

## macOS

`./install-macos.sh` builds a disposable copy per PHP (default: Homebrew php@8.4 and php@8.4-zts), installs `glfw.so` into its extension_dir, ad-hoc signs it, writes `30-glfw.ini` unless an ini there already loads glfw.[^mac] Needs `brew install glfw` (pkg-config `glfw3 >= 3.4`).

Tests: `composer install`, then `php84 -d memory_limit=128M vendor/bin/pest` (and `zhp`). The suite opens windows, goes full screen, minimizes and sets gamma (restored after).

To test a build without installing it: copy the PHP's conf.d to a scratch dir, drop any glfw ini, add `extension=<build>/modules/glfw.so`, run with `PHP_INI_SCAN_DIR=<scratch>`.

## Pi (Debian trixie, Wayland)

Copy: `tar --no-xattrs -czf - --exclude=.git --exclude=vendor . | fnk "mkdir -p ~/glfw && tar -xzf - -C ~/glfw"`. Install: `fnk 'cd ~/glfw && ./install-debian-trixie.sh'` (distro `libglfw3-dev` 3.4).[^debian]

Run with `WAYLAND_DISPLAY=wayland-0 DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000`, and without ext-gtk loaded (see [platform facts](/docs/{{version}}/ecosystem/standalone-extensions/glfw/architecture/platform-facts)).

[^mac]: macOS installer
[^debian]: Debian trixie installer
