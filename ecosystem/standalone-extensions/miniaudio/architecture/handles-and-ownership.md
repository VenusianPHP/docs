# Handles and ownership

How handle objects hold miniaudio's C structs, track who points into whom, expose fields, and end with the request or a fork.

## States

`phpma_handle` wraps a 64-byte aligned C struct that never moves.[^runtime] STORAGE (`new`), LIVE (an `_init` succeeded), BORROWED (memory miniaudio or another handle owns; kept valid by its owner, refused once the owner is uninitialized). `ma_spinlock` is LIVE from `new`. `foreign` marks memory miniaudio allocated (`ma_audio_buffer_alloc_and_init`, pages); its uninit frees it and the object becomes empty storage.

## Frames and ownership

A call converts its arguments into a frame: temporary memory, the handles the arguments point into, retained zvals, and persistent memory (`keep`). On a successful `_init` the frame commits to the target: the handles become its dependencies (each holds a reference and a dependents count), retained zvals and kept memory move onto it. Uninit runs the C uninit, frees kept memory and the heap, and releases dependencies. Uninitializing a handle first uninitializes every live handle that depends on it, newest first. A failed `_init` drops the callback context made for it.

## Fields

Each handle kind has a generated table of its struct's plain fields (scalars, enums, `char[]`, scalar arrays, handle pointers, value structs, anonymous sub-structs as arrays). `read_property` reads them live; writes are `Error`; reading an uninitialized handle's field is `Error`. Offsets are from the start of the handle's struct, also for nested rows.

## Request end and fork

RSHUTDOWN marks the callback queue closing (every callback gets its no-op answer), then uninitializes the live list newest first; the registry is destroyed after the object store. In a fork child, `ma_device`, `ma_engine`, `ma_resource_manager` and `ma_device_job_thread` from before the fork throw `Error` on use, and their uninit skips the C call. A resource manager without job threads has its jobs processed while one of its objects uninitializes, so a pending load cannot hang request end.

[^runtime]: handles, frames, conversions, fields
