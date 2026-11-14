# Callbacks

How libvlc's threads reach PHP without entering it, and what each callable is called with.

## Threads

* libvlc calls back on its own threads. PHP never runs there: the call is handed to the PHP thread that set the callable (its owner), which raises its VM interrupt and runs it at its next interrupt point: a loop iteration, `usleep()`, a function call. A thread blocked in one long `sleep()` serves nothing until it wakes.
* A callback libvlc fires on the owner thread itself, inside a binding call, runs at once.
* **Waited**: calls whose result libvlc needs (media open, read and seek; audio and video format setup; the video lock; log) wait up to a deadline, then get libvlc's no-op. Media callbacks report an error, the audio setup refuses, the video lock renders into a scratch picture the extension owns.
* **Deferred**: events and the exit handler copy their data and let libvlc's thread go; the callable runs after, so it may stop or release the player that emitted the event.
* **Posted**: calls that return nothing (audio play, pause, resume, flush, drain and volume; video unlock and display; media close; dialogs) are queued with their arguments copied. libvlc never waits on PHP, so real-time audio cannot stall on it. Audio and video data waiting for PHP is capped at 1024 calls; past that, new data is dropped rather than growing without bound.
* An exception thrown by a callable surfaces on the owner thread at its next interrupt point. When the request ends, queued calls are dropped and libvlc gets the no-ops.

## Callables

| Callback | Called as | libvlc waits |
|---|---|---|
| `libvlc_event_attach` | `fn(libvlc_event_t $event)` | until the data is copied (≤ 1 s) |
| `libvlc_log_set` | `fn(int $level, libvlc_log_t $ctx, string $message)` | ≤ 1 s; `$ctx` is valid during the call |
| `libvlc_set_exit_handler` | `fn()` | as events |
| `libvlc_media_new_callbacks` | open `fn(?int &$size): int`, read `fn(int $len): string\|int`, seek `fn(int $offset): int`, close `fn()` | ≤ 5 s each; close never |
| `libvlc_audio_set_callbacks` | play `fn(string $samples, int $count, int $pts)`, pause, resume, flush `fn(int $pts)`, drain `fn()` | never |
| `libvlc_audio_set_volume_callback` | `fn(float $volume, bool $mute)` | never |
| `libvlc_audio_set_format_callbacks` | setup `fn(string &$format, int &$rate, int &$channels): int`, cleanup `fn()` | setup ≤ 5 s |
| `libvlc_video_set_callbacks` | lock `fn(): array` (plane addresses), unlock `fn(int $picture, array $planes)`, display `fn(int $picture)` | lock ≤ 100 ms |
| `libvlc_video_set_format_callbacks` | setup `fn(string &$chroma, int &$width, int &$height, array &$pitches, array &$lines): int`, cleanup `fn()` | setup ≤ 5 s |
| `libvlc_dialog_set_callbacks` | one Closure per `libvlc_dialog_cbs` field, with the C parameters after `p_data` | never |

Audio samples arrive as a PHP string sized from the format set with `libvlc_audio_set_format()` or the setup callable. Video planes are native addresses: the lock callable returns memory something else owns (an FFI buffer, a framebuffer), and libvlc renders into it. A `null` callable, or a `libvlc_dialog_cbs` field left `null`, is `NULL` to libvlc, as in C.

When each callable is freed: [Lifetime](/docs/{{version}}/ecosystem/standalone-extensions/vlc/architecture/lifetime).
