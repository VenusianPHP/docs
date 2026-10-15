# Platform facts

What each windowing system leaves out, as GLFW 3.4 reports it, measured on macOS (Cocoa) and a Pi 5 under labwc (Wayland).

## Wayland (Pi 5, labwc)

* Window position (get/set/hint), opacity, icon, monitor gamma → `GLFW_FEATURE_UNAVAILABLE`; position reads 0,0; opacity reads 1.0; gamma ramp null.[^tests]
* Iconify: request sent, never reported (attribute stays 0, no callback).
* Size set by the program: applied, not called back. Compositor-set sizes (maximize) call back size + framebuffer.
* Leaving full screen: compositor picks the windowed size. Frame size reads 0 (compositor decorates).
* Focus: compositor gives it on user input; `glfwFocusWindow` raises no error but may not focus.
* GL: default context GL 3.1 over EGL (V3D); 3.3+ refused. `glfwGetProcAddress` may answer a stub for unknown names.
* libdecor GTK 3 plugin + GTK 4 (ext-gtk) in one process → deadlock in `glfwShowWindow` (GTK 3 type init). Mitigation: `glfwInitHint(GLFW_WAYLAND_LIBDECOR, GLFW_WAYLAND_DISABLE_LIBDECOR)` before init, or no ext-gtk in that process.

## Cocoa (macOS)

* Window icon → `GLFW_FEATURE_UNAVAILABLE`.
* Current video mode in points (1800×1169 on a scaled Retina panel); `glfwGetVideoModes` lists pixel modes, so the current one is not in the list.
* `GLFW_POSITION_Y` hint counted from the screen's bottom (3.4.0); `glfwSetWindowPos` correct.
* Size limits / aspect bind the user's resizing; programmatic `glfwSetWindowSize` ignores them (as AppKit). Read back through ext-appkit `contentMinSize`/`contentMaxSize`/`contentAspectRatio`.
* Resizes call back synchronously, inside `glfwSetWindowSize`.
* Focus: macOS refuses activation while the user works in another app.
* Vulkan: Homebrew's loader is not on dyld's path; `glfwInitVulkanLoader(vkGetInstanceProcAddr)` before init. ext-vulkan exports no such address yet; tests take it with FFI from `vk_loader_path()`.

[^tests]: Pest suite, platform branches
