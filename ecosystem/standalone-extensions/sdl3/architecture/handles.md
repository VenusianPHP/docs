# Handles

One PHP object per native pointer, released explicitly, with a slot for whatever the native object borrows from PHP.

## Overview

A handle is `sdl3_handle { void *ptr; zval keep; zend_object std; }`. `ptr` is the native object. `free_obj` drops the identity entry and the `keep` zval. It does not call `SDL_Destroy*` or `SDL_Release*`.[^runtime]

`sdl3_box` returns the PHP object already stored for that address and class, or a new one. The identity table is module global `boxes`: native address → `zend_object*`, not refcounted. GINIT creates it and GSHUTDOWN destroys it, so each ZTS thread has its own table.[^runtime]

`sdl3_release` clears `ptr`, removes the identity entry, releases any handle stored in `keep`, and drops `keep`. The next SDL object at that address boxes as a new PHP object. `sdl3_handle_ptr` throws `ValueError` (`SDL_Window has been destroyed`) when `ptr` is NULL. `fromPointer(0)` throws `ValueError`. Any other address is trusted.

## What release covers

| Call | PHP handle released | `keep` |
|---|---|---|
| `SDL_DestroyWindow` | the window, and the window surface if `SDL_GetWindowSurface` boxed one | the surface object |
| `SDL_DestroyWindowSurface` | the window surface if `SDL_GetWindowSurface` boxed one; the window stays live | the surface object |
| `SDL_DestroySurface` | the surface | the pixel string from `SDL_CreateSurfaceFrom` |
| `SDL_CloseIO` | the stream | |
| `SDL_GL_DestroyContext` | the context | |
| `SDL_Metal_DestroyView` | the view | |
| `SDL_DestroyGPUDevice` | the device only. Children stay live and then refuse, because their release functions take the device | |
| `SDL_ReleaseGPUTexture`, `SDL_ReleaseGPUSampler`, `SDL_ReleaseGPUBuffer`, `SDL_ReleaseGPUTransferBuffer`, `SDL_ReleaseGPUShader`, `SDL_ReleaseGPUGraphicsPipeline`, `SDL_ReleaseGPUFence` | that object | |
| `SDL_EndGPUCopyPass`, `SDL_EndGPURenderPass` | the pass | |
| `SDL_SubmitGPUCommandBuffer`, `SDL_SubmitGPUCommandBufferAndAcquireFence`, `SDL_CancelGPUCommandBuffer` | the command buffer, and any swapchain texture it acquired | the texture list |

`SDL_CreateSurfaceFrom` with a string stores a reference in the surface's `keep`, so the pixels outlive the caller's variable. An address stores nothing.

## Hit tests

Module global `hit_tests` maps a window address to the entry SDL holds as `callback_data`: the callable's `zend_fcall_info_cache`, the `$callback_data` zval, and a reference count. The trampoline-safe `zend_fcc_dup`/`zend_fcc_dtor` pair owns the callable. A call takes a reference for its duration, so a callback that replaces or removes its own hit test frees the entry after it returns. `SDL_DestroyWindow` drops the window's entry. `SDL_Quit` and RSHUTDOWN clear SDL's callback on every window in the table and empty it, so SDL never calls into request memory that is gone.

[^runtime]: `src/runtime.h`
