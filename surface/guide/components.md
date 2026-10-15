# Components

Splits, providers, container bindings, published configs.

## Overview

`venusian/surface` (root, version key `0.10.0`) `replace`s every split at `self.version`. Splits with a manifest this line:[^root]

| Split | Namespace | Holds | Requires |
|---|---|---|---|
| `venusian-surface/nuts-and-bolts` | `Surface\NutsAndBolts\` | `Color`, `Affine` | php only |
| `venusian-surface/contracts` | `Surface\Contracts\` | Interfaces, mail, `MenuRole`, exceptions, primitive contracts, `Placement`, `PrimitiveRegistry`, typography values | voyager contracts, nuts-and-bolts |
| `venusian-surface/bridge` | `Surface\Bridge\` | `ToolkitManager`, `ToolkitBridgeDriver`, `BridgedToolkitSession`, `ToolkitPump` | contracts, `venusian-voyager/io-pools` |
| `venusian-surface/windows` | `Surface\Windows\` | `ToolkitWindowManager`, `StagedWindowManager`, `StagedWindow` (base), `MenuProfile`, `MenuItem`, primitive abstracts (incl. `TKCanvas`), `HostsPrimitives` | contracts, bridge, framebuffers, nuts-and-bolts |
| `venusian-surface/framebuffers` | `Surface\Framebuffers\` | `FramebufferManager`, `Layout`, `PixelMapper`, `SpanList`, the five abstract kinds, `Native\*` (bytes in PHP), `Extended\*` (bytes in C) | contracts, nuts-and-bolts, voyager nuts-and-bolts; suggests ext-fb 0.10 |
| `venusian-surface/drawing` | `Surface\Drawing\` | `DrawingManager`, `RenderingEngine` (base), `Velvet\VelvetGE` | contracts, framebuffers, rasterize, nuts-and-bolts, voyager contracts + nuts-and-bolts; suggests the four engine packages |
| `venusian-surface/embedded-displays` | `Surface\EmbeddedDisplays\` | `EmbeddedDisplayManager`, `EmbeddedDisplay` | gpio/contracts, contracts, framebuffers, voyager contracts + nuts-and-bolts; suggests scrapyard-io/framework and the 0.10 panel chips |
| `venusian-surface/human-input` | `Surface\HumanInput\` | `HumanInputManager`, `HumanInputPoller`, `InputFrame`, `ICInput`, merged keyboard and mouse, keymaps, `MagicAliases\HumanInput` | contracts, bridge, voyager contracts + io-pools + nuts-and-bolts |
| `venusian-surface/fonts` | `Surface\Fonts\` | `FontManager`, `ClassicFont`, `Console\FontMakeCommand`, `Support\AdafruitGfxHeader` | contracts, console, filesystem |
| `venusian-surface/images` | `Surface\Images\` | `ImagesManager`, `ImageDecoder` (base), `TiffDirectory`, `Native\*` (gd + PHP TIFF), `Extended\*` (C) | contracts, framebuffers, voyager contracts + nuts-and-bolts; suggests ext-gd, ext-imgdec 0.10 |
| `venusian-surface/rasterize` | `Surface\Rasterize\` | `RasterizeManager`, `Rasterizer` (shapes), `Stroker`, `Native\*` (geometry in PHP), `Extended\*` (geometry in C) | contracts, voyager contracts + nuts-and-bolts; suggests ext-rasterize 0.10 |

Toolkit drivers live outside: `jovian/venusian-appkit`, `-gtk`, `-qt`; stagers `jovian/venusian-sdl3`, `-glfw`; pad source `jovian/venusian-evdev`. A split never requires `venusian/surface`; only an app composes.

## Providers

* Root discovers `Surface\Core\Providers\SurfaceServiceProvider` (aggregate): merges `config/bridge.php` → `bridge`, `config/windows.php` → `windows`, `config/framebuffers.php` → `framebuffers`, `config/rasterize.php` → `rasterize`, `config/images.php` → `images`, `config/drawing.php` → `drawing`, `config/embedded-displays.php` → `embedded-displays`, `config/fonts.php` → `fonts`, `config/human-input.php` → `human-input`; registers Windows, Bridge, HumanInput, Framebuffers, EmbeddedDisplays, Rasterize, Images, Fonts and Drawing providers; publishes the nine configs under tag `surface-config`.[^core]
* `BridgeServiceProvider`: singleton `toolkit-bridge` = `ToolkitManager`, alias `ToolkitManager::class`.[^bridge]
* `WindowsServiceProvider`: singleton `toolkit-windows` = `ToolkitWindowManager(toolkit-bridge, config('windows.menus'), config('windows.default_menu'))`, alias `ToolkitWindowManager::class`. Profiles parsed on first resolve. Singleton `staged-windows` = `StagedWindowManager(toolkit-bridge, config('bridge.stage.<os>.default'))`, alias `StagedWindowManager::class`.[^windows]
* `HumanInputServiceProvider`: singleton `human-input` = `HumanInputManager(toolkit-bridge, InputFrame sized by sketches.refresh_rate, os, config('human-input.pads.<os>'), post to event-loop when resolved)`, alias `HumanInputManager::class`; joins `HumanInputPoller` to the loop once `event-loop` resolves.[^human-input]
* `FramebuffersServiceProvider`: singleton `framebuffers` = `FramebufferManager`, alias `FramebufferManager::class`; `driver('native')` always, `driver('extended')` with ext-fb 0.10, `driver('auto')` (default) picks between them.[^framebuffers]
* `RasterizeServiceProvider`: singleton `rasterize` = `RasterizeManager`, alias `RasterizeManager::class`; `driver('native')` always, `driver('extended')` with ext-rasterize 0.10, `driver('auto')` (default) picks between them.[^rasterize]
* `ImagesServiceProvider`: singleton `images` = `ImagesManager`, alias `ImagesManager::class`; `driver('native')` always (PNG/JPEG need ext-gd), `driver('extended')` with ext-imgdec 0.10, `driver('auto')` (default) picks between them.[^images]
* `DrawingServiceProvider`: singleton `drawing` = `DrawingManager(config, framebuffers, rasterize)`, alias `DrawingManager::class`; `renderer('velvet', …)` built in.[^drawing]
* `EmbeddedDisplaysServiceProvider`: singleton `displays` = `EmbeddedDisplayManager(framebuffers, config('embedded-displays.defaults'), circuit catalog when bound, post to event-loop when bound)`, alias `EmbeddedDisplayManager::class`.[^embedded-displays]
* Each driver package's provider binds its own contract to `toolkit-bridge`'s `driver('<name>')`: one driver, one session per process.

```bash
php computer vendor:publish --tag=surface-config
```

[^root]: composer.json
[^core]: SurfaceServiceProvider
[^bridge]: BridgeServiceProvider
[^windows]: WindowsServiceProvider
[^framebuffers]: FramebuffersServiceProvider
[^rasterize]: RasterizeServiceProvider
[^images]: ImagesServiceProvider
[^embedded-displays]: EmbeddedDisplaysServiceProvider
[^drawing]: DrawingServiceProvider
[^human-input]: HumanInputServiceProvider
