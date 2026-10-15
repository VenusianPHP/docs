# Constants

How Vulkan enums and extension names become PHP constants.

## Floor

`tools/vk-constants.php` reads a `vulkan_core.h` and writes `stubs/vk_constants.stub.php`. The committed stub is generated from the Pi's header, `VK_HEADER_VERSION` 1.4.309, so it compiles against the Mac's newer 1.4.357 header. An optional second header drops names that header does not contain. Members inside `#ifdef VK_ENABLE_BETA_EXTENSIONS` are skipped. Aliases whose target is already in the list, and `*_MAX_ENUM` members, are skipped.[^tool]

Each enumerator is `/** @var int @cvalue NAME */ const NAME = UNKNOWN;`. Extension-name macros are `@var string` with `@cvalue`. `VK_NULL_HANDLE` is the literal `0`. `VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME` is the literal `"VK_KHR_portability_subset"`, because that macro lives in `vulkan_beta.h`. `VK_EXT_METAL_SURFACE_EXTENSION_NAME` is the literal `"VK_EXT_metal_surface"`, because that macro lives in `vulkan_metal.h`; `VK_KHR_WAYLAND_SURFACE_EXTENSION_NAME` (`vulkan_wayland.h`), `VK_KHR_XCB_SURFACE_EXTENSION_NAME` (`vulkan_xcb.h`), `VK_KHR_XLIB_SURFACE_EXTENSION_NAME` (`vulkan_xlib.h`) and `VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME` are literals too. `VK_API_VERSION_1_1` and `VK_API_VERSION_1_3` are `@cvalue`. The generator also writes `vk_read_mapped`, `vk_write_mapped`, `vk_close_fd` and `vk_loader_path` at the end of the stub.

`VK_WHOLE_SIZE` is `@cvalue`. As a PHP int it is the signed interpretation of `~0ULL`. Passing it to a `VkDeviceSize` parameter casts back to all-bits-one.

[^tool]: `tools/vk-constants.php`.
