# Binding surface

Functions, classes, enums and constants ext-gtk binds, each one GTK, GIO or GLib call.

## Overview

Scope: calls that initialise GTK, register the app with the desktop, hold/release it, pump the default main context, sleep with a budget, wake a sleep, open/close windows, build menu bars from GMenu models and GSimpleAction groups, lay widgets out (box, grid, fixed), style them (CSS classes and providers), the controls a toolkit window hosts, column-view tables, and video through GTK's media backend. Stubs = source of truth; `tests/SurfaceTest.php` fails if a stub declaration is missing from the build.[^stubs]

Naming, all fixed:

* Function on no type = global function, C name (`g_timeout_add`, `g_signal_connect`, `gtk_init`).
* `<prefix>_<type>_<verb>(Type *self, …)` = method on the class named after the type, verb camelCased: `g_application_get_is_registered(app)` → `$app->getIsRegistered()`, `g_main_context_default()` → `GMainContext::default()`.
* `*_new` = static `new()` (`GtkApplication::new()`); wrappers are never built with `new`.
* GEnum/GFlags = backed int enum, prefix dropped (`GApplicationFlags::NON_UNIQUE`). Flags params = `Enum|int` (OR ints).[^headers]
* `GError **` out-param = thrown `GError` exception; the function's own return stays.
* Callback + user_data + GDestroyNotify = one PHP callable param.

## Schema

| Binding | Native |
|---|---|
| `gtk_init()`, `gtk_init_check()`, `gtk_is_initialized()`, `gtk_get_{major,minor,micro}_version()` | same |
| `g_set_prgname()`, `g_get_prgname()` | same; set it before GTK starts: GTK names the X11 `WM_CLASS` after it; an empty name is a ValueError |
| `g_timeout_add(int $interval, callable $function): int` | `g_timeout_add_full` (default priority); callable returns bool = keep |
| `g_idle_add(callable): int` | `g_idle_add_full` (default idle priority) |
| `g_unix_fd_add(int\|resource\|Socket $fd, GIOCondition\|int, callable(int $fd, int $condition): bool): int` | `g_unix_fd_add_full` |
| `g_source_remove(int): bool` | same; false for an id no longer in the default context |
| `g_signal_connect(GObject, string, callable): int` | `g_signal_connect_closure_by_id`; handler gets the signal's params, instance first |
| `g_signal_emit_by_name(GObject, string, mixed ...$params): mixed` | `g_signal_emitv` with the signal's own parameter types: bool, int (enums/flags; an int-backed enum case passes its value, a pure enum is refused), float, ?string, GObjects of the declared type or null; count checked (ArgumentCountError), other types refused (ValueError); returns the signal's value |
| `g_signal_handler_disconnect`, `g_signal_handler_is_connected` | same |
| `GObject::typeName()`, `pointer()` | `G_OBJECT_TYPE_NAME`, address |
| `GApplication` | `id_is_valid` (static), `get_application_id`, `get_flags`, `get_is_registered`, `get_is_remote`, `register`, `activate`, `hold`, `release`, `quit`, `run(array $argv)`; GActionMap add/remove/lookup (lookup `?GObject`: GTK may add non-simple actions); GActionGroup has/list/activate |
| `GtkApplication::new(?string, GApplicationFlags\|int)` | `gtk_application_new` |
| `GtkWidget` | show/hide/set_visible, get_visible, get_realized, get_mapped, hexpand/vexpand, get_parent, insert_action_group (any GActionGroup), activate_action (variant form), grab_focus, has_focus (window's focus widget in an active window) |
| `GtkWindow` | new (transfer none: GTK keeps the toplevel), title, default size (`[w, h]`), child, present, close, destroy, is_active, transient_for, application, modal, hide_on_close, get_focus (an entry's focus is its inner GtkText) |
| `GtkApplicationWindow` | new(app) — the application is a declared-optional, runtime-required parameter because PHP holds static methods to the parent's signature; show_menubar; get_id |
| `GtkAboutDialog` | new; program name, version, copyright, comments, website |
| `GtkBox`, `GtkPopoverMenuBar` | new(orientation, spacing), append/prepend/remove; new_from_model, menu model |
| `GtkPopover`, `GtkPopoverMenu` | setPointingTo(x, y, w, h) (no negative size), getPointingTo(): ?array (null until set; refused with no parent, as GTK then measures the parent), has_arrow, popup, popdown, signal `closed`; GtkPopoverMenu::newFromModel, getMenuModel. Attach with `GtkPopover::setParent()` (refused while parented), take off with `unparent()`: `gtk_widget_set_parent`/`unparent` bound on popovers only, as GtkWidget keeps no unparent (dangling container pointers) |
| `GMenuModel`, `GMenu`, `GMenuItem` | n_items, is_mutable; append/append_item/append_section/append_submenu/prepend/insert/remove/remove_all/freeze; label, detailed action, action+target, attribute values (`accel` etc.), submenu, section |
| `GSimpleAction` | new(name, ?type), new_stateful(name, ?type, state), enabled, state, name, activate, change_state; signals `activate` (`?GVariant`), `change-state` (`GVariant`) |
| `GSimpleActionGroup` | new; GActionMap add/remove/lookup; GActionGroup has/list/activate |
| `GVariant` | new_boolean/string/int32/double, typed getters, type string, is_of_type, print |
| `GtkApplication` (windows) | add/remove_window, get_active_window, get_windows, menubar, accels for action |
| `GMainContext` | `default`, `get_thread_default`, `iteration`, `pending`, `wakeup`, `acquire`, `release`, `is_owner`; `pointer()` |
| `GtkWidget` (layout) | `activate`, halign/valign (`GtkAlign`), size_request (`[w, h]`, -1 unset), get_width/height, sensitive, `is_sensitive` (own flag and every ancestor's), `get_color(): [r, g, b, a]` (CSS-computed foreground), margin start/end/top/bottom, add/remove/has_css_class, `measure(GtkOrientation, int): {minimum, natural, minimumBaseline, naturalBaseline}`, `compute_bounds(target): ?[x, y, w, h]` (border box, which includes CSS padding and border; `get_width`/`get_height` are the content box), get_first_child, get_next_sibling (child order), get_native, get_root, `getSurface()` = `gtk_native_get_surface` on a GtkNative, null otherwise |
| `GtkBox` (more) | insert_child_after, reorder_child_after (`null` sibling = first), spacing, homogeneous |
| `GtkGrid` | new, `attach(child, column, row, width, height)` (width/height < 1 refused), remove, `get_child_at`, row/column spacing |
| `GtkFixed` | new, put, move, remove, `get_child_position` (`[x, y]` floats; GTK applies the transform at layout, so read after the fixed has been allocated) |
| `GtkCssProvider`, `GdkDisplay` | new (transfer full), `load_from_string`; `get_default`, `sync` (`gdk_display_sync`: a round trip on Wayland); `gtk_style_context_add_provider_for_display(display, provider, int $priority)`, `gtk_style_context_remove_provider_for_display`; `GTK_STYLE_PROVIDER_PRIORITY_APPLICATION` |
| `GdkSurface` | get_width, get_height; signal `layout(int width, int height)` |
| `GdkGLContext`, enum `GdkGLAPI` (GL 1, GLES 2) | make_current, clear_current (static), get_current (static, null when none), realize (GError → GtkException), get_use_es, get_version (`[major, minor]`), get_api |
| `GtkGLArea` | `new`, get_context (null before realize), make_current, attach_buffers, queue_render, get/set auto_render, has_depth_buffer, has_stencil_buffer, get/set allowed_apis (GdkGLAPI flags as int), set_required_version, get_error (message or null); signal `render(GtkGLArea, GdkGLContext): bool` with the context current and the area's framebuffer bound |
| `GdkTexture`, `GdkMemoryTexture`, `GdkMemoryFormat` | get_width, get_height; `gdk_memory_texture_new(width, height, format, bytes, stride)` with the bytes as a PHP string (copied into a GBytes) or as an address — an ext-fb buffer's `pointer()`, trusted, the rows the width, height and stride name are read there; refusing a stride shorter than a row and bytes that do not hold every row; the fourteen 8-bit formats, the four X8 ones (opaque) needing GTK 4.14 |
| `GtkWidget::getDisplay()` | `gtk_widget_get_display()`: the widget's `GdkDisplay` |
| `GdkMemoryTextureBuilder` | GTK 4.16+: `gdk_memory_texture_builder_new` (refused on an older running GTK, naming the version; the class is compiled only when headers are 4.16+), fluent `setBytes(string\|int, ?int $length)` (an address is trusted, `$length` bytes are read there), `setWidth/setHeight/setStride` (refusing negatives), `setFormat(GdkMemoryFormat)`, `setUpdateTexture(?GdkTexture)`, `setUpdateRegion(?array)` of `[x, y, width, height]` rects into one cairo region, `build(): ?GdkTexture` (transfer full; null when width, height, format, stride or bytes is unset) |
| `GdkDmabufTextureBuilder` | GTK 4.14+ on Linux only (compiled under `GTK_CHECK_VERSION(4, 14, 0) && defined(__linux__)`; absent elsewhere): `gdk_dmabuf_texture_builder_new` (refused on an older running GTK), fluent `setDisplay(GdkDisplay)`, `setWidth/setHeight/setFourcc/setNPlanes` (refusing negatives and values past the C type; at most 4 planes), `setModifier` (a guint64: a negative int is its bits), `setPremultiplied(bool)`, `setFd/setStride/setOffset(int $plane, int)` (plane 0-3; fd -1 unsets; the fd is borrowed, never closed: it must stay open while textures built over it live), `setUpdateTexture(?GdkTexture)`, `setUpdateRegion(?array)` as the memory builder's, `build(?callable $destroy = null): GdkTexture` (`$destroy` is GTK's destroy notify: called once, when the texture is finalized and GTK is done with the fds, so a borrowed fd can close and its buffer be reused then; a failed import throws GTK's `GError` and never calls it; no texture without a GError is a `GtkException`) |
| `GdkDmabufFormats` | GTK 4.14+ (compiled under `GTK_CHECK_VERSION(4, 14, 0)`), boxed, made only by `GdkDisplay::getDmabufFormats()` (refused on an older running GTK): `getNFormats()`, `getFormat(int $idx): array{int, int}` (fourcc, modifier; an index out of range is a ValueError), `contains(int $fourcc, int $modifier): bool`. Off Linux the list is empty. The Pi's GTK 4.18 on V3D lists 214, `DRM_FORMAT_ABGR8888` and `XBGR8888` linear among them |
| `GtkLabel` | `new(?string)`, text, wrap, `set_ellipsize(PangoEllipsizeMode)`, xalign, `set_justify(GtkJustification)`, `set_markup` (Pango plus `<a href>`, sets use_markup; malformed markup throws GError, label unchanged), use_markup, `get_current_uri`; signal `activate-link(uri)` (true = handled) |
| `GtkButton`, `GtkToggleButton` | `new_with_label`, label; signal `clicked`. ToggleButton extends Button: active, `toggled`. `activate()` on a realized button emits `clicked` after GTK's 250 ms pressed state |
| `GtkLinkButton` | extends GtkButton: `new(uri)` (the URI is the label), `new_with_label(uri, ?label)`, uri (set resets visited), visited; signal `activate-link` (true = handled, else GTK opens the URI) |
| `GCancellable`, `GAsyncResult`, `GtkUriLauncher` | `new`, `cancel`, `is_cancelled`; a ready callback's result (the `GTask` GType boxes as it); `new(?uri)`, uri, `launch(?parent, ?cancellable, callable)` (callable runs once with (launcher, result); no URI = GtkException; Linux goes through the desktop portal), `launch_finish` (GError thrown; a result not from this launcher's launch is a ValueError) |
| `GtkCheckButton`, `GtkSwitch` | `new_with_label`, active, label (nullable); `toggled`. Switch: new, active; `notify::active`. CheckButton is not a GtkButton in GTK 4 |
| `GtkEntry`, `GtkEntryBuffer` | new, `get_buffer`, placeholder text, visibility; `activate`. Buffer: `get_text`, `set_text(string, int $nChars = -1)`; `notify::text` |
| `GtkTextView`, `GtkTextBuffer` | new, `get_buffer`, editable, `set_wrap_mode(GtkWrapMode)`. Buffer: `set_text(string, int $len = -1)`, `get_text(int $start, int $end, bool $hidden = false)` over `get_iter_at_offset` iters (-1 end = G_MAXINT), `begin/end_user_action` (nest; GTK wraps a user's edit in one); `changed`, `begin-user-action`, `end-user-action` |
| `GtkScale` | `new_with_range(GtkOrientation, float, float, float)`, GtkRange value/set_range/set_increments (arrow key and page step), draw_value; `value-changed` |
| `GtkStringList`, `GtkStringObject` | `new(string[])` (non-strings refused), append, `remove(int)` (out of range refused), `splice(position, nRemovals, string[])` (one items-changed; range refused), `get_string(int): ?string`, `g_list_model_get_n_items`; `get_string` |
| `GtkDropDown` | `new_from_strings(string[])`, selected (`GTK_INVALID_LIST_POSITION` = none), `get_selected_item`, `set_model(?GObject)` (GListModel required); `notify::selected` |
| `GtkCalendar`, `GDateTime` | new, `get_date(): GDateTime` (new ref, boxed), `select_day(GDateTime)` inside `G_GNUC_BEGIN/END_IGNORE_DEPRECATIONS` (4.20 deprecates it for `set_date`, which 4.18 lacks); `day-selected` fires on a change only. GDateTime: `new_local(y, m, d, h, min, float s)` (invalid → ValueError), year, month, day_of_month, `to_unix` (system-local) |
| `GtkProgressBar`, `GtkSpinner` | new, fraction, pulse, pulse_step; new, spinning |
| `GtkEventController` + `Key`/`Motion`/`Scroll`/`Focus`, `GtkGesture`, `GtkGestureSingle`, `GtkGestureClick` | new, propagation_phase, widget, current_event (GdkEvent; GdkScrollEvent relative_direction, GTK 4.20+); scroll flags, unit; GtkGesture::setState(GtkEventSequenceState) (true when a sequence changed); single button, current_button, touch_only; GtkGestureLongPress new |
| `GtkEventControllerLegacy`, `GdkEvent` + `GdkButtonEvent`/`GdkTouchEvent`/`GdkScrollEvent` | new; event_type (GdkEventType), position (surface coords), pointer_emulated, modifier_state; button; emulating_pointer. Signal GdkEvent arguments are boxed by type |
| `GtkIMContext`, `GtkIMMulticontext` | multicontext new; client_widget, filter_keypress(GdkEvent), focus_in/out, reset; commit signal |
| `GtkWidget`, `GtkWindow` | add_controller (takes its own reference), remove_controller, compute_point, pick (GTK_PICK_* constants); window surface_transform |
| `GtkSettings`, `g_object_get_property` | get_default; any GObject property by name (ValueError for an unknown one), converted as signal arguments are |
| functions, enums, constants | gdk_keyval_to_unicode, gdk_keyval_to_lower; GtkPropagationPhase, GdkScrollUnit, GdkScrollRelativeDirection (4.20+); GTK_EVENT_CONTROLLER_SCROLL_*, GDK_*_MASK (flag types as int constants) |
| `GtkPicture` | `new`, `new_for_filename`, `set_filename(?string)` (missing file → `get_paintable()` null), content_fit (`GtkContentFit`), `get_paintable(): ?GObject`, `set_paintable(?GObject)` (a GdkPaintable such as a texture; anything else is a TypeError), can_shrink |
| `GtkSeparator`, `GtkScrolledWindow` | `new(GtkOrientation)`; new, child (a non-GtkScrollable child is wrapped: `get_child` returns the GtkViewport), `set_policy(GtkPolicyType, GtkPolicyType)` |
| `GtkColumnView`, `GtkColumnViewColumn` | `new(?GObject)` (GtkSelectionModel required, (transfer full) honoured with a new ref), append/remove_column, model, row/column separators; `new(?string, ?GtkSignalListItemFactory)` (factory (transfer full), new ref), title, expand, resizable |
| `GtkSignalListItemFactory`, `GtkListItem` | new; signals `setup`, `bind`, `unbind`, `teardown` each `(factory, GtkListItem)`. ListItem: position, `get_item(): ?GObject`, child |
| `GtkSingleSelection` | `new(?GObject)` (GListModel required, new ref), selected, selected_item, autoselect, can_unselect, model; `notify::selected`; `GTK_INVALID_LIST_POSITION` |
| `GtkMediaStream`, `GtkMediaFile`, `GtkVideo` | play, pause, playing, ended, `get_error(): ?GError` (object, not thrown), `seek(int µs)`, is_seekable, timestamp, duration (µs), muted, loop, has_video; `notify::playing/ended/error`. MediaFile: `new_for_filename` (needs GTK initialised), `set_filename(?string)`, clear. Video: new, media_stream, autoplay, loop. `gtk_media_backend_available(): bool` (needs GTK initialised) |

Validation: action names, detailed action names, GVariant type strings, parameter/state types and accelerators are checked before the call; GLib would otherwise log a critical and do nothing. The widget calls check the same way: a child's parent (inserts need none, removes and moves need this container), native int/int16/guint ranges (margins, size requests, spacings, grid cells, text offsets, list positions, seek), scale ranges (`min < max`, `step != 0`), UTF-8 and lengths on entry and text buffers (an entry `nChars` past the string makes GTK read past it), a column already in a view. `gtk_widget_unparent` is not bound: GTK reserves it for widget implementations, and on a window's or scrolled window's child it leaves the container's child pointer dangling. Each container binds its own `remove` or `setChild(null)`. Typed GVariant getters refuse a mismatched variant with GtkException.

Signal parameter marshalling: objects/interfaces boxed; GVariant boxed; bool, ints, floats, strings as PHP scalars; enums/flags as int; pointers and boxed types as addresses. Return values set back into the signal's typed return GValue.

Behaviour confirmed on both platforms: `register()` emits `startup`, which initialises GTK. `run()` ends with shutdown, after which the app is unregistered. macOS: GTK's backend makes the process a regular app on startup (Dock icon); GTK has no call to withdraw it. Linux: registration owns the app id on the session bus; the taskbar lists windows, not processes.

[^stubs]: Stub files, one per type
[^headers]: GIO enums (GApplicationFlags)
