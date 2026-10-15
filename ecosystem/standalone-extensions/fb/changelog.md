# Changelog

What changed in this package, newest first.

### 2026-10-13

* Version 0.10.5: `PHP_FB_VERSION` moves from 0.10.0. README rewritten to the php-io-extensions template.
* `FbBuffer::__construct()` and `FbFormat::size()` refuse sides a 32-bit PHP cannot address (`ValueError`), where the byte count used to wrap `size_t`; `blitRgba8()` and `paintRgba8()` check their image length in 64-bit arithmetic. No change on 64-bit. [surface](/docs/{{version}}/ecosystem/standalone-extensions/fb/guide/overview)

### 2026-10-03

* Bundle created with ext-fb 0.10.0, a plain-C rewrite: [surface](/docs/{{version}}/ecosystem/standalone-extensions/fb/guide/overview) (`FbFormat`, `FbBuffer`, 23 constants), [build](/docs/{{version}}/ecosystem/standalone-extensions/fb/runbooks/build-install-test).
* Bulk paths in the pixel core: byte runs for whole-byte layouts and whole rows, byte reorder between 32-bit orders; `tests/BulkTest.php`. [surface](/docs/{{version}}/ecosystem/standalone-extensions/fb/guide/overview)
* `FbBuffer::paintSpans()`: coverage spans blended or thresholded in C, version unchanged; `src/` builds warning-free under `-Wall -Wextra`. [surface](/docs/{{version}}/ecosystem/standalone-extensions/fb/guide/overview)
* `FbBuffer::paintRgba8()`: an RGBA8 image placed through an inverse affine, nearest or smooth, blended; built `-ffp-contract=off`; version unchanged. [surface](/docs/{{version}}/ecosystem/standalone-extensions/fb/guide/overview), [build](/docs/{{version}}/ecosystem/standalone-extensions/fb/runbooks/build-install-test)
* `paintRgba8()` gains `row`: the surface row the buffer's row 0 stands for, so a window onto a taller surface samples exactly as the whole would. [surface](/docs/{{version}}/ecosystem/standalone-extensions/fb/guide/overview)
