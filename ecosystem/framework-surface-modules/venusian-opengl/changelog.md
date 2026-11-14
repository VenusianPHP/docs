# Changelog

What changed in this package, newest first.

### 2026-11-08

* **v0.11.0**, the first tagged release: `composer require jovian/venusian-opengl` (no `:0.10.x-dev`). Requires PHP `~8.4.27||^8.5.12` (8.4.27 or newer, 8.5.12 or newer), ext-opengl ^0.11, ext-fb ^0.11.1 and `venusian-surface/*` ^0.11. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-opengl/overview)
* Draws Surface 0.11's drawing operations: `ROUNDRECT`, `ROUNDRING` and `SHADOW` (rounded shapes and shadows), `ATLAS`, `MASK` and `GLYPHS` (TrueType text from a glyph atlas), `COVER_GRADIENT` (gradients), the layer operations `TARGET`, `BACKDROP`, `FILTER` and `LAYER_SOURCE` with Surface's `FilterPlan` filter passes, and glass (`GLASS_BACKDROP`, `GLASS`; the device is `DrawsGlass`). The GpuParity scenes match Velvet's pixels, rounded edges and anti-aliased glass edges aside. Layers on an HDR target throw. Filter numbers beyond four floats travel in an RGBA8 texture of float32 bytes (the context has no float texture formats). [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-opengl/overview#what-it-draws)
* Reuse: the vertex buffer is a ring of three written in place, and a frame's source textures go back to a pool by size and kind instead of being deleted. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-opengl/guide/engine)

### 2026-10-08

* Staged windows phase 6: show-pass presents, vsync, frames in flight, HDR, hidden windows, see [architecture](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-opengl/guide/engine).

### 2026-10-05

* venusian-opengl 0.10.0: [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-opengl/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-opengl/runbooks/testing).
