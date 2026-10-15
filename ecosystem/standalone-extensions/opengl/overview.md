# Overview

![CI](https://github.com/php-io-extensions/open-gl/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/open-gl/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/open-gl/actions/workflows/ci.yml)

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
- `venusian build` reads the system packages from `extra.venusian.system` in composer.json: apt packages to build with and the run-time ones a `.deb` depends on or recommends, and the Homebrew ones.

## Install

Through PIE:

```bash
pie install php-io-extensions/opengl
```

From a checkout of this package:

```bash
./install-macos.sh            # Homebrew php@8.4 and php@8.4-zts, or pass PHP binaries
./install-debian-trixie.sh    # Debian trixie, Raspberry Pi OS
```

## Translations

Bindings are 1:1. There are no defaults and no composites. The only translations:

- A pointer + count pair is one PHP list: `glShaderSource(int $shader, array $strings)`, `glGenBuffers(int $n): array`, `glDeleteBuffers(array $buffers)`, `glDrawBuffers(array $bufs)`.
- An out-parameter is a by-reference parameter.
- An info log is a string. Its length is the matching `GL_INFO_LOG_LENGTH` query. A length of 0 answers `""`.
- A `const void *` data argument is `string|int|null`: bytes, an address, or NULL.
- A `void *` destination is `?int`. `null` answers the bytes as a string.
- A pointer GL reads as a buffer offset (`glVertexAttribPointer`, `glDrawElements`) is an `int`.
- An attribute list (CGL or EGL) is a list of ints that must end with its terminator (`0` for CGL, `EGL_NONE` for EGL). One that does not is a `ValueError`, and the list is not read past.
- `glUniformMatrix4fv` takes the matrix floats as one list. The count passed to GL is `count($value) / 16`. A length that is not a multiple of 16 is a `ValueError`.

A string given as pixel or buffer data must hold what GL will read. For `glTexImage2D` and `glTexSubImage2D` that size comes from the width, height, format, type, and the current `GL_UNPACK_ALIGNMENT` and `GL_UNPACK_ROW_LENGTH`. For `glBufferData` and `glBufferSubData` it is the size. A short string is a `ValueError` ("must hold N bytes, M given"). A format/type pair the binding cannot size is a `ValueError` that names both; an address is still accepted. An address other than 0 is trusted.

Row length is `GL_UNPACK_ROW_LENGTH` or `GL_PACK_ROW_LENGTH` when that is set, otherwise the width. The stride is that many pixels times the bytes in a pixel, rounded up to the alignment. The required size is `skip rows × stride + skip pixels × bytes + stride × (height − 1) + width × bytes`, with the skips from `GL_UNPACK_SKIP_ROWS`/`_PIXELS` or `GL_PACK_SKIP_ROWS`/`_PIXELS`; a string read holds the skipped bytes too. Uploads use the unpack state. `glReadPixels` uses the pack state.

`glReadPixels(..., ?int $pixels)`: `null` answers the packed bytes as a string, and is refused while a `GL_PIXEL_PACK_BUFFER` is bound. An int is passed through as GL reads it: an address, or an offset into the bound pack buffer, where 0 is a valid offset. Address 0 is refused when no pack buffer is bound.

Sized pixel types: `GL_RGBA` with `GL_UNSIGNED_BYTE` (4 bytes), `GL_HALF_FLOAT` (8, with `GL_RGBA16F` textures) and `GL_UNSIGNED_INT_2_10_10_10_REV` (4, `GL_RGB10_A2`).

EGL window surfaces (Linux): `eglCreateWindowSurface(display, config, int $native_window, ?array $attribs)` takes an X11 window id or a `wl_egl_window` address from `wl_egl_window_create(int $wl_surface, w, h)` (`wl_egl_window_resize`, `wl_egl_window_destroy`; 0 surface answers 0). `eglGetConfigAttrib`, `eglSurfaceAttrib`. Constants for `EGL_GL_COLORSPACE_KHR` (sRGB, linear, scRGB linear, BT.2020 PQ, Display P3), float configs (`EGL_COLOR_COMPONENT_TYPE_*`), SMPTE 2086 / CTA 861.3 metadata, `EGL_PLATFORM_WAYLAND_KHR` / `_X11_KHR`. Pi 5 Mesa (labwc) lists `EGL_KHR_gl_colorspace` + `EGL_EXT_pixel_format_float` only; configs come deepest first, and only 8-bit ones take a colour space.

`glMapBufferRange` answers the mapped address (`int`, 0 when GL fails). Bytes for PHP come from `glReadPixels`.

Every `gl*` binding throws `Error` ("glX(): no current OpenGL context") when `CGLGetCurrentContext()` or `eglGetCurrentContext()` says nothing is current. Releasing the current context clears it first, so the same check holds afterwards.

On OpenGL ES, `glTexSubImage2D` of `GL_RGB` into a texture created with sized internal format `GL_RGBA8` is `GL_INVALID_OPERATION`. Desktop GL accepts that conversion. The sizing test lets the 25-byte string through, then drains that driver error so it cannot fail a later `glGetError()`.

## Example

```php
if (PHP_OS_FAMILY === 'Darwin') {
    $attribs = [kCGLPFAOpenGLProfile, kCGLOGLPVersion_GL4_Core, kCGLPFAAccelerated, kCGLPFAColorSize, 24, kCGLPFAAlphaSize, 8, 0];
    CGLChoosePixelFormat($attribs, $pixelFormat, $count);
    CGLCreateContext($pixelFormat, null, $context);
    CGLDestroyPixelFormat($pixelFormat);
    CGLSetCurrentContext($context);
} else {
    $display = eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, null);
    eglInitialize($display, $major, $minor);
    eglBindAPI(EGL_OPENGL_ES_API);
    eglChooseConfig($display, [EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT, EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_NONE], $configs, 1, $count);
    $context = eglCreateContext($display, $configs[0], null, [EGL_CONTEXT_MAJOR_VERSION, 3, EGL_CONTEXT_MINOR_VERSION, 1, EGL_NONE]);
    eglMakeCurrent($display, null, null, $context);
}

glClearColor(0.0, 0.0, 0.0, 1.0);
glClear(GL_COLOR_BUFFER_BIT);
$pixels = glReadPixels(0, 0, 8, 8, GL_RGBA, GL_UNSIGNED_BYTE, null);
```

Offscreen contexts need no display on either machine. The Mac context is CGL 4.1 core. The Linux context is surfaceless EGL, OpenGL ES 3.1.

## Test

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest   # Homebrew NTS
zhp -d memory_limit=128M vendor/bin/pest     # Homebrew ZTS
```

On the Pi, copy the tree and run `./install-debian-trixie.sh`, then the same Pest command with `php`. The gate draws a triangle by stencil-then-cover into a 4× framebuffer, resolves it with `glBlitFramebuffer`, and reads it back.
