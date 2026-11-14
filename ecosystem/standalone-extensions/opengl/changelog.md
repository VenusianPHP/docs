# Changelog

What changed in this package, newest first.

### 2026-11-06

* **ext-guard**: enrolled; `bindings.json` holds six refusal sites, each with a probe in `tests/Probes` run on a `--enable-opengl-probes` build (`OPENGL_PROBE_OFF=<site>` turns one off): `opengl-no-context` (macOS), `opengl-attrib-terminator` (CGL), `opengl-bytes-length`, `opengl-null-address`, `opengl-list-count`, `opengl-wl-null-window` (Linux). The over-read probes run the crash under libgmalloc on macOS. [Data](/docs/{{version}}/ecosystem/standalone-extensions/opengl/architecture/data).
* **Dropped refusals**, none of which crashed with the check off on macOS or Linux (x86_64 Ubuntu 24.04, Mesa): released handles, 32-bit and ≥ 0 ranges, negative `glGen*` counts and `eglChooseConfig` size, the `glClientWaitSync` timeout, `wl_egl_window_create` sizes and surface 0, an empty `CGLSetParameter` list, the damage extension string, an unterminated EGL attribute list, the format/type pairs the old table could not size (the table is now complete; GL refuses the rest without reading). The no-context check is macOS only.
* **API, 1:1**: counts are their own parameters (`glDelete*`, `glDrawBuffers`, `glShaderSource` with its `$length`, `glUniformMatrix4fv`, `eglSwapBuffersWithDamageKHR`); `glGen*` and the info logs write by reference; `glReadPixels` writes to an address only (the string mode is gone); `CGLDestroyPixelFormat` returns its `CGLError`, `CGLErrorString` `?string`; `pointer()` is 0 once released, `fromPointer` `?static`; `EGL_DEFAULT_DISPLAY` removed (a pointer cast in C); `eglGetPlatformDisplay` attributes are full `EGLAttrib`; releasing the current context makes no extra call.
* **Fix**: `glGetIntegerv` wrote into a 4-int stack array; Mesa's `GL_COMPRESSED_TEXTURE_FORMATS` (66) smashed the stack. It is sized from the state tables now and returns every value.
* Homebrew PHP 8.4 NTS and ZTS: 61 passed, 8 skipped (Linux only), probe build included. x86_64 PHP 8.4 NTS, surfaceless EGL: 59 passed, 9 skipped. Not run: the Wayland window tests and the Pi.

### 2026-10-28

* **Version**: 0.11.0 in `PHP_OPENGL_VERSION` (`php_opengl.h`); `branch-alias` `dev-main` is `0.11.x-dev`. Promoted with the Venusian 0.11 ecosystem. No API or behaviour change.
* **Coverage**: `scripts/support.php` writes `SUPPORT.md` and the README's API badge over the floors: OpenGL 4.1 core profile, OpenGL ES 2.0 / 3.0, EGL 1.0–1.5 from the Khronos registries, plus every CGL function of the macOS SDK's OpenGL.framework headers. Extensions are not counted. `--check` exits 1 when the list or badge is stale. 115 / 579 (19.9%).

### 2026-10-09

* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.

### 2026-10-08

EGL window surfaces (`eglCreateWindowSurface`, `wl_egl_window_create/resize/destroy`, wayland-egl now required on Linux), `eglGetConfigAttrib`, `eglSurfaceAttrib`, the colour-space / SMPTE 2086 / CTA 861.3 / float-config constants, `GL_RGBA16F`, `GL_HALF_FLOAT`, `GL_RGB10_A2`, `GL_UNSIGNED_INT_2_10_10_10_REV`; strings sized for half-float and 10-bit pixels. Pi 5 Mesa (labwc) lists `EGL_KHR_gl_colorspace` and `EGL_EXT_pixel_format_float` only: no scRGB, PQ or P3 colour space. Its configs come deepest first (10, 8, 16 bit), and only 8-bit ones take a colour-space attribute; it accepts SMPTE 2086 attributes without listing the extension. Suite: Pi 30 passed; php84/zhp 25 passed, 5 skipped.

EGL swap interval, surface queries, and the swap with damage (`EGL_KHR_swap_buffers_with_damage`, present on the Pi's Mesa through a Wayland EGL window). Creating a GLFW window releases the thread's current context: the test restores the one taken before. Suite: Pi 26 passed; Homebrew PHP 8.4 NTS and ZTS 24 passed, 2 skipped (EGL is the Linux build).

### 2026-10-04

Created the bundle for 0.10.0. The extension binds the shared OpenGL 4.1 core / OpenGL ES 3 calls, CGL on macOS, and EGL on Linux. The suite is 21 tests: 271 assertions on Homebrew PHP 8.4 NTS and ZTS, 298 assertions on the Pi (the EGL stub declares more constants than the CGL stub). Gate: stencil-then-cover triangle, 4× MSAA, blit resolve, read back, on CGL and on surfaceless EGL. The hypotenuse is neither solid colour on either. GLES rejects `GL_RGB` into a `GL_RGBA8` texture; the sizing test drains that error.

### 2026-10-05

Added `eglGetCurrentDisplay()`, `eglGetCurrentSurface()`, `EGL_DRAW` and `EGL_READ`: a caller that switches contexts puts back the display and surfaces with the context. Suite 22 tests on the Mac and the Pi (307 assertions there).

Added the four pixel-store skip constants. Strings for uploads and reads are sized with the skips: a skip left by another caller made `glReadPixels` write past a string sized without them. Suite 23 tests on Homebrew PHP 8.4 NTS and ZTS and the Pi.

### 2026-10-06

Added `GL_DRAW_FRAMEBUFFER_BINDING` and `GL_READ_FRAMEBUFFER_BINDING`: a caller reads which framebuffer a toolkit bound before its render callback. Suite 24 tests on the Mac and the Pi.
