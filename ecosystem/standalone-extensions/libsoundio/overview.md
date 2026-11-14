# Overview

![CI](https://github.com/php-io-extensions/libsoundio/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/libsoundio/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/libsoundio/actions/workflows/ci.yml)
[![libsoundio API](https://img.shields.io/badge/libsoundio_API-100.0%25_%2872%2F72%29-blue?style=flat-square)](https://github.com/php-io-extensions/libsoundio/blob/HEAD/SUPPORT.md)

1:1 PHP bindings of libsoundio 2.0: the context and its backends, events, devices, channel layouts, formats, output and input streams, and the ring buffer. Version 0.11.0. Linux and macOS.

Function and constant names are the C names. A handle is one PHP object per native pointer. Dropping the last PHP reference does not destroy the native object.

## Requirements

- libsoundio 2.0 or newer
- PHP 8.4, NTS or ZTS
- macOS: `brew install libsoundio`
- Debian trixie and Raspberry Pi OS: `apt install libsoundio-dev`
- `venusian build` reads the system packages from `extra.venusian.system` in composer.json: the run-time apt package a `.deb` depends on, and the Homebrew one.

libsoundio ships no pkg-config file; `config.m4` finds `include/soundio/soundio.h` under the usual prefixes, or under `--with-libsoundio=DIR`.

## Install

Through PIE:

```bash
pie install php-io-extensions/libsoundio
```

From a checkout:

```bash
./install-macos.sh              # Homebrew php@8.4 and php@8.4-zts
./install-debian-trixie.sh      # Debian trixie / Raspberry Pi OS
```

The macOS installer ad-hoc signs the `.so` and writes `30-libsoundio.ini`, unless an ini in that PHP's scan directory already loads `libsoundio`. Pass other PHP binaries as arguments to install those instead.

## Names

Bindings are the C API with these translations:

- `struct SoundIo *`, `SoundIoDevice *`, `SoundIoOutStream *`, `SoundIoInStream *` and `SoundIoRingBuffer *` are handles of those class names; `NULL` is `null`.
- A handle's C struct fields are its properties, read and written live on the native struct. Fields libsoundio fills are `readonly`.
- `SoundIoChannelLayout`, `SoundIoSampleRateRange` and `SoundIoChannelArea` are copied value objects: `new SoundIoChannelLayout()` is C's `{0}`, then set its fields.
- An out-parameter is a by-reference parameter (`soundio_outstream_get_latency($stream, $latency)`; `soundio_outstream_begin_write($stream, $areas, $frame_count)`).
- A list libsoundio takes with a count is a PHP list, and the count stays its own parameter (`soundio_sort_channel_layouts($layouts, $count)`).
- A `char *` libsoundio returns as a buffer address (`soundio_ring_buffer_write_ptr`, `_read_ptr`), a channel area's `ptr`, and `userdata` are `int` addresses.
- `pointer()` is the address, 0 once released; `fromPointer(0)` is `null`.

Failure is the C `int` error code, as in C; `soundio_strerror()` names it. Constants are PHP constants under their C names, with the values of the libsoundio header.

## Callbacks

libsoundio calls most of its callbacks on its own threads. PHP may only run on the thread that owns the request, so those fields are native function addresses, `int`, 0 for NULL:

| Field | Called on | In PHP |
|---|---|---|
| `SoundIo.on_devices_change`, `SoundIo.on_backend_disconnect` | inside `soundio_flush_events()` / `soundio_wait_events()` | `Closure` or `null` |
| `SoundIo.on_events_signal` | any libsoundio thread | address |
| `SoundIo.emit_rtprio_warning` | inside `soundio_flush_events()`, but without a context argument | address |
| `SoundIo.jack_info_callback`, `SoundIo.jack_error_callback` | JACK's threads | address |
| `SoundIoOutStream.write_callback`, `.underflow_callback`, `.error_callback` | the realtime audio thread | address |
| `SoundIoInStream.read_callback`, `.overflow_callback`, `.error_callback` | the realtime audio thread | address |

So ext-libsoundio on its own opens contexts, enumerates devices, and creates, opens and starts streams, and moves bytes through the ring buffer, but plays and records nothing: the audio thread's `write_callback` / `read_callback` has to be native code whose address another extension supplies. libsoundio's own design bridges them with a `SoundIoRingBuffer`, which is bound 1:1.

`on_devices_change` and `on_backend_disconnect` are called as `fn(SoundIo $soundio): void` and `fn(SoundIo $soundio, int $err): void`. They run only inside `soundio_flush_events()` / `soundio_wait_events()` on the PHP thread; one fired anywhere else never enters PHP.

## Refusals

The extension refuses a call only where libsoundio would crash the process (`ValueError`):

- a released handle, except where libsoundio takes `NULL` (`soundio_device_unref`, `soundio_outstream_destroy`, `soundio_instream_destroy`, `soundio_ring_buffer_destroy`);
- `soundio_outstream_start` with `write_callback` 0, and `soundio_instream_start` with `read_callback` 0: the audio thread would call NULL;
- a count past its list (`soundio_sort_channel_layouts`, `soundio_best_matching_channel_layout`);
- `soundio_channel_layout_get_builtin` with an index outside `0 … soundio_channel_layout_builtin_count() - 1`;
- `soundio_outstream_set_volume` on a backend other than CoreAudio or WASAPI: libsoundio 2.0 calls the backend's missing `set_volume` through NULL.

`tests/Probes` shows each crash on a probe build (`LIBSOUNDIO_CONFIGURE="--enable-libsoundio-probes" ./install-macos.sh`).

## Example

```php
$soundio = soundio_create();
soundio_connect_backend($soundio, SoundIoBackendDummy);
soundio_flush_events($soundio);

$device = soundio_get_output_device($soundio, soundio_default_output_device_index($soundio));
echo $device->name, ' ', soundio_format_string($device->current_format), "\n";

$stream = soundio_outstream_create($device);
$stream->format = SoundIoFormatFloat32NE;
$stream->write_callback = $nativeWriteCallback;   // an address from native code
soundio_outstream_open($stream);
soundio_outstream_start($stream);

soundio_outstream_destroy($stream);
soundio_device_unref($device);
soundio_destroy($soundio);
```

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/libsoundio/blob/HEAD/SUPPORT.md) lists every function libsoundio 2.0.0, the floor this extension builds against, declares in `soundio.h`, each marked bound or not; the API badge is computed from it. Regenerate both after a binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

## Tests

```bash
composer install
php -d memory_limit=128M vendor/bin/pest
```

The suite runs on libsoundio's dummy backend: no audio hardware, no sound.

## License

MIT. See [LICENSE](https://github.com/php-io-extensions/libsoundio/blob/HEAD/LICENSE).
