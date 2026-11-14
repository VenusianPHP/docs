# Changelog

What changed in this package, newest first.

### 2026-11-08

* **v0.11.0**: requires PHP `~8.4.27||^8.5.12` (8.4.27 or newer, 8.5.12 or newer), ext-vulkan ^0.11, ext-posi ^0.11 (closes dmabuf descriptors) and `venusian-surface/*` ^0.11. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/overview)
* Vulkan 1.4 with host image copies: the instance asks for 1.4 and the device needs the `hostImageCopy` feature (refused by name without it). Readbacks and uploads are `vkCopyImageToMemory` / `vkCopyMemoryToImage`, the frame's vertices go in with `vkCmdUpdateBuffer` into pooled device-local buffers, and the package maps no memory; `coherent()` and the staging buffers are gone. Verified on MoltenVK; not yet run on Linux or the Pi. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine)
* Draws Surface 0.11's drawing operations: `ROUNDRECT`, `ROUNDRING` and `SHADOW` (rounded shapes and shadows), `ATLAS`, `MASK` and `GLYPHS` (TrueType text from a glyph atlas), `COVER_GRADIENT` (gradients), the layer operations `TARGET`, `BACKDROP`, `FILTER` and `LAYER_SOURCE` with Surface's `FilterPlan` filter passes, and glass (`GLASS_BACKDROP`, `GLASS`; the device is `DrawsGlass`). The GpuParity scenes match Velvet's pixels, rounded edges and anti-aliased glass edges aside. Layers on an HDR target throw. The fragment push-constant block is 112 bytes (128 in all). [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/overview#what-it-draws)

### 2026-10-08

* Staged windows phase 6: show-pass presents, vsync, frames in flight, HDR, hidden windows, see [architecture](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine).

### 2026-10-06

* The final review of 11b: three export images, held for the importer until `releaseDmabuf()`; dedicated allocation; a device let go hands its surface back itself; xcb and Xlib surface extensions on the instance; one surface per device. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine)
* A dmabuf export for GTK: `DMABUF` surfaces adopted, a linear exported image blitted per present, `VulkanFramebuffer implements DmabufExportable`; `surfaces()` lists `DMABUF` only with the export extensions. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/runbooks/testing)
* venusian-vulkan 0.10.0: [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/runbooks/testing).
