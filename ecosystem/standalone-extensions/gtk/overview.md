# Overview

![CI](https://github.com/php-io-extensions/gtk/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/gtk/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/gtk/actions/workflows/ci.yml)

1:1 PHP bindings of GTK 4 and the GLib main loop GTK runs on, written directly
in C against the Zend API. C functions keep their names (`g_timeout_add`,
`g_signal_connect`); functions on a type are methods of the class named after it
(`g_application_register(app)` is `$app->register()`). No defaults, no
composites: behaviour is composed by the caller.

Linux first, macOS too. GTK 4.12+, GLib 2.74+, PHP 8.4+, NTS and ZTS.

## What is bound

The calls that initialise GTK, register the application with the desktop, hold
and release it, pump the main context, sleep with a budget, wake a sleep, open
and close windows, and build menu bars from menu models and actions:

| | Native |
|---|---|
| functions | `gtk_init`, `gtk_init_check`, `gtk_is_initialized`, `gtk_get_{major,minor,micro}_version`, `g_set_prgname`, `g_get_prgname`, `g_timeout_add`, `g_idle_add`, `g_unix_fd_add`, `g_source_remove`, `g_signal_connect`, `g_signal_emit_by_name`, `g_signal_handler_disconnect`, `g_signal_handler_is_connected` |
| `GObject` | `G_OBJECT_TYPE_NAME` |
| `GApplication` | `g_application_id_is_valid`, `get_application_id`, `get_flags`, `get_is_registered`, `get_is_remote`, `register`, `activate`, `hold`, `release`, `quit`, `run`, `g_action_map_add/remove/lookup_action`, `g_action_group_has/list/activate_action` |
| `GtkApplication` | `gtk_application_new`, `add_window`, `remove_window`, `get_active_window`, `get_windows`, `get_menubar`, `set_menubar`, `set_accels_for_action`, `get_accels_for_action` |
| `GtkWidget` | `set_visible` (as `show`/`hide`/`setVisible`), `get_visible`, `get_realized`, `get_mapped`, `get/set_hexpand`, `get/set_vexpand`, `get_parent`, `insert_action_group`, `activate_action_variant`, `activate`, `get/set_halign`, `get/set_valign`, `get/set_size_request`, `get_width`, `get_height`, `get/set_sensitive`, `is_sensitive`, `get_color`, `set_margin_start/end/top/bottom`, `add/remove/has_css_class`, `measure`, `compute_bounds`, `get_first_child`, `get_next_sibling`, `get_native`, `get_root`, `gtk_native_get_surface` (as `getSurface`), `grab_focus`, `has_focus` |
| `GtkWindow` | `new`, `get/set_title`, `get/set_default_size`, `get/set_child`, `present`, `close`, `destroy`, `is_active`, `get/set_transient_for`, `get/set_application`, `get/set_modal`, `get/set_hide_on_close`, `get_focus` |
| `GtkApplicationWindow` | `new`, `get/set_show_menubar`, `get_id` |
| `GtkAboutDialog` | `new`, `get/set_program_name`, `get/set_version`, `get/set_copyright`, `get/set_comments`, `get/set_website` |
| `GtkBox` | `new`, `append`, `prepend`, `remove`, `insert_child_after`, `reorder_child_after`, `get/set_spacing`, `get/set_homogeneous` |
| `GtkGrid`, `GtkFixed` | `new`, `attach`, `remove`, `get_child_at`, `get/set_row_spacing`, `get/set_column_spacing`; `new`, `put`, `move`, `remove`, `get_child_position` |
| `GdkGLContext`, `GdkGLAPI`, `GtkGLArea` | `make_current`, `clear_current`, `get_current`, `realize`, `get_use_es`, `get_version`, `get_api`; `new`, `get_context`, `make_current`, `attach_buffers`, `queue_render`, `get/set_auto_render`, `get/set_has_depth_buffer`, `get/set_has_stencil_buffer`, `get/set_allowed_apis`, `set_required_version`, `get_error` (signal `render`) |
| `GtkCssProvider`, `GdkDisplay`, `GdkSurface` | `new`, `load_from_string`; `get_default`, `sync`; `get_width`, `get_height` (signal `layout`); functions `gtk_style_context_add/remove_provider_for_display` |
| `GtkLabel` | `new`, `get/set_text`, `get/set_wrap`, `set_ellipsize`, `get/set_xalign`, `set_justify`, `set_markup`, `get/set_use_markup`, `get_current_uri` |
| `GtkButton`, `GtkToggleButton`, `GtkCheckButton`, `GtkSwitch` | `new_with_label`, `get/set_label`; `new_with_label`, `get/set_active`; `new_with_label`, `get/set_active`, `get/set_label`; `new`, `get/set_active` |
| `GtkLinkButton` | `new`, `new_with_label`, `get/set_uri`, `get/set_visited` |
| `GCancellable`, `GAsyncResult`, `GtkUriLauncher` | `new`, `cancel`, `is_cancelled`; —; `new`, `get/set_uri`, `launch`, `launch_finish` |
| `GtkEntry`, `GtkEntryBuffer` | `new`, `get_buffer`, `get/set_placeholder_text`, `get/set_visibility`; `get/set_text` |
| `GtkTextView`, `GtkTextBuffer` | `new`, `get_buffer`, `get/set_editable`, `set_wrap_mode`; `set_text`, `get_text` (by offsets), `begin/end_user_action` |
| `GtkScale` | `new_with_range`, `gtk_range_get/set_value`, `gtk_range_set_range`, `gtk_range_set_increments`, `get/set_draw_value` |
| `GtkDropDown`, `GtkStringList`, `GtkStringObject` | `new_from_strings`, `get/set_selected`, `get_selected_item`, `set_model`; `new`, `append`, `remove`, `splice`, `get_string`, `g_list_model_get_n_items`; `get_string` |
| `GtkCalendar`, `GDateTime` | `new`, `get_date`, `select_day`; `new_local`, `get_year`, `get_month`, `get_day_of_month`, `to_unix` |
| `GtkProgressBar`, `GtkSpinner` | `new`, `get/set_fraction`, `pulse`, `set_pulse_step`; `new`, `get/set_spinning` |
| `GtkEventController` (`Key`, `Motion`, `Scroll`, `Focus`), `GtkGesture`, `GtkGestureSingle`, `GtkGestureClick` | `new` (scroll takes `GTK_EVENT_CONTROLLER_SCROLL_*` flags), `get/set_propagation_phase`, `get_widget`, `get_current_event` (`GdkEvent`, `GdkScrollEvent` with `get_relative_direction` on GTK 4.20+); scroll `get/set_flags`, `get_unit`; gesture `set_state` (`GtkEventSequenceState`); single `get/set_button`, `get_current_button`, `get/set_touch_only`; `GtkGestureLongPress` `new`; signals through `g_signal_connect` |
| `GtkEventControllerLegacy`, `GdkEvent` (`GdkButtonEvent`, `GdkTouchEvent`, `GdkScrollEvent`) | `new`; event `get_event_type`, `get_position`, `get_pointer_emulated`, `get_modifier_state`; button `get_button`; touch `get_emulating_pointer`; enum `GdkEventType` |
| `GtkIMContext`, `GtkIMMulticontext` | multicontext `new`; `set_client_widget`, `filter_keypress`, `focus_in`, `focus_out`, `reset`; `commit` signal |
| `GtkWidget` controllers, coordinates | `add_controller`, `remove_controller`, `compute_point`, `pick` (`GTK_PICK_*`); `GtkWindow` `get_surface_transform` (`gtk_native_get_surface_transform`) |
| `GtkSettings`, properties | `get_default`; `g_object_get_property` (any GObject property, as a signal argument converts) |
| Keyvals | `gdk_keyval_to_unicode`, `gdk_keyval_to_lower`; `GDK_*_MASK` constants, enums `GtkPropagationPhase`, `GdkScrollUnit`, `GdkScrollRelativeDirection` (4.20+) |
| `GtkPicture`, `GtkSeparator`, `GtkScrolledWindow` | `new`, `new_for_filename`, `set_filename`, `get/set_content_fit`, `get/set_paintable`, `get/set_can_shrink`; `new`; `new`, `get/set_child`, `set_policy` |
| `GdkTexture`, `GdkMemoryTexture`, `GdkMemoryTextureBuilder` | `get_width`, `get_height`; `new` from bytes or an address in a `GdkMemoryFormat`; GTK 4.16+ builder: fluent setters, bytes from a string or an address with a length, an update texture and an update region of `[x, y, width, height]` rects, `build` (null when unset) |
| `GdkDmabufTextureBuilder` | Linux, GTK 4.14+: fluent `setDisplay`, `setWidth`, `setHeight`, `setFourcc`, `setModifier`, `setPremultiplied`, `setNPlanes`, per plane `setFd` (borrowed: keep it open while the textures live), `setStride`, `setOffset`, `setUpdateTexture`, `setUpdateRegion`, `build(?callable $destroy)` (`$destroy` runs once GTK has finalized the texture and is done with the fds; a failed import throws its `GError`) |
| `GdkDmabufFormats` | GTK 4.14+, from `GdkDisplay::getDmabufFormats()`: `getNFormats`, `getFormat` (`[fourcc, modifier]`), `contains(fourcc, modifier)`; empty off Linux |
| `GtkColumnView`, `GtkColumnViewColumn` | `new`, `append/remove_column`, `get/set_model`, `set_show_row/column_separators`; `new`, `get/set_title`, `set_expand`, `set_resizable` |
| `GtkSignalListItemFactory`, `GtkListItem`, `GtkSingleSelection` | `new` (signals `setup`, `bind`, `unbind`, `teardown`); `get_position`, `get_item`, `get/set_child`; `new`, `get/set_selected`, `get_selected_item`, `set_autoselect`, `set_can_unselect`, `get_model` |
| `GtkMediaStream`, `GtkMediaFile`, `GtkVideo` | `play`, `pause`, `get/set_playing`, `get_ended`, `get_error`, `seek`, `is_seekable`, `get_timestamp`, `get_duration`, `get/set_muted`, `get/set_loop`, `has_video`; `new_for_filename`, `set_filename`, `clear`; `new`, `get/set_media_stream`, `get/set_autoplay`, `set_loop`; function `gtk_media_backend_available` |
| `GtkPopoverMenuBar` | `new_from_model`, `get/set_menu_model` |
| `GtkPopover`, `GtkPopoverMenu` | `set/get_pointing_to` (four ints; get refused with no parent), `set/get_has_arrow`, `popup`, `popdown`, signal `closed`; menu `new_from_model`, `get_menu_model`; attached with its own `setParent` / `unparent` (`gtk_widget_set_parent`, bound for popovers only) |
| `GMenuModel`, `GMenu`, `GMenuItem` | `get_n_items`, `is_mutable`; `new`, `append`, `append_item`, `append_section`, `append_submenu`, `prepend`, `insert`, `remove`, `remove_all`, `freeze`; `new`, `set_label`, `set_detailed_action`, `set_action_and_target_value`, `set/get_attribute_value`, `set_submenu`, `set_section` |
| `GSimpleAction`, `GSimpleActionGroup` | `new`, `new_stateful`, `set_enabled`, `set_state`, `g_action_get_name/enabled/state`, `g_action_activate`, `g_action_change_state`; `new`, `g_action_map_add/remove/lookup_action`, `g_action_group_has/list/activate_action` |
| `GVariant` | `new_boolean/string/int32/double`, `get_boolean/string/int32/double`, `get_type_string`, `is_of_type`, `print` |
| `GMainContext` | `default`, `get_thread_default`, `iteration`, `pending`, `wakeup`, `acquire`, `release`, `is_owner` |

Enums: `GApplicationFlags`, `GIOCondition`, `GtkOrientation`, `GtkAlign`,
`PangoEllipsizeMode`, `GtkJustification`, `GtkWrapMode`, `GtkContentFit`,
`GtkPolicyType`. Constants: `G_SOURCE_CONTINUE`, `G_SOURCE_REMOVE`,
`GTK_STYLE_PROVIDER_PRIORITY_APPLICATION`, `GTK_INVALID_LIST_POSITION`. Errors:
`GError` (a GError, with its `domain`; also what `GtkMediaStream::getError()`
returns), `GtkException` (a call refused before reaching GTK). The stubs in
`stubs/` are the full declaration.

Video needs GTK's media backend module: `libgtk-4-media-gstreamer` on Debian
(the installer checks), none in Homebrew's gtk4 (the installer warns;
`gtk_media_backend_available()` answers false and `GtkVideo` shows nothing).

## Example

```php
$app = GtkApplication::new('com.example.App', GApplicationFlags::DEFAULT_FLAGS);
g_signal_connect($app, 'activate', fn (GtkApplication $app) => null);
$app->register();   // startup: GTK initialises
$app->hold();

$ctx = GMainContext::default();

// Sleep up to 16 ms, or until a source is ready, dispatching what is.
$budget = g_timeout_add(16, fn (): bool => G_SOURCE_REMOVE);
$ctx->iteration(true);

// Wake on a descriptor (a kqueue or epoll fd works: it turns readable when its own events are pending).
g_unix_fd_add($fd, GIOCondition::IN, fn (int $fd, int $condition): bool => G_SOURCE_CONTINUE);

$app->release();
```

## Install

```bash
bash install-debian-trixie.sh   # Debian, Ubuntu, Raspberry Pi OS (needs libgtk-4-dev)
bash install-macos.sh           # Homebrew php@8.4 and php@8.4-zts (needs brew install gtk4)
```

Or with PIE: `pie install php-io-extensions/gtk`.

`venusian build` reads the system packages from `extra.venusian.system` in composer.json: apt packages to build with and the run-time ones a `.deb` depends on or recommends, and the Homebrew ones.

## Test

```bash
composer install
php vendor/bin/pest
php examples/smoke.php          # bridge: register, pump, sleep, wake; prints SMOKE_OK
php examples/window-smoke.php   # window, menu bar, actions, close-request; prints SMOKE_OK
```

On Linux over SSH, export the session's `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR` and
`DBUS_SESSION_BUS_ADDRESS` first. The video playback test runs where a media
backend is installed and is skipped elsewhere. Design notes live in the OKF bundle under `.okf/`.

## License

MIT
