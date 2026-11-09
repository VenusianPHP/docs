# Changelog

What changed in this package, newest first.

### 2026-11-08

* **v0.11.0**, the first tagged release: `composer require jovian/venusian-metal` (no `:0.10.x-dev`). Requires PHP `~8.4.27||^8.5.12` (8.4.27 or newer, 8.5.12 or newer), ext-metal ^0.11, ext-appkit ^0.11 (was suggested), ext-fb ^0.11.1 and `venusian-surface/*` ^0.11. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/overview)
* Draws Surface 0.11's drawing operations: `ROUNDRECT`, `ROUNDRING` and `SHADOW` (rounded shapes and shadows), `ATLAS`, `MASK` and `GLYPHS` (TrueType text from a glyph atlas), `COVER_GRADIENT` (gradients), the layer operations `TARGET`, `BACKDROP`, `FILTER` and `LAYER_SOURCE` with Surface's `FilterPlan` filter passes, and glass (`GLASS_BACKDROP`, `GLASS`; the device is `DrawsGlass`). The GpuParity scenes match Velvet's pixels, rounded edges and anti-aliased glass edges aside. Layers on an HDR target throw. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/overview#what-it-draws)
* Filter pass images are recycled inside a chain once no later pass reads them, and the free pool is capped at 128 MiB. `draw()` ends an open encoder and commits the half-built command buffer before an exception leaves.
* Reuse: image and ramp source textures are pooled by size; the vertex buffer is made per frame (ext-metal cannot write a buffer in place). [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/guide/engine#pass)

### 2026-10-08

* Staged windows phase 6: show-pass presents, vsync, frames in flight, HDR, hidden windows, see [architecture](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/guide/engine).

### 2026-10-05

* venusian-metal 0.10.0: [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/runbooks/testing).
