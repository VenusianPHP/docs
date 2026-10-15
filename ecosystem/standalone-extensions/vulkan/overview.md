# Overview

![CI](https://github.com/php-io-extensions/vulkan/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/vulkan/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/vulkan/actions/workflows/ci.yml)

1:1 PHP bindings of Vulkan: instance and device, memory, images, buffers, render
passes, pipelines, descriptors, commands, sync, surfaces and swapchains, and the
Linux dmabuf export GTK needs. Written in C against the Zend API and
`<vulkan/vulkan.h>`, linked to the system Vulkan loader. PHP 8.4+, NTS and ZTS.
Version 0.10.0.

Functions are global PHP functions under their C names. Enums and flags are PHP
constants under their C names, values taken from the headers. Each handle is a
final class. Each struct is a final class whose properties are the C members.

## Requirements

- The Vulkan loader and headers. Debian and Raspberry Pi OS: `libvulkan-dev`.
  macOS: `brew install vulkan-loader vulkan-headers molten-vk`.
- A GPU device. Tests skip the CPU device (llvmpipe). On macOS the device
  tests run through MoltenVK once the instance and device enable portability,
  as in [On macOS](#on-macos). The swapchain test and the dmabuf test stay
  Linux-only.
- The measured Pi is Mesa 26.2 V3DV, Vulkan headers 1.4.309, API 1.3. The Mac
  headers measured here are 1.4.357.
- `venusian build` reads the system packages from `extra.venusian.system` in composer.json: apt packages to build with and the run-time ones a `.deb` depends on or recommends, and the Homebrew ones.

## Install

Through PIE:

```bash
pie install php-io-extensions/vulkan:0.10.x-dev
```

From a checkout:

```bash
./install-macos.sh            # Homebrew php@8.4 and php@8.4-zts, or pass PHP binaries
./install-debian-trixie.sh    # Debian trixie, Raspberry Pi OS
```

`./install-macos.sh` refuses to start unless `pkg-config` finds `vulkan`, and
tells you to `brew install vulkan-loader vulkan-headers molten-vk`.

## Translations

Bindings are 1:1. There are no defaults and no composites. The only translations:

- A pointer + count pair is one PHP list.
- The enumerate-twice calls (`vkEnumerate*`, `vkGet*Properties` with a count,
  `vkGetSwapchainImagesKHR`) fill a by-reference list. The binding calls twice
  and retries while the result is `VK_INCOMPLETE`.
- An out-handle or out-struct is a by-reference parameter.
- `sType` is not a property. Each struct class fills its own.
- `pNext` is `?object`, a chain of struct objects. A chain that loops is a
  `ValueError` before the binding walks it. A struct of the wrong kind for its
  parent is linked as given.
- `vkGetPhysicalDeviceFeatures2` takes the `VkPhysicalDeviceFeatures2` object
  and fills it in place, including the structs already linked on `pNext`. The
  call does not replace those objects.
- `pAllocator` is `null`. There is no custom allocator.
- `VkShaderModuleCreateInfo::$code` is one string. `codeSize` is its length. A
  length that is not a multiple of 4 is a `ValueError`.
- `vkCmdPushConstants` takes a string. A string shorter than `size` is a
  `ValueError`.
- Results are the `VkResult` int, as in C.
- `vkMapMemory` writes the mapped address to `$ppData` (`int`). PHP reads and
  writes that address with `vk_read_mapped(int $address, int $size): string` and
  `vk_write_mapped(int $address, string $bytes): void`. Address 0 is refused.
  Any other address is trusted. `vkFlushMappedMemoryRanges` and
  `vkInvalidateMappedMemoryRanges` are what make non-coherent memory correct.
- `vkGetMemoryFdKHR` hands out a file descriptor the caller owns.
  `vk_close_fd(int $fd): void` closes it; a descriptor that is not open (closed
  already) is a `ValueError`.
- `vk_loader_path(): ?string` names the file the Vulkan loader this extension
  calls was loaded from (`dladdr` of `vkGetInstanceProcAddr`), so another
  library that loads a loader itself (Qt's `QVulkanInstance`) can be pointed at
  the same one.
- `VkMemoryDedicatedAllocateInfo` chains on `VkMemoryAllocateInfo`: an
  exported image allocated dedicated works on drivers that require it.

`VkCopyDescriptorSet` and `VkBufferMemoryBarrier` are not bound.
`vkUpdateDescriptorSets` refuses a non-empty copy list. `vkCmdPipelineBarrier`
takes `VkMemoryBarrier`s and `VkImageMemoryBarrier`s and refuses a non-empty
buffer-barrier list; a list holding another class is a `TypeError`.

## Handles and parents

Handles are `final`, not constructable, not cloneable, not serializable, with
`pointer(): int` and `static fromPointer(int $pointer): static`. Address 0 is
refused. One PHP object per class and native value.

Destroying a parent releases every PHP handle whose parent chain reaches it.
After `vkDestroyDevice`, a `VkBuffer` or `VkQueue` from that device throws
`ValueError` ("VkBuffer has been destroyed") instead of reaching the driver.
`vkDestroyCommandPool` releases its command buffers. `vkDestroyDescriptorPool`
releases its descriptor sets. Swapchain images are owned by the swapchain:
`vkDestroySwapchainKHR` releases them, and PHP does not destroy them.
A surface created outside this extension (SDL's `SDL_Vulkan_CreateSurface`)
enters through `VkSurfaceKHR::fromPointer()`. Its parent is unknown, so only
`vkDestroySurfaceKHR` releases it.

## Device selection

Skip `VK_PHYSICAL_DEVICE_TYPE_CPU`. The integrated or discrete GPU is the
device. Pick a stencil format with `vkGetPhysicalDeviceFormatProperties`:
`VK_FORMAT_D24_UNORM_S8_UINT`, otherwise `VK_FORMAT_D32_SFLOAT_S8_UINT`.

## On macOS

Homebrew packages: `vulkan-loader`, `vulkan-headers`, `molten-vk`. The loader
finds MoltenVK through its ICD manifest and lists that device only to an
instance created with `VK_KHR_portability_enumeration` and
`VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR`. A device on it enables
`VK_KHR_portability_subset` when `vkEnumerateDeviceExtensionProperties` lists
that extension. `vkGetPhysicalDeviceFeatures2` with a
`VkPhysicalDevicePortabilitySubsetFeaturesKHR` chained on
`VkPhysicalDeviceFeatures2::$pNext` reports what the subset forbids.
`triangleFans` is one of those flags; read it from the driver.

A surface over ext-metal uses `CAMetalLayer::pointer()` as
`VkMetalSurfaceCreateInfoEXT::$pLayer`, with `VK_KHR_surface` and
`VK_EXT_metal_surface` enabled on the instance, then `vkCreateMetalSurfaceEXT`.

Enable portability only where the loader and the device list it. On the Pi
neither name is present, so the same code leaves the create infos alone:

```php
$app = new VkApplicationInfo();
$app->pApplicationName = 'ext-vulkan tests';
$app->apiVersion = VK_API_VERSION_1_3;
vkEnumerateInstanceExtensionProperties(null, $available);
$names = array_map(fn (VkExtensionProperties $e): string => $e->extensionName, $available);
$extensions = [];
$instanceInfo = new VkInstanceCreateInfo();
$instanceInfo->pApplicationInfo = $app;
if (in_array(VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME, $names, true)) {
    $extensions[] = VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME;
    $instanceInfo->flags |= VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
}
$instanceInfo->enabledExtensionNames = $extensions;

vkEnumerateDeviceExtensionProperties($physical, null, $deviceExtensions);
$deviceNames = array_map(fn (VkExtensionProperties $e): string => $e->extensionName, $deviceExtensions);
if (in_array(VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME, $deviceNames, true)) {
    $deviceInfo->enabledExtensionNames[] = VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME;
}
```

## Example

Clear an 8×8 image and copy it out. This skips the CPU device and uses the
first graphics queue.

```php
$app = new VkApplicationInfo();
$app->apiVersion = VK_API_VERSION_1_3;
$instanceInfo = new VkInstanceCreateInfo();
$instanceInfo->pApplicationInfo = $app;
vkCreateInstance($instanceInfo, null, $instance);

vkEnumeratePhysicalDevices($instance, $devices);
foreach ($devices as $candidate) {
    vkGetPhysicalDeviceProperties($candidate, $properties);
    if ($properties->deviceType !== VK_PHYSICAL_DEVICE_TYPE_CPU) {
        $physical = $candidate;
        break;
    }
}
vkGetPhysicalDeviceQueueFamilyProperties($physical, $families);
$family = array_key_first(array_filter(
    $families,
    fn (VkQueueFamilyProperties $family): bool => ($family->queueFlags & VK_QUEUE_GRAPHICS_BIT) !== 0,
));
$queueInfo = new VkDeviceQueueCreateInfo();
$queueInfo->queueFamilyIndex = $family;
$queueInfo->pQueuePriorities = [1.0];
$deviceInfo = new VkDeviceCreateInfo();
$deviceInfo->pQueueCreateInfos = [$queueInfo];
vkCreateDevice($physical, $deviceInfo, null, $device);
vkGetDeviceQueue($device, $family, 0, $queue);

$imageInfo = new VkImageCreateInfo();
$imageInfo->imageType = VK_IMAGE_TYPE_2D;
$imageInfo->format = VK_FORMAT_R8G8B8A8_UNORM;
[$imageInfo->extent->width, $imageInfo->extent->height, $imageInfo->extent->depth] = [8, 8, 1];
$imageInfo->mipLevels = 1;
$imageInfo->arrayLayers = 1;
$imageInfo->samples = VK_SAMPLE_COUNT_1_BIT;
$imageInfo->tiling = VK_IMAGE_TILING_OPTIMAL;
$imageInfo->usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
vkCreateImage($device, $imageInfo, null, $image);
```

Map the destination buffer with `vkMapMemory`, then `vk_read_mapped` on the
address it wrote. Call `vkFlushMappedMemoryRanges` after a write and
`vkInvalidateMappedMemoryRanges` before a read when the memory is not coherent.

## Testing

```bash
php84 -d memory_limit=128M vendor/bin/pest   # Homebrew NTS
zhp   -d memory_limit=128M vendor/bin/pest   # Homebrew ZTS
php   -d memory_limit=128M vendor/bin/pest   # the Pi
```

On the Pi the swapchain test needs `WAYLAND_DISPLAY=wayland-0` and
`XDG_RUNTIME_DIR=/run/user/$(id -u)`. A window appears. The gate draws a
stencil-then-cover triangle into a 4× image, resolves it in the render pass,
blits, copies out, and reads the pixels back. On macOS that gate runs through
MoltenVK, which has `VK_FORMAT_D32_SFLOAT_S8_UINT` and not
`VK_FORMAT_D24_UNORM_S8_UINT`.
