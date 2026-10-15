# Structs

How C structs cross into PHP, including sType, pNext, and VkClearValue.

## Translations

Properties are the C members. `sType` is not a property; each `vk_<Struct>_from` writes the structure type. Count members that pair with a list are dropped and derived from the list length. `VkPipelineViewportStateCreateInfo::$viewportCount` and `$scissorCount` stay, because dynamic state leaves the arrays empty and Vulkan still reads the counts.

`pAllocator` parameters are typed `null`.

`pNext` is `?object`. The binding links the chain and records each object before it recurses. Seeing an object already on the chain throws `ValueError` "pNext chain loops". A known struct of the wrong kind for its parent is still linked. The same struct object may appear twice in a list; that is not a `pNext` cycle. `VkRenderPassBeginInfo` passes the same clear colour twice.[^plan]

`vkGetPhysicalDeviceFeatures2` is the output form of that chain. The caller passes a `VkPhysicalDeviceFeatures2` and the binding writes the driver's answers back onto that object and onto each object already linked from `pNext`. It does not replace those objects, and it leaves each `pNext` link as the caller set it. On a driver that does not recognise `VkPhysicalDevicePortabilitySubsetFeaturesKHR`, the chained object stays at the values the caller put there.

`VkClearValue` holds exactly one of `$color` or `$depthStencil`. Both set, or neither, throws `ValueError` "VkClearValue holds one of color or depthStencil". `VkClearColorValue::$float32` is four floats.

`VkShaderModuleCreateInfo::$code` is one string. Its byte length becomes `codeSize`. A length that is not a multiple of 4 is refused. `vkCmdPushConstants` refuses a string shorter than `size`.

Scratch allocations live until the Vulkan call returns, then they are freed. SPIR-V is copied into scratch so the words are aligned.

`VkCopyDescriptorSet`, `VkMemoryBarrier`, and `VkBufferMemoryBarrier` are not bound. A non-empty list of those is refused and the message names the struct.

[^plan]: Slice 4 plan, global constraints and the clear-value rule.
