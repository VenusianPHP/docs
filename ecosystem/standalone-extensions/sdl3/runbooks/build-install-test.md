# Build, install, test

How ext-sdl3 is built into Homebrew PHP on the Mac and the distro SDL on the Pi.

## Overview

SDL_GPU needs `SDL_Init(SDL_INIT_VIDEO)` first. The extension builds against SDL 3.2 or newer and binds only the 3.2 API.[^measured]

| Machine | SDL that loads | Video | SDL_GPU driver | Depth-stencil format | RGBA8 4× | Shader formats |
|---|---|---|---|---|---|---|
| Pi 5, distro 3.2.10 | 3.2.10 | wayland | vulkan | `D24_UNORM_S8_UINT` only | yes | SPIR-V |
| Pi 5, `/usr/local/lib` 3.4.9 | 3.4.9 | none | — | — | — | — |
| Mac, Homebrew 3.4.4 | 3.4.4 | cocoa | metal | `D32_FLOAT_S8_UINT` only | yes | MSL, METALLIB |

## Mac

`./install-macos.sh` builds a disposable copy for `/opt/homebrew/opt/php@8.4/bin/php` and `php@8.4-zts`, installs `sdl3.so`, ad-hoc signs it, and writes `30-sdl3.ini`. It refuses to start unless `pkg-config --exists sdl3` (`brew install sdl3`).

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest
zhp -d memory_limit=128M vendor/bin/pest
```

## Pi

Copy the tree with `fnk`. `./install-debian-trixie.sh` checks `pkg-config` for `sdl3 >= 3.2` (`apt install libsdl3-dev`), then sets `PKG_CONFIG_PATH` to `/usr/lib/$(gcc -dumpmachine)/pkgconfig`, adds `-I/usr/include` so those headers win over `/usr/local/include`, and links `-L` the distro libdir. The loaded library reports 3.2.10.

```bash
WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/$(id -u) php -d memory_limit=128M vendor/bin/pest
```

A swapchain test shows a window. Say so before that run.

`vendor/`, `composer.lock`, and the phpize tree are not part of the commit. The installer deletes its build products.

[^measured]: Measured before the slice 2 plan, 2026-10-04
