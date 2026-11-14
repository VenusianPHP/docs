# Bindings

Every sokol_audio.h declaration bound, the PHP translation of each C type, and why nothing is left out.

## Functions (11)

`saudio_setup`, `saudio_shutdown`, `saudio_isvalid`, `saudio_userdata`, `saudio_query_desc`, `saudio_sample_rate`, `saudio_buffer_frames`, `saudio_channels`, `saudio_suspended`, `saudio_expect`, `saudio_push`.[^header] The C++ reference overload `saudio_setup(const saudio_desc&)` is the same function.

## Classes (5 + 1)

`saudio_desc`, `saudio_logger`, `saudio_allocator`, `saudio_win32_desc`, `saudio_n3ds_desc`: `final`, one typed property per field in field order, constructor takes every field optional (zero; nested structs fresh, created in `create_object` so they are never uninitialised). `clone` deep-copies nested struct objects only; closures and user data are shared, as C copies pointers.[^c] `saudio_assertion_error extends Error`.

## Constants (37)

`SAUDIO_LOGITEM_*`: the 34 `_SAUDIO_LOG_ITEMS` x-macro entries, values 0-33 in upstream order. `SAUDIO_N3DS_DSP_INTERP_POLYPHASE/LINEAR/NONE` = 0/1/2.[^stub]

## Translations

* `int` → `int`, range-checked to C `int`; `bool` → `bool`; enum → `int`.
* `float* buffer` / `const float* frames` → string of packed 32-bit native floats. `saudio_push(string $frames, int $num_frames)` reads the first `num_frames * saudio_channels() * 4` bytes; shorter → `ValueError`.
* `void* user_data` (desc, logger, allocator) → `mixed`. sokol gets `NULL`; the PHP value is held by the binding and returned by `saudio_userdata()`, `saudio_query_desc()` and the callbacks.
* Function pointers → `?Closure`: `stream_cb` `fn(string &$buffer, int $num_frames, int $num_channels)`, `stream_userdata_cb` adds `mixed $user_data`, `saudio_logger.func` `fn(string $tag, int $log_level, int $log_item_id, ?string $message_or_null, int $line_nr, ?string $filename_or_null, mixed $user_data)`. sokol gets C trampolines (`src/callbacks.c`); its own dispatch (stream_cb wins over stream_userdata_cb) is unchanged.
* `saudio_allocator.alloc_fn/free_fn` must be `null` (`ValueError` otherwise): PHP has no allocator to hand sokol. sokol keeps `malloc`/`free`.
* `saudio_query_desc()` builds a fresh `saudio_desc` from sokol's stored copy plus the held PHP values.

## Not bound

Nothing in the public section is left out. `SOKOL_DUMMY_BACKEND`, `SAUDIO_USE_ALSA` (deprecated upstream) and `SAUDIO_RING_MAX_SLOTS` are compile-time knobs, left at upstream defaults. `win32` and `n3ds` are data sokol ignores on Linux/macOS, as in C. Messages and file names reach the logger in every build because the impl unit defines `SOKOL_DEBUG`.

[^stub]: the declaration
[^header]: upstream public section (lines 544-725)
[^c]: functions, struct classes, conversions
