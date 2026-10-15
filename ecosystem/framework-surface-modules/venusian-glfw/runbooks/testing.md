# Testing

Real windows on the Mac (php84, zhp) and the Pi (Wayland, X11); temporary path repositories for Surface's splits and venusian-vulkan.

## Steps

* `tests/Pest.php` fails with a message without ext-glfw and ext-opengl. `stager()` is one driver for the process; `GLFW_TEST_PLATFORM` (`cocoa`, `wayland`, `x11`) picks GLFW's platform.
* `venusian-surface/windows` is not on Packagist, and jovian/venusian-vulkan has no 0.10 release there (its `0.10.x` branch is still the 0.8 package): add path repositories to `<surface>/src/Surface/*` and `../venusian-vulkan` for the run, `composer update`. The other Surface splits (`bridge`, `contracts`, `drawing`, `framebuffers`, `human-input`) are tagged v0.10.0 on Packagist.
* Mac: `php84 -d memory_limit=128M vendor/bin/pest`, then `zhp`. The Vulkan lend skips where GLFW finds no Vulkan loader.
* Pi: copy this package, the Surface checkout and venusian-vulkan without `vendor/`, `.git` and locks (`tar` piped into `fnk`) to the same relative paths; then `WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 GLFW_TEST_PLATFORM=wayland php -d memory_limit=128M vendor/bin/pest`, and with `DISPLAY=:0 GLFW_TEST_PLATFORM=x11`.
* The suite shows windows, goes full screen and switches display modes: announce it before a run.
* After: remove `vendor/`, `composer.lock` and the repository entries; `composer.json` carries none.
