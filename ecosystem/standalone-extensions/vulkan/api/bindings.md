# Bindings

The Vulkan functions and structs this extension binds, by group.

## Groups

| Group | Source | What it binds |
|---|---|---|
| Instance and device | `src/vk_instance.c` | `VkInstance`, `VkPhysicalDevice`, `VkDevice`, `VkQueue`; create, destroy, enumerate, properties, formats, memory properties, queues; `vkGetPhysicalDeviceFeatures2` fills a `VkPhysicalDeviceFeatures2` and its `pNext` chain in place. `VkPhysicalDevicePortabilitySubsetFeaturesKHR` is the chain node for what `VK_KHR_portability_subset` forbids |
| Memory | `src/vk_memory.c` | `VkDeviceMemory`, `VkBuffer`, `VkImage`, `VkImageView`, `VkSampler`; allocate, map, flush, invalidate, bind |
| Pipelines | `src/vk_pipeline.c` | render passes, framebuffers, shader modules, graphics pipelines, descriptor layouts, pools, sets, writes |
| Commands | `src/vk_command.c` | command pools and buffers, draw and copy and blit, barriers, submit, fences, semaphores |
| Surfaces | `src/vk_surface.c` | `VkSurfaceKHR`, `VkSwapchainKHR`; capabilities, formats, present modes, acquire, present; `VkPresentRegionsKHR` / `VkPresentRegionKHR` / `VkRectLayerKHR` (incremental present), `VkPresentIdKHR` and `vkWaitForPresentKHR` (present wait, `VK_ERROR_EXTENSION_NOT_PRESENT` without it), `VkPhysicalDevicePresentIdFeaturesKHR` / `PresentWaitFeaturesKHR` (written back by `vkGetPhysicalDeviceFeatures2`), `VkHdrMetadataEXT` / `VkXYColorEXT` and `vkSetHdrMetadataEXT` (false without the extension) |
| Metal surface | `src/vk_metal.c` | `vkCreateMetalSurfaceEXT`, macOS only, loaded with `vkGetInstanceProcAddr` |
| dmabuf | `src/vk_external.c` | `vkGetMemoryFdKHR`, `vkGetImageDrmFormatModifierPropertiesEXT` via `vkGetDeviceProcAddr`; `vkGetImageSubresourceLayout` |

`vk_read_mapped` and `vk_write_mapped` live in `src/vulkan.c`. They are not Vulkan API entry points.

A device proc that the loader does not export answers `VK_ERROR_EXTENSION_NOT_PRESENT`.
