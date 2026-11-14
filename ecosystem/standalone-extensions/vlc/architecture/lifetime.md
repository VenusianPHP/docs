# Lifetime

When ext-vlc frees the callables it hands libvlc, and how it knows libvlc is done with them.

## Handles

One PHP object per native pointer and class. Dropping the last PHP reference to a handle does not release the native object; the `*_release` does, as in C. For the reference-counted classes the binding counts the references it handed out (creation, `*_retain` / `_hold`, the getters libvlc documents as returning a new reference); after the last `*_release`, the handle reads `0` from `pointer()` and is refused.

## Callables

libvlc holds every callable you pass it as a C function pointer and its data. The binding frees a callable, and whatever it captured, only once libvlc can no longer call it. libvlc 3.0 announces one death, `libvlc_MediaFreed`; for the rest, the binding's counts decide:

| Callables | Freed |
|---|---|
| `libvlc_media_new_callbacks` open, read, seek, close | when libvlc frees the media, on whichever thread drops its last reference. A player or list holding the media keeps them. A close libvlc posted before the free still runs. |
| `libvlc_event_attach` | on `libvlc_event_detach`, or detached before the binding's last release of their object. The VLM's go with `libvlc_vlm_release`; a renderer discoverer's with its release. |
| `libvlc_log_set`, `libvlc_set_exit_handler`, `libvlc_dialog_set_callbacks` | when replaced or unset, or unset in libvlc before the instance's last release. Objects made from the instance may keep libvlc's instance alive; its callables stop here. |
| a player's audio, video and format callables | when replaced, or when libvlc destroys the player. A list player holding the player (`libvlc_media_list_player_set_media_player`, its own player from `_get_media_player`) counts as a reference, so releasing your handle while the list player plays it keeps them. |

An object the script never releases keeps its callables, as libvlc keeps the object. At request end every callable is freed; the small native record libvlc points at stays until its object goes.

`tests/LifetimeTest.php` checks each row through a `__destruct` on state the callables capture. On macOS, `leaks --atExit` over 200 rounds of creating and releasing every callback-holding object reports 0 leaks.
