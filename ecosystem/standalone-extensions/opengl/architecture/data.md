# Data

How counts and lists, strings, addresses, offsets, and pixel-store sizes cross into GL, and where the extension refuses.

## Overview

The binding stays 1:1. These are the only translations.[^texture]

| C | PHP |
|---|---|
| list + count GL reads | the count is its own parameter, the list a PHP list (`glDeleteBuffers($n, $buffers)`, `glShaderSource($shader, $count, $string, $length)`, `glDrawBuffers`, `glUniformMatrix4fv`, `eglSwapBuffersWithDamageKHR`) |
| out-parameter | by-reference parameter (`glGenBuffers($n, &$buffers)`, `glGetShaderInfoLog($shader, $bufSize, &$length, &$infoLog)`) |
| `const void *` data | `string\|int\|null`; null and 0 are NULL |
| `void *` destination | `?int`: an address, or an offset into the bound buffer object |
| buffer offset (`glVertexAttribPointer`, `glDrawElements`) | `int` |
| C int | `int`, converted as C converts it |
| `GLboolean`, `EGLBoolean` | `bool` |

`glUniformMatrix4fv` elements convert as PHP's `(float)`; `glShaderSource` elements as PHP converts a value to a string. Neither is refused.

## Refusals

Only where the call crashes. Each site is in `bindings.json` with a probe in `tests/Probes`.[^bindings]

| Site | Calls |
|---|---|
| `opengl-no-context` | every `gl*` with no current context, macOS only (libglvnd answers it on Linux) |
| `opengl-attrib-terminator` | a CGL attribute list without its 0; EGL lists go to EGL as given |
| `opengl-bytes-length` | a string shorter than GL reads (sizing below) |
| `opengl-null-address` | address 0 to `glBufferSubData`; to `glTexSubImage2D` / `glReadPixels` with no unpack / pack buffer bound |
| `opengl-list-count` | a count past its list |
| `opengl-wl-null-window` | `wl_egl_window_resize` / `wl_egl_window_destroy` of 0 |

Dropped after a checks-off build did not crash (macOS and Linux): released handles (CGL, EGL, `GLsync` reach the toolkit as NULL), 32-bit and ≥ 0 ranges, negative `glGen*` counts, a negative `eglChooseConfig` size, the `glClientWaitSync` timeout, `wl_egl_window_create` sizes and surface 0, an empty `CGLSetParameter` list, the damage extension string. Releasing the current context makes no extra call: CGL clears it, EGL keeps it current until released.

## Sizing

Buffer data uses the `size` argument. Pixel data uses:[^texture]

- bytes in a pixel: the GL 4.1 / ES 3.0 tables, components × type size, or the packed type's size
- columns: `GL_UNPACK_ROW_LENGTH` when set, otherwise the width
- stride: columns times bytes, rounded up to `GL_UNPACK_ALIGNMENT`
- skips: `GL_UNPACK_SKIP_ROWS` / `GL_UNPACK_SKIP_PIXELS`
- required: `skip rows × stride + skip pixels × bytes + stride × (height − 1) + width × bytes`; 0 for an empty region

A format/type pair outside the tables goes to GL, which answers `GL_INVALID_ENUM` without reading. Any address other than 0 is trusted and not sized.[^buffer]

`glMapBufferRange` answers the mapped address (`int`, 0 when GL returns NULL). It does not copy bytes into PHP; memory with an address (an ext-fb buffer) takes `glReadPixels`.

`glGetIntegerv` sizes its output from the GL 4.1 / ES 3.0 state tables, the list pnames from their `GL_NUM_*` query, never fewer than 16 ints. The old fixed 4-int array overflowed for `GL_COMPRESSED_TEXTURE_FORMATS` on Mesa (66 formats).

On OpenGL ES, `GL_RGB` / `GL_UNSIGNED_BYTE` into a texture created with sized `GL_RGBA8` is `GL_INVALID_OPERATION`. Desktop GL converts it. The sizing test still sends the 25-byte string, then calls `glGetError()` so that error cannot fail a later check.

[^texture]: src/gl_texture.c
[^buffer]: src/gl_buffer.c
[^bindings]: bindings.json
