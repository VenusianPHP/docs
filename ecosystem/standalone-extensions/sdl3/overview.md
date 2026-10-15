# Overview

![CI](https://github.com/php-io-extensions/sdl3/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/sdl3/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/sdl3/actions/workflows/ci.yml)

1:1 PHP bindings of SDL 3 at the 3.2 API: windows, displays and fullscreen modes, surfaces, the GL, Metal and Vulkan hooks, and SDL_GPU. Version 0.10.0. Linux and macOS.

Function and constant names are the C names. A handle is one PHP object per native pointer. Dropping the last PHP reference does not destroy the native object.

## Requirements

- SDL 3.2 or newer
- PHP 8.4, NTS or ZTS
- macOS: `brew install sdl3`
- Debian trixie and Raspberry Pi OS: `apt install libsdl3-dev`
- `venusian build` reads the system packages from `extra.venusian.system` in composer.json: apt packages to build with and the run-time ones a `.deb` depends on or recommends, and the Homebrew ones.

On a Pi that also has SDL under `/usr/local`, that build has no Wayland device. The distro package is the one with Wayland. `install-debian-trixie.sh` configures against `/usr/lib/$(gcc -dumpmachine)` and puts `/usr/include` ahead of `/usr/local/include`, so the extension links distro SDL 3.2.

## Install

Through PIE:

```bash
pie install php-io-extensions/sdl3
```

From a checkout:

```bash
./install-macos.sh              # Homebrew php@8.4 and php@8.4-zts
./install-debian-trixie.sh      # Debian trixie / Raspberry Pi OS
```

The macOS installer ad-hoc signs the `.so` and writes `30-sdl3.ini`. Pass other PHP binaries as arguments to install those instead.

## Names

Bindings are the C API with four translations:

- A pointer and a count, in a struct or a parameter list, are one PHP list. The count is the length of the list. An empty list passes NULL and a count of 0.
- `const Uint8 *code` and `size_t code_size` are one `string`.
- An out-parameter is a by-reference parameter (`?int &$w`).
- A `void *` is an `int` address. `0` is refused. Any other address is trusted, and the stub says so.
- A struct the caller passes for SDL to fill (`SDL_Rect *rect`, `SDL_DisplayMode *closest`) is an object SDL writes into. A `const SDL_DisplayMode *` SDL returns is a copied `SDL_DisplayMode`, or `null`. A list SDL allocates (`SDL_GetDisplays`, `SDL_GetFullscreenDisplayModes`) is a PHP list, or `null` on failure; the count is its length.

A C `bool` stays `bool`. Failure is `SDL_GetError()`, as in C. Enum and flag fields are `int`. `props` fields are `int`.

Constants are PHP constants under their C names. The values come from the SDL headers.

## Handles

Handle classes are `final`, with a private constructor, and are not cloneable or serializable. Each has `pointer(): int` and `static fromPointer(int $pointer): static`. `fromPointer(0)` throws `ValueError`. The same native pointer in one thread is the same PHP object.

`SDL_Destroy*`, `SDL_Release*`, `SDL_CloseIO`, `SDL_EndGPUCopyPass`, `SDL_EndGPURenderPass`, and submitting or cancelling a command buffer mark that handle released. A swapchain texture is released when the command buffer that acquired it is submitted or cancelled. A window surface from `SDL_GetWindowSurface()` is released by `SDL_DestroyWindowSurface()` or when the window is destroyed. Passing a released handle to any binding throws `ValueError` naming the class (`SDL_Window has been destroyed`). The native object is not freed when the PHP object is. A later SDL object at the same address is a new PHP object.

## Bytes

`SDL_MapGPUTransferBuffer()` returns the mapped address, or `0` on failure. `SDL_CreateSurfaceFrom()` with an `int` takes an address the same way. Bytes move between PHP and that address through SDL's own streams:

```php
$io = SDL_IOFromMem($surface->pixels(), $surface->pitch() * $surface->h());
SDL_WriteIO($io, $bytes, strlen($bytes));
SDL_CloseIO($io);
```

`SDL_ReadIO($io, $size)` returns the bytes read, shorter at the end of the stream. `SDL_WriteIO` throws `ValueError` when `$size` is larger than the string. `SDL_CreateSurfaceFrom()` with a string keeps that string alive until `SDL_DestroySurface()`, because SDL does not copy the pixels.

## Hit tests

`SDL_SetWindowHitTest($window, $callback, $callback_data)` takes a PHP callable. SDL calls it as `$callback(SDL_Window $win, SDL_Point $area, mixed $data): int` on the thread pumping events, and uses the `SDL_HITTEST_*` it returns. A callback that throws, or returns something other than an `int`, answers `SDL_HITTEST_NORMAL`; the exception reaches the PHP call that pumped the events. A `null` callback removes it. The callable and `$callback_data` are held until the hit test is replaced or removed, the window is destroyed, `SDL_Quit()` runs, or the request ends.

Cocoa honours `SDL_HITTEST_DRAGGABLE` and sends `SDL_EVENT_WINDOW_HIT_TEST` when it does. An inactive Mac window spends its first click on activation unless the `SDL_MOUSE_FOCUS_CLICKTHROUGH` hint is `1`.

## Threads

Video and the GPU device stay on the thread that called `SDL_Init`. The binding does not add a check. On macOS, Cocoa rejects a video call from another thread. The identity table is per thread, so a handle boxed on one thread is not the PHP object on another.

## Example

A hidden window, a GPU device, a cleared 2×2 texture, and the pixels read back:

```php
SDL_Init(SDL_INIT_VIDEO);

$window = SDL_CreateWindow('sdl3', 160, 120, SDL_WINDOW_HIDDEN);
$device = SDL_CreateGPUDevice(SDL_GPU_SHADERFORMAT_MSL | SDL_GPU_SHADERFORMAT_SPIRV, false, null);

$info = new SDL_GPUTextureCreateInfo();
$info->type = SDL_GPU_TEXTURETYPE_2D;
$info->format = SDL_GPU_TEXTUREFORMAT_R8G8B8A8_UNORM;
$info->usage = SDL_GPU_TEXTUREUSAGE_COLOR_TARGET;
[$info->width, $info->height, $info->layer_count_or_depth, $info->num_levels] = [2, 2, 1, 1];
$info->sample_count = SDL_GPU_SAMPLECOUNT_1;
$texture = SDL_CreateGPUTexture($device, $info);

$color = new SDL_GPUColorTargetInfo();
$color->texture = $texture;
$color->load_op = SDL_GPU_LOADOP_CLEAR;
$color->store_op = SDL_GPU_STOREOP_STORE;
[$color->clear_color->r, $color->clear_color->g, $color->clear_color->b, $color->clear_color->a] = [0.0, 1.0, 0.0, 1.0];

$commands = SDL_AcquireGPUCommandBuffer($device);
SDL_EndGPURenderPass(SDL_BeginGPURenderPass($commands, [$color], null));

$down = new SDL_GPUTransferBufferCreateInfo();
$down->usage = SDL_GPU_TRANSFERBUFFERUSAGE_DOWNLOAD;
$down->size = 16;
$transfer = SDL_CreateGPUTransferBuffer($device, $down);
$copy = SDL_BeginGPUCopyPass($commands);
$region = new SDL_GPUTextureRegion();
$region->texture = $texture;
[$region->w, $region->h, $region->d] = [2, 2, 1];
$to = new SDL_GPUTextureTransferInfo();
$to->transfer_buffer = $transfer;
SDL_DownloadFromGPUTexture($copy, $region, $to);
SDL_EndGPUCopyPass($copy);
$fence = SDL_SubmitGPUCommandBufferAndAcquireFence($commands);
SDL_WaitForGPUFences($device, true, [$fence]);

$io = SDL_IOFromConstMem(SDL_MapGPUTransferBuffer($device, $transfer, false), 16);
$bytes = SDL_ReadIO($io, 16); // four pixels of "\x00\xff\x00\xff"
SDL_CloseIO($io);
SDL_UnmapGPUTransferBuffer($device, $transfer);

SDL_ReleaseGPUFence($device, $fence);
SDL_ReleaseGPUTransferBuffer($device, $transfer);
SDL_ReleaseGPUTexture($device, $texture);
SDL_DestroyGPUDevice($device);
SDL_DestroyWindow($window);
SDL_Quit();
```

## Testing

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest
zhp -d memory_limit=128M vendor/bin/pest
```

`php84` is Homebrew `php@8.4`. `zhp` is `php@8.4-zts`. On the Pi, `php` is the ZTS build, and the suite needs the Wayland session:

```bash
WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/$(id -u) php -d memory_limit=128M vendor/bin/pest
```

The X11 driver runs through XWayland with `DISPLAY=:0` and no `WAYLAND_DISPLAY`. Both machines must be green. The suite shows windows, maximizes and minimizes them, enters fullscreen, and switches the display mode for exclusive fullscreen on the Mac and X11. The gate draws a triangle by stencil-then-cover into a 4× target, resolves it, blits it, and reads both images back.
