# Callbacks and threads

How the stream callback and logger reach PHP from sokol's audio thread, the deadline, shutdown ordering, fork and request end.

## Ownership

One sokol-audio per process. `saudio_setup()` records the calling thread (`pthread_self`) and its `&EG(vm_interrupt)` under a process mutex. Held PHP values (`phpsaudio_values`) are touched only by that thread.[^callbacks]

## Stream request

Audio thread (CoreAudio queue thread, PulseAudio pthread) calls the trampoline:

1. If not set up, stopping or dead → buffer zeroed, return.
2. On the owner thread itself (no-thread backends) → run the closure inline.
3. Else post `{buffer, frames, channels, userdata?}` as `POSTED`, set the owner's `vm_interrupt`, `pthread_cond_timedwait` until `num_frames / sample_rate` (actual rate after setup; 44100 before).
4. Still `POSTED` at the deadline or on stop → withdrawn (`IDLE`), zeroed. `STARTED` → wait without deadline for `IDLE`.

Owner, in `zend_interrupt_function` (chained after any previous hook): `POSTED` → `STARTED`, unlock, call the closure with a by-ref zero-filled string of `frames*channels*4` bytes, copy back only if it is a string of exactly that length (else `TypeError`/`ValueError`, silence), `IDLE`, broadcast. An exception (thrown or bad buffer) stays in `EG(exception)` and propagates from the interrupt point; no PHP callback runs while one is pending.

Consequence: PHP code that keeps reaching interrupt points (loops, calls) plays; `sleep()` or long C calls play silence. `StreamTest` checks ≤1 callback across a 400 ms `usleep`.[^tests]

## Logs

Logger called on the owner (all of setup) → inline. On another thread (`PULSEAUDIO_SIMPLE_WRITE_FAILED`, AAudio restart) → node appended to a list (pointers only: sokol passes literals and its static message table), interrupt raised, no wait. Delivered after the stream request in the hook, or by `saudio_shutdown()`; dropped at request end.

## Shutdown

`stopping = true` + broadcast (a waiting audio thread withdraws to silence) → upstream `saudio_shutdown()` (joins / `AudioQueueStop(sync)`) → clear state, deliver queued logs, release held values.

## Fork and request end

`pthread_atfork`: prepare locks the mutex, parent unlocks, child reinitialises mutex/cond and marks `dead` if sokol was valid. Dead: stateful calls `Error`; RSHUTDOWN releases PHP values only (sokol's state belongs to the parent's thread). RSHUTDOWN otherwise runs the shutdown sequence without delivering logs. `LifecycleTest` covers both.[^tests]

[^callbacks]: queue, interrupt hook, trampolines, atfork, rshutdown
[^tests]: StreamTest, LoggerTest, LifecycleTest
