# Overview

![CI](https://github.com/php-io-extensions/open-gl/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/open-gl/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/open-gl/actions/workflows/ci.yml)
[![OpenGL API](https://img.shields.io/badge/OpenGL_API-19.9%25_%28115%2F579%29-blue?style=flat-square)](https://github.com/php-io-extensions/open-gl/blob/v0.11.1/SUPPORT.md)

1:1 PHP bindings of the OpenGL 4.1 core calls and the OpenGL ES 3 calls both
dialects share, plus the context API that makes an offscreen context possible:
CGL on macOS, EGL on Linux. Written in C against the Zend API. PHP 8.4+, NTS
and ZTS.

An OpenGL context cannot exist without CGL or EGL, and the bytes path needs an
offscreen context, so those APIs ride in this extension. `gl*` functions are
global PHP functions under their C names. Object names (`GLuint`) are plain
ints. Constants are PHP constants under their C names, values taken from the
headers. CGL handles, EGL handles, and `GLsync` are final classes.

## Requirements

- macOS: OpenGL 4.1, deprecated by Apple, present in SDK 15.4. The build
  defines `GL_SILENCE_DEPRECATION` and links `OpenGL.framework`.
- Linux: `libegl-dev` and `libgles-dev` (EGL 1.5 and GLESv2). The Pi measured
  here is Mesa 26.2, EGL 1.5, OpenGL ES 3.1 on V3D 7.1, `GL_MAX_SAMPLES` 4.

## Install

Through PIE:

```bash
pie install php-io-extensions/open-gl
```

From a checkout of this package:

```bash
./install-macos.sh            # Homebrew php@8.4 and php@8.4-zts, or pass PHP binaries
./install-debian-trixie.sh    # Debian trixie, Raspberry Pi OS
```

## Translations

Bindings are 1:1. There are no defaults and no composites. The only translations:

- A list GL takes with a count keeps the count as its own parameter: `glShaderSource($shader, $count, $string, $length)`, `glDeleteBuffers($n, $buffers)`, `glDrawBuffers($n, $bufs)`, `glUniformMatrix4fv($location, $count, $transpose, $value)` (16 floats a matrix), `eglSwapBuffersWithDamageKHR($dpy, $surface, $rects, $n_rects)`. A count past the list is a `ValueError`.
- An out-parameter is a by-reference parameter: `glGenBuffers($n, $buffers)` writes the list of names; `glGetShaderInfoLog($shader, $bufSize, $length, $infoLog)` writes at most `$bufSize` bytes, its NUL included.
- A `const void *` data argument is `string|int|null`: bytes, an address, or NULL (null and 0).
- A `void *` destination is `?int`: an address, or an offset into the bound buffer object.
- A pointer GL reads as a buffer offset (`glVertexAttribPointer`, `glDrawElements`) is an `int`.
- A C int converts as C converts it; a list element of `glUniformMatrix4fv` as PHP's `(float)`, of `glShaderSource` as PHP converts a value to a string.
- `GLboolean` and `EGLBoolean` are `bool`.
- `EGL_DEFAULT_DISPLAY` is not a constant: the C macro is a pointer cast. Pass `null` or `0`.

Handles: `pointer()` is 0 once released, `fromPointer(0)` is `null`. A released handle goes to CGL, EGL or GL as NULL, which they answer with an error.

## Refusals

The extension declines a call only where making it crashes the process. Each site has a probe in `tests/Probes` that shows the crash with the site off, on a probe build (`OPENGL_CONFIGURE="--enable-opengl-probes" ./install-macos.sh`, env `OPENGL_PROBE_OFF=<site>`):

- `opengl-no-context` (macOS): a `gl*` call with no current context is an `Error`. Apple's GL dereferences the current context. Linux's libglvnd answers such a call with nothing, so there is no check there.
- `opengl-attrib-terminator`: a CGL attribute list that does not end with 0. EGL lists go to EGL as given.
- `opengl-bytes-length`: a string shorter than what GL reads. For buffers that is `$size`. For `glTexImage2D` and `glTexSubImage2D` it comes from the width, height, format and type (the GL 4.1 and ES 3.0 pixel tables) and the unpack state: row length is `GL_UNPACK_ROW_LENGTH` or the width, the stride is that times the pixel rounded up to `GL_UNPACK_ALIGNMENT`, and the size is `skip rows × stride + skip pixels × pixel + stride × (height − 1) + width × pixel`. A format/type pair outside the tables goes to GL, which refuses it without reading.
- `opengl-null-address`: address 0 to `glBufferSubData`, or to `glTexSubImage2D` / `glReadPixels` with no pixel buffer bound. `glBufferData` and `glTexImage2D` take NULL.
- `opengl-list-count`: a count past its list.
- `opengl-wl-null-window` (Linux): `wl_egl_window_resize` or `wl_egl_window_destroy` of 0.

EGL window surfaces (Linux): `eglCreateWindowSurface(display, config, int $native_window, ?array $attribs)` takes an X11 window id or a `wl_egl_window` address from `wl_egl_window_create(int $wl_surface, w, h)` (`wl_egl_window_resize`, `wl_egl_window_destroy`). `eglGetConfigAttrib`, `eglSurfaceAttrib`. Constants for `EGL_GL_COLORSPACE_KHR` (sRGB, linear, scRGB linear, BT.2020 PQ, Display P3), float configs (`EGL_COLOR_COMPONENT_TYPE_*`), SMPTE 2086 / CTA 861.3 metadata, `EGL_PLATFORM_WAYLAND_KHR` / `_X11_KHR`. Pi 5 Mesa (labwc) lists `EGL_KHR_gl_colorspace` + `EGL_EXT_pixel_format_float` only; configs come deepest first, and only 8-bit ones take a colour space.

`glMapBufferRange` answers the mapped address (`int`, 0 when GL fails). `glReadPixels` writes into an address: memory from another extension (an ext-fb buffer's `pointer()`), or a mapped pixel-pack buffer.

`glGetIntegerv` writes every int GL writes for the pname: 4 for `GL_VIEWPORT`, `GL_SCISSOR_BOX`, `GL_COLOR_WRITEMASK`, `GL_COLOR_CLEAR_VALUE`, `GL_BLEND_COLOR`; 2 for the ranges and `GL_MAX_VIEWPORT_DIMS`; the matching `GL_NUM_*` count for `GL_COMPRESSED_TEXTURE_FORMATS`, `GL_PROGRAM_BINARY_FORMATS` and `GL_SHADER_BINARY_FORMATS`.

On OpenGL ES, `glTexSubImage2D` of `GL_RGB` into a texture created with sized internal format `GL_RGBA8` is `GL_INVALID_OPERATION`. Desktop GL accepts that conversion. The sizing test lets the 25-byte string through, then drains that driver error so it cannot fail a later `glGetError()`.

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/open-gl/blob/v0.11.1/SUPPORT.md) lists every command of the floors this extension builds on: OpenGL 4.1
core profile, OpenGL ES 3.0 and EGL 1.5 from the Khronos registries, and every CGL function of the
macOS SDK's OpenGL.framework headers, each marked bound or not; extensions are not counted. The API
badge is computed from it. Regenerate both on macOS after a binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

## Example

```php
if (PHP_OS_FAMILY === 'Darwin') {
    $attribs = [kCGLPFAOpenGLProfile, kCGLOGLPVersion_GL4_Core, kCGLPFAAccelerated, kCGLPFAColorSize, 24, kCGLPFAAlphaSize, 8, 0];
    CGLChoosePixelFormat($attribs, $pixelFormat, $count);
    CGLCreateContext($pixelFormat, null, $context);
    CGLDestroyPixelFormat($pixelFormat);
    CGLSetCurrentContext($context);
} else {
    $display = eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA, null, null);
    eglInitialize($display, $major, $minor);
    eglBindAPI(EGL_OPENGL_ES_API);
    eglChooseConfig($display, [EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT, EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_NONE], $configs, 1, $count);
    $context = eglCreateContext($display, $configs[0], null, [EGL_CONTEXT_MAJOR_VERSION, 3, EGL_CONTEXT_MINOR_VERSION, 1, EGL_NONE]);
    eglMakeCurrent($display, null, null, $context);
}

glClearColor(0.0, 0.0, 0.0, 1.0);
glClear(GL_COLOR_BUFFER_BIT);
$target = new FbBuffer(new FbFormat(FB_LAYOUT_RGBA8888, channelOrder: FB_CHANNELS_RGBA), 8, 8); // ext-fb
glReadPixels(0, 0, 8, 8, GL_RGBA, GL_UNSIGNED_BYTE, $target->pointer());
$pixels = $target->bytes();
```

Offscreen contexts need no display on either machine. The Mac context is CGL 4.1 core. The Linux context is surfaceless EGL, OpenGL ES 3.1.

## Test

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest   # Homebrew NTS
zhp -d memory_limit=128M vendor/bin/pest     # Homebrew ZTS
```

On the Pi, copy the tree and run `./install-debian-trixie.sh`, then the same Pest command with `php`. The gate draws a triangle by stencil-then-cover into a 4× framebuffer, resolves it with `glBlitFramebuffer`, and reads it back.
