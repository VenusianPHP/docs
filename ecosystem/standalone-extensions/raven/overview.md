# Overview

![CI](https://github.com/php-io-extensions/raven/actions/workflows/ci.yml)

<div align="center" id="header">

<h2>ext-raven</h2>

<h4>Raven 0.3.0 bound 1:1 into PHP 8.4+, with the toolkit compiled in</h4>

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/raven/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/raven/actions/workflows/ci.yml)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/raven?style=flat-square)](https://packagist.org/packages/php-io-extensions/raven)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/raven/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/raven)
[![License](https://img.shields.io/github/license/php-io-extensions/raven?style=flat-square)](https://github.com/php-io-extensions/raven/blob/v0.11.0/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://github.com/oscar-soirey/Raven)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

An editor, a tool or a control panel needs windows, buttons, lists, trees, text editors and docked panels that lay themselves out, take keyboard and mouse input, and redraw only what changed. Writing that in PHP means a widget tree, a layout engine, text shaping, a renderer and a window system per platform: a GUI toolkit, which is years of work before the first button looks right.

<b>Raven</b> is that toolkit. Oscar Soirey's library is a retained-mode GUI in C: windows hold widget trees, panels place their children, controls report changes through callbacks, interfaces can be written in XML, and a Vulkan renderer draws them on native Cocoa, X11 or Wayland windows. Its layout and painting run on worker and render threads while the application stays on one UI thread.

<b>The only problem?</b> PHP can't reach it. This extension binds every function of `Raven.h` one to one under the C names, with Raven compiled into the module from an unchanged copy of upstream main (`fc37a06`, library 0.3.0), so there is nothing to install from the system but libX11 on Linux. Structs are typed classes, callbacks are PHP callables that always run on the PHP thread, sizes and ranges are checked before Raven sees them, and Raven's errors come back through its own `RError` codes and error callback. No defaults, no composites, no opinions: what Raven documents is what you call.

## Basic usage

Build an interface, bind what it does, run the loop:

```php
Rinit(R_BACKEND_VULKAN);

$xml = <<<'XML'
<VBox Padding="12" Spacing="8">
  <Label Text="Name"/>
  <TextInput Name="name"/>
  <Button Text="Greet" OnClicked="app.greet"/>
</VBox>
XML;

$window = Rwindow_create('Hello', 480, 200, R_WINDOW_DEFAULT);
Rwindow_set_content($window, Rwidget_create_from_xml($xml, strlen($xml)));

Raction_bind('app.greet', function (int $sender, ?string $action, mixed $window): void {
    Rwindow_set_title($window, 'Hello, ' . Rtext_input_get_text(Rwidget_find($window, 'name')));
}, $window);

while (Rwait_frame(-1.0)) {
}
Rshutdown();
```

The same widgets are built from code with `Rwidget_create`, `Rbutton_create`, `Rwidget_add_child` and the setters of each control. For a test or a server without a display, `Rinit_ex(new RInitDesc(backend: R_BACKEND_NULL, headless: R_TRUE))` runs everything without opening a window or drawing.

## Requirements

- PHP 8.4 or newer, NTS or ZTS, with `phpize` and `php-config`.
- A C11 compiler.
- Linux: libX11 headers and `pkg-config`. Wayland, D-Bus and the Vulkan loader are opened at run time.
- macOS: Xcode Command Line Tools.
- To show windows: a Vulkan loader at run time (MoltenVK on macOS). Without one, `Rinit(R_BACKEND_VULKAN)` fails with `R_ERROR_BACKEND`; `R_BACKEND_NULL` always works.

```bash
# Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential pkg-config libx11-dev php8.4-dev

# macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
brew install molten-vk vulkan-loader   # only to show windows
```

## Installation

### With PHP PIE (recommended)

```bash
pie install php-io-extensions/raven
```

### Manually (install script)

```bash
git clone https://github.com/php-io-extensions/raven.git
cd raven

./install-debian-trixie.sh             # Debian Trixie, Ubuntu 24.04+, Raspberry Pi OS: the php on PATH
./install-macos.sh                     # Homebrew php@8.4 and php@8.4-zts
./install-macos.sh /path/to/bin/php    # either script takes specific PHP binaries
```

The macOS installer builds in a temporary copy for each PHP, installs `raven.so`, ad-hoc signs it, and writes `30-raven.ini` unless an ini in that scan directory already loads raven. The Debian installer needs `libx11-dev` and `pkg-config`, builds in the checkout, writes `30-raven.ini` into each conf.d of that PHP, and cleans the build products afterwards. A full build compiles Raven's sources: about a minute per PHP on a Mac. The Debian installer has not yet been run on the Pi.

### Manually (phpize)

```bash
git clone https://github.com/php-io-extensions/raven.git
cd raven
phpize
./configure --enable-raven
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
```

Then add `extension=raven.so` to your `php.ini`, or to a file in the scan directory `php --ini` reports.

### Verify

```console
$ php --ri raven

raven

raven support => enabled
Version => 0.11.0
Raven version => 0.3.0
Raven commit => fc37a06763395c9557c1723b41f1bd7b89e2caef
Vulkan-Headers commit => b379292b2ab6df5771ba9870d53cf8b2c9295daf
```

## API

All 1,623 functions of `Raven.h` but five raw-memory ones (`Rmemory_alloc`, `Rmemory_realloc`, `Rmemory_free`, `Rpixels_alloc`, `Rpixels_free`): 1,618 functions, 45 classes, every enumerator and public `#define` as a constant. The stubs in [`stubs/`](https://github.com/php-io-extensions/raven/tree/v0.11.0/stubs) are the reference, one file per Raven header, with that header's comments on the functions; Raven's own headers in [`lib/raven/include/raven/`](https://github.com/php-io-extensions/raven/tree/v0.11.0/lib/raven/include/raven) and [Raven's documentation](https://oscar-soirey.github.io/Raven/) document what each call does. Main [`fc37a06`](https://github.com/oscar-soirey/Raven/commit/fc37a06763395c9557c1723b41f1bd7b89e2caef) ([PR #276](https://github.com/oscar-soirey/Raven/pull/276)) restores the implementations those APIs need on main. Device services (`raven_device.h`), DiffView, SystemWebView, table checkbox/progress columns, ComboBox editable/searchable, TextEditor search/replace, spell check, animated GIF/APNG, clipboard images, notification actions and time zones sit on top of UI test automation, IME composition, PNG encode/save, Carousel, MapView, and Raven Script.

See [bindings](/docs/{{version}}/ecosystem/standalone-extensions/raven/api/bindings) for the translations, [callbacks](/docs/{{version}}/ecosystem/standalone-extensions/raven/architecture/callbacks) for how callables run, and [the generator](/docs/{{version}}/ecosystem/standalone-extensions/raven/architecture/generator) for how the stubs are made.

### Translations

| C | PHP |
|---|-----|
| `Rid`, `Ruint`, `int`, enums, `size_t`, `uint64_t` | `int`, range-checked to the C type (`ValueError`) |
| `float`, `double` | `float` |
| `const char*` | `?string`; with a `size_t` after it, the size must not pass the string's end |
| `int*`, `float*`, `double*`, `Ruint*`, `const char**` | by-reference parameter, written after the call |
| `const T*`, `T*` (struct) | `?T`, a final class with one typed property per C field; `T*` is written back |
| `float[4]` field | `array` of exactly 4 floats |
| `const uint8_t* rgba, int width, int height` | `string` of at least `width × height × 4` bytes (two consecutive pixel buffers share the following `width`/`height`) |
| `uint8_t* diff_rgba` sized by `width`/`height` | `?string` written after the call |
| `const void* data, size_t size` | `string` and the size, which must not pass its end |
| `const double*`, `const float*`, `const char* const*`, `const T*` with a count | `array` holding at least `count` elements |
| `const float*` sized by the two preceding `int`s (`Rchart_set_grid`) | `array` holding at least `rows × columns` floats |
| callback + `void* user_data` | `?callable` + `mixed`; the callable gets the C arguments with `user_data` in its C place |
| `void*` user handle (`Rwidget_set_user_handle` …) | `mixed`, held per widget, window, tree item or node |
| `RPainter*` | `RPainter`, valid until its paint callback returns |
| `RActionContext*` | `RActionContext`, valid until its parameterized-action callback returns |
| Vulkan handles, native window fields | `int` addresses |
| returned pixels / file contents | `?string`, Raven's memory released before return |

### Callbacks and threads

Raven runs every widget callback on its UI thread, inside `Rdraw_frame`, `Rwait_frame` or `Rwait_events`; the UI thread is the PHP thread that called `Rinit`, so callables run directly. An exception a callable throws comes out of the Raven call that ran it, and no other callable runs until then.

Workers and the render thread never enter PHP. `Rparallel_for` runs every range on the PHP thread before it returns; `Rtask_run_async` hands its task back to the UI thread with `Rtask_post`; render-thread callbacks (viewport drawing, the Vulkan queue lock, a custom backend) wait for the PHP thread to serve them, at its next VM interrupt or Raven frame, and take their no-op result if it does not start within the deadline (100 ms for viewport drawing, 5 s otherwise). `RInitDesc::$disable_render_thread = R_TRUE` keeps rendering on the PHP thread.

The extension keeps each callable while Raven may call it, releases those of destroyed widgets on a sweep, and releases all of them at `Rshutdown` and at request end (which shuts Raven down if the script did not).

### Errors

Arguments that do not fit the C type are a `ValueError` or `TypeError` before Raven is called. Using Raven in a process forked after `Rinit` is an `Error`. Everything else is Raven's: return values, `Rerror_get_last()`, and `Rerror_set_callback()`.

## Running the test suite

```bash
composer install
XDEBUG_MODE=off php -d memory_limit=128M vendor/bin/pest
```

Tests run Raven headless on the null backend: no window opens. At v0.11.0 the suite is 75 passed (703 assertions). The crash sweep (`php tools/sweep.php`) calls every bound function with zero/null arguments, one child process each: no crash; the three headless file dialogs and four device pickers time out waiting for a host result; ten `RActionContext` getters fail the sweep's `new` (private constructor). See [build, install, test](/docs/{{version}}/ecosystem/standalone-extensions/raven/runbooks/build-install-test).

## Security

See [SECURITY.md](https://github.com/php-io-extensions/raven/blob/v0.11.0/SECURITY.md).

## License

MIT, for the extension. Raven is Apache-2.0 ([`lib/raven/LICENSE`](https://github.com/php-io-extensions/raven/blob/v0.11.0/lib/raven/LICENSE), [`lib/raven/NOTICE`](https://github.com/php-io-extensions/raven/blob/v0.11.0/lib/raven/NOTICE), its third-party notices in [`lib/raven/THIRD_PARTY.md`](https://github.com/php-io-extensions/raven/blob/v0.11.0/lib/raven/THIRD_PARTY.md)); the Vulkan headers are Apache-2.0 or MIT ([`lib/vulkan-headers/LICENSE.md`](https://github.com/php-io-extensions/raven/blob/v0.11.0/lib/vulkan-headers/LICENSE.md)).
