# Errors

An NSError comes back by reference as ext-appkit's NSError; an NSException becomes the PHP NSException. The kept refusals, each with a probe, are ValueError.

## Overview

An `NSError**` is a by-reference `?NSError &$error` parameter in native position. The error Metal reports goes there as ext-appkit's `NSError` (through `NSObject::fromPointer`), also beside a non-nil result (a compiler warning). A nil result is `null`. `MTLCommandBuffer::error()` is `?NSError`. Throwing on an `NSError` is a caller's choice: jovian/venusian-metal's `MetalException`.[^runtime]

`METAL_BEGIN` / `METAL_END` wrap every binding body in an autorelease pool and a `@try`. An `NSException` becomes the PHP `NSException` (extends `Exception`) with message `"<name>: <reason>"`. A pipeline descriptor without a vertex function is one: Metal raises it, under `METAL_ERROR_MODE=1`, instead of returning an `NSError`.

Metal aborts the process for some descriptor mistakes (`vertexFunction must not be nil`) unless `METAL_ERROR_MODE=1`, which reports them as `NSException`. MINIT sets that variable when the process has not set it.[^module]

## Kept refusals

A refusal is kept only where a probe build shows the native call crash without it. Each site reads `if (!METAL_PROBE_OFF("<id>") && (<check>))` and carries `/* binding:<id> */` on its throw line. A build configured with `--enable-metal-probes` (`METAL_CONFIGURE` in `install-macos.sh`) defines the constant `METAL_PROBES`, and env `METAL_PROBE_OFF=<id>` turns that one site off. `tests/Probes` runs each call in a child PHP with the site on and off. Never ship a probe build.

| Site | Call | Without the check |
|---|---|---|
| `metal-null-address` | `string\|int` bytes given as address `0` (`newBufferWithBytesLengthOptions`, `replaceRegionMipmapLevelWithBytesBytesPerRow`) | SIGSEGV: Metal reads NULL |
| `metal-destination-null-address` | `getBytesBytesPerRowFromRegionMipmapLevel` destination `0` | SIGSEGV: Metal writes NULL |
| `metal-bytes-length` | a `string\|int` byte string shorter than the call's byte count | SIGSEGV under libgmalloc: Metal reads past the string |
| `metal-shader-bytes-length` | `setVertexBytes` / `setFragmentBytes` string shorter than `$length` | SIGSEGV under libgmalloc |
| `metal-vertex-buffer-index` | `setVertexBufferOffsetAtIndex` index below 0 | SIGSEGV: the encoder writes its binding table at NSUIntegerMax |
| `metal-shader-bytes-index` | `setVertexBytes` / `setFragmentBytes` index below 0 | SIGSEGV |
| `metal-fragment-texture-index` | `setFragmentTextureAtIndex` index below 0 | SIGSEGV |
| `metal-fragment-sampler-index` | `setFragmentSamplerStateAtIndex` index below 0 | SIGSEGV |

Any other address is trusted. Every other integer reaches Metal as `(NSUInteger)`, negative ones included: Metal takes the value, or raises an `NSException` (under `METAL_ERROR_MODE=1`) that becomes the PHP `NSException`. A positive index past Metal's limit (1000) does not crash the encoder; only the wrapped negative one does. `setColorspace(0)` is a NULL `CGColorSpaceRef`, which Core Animation takes.

`metal_region_span` sizes the bytes `replaceRegion…` reads from a string. A region height below 0, or a `$bytesPerRow` times height past `SIZE_MAX`, throws `ValueError`: the size would wrap, and the length check would pass a short string. `getBytes…` writes to an address only, trusted to have room.

[^runtime]: metal_throw_nserror and METAL_BEGIN
[^module]: METAL_ERROR_MODE
