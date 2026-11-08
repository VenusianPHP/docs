# Overview

![CI](https://github.com/php-io-extensions/vulkan/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/vulkan/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/vulkan/actions/workflows/ci.yml)
[![Vulkan API](https://img.shields.io/badge/Vulkan_API-16.0%25_%2897%2F605%29-blue?style=flat-square)](https://github.com/php-io-extensions/vulkan/blob/v0.11.1/SUPPORT.md)

1:1 PHP bindings of Vulkan: instance and device, memory, images, buffers, render
passes, pipelines, descriptors, commands, sync, surfaces and swapchains, and the
Linux dmabuf export GTK needs. Written in C against the Zend API and
`<vulkan/vulkan.h>`, linked to the system Vulkan loader. PHP 8.4+, NTS and ZTS.
Version 0.11.1.

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

## Install

Through PIE:

```bash
pie install php-io-extensions/vulkan
```

From a checkout:

```bash
./install-macos.sh            # Homebrew php@8.4 and php@8.4-zts, or pass PHP binaries
./install-debian-trixie.sh    # Debian trixie, Raspberry Pi OS
```

`./install-macos.sh` refuses to start unless `pkg-config` finds `vulkan`, and
tells you to `brew install vulkan-loader vulkan-headers molten-vk`.

## Translations

Bindings are 1:1. Every parameter and member of the C call is there, counts
included. There are no defaults, no composites and no helper functions. The
translations:

- A C array is a PHP list. Its count stays a separate argument or member, as in
  C. Vulkan reads `count` elements; the binding builds the list into a C array.
- Enumerate calls take `?int &$count` and `?array &$list`, as C's two calls:
  pass `null` for the list to get the count, then pass the count and a variable
  to get up to that many. `VK_INCOMPLETE` is returned as in C.
- An out-handle, out-struct or out-int is a by-reference parameter.
- `sType` is not a property. Each struct class fills its own.
- `pNext` is `?object`, a chain of struct objects.
- `VkBool32` is `bool`.
- `pAllocator` and `pipelineCache` are `int` addresses; `0` is `NULL`.
- SPIR-V is `VkShaderModuleCreateInfo::$codeSize` plus the string `$pCode`.
  Push constants are a string.
- Results are the `VkResult` int, as in C.
- `vkMapMemory` writes the mapped address to `$ppData` (`int`). Host data moves
  through `vkCmdUpdateBuffer` (a string, at most 65,536 bytes a call) and the
  host image copies: `vkCopyMemoryToImage` takes strings, and
  `vkCopyImageToMemory` fills the `$pHostPointer` string of each region (give
  it a string of the size to read). `vkTransitionImageLayout` moves an image to
  the layout a host copy needs. They need Vulkan 1.4, the `hostImageCopy`
  feature (chain `VkPhysicalDeviceHostImageCopyFeatures` into
  `VkDeviceCreateInfo`), and images made with `VK_IMAGE_USAGE_HOST_TRANSFER_BIT`.
  `vkGetMemoryFdKHR` hands out a descriptor the caller closes (`posix_close()` of
  ext-posi).
- `vkGetInstanceProcAddr($instance, $pName)` returns the function's address as
  an `int` (`PFN_vkVoidFunction`; `0` is `NULL`). With `null` and
  `'vkGetInstanceProcAddr'` it names the loader this process loaded: another
  library's `dlsym()` of the same name (ext-posi) gives the same address only
  in the same loader.

## Refusals

The binding declines to make the call only where making it would crash the
process. Each refusal has a probe in `tests/Probes` that shows the crash with
the refusal switched off (`--enable-vulkan-probes`).

| Site | Throws | Refused call |
|---|---|---|
| `vulkan-list-count` | `ValueError` | a count past its list: Vulkan reads past the C array |
| `vulkan-bytes-length` | `ValueError` | `codeSize` or push-constant `size` past the string |
| `vulkan-null-dispatchable` | `ValueError` | a released instance, physical device, device, queue or command buffer: the loader reads its dispatch table through it |
| `vulkan-no-proc` | `Error` | an extension command `vkGetDeviceProcAddr` gave as `NULL` |

Everything else goes to Vulkan as given, including values the validation
layers would reject.

## Handles and parents

Handles are `final`, not constructable, not cloneable, not serializable, with
`pointer(): int` and `static fromPointer(int $pointer): ?static`.
`fromPointer(0)` is `null`. One PHP object per class and native value.

Destroying a parent releases every PHP handle whose parent chain reaches it. A
released handle's `pointer()` is 0 and it goes to Vulkan as `VK_NULL_HANDLE`.
A released dispatchable handle is refused (see [Refusals](#refusals)). Destroy
functions take `null`, as in C.
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
`triangleFans` is one of those flags; read it from the device.

A surface over ext-metal uses `CAMetalLayer::pointer()` as
`VkMetalSurfaceCreateInfoEXT::$pLayer`, with `VK_KHR_surface` and
`VK_EXT_metal_surface` enabled on the instance, then `vkCreateMetalSurfaceEXT`.

Enable portability only where the loader and the device list it. On the Pi
neither name is present, so the same code leaves the create infos alone:

```php
$app = new VkApplicationInfo();
$app->pApplicationName = 'ext-vulkan tests';
$app->apiVersion = VK_API_VERSION_1_3;
vkEnumerateInstanceExtensionProperties(null, $count, null);
vkEnumerateInstanceExtensionProperties(null, $count, $available);
$names = array_map(fn (VkExtensionProperties $e): string => $e->extensionName, $available);

$instanceInfo = new VkInstanceCreateInfo();
$instanceInfo->pApplicationInfo = $app;
if (in_array(VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME, $names, true)) {
    $instanceInfo->ppEnabledExtensionNames = [VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME];
    $instanceInfo->enabledExtensionCount = 1;
    $instanceInfo->flags |= VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
}


vkEnumerateDeviceExtensionProperties($physical, null, $count, null);
vkEnumerateDeviceExtensionProperties($physical, null, $count, $deviceExtensions);
$deviceNames = array_map(fn (VkExtensionProperties $e): string => $e->extensionName, $deviceExtensions);
if (in_array(VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME, $deviceNames, true)) {
    $deviceInfo->ppEnabledExtensionNames[] = VK_KHR_PORTABILITY_SUBSET_EXTENSION_NAME;
    $deviceInfo->enabledExtensionCount++;
}
```

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/vulkan/blob/v0.11.1/SUPPORT.md) lists every command of the Vulkan 1.4.309 registry, the header floor this
extension builds against: core 1.0 to 1.4 and every supported extension that is not deprecated or
obsoleted, aliases not counted twice, each marked bound or not; the API badge is computed from it.
Regenerate both after a binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

## Example

Clear an 8×8 image and copy it out. This skips the CPU device and uses the
first graphics queue.

```php
$app = new VkApplicationInfo();
$app->apiVersion = VK_API_VERSION_1_3;
$instanceInfo = new VkInstanceCreateInfo();
$instanceInfo->pApplicationInfo = $app;
vkCreateInstance($instanceInfo, 0, $instance);

vkEnumeratePhysicalDevices($instance, $count, null);
vkEnumeratePhysicalDevices($instance, $count, $devices);
foreach ($devices as $candidate) {
    vkGetPhysicalDeviceProperties($candidate, $properties);
    if ($properties->deviceType !== VK_PHYSICAL_DEVICE_TYPE_CPU) {
        $physical = $candidate;
        break;
    }
}
vkGetPhysicalDeviceQueueFamilyProperties($physical, $count, null);
vkGetPhysicalDeviceQueueFamilyProperties($physical, $count, $families);
$family = array_key_first(array_filter(
    $families,
    fn (VkQueueFamilyProperties $family): bool => ($family->queueFlags & VK_QUEUE_GRAPHICS_BIT) !== 0,
));
$queueInfo = new VkDeviceQueueCreateInfo();
$queueInfo->queueFamilyIndex = $family;
$queueInfo->queueCount = 1;
$queueInfo->pQueuePriorities = [1.0];
$deviceInfo = new VkDeviceCreateInfo();
$deviceInfo->queueCreateInfoCount = 1;
$deviceInfo->pQueueCreateInfos = [$queueInfo];
vkCreateDevice($physical, $deviceInfo, 0, $device);
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
vkCreateImage($device, $imageInfo, 0, $image);
```

Create the image with `VK_IMAGE_USAGE_HOST_TRANSFER_BIT`, move it to
`VK_IMAGE_LAYOUT_GENERAL` with `vkTransitionImageLayout`, and read it with
`vkCopyImageToMemory` once the queue is idle: a `VkImageToMemoryCopy` region
holds a string of `width * height * 4` bytes in `$pHostPointer`, and the call
puts the pixels in it.

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
