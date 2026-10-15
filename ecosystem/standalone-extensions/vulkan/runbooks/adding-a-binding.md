# Adding a binding

Where a new Vulkan function, struct, or constant goes.

## Steps

1. Add the function, struct, or constant to the stub for its group (`stubs/vk_*.stub.php`). A handle class is `final`, `@not-serializable`, with a private `__construct`, `pointer()`, and `fromPointer()`. A struct class is `final` and `@not-serializable`, with public typed properties named as the C members. `sType` is not a property. A by-value nested struct is created in `__construct`.
2. Regenerate arginfo: `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs`. Commit the stub and the `*_arginfo.h`. Do not hand-edit the arginfo.
3. Include that one arginfo header from the `.c` that implements the functions. A second arginfo in the same file collides on `ext_functions`.
4. Add `vk_<Struct>_from` and `vk_<Struct>_to`, and a row in the `pNext` kind table in `src/structs.c`, if the struct can be chained or nested. Declare the class entry in `src/structs.h` and define it in `src/structs.c`.
5. Parent a new handle on the object whose destroy should release it. Call `vulkan_release_tree` after the native destroy.
6. Add the `.c` to `VULKAN_SOURCES` in `config.m4`. `vk_metal.c` is darwin only, behind `-DVK_USE_PLATFORM_METAL_EXT`.
7. `tests/SurfaceTest.php` fails if a stub declaration is missing from the loaded extension. Add a Pest test that drives the new call on the Pi. Device tests call `gpu()`, which skips on macOS.
8. New constants: add the enum type to the list in `tools/vk-constants.php` and regenerate from the Pi header and the Mac header.
