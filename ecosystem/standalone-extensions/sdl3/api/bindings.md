# Bindings

SDL 3.2 functions, handles, structs and constants bound by this extension, grouped as the slice plan's tasks.

## Overview

Every name below is the C name. Constants are `@cvalue` from the SDL headers.[^stubs]

## Core and events

`SDL_Init`, `SDL_InitSubSystem`, `SDL_QuitSubSystem`, `SDL_Quit`, `SDL_GetError`, `SDL_ClearError`, `SDL_GetVersion`, `SDL_SetHint`, `SDL_PumpEvents`, `SDL_PollEvent`, `SDL_WaitEventTimeout`, `SDL_PushEvent`, `SDL_SetEventEnabled`, `SDL_EventEnabled`. A null event to `SDL_PollEvent` or `SDL_WaitEventTimeout` leaves the event queued. Structs `SDL_Event`, `SDL_WindowEvent`, `SDL_DisplayEvent` (`SDL_Event::$display`, written for `SDL_EVENT_DISPLAY_FIRST`..`LAST`), `SDL_KeyboardEvent`, `SDL_TextInputEvent`, `SDL_MouseMotionEvent`, `SDL_MouseButtonEvent`, `SDL_MouseWheelEvent` (no `integer_x`/`integer_y`, which are 3.4) as `SDL_Event::$key/$text/$motion/$button/$wheel`. Polling writes only the part its type names. A pushed text event's text is copied and kept until SDL quits its events or the request ends, since SDL keeps the pointer (measured). Constants `SDL_INIT_VIDEO`, `SDL_EVENT_QUIT`, every `SDL_EVENT_WINDOW_*`, every `SDL_EVENT_DISPLAY_*`, the first/last bounds of both ranges, `SDL_EVENT_KEY_DOWN`/`UP`, `SDL_EVENT_TEXT_INPUT`, `SDL_EVENT_MOUSE_MOTION`, `SDL_EVENT_MOUSE_BUTTON_DOWN`/`UP`, `SDL_EVENT_MOUSE_WHEEL`, `SDL_EVENT_JOYSTICK_AXIS_MOTION`, `SDL_EVENT_JOYSTICK_UPDATE_COMPLETE`, `SDL_EVENT_GAMEPAD_ADDED`, `SDL_EVENT_GAMEPAD_AXIS_MOTION`, `SDL_EVENT_FINGER_DOWN`, `SDL_BUTTON_*`, `SDL_MOUSEWHEEL_*`, `SDL_KMOD_*`, `SDL_HINT_VIDEO_DRIVER`, `SDL_HINT_VIDEO_MAC_FULLSCREEN_SPACES`, `SDL_HINT_VIDEO_MINIMIZE_ON_FOCUS_LOSS`, `SDL_HINT_VIDEO_FORCE_EGL`.

## Keyboard, gamepads and joysticks

`SDL_GetKeyboardFocus`, `SDL_StartTextInput`, `SDL_StopTextInput`, `SDL_TextInputActive`. Handles `SDL_Gamepad` and `SDL_Joystick` count their opens: SDL hands back the same pointer for a device opened again, and the PHP handle is released at the last close, or when its subsystem goes down (`SDL_QuitSubSystem`, `SDL_Quit`): gamepad for `SDL_Gamepad`, joystick for `SDL_Joystick`. A poll into an `SDL_Event` whose part PHP code unset throws. Gamepad: list, is-gamepad, open, close, name, id, button, axis, update. Joystick: list, open, close, name, axis/button/hat counts and reads, update. Virtual joysticks (`SDL_VirtualJoystickDesc`: type, vendor and product ids, axis/button/hat counts, masks, name; version set by the binding; balls, touchpads, sensors and callbacks not bound), attach, detach, and virtual axis/button/hat sets: suites test pads without hardware. A `SDL_JOYSTICK_TYPE_GAMEPAD` device with masks 0 maps button and axis *i* to the gamepad's *i* (measured). A gamepad trigger reads its raw −32768…32767 as 0…32767, and a virtual trigger rests at −32768 (measured). Constants: `SDL_INIT_JOYSTICK`, `SDL_INIT_GAMEPAD`, `SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS`, the 15 `SDL_GAMEPAD_BUTTON_*`, the 6 `SDL_GAMEPAD_AXIS_*`, `SDL_HAT_*`, `SDL_JOYSTICK_TYPE_UNKNOWN`/`GAMEPAD`, `SDL_JOYSTICK_AXIS_MIN`/`MAX`, and the 106 `SDL_SCANCODE_*` a keyboard map needs (letters, digits, F1–F12, arrows, editing keys, modifiers, punctuation, keypad, print screen, scroll lock, pause, num lock, application, clear).

## Windows and properties

Handle `SDL_Window`. `SDL_CreateWindow`, `SDL_CreateWindowWithProperties`, `SDL_DestroyWindow`, id lookup, title, size in points and in pixels, pixel density, display scale, show, hide, raise, flags, window properties. `SDL_CreateProperties`, `SDL_DestroyProperties`, and the set/get calls for pointer, number, string, and boolean. `SDL_GetStringProperty`, `SDL_GetFloatProperty`, `SDL_SetFloatProperty`, `SDL_GetBooleanProperty`. Window flags `SDL_WINDOW_*` except the mouse/keyboard grab, mouse focus/capture, tooltip and popup-menu flags. The `SDL_PROP_WINDOW_CREATE_*` strings: title, position, size, the graphics API booleans, hidden, resizable, borderless, always-on-top, focusable, maximized, minimized, fullscreen, transparent, utility, external graphics context, the Cocoa window and view, the Wayland surface, the X11 window. The window's own properties: HDR enabled, SDR white level, HDR headroom, the Cocoa window and Metal view tag, the X11 display, screen and window, the Wayland display and surface. `SDL_PROP_DISPLAY_HDR_ENABLED_BOOLEAN`.

## Window state

`SDL_SetWindowSize`, `SDL_SetWindowPosition`, `SDL_GetWindowPosition`, minimum and maximum size set/get, aspect ratio set/get, `SDL_GetWindowBordersSize`, `SDL_GetWindowSafeArea`. `SDL_MaximizeWindow`, `SDL_MinimizeWindow`, `SDL_RestoreWindow`, `SDL_SyncWindow`. `SDL_SetWindowResizable`, `SDL_SetWindowBordered`, `SDL_SetWindowAlwaysOnTop`, `SDL_SetWindowFocusable`, opacity set/get, `SDL_SetWindowIcon`, `SDL_FlashWindow` with `SDL_FLASH_*`. `SDL_SetWindowHitTest` with `SDL_HITTEST_*`. `SDL_ScreenSaverEnabled`, `SDL_EnableScreenSaver`, `SDL_DisableScreenSaver`. `SDL_WINDOWPOS_UNDEFINED`, `SDL_WINDOWPOS_CENTERED` and their masks. `SDL_ShowSimpleMessageBox` with the `SDL_MESSAGEBOX_*` dialog and button-order flags.

Measured driver behaviour: Wayland refuses `SDL_SetWindowPosition` ("wayland cannot position non-popup windows"), accepts always-on-top and not-focusable after creation without setting their flags, and emulates an exclusive mode by sizing the window to it while the display mode stays put. Cocoa and Wayland answer "That operation is not supported" for `SDL_GetWindowBordersSize`. X11 applies a resize to a mapped window, and each min/max/aspect call re-applies the size the window last committed.

## Displays and fullscreen

Struct `SDL_DisplayMode` (a copy; SDL's driver data is not carried, and SDL matches a mode passed back in by its public fields). Struct `SDL_Point`. `SDL_GetCurrentVideoDriver`, `SDL_GetDisplays`, `SDL_GetPrimaryDisplay`, `SDL_GetDisplayProperties`, `SDL_GetDisplayName`, `SDL_GetDisplayBounds`, `SDL_GetDisplayUsableBounds`, natural and current orientation with `SDL_ORIENTATION_*`, `SDL_GetDisplayContentScale`, `SDL_GetFullscreenDisplayModes`, `SDL_GetClosestFullscreenDisplayMode`, desktop and current display mode, `SDL_GetDisplayForPoint`, `SDL_GetDisplayForRect`, `SDL_GetDisplayForWindow`. `SDL_SetWindowFullscreenMode` (null for borderless desktop, a mode for exclusive), `SDL_GetWindowFullscreenMode`, `SDL_SetWindowFullscreen`.

## Surfaces and streams

Handles `SDL_IOStream`, `SDL_Surface`. Struct `SDL_Rect`. `SDL_IOFromMem`, `SDL_IOFromConstMem`, `SDL_ReadIO`, `SDL_WriteIO`, `SDL_CloseIO`. `SDL_GetWindowSurface`, `SDL_UpdateWindowSurface`, `SDL_UpdateWindowSurfaceRects`, `SDL_WindowHasSurface`, `SDL_DestroyWindowSurface`, `SDL_SetWindowSurfaceVSync` and `SDL_GetWindowSurfaceVSync` with `SDL_WINDOW_SURFACE_VSYNC_DISABLED`/`ADAPTIVE`, `SDL_CreateSurfaceFrom`, `SDL_DestroySurface`, `SDL_BlitSurface`, `SDL_BlitSurfaceScaled`, `SDL_FillSurfaceRect`. `SDL_PIXELFORMAT_RGBA32`, `SDL_PIXELFORMAT_BGRA32`, `SDL_SCALEMODE_NEAREST`, `SDL_SCALEMODE_LINEAR`.

`SDL_MapGPUTransferBuffer` returns the address. These stream calls are how bytes move.

## GL, Metal, Vulkan

Handles `SDL_GLContext`, `SDL_MetalView`. Attribute, context, swap, swap interval set/get, and destroy for GL; `SDL_EGL_GetCurrentDisplay` (the EGLDisplay address, null off EGL). `SDL_Metal_CreateView`, `SDL_Metal_GetLayer` (the `CAMetalLayer` address), `SDL_Metal_DestroyView`. `SDL_Vulkan_GetInstanceExtensions`, `SDL_Vulkan_CreateSurface`, `SDL_Vulkan_DestroySurface`. The `SDL_GL_*` attribute and profile constants.

## SDL_GPU types

Handles named by the structs: `SDL_GPUShader`, `SDL_GPUTexture`, `SDL_GPUBuffer`, `SDL_GPUTransferBuffer`, `SDL_GPUSampler`. Every struct in the slice plan's task 5 table, fields as SDL 3.2 names them. The `SDL_GPU_*` constants those calls and structs take, including every texture format in the 3.2 header, plus `SDL_FLIP_NONE`.

## SDL_GPU device and passes

Handles `SDL_GPUDevice`, `SDL_GPUCommandBuffer`, `SDL_GPUCopyPass`, `SDL_GPUFence`, `SDL_GPUGraphicsPipeline`, `SDL_GPURenderPass`. Device, texture, sampler, buffer, transfer buffer, shader, and pipeline create/release. Map and unmap. Command buffers, fences, idle. Copy, render, and blit. Swapchain claim, `SDL_WindowSupportsGPUPresentMode`, `SDL_WindowSupportsGPUSwapchainComposition`, parameters, format, acquire and `SDL_WaitAndAcquireGPUSwapchainTexture`, `SDL_WaitForGPUSwapchain`, `SDL_SetGPUAllowedFramesInFlight` (range checked only in SDL's GPU debug mode, measured).

[^stubs]: `stubs/*.stub.php`
