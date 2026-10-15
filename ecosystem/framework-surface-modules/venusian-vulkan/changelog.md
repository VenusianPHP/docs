# Changelog

What changed in this package, newest first.

### 2026-10-08

* Staged windows phase 6: show-pass presents, vsync, frames in flight, HDR, hidden windows, see [architecture](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine).

### 2026-10-06

* The final review of 11b: three export images, held for the importer until `releaseDmabuf()`; dedicated allocation; a device let go hands its surface back itself; xcb and Xlib surface extensions on the instance; one surface per device. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine)
* A dmabuf export for GTK: `DMABUF` surfaces adopted, a linear exported image blitted per present, `VulkanFramebuffer implements DmabufExportable`; `surfaces()` lists `DMABUF` only with the export extensions. [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/runbooks/testing)
* venusian-vulkan 0.10.0: [engine](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/guide/engine), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-vulkan/runbooks/testing).
