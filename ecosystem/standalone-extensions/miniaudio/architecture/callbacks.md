# Callbacks

How miniaudio's threads reach PHP callables without entering PHP, the deadlines and no-op answers, and every callback family.

## Queue

One queue per PHP thread (RINIT). A trampoline on the owner thread serves directly; on any other thread it appends a request, raises the owner's `EG(vm_interrupt)`, and waits. Not started before its deadline (device period from the frame count; 100 ms other audio-path callbacks; 5 s job/VFS/log) → withdrawn and the no-op answer applies (silence; `MA_BUSY` data-source reads; `MA_ERROR`). Taken → waits until done. The owner serves from `zend_interrupt_function` (chained) and from `phpma_run_serving`, which runs a blocking call (`BLOCKING` in the generator, every uninit) on a helper pthread while the owner serves. A callback never runs while an exception is pending; an exception is rethrown when the binding call returns; a wrong return type is `TypeError`.[^callbacks]

## Contexts

`phpma_ctx` per handle, keyed by its C struct in a process map (rwlock), holds closures and user data by struct path (`vtable.onRead`, `pitchResampling.pBackendVTable.onProcess`). User data handed to miniaudio is a `phpma_sub` (context + path), validated against a set before use. Contexts are kept memory of their handle and die with its uninit.

## Families

Device data/notification/stop; engine `onProcess` (device path only, upstream); sound end; log callbacks (one context per registration); device enumeration; data source vtable and `onGetNext`; node vtable; decoder read/seek; encoder write/seek; `ma_vfs_callbacks` and `ma_async_notification_callbacks` objects (one native view per object for the request, closures read live; VFS files boxed PHP values); resampling backends (state = the value `onInit` returns); decoding backends (8 proc sets per vtable list; `ma_read_proc`/`ma_seek_proc`/`ma_tell_proc` objects invalid after `onUninit`); device backends (`onContextInit` fills `$pCallbacks`, then installed; `ma_enum_devices_callback_proc` valid during the call); custom jobs (64 proc slots per process, released at request end).[^backends]

[^callbacks]: queue, contexts, device/engine/sound/log/data source/node/stream/VFS/notification trampolines
[^backends]: resampling, decoding and device backends, custom jobs, proc classes
