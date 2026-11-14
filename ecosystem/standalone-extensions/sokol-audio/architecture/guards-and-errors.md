# Guards and errors

Checks that run before sokol_audio.h is called, the SOKOL_ASSERT each one prevents, and how remaining assertions become exceptions.

## State guards (`Error`)

* Not set up → `saudio_setup() has not been called` (stands in for `SOKOL_ASSERT(_saudio.setup_called)` in every getter, push, expect, shutdown). `saudio_isvalid()` has no assert and no guard.
* Set up again → `saudio_setup() was already called; call saudio_shutdown() first` (`!_saudio.valid`, `!_saudio.setup_called`).
* Another PHP thread (ZTS) → `sokol-audio was set up by another thread`: sokol is one static instance per process.
* `saudio_shutdown()` inside a callback → Error: the audio thread is blocked on that callback, and sokol's shutdown joins it (deadlock). `saudio_setup()` there fails the already-set-up guard.
* Forked child of a live instance → `sokol-audio's audio thread did not survive fork`.[^callbacks]

Ownership is claimed under the process mutex before validation, released if validation fails.

## Input guards (`ValueError`)

* desc sizes `< 0` or `> INT_MAX`.
* effective `num_packets + 1 > SAUDIO_RING_MAX_SLOTS` (ring init assert).
* effective `buffer_frames * channels * 4 > INT_MAX`, `packet_frames * channels * 4 * num_packets > INT_MAX` (sokol's int byte counts).
* allocator functions non-null (both-or-neither assert, and PHP has no allocator).
* `saudio_push`: `num_frames < 1` (`frames && num_frames > 0`), string short of `num_frames` frames.[^c]

Effective = upstream's `_saudio_def` default for 0, read from the header by the impl unit (`phpsaudio_default_*`, `phpsaudio_ring_max_slots`).

## Assertions

`SOKOL_ASSERT(c)` is defined in `src/sokol_audio_impl.c` to call `phpsaudio_on_assert`, which records the first failure (condition, header basename, line) under the mutex and returns.[^impl] Every binding calls `phpsaudio_assert_check()` after sokol returns and throws `saudio_assertion_error "<cond> at sokol_audio.h:<line>"`. With the guards above no public-API path reaches an assert; the handler exists so an internal one never aborts PHP. An assert on the audio thread surfaces on the next binding call.

## Backend failure

Not an exception. `saudio_isvalid()` false, the logger reports, other calls return sokol's zeros (tests: `PushTest` "pushes nothing").[^tests]

[^callbacks]: ownership guards, assertion slot
[^c]: desc validation, push checks
[^impl]: SOKOL_ASSERT definition
[^tests]: GuardTest
