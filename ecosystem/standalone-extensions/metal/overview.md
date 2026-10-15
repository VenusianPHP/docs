# Overview

![CI](https://github.com/php-io-extensions/metal/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/metal/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/metal/actions/workflows/ci.yml)

1:1 PHP bindings of Metal, `CAMetalLayer` and `CAEDRMetadata`, as classes named after their native counterparts. Version 0.10.0. macOS only.

A handle is one PHP object per native object, retained while PHP holds it. `NSError` and `NSException` become `MetalException`.

## Requirements

- macOS with Metal
- PHP 8.4, NTS or ZTS

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
- A descriptor's `[[X alloc] init]` is `X::new()`. A class factory keeps the selector name (`MTLVertexDescriptor::vertexDescriptor()`, `CAMetalLayer::layer()`). Properties are `name()` / `setName()`. `isBlendingEnabled` is `blendingEnabled()`.
- `pointer(): int` and `static fromPointer(int $pointer): static` hand an object to another extension. `fromPointer(0)` throws `MetalException`. An address that is not the called class throws too. Any other address is trusted to hold an object.
- An `NSError**` is not a PHP argument. A nil result throws `MetalException` with the error's `localizedDescription` and `code`. The method name still ends in `Error`.
- A `string|int` byte argument is a PHP string or an address. `0` is refused. Any other address is trusted. A string shorter than the call's byte count throws `ValueError`.

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

$pixel = $texture->getBytesBytesPerRowFromRegionMipmapLevel(
    null, 4, new MTLRegion(new MTLOrigin(1, 1, 0), new MTLSize(1, 1, 1)), 0
);
// $pixel is "\x00\xff\x00\xff"
```

## Testing

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest
zhp -d memory_limit=128M vendor/bin/pest
```

`php84` is Homebrew `php@8.4`. `zhp` is `php@8.4-zts`. Both must be green.
