# Overview

![CI](https://github.com/php-io-extensions/glfw/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/glfw/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/glfw/actions/workflows/ci.yml)

1:1 PHP bindings of GLFW 3.4 for staged windows: initialization and errors, monitors, video modes and gamma, windows with their hints, attributes and callbacks, events and time, OpenGL contexts, Vulkan surfaces, and native handles. Version 0.11.0. Linux and macOS.

Input is not bound: no keyboard, mouse, cursor, joystick or gamepad functions. Function and constant names are the C names. A handle is one PHP object per native pointer. Dropping the last PHP reference does not destroy the native object.

## Requirements

- GLFW 3.4 or newer
- PHP 8.4, NTS or ZTS
- macOS: `brew install glfw`
- Debian trixie and Raspberry Pi OS: `apt install libglfw3-dev`
- `venusian build` reads the system packages from `extra.venusian.system` in composer.json: apt packages to build with and the run-time ones a `.deb` depends on or recommends, and the Homebrew ones.

No Vulkan, X11, Wayland, GLX or EGL headers are needed to build: the extension declares the few Vulkan types and native-access functions it uses with ABI-identical types.

## Install

Through PIE:

```bash
pie install php-io-extensions/glfw
```

From a checkout:

```bash
./install-macos.sh              # Homebrew php@8.4 and php@8.4-zts
./install-debian-trixie.sh      # Debian trixie / Raspberry Pi OS
```

The macOS installer ad-hoc signs the `.so` and writes `30-glfw.ini`, unless an ini in that PHP's scan directory already loads `glfw`. Pass other PHP binaries as arguments to install those instead.

## Names

Bindings are the C API with these translations:

- An out-parameter is a by-reference parameter (`glfwGetWindowSize($window, $width, $height)`).
- A `GLFWwindow *` or `GLFWmonitor *` is a `GLFWwindow` or `GLFWmonitor` handle; `NULL` is `null`.
- A `const GLFWvidmode *` GLFW returns is a copied `GLFWvidmode`. A list GLFW returns with a count (`glfwGetMonitors`, `glfwGetVideoModes`, `glfwGetRequiredInstanceExtensions`) is a PHP list.
- `GLFWgammaramp` holds three lists of 16-bit ints. `GLFWimage` holds RGBA8 pixels as a string of 4 × width × height bytes; `glfwSetWindowIcon` takes a list of them.
- A function address, a Vulkan handle, or a native handle is an `int`.
- A callback is a PHP callable or `null`, called directly from GLFW with the C arguments, a `GLFWwindow` first.
- A C `int` that GLFW uses as a boolean in a return (`glfwInit`, `glfwWindowShouldClose`, `glfwVulkanSupported`) is `bool`. Hints and attributes stay `int` (`GLFW_TRUE`, `GLFW_FALSE`, `GLFW_DONT_CARE`).

Failure is `glfwGetError()` or the error callback, as in C. Constants are PHP constants under their C names, with the values of the GLFW header.

## Windows for a game engine

```php
glfwInit();
glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);           // Metal, Vulkan or a CPU blit draws it
$window = glfwCreateWindow(1280, 720, 'Game');
glfwSetWindowSizeLimits($window, 640, 360, GLFW_DONT_CARE, GLFW_DONT_CARE);
glfwSetWindowAspectRatio($window, 16, 9);
glfwSetFramebufferSizeCallback($window, function (GLFWwindow $w, int $width, int $height): void {
    // resize the swapchain to the pixels
});

// Exclusive full screen in the monitor's current mode, and back to a window.
$monitor = glfwGetPrimaryMonitor();
$mode = glfwGetVideoMode($monitor);
glfwSetWindowMonitor($window, $monitor, 0, 0, $mode->width, $mode->height, $mode->refreshRate);
glfwSetWindowMonitor($window, null, 100, 100, 1280, 720, GLFW_DONT_CARE);

// Borderless, always on top, click-through.
glfwSetWindowAttrib($window, GLFW_DECORATED, GLFW_FALSE);
glfwSetWindowAttrib($window, GLFW_FLOATING, GLFW_TRUE);
glfwSetWindowAttrib($window, GLFW_MOUSE_PASSTHROUGH, GLFW_TRUE);

while (! glfwWindowShouldClose($window)) {
    glfwWaitEventsTimeout(1 / 60);
}
glfwDestroyWindow($window);
glfwTerminate();
```

An OpenGL window turns vsync off and on with `glfwSwapInterval(0)` and `glfwSwapInterval(1)` while its context is current.

## Vulkan

Instances, physical devices and surfaces are their handle values as ints, so ext-vulkan's handles pass through `pointer()` and `fromPointer()`:

```php
$result = glfwCreateWindowSurface($instance->pointer(), $window, 0, $surface);
$vkSurface = VkSurfaceKHR::fromPointer($surface);
```

GLFW finds the Vulkan loader on the dynamic linker's path. Homebrew's loader on macOS is not on it; hand GLFW its `vkGetInstanceProcAddr` before `glfwInit()` with `glfwInitVulkanLoader($address)`.

## Native handles

`glfwGetCocoaWindow`, `glfwGetCocoaView`, `glfwGetCocoaMonitor` and `glfwGetNSGLContext` on macOS; `glfwGetX11*`, `glfwGetWayland*`, `glfwGetGLX*` and `glfwGetEGL*` on Linux. Each answers an address or an id, for another extension to adopt (`NSWindow::fromPointer(glfwGetCocoaWindow($window))`).

## Platform differences

GLFW's own, reported through `glfwGetError()`:

- **Wayland** gives the window's position, opacity and icon, and the monitor's gamma, to the compositor: those calls fail with `GLFW_FEATURE_UNAVAILABLE`. A client is never told it was iconified. A size the program sets is not called back; sizes the compositor sets are. The compositor picks the windowed size after full screen and draws the decorations, so the frame size reads as 0.
- **Wayland decorations** come from libdecor's GTK 3 plugin by default. In a process that has also loaded GTK 4 (ext-gtk), GTK 3's type registration deadlocks in `glfwShowWindow`; set `glfwInitHint(GLFW_WAYLAND_LIBDECOR, GLFW_WAYLAND_DISABLE_LIBDECOR)` before `glfwInit()` there.
- **macOS** has no window icon (`GLFW_FEATURE_UNAVAILABLE`), reports the current video mode in points and lists modes in pixels, and counts `GLFW_POSITION_Y` from the screen's bottom in GLFW 3.4.0.
- **Focus** is granted by the window manager: macOS refuses activation while the user works in another app, and Wayland compositors give focus on user input.

## Tests

```bash
composer install
php -d memory_limit=128M vendor/bin/pest
```

On a Linux desktop session over SSH, export `WAYLAND_DISPLAY`, `DISPLAY` and `XDG_RUNTIME_DIR` first.

## License

MIT
