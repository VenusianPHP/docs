# Constants

How Vulkan enums and extension names become PHP constants.

## Floor

`tools/vk-constants.php` reads a `vulkan_core.h` and writes `stubs/vk_constants.stub.php`. The committed stub is generated from the Pi's header, `VK_HEADER_VERSION` 1.4.309, so it compiles against the Mac's newer 1.4.357 header. An optional second header drops names that header does not contain. Members inside `#ifdef VK_ENABLE_BETA_EXTENSIONS` are skipped. Aliases whose target is already in the list, and `*_MAX_ENUM` members, are skipped.[^tool]

Each enumerator is `/** @var int @cvalue NAME */ const NAME = UNKNOWN;`. Extension-name macros are `@var string` with `@cvalue`. Every constant is `@cvalue`; none is a literal. `VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME` and `VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME` come from the headers. `VK_EXT_METAL_SURFACE_EXTENSION_NAME` sits inside `#ifdef VK_USE_PLATFORM_METAL_EXT`, so it exists only on macOS. `VK_NULL_HANDLE` and the Wayland, XCB and Xlib names are not registered: this extension includes none of those headers. The stub holds constants only.

`VK_WHOLE_SIZE` is `@cvalue`. As a PHP int it is the signed interpretation of `~0ULL`. Passing it to a `VkDeviceSize` parameter casts back to all-bits-one.

[^tool]: `tools/vk-constants.php`.
