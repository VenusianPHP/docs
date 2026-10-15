# Changelog

What changed in this package, newest first.

### 2026-10-09

* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.

### 2026-10-08

Bound pad identity and player lights for HumanInput slice 18b: `SDL_GetGamepadSerial`, `SDL_GetJoystickSerial`, `SDL_GetGamepadPath`, `SDL_GetJoystickPath`, `SDL_Get/SetGamepadPlayerIndex`, `SDL_Get/SetJoystickPlayerIndex`. A virtual device has neither serial nor path. Measured: on the Pi without /dev/hidraw access SDL reads a DualSense through evdev with no serial; its path is the /dev/input/event node. Suite: Mac NTS and ZTS 81 passed, 2 skipped; Pi 78 passed, 5 skipped (after the path bindings too).

Bound input for HumanInput's sdl3 engine: keyboard, text and mouse events both ways with `SDL_PushEvent`, event switches, `SDL_QuitSubSystem`, keyboard focus and text input, scancodes, gamepads, joysticks and virtual joysticks with counted opens. Measured: SDL keeps a pushed text event's pointer, so the binding keeps the bytes; every `SDL_UpdateGamepads()` queues a `JOYSTICK_UPDATE_COMPLETE` even with gamepad and joystick events off, and only `SDL_SetEventEnabled` over 0x600–0x6FF stops them. Suite: Mac NTS and ZTS 78 passed, 2 skipped; Pi 75 passed, 5 skipped. Review fixes: a gamepad-only quit releases `SDL_Gamepad` handles, and a poll into an unset part throws instead of crashing (80 passed on the Mac).

GPU swapchain pacing: wait for a swapchain, wait-and-acquire, frames in flight, composition support. Suite: Homebrew PHP 8.4 NTS and ZTS 60 passed, 2 skipped; Pi 57 passed, 5 skipped under Wayland and X11.

Bound what a staged window needs from SDL 3.2, input excluded: window position, size limits, aspect ratio, safe area, border sizes, maximize/minimize/restore/sync, border/resize/stacking/focus toggles, opacity, icon, flash, PHP hit tests, screen saver, the simple message box; displays, display modes, orientation, content scale, display lookup, borderless and exclusive fullscreen; HDR and native-handle properties with string/float/boolean property access; window surface rects, surface lifetime and surface vsync; the GL swap interval getter and the GPU present-mode query; `SDL_DisplayEvent` and the remaining window and display event types; `SDL_ClearError`, `SDL_EGL_GetCurrentDisplay`. Every new symbol is in the distro SDL 3.2.10 headers. The suite is 59 passed, 2 skipped, 1097 assertions on Homebrew PHP 8.4 NTS and ZTS, and 56 passed, 5 skipped on the Pi under both Wayland and X11 (runtime SDL 3.2.10). Hit-test clicks and dialog dismissal are driven through AppKit on the Mac only.

### 2026-10-04

Created the bundle for 0.10.0. The extension binds SDL 3.2: core and events, windows and properties, surfaces and memory streams, the GL, Metal and Vulkan hooks, and SDL_GPU through blit. The suite is 28 passed, 1 skipped, 622 assertions on Homebrew PHP 8.4 NTS and ZTS, and 28 passed, 1 skipped, 618 assertions on the Pi (distro SDL 3.2.10, Vulkan). The skipped test is Vulkan instance extensions on the Mac and the Metal view on the Pi. The gate's stencil-then-cover triangle, resolved from 4 samples and blitted, reads back the same on Metal and on V3DV, with the hypotenuse neither solid red nor solid clear.
