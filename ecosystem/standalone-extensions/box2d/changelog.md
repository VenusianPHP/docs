# Changelog

What changed in this package, newest first.

### 2026-10-12

* **Version**: 0.10.5 in `PHP_BOX2D_VERSION`, `AGENTS.md`, `VersionTest` and this bundle. No API change. First tag; the number lines up with the sibling extensions.
* **README**: rewritten on the php-io-extensions template (header badges, two-part basic usage, requirements table, PIE / install script / phpize install paths, API, OKF section, suite run). The falling-box example and the suite count (99 passed, 1397 assertions) were run against a scratch build on Homebrew PHP 8.4 NTS.
* **install-debian-trixie.sh**: the post-install check tested `function_exists("SDL_Init")`, left over from the sdl3 installer it was copied from, so it passed only where ext-sdl3 was also installed. It now tests `extension_loaded("box2d")`.

### 2026-10-11

* Bundle created with ext-box2d 0.10.0: Box2D v3.1.1 vendored, 505 functions, 72 classes, 27 constants. Phase 9 workers verified (pool, callback queue, fork, request end); `LifecycleTest` added; `install-debian-trixie.sh` added. Suite 99 tests green on macOS NTS + ZTS and Pi 5 ZTS. [bindings](/docs/{{version}}/ecosystem/standalone-extensions/box2d/api/bindings), [guards](/docs/{{version}}/ecosystem/standalone-extensions/box2d/architecture/guards-and-errors), [workers](/docs/{{version}}/ecosystem/standalone-extensions/box2d/architecture/workers-and-callbacks), [build](/docs/{{version}}/ecosystem/standalone-extensions/box2d/runbooks/build-install-test).
