# Changelog

What changed in this package, newest first.

### 2026-11-12

* **0.11.0**: SoLoud master `e82fd32` vendored unchanged and bound at its C++ API: 789 / 789 public members (75 classes, their constructors, methods and fields, the `FFT`, `Misc` and `Thread` functions). Stubs and binding C++ generated from clang's AST of SoLoud's headers.
* PHP can extend `AudioSource`, `AudioSourceInstance`, `Filter`, `FilterInstance`, `FFTFilterInstance`, `AudioCollider`, `AudioAttenuator`, `File` and `Thread\PoolTask`; SoLoud's threads hand each call to the owner PHP thread.
* Suite 150 passed (554 assertions) on macOS php 8.4 NTS and ZTS and on a Pi 5 (Debian trixie, PHP 8.4 ZTS, aarch64).
* SoLoud's miniaudio 0.10 never opened Core Audio on current macOS (it dlopens a relative framework path); built with `MA_NO_RUNTIME_LINKING` and the audio frameworks linked on Darwin.
* `SOLOUD_NO_ASSERTS` (upstream's switch): with asserts on, a Freeverb on a mono source aborts the process during normal playback.
