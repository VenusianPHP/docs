# Build, install, test

Debian installer on the Pi, Homebrew installer on the Mac, Pest, smoke, clean tree.

## Overview

Linux (`install-debian-trixie.sh`): needs `libgtk-4-dev`, `pkg-config`, php-dev. Builds in place with phpize, installs `gtk.so`, writes `30-gtk.ini` to the CLI (and FPM/Apache) conf.d, removes build artifacts (incl. `src/.libs`, `src/*.lo`). ≈ 6 s on a Pi 5.[^debian]

macOS (`install-macos.sh`): needs `brew install gtk4`. Builds in a temp copy for php@8.4 (`php84`) and php@8.4-zts (`zhp`), ad-hoc signs, writes `30-gtk.ini`.[^mac]

Pi loop from the Mac: the Mac tree is authoritative; the Pi copy at `~/gtk` is disposable.

```bash
fnk 'rm -rf ~/gtk'
rsync -az --delete --exclude .git --exclude vendor --exclude composer.lock ./ angel@<pi>:/home/angel/gtk/
fnk 'cd ~/gtk && bash install-debian-trixie.sh'
```

Verify (Linux over SSH: export `WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`):

```bash
php --ri gtk
composer install && php vendor/bin/pest
php examples/smoke.php     # SMOKE_OK
rm -rf vendor composer.lock build.log
```

Smoke steps: register (startup initialises GTK) + hold + activate; Dock icon (macOS, `lsappinfo`) or app id owned on the session bus (Linux); pump; 50 ms budget; `wakeup()`; idle; pipe-fd wake; kqueue (macOS) / epoll (Linux) fd nested in GLib's poll; `run()` ended by `quit()`; release.[^smoke]

Probe build (shows each kept refusal's crash; never installed for use). In a scratch copy, not the tree:

```bash
phpize && ./configure --enable-gtk --enable-gtk-probes && make
PHPGTK_PROBE_EXT=$PWD/modules/gtk.so php -d extension=$PWD/modules/gtk.so vendor/bin/pest tests/Probes
```

The parent PHP must load the probe build itself (`PHPGTK_PROBES` defined), so its conf.d must not also load the installed `gtk.so`: point `PHP_INI_SCAN_DIR` at a copy of conf.d without `30-gtk.ini`. Each probe runs a child process twice, the site kept and `PHPGTK_PROBE_OFF=<id>`, and asserts the refusal, then the signal. libgmalloc probes (stale iters, regions, GBytes) run on macOS only. `VersionGateTest` needs `PHPGTK_OLD_GTK_HOST` / `PHPGTK_OLD_GTK_EXT` (a host with an older GTK runtime). On a release build every probe test skips.

[^debian]: install-debian-trixie.sh
[^mac]: install-macos.sh
[^smoke]: examples/smoke.php
