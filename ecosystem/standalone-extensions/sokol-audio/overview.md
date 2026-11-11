# Overview

![CI](https://github.com/php-io-extensions/sokol-audio/actions/workflows/ci.yml) ![Packagist](https://packagist.org/packages/php-io-extensions/sokol-audio)…

<div align="center" id="header">

<h2>ext-sokol-audio</h2>

<h4>sokol_audio.h bound 1:1 into PHP 8.4+, with the library compiled in</h4>

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/sokol-audio/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/sokol-audio/actions/workflows/ci.yml)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/sokol-audio?style=flat-square)](https://packagist.org/packages/php-io-extensions/sokol-audio)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/sokol-audio/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/sokol-audio)
[![License](https://img.shields.io/github/license/php-io-extensions/sokol-audio?style=flat-square)](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://github.com/floooh/sokol)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/sokol-audio/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

A game, an emulator, a synthesizer or a kiosk that beeps needs to get samples to the speakers, continuously, without gaps. PHP can generate samples well enough, but it has no way to hand them to the sound card: you shell out to a player, write a WAV and hope, or reach for a full audio framework when all you wanted was a stream of floats.

<b>sokol_audio.h</b> is that stream. Andre Weissflog's single-file C library opens the platform's audio output (CoreAudio on macOS, PulseAudio on Linux) and asks for 32-bit float samples, mono or stereo, either through a callback on its own audio thread or from a ring buffer you push into from your main loop. Eleven functions, five structs, no mixing, no decoding, no opinions.

<b>The only problem?</b> PHP can't reach it, and the callback model runs on a thread PHP can't enter. This extension binds sokol_audio.h one to one under the C names, with the library compiled into the module from an unchanged copy of the upstream source. Structs are typed classes. The stream callback and the logger are PHP closures that run on your PHP thread: the audio thread hands each request over and waits, and a request your script doesn't pick up in time plays silence instead of blocking. Every input that would trip one of sokol's assertions is refused before sokol sees it.

### Basic usage

Most ways you will interface with ext-sokol-audio are in two parts -

Set it up. `saudio_setup()` takes a `saudio_desc`; zero fields mean sokol's defaults (44100 Hz, mono, 2048-frame buffer). Give it a logger, because sokol reports failures only through the logger:

```php
saudio_setup(new saudio_desc(
    num_channels: 1,
    logger: new saudio_logger(fn ($tag, $level, $item, $message) => fprintf(STDERR, "%s\n", $message)),
));
printf("%d Hz, %d channel(s), valid: %s\n", saudio_sample_rate(), saudio_channels(), saudio_isvalid() ? 'yes' : 'no');
```

Feed it. In the push model, `saudio_expect()` says how many frames fit and `saudio_push()` takes them as a string of packed floats. Shut down when you're done:

```php
$rate = saudio_sample_rate();
$phase = 0.0;
$until = microtime(true) + 1.0;                               // one second of A4
while (microtime(true) < $until) {
    $frames = saudio_expect();                                // room left in the packet queue
    if ($frames > 0) {
        $samples = [];
        for ($i = 0; $i < $frames; $i++) {
            $samples[] = 0.2 * sin($phase);
            $phase += 2 * M_PI * 440.0 / $rate;
        }
        saudio_push(pack('f*', ...$samples), $frames);
    }
    usleep(5000);
}

saudio_shutdown();
```

```console
$ php tone.php
44100 Hz, 1 channel(s), valid: yes
```

Or let sokol ask. In the callback model you fill `$buffer` with exactly `num_frames * num_channels` floats whenever the device needs them:

```php
$phase = 0.0;
saudio_setup(new saudio_desc(
    num_channels: 2,
    stream_cb: function (string &$buffer, int $num_frames, int $num_channels) use (&$phase): void {
        $samples = [];
        for ($i = 0; $i < $num_frames; $i++) {
            $s = 0.2 * sin($phase);
            $phase += 2 * M_PI * 440.0 / 44100;
            $samples[] = $s;                                  // left
            $samples[] = $s;                                  // right
        }
        $buffer = pack('f*', ...$samples);                   // exactly num_frames * num_channels floats
    },
));

$until = microtime(true) + 1.0;
while (microtime(true) < $until) {
    usleep(1000);                                             // each pass is a point where the callback can run
}
saudio_shutdown();
```

### Requirements

| | |
|---|---|
| OS | Linux or macOS. `composer.json` lists those two families. |
| PHP | 8.4 or newer, NTS or ZTS. |
| Libraries | sokol_audio.h ships inside the extension, from floooh/sokol commit `93aa187b5d387cc24b7290b3ca3f13f61e139e7c` (sokol has no release tags), copied unchanged into `lib/sokol/` and compiled into the module. macOS links the system AudioToolbox framework. Linux links `libpulse-simple` and `libpulse`; a PulseAudio server, or PipeWire's pulse server, plays the sound. |

To build it you need a C compiler, the development files of the PHP you intend to load it into, and on Linux the PulseAudio headers:

```bash
# Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential php8.4-dev libpulse-dev

# macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
brew install php@8.4
```

### Installation

### With PHP PIE (recommended)

[PIE](https://github.com/php/pie) is the PHP Foundation's installer for extensions. It downloads the tagged source from Packagist, builds it against the PHP on your `PATH`, installs the module and enables it. `sudo` where your PHP's extension directory is root-owned, as on Debian; not on a Homebrew Mac:

```bash
pie install php-io-extensions/sokol-audio
```

### Manually (install script)

The repository ships two installers, one per platform. Each one builds for each PHP it targets, installs `sokol_audio.so` into that PHP's `extension_dir`, writes `30-sokol_audio.ini` into its `conf.d` scan directory, and checks the module loads. The macOS one builds in a temporary copy, ad-hoc signs the module so the system loads it on first use, and keeps an ini that already loads sokol_audio instead of writing its own; the Debian one installs `libpulse-dev` if it is missing, builds in the checkout, writes the ini into every `conf.d` of that PHP (CLI, FPM), and cleans the build products out afterwards.

```bash
git clone https://github.com/php-io-extensions/sokol-audio.git
cd sokol-audio

./install-debian-trixie.sh             # Debian Trixie, Ubuntu 24.04+, Raspberry Pi OS: the php on PATH
./install-macos.sh                     # Homebrew php@8.4 and php@8.4-zts
./install-macos.sh /path/to/bin/php    # either script takes specific PHP binaries
```

### Manually (phpize)

```bash
git clone https://github.com/php-io-extensions/sokol-audio.git
cd sokol-audio
phpize
./configure --enable-sokol-audio
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
```

Then enable it: add `extension=sokol_audio.so` to your `php.ini`, or drop that line into a file in the scan directory that `php --ini` reports.

### Verify

```console
$ php --ri sokol_audio

sokol_audio

sokol_audio support => enabled
Version => 0.11.1
sokol commit => 93aa187b5d387cc24b7290b3ca3f13f61e139e7c
Backend => CoreAudio
```

### API

Function, struct and constant names are the C names, so the documentation block at the top of [`sokol_audio.h`](https://github.com/php-io-extensions/sokol-audio/blob/HEAD/lib/sokol/sokol_audio.h) is the reference: 11 functions, 5 struct classes, 37 constants, declared with their PHP types in [`stubs/sokol_audio.stub.php`](https://github.com/php-io-extensions/sokol-audio/blob/HEAD/stubs/sokol_audio.stub.php).

| | |
|---|---|
| Functions | `saudio_setup`, `saudio_shutdown`, `saudio_isvalid`, `saudio_userdata`, `saudio_query_desc`, `saudio_sample_rate`, `saudio_buffer_frames`, `saudio_channels`, `saudio_suspended`, `saudio_expect`, `saudio_push` |
| Structs | `saudio_desc`, `saudio_logger`, `saudio_allocator`, `saudio_win32_desc`, `saudio_n3ds_desc` |
| Constants | `SAUDIO_LOGITEM_*` (34, the `saudio_log_item` enum), `SAUDIO_N3DS_DSP_INTERP_*` (3) |

### Translations

The only differences from C:

- A struct is a `final` class of the same name with one typed property per field, in field order; the constructor takes every field, zero by default, with nested structs fresh. `clone` copies nested structs.
- `float*` sample buffers are strings of packed 32-bit floats (`pack('f*', ...)`, `unpack('f*', ...)`). `saudio_push(string $frames, int $num_frames)` reads the first `num_frames` frames; a shorter string is a `ValueError`.
- `void* user_data` is `mixed`, handed back unchanged by `saudio_userdata()`, `saudio_query_desc()` and the callbacks.
- Function pointer fields are `?Closure`:

| C | PHP closure |
|---|---|
| `stream_cb` | `fn(string &$buffer, int $num_frames, int $num_channels): void` |
| `stream_userdata_cb` | `fn(string &$buffer, int $num_frames, int $num_channels, mixed $user_data): void` |
| `saudio_logger.func` | `fn(string $tag, int $log_level, int $log_item_id, ?string $message_or_null, int $line_nr, ?string $filename_or_null, mixed $user_data): void` |

- `saudio_allocator`'s functions must be `null`: PHP has no memory to hand sokol-audio, which keeps `malloc` and `free`. The class exists so `saudio_desc` stays 1:1; its `user_data` round-trips through `saudio_query_desc()`.
- `win32` and `n3ds` are bound as data. On Linux and macOS sokol ignores them, as it does in C.

### Callbacks and threads

sokol-audio is one per process. The PHP thread that calls `saudio_setup()` owns it until `saudio_shutdown()` or the end of the request.

The stream callback runs on sokol's audio thread in C, and that thread never enters PHP. It hands the request to the owning thread and waits; the owning thread runs your closure at its next VM interrupt point (any loop iteration or function call), then the audio thread gets the filled buffer. A request your script hasn't started within one buffer's duration (`num_frames / sample rate`, 46 ms at the defaults) is withdrawn and that buffer plays silence. So a script that keeps running PHP code, even `while (true) { usleep(1000); }`, plays continuously; a script inside `sleep(5)` or a long blocking C call plays silence until it comes back.

Log calls from setup run your logger directly. The few sokol logs from the audio thread (`PULSEAUDIO_SIMPLE_WRITE_FAILED` when the server goes away) are queued and delivered at the next interrupt point or by `saudio_shutdown()`; any still queued at request end are dropped.

### Errors

- A stateful call before `saudio_setup()`, a second `saudio_setup()` without `saudio_shutdown()`, or a call from another PHP thread on ZTS is an `Error`. So is `saudio_setup()` or `saudio_shutdown()` from inside a sokol callback.
- Inputs sokol would assert on or overflow are a `ValueError` before sokol sees them: negative sizes, more than 1023 packets (`SAUDIO_RING_MAX_SLOTS - 1`), byte counts past `INT_MAX`, `saudio_push()` with `num_frames < 1` or a short string, allocator functions.
- sokol's own `SOKOL_ASSERT`s stay on in every build and never abort the process: a failure becomes `saudio_assertion_error` naming the condition, file and line when the call returns.
- An exception thrown by a callback, or a `$buffer` left the wrong type or size (`TypeError`, `ValueError`), surfaces at the interrupt point where the callback ran; that buffer plays silence.
- A failing audio backend is not an exception: `saudio_isvalid()` is `false`, the logger says why, and the other calls return sokol's zero values, as in C.
- After `fork()`, the child has no audio thread: every stateful call there is an `Error`. A child of a process that never set sokol-audio up can set it up itself.

### Extensions you might use with this one

* [ext-miniaudio](https://github.com/php-io-extensions/miniaudio): decoding, mixing, effects and a node graph, for when a stream of floats is not enough.
* [ext-epoll](https://github.com/php-io-extensions/epoll) and [ext-kqueue](https://github.com/php-io-extensions/kqueue): a frame loop that waits on input and a timer, and keeps reaching interrupt points so the stream callback runs.

### AI-assisted development

This codebase was built with LLM assistance under human direction. Prompts, reviews, and architectural decisions were owned by a professional software engineer — the model accelerates drafting and exploration; it does not replace judgment on APIs, dependency direction, or what ships.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records what the README doesn't: the full list of bindings and translations, every guard and the sokol assertion it stands in front of, how the callback queue hands a buffer between the audio thread and PHP, what `fork()` and request end do, and a log of every change that altered behaviour.

Start at [`.okf/index.md`](/docs/{{version}}/ecosystem/standalone-extensions/sokol-audio/overview). [`AGENTS.md`](https://github.com/php-io-extensions/sokol-audio/blob/HEAD/AGENTS.md) is the short rule sheet an agent reads before touching the C, the stub, the vendored header, or packaging.

### Resources

* [sokol_audio.h](https://github.com/floooh/sokol/blob/master/sokol_audio.h): the header's own documentation is the manual for every call this extension binds.
* [floooh/sokol at `93aa187`](https://github.com/floooh/sokol/tree/93aa187b5d387cc24b7290b3ca3f13f61e139e7c): the commit vendored in [`lib/sokol/`](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/lib/sokol), unchanged.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`stubs/`](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/stubs) holds the API declaration; `sokol_audio_arginfo.h` is generated from it.
* [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): the spec the [`.okf/`](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/.okf) bundle follows.

### Running the test suite

The suite is Pest v4: the struct classes and constants, every guard, the push model, the stream callbacks served from a PHP loop (silence on a missed deadline, exceptions and bad buffers rethrown), the logger, and a lifecycle test that spawns child PHP processes to check request end and `fork()`. Tests that need an output device skip where `saudio_isvalid()` is false; on a headless Linux box, start PipeWire's pulse server with a null sink (see [`.github/workflows/ci.yml`](https://github.com/php-io-extensions/sokol-audio/blob/HEAD/.github/workflows/ci.yml); PulseAudio's own null sink renders 2-second blocks for sokol's stream and the callback tests fail). The tests write silence; nothing is audible. Build the module, then enable it through an ini scan directory rather than `-d`, so the child processes load it too:

```bash
git clone https://github.com/php-io-extensions/sokol-audio.git
cd sokol-audio
phpize && ./configure --enable-sokol-audio && make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
composer install
mkdir -p /tmp/sokol-audio-ini && echo "extension=$PWD/modules/sokol_audio.so" > /tmp/sokol-audio-ini/sokol_audio.ini
PHP_INI_SCAN_DIR=":/tmp/sokol-audio-ini" php -d memory_limit=128M vendor/bin/pest
```

```console
Tests:    1 skipped, 51 passed (266 assertions)
```

The skipped test drops the client's pulse connection to make the audio thread log: it kills `pipewire-pulse` (systemd's socket activation restarts it), or PulseAudio. It runs only on Linux with `SAUDIO_TEST_KILL_PULSE=1` (`--filter 'audio thread log'`), as CI's last step. The leading `:` keeps your PHP's own scan directory and adds the second one. If that PHP already loads an installed `sokol_audio.so`, the suite tests the installed one instead; point `PHP_INI_SCAN_DIR` at a copy of the scan directory with its sokol_audio ini replaced. A module only loads in the PHP whose `phpize` built it: for Homebrew's ZTS build, run `phpize` and pass `--with-php-config` from `/opt/homebrew/opt/php@8.4-zts/bin`.

### Contributing

Open an issue first for anything beyond a typo. Pull requests change the stub and the C under `src/` together, regenerate `sokol_audio_arginfo.h` with gen_stub, and add a Pest test for the behaviour. `lib/sokol/` is upstream and is never edited: a newer sokol_audio.h lands only by replacing it from a later upstream commit. CI must be green on every cell of the matrix, NTS and ZTS alike. Read [`AGENTS.md`](https://github.com/php-io-extensions/sokol-audio/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

ext-sokol-audio runs sokol's C code and an audio thread inside the PHP process. See [SECURITY.md](https://github.com/php-io-extensions/sokol-audio/blob/HEAD/SECURITY.md) for what it guards against and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/LICENSE). sokol is zlib/libpng, Copyright (c) 2018 Andre Weissflog: [`lib/sokol/LICENSE`](https://github.com/php-io-extensions/sokol-audio/tree/HEAD/lib/sokol/LICENSE).
