# Bindings

What ext-vlc binds from libvlc 3.0.24's C API, what it does not and why, and how each C shape becomes PHP.

## Counts

Every function declared `LIBVLC_API` in the 3.0.24 headers except `deprecated.h`: 282, of which 277 are bound. [SUPPORT.md](https://github.com/php-io-extensions/vlc/blob/HEAD/SUPPORT.md) lists each one, grouped by header; `scripts/support.php --check` fails if one goes missing.

## Not bound

* `deprecated.h`: out of scope.
* `libvlc_vprinterr`: it takes a `va_list`. `libvlc_printerr` formats its arguments with PHP's `sprintf()` and covers it.
* `libvlc_media_player_set_evas_object`, `libvlc_vlm_get_media_instance_title`, `libvlc_vlm_get_media_instance_chapter`, `libvlc_vlm_get_media_instance_seekable`: declared, but not exported by the 3.0.24 library.

## Translations

* Opaque types (`libvlc_instance_t *`, `libvlc_media_t *`, `libvlc_media_player_t *`, ...) → final classes of those names, one PHP object per native pointer; `NULL` → `null`. `pointer()` gives the address, `fromPointer()` wraps one.
* Lists libvlc returns (`libvlc_audio_output_list_get`, `libvlc_media_tracks_get`, ...) → handles whose properties are the C fields, read live. libvlc owns them until the list goes back to its `*_release`; a linked list's `p_next` is the next handle.
* `libvlc_event_t`, `libvlc_media_stats_t`, `libvlc_video_viewpoint_t`, `libvlc_dialog_cbs` → value objects. `libvlc_event_t::$u` is the union member for the event type.
* Out-parameters → by-reference: `libvlc_video_get_size($mp, 0, $width, $height)`.
* `argc` / `argv` and every other pointer + count → a PHP list and its count, in C order: `libvlc_new(count($args), $args)`.
* `void *`, `FILE *`, `uintptr_t`, drawables (`libvlc_media_player_set_nsobject`, `_set_xwindow`) and video planes → `int` addresses.
* Strings libvlc allocates → PHP strings, freed by the binding. String parameters accept `null` where C accepts `NULL`.
* Enumerators and `#define` constants → global `int` constants with their C names.
* A function that takes a C callback and its `void *` data → PHP callables in their place: [Callbacks](/docs/{{version}}/ecosystem/standalone-extensions/vlc/architecture/callbacks).
* Reference-counted classes (instance, media, player, media list, list player, media library, renderer item): the binding counts the references it handed out, so a handle reads `0` from `pointer()` after its last `*_release`. A handle it never counted (`fromPointer()`, an event's object) counts as one.
