# Overview

<div align="center" id="header">

<h2>ext-vlc</h2>

<h4>libvlc 3.0 bound 1:1 into PHP 8.4+</h4>

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/vlc/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/vlc/actions/workflows/ci.yml)
[![libvlc API](https://img.shields.io/badge/libvlc_API-98.2%25_%28277%2F282%29-blue?style=flat-square)](https://github.com/php-io-extensions/vlc/blob/HEAD/SUPPORT.md)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/vlc?style=flat-square)](https://packagist.org/packages/php-io-extensions/vlc)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/vlc/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/vlc)
[![License](https://img.shields.io/github/license/php-io-extensions/vlc?style=flat-square)](https://github.com/php-io-extensions/vlc/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://www.videolan.org/vlc/libvlc.html)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/vlc/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

Playing media means demuxing a container, decoding its streams, keeping audio and video in sync, and reaching an output: a sound card, a window, a stream to the network. Each piece is its own library, and PHP has none of them.

<b>libvlc</b> is VLC's engine as a C library. It opens anything VLC opens (files, network streams, discs, capture devices), plays it through a media player with seeking, tracks, subtitles, an equalizer and video adjustments, runs playlists, discovers renderers and network media, and streams through VLM. With callbacks, it hands you the media bytes, the decoded audio samples or the video pictures instead of its own outputs.

<b>The only problem?</b> PHP can't reach it. This extension binds libvlc 3.0's C API one to one: every function in its headers except `deprecated.h`, with the C names, the C types mapped to PHP and libvlc's callbacks as PHP callables. libvlc calls back on its own threads; the extension hands each call to the PHP thread that set it. No defaults, no wrapper classes: what libvlc documents is what you call.

### Basic usage

```php
putenv('VLC_PLUGIN_PATH=/Applications/VLC.app/Contents/MacOS/plugins'); // macOS only

$vlc = libvlc_new(1, ['--quiet']);
$media = libvlc_media_new_path($vlc, '/path/to/song.mp3');
$mp = libvlc_media_player_new_from_media($media);
libvlc_media_release($media);

$ended = false;
libvlc_event_attach(libvlc_media_player_event_manager($mp), libvlc_MediaPlayerEndReached,
    function (libvlc_event_t $e) use (&$ended): void { $ended = true; });

libvlc_media_player_play($mp);
while (! $ended) {
    usleep(10_000);
}
libvlc_media_player_release($mp);
libvlc_release($vlc);
```

Decoded audio, as PHP strings:

```php
libvlc_audio_set_format($mp, 'S16N', 44100, 2);
libvlc_audio_set_callbacks($mp,
    function (string $samples, int $count, int $pts): void { /* $count frames, 4 bytes each */ },
    null, null, null, null);
```

### Requirements

| | |
|---|---|
| PHP | 8.4 or newer, NTS or ZTS |
| OS | Linux, macOS |
| libvlc | 3.0 (built and tested against 3.0.24) |
| Build | a C compiler, `phpize` and `php-config` for the PHP you install into |

```bash
# Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential php8.4-dev libvlc-dev vlc-plugin-base

# macOS: VLC.app ships libvlc's headers and library; Homebrew's PHP ships phpize and php-config
brew install --cask vlc
xcode-select --install
```

VLC.app ships no pkg-config file. `config.m4` finds `include/vlc/vlc.h` in `/Applications/VLC.app/Contents/MacOS` and the usual prefixes, or under `./configure --with-vlc=DIR`.

### macOS: `VLC_PLUGIN_PATH`

VLC.app's libvlc finds its plugins only through `VLC_PLUGIN_PATH`. Without it, `libvlc_new()` returns `null`. Set it for every process that uses the extension, or with `putenv()` before the first `libvlc_new()`:

```bash
export VLC_PLUGIN_PATH=/Applications/VLC.app/Contents/MacOS/plugins
```

The extension sets no default. Debian's libvlc knows its own plugin directory.

### Installation

### With PHP PIE (recommended)

```bash
pie install php-io-extensions/vlc
```

PIE builds the module against the PHP it runs under and enables it.

### Manually (install script)

The repository ships two installers. Each builds for its PHP, installs `vlc.so` into that PHP's `extension_dir`, writes `30-vlc.ini`, and checks the module loads. The macOS one builds in a temporary copy for Homebrew `php@8.4` and `php@8.4-zts` and ad-hoc signs the module; the Debian one builds in the checkout, enables the module for CLI, FPM and Apache, and cleans the build products out afterwards.

```bash
git clone https://github.com/php-io-extensions/vlc.git
cd vlc
./install-macos.sh            # macOS
./install-debian-trixie.sh    # Debian 13, Raspberry Pi OS
```

### Manually (phpize)

```bash
phpize
./configure --enable-vlc
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
echo "extension=vlc" | sudo tee "$(php -r 'echo PHP_CONFIG_FILE_SCAN_DIR;')/30-vlc.ini"
```

### Verify

```bash
php --ri vlc
```

```console
vlc support => enabled
Version => 0.11.0
libvlc version => 3.0.24 Vetinari
```

### API

Functions and constants keep their C names (`libvlc_media_player_play`, `libvlc_Playing`). Opaque pointers are handles of their C type's class name, one PHP object per native pointer. A list libvlc returns is handles whose properties are the C fields, read live, until you pass it back to its `*_release`. Out-parameters are by-reference; pointer and count pairs are a PHP list and its count, in C order. Dropping the last PHP reference to a handle does not release the native object: call the `*_release`, as in C. See [Bindings](/docs/{{version}}/ecosystem/standalone-extensions/vlc/api/bindings) for every translation and what is not bound.

### Threads and callbacks

libvlc calls back on its input, decoder and output threads. PHP never runs there: each call is handed to the PHP thread that set the callable and runs at that thread's next VM interrupt point (a loop iteration, `usleep()`, a function call). Calls whose result libvlc needs wait up to a deadline and then get libvlc's no-op; events copy their data and let libvlc's thread go before your callable runs; audio and video output calls never make libvlc wait. See [Callbacks](/docs/{{version}}/ecosystem/standalone-extensions/vlc/architecture/callbacks).

### Lifetime and errors

The extension frees a callable when libvlc can no longer call it: callback media when libvlc frees the media, event callables with detach or the last release of their object, a player's callables when libvlc destroys the player: [Lifetime](/docs/{{version}}/ecosystem/standalone-extensions/vlc/architecture/lifetime). libvlc's results and error messages pass through. The extension refuses a call only where libvlc would crash the process, each refusal proven by a probe: [Errors](/docs/{{version}}/ecosystem/standalone-extensions/vlc/architecture/errors).

### Extensions you might use with this one

* [php-io-extensions/fb](https://github.com/php-io-extensions/fb): a Linux framebuffer, for the pictures the video callbacks render.
* [php-io-extensions/miniaudio](https://github.com/php-io-extensions/miniaudio) and [php-io-extensions/soloud](https://github.com/php-io-extensions/soloud): to mix or process the samples the audio callbacks hand you.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/vlc/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records the binding surface, handles and reference counts, the callback queue, record lifetimes, every refusal and how to build and test.

### Resources

* [libvlc API documentation](https://videolan.videolan.me/vlc/group__libvlc.html): the reference for every call this extension binds (the 3.0 headers are the source of record).
* [SUPPORT.md](https://github.com/php-io-extensions/vlc/blob/HEAD/SUPPORT.md): every function in the libvlc 3.0.24 headers and whether a stub binds it.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`stubs/`](https://github.com/php-io-extensions/vlc/tree/HEAD/stubs) holds the API declarations; each `*_arginfo.h` is generated from its stub.

### Running the test suite

Pest v4: every header group, every callback kind, the record lifetimes, and the refusals. Instances use `--aout=dummy --vout=dummy`, so nothing is audible or shown; media are WAV files the tests generate.

```bash
git clone https://github.com/php-io-extensions/vlc.git
cd vlc
./install-macos.sh            # or ./install-debian-trixie.sh
composer install
php -d memory_limit=128M vendor/bin/pest
```

```console
Tests:    5 skipped, 96 passed (415 assertions)
```

The skipped tests are probe halves: they run only on a probe build (`VLC_CONFIGURE=--enable-vlc-probes ./install-macos.sh`, never shipped), where each refusal's check can be switched off to show the crash it prevents. The video callback test also skips without ext-ffi, which it uses to own the pixel buffer.

### Contributing

Open an issue first for anything beyond a typo. The `gen_*` stubs and sources are generated: change `tools/generate.php`, regenerate, run gen_stub and `scripts/support.php`, and add a Pest test. Read [`AGENTS.md`](https://github.com/php-io-extensions/vlc/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

ext-vlc runs libvlc, its plugins and its threads inside the PHP process, and libvlc opens whatever MRL it is given. See [SECURITY.md](https://github.com/php-io-extensions/vlc/blob/HEAD/SECURITY.md) for what it guards against and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/vlc/tree/HEAD/LICENSE). libvlc is LGPL-2.1-or-later, Copyright VideoLAN and the VLC authors, and is not part of this package.
