# Overview

Venusian Surface (`venusian/surface`, 0.11.x) is the Venusian Display Panel Framework: native windows and toolkit primitives, staged windows, pixel framebuffers, drawing engines, fonts, images, embedded display panels and human input for Venusian apps.

## Requirements

- PHP 8.4.27+ or 8.5.12+.
- `venusian-voyager/*` 0.11 (console, filesystem, io-pools, nuts-and-bolts) and `gpio/contracts` 0.11.
- Optional extensions per module: ext-fb, ext-rasterize, ext-imgdec (the `extended` drivers), ext-gd (native PNG/JPEG), ext-kqueue or ext-epoll (joining the loop). See [components](/docs/{{version}}/surface/guide/components).

## Install

```bash
composer require venusian/surface
php computer vendor:publish --tag=surface-config
```

The root package `replace`s every `venusian-surface/*` split; a library can require a single split instead. `Surface\Core\Providers\SurfaceServiceProvider` is discovered through `extra.venusian.providers`.

## Modules

| Module | Page |
|---|---|
| Bridge: toolkit sessions on the loop | [bridge](/docs/{{version}}/surface/architecture/bridge) |
| Windows: toolkit and staged windows | [windows](/docs/{{version}}/surface/architecture/windows) |
| Toolkit primitives | [toolkit primitives](/docs/{{version}}/surface/architecture/toolkit-primitives) |
| Framebuffers | [framebuffers](/docs/{{version}}/surface/architecture/framebuffers) |
| Rasterize | [rasterize](/docs/{{version}}/surface/architecture/rasterize) |
| Drawing | [drawing](/docs/{{version}}/surface/architecture/drawing) |
| Images | [images](/docs/{{version}}/surface/architecture/images) |
| Fonts | [fonts](/docs/{{version}}/surface/architecture/fonts) |
| EmbeddedDisplays | [embedded displays](/docs/{{version}}/surface/architecture/embeddeddisplays) |

Toolkits (`jovian/venusian-appkit`, `-gtk`, `-qt`), stagers (`-sdl3`, `-glfw`), GPU engines (`-metal`, `-opengl`, `-sdl3`, `-vulkan`) and pad sources (`-evdev`) ship as separate packages.

## Usage

Start with [composing an app](/docs/{{version}}/surface/runbooks/composing-an-app); tests run as in [testing](/docs/{{version}}/surface/runbooks/testing).
