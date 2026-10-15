# Handles and callbacks

One PHP object per GLFW pointer, released when GLFW frees it; PHP callables stored per window and in globals, cut off at request end.

## Handles

`GLFW_G(boxes)`: native address → zend_object, live handles only, not refcounted. `glfw_box` answers the existing object or makes one; `fromPointer` boxes a trusted address (0 refused).[^runtime]

Release (pointer cleared, entry dropped; later use → `ValueError` "GLFWwindow has been destroyed" / "GLFWmonitor has been disconnected"):[^glfw3]

* `glfwDestroyWindow` — that window, after its callbacks are dropped.
* `glfwTerminate` — every window and monitor.
* Monitor callback with GLFW_DISCONNECTED — that monitor, after the callback ran.

Dropping the last PHP reference frees the PHP object only; the native window lives until `glfwDestroyWindow`/`glfwTerminate`.

## Callbacks

* Window: `GLFW_G(window_callbacks)` GLFWwindow* → nine zval slots; a C trampoline per callback type looks the slot up and calls it with `(GLFWwindow, …args)`. Setting null clears the slot and the GLFW callback.[^glfw3]
* Error, monitor: one zval each in globals.
* A callback does not run while an exception is pending; an exception thrown inside one surfaces from the GLFW call that dispatched it (Cocoa resizes synchronously: from `glfwSetWindowSize`; elsewhere from the event pump).
* RSHUTDOWN: GLFW told to stop calling (error, monitor, every window's nine), then callables freed.[^runtime]

[^runtime]: Handle table and callback storage
[^glfw3]: Trampolines and release points
