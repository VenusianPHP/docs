# Structs

C structs as final classes, with pointer-and-count pairs collapsed to lists and filled by sdl3_*_from.

## Overview

A struct class is `final`, not serializable, and not cloneable. Properties are public and named as the C fields. Scalars start at zero, lists at `[]`, handle fields at `null`. A constructor builds each nested struct. Padding fields are not properties.[^types]

Four translations, and no others:

| C | PHP |
|---|---|
| pointer + count | one `array`; the count is `count($list)`; empty is NULL and 0 |
| `const Uint8 *code` + `size_t code_size` | one `string` |
| out-parameter | by-reference parameter |
| `void *` | `int` address, `0` refused |

`bool` stays `bool`. Enums, flags, and `props` are `int`.

## Filling a C struct

`bool sdl3_<Struct>_from(zend_object *obj, <Struct> *out, sdl3_scratch *scratch)` zeroes `out`, then reads properties. A list element of the wrong class throws `TypeError` naming the property. A released handle throws `ValueError` naming the handle class. Either happens before the SDL call, and the helper returns false.[^types]

The C arrays a list needs are allocated in `scratch` and freed by the caller after the SDL call returns. The string behind `code` or `entrypoint` is the property's `zend_string`, which stays alive for that call because the PHP object does.

The bound fields are the SDL 3.2.10 struct. `SDL_GPUMultisampleState` has no `enable_alpha_to_coverage`, and `SDL_GPUDepthStencilTargetInfo` has no `mip_level` or `layer`. Those members exist only in 3.4. `memset` zeroes them when this tree is compiled against 3.4 headers, without naming them, so the same source compiles on 3.2.[^header]

[^types]: `src/SDL_gpu_types.c`
[^header]: SDL 3.2.10 `SDL_gpu.h`
