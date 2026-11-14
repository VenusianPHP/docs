# Errors

What ext-vlc returns, what it throws, and the calls it refuses.

## Results pass through

libvlc reports errors as return values (`-1`, `NULL`) with a message in `libvlc_errmsg()`; they are returned, never thrown. Marshalling throws `TypeError`: a list element of the wrong class or type.

## Refusals

The extension declines a call only where libvlc would crash the process. Each refusal has a probe test that runs the call with the check off on a probe build and shows the crash.

| Site | Refused | Crash it prevents |
|---|---|---|
| `vlc-no-instance` | `libvlc_clearerr()` before the process's first `libvlc_new()` (`Error`) | libvlc creates its error state in the first `libvlc_new()`; before it, SIGABRT |
| `vlc-released-handle` | a handle after its last counted `*_release`, or a list element after its list's `*_release` (`ValueError`) | libvlc dereferences the NULL handle: SIGSEGV |
| `vlc-list-count` | a count past its list (`libvlc_new`, the `*_release(list, count)` calls) (`ValueError`) | libvlc reads that many elements: past the array |
| `vlc-printerr-no-instance` | `libvlc_printerr()` before the process's first `libvlc_new()` (`Error`) | it frees the uncreated error slot: SIGABRT |
| `vlc-discoverer-not-running` | `libvlc_media_discoverer_stop()` on a discoverer that is not running (`ValueError`) | libvlc stops a services discovery that is NULL: SIGSEGV |

Typed instead of refused: `libvlc_media_list_player_set_media_player()` takes a player and `libvlc_vlm_add_broadcast()`, `_add_vod()` and `_change_media()` take a name, never `null`: libvlc dereferences both. Every other string parameter accepts `null` as C does; each was called with `null` in its own process and none crashed.

Not refused: `libvlc_errmsg()` before the first `libvlc_new()`. It reads another library's thread-local slot and returns garbage, but does not crash.
