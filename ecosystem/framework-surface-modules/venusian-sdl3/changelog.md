# Changelog

What changed in this package, newest first.

### 2026-11-08

* **v0.11.0**, the first tagged release: `composer require jovian/venusian-sdl3` (no `:0.10.x-dev`). Requires PHP `~8.4.27||^8.5.12` (8.4.27 or newer, 8.5.12 or newer), ext-sdl3 ^0.11, ext-fb ^0.11.1 and `venusian-surface/*` ^0.11. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/overview)
* Draws Surface 0.11's drawing operations: `ROUNDRECT`, `ROUNDRING` and `SHADOW` (rounded shapes and shadows), `ATLAS`, `MASK` and `GLYPHS` (TrueType text from a glyph atlas), `COVER_GRADIENT` (gradients), the layer operations `TARGET`, `BACKDROP`, `FILTER` and `LAYER_SOURCE` with Surface's `FilterPlan` filter passes, and glass (`GLASS_BACKDROP`, `GLASS`; the device is `DrawsGlass`). The GpuParity scenes match Velvet's pixels, rounded edges and anti-aliased glass edges aside. Layers on an HDR target throw. Shaders in MSL and SPIR-V; the SPIR-V filter path has not been run on Linux yet. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/overview#what-it-draws)
* Reuse: one vertex buffer and one transfer buffer kept across frames (written with cycle on), source textures pooled by format and size. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/guide/engine)

### 2026-10-08

* HumanInput slice 18b: SDL's pads are the `sdl3` pad source (`Sdl3PadSource`, `extendPads('sdl3', …)`), read with or without a session or video; pads carry SDL's serial as `hardwareId()` and set SDL's player index; the engine lists no pads and taps its session at `connect()` or throws. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/guide/input)

### 2026-10-08

* HumanInput's `sdl3` input engine: `Sdl3InputEngine`, `Sdl3Pads`, `ScancodeMap`, `JoystickMap`; the session shows events to taps; the provider registers the engine. Requires `venusian-surface/human-input`. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/guide/input)

### 2026-10-08

* Staged windows phase 6: show-pass presents, vsync, frames in flight, HDR, hidden windows, see [architecture](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/guide/engine).

### 2026-10-08

* The `sdl3` stager: `Sdl3BridgeDriver`, `Sdl3Session`, `Sdl3StagedWindow`, `Sdl3Displays`; the provider registers it on the bridge. Requires `venusian-surface/bridge` and `windows`. [stager](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/guide/stager)

### 2026-10-05

* venusian-sdl3 0.10.0: [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-sdl3/runbooks/testing).
