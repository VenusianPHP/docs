# Build, install, test

Debian installer on the Pi, Homebrew installer on the Mac, Pest, smoke, clean tree.

## Overview

`config.m4`: `PHP_REQUIRE_CXX`, `PKG_CHECK_MODULES(Qt6Widgets Qt6Gui Qt6Core Qt6Multimedia Qt6MultimediaWidgets Qt6OpenGL Qt6OpenGLWidgets Qt6WebEngineCore Qt6WebEngineWidgets >= 6.4)`. `PHP_EVAL_INCLINE/LIBLINE` keep only `-I/-l/-L`, so Qt's full `QT_CFLAGS` (with `-D`, `-F`) go in as extension cflags and, built shared, `QT_LIBS` (with `-framework`) as `QT_SHARED_LIBADD`; compiled into PHP (`venusian build`), `-l`/`-L` go through `PHP_EVAL_LIBLINE`, frameworks through `PHP_ADD_FRAMEWORK` and their `-F` into `EXTRA_LDFLAGS_PROGRAM` (PHP's program link lines never use `PHP_FRAMEWORKPATH`). Socket arguments need ext/sockets: inside php-src its header is always present, so `runtime.cpp` keys on `HAVE_SOCKETS`. Compiled `-std=c++17 -DQT_NO_KEYWORDS`.[^config]

Linux (`install-debian-trixie.sh`): needs `qt6-base-dev`, `qt6-multimedia-dev`, `libqt6multimediawidgets6`, `g++`, php-dev; configure also needs `qt6-webengine-dev` (`Qt6WebEngineCore` / `Qt6WebEngineWidgets`). The preflight refuses to build when pkg-config lacks the Multimedia or OpenGL widget modules (`qt6-base-dev` carries Qt6OpenGL and Qt6OpenGLWidgets) or `$(qtpaths6 --query QT_INSTALL_PLUGINS)/multimedia` holds no backend plugin (`libqt6multimedia6`; `qtpaths6` is in `qt6-base-dev-tools`). It does not yet preflight WebEngine. Builds in place, installs `qt.so`, writes `30-qt.ini`, removes build artifacts. ≈ 12 s on a Pi 5.[^debian]

macOS (`install-macos.sh`): needs `brew install qt` (carries Multimedia and WebEngine); the same preflight check (it does not yet preflight WebEngine). Builds in a temp copy for `php84` and `zhp`. When the default C++ include path has no libc++ (a Command Line Tools upgrade can leave a stale `/Library/Developer/CommandLineTools/usr/include/c++/v1` ahead of the SDK's), it builds with `-nostdinc++ -isystem <SDK>/usr/include/c++/v1` and says so.[^mac]

Linux CI (`.github/workflows/ci.yml`) runs the Ubuntu cells in `usftechacg/php-qt:<8.4|8.5>-<nts|zts>` (amd64 and arm64, built from `.github/ci/Dockerfile`: the official `php:<tag>-trixie` image with Debian's Qt 6, WebEngine included, and phpize's tools), so they install nothing. macOS cells still install Qt with Homebrew.

Pi loop from the Mac (Pi copy at `~/qt` is disposable):

```bash
fnk 'rm -rf ~/qt'
rsync -az --delete --exclude .git --exclude vendor --exclude composer.lock ./ angel@<pi>:/home/angel/qt/
fnk 'cd ~/qt && bash install-debian-trixie.sh'
```

Verify (Linux over SSH: `export DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000`):

```bash
php --ri qt
composer install && php vendor/bin/pest   # VideoTest opens a QVideoWidget window and plays tests/fixtures/clip.mp4
php examples/smoke.php     # SMOKE_OK
rm -rf vendor composer.lock build.log
```

Probe builds, for the tests in `tests/Probes` (they skip on a release build): copy the tree out of the repo, then `phpize && ./configure --enable-qt --enable-qt-probes && make`. Run Pest with the release `qt.so` left out of the ini scan and the probe one loaded; child processes load it through `PHPQT_PROBE_EXT`:

```bash
mkdir ini && cp $(php-config --ini-dir)/*.ini ini/ && rm ini/*qt*.ini
echo "extension=$PWD/probe/modules/qt.so" > ini/30-qt-probe.ini
PHP_INI_SCAN_DIR=$PWD/ini PHPQT_PROBE_EXT=$PWD/probe/modules/qt.so php -d memory_limit=128M vendor/bin/pest tests/Probes
```

Each probe test runs its code in a child twice: the site kept (the refusal), then `PHPQT_PROBE_OFF=<id>` (the crash, by signal). The main-thread cases need a ZTS PHP with ext-parallel; the libgmalloc cases and the macOS-only sites skip on Linux. Never ship a probe build.

Smoke steps: QApplication up (macOS: Dock icon via `lsappinfo`; Linux: display server connected); pump; 50 ms single-shot QTimer budget; `wakeUp()`; `singleShot` functor; pipe-fd wake through QSocketNotifier; kqueue (macOS) / epoll (Linux) fd nested in Qt's dispatcher; `exec()` ended by `quit()`; disconnect; application destroyed.[^smoke]

[^debian]: install-debian-trixie.sh
[^mac]: install-macos.sh
[^config]: config.m4
[^smoke]: examples/smoke.php
