# Changelog

What changed in this package, newest first.

### 2026-11-11

* **0.11.1**: `CoverageTest` reads the committed stubs instead of `tools/api.json`, so the suite passes on a tree without `tools/` (the published 0.11.0 tree failed CI on it). Suite 62 passed (369 assertions).
* **Pi 5**: `install-debian-trixie.sh` built and installed in 40 s on PHP 8.4.27 ZTS (aarch64); suite 62 passed (362 assertions), 3.0 s. Real hardware: a PHP data callback fed a 440 Hz tone to PulseAudio's HDMI device for 1 s (49,500 frames).

* Bundle created with ext-miniaudio 0.11.0: miniaudio 0.11.26 vendored with stb_vorbis; 924 functions (891 generated, 33 hand-written), 193 classes, 4 interfaces, 391 constants. Callback queue and every custom backend family bound. Suite 62 tests / 362 assertions green on macOS php84 NTS and ZTS. [bindings](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/api/bindings), [generator](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/architecture/generator), [handles](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/architecture/handles-and-ownership), [callbacks](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/architecture/callbacks), [build](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/runbooks/build-install-test).
* Upstream defect reproduced 1:1: `ma_audio_buffer_alloc_and_init` copies the data, then `ma_audio_buffer_init_ex` zeroes the struct including the padding over the first bytes of that data.
