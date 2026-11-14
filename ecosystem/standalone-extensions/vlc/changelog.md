# Changelog

What changed in this package, newest first.

### 2026-11-12

* **0.11.0**: libvlc 3.0.24 bound at its C API: 277 / 282 functions (`deprecated.h` excluded). Not bound: `libvlc_vprinterr` (a `va_list`; `libvlc_printerr` covers it) and four functions the 3.0.24 library declares but does not export. The 190 plain-shaped functions are generated from the headers by `tools/generate.php`.
* libvlc's callbacks are PHP callables: events, log, exit handler, media input, audio output, volume, audio and video formats, video memory, dialogs. libvlc's threads hand each call to the PHP thread that set it.
* Every callable is freed when libvlc can no longer call it (callback media on `libvlc_MediaFreed`, event callables with their object, a player's callables when libvlc destroys the player). `leaks --atExit` on a create/release stress script reports 0 leaks.
* Five refusals, each probe-proven: `libvlc_clearerr()` and `libvlc_printerr()` before the first `libvlc_new()`, a released handle, a count past its list, `libvlc_media_discoverer_stop()` on a discoverer that is not running.
* Suite 96 passed on macOS php 8.4 NTS and ZTS (VLC.app 3.0.24), 95 passed on a Pi 5 (Debian trixie, PHP 8.4 ZTS, `libvlc-dev` 3.0.24, aarch64, no ext-ffi). A tone played through the Pi's HDMI audio to `libvlc_MediaPlayerEndReached`.
