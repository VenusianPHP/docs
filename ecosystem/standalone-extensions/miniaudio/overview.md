# Overview

![CI](https://github.com/php-io-extensions/miniaudio/actions/workflows/ci.yml) ![Packagist](https://packagist.org/packages/php-io-extensions/miniaudio)…

<div align="center" id="header">

<h2>ext-miniaudio</h2>

<h4>miniaudio 0.11.26 bound 1:1 into PHP 8.4+, with the library compiled in</h4>

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/miniaudio/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/miniaudio/actions/workflows/ci.yml)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/miniaudio?style=flat-square)](https://packagist.org/packages/php-io-extensions/miniaudio)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/miniaudio/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/miniaudio)
[![License](https://img.shields.io/github/license/php-io-extensions/miniaudio?style=flat-square)](https://github.com/php-io-extensions/miniaudio/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://miniaud.io/)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

A game, a music tool, a voice app or a kiosk needs to play sound: open the speakers, decode a WAV or an MP3, mix several sounds, move them around a listener, record from a microphone. In PHP that has meant shelling out to a player, or writing raw bytes to a device file and hoping the format matches, and none of it mixes, resamples or keeps time.

<b>miniaudio</b> does all of it. David Reid's single-file C library talks to CoreAudio, ALSA, PulseAudio and JACK, decodes WAV, FLAC, MP3 and Vorbis, converts formats, channels and sample rates, and builds from a low-level device API up to a node graph and a mixing engine with 3D sound. It has no dependencies of its own, and it loads the platform's audio system at runtime.

<b>The only problem?</b> PHP can't reach it. The route was FFI: declare a thousand functions and two hundred structs by hand, keep the memory miniaudio holds pointers into alive, and find a way for an audio thread to call back into PHP, which it must never do. This extension binds miniaudio 0.11.26 one to one under the C names, with the library compiled into the module from an unchanged copy of the upstream tag, so there is nothing to install from the system. Structs are typed classes, the objects miniaudio keeps pointers into are handle classes that hold the C struct in place, PCM crosses as strings whose size is checked against the frame count, and miniaudio's threads hand every callback to the PHP thread that owns it. No defaults, no composites, no opinions: what miniaudio documents is what you call.

### Basic usage

Most ways you will interface with ext-miniaudio are in two parts -

Play files through the engine. `ma_engine` opens the default device and mixes everything you start on it; each `ma_sound` is one file, streamed or decoded up front. Like C, you make the storage with `new` and an `_init` call fills it:

```php
$engine = new ma_engine();
ma_engine_init(null, $engine);                                   // default device, its native rate and channels

$sound = new ma_sound();
ma_sound_init_from_file($engine, 'theme.mp3', MA_SOUND_FLAG_STREAM, null, null, $sound);
ma_sound_set_volume($sound, 0.8);
ma_sound_start($sound);

while (ma_sound_is_playing($sound)) {
    usleep(10000);
}
ma_engine_uninit($engine);                                       // uninitializes its sounds first
```

Feed a device yourself. A data callback runs whenever the device wants frames; miniaudio's audio thread hands it to your PHP thread, which runs it while it is in PHP code or waiting inside a miniaudio call. Here a sine from `ma_waveform` fills the buffer:

```php
$wave = new ma_waveform();
ma_waveform_init(ma_waveform_config_init(ma_format_f32, 2, 48000, ma_waveform_type_sine, 0.2, 440.0), $wave);

$config = ma_device_config_init(ma_device_type_playback);
$config->playback->format = ma_format_f32;
$config->playback->channels = 2;
$config->sampleRate = 48000;
$config->dataCallback = function (ma_device $device, ?string &$output, ?string $input, int $frameCount) use ($wave): void {
    ma_waveform_read_pcm_frames($wave, $output, $frameCount, $read);
};

$device = new ma_device();
ma_device_init(null, $config, $device);
ma_device_start($device);
$end = microtime(true) + 2.0;
while (microtime(true) < $end) {
    usleep(1000);                                                // callbacks are served between these
}
ma_device_uninit($device);
```

Both run as shown; on a machine without speakers, pass a context made with `ma_context_init([ma_backend_null], 1, null, $ctx)` as the device's context (or the engine config's `pContext`) and they run silently.

### Requirements

| | |
|---|---|
| PHP | 8.4 or newer, NTS or ZTS |
| OS | Linux, macOS |
| Build | a C compiler, `phpize` and `php-config` for the PHP you install into |
| Runtime | nothing extra: CoreAudio on macOS, ALSA / PulseAudio / JACK on Linux, each loaded at runtime when present |

```bash
# Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential php8.4-dev

# macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
```

### Installation

### With PHP PIE (recommended)

```bash
pie install php-io-extensions/miniaudio
```

PIE builds the module against the PHP it runs under and enables it.

### Manually (install script)

The repository ships two installers, one per platform. Each one builds for each PHP it targets, installs `miniaudio.so` into that PHP's `extension_dir`, writes `30-miniaudio.ini` into its `conf.d` scan directory, and checks the module loads. The macOS one builds in a temporary copy, ad-hoc signs the module so the system loads it on first use, and keeps an ini that already loads miniaudio instead of writing its own; the Debian one builds in the checkout, writes the ini into every `conf.d` of that PHP (CLI, FPM), and cleans the build products out afterwards.

```bash
git clone https://github.com/php-io-extensions/miniaudio.git
cd miniaudio

./install-debian-trixie.sh             # Debian Trixie, Ubuntu 24.04+, Raspberry Pi OS: the php on PATH
./install-macos.sh                     # Homebrew php@8.4 and php@8.4-zts
./install-macos.sh /path/to/bin/php    # either script takes specific PHP binaries
```

### Manually (phpize)

```bash
git clone https://github.com/php-io-extensions/miniaudio.git
cd miniaudio
phpize
./configure --enable-miniaudio
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
```

Then enable it: add `extension=miniaudio.so` to your `php.ini`, or drop that line into a file in the scan directory that `php --ini` reports.

### Verify

```console
$ php --ri miniaudio

miniaudio

miniaudio support => enabled
Version => 0.11.1
miniaudio version => 0.11.26
miniaudio commit => 877ea4a7c2601c7b0f2a44e83dfac42e6470fea6
```

### API

924 functions, 193 classes, 4 interfaces and 391 constants: every `MA_API` function in the public section of `miniaudio.h` except the six raw-memory functions (`ma_malloc` and friends: every buffer crosses as a string) and `ma_log_postv` (a C `va_list` has no PHP form). The names are the C names. [`miniaudio.h`](https://github.com/php-io-extensions/miniaudio/blob/HEAD/lib/miniaudio/miniaudio.h) and [miniaud.io](https://miniaud.io/docs/) document every call; the stubs in [`stubs/`](https://github.com/php-io-extensions/miniaudio/tree/HEAD/stubs) give the PHP signature of each.

### Translations

- **Value structs** (configs, `ma_device_info`, `ma_vec3f`, `ma_job` …) are final classes with one typed property per C field, in order. The constructor takes every field as an optional named argument; `*_config_init()` returns a filled one. Anonymous inner structs get a class named after the path (`ma_device_config_playback`). A typedef of a struct is its own class with the same fields (`ma_sound_group_config`).
- **Handle classes** (`ma_engine`, `ma_sound`, `ma_device`, `ma_decoder`, every filter, node and buffer …) hold the C struct in place, because miniaudio keeps pointers into it. `new` is the uninitialized storage, the `_init` call fills it, and the C struct's plain fields read as live read-only properties (`$device->sampleRate`, `$device->playback['format']`, `$decoder->outputChannels`). Freeing the object uninitializes it. Handles are not cloneable.
- **Interfaces** `ma_data_source`, `ma_node`, `ma_vfs` and `ma_async_notification` stand for miniaudio's `void` typedefs: every data source, node, VFS and notification class implements the matching one.
- **PCM** is a string: an output buffer is a by-reference `?string` sized by the call, an input buffer must hold at least the frames the call names, and every size is a frame count times the frame size of the object involved, checked for overflow. A scalar `T*` is a by-reference `int`/`float`; a struct `T*` is an object updated in place; channel maps and backend lists are arrays.
- **Callbacks** are callables (or `?Closure` properties on structs), with the C arguments translated by the same rules. `void*` user data is `mixed`.
- **Ownership.** A handle that another one points into (an engine under its sounds, a graph under its nodes, a context under its devices) is kept alive by it, and uninitializing it uninitializes the dependents first.

### Errors

- A handle that is not initialized, a short PCM string, an out-of-range narrow integer, a too-long string for a `char[]` field, or a non-null `ma_allocation_callbacks` is a `ValueError` before miniaudio sees it. A null handle gets miniaudio's own `MA_INVALID_ARGS`.
- miniaudio's results come back as the `int` it returns (`MA_SUCCESS`, `MA_INVALID_ARGS` …); `ma_result_description()` names them.
- An exception thrown by a callback is rethrown when the miniaudio call it ran under returns; a return value of the wrong type is a `TypeError`.

### Threads and callbacks

miniaudio calls back on its own threads: the device's audio thread, resource manager job threads. Those never enter PHP. They queue the callback to the PHP thread that owns the object, which runs it at its next opcode boundary, or while it waits inside a miniaudio call that can wait on such a thread (`ma_device_stop`, `ma_engine_uninit`, `ma_fence_wait` …, which run on a helper thread meanwhile). A callback that is not picked up in time gets miniaudio's no-op answer: silence for audio, `MA_BUSY` for a data source read, `MA_ERROR` elsewhere. Sleeping in C (`sleep()`) starves the audio; a loop with `usleep()` serves it. A device, engine or resource manager made before `fork()` is an `Error` in the child; everything else keeps working there. Each request uninitializes what it left, newest first.

Every extension point miniaudio has is reachable from PHP: data sources (`ma_data_source_vtable`), nodes (`ma_node_vtable`), VFS (`ma_vfs_callbacks` objects), decoding backends, resampling backends, device backends (`ma_backend_callbacks`), custom jobs and async notifications.

### Extensions you might use with this one

* [php-io-extensions/box2d](https://github.com/php-io-extensions/box2d): 2D physics, for the collisions your sounds follow.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/miniaudio/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records what the README doesn't: how the generator decides each translation, the handle and ownership model, the callback queue, and how to build and test.

### Resources

* [miniaudio documentation](https://miniaud.io/docs/): the manual for every call this extension binds; this README only adds what PHP changes.
* [miniaudio 0.11.26](https://github.com/mackron/miniaudio/tree/0.11.26): the upstream tag vendored in [`lib/miniaudio/`](https://github.com/php-io-extensions/miniaudio/tree/HEAD/lib/miniaudio), unchanged.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`stubs/`](https://github.com/php-io-extensions/miniaudio/tree/HEAD/stubs) holds the API declarations; each `*_arginfo.h` is generated from its stub.
* [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): the spec the [`.okf/`](https://github.com/php-io-extensions/miniaudio/tree/HEAD/.okf) bundle follows.

### Running the test suite

The suite is Pest v4: coverage of every function, value structs, utilities, filters, conversion, data sources, devices, node graphs, the resource manager, the engine, the callback queue and every custom backend family, guards, and a lifecycle test that spawns child PHP processes and a built-in server. Devices run on miniaudio's null backend, so it makes no sound and needs no audio hardware. Build the module, then enable it through an ini scan directory rather than `-d`, so the child processes load it too:

```bash
git clone https://github.com/php-io-extensions/miniaudio.git
cd miniaudio
phpize && ./configure --enable-miniaudio && make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
composer install
mkdir -p /tmp/miniaudio-ini && echo "extension=$PWD/modules/miniaudio.so" > /tmp/miniaudio-ini/miniaudio.ini
PHP_INI_SCAN_DIR=":/tmp/miniaudio-ini" php -d memory_limit=128M vendor/bin/pest
```

```console
Tests:    62 passed (362 assertions)
Duration: 5.68s
```

The leading `:` keeps your PHP's own scan directory and adds the second one. If that PHP already loads an installed `miniaudio.so`, the suite tests the installed one; point `PHP_INI_SCAN_DIR` at a copy of the scan directory without it. A module only loads in the PHP whose `phpize` built it: for Homebrew's ZTS build, run `phpize` and pass `--with-php-config` from `/opt/homebrew/opt/php@8.4-zts/bin`.

### Contributing

Open an issue first for anything beyond a typo. The binding is generated: `tools/extract.php` reads clang's AST of `miniaudio.h` into `tools/api.json`, and `tools/generate.php` writes the stubs and `src/gen/` from it plus the per-function decisions in `tools/bindings.php`. Change the generator or `tools/bindings.php`, regenerate, regenerate the `*_arginfo.h` files with gen_stub, and add a Pest test for the behaviour. `lib/miniaudio/` is upstream and is never edited. CI must be green on every cell of the matrix, NTS and ZTS alike. Read [`AGENTS.md`](https://github.com/php-io-extensions/miniaudio/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

ext-miniaudio runs miniaudio's C code on values from PHP, on miniaudio's threads as well as PHP's, and reads the files and devices you name. See [SECURITY.md](https://github.com/php-io-extensions/miniaudio/blob/HEAD/SECURITY.md) for what it guards against and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/miniaudio/tree/HEAD/LICENSE). miniaudio is public domain or MIT No Attribution, at your choice, Copyright 2025 David Reid: [`lib/miniaudio/LICENSE`](https://github.com/php-io-extensions/miniaudio/tree/HEAD/lib/miniaudio/LICENSE). `lib/miniaudio/extras/stb_vorbis.c` is public domain or MIT, by Sean Barrett.
