# Changelog

What changed in this package, newest first.

### 2026-11-06 (1:1 pass)

* **API**: under ext-guard's audit (0 findings). `NSError**` is `?NSError &$error` (ext-appkit's `NSError`), nil is `null`; `MTLCommandBuffer::error()` is `?NSError`. An `NSException` is the PHP `NSException`; `MetalException` moved to jovian/venusian-metal. `drawableSize` is ext-appkit's `NSSize` (metal's `CGSize` is gone); `colorspace` is `?CGColorSpace`. `isBlendingEnabled()` / `isDepthWriteEnabled()`. `getBytes…(int $pixelBytes, …): void`, the string mode moved to jovian. `fromPointer()` is `?static` with no class check. `ZEND_MOD_REQUIRED("appkit")`. NTS and ZTS: 48 passed, 12 probes skipped; probe build: 12 probes pass. `LayerTest` (GUI) not run.

### 2026-11-06

* **Refusals**: a build with every check off showed which calls crash. Kept, each with a probe in `tests/Probes` and a `METAL_PROBE_OFF` site: address 0 as bytes and as the `getBytes` destination, a byte string shorter than the length, and a negative render-encoder binding index (vertex buffer, vertex/fragment bytes, fragment texture, fragment sampler). Dropped: every other non-negative check and `setColorspace(0)`. `--enable-metal-probes` builds the switch. Probe build on PHP 8.4 NTS: 12 probes pass. Release build, NTS and ZTS: 41 passed, 12 skipped across Probes, Resource, Command, Device, Pipeline and Types. `LayerTest` (GUI) not run.

### 2026-10-28

* **Version**: 0.11.0 in `PHP_METAL_VERSION` (`php_metal.h`); `branch-alias` `dev-main` is `0.11.x-dev`. Promoted with the Venusian 0.11 ecosystem. No API or behaviour change. Built and loaded on Homebrew PHP 8.4 NTS and ZTS: 49 passed on each.
* **Coverage**: `scripts/support.php` writes `SUPPORT.md` and the README's API badge from clang's AST dump of the macOS SDK (15.4, the floor): Metal.framework's classes, categories and protocols, QuartzCore's CAMetalLayer, CAMetalDrawable, CAEDRMetadata and CAMetalDisplayLink, and Metal's MTL C functions, not deprecated or unavailable on macOS. `--check` exits 1 when the list or badge is stale. 189 / 1738 (10.9%).

### 2026-10-08

Staged-window presentation and HDR: drawable timeout, transaction presents, EDR, colorspace, `CAEDRMetadata`, drawable `presentedTime` / `drawableID`, timed and paced presents. Suite 49 on Homebrew PHP 8.4 NTS and ZTS.

### 2026-10-04

Created the bundle for 0.10.0. The extension binds Metal and CAMetalLayer 1:1. The suite is 46 tests, 455 assertions, green on Homebrew PHP 8.4 NTS and ZTS. On this M1 a private buffer's `contents` pointer is not nil, and the gate's hypotenuse resolves along the main diagonal at two of four samples.
