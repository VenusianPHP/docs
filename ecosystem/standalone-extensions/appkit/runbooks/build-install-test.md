# Build, install, test

install-macos.sh into php84 + zhp, Pest, the probe build, smoke, clean tree.

## Overview

`bash install-macos.sh` builds in a temp copy (repo stays clean) for Homebrew php@8.4 (NTS, `php84`) and php@8.4-zts (`zhp`), installs `appkit.so` into each extension_dir, ad-hoc signs it, writes `30-appkit.ini`. Other PHPs: pass binaries as args. Clean build of both ≈ 13 s; incremental `make` recompiles only the touched `.m`.[^installer]

`config.m4`: `PHP_ADD_SOURCES` knows only .c/.s/.S/.cpp, so it writes each `.m` rule itself (`-x objective-c -fno-objc-arc -fobjc-exceptions`) and appends to `shared_objects_appkit`. Links the frameworks in `APPKIT_FRAMEWORKS` (Foundation, CoreFoundation, AppKit, AVKit, AVFoundation, CoreMedia, QuartzCore, CoreGraphics, OpenGL, IOKit, GameController) and objc.[^config]

Verify:

```bash
php84 --ri appkit && zhp --ri appkit
composer install && php84 vendor/bin/pest && zhp vendor/bin/pest
php84 examples/smoke.php          # SMOKE_OK
php84 examples/smoke.php --hold=10 # icon stays up 10 s to look at
rm -rf vendor composer.lock
```

Probe build (`tests/Probes`; skipped by any other build). Build in a scratch copy, never install it:

```bash
P=$(mktemp -d)/appkit && rsync -a --exclude vendor --exclude .git ./ "$P"/
(cd "$P" && /opt/homebrew/opt/php@8.4/bin/phpize \
  && ./configure --enable-appkit --enable-appkit-probes --with-php-config=/opt/homebrew/opt/php@8.4/bin/php-config && make)
composer install
APPKIT_PROBE_EXT="$P/modules/appkit.so" php84 -n -d memory_limit=128M -d extension="$P/modules/appkit.so" vendor/bin/pest tests/Probes
rm -rf "$(dirname "$P")" vendor composer.lock
```

Each probe test runs its call in a child of that PHP (`-n`, only the probe build loaded) twice: site on (refused, clean exit) and `APPKIT_PROBE_OFF=<id>` (the signal). `MainThreadTest` needs a ZTS build (`zhp`, built with `php@8.4-zts`'s phpize/php-config) and ext-parallel (`APPKIT_PROBE_PARALLEL` or the extension_dir's `parallel.so`). Sites: [errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/errors-and-threads).

Smoke steps: Dock icon up (`lsappinfo list` type `Foreground`), pump, 50 ms budget, posted-event wake, pipe-fd wake, kqueue fd nested in the run loop, `run()` stopped by a callout, Dock icon gone (`BackgroundOnly`). Needs a logged-in GUI session.[^smoke]

[^installer]: install-macos.sh
[^config]: config.m4
[^smoke]: examples/smoke.php
