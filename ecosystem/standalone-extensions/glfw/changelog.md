# Changelog

What changed in this package, newest first.

### 2026-10-09

* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.

### 2026-10-08

* Bundle created with ext-glfw 0.10.0: plain C, GLFW 3.4, input excluded. 83 functions plus 4 native on macOS (Cocoa, NSGL) or 12 on Linux (X11, Wayland, GLX, EGL), 5 classes, every non-input constant. Suite 57 tests: macOS NTS + ZTS (55 passed, 2 Linux-only skipped), Pi 5 ZTS under labwc Wayland (53 passed, 4 skipped). [bindings](/docs/{{version}}/ecosystem/standalone-extensions/glfw/api/bindings), [handles and callbacks](/docs/{{version}}/ecosystem/standalone-extensions/glfw/architecture/handles-and-callbacks), [platform facts](/docs/{{version}}/ecosystem/standalone-extensions/glfw/architecture/platform-facts), [build](/docs/{{version}}/ecosystem/standalone-extensions/glfw/runbooks/build-install-test), [adding a binding](/docs/{{version}}/ecosystem/standalone-extensions/glfw/runbooks/adding-a-binding).
