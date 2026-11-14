# Overview

![CI](https://github.com/php-io-extensions/metal/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/metal/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/metal/actions/workflows/ci.yml)
[![Metal API](https://img.shields.io/badge/Metal_API-10.9%25_%28189%2F1738%29-blue?style=flat-square)](https://github.com/php-io-extensions/metal/blob/v0.11.1/SUPPORT.md)

1:1 PHP bindings of Metal, `CAMetalLayer` and `CAEDRMetadata`, as classes named after their native counterparts. Version 0.11.1. macOS only.

A handle is one PHP object per native object, retained while PHP holds it. Requires ext-appkit: an `NSError`, a `CGSize` and a `CGColorSpaceRef` are ext-appkit's `NSError`, `NSSize` and `CGColorSpace`. An `NSException` becomes the PHP `NSException`.

## Requirements

- macOS with Metal
- PHP 8.4, NTS or ZTS
- ext-appkit 0.11 (`"ext-appkit": "^0.11.0"` in composer.json; the module requires it at load)

## Install

Through PIE:

```bash
pie install php-io-extensions/metal
```

From a checkout of this repository:

```bash
./install-macos.sh
```

That builds into Homebrew `php@8.4` and `php@8.4-zts`, ad-hoc signs the `.so`, and writes `30-metal.ini`. Pass other PHP binaries as arguments to install those instead.

## Names

- One PHP class per Metal type, one method per selector. Keywords are joined in camelCase: `newLibraryWithSource:options:error:` is `newLibraryWithSourceOptionsError()`.
- Flag parameters take `Enum|int`. Enum cases are the C constant without its type prefix, in upper snake case: `MTLPixelFormatRGBA8Unorm` is `MTLPixelFormat::RGBA8_UNORM`.
- A descriptor's `[[X alloc] init]` is `X::new()`. A class factory keeps the selector name (`MTLVertexDescriptor::vertexDescriptor()`, `CAMetalLayer::layer()`). Properties are `name()` / `setName()`; a renamed getter keeps its name (`isBlendingEnabled()`).
- `pointer(): int` and `static fromPointer(int $pointer): ?static` hand an object to another extension. The address is trusted to hold the called class's object. `0` is `null`.
- An `NSError**` is a by-reference `?NSError &$error` in native position. A nil result is `null`.
- A `string|int` byte argument is a PHP string or an address. `0` is refused. Any other address is trusted. A string shorter than the call's byte count throws `ValueError`. Other integers reach Metal as they are; see [errors](/docs/{{version}}/ecosystem/standalone-extensions/metal/architecture/errors) for the refusals a probe keeps.

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/metal/blob/v0.11.1/SUPPORT.md) lists every method and property accessor that the SDK's Metal headers
declare on a class, category or protocol, QuartzCore's Metal classes (`CAMetalLayer`,
`CAMetalDrawable`, `CAEDRMetadata`, `CAMetalDisplayLink`) and Metal's C functions, not deprecated or
unavailable on macOS, each marked bound or not; the API badge is computed from it. Regenerate both
after a binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

## Example

Clear a 2×2 texture to green and read one pixel back:

```php
$texture = MTLTextureDescriptor::texture2DDescriptorWithPixelFormatWidthHeightMipmapped(
    MTLPixelFormat::RGBA8_UNORM, 2, 2, false
);
$texture->setStorageMode(MTLStorageMode::SHARED);
$texture->setUsage(MTLTextureUsage::RENDER_TARGET);
$texture = MTLCreateSystemDefaultDevice()->newTextureWithDescriptor($texture);

$pass = MTLRenderPassDescriptor::renderPassDescriptor();
$color = $pass->colorAttachments()->objectAtIndexedSubscript(0);
$color->setTexture($texture);
$color->setLoadAction(MTLLoadAction::CLEAR);
$color->setClearColor(new MTLClearColor(0.0, 1.0, 0.0, 1.0));
$color->setStoreAction(MTLStoreAction::STORE);

$commands = MTLCreateSystemDefaultDevice()->newCommandQueue()->commandBuffer();
$commands->renderCommandEncoderWithDescriptor($pass)->endEncoding();
$commands->commit();
$commands->waitUntilCompleted();

$pixel = new FbBuffer(new FbFormat(FB_LAYOUT_RGBA8888, channelOrder: FB_CHANNELS_RGBA), 1, 1); // ext-fb
$texture->getBytesBytesPerRowFromRegionMipmapLevel(
    $pixel->pointer(), 4, new MTLRegion(new MTLOrigin(1, 1, 0), new MTLSize(1, 1, 1)), 0
);
// $pixel->bytes() is "\x00\xff\x00\xff"
```

## Testing

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest
zhp -d memory_limit=128M vendor/bin/pest
```

`php84` is Homebrew `php@8.4`. `zhp` is `php@8.4-zts`. Both must be green.
