# Changelog

What changed in this package, newest first.

### 2026-11-11 (0.11.1)

* **Version** 0.11.1. No binding change.
* **CI**: Ubuntu cells run PipeWire's pulse server with a null sink instead of PulseAudio's. 0.11.0's Ubuntu cells failed two `StreamTest` cases: sokol's stream requests no latency, PulseAudio's null sink rendered 2 s blocks, one callback per 2 s. Reproduced and fixed in `ubuntu:24.04` under Docker: 51 passed, 1 skipped, then the audio-thread log test passed.
* **LoggerTest**: the audio-thread log test kills every `pipewire-pulse` (else PulseAudio). A first cut ran `systemctl --user restart pipewire-pulse.service` first: GitHub's runner has a systemd user session and the package's user units, so that started a second server and sokol's connection stayed up (CI run 43094140349). Socket activation restarts the server on the Pi.

### 2026-11-11

* **StreamTest**: the exception and bad-buffer tests set up inside the expectation. PulseAudio requests the first buffer as soon as `saudio_setup()` returns (CoreAudio waits out two primed buffers), so the callback could be served, and throw, before the old `expect(fn () => spin)`. **LoggerTest**: the audio-thread log test restarts `pipewire-pulse` where `pulseaudio` is absent.

* Bundle created with ext-sokol-audio 0.11.0: sokol_audio.h vendored at floooh/sokol `93aa187b5d387cc24b7290b3ca3f13f61e139e7c`; 11 functions, 5 struct classes + `saudio_assertion_error`, 37 constants. Stream callback and logger served on the owner thread through the VM interrupt queue, silence after one buffer's duration. Suite 51 passed, 1 skipped (Linux-only PulseAudio kill test) on Homebrew PHP 8.4 NTS and ZTS. Pi 5 (Debian trixie, PHP 8.4.27 ZTS, PipeWire pulse server, HDMI speaker): installer builds clean, 51 passed + the audio-thread log test, 3 runs; README tone examples audible. [bindings](/docs/{{version}}/ecosystem/standalone-extensions/sokol-audio/api/bindings), [guards](/docs/{{version}}/ecosystem/standalone-extensions/sokol-audio/architecture/guards-and-errors), [callbacks](/docs/{{version}}/ecosystem/standalone-extensions/sokol-audio/architecture/callbacks-and-threads), [build](/docs/{{version}}/ecosystem/standalone-extensions/sokol-audio/runbooks/build-install-test).
