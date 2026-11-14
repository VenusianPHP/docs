# Bindings

Every function, class and constant ext-glfw binds, by GLFW group; each function one GLFW call.

## Overview

Stubs = declaration; `tests/SurfaceTest.php` fails when a stub function, constant or class is missing from the build (native functions counted on their platform only).[^stubs] Names = C names. Translations: out-param → by-ref; counted list → PHP list; address/Vulkan/native handle → `int`; C `int` → `int` (GLFW_TRUE/FALSE included), converted as C converts; set-callback → returns the previous callable. Refusals: only the sites in `bindings.json` (released handle, icon pixels, icon count), each with a probe in `tests/Probes`.

| Group | Functions |
|---|---|
| Init, version, error | glfwInit, glfwTerminate, glfwInitHint, glfwGetVersion, glfwGetVersionString, glfwGetError (description by-ref, null when none), glfwSetErrorCallback, glfwGetPlatform, glfwPlatformSupported |
| Monitors | glfwGetMonitors (primary first), glfwGetPrimaryMonitor, glfwGetMonitorPos, glfwGetMonitorWorkarea, glfwGetMonitorPhysicalSize (mm), glfwGetMonitorContentScale, glfwGetMonitorName, glfwSetMonitorCallback, glfwGetVideoModes, glfwGetVideoMode, glfwSetGamma, glfwGetGammaRamp, glfwSetGammaRamp |
| Windows | glfwDefaultWindowHints, glfwWindowHint (`GLFW_ANY_POSITION` 0x80000000 converts to INT_MIN as in C), glfwWindowHintString, glfwCreateWindow (null on failure; monitor = full screen; share), glfwDestroyWindow, glfwWindowShouldClose, glfwSetWindowShouldClose, glfwGetWindowTitle, glfwSetWindowTitle, glfwSetWindowIcon (window, count, list of GLFWimage; count 0 restores), glfwGet/SetWindowPos, glfwGet/SetWindowSize, glfwSetWindowSizeLimits, glfwSetWindowAspectRatio, glfwGetFramebufferSize, glfwGetWindowFrameSize, glfwGetWindowContentScale, glfwGet/SetWindowOpacity, glfwIconifyWindow, glfwRestoreWindow, glfwMaximizeWindow, glfwShowWindow, glfwHideWindow, glfwFocusWindow, glfwRequestWindowAttention, glfwGetWindowMonitor, glfwSetWindowMonitor (monitor + mode = exclusive full screen; null = windowed), glfwGet/SetWindowAttrib |
| Window callbacks | glfwSetWindowPosCallback, …SizeCallback, …CloseCallback, …RefreshCallback, …FocusCallback, …IconifyCallback, …MaximizeCallback, glfwSetFramebufferSizeCallback, glfwSetWindowContentScaleCallback, glfwSetKeyCallback, glfwSetCharCallback, glfwSetMouseButtonCallback, glfwSetCursorPosCallback, glfwSetCursorEnterCallback, glfwSetScrollCallback — callable(GLFWwindow, …C args) or null; the C ints stay ints (action, mods, entered), the C doubles are floats. Also glfwGetKeyName(key, scancode): ?string (null where GLFW returns NULL), glfwGetCursorPos(window, ?float &$xpos, ?float &$ypos) and glfwGetKey(window, key): int (GLFW_PRESS or GLFW_RELEASE: the last state GLFW reported to the window, so a modifier already held when the window gained focus may read GLFW_RELEASE until GLFW sees its next event; a bad key sets GLFW_INVALID_ENUM and reads GLFW_RELEASE) |
| Events, time | glfwPollEvents, glfwWaitEvents, glfwWaitEventsTimeout, glfwPostEmptyEvent, glfwGetTime, glfwSetTime, glfwGetTimerValue, glfwGetTimerFrequency |
| Context | glfwMakeContextCurrent (null releases), glfwGetCurrentContext, glfwSwapBuffers, glfwSwapInterval (0 = vsync off, 1 = on), glfwExtensionSupported, glfwGetProcAddress |
| Vulkan | glfwInitVulkanLoader (vkGetInstanceProcAddr address before init; 0 = search), glfwVulkanSupported, glfwGetRequiredInstanceExtensions, glfwGetPhysicalDevicePresentationSupport, glfwGetInstanceProcAddress, glfwCreateWindowSurface (instance int, window, allocator int, surface by-ref → VkResult) |
| Native, macOS | glfwGetCocoaWindow, glfwGetCocoaView, glfwGetCocoaMonitor (CGDirectDisplayID), glfwGetNSGLContext |
| Native, Linux | glfwGetX11Display, glfwGetX11Window, glfwGetX11Adapter, glfwGetX11Monitor, glfwGetWaylandDisplay, glfwGetWaylandWindow, glfwGetWaylandMonitor, glfwGetGLXContext, glfwGetGLXWindow, glfwGetEGLDisplay, glfwGetEGLContext, glfwGetEGLSurface |

Classes: `GLFWwindow`, `GLFWmonitor` (handles); `GLFWvidmode` (width, height, redBits, greenBits, blueBits, refreshRate); `GLFWgammaramp` (red, green, blue: int lists of one length, each value cast to unsigned short); `GLFWimage` (width, height, pixels: RGBA8 string, at least 4 × w × h bytes).

Constants: every non-input `GLFW_*` of the header, and the input actions, `GLFW_KEY_*`, `GLFW_MOD_SHIFT`/`CONTROL`/`ALT`/`SUPER` and `GLFW_MOUSE_BUTTON_1`…`8`, with their header value: version, TRUE/FALSE, DONT_CARE, ANY_POSITION, error codes, window hints and attributes (incl. 3.4 POSITION_X/Y, MOUSE_PASSTHROUGH, SCALE_FRAMEBUFFER), framebuffer and context hints, client APIs, profiles, robustness, release behaviour, context creation APIs, ANGLE platform types, init hints (PLATFORM, COCOA_*, X11_XCB_VULKAN_SURFACE, WAYLAND_LIBDECOR + PREFER/DISABLE), platforms, CONNECTED/DISCONNECTED.[^header]

Not bound: the other input polling calls, cursors and cursor modes, input modes, clipboard, joysticks, gamepads, window/monitor user pointers, glfwSetWindowUserPointer (the extension does not use it either).

[^stubs]: glfw3.stub.php and glfw3native.stub.php
[^header]: GLFW 3.4 header
