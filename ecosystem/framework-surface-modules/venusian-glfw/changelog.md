# Changelog

What changed in this package, newest first.

### 2026-11-08

* **v0.11.0**, the first tagged release: `composer require jovian/venusian-glfw` (no `:0.10.x-dev`, and `venusian-surface/windows` now comes from Packagist). Requires PHP `~8.4.27||^8.5.12` (8.4.27 or newer, 8.5.12 or newer), ext-glfw ^0.11, ext-opengl ^0.11 and `venusian-surface/*` ^0.11. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-glfw/overview)
* Staged input: GLFW keys, modifiers and buttons map to Surface's staged input mail (key presses, repeats and releases, committed text, pointer moves, enter and leave, drags, presses, releases and scrolls). Lending a Metal layer on macOS works again: its view is built with a four-argument `NSRect`. On macOS ext-appkit is now required, since a press's click count and a scroll's precision come from the current NSEvent; on Linux a press is one click and a scroll is not precise. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-glfw/overview#requirements)

### 2026-10-08

* Staged windows phase 6: show-pass presents, vsync, frames in flight, HDR, hidden windows, see [architecture](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-glfw/guide/stager).

### 2026-10-08

* venusian-glfw 0.10.0: the `glfw` stager. [stager](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-glfw/guide/stager), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-glfw/runbooks/testing). Suite 15 passed on the Mac (php84, zhp; Vulkan skipped, GLFW finds no loader there), 14 on Pi Wayland, 15 on Pi X11.
