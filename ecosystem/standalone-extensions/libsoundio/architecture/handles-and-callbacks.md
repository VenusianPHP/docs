# Handles and callbacks

One PHP object per libsoundio pointer, released when libsoundio frees it; live field properties; two PHP callouts entered only on the PHP thread, every other callback an address.

## Handles

`LIBSOUNDIO_G(boxes)`: native address → zend_object, live handles only, not refcounted. `libsoundio_box` answers the existing object or makes one; `fromPointer` boxes a trusted address (0 → null).[^runtime]

Release (pointer cleared, entry dropped; `pointer()` → 0; as a required argument → `ValueError` "<class> has been released", site `libsoundio-released-handle` in `libsoundio_handle_arg`; where libsoundio takes NULL — `soundio_device_unref` and the stream and ring buffer `_destroy` functions — the NULL passes through):

* `soundio_destroy` — the context, after its callouts are dropped.
* `soundio_outstream_destroy`, `soundio_instream_destroy`, `soundio_ring_buffer_destroy` — that object.
* `soundio_device_unref` — the device, when its `ref_count` was 1 before the call. A device fresh from `soundio_get_*_device` reads `ref_count` 2: libsoundio keeps its own reference until `soundio_destroy`.

Dropping the last PHP reference frees the PHP object only.

## Fields

Each handle class reads and writes its C struct fields live (`bindings.json` glue). `const char *` fields the program writes (`app_name`, a stream's `name`, `layout.name`) point into a PHP string held in `LIBSOUNDIO_G(keep)` until the field is written again or the object is destroyed.[^types]

## Callbacks

libsoundio calls these on the PHP thread, inside `soundio_flush_events` / `soundio_wait_events`: `on_devices_change`, `on_backend_disconnect` (`?Closure` properties, stored in `LIBSOUNDIO_G(callouts)` per `SoundIo`), and `emit_rtprio_warning` (no context argument, so an address). Those two functions set the dispatching context around the call; a callout fired outside it never enters PHP.[^types]

Every other callback — `on_events_signal`, `jack_info_callback`, `jack_error_callback`, the streams' `write_callback`, `read_callback`, `underflow_callback`, `overflow_callback`, `error_callback` — runs on libsoundio's realtime or JACK threads, where PHP must not run (no locks, no allocation, owner thread only). They are `int` addresses, 0 = NULL. The extension writes no native callback of its own: a ring-buffer pump would choose frame counts, underrun behaviour and sample layout, which libsoundio leaves to the program.

Consequence: the extension plays and records nothing alone; native code supplies `write_callback` / `read_callback`. Starting a stream with that field 0 is refused (sites `libsoundio-null-write-callback`, `libsoundio-null-read-callback`): the audio thread would call NULL.

RSHUTDOWN: every `SoundIo` gets libsoundio's own callouts back, then the closures are freed.

[^runtime]: Handle table, keep table, refusal helpers
[^types]: Field properties and callouts
