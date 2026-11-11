# Changelog

What changed in this package, newest first.

### 2026-11-11

* **Green: Mac NTS and ZTS, Pi NTS and ZTS.** Normal builds 63 passed, 9 probes skipped; probe builds 72 / 72 on the Mac, 71 + the macOS-only `best_matching` case skipped on the Pi. Debian's libsoundio keeps `assert()`: the `libsoundio-builtin-index` off-run aborts (SIGABRT) there instead of over-reading, so that probe accepts SIGABRT. Copy to the Pi with `COPYFILE_DISABLE=1`, or macOS tar ships `._*` files that break gen_stub.
* **ext-libsoundio 0.11.0: 72 / 72.** Guarded build against the system libsoundio (Homebrew 2.0.1, Debian `libsoundio-dev` 2.0.0); `config.m4` finds the header by path, no pkg-config file ships. Handles with live field properties, three value classes, every enumerator as a constant.
* **Callbacks.** `on_devices_change` and `on_backend_disconnect` are `?Closure`, entered only inside `soundio_flush_events` / `soundio_wait_events`. The audio-thread, JACK and signal callbacks and `emit_rtprio_warning` are `int` addresses; no native pump is written (it would be opinion). Alone, the extension plays nothing.
* **Refusals kept, each probe-proven:** `libsoundio-released-handle`, `libsoundio-null-write-callback`, `libsoundio-null-read-callback`, `libsoundio-list-count`, `libsoundio-builtin-index`, `libsoundio-set-volume-unsupported` (libsoundio 2.0 calls a NULL `set_volume` on every backend but CoreAudio and WASAPI; the dummy backend segfaults). Dropped, no crash: `libsoundio-string-length` (lengths compared before reading), `libsoundio-channel-count` (the over-read stops inside the call's own frame). The `best_matching` list-count probe faults only under macOS's guard-page allocator; skipped on Linux.
* **Facts.** A device from `soundio_get_*_device` has `ref_count` 2 (libsoundio's own reference). `begin_write` on an opened, unstarted stream returns `SoundIoErrorInvalid` without crashing.
