# Overview

![CI](https://github.com/php-io-extensions/box2d/actions/workflows/ci.yml) ![Packagist](https://packagist.org/packages/php-io-extensions/box2d)…

<div align="center" id="header">

<h2>ext-box2d</h2>

<h4>Box2D v3.1.1 bound 1:1 into PHP 8.4+, with the engine compiled in</h4>


[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/box2d/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/box2d/actions/workflows/ci.yml)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/box2d?style=flat-square)](https://packagist.org/packages/php-io-extensions/box2d)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/box2d/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/box2d)
[![License](https://img.shields.io/github/license/php-io-extensions/box2d?style=flat-square)](https://github.com/php-io-extensions/box2d/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://box2d.org/)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/box2d/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

A game, a simulation or an interactive display needs things to fall, slide, bounce and push each other, and to do it the same way every frame. Writing that in PHP means integrating velocities, finding which shapes overlap, resolving the overlaps without jitter, and keeping stacks of boxes from sinking into each other: a rigid-body solver, which is years of work to get stable and still too slow in PHP once the scene has a few hundred bodies.

<b>Box2D</b> is that solver. Erin Catto's engine has run the 2D physics in games for two decades, and version 3 is a rewrite in C: a world holds bodies, bodies carry shapes, joints tie bodies together, and one `b2World_Step()` per frame moves everything forward with contacts, friction, restitution and sensors resolved. It's deterministic, it parallelises across cores, and its documentation covers every call.

<b>The only problem?</b> PHP can't reach it. The route was FFI: parse `box2d.h`, declare every struct by hand, keep ids and callbacks straight across the C boundary, and run with `ffi.enable` on. This extension binds Box2D v3.1.1 one to one under the C names, with the library compiled into the module from an unchanged copy of the upstream tag, so there is nothing to install from the system and nothing for a package manager to version-skew. Structs are typed classes, ids are checked live before Box2D sees them, Box2D's assertions become exceptions instead of aborts, and a world can step on its own thread pool while your callbacks stay on the PHP thread. No defaults, no composites, no opinions: what Box2D documents is what you call.

### Basic usage

Most ways you will interface with ext-box2d are in two parts -

Build the world. Every `b2*Def` comes from its `b2Default*Def()` function, you set the fields you care about, and the create functions hand back ids. Here a static ground box and a dynamic box above it:

```php
$world = b2CreateWorld(b2DefaultWorldDef());                 // gravity (0, -10)

$ground = b2CreateBody($world, b2DefaultBodyDef());
b2CreatePolygonShape($ground, b2DefaultShapeDef(), b2MakeBox(50.0, 1.0));

$def = b2DefaultBodyDef();
$def->type = b2_dynamicBody;
$def->position = new b2Vec2(0.0, 4.0);
$box = b2CreateBody($world, $def);
$shape = b2DefaultShapeDef();
$shape->density = 1.0;
$shape->material->friction = 0.3;
b2CreatePolygonShape($box, $shape, b2MakeBox(1.0, 1.0));
```

Step it. One `b2World_Step()` per frame with the time step and sub-step count; read positions, velocities, contacts and events between steps. Destroy the world when you're done, which frees everything in it.

```php
for ($i = 0; $i < 90; $i++) {
    b2World_Step($world, 1.0 / 60.0, 4);
}
$p = b2Body_GetPosition($box);
printf("%.2f %.2f\n", $p->x, $p->y);                         // 0.00 2.00: at rest on the ground

b2DestroyWorld($world);
```

```console
$ php falling-box.php
0.00 2.00
```

### Requirements

| | |
|---|---|
| OS | Linux or macOS. `composer.json` lists those two families. |
| PHP | 8.4 or newer, NTS or ZTS. |
| Libraries | None. Box2D ships inside the extension, from tag `v3.1.1` (commit `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`), copied unchanged into `lib/box2d/` and compiled into the module. On Linux the module links `pthread` for the worker pool. |

To build it you need a C compiler and the development files of the PHP you intend to load it into:

```bash
 # Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential php8.4-dev

 # macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
brew install php@8.4
```

### Installation

#### With PHP PIE (recommended)

[PIE](https://github.com/php/pie) is the PHP Foundation's installer for extensions. It downloads the tagged source from Packagist, builds it against the PHP on your `PATH`, installs the module and enables it. `sudo` where your PHP's extension directory is root-owned, as on Debian; not on a Homebrew Mac:

```bash
pie install php-io-extensions/box2d
```

#### Manually (install script)

The repository ships two installers, one per platform. Each one builds for each PHP it targets, installs `box2d.so` into that PHP's `extension_dir`, writes `30-box2d.ini` into its `conf.d` scan directory, and checks the module loads. The macOS one builds in a temporary copy, ad-hoc signs the module so the system loads it on first use, and keeps an ini that already loads box2d instead of writing its own; the Debian one builds in the checkout, writes the ini into every `conf.d` of that PHP (CLI, FPM), and cleans the build products out afterwards.

```bash
git clone https://github.com/php-io-extensions/box2d.git
cd box2d

./install-debian-trixie.sh             # Debian Trixie, Ubuntu 24.04+, Raspberry Pi OS: the php on PATH
./install-macos.sh                     # Homebrew php@8.4 and php@8.4-zts
./install-macos.sh /path/to/bin/php    # either script takes specific PHP binaries
```

#### Manually (phpize)

```bash
git clone https://github.com/php-io-extensions/box2d.git
cd box2d
phpize
./configure --enable-box2d
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
```

Then enable it: add `extension=box2d.so` to your `php.ini`, or drop that line into a file in the scan directory that `php --ini` reports.

#### Verify

```console
$ php --ri box2d

box2d

box2d support => enabled
Version => 0.11.x
Box2D version => 3.1.1
Box2D commit => 8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3
```

### API

Function, struct, enum and constant names are the C names, so [Box2D's documentation](https://box2d.org/documentation/) is the reference: 505 functions, 72 classes and 27 constants, one stub per Box2D header in [`stubs/`](https://github.com/php-io-extensions/box2d/tree/HEAD/stubs) (`base`, `id`, `math_functions`, `collision`, `types`, `box2d`), each declared with its PHP types.

| Header | Functions | What it covers |
|---|---|---|
| `box2d.h` | 313 | Worlds, bodies, shapes, chains, the eight joint types, events, queries, casts, debug draw. |
| `collision.h` | 72 | Shapes as geometry: polygons, circles, capsules, segments, hulls, rays, manifolds, the dynamic tree. |
| `math_functions.h` | 73 | `b2Vec2`, `b2Rot`, `b2Transform`, `b2AABB` and the vector math on them. |
| `types.h` | 17 | The `b2Default*Def()` constructors: world, body, shape, chain, filters, surface material, every joint, explosion, debug draw. |
| `id.h` | 10 | Packing each id kind to an `int` and back (`b2StoreBodyId()`, `b2LoadBodyId()` …). |
| `base.h` | 7 | The version, the byte count, timers, `b2Yield()` and `b2Hash()`. |
| values and macros | 13 | `b2_nullBodyId`, `b2Vec2_zero`, `b2Transform_identity` and the other static values, as functions. |

#### Translations

The only differences from C:

- A struct is a `final` class of the same name with one typed property per field, in field order; the constructor takes every field, zero by default, with nested structs fresh. Ids (`b2WorldId`, `b2BodyId` …) are struct classes.
- A fixed C array in a struct is a list. A `const T*` argument is a `T` object; a scalar out-parameter is by-reference; an in/out struct is updated in place; an input array with a count is `array, int`; an output array with a capacity is `?array &$list, int $capacity`, returning the count.
- `uint64_t` bits are PHP `int` with the same 64 bits (`B2_DEFAULT_MASK_BITS` is `-1`). Narrow integers are range-checked.
- A callback is a `callable` with its `mixed $context` passed through unchanged. Struct fields holding callbacks (`b2WorldDef.frictionCallback`, `b2DebugDraw.Draw*Fcn`) are `?Closure`.
- Static values (`b2_nullBodyId`, `b2Vec2_zero`, `b2Transform_identity` …) are functions returning a fresh instance.
- `b2DynamicTree` is an opaque handle, destroyed when its last reference goes if `b2DynamicTree_Destroy` was not called.

#### Errors

- A dead id, a def not made by a `b2Default*Def()` function, or an integer out of range is a `ValueError` before Box2D sees it. On ZTS, an id from another PHP thread is an `Error`.
- A failed Box2D assertion is a `b2AssertionError` naming the condition, file and line. Assertions stay on in every build; Box2D never aborts the process.
- While a world steps, its callbacks may read what Box2D does not write during a step (validity, types, user data, filters, materials); any other call on that world is an `Error("world is stepping")`.
- An exception thrown in a callback stops that callable for the rest of the step (Box2D's default answer is used) and is rethrown when the call returns. A return value of the wrong type is a `TypeError`.

#### Workers

Set `b2WorldDef::$workerCount` above 1 and the world gets its own pool of `min(workerCount, 64)` threads for its steps. `b2World_Step()` still blocks until the step is done; the pool only spreads it over more cores. Results are identical bit for bit for every worker count.

Friction, restitution, custom filter and pre-solve callables still run on the PHP thread that called `b2World_Step()`: a worker thread hands the call over and waits. A pool does not survive `fork()`, so stepping a pooled world in a child is an `Error`; serial worlds keep working. Each request's worlds, pools and dynamic trees are freed when the request ends.

### Extensions you might use with this one

* [ext-epoll](https://github.com/php-io-extensions/epoll) and [ext-kqueue](https://github.com/php-io-extensions/kqueue): a frame loop that waits on input, sockets and a timer between steps. `b2World_Step()` is a plain blocking call, so it slots into any loop that owns its own wait.
* [ext-posi](https://github.com/php-io-extensions/posi): hardware in the loop. Sensor readings over I2C or a serial port become forces and impulses; body positions go back out to a display or a servo.

### AI-assisted development

This codebase was built with LLM assistance under human direction. Prompts, reviews, and architectural decisions were owned by a professional software engineer — the model accelerates drafting and exploration; it does not replace judgment on APIs, dependency direction, or what ships.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/box2d/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records what the README doesn't: every function, class and constant by header and the complete list of translations from C, each guard that runs before Box2D and the error it raises, how the worker pool is built, how callbacks reach the stepping thread, what `fork()` and request end do to a pool, and a log of every change that altered behaviour.

Start at [`.okf/index.md`](/docs/{{version}}/ecosystem/standalone-extensions/box2d/overview). [`AGENTS.md`](https://github.com/php-io-extensions/box2d/blob/HEAD/AGENTS.md) is the short rule sheet an agent reads before touching the C, the stubs, the vendored Box2D, or packaging; each rule points into the bundle for the reason behind it.

Point your agent at the repo and it has the same context the maintainer has. Point yourself at it when the README's answer is "it does X" and you want "because".

### Resources

* [Box2D documentation](https://box2d.org/documentation/): the manual for every call this extension binds; this README only adds what PHP changes.
* [Box2D v3.1.1](https://github.com/erincatto/box2d/tree/v3.1.1): the upstream tag vendored in [`lib/box2d/`](https://github.com/php-io-extensions/box2d/tree/HEAD/lib/box2d), unchanged.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`stubs/`](https://github.com/php-io-extensions/box2d/tree/HEAD/stubs) holds the API declarations; each `*_arginfo.h` is generated from its stub.
* [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): the spec the [`.okf/`](https://github.com/php-io-extensions/box2d/tree/HEAD/.okf) bundle follows.

### Running the test suite

The suite is Pest v4: worlds, bodies, shapes, chains, joints, events, geometry, the dynamic tree, debug draw, guards, callback errors, workers, and a lifecycle test that spawns child PHP processes to check pools, `fork()` and request end. It runs on Linux and macOS. Build the module, then enable it through an ini scan directory rather than `-d`, so the child processes the lifecycle test starts load it too:

```bash
git clone https://github.com/php-io-extensions/box2d.git
cd box2d
phpize && ./configure --enable-box2d && make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
composer install
mkdir -p /tmp/box2d-ini && echo "extension=$PWD/modules/box2d.so" > /tmp/box2d-ini/box2d.ini
PHP_INI_SCAN_DIR=":/tmp/box2d-ini" php -d memory_limit=128M vendor/bin/pest
```

```console
Tests:    99 passed (1397 assertions)
Duration: 2.81s
```

The leading `:` keeps your PHP's own scan directory and adds the second one. If that PHP already loads an installed `box2d.so`, the suite warns `Module "box2d" is already loaded` and tests the installed one instead; copy the scan directory somewhere, replace its box2d ini with the line above, and point `PHP_INI_SCAN_DIR` at the copy without the colon. A module only loads in the PHP whose `phpize` built it: for Homebrew's ZTS build, run `phpize` and pass `--with-php-config` from `/opt/homebrew/opt/php@8.4-zts/bin`. Set `XDEBUG_MODE=off` for any timing you intend to read.

### Contributing

Open an issue first for anything beyond a typo. Pull requests change a stub in `stubs/` and the C under `src/` together, regenerate the `*_arginfo.h` files with gen_stub, and add a Pest test for the behaviour. `lib/box2d/` is upstream and is never edited: a newer Box2D lands only by replacing it from a published tag. CI must be green on every cell of the matrix, NTS and ZTS alike. Read [`AGENTS.md`](https://github.com/php-io-extensions/box2d/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

ext-box2d runs Box2D's C code on values from PHP, and threads when a world has workers. See [SECURITY.md](https://github.com/php-io-extensions/box2d/blob/HEAD/SECURITY.md) for what it guards against and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/box2d/tree/HEAD/LICENSE). Box2D is MIT, Copyright (c) 2022 Erin Catto: [`lib/box2d/LICENSE`](https://github.com/php-io-extensions/box2d/tree/HEAD/lib/box2d/LICENSE).
