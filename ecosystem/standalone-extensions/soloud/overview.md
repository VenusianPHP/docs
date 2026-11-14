# Overview

![CI](https://github.com/php-io-extensions/soloud/actions/workflows/ci.yml) ![Packagist](https://packagist.org/packages/php-io-extensions/soloud)…

<div align="center" id="header">

<h2>ext-soloud</h2>

<h4>SoLoud's C++ API bound 1:1 into PHP 8.4+, with the library compiled in</h4>

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/soloud/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/soloud/actions/workflows/ci.yml)
[![SoLoud API](https://img.shields.io/badge/SoLoud_API-100.0%25_%28789%2F789%29-blue?style=flat-square)](https://github.com/php-io-extensions/soloud/blob/HEAD/SUPPORT.md)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/soloud?style=flat-square)](https://packagist.org/packages/php-io-extensions/soloud)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/soloud/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/soloud)
[![License](https://img.shields.io/github/license/php-io-extensions/soloud?style=flat-square)](https://github.com/php-io-extensions/soloud/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://solhsa.com/soloud/)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/soloud/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

A game needs more than "play this file": dozens of voices at once, buses to group them, echo and reverb, 3D positions around a listener, a speech synth or a retro sound generator, and a mixer that keeps all of it in time. In PHP that has meant shelling out to a player, which mixes nothing.

<b>SoLoud</b> is that mixer. Jari Komppa's C++ audio engine plays WAV, OGG, FLAC and MP3 from memory or streamed, mixes voices through buses and queues, runs biquad, echo, flanger, freeverb, lofi, robotize and FFT filters per voice or globally, positions sound in 3D with attenuation and doppler, and carries its own generators: Sfxr, Speech, Noise, Monotone, TedSid, Ay, Vizsn.

<b>The only problem?</b> PHP can't reach it. SoLoud is C++, and its flat `soloud_c.h` is a lossy mirror its author generated for other languages: no subclassing, no file I/O classes, no public fields. This extension binds the C++ API itself, one to one: every public class, method, field, enum and free function in SoLoud's headers, with the library compiled into the module from an unchanged copy of upstream. C++ classes are PHP classes, PHP can extend SoLoud's abstract classes, and SoLoud's mixer thread hands every override call to the PHP thread that owns it. No defaults, no composites, no opinions: what SoLoud documents is what you call.

### Basic usage

```php
$engine = new SoLoud\Soloud();
$engine->init(SoLoud\Soloud::CLIP_ROUNDOFF, SoLoud\Soloud::MINIAUDIO);

$wav = new SoLoud\Wav();
$wav->load('blip.wav');
$voice = $engine->play($wav);
$engine->setPan($voice, -0.5);

$echo = new SoLoud\EchoFilter();
$echo->setParams(0.25, 0.5);
$wav->setFilter(0, $echo);
```

A PHP source:

```php
final class Tone extends SoLoud\AudioSource
{
    public function __construct()
    {
        parent::__construct();
        $this->mChannels = 1;
        $this->mBaseSamplerate = 44100.0;
    }

    public function createInstance(): ?SoLoud\AudioSourceInstance
    {
        return new ToneInstance();
    }
}

final class ToneInstance extends SoLoud\AudioSourceInstance
{
    private int $t = 0;

    public function getAudio(?string &$aBuffer, int $aSamplesToRead, int $aBufferSize): int
    {
        $s = [];
        for ($i = 0; $i < $aBufferSize; $i++) {
            $s[] = 0.2 * sin(2 * M_PI * 440 * $this->t++ / 44100);
        }
        $aBuffer = pack('g*', ...$s);

        return $aSamplesToRead;
    }

    public function hasEnded(): bool
    {
        return false;
    }
}
```

### Requirements

| | |
|---|---|
| PHP | 8.4 or newer, NTS or ZTS |
| OS | Linux, macOS |
| Build | a C++17 compiler, `phpize` and `php-config` for the PHP you install into |
| Runtime | nothing extra: Core Audio on macOS (linked), ALSA / PulseAudio / JACK on Linux (loaded at runtime when present). The null backend needs no device. |

```bash
# Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential php8.4-dev

# macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
```

### Installation

### With PHP PIE (recommended)

```bash
pie install php-io-extensions/soloud
```

PIE builds the module against the PHP it runs under and enables it.

### Manually (install script)

The repository ships two installers. Each builds for its PHP, installs `soloud.so` into that PHP's `extension_dir`, writes `30-soloud.ini`, and checks the module loads. The macOS one builds in a temporary copy for Homebrew `php@8.4` and `php@8.4-zts` and ad-hoc signs the module; the Debian one builds in the checkout, writes the ini into every `conf.d` of that PHP (CLI, FPM, Apache) and cleans the build products out afterwards. SoLoud compiles with the module, so the build takes a few minutes.

```bash
git clone https://github.com/php-io-extensions/soloud.git
cd soloud
./install-macos.sh            # macOS
./install-debian-trixie.sh    # Debian 13, Raspberry Pi OS
```

### Manually (phpize)

```bash
phpize
./configure --enable-soloud
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
echo "extension=soloud" | sudo tee "$(php -r 'echo PHP_CONFIG_FILE_SCAN_DIR;')/30-soloud.ini"
```

### Verify

```bash
php --ri soloud
```

```console
soloud support => enabled
Extension version => 0.11.0
SoLoud version => 202002
Upstream commit => e82fd32c1f62183922f08c14c814a02b58db1873
```

### API

`SoLoud::X` is `SoLoud\X`, nested scopes are namespaces (`SoLoud\Thread\Pool`), free functions are namespace functions (`SoLoud\FFT\fft()`), and enumerators are `int` constants (`SoLoud\Soloud::NULLDRIVER`, `SoLoud\SO_NO_ERROR`). Result codes are returned, never thrown. See [Bindings](/docs/{{version}}/ecosystem/standalone-extensions/soloud/api/bindings) for every translation and what is not bound.

### Lifetime and errors

PHP deletes what it constructs. Where SoLoud keeps a pointer from one object to another, the holder keeps the held PHP object alive, and every object makes its own deletion safe, so no order of `unset()` or request shutdown crashes the process: [Lifetime](/docs/{{version}}/ecosystem/standalone-extensions/soloud/architecture/lifetime). Calls SoLoud does not check and that would crash (a length past the string, mixing past the engine's scratch, a filter on more channels than its state, a `File` that is not open, a dead thread handle) are refused with a `ValueError`; each refusal has a probe that crashes with the check off: [Errors](/docs/{{version}}/ecosystem/standalone-extensions/soloud/architecture/errors).

### Threads and callbacks

SoLoud's mixer, pool workers and threads from `SoLoud\Thread\createThread()` never enter PHP. A call into a PHP override is queued to the PHP thread that made the object, which runs it at its next VM interrupt. A mixer call not finished within one device buffer plays silence. Run PHP while sound plays: a thread blocked in `usleep()` runs no opcodes and serves nothing. See [Callbacks](/docs/{{version}}/ecosystem/standalone-extensions/soloud/architecture/callbacks).

### Extensions you might use with this one

* [php-io-extensions/box2d](https://github.com/php-io-extensions/box2d): 2D physics, for the collisions your sounds follow.
* [php-io-extensions/miniaudio](https://github.com/php-io-extensions/miniaudio): miniaudio's own API, device and node level. The two load side by side: SoLoud's private miniaudio copy is not exported.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/soloud/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records the binding surface, the lifetime model, the callback queue, every refusal and how to build and test.

### Resources

* [SoLoud documentation](https://solhsa.com/soloud/): the manual for every call this extension binds.
* [jarikomppa/soloud at `e82fd32`](https://github.com/jarikomppa/soloud/tree/e82fd32c1f62183922f08c14c814a02b58db1873): the master commit vendored in [`lib/soloud/`](https://github.com/php-io-extensions/soloud/tree/HEAD/lib/soloud), unchanged. The last tag, `RELEASE_20200207`, is four years older.
* [SUPPORT.md](https://github.com/php-io-extensions/soloud/blob/HEAD/SUPPORT.md): every public member and whether a stub binds it.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`stubs/`](https://github.com/php-io-extensions/soloud/tree/HEAD/stubs) holds the API declarations; each `*_arginfo.h` is generated from its stub.

### Running the test suite

Pest v4: every stub group, every shutdown order with everything live at exit, PHP sources, filters, attenuators, files and pool tasks, and one test that runs SoLoud's real mixer thread at volume 0 (it skips without an output device). Engines otherwise use the null backend; nothing is audible. Enable the module through an ini scan directory so the child processes the shutdown tests spawn load it too:

```bash
git clone https://github.com/php-io-extensions/soloud.git
cd soloud
phpize && ./configure --enable-soloud && make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
composer install
mkdir -p /tmp/soloud-ini && echo "extension=$PWD/modules/soloud.so" > /tmp/soloud-ini/soloud.ini
PHP_INI_SCAN_DIR=":/tmp/soloud-ini" php -d memory_limit=128M vendor/bin/pest
```

```console
Tests:    53 skipped, 150 passed (554 assertions)
```

The skipped tests are probe halves: they run only on a probe build (`./configure --enable-soloud --enable-soloud-probes`, never shipped), where each refusal's check can be switched off to show the crash it prevents.

### Contributing

Open an issue first for anything beyond a typo. The stubs and `src/gen/` are generated: change `tools/bindings.php` or `tools/generate.php`, regenerate, run gen_stub and `scripts/support.php`, and add a Pest test. `lib/soloud/` is upstream and is never edited. Read [`AGENTS.md`](https://github.com/php-io-extensions/soloud/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

ext-soloud runs SoLoud's C++ and its mixer thread inside the PHP process. See [SECURITY.md](https://github.com/php-io-extensions/soloud/blob/HEAD/SECURITY.md) for what it guards against and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/soloud/tree/HEAD/LICENSE). SoLoud is zlib/libpng, Copyright (c) Jari Komppa: [`lib/soloud/LICENSE`](https://github.com/php-io-extensions/soloud/tree/HEAD/lib/soloud/LICENSE).
