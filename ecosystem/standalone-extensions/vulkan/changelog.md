# Changelog

What changed in this package, newest first.

### 2026-10-09

* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.

### 2026-10-08

Staged-window presentation: incremental present regions, present id and `vkWaitForPresentKHR`, the present id / wait feature structs, HDR metadata, and the five extension-name constants. `vulkan_u64_list` moved to the runtime. Suite: Homebrew php@8.4 NTS and ZTS 28 passed, 3 skipped; Pi (V3DV) 30 passed, 1 skipped, the present with regions, id and wait included.

### 2026-10-06

`VkMemoryDedicatedAllocateInfo`; `vk_loader_path()` (dladdr of `vkGetInstanceProcAddr`); the X11 surface extension names (`VK_KHR_xcb_surface`, `VK_KHR_xlib_surface`). Suite: Homebrew php@8.4 NTS and ZTS 26 passed, 2 skipped; Pi 27 passed, 1 skipped.

`vk_close_fd()` closes a descriptor `vkGetMemoryFdKHR` handed out (`EBADF` is a `ValueError`). The generator writes everything the committed stub holds: `VK_API_VERSION_1_1`, the Wayland surface and properties2 names, `vk_close_fd`. Suite: Homebrew php@8.4 NTS and ZTS 24 passed, 2 skipped; Pi 25 passed, 1 skipped.

### 2026-10-05

MoltenVK. `vkGetPhysicalDeviceFeatures2` fills `VkPhysicalDeviceFeatures2` and a chained `VkPhysicalDevicePortabilitySubsetFeaturesKHR` in place (`VK_ENABLE_BETA_EXTENSIONS` before `<vulkan/vulkan.h>`). The test helpers enable `VK_KHR_portability_enumeration` and `VK_KHR_portability_subset` only where the loader and the device list them. On this M1 Pro, MoltenVK 1.4.2 reports `triangleFans` true, `pointPolygons` false, and depth-stencil `D32_SFLOAT_S8_UINT` only. A `VkSurfaceKHR` over ext-metal's `CAMetalLayer` carries a swapchain. Suite: Homebrew php@8.4 NTS and ZTS 22 passed, 2 skipped, 1221 assertions; Pi 23 passed, 1 skipped, 1223 assertions.

### 2026-10-05

Created the bundle for 0.10.0. The extension binds Vulkan 1:1 against the system loader: instance and device, memory and images, render passes and pipelines, commands and fences, surfaces and swapchains, and Linux dmabuf export. Constants are generated from the Pi's `vulkan_core.h` 1.4.309. The suite is 20 passed (1210 assertions) on the Pi (Mesa 26.2 V3DV) with `WAYLAND_DISPLAY=wayland-0`, and 5 passed, 15 skipped (1147 assertions) on Homebrew PHP 8.4 NTS and ZTS. The Mac skips every test that opens a device: MoltenVK needs the portability flags of slice 5. The gate is a stencil-then-cover triangle into a 4× image, resolved in the render pass, blitted, copied out, and read back.
