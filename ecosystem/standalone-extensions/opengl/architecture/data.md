# Data

How pointer and count pairs, strings, addresses, offsets, and pixel-store sizes cross into GL.

## Overview

The binding stays 1:1. These are the only translations.[^texture]

| C | PHP |
|---|---|
| pointer + count | one list (`glGenBuffers`, `glDeleteBuffers`, `glShaderSource`, `glDrawBuffers`) |
| out-parameter | by-reference parameter |
| info log | string, length from `GL_INFO_LOG_LENGTH`; 0 answers `""` |
| `const void *` data | `string\|int\|null` |
| `void *` destination | `?int`; `null` answers the bytes |
| buffer offset (`glVertexAttribPointer`, `glDrawElements`) | `int` |
| attribute list | list of ints ending with `0` (CGL) or `EGL_NONE` (EGL) |

`glUniformMatrix4fv` takes the floats as one list. The count is `count($value) / 16`. Any other length is a `ValueError`.

## Sizing

A string must hold what GL will read. Buffer data uses the `size` argument. Pixel data uses:[^texture]

- bytes in a pixel: `GL_RGBA`/`GL_UNSIGNED_BYTE` 4, `GL_RGB`/`GL_UNSIGNED_BYTE` 3, `GL_RED`/`GL_UNSIGNED_BYTE` 1, `GL_RGBA`/`GL_FLOAT` 16
- columns: `GL_UNPACK_ROW_LENGTH` or `GL_PACK_ROW_LENGTH` when set, otherwise the width
- stride: columns times bytes, rounded up to `GL_UNPACK_ALIGNMENT` or `GL_PACK_ALIGNMENT`
- skips: `GL_UNPACK_SKIP_ROWS`/`GL_UNPACK_SKIP_PIXELS` or `GL_PACK_SKIP_ROWS`/`GL_PACK_SKIP_PIXELS`
- required: `skip rows × stride + skip pixels × bytes + stride × (height − 1) + width × bytes`; 0 for an empty region

Uploads read the unpack state. `glReadPixels` reads the pack state. A short string is `ValueError` "must hold N bytes, M given". A format/type pair that is not in the table is `ValueError` "cannot size format 0x… type 0x… for a string; pass an address". An address is still accepted.

## Addresses and reads

Address 0 is refused, except as a `glReadPixels` offset while a pixel-pack buffer is bound. Any other address is trusted and is not sized.[^buffer]

`glReadPixels(null)` refuses while `GL_PIXEL_PACK_BUFFER_BINDING` is non-zero, because the pointer would be an offset. Otherwise it answers a string of the packed size. An int is passed through.

`glMapBufferRange` answers the mapped address (`int`, 0 when GL returns NULL). It does not copy the bytes into PHP.

On OpenGL ES, `GL_RGB` / `GL_UNSIGNED_BYTE` into a texture created with sized `GL_RGBA8` is `GL_INVALID_OPERATION`. Desktop GL converts it. The sizing test still sends the 25-byte string, then calls `glGetError()` so that driver error cannot fail a later check.

[^texture]: src/gl_texture.c
[^buffer]: src/gl_buffer.c
