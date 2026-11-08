# Structs

How C structs cross into PHP, including sType, pNext, and VkClearValue.

## Translations

Properties are the C members, count members included. `sType` is not a property; each `vk_<Struct>_from` writes the structure type. The binding reads the count member first and builds that many elements from the list. A count past the list is refused (`vulkan-list-count`); a list longer than its count passes the first `count` elements. Function arguments work the same way. A `null` list is `NULL`. Fixed C arrays (`blendConstants`, `srcOffsets`) are zero-filled past a short list. `VkBool32` members are `bool`.

`pAllocator` and `pipelineCache` parameters are `int` addresses; 0 is `NULL`.

`pNext` is `?object`. The binding links the chain and records each object before it recurses. Seeing an object already on the chain throws `ValueError` "pNext chain loops". A known struct of the wrong kind for its parent is still linked. The same struct object may appear twice in a list; that is not a `pNext` cycle. `VkRenderPassBeginInfo` passes the same clear colour twice.[^structs]

`vkGetPhysicalDeviceFeatures2` is the output form of that chain. The caller passes a `VkPhysicalDeviceFeatures2` and the binding writes the device's answers back onto that object and onto each object already linked from `pNext`. It does not replace those objects, and it leaves each `pNext` link as the caller set it. On an implementation that does not recognise `VkPhysicalDevicePortabilitySubsetFeaturesKHR`, the chained object stays at the values the caller put there.

`VkClearValue` holds exactly one of `$color` or `$depthStencil`. Both set, or neither, throws `ValueError` "VkClearValue holds one of color or depthStencil". `VkClearColorValue::$float32` is four floats.

`VkShaderModuleCreateInfo` has `$codeSize` and the string `$pCode`. `vkCmdPushConstants` takes `size` and a string. A string shorter than the bytes Vulkan reads is refused (`vulkan-bytes-length`).

Scratch allocations live until the Vulkan call returns, then they are freed. SPIR-V is copied into scratch (`codeSize` bytes) so the words are aligned.

`VkCopyDescriptorSet`, `VkMemoryBarrier` and `VkBufferMemoryBarrier` are bound.

[^structs]: struct marshalling and pNext chains
