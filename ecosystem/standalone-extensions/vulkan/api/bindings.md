# Bindings

The Vulkan functions and structs this extension binds, by group.

## Groups

| Group | Source | What it binds |
|---|---|---|
| Instance and device | `src/vk_instance.c` | `VkInstance`, `VkPhysicalDevice`, `VkDevice`, `VkQueue`; create, destroy, enumerate, properties, formats, memory properties, queues; `vkGetPhysicalDeviceFeatures2` fills a `VkPhysicalDeviceFeatures2` and its `pNext` chain in place; `vkGetInstanceProcAddr` takes `?VkInstance` and a name and answers the address as an `int` (0 is `NULL`; with `null` and its own name it is the loader's address). `VkPhysicalDevicePortabilitySubsetFeaturesKHR` is the chain node for what `VK_KHR_portability_subset` forbids |
| Memory | `src/vk_memory.c` | `VkDeviceMemory`, `VkBuffer`, `VkImage`, `VkImageView`, `VkSampler`; allocate, map, flush, invalidate, bind |
| Pipelines | `src/vk_pipeline.c` | render passes, framebuffers, shader modules, graphics pipelines, descriptor layouts, pools, sets, writes |
| Commands | `src/vk_command.c` | command pools and buffers, draw and copy and blit, barriers, submit, fences, semaphores |
| Surfaces | `src/vk_surface.c` | `VkSurfaceKHR`, `VkSwapchainKHR`; capabilities, formats, present modes, acquire, present; `VkPresentRegionsKHR` / `VkPresentRegionKHR` / `VkRectLayerKHR` (incremental present), `VkPresentIdKHR` and `vkWaitForPresentKHR`, `VkPhysicalDevicePresentIdFeaturesKHR` / `PresentWaitFeaturesKHR` (written back by `vkGetPhysicalDeviceFeatures2`), `VkHdrMetadataEXT` / `VkXYColorEXT` and `vkSetHdrMetadataEXT` (void, as C) |
| Metal surface | `src/vk_metal.c` | `vkCreateMetalSurfaceEXT`, macOS only, loaded with `vkGetInstanceProcAddr` |
| dmabuf | `src/vk_external.c` | `vkGetMemoryFdKHR`, `vkGetImageDrmFormatModifierPropertiesEXT` via `vkGetDeviceProcAddr`; `vkGetImageSubresourceLayout` |

Every function is a Vulkan entry point; there are no helper functions. There is no FFI: host data moves through `vkCmdUpdateBuffer` (a string, at most 65,536 bytes a call) and the Vulkan 1.4 host image copies `vkCopyMemoryToImage`, `vkCopyImageToMemory` and `vkTransitionImageLayout` (commands group). A `VkMemoryToImageCopy` or `VkImageToMemoryCopy` region carries its bytes as the string `$pHostPointer`; for a read the caller gives a string of the size to read and the call fills it. The bytes must cover the region's texels at least one byte each (site `vulkan-bytes-length`). `VkPhysicalDeviceHostImageCopyFeatures` is the `pNext` node that enables and reports the feature; the images need `VK_IMAGE_USAGE_HOST_TRANSFER_BIT`.

An extension command whose `vkGet*ProcAddr` answer is `NULL` is refused with `Error` (site `vulkan-no-proc`): calling `NULL` kills the process. Some implementations hand out the command although its extension is not enabled; the call then goes through.

## Refusals

| Site | Throws | Refused call | Probe |
|---|---|---|---|
| `vulkan-list-count` | `ValueError` | a count past its list | `tests/Probes/ListCountTest.php` |
| `vulkan-bytes-length` | `ValueError` | `codeSize` or push-constant `size` past the string | `tests/Probes/BytesLengthTest.php` |
| `vulkan-null-dispatchable` | `ValueError` | a released `VkInstance`, `VkPhysicalDevice`, `VkDevice`, `VkQueue` or `VkCommandBuffer` | `tests/Probes/NullDispatchableTest.php` |
| `vulkan-no-proc` | `Error` | an extension command with no proc address | `tests/Probes/NoProcTest.php` |

`bindings.json` lists the sites, the marshal helpers, the glue and the typemap. Probes run on a build configured with `--enable-vulkan-probes` (`VULKAN_CONFIGURE=--enable-vulkan-probes ./install-macos.sh`); the `VULKAN_PROBE_OFF` environment variable switches one site off in a child process.
