# Binding surface

Functions, classes, interfaces, enums and constants ext-gtk binds, each one GTK, GDK, GIO, GLib, cairo or graphene call, 1:1.

## Overview

Scope: calls that initialise GTK, register the app with the desktop, hold/release it, pump the default main context, open/close windows, build menu bars from GMenu models and GSimpleAction groups, lay widgets out (box, grid, fixed, paned, notebook), style them (CSS classes and providers), the controls a toolkit window hosts, column-view tables, textures, GL areas, and video through GTK's media backend. Stubs = source of truth; `tests/SurfaceTest.php` fails if a stub declaration is missing from the build.[^stubs]

Naming, all fixed:

* Function on no type = global function, C name (`g_timeout_add`, `g_signal_connect`, `gtk_init`).
* `<prefix>_<type>_<verb>(Type *self, …)` = method on the class named after the type, verb camelCased: `g_application_get_is_registered(app)` → `$app->getIsRegistered()`, `g_main_context_default()` → `GMainContext::default()`.
* `*_new` = static `new()` (`GtkApplication::new()`); wrappers are never built with `new`, except the struct classes (`GdkRectangle`, `GraphenePoint`, `GrapheneSize`, `GrapheneRect`), whose constructor takes the struct's fields.
* GObject interfaces are PHP interfaces implemented by the bound classes whose GType implements them (`GAction`, `GActionMap`, `GActionGroup`, `GListModel`, `GtkSelectionModel`, `GdkPaintable`, `GtkStyleProvider`, `GtkNative`, `GtkRoot`); the interface methods live there. Only the ext's own classes may implement them: a PHP class that does is a fatal error at declaration.
* GEnum/GFlags = backed int enum, prefix dropped (`GApplicationFlags::NON_UNIQUE`). Flags params = `Enum|int` (OR ints).[^headers]
* `GError **` out-param = thrown `GError` exception after the call; the function's own return stays.
* Other out-params = by-reference PHP params in native position; a gboolean result is returned.
* Callback + user_data + GDestroyNotify = one PHP callable param.
* No defaults the native call lacks. Where PHP's static-method inheritance forces one (`GtkApplicationWindow::new(?GtkApplication $application = null)`, `GtkLinkButton::newWithLabel(string $uri, ?string $label = null)`), the stub says so.
* A native NULL is `null`; the stub return is nullable.

## Schema

| Binding | Native |
|---|---|
| `gtk_init()`, `gtk_init_check()`, `gtk_is_initialized()`, `gtk_get_{major,minor,micro}_version()` | same |
| `g_set_prgname()`, `g_get_prgname()` | same; set it before GTK starts: GTK names the X11 `WM_CLASS` after it |
| `g_timeout_add(int $interval, callable $function): int`, `g_idle_add(callable): int` | `g_timeout_add_full`, `g_idle_add_full` (default priorities); callable returns bool = keep |
| `g_unix_fd_add(int $fd, GIOCondition\|int, callable(int $fd, int $condition): bool): int` | `g_unix_fd_add_full` |
| `g_source_remove(int): bool` | same (a guint; GLib criticals an unknown id) |
| `g_signal_connect(GObject, string, callable): int` | `g_signal_connect_closure`; GLib parses the name (a critical and 0 for an unknown one); the handler gets the signal's params, instance first |
| `g_signal_emit_by_name(GObject, string, mixed ...$params): mixed` | `g_signal_emitv` with the signal's own parameter types, each value of its GType's kind (bool, int or int-backed enum within the C type, float, ?string, GObjects of the type, GVariant, GParamSpec, a GtkTextIter / GBytes / address for boxed types, an address for pointers); count checked (ArgumentCountError), other kinds a TypeError; returns the signal's value |
| `g_signal_handler_disconnect`, `g_signal_handler_is_connected` | same |
| `g_object_get_property`, `g_object_set_property` | any GObject property by name, converted as signal arguments are; GLib warns about an unknown, read-only or invalid one |
| `GObject::typeName()`, `pointer()` | `G_OBJECT_TYPE_NAME`, address (the pointer hand-off) |
| `GParamSpec` | name, nick, blurb, value type (`G_PARAM_SPEC_VALUE_TYPE`, by name); `notify::*` handlers receive it |
| `GApplication` | `id_is_valid` (static), application id, flags, is_registered, is_remote, `register(?GCancellable)`, activate, hold, release, quit, `run(array $argv)`; implements GActionMap and GActionGroup |
| `GtkApplication::new(?string, GApplicationFlags\|int): ?GtkApplication` | `gtk_application_new` (NULL for an invalid id) |
| `GtkApplication` (windows) | add/remove_window, get_active_window, get_windows, menubar, `set_accels_for_action` |
| `GAction`, `GActionMap`, `GActionGroup` | name, enabled, state, activate, change_state; add/remove/lookup action; has/list/activate action (`activateAction` returns void) |
| `GSimpleAction`, `GSimpleActionGroup` | new(name, ?type), new_stateful(name, ?type, state), set_enabled, set_state; signals `activate` (`?GVariant`), `change-state` (`GVariant`). Group: new |
| `GVariant` | new_boolean/string/int32/double (`newString` → `?GVariant`), typed getters (`getString(): ?string`; GLib criticals a mismatched type), type string, is_of_type, print |
| `GMenuModel`, `GMenu`, `GMenuItem` | n_items, is_mutable; append/append_item/append_section/append_submenu/prepend/insert/remove/remove_all/freeze; label, detailed action, action+target, attribute values (`accel` etc.), submenu, section |
| `GMainContext` | `default`, `get_thread_default`, `iteration`, `pending`, `wakeup`, `acquire`, `release`, `is_owner`; `pointer()` |
| `GtkWidget` | show/hide (`gtk_widget_show`/`hide`), set/get_visible, realized, mapped, hexpand/vexpand, parent, `insert_action_group(string, ?GActionGroup)`, `activateActionVariant(string, ?GVariant): bool`, grab_focus, `childFocus(GtkDirectionType): bool` (GTK's Tab move inside the widget; on a window from its focus widget), has_focus, add/remove_controller, pick (GTK_PICK_*), get_display |
| `GtkWidget` (layout) | `activate`, halign/valign (`GtkAlign`), size_request, width/height, sensitive, `is_sensitive`, `get_color`, margins, add/remove/has_css_class, `measure`, `computePoint(target, GraphenePoint, ?GraphenePoint &$out): bool`, `computeBounds(target, ?GrapheneRect &$out): bool` (border box), first_child, next_sibling, `getNative(): ?GtkNative`, `getRoot(): ?GtkRoot` |
| `GtkNative`, `GtkRoot` | `getSurface(): ?GdkSurface`, `realize`, `getSurfaceTransform(?float &$x, ?float &$y)`, static `getForSurface`; implemented by windows and popovers |
| `GraphenePoint`, `GrapheneSize`, `GrapheneRect` | the graphene structs (single-precision floats), built from their fields |
| `GtkWindow` | `new(): ?GtkWindow` (transfer none: GTK keeps the toplevel), title, default size, child, present, close, destroy, is_active, transient_for, application, modal, hide_on_close, get_focus |
| `GtkApplicationWindow` | new(app), show_menubar, get_id |
| `GtkAboutDialog` | new; program name, version, copyright, comments, website |
| `GtkBox`, `GtkPopoverMenuBar` | new(orientation, spacing), append/prepend/remove, insert_child_after, reorder_child_after, spacing, homogeneous; new_from_model, menu model |
| `GtkGrid`, `GtkFixed` | new, `attach(child, column, row, width, height)`, remove, get_child_at, row/column spacing; new, put, move, remove, `get_child_position` |
| `GtkPaned`, `GtkNotebook` | start/end child, position, resize/shrink, wide handle; append_page, remove_page, current page, nth_page, page_num, n_pages, tab label text, show_tabs, scrollable; `switch-page` |
| `GtkPopover`, `GtkPopoverMenu` | `setPointingTo(?GdkRectangle)`, `getPointingTo(?GdkRectangle &$rect): bool`, has_arrow, popup, popdown, `setParent`/`unparent` (bound on popovers only: GtkWidget keeps no unparent, which leaves container child pointers dangling), signal `closed`; newFromModel, getMenuModel |
| `GtkCssProvider`, `GdkDisplay` | new, `load_from_string`; get_default, sync; `gtk_style_context_add/remove_provider_for_display(display, GtkStyleProvider, …)`; `GTK_STYLE_PROVIDER_PRIORITY_APPLICATION` |
| `GdkSurface` | width, height; signal `layout(int width, int height)` |
| `GdkGLContext`, enum `GdkGLAPI` | make_current, clear_current, get_current, `realize(): bool` (GError thrown), use_es, version, `getApi(): int` (flags) |
| `GtkGLArea` | new, context, make_current, attach_buffers, queue_render, auto_render, depth/stencil buffers, allowed_apis, required_version, `getError(): ?GError`; signal `render(GtkGLArea, GdkGLContext): bool` |
| `GBytes` | `new(string\|int $data, int $size): ?GBytes` (a string copy up to `$size`; an int is an address, the pointer hand-off; NULL for address 0 with a size), size, data |
| `CairoRegion`, `GdkRectangle` | create, create_rectangle, num_rectangles, get_rectangle, union_rectangle (cairo_status_t) |
| `GdkTexture`, `GdkMemoryTexture`, `GdkMemoryFormat` | width, height; `GdkMemoryTexture::new(width, height, format, GBytes, stride): ?GdkMemoryTexture` (GDK criticals sizes the bytes cannot hold); the fourteen 8-bit formats, the four X8 ones needing GTK 4.14 |
| `GdkPaintable` | current image, flags, intrinsic size and aspect ratio, `computeConcreteSize(…, ?float &$w, ?float &$h)`, invalidate contents/size; implemented by textures and media streams |
| `GdkMemoryTextureBuilder` | GTK 4.16+ (refused on an older running GTK): new, `setBytes(GBytes)`, width, height, stride, format, `setUpdateTexture(?GdkTexture)`, `setUpdateRegion(?CairoRegion)` (all void), `build(): ?GdkTexture` |
| `GdkDmabufTextureBuilder` | GTK 4.14+ on Linux only (refused on an older running GTK): new, display, width, height, fourcc, modifier (a guint64: a negative int is its bits), premultiplied, n_planes, `setFd/setStride/setOffset(int $plane, int)` (the fd is borrowed, never closed), update texture and region (all void), `build(?callable $destroy): ?GdkTexture` (`$destroy` runs once, when GTK finalizes the texture; a failed import throws GTK's `GError`, NULL is returned as null, and neither calls it) |
| `GdkDmabufFormats` | GTK 4.14+: `GdkDisplay::getDmabufFormats()`, n_formats, `getFormat(int): array{int, int}`, contains |
| `GtkLabel` | `new(?string)`, text, wrap, ellipsize, xalign, justify, `set_markup` (GTK warns about malformed markup), use_markup, current_uri; signal `activate-link(uri)` |
| `GtkButton`, `GtkToggleButton`, `GtkLinkButton` | new_with_label, label, `clicked`; active, `toggled`; `new(uri)`, `newWithLabel(uri, ?label)`, uri, visited, `activate-link` |
| `GCancellable`, `GAsyncResult`, `GtkUriLauncher` | new, cancel, is_cancelled; `new(?uri)`, uri, `launch(?GtkWindow, ?GCancellable, ?callable)` (a null callable launches with no callback; no URI comes back as GTK's GError in `launch_finish`; Linux goes through the desktop portal), `launch_finish` (GError thrown) |
| `GtkCheckButton`, `GtkSwitch` | new_with_label, active, label; `toggled`. Switch: new, active; `notify::active` |
| `GtkEntry`, `GtkEntryBuffer` | new, buffer, placeholder text, visibility; `activate`. Buffer: `get_text`, `set_text(string, int $nChars)` |
| `GtkTextView`, `GtkTextBuffer` | new, buffer, editable, wrap mode, monospace, cursor_visible, `getLineYrange(iter, ?int &$y, ?int &$height)`. Buffer: `set_text(string, int $len)`, `getText(GtkTextIter, GtkTextIter, bool): ?string`, begin/end_user_action, tag_table, `getIterAtLine(?GtkTextIter &$iter, int $line): bool` and `getIterAtLineOffset(&$iter, int $line, int $offset): bool` (past the end GTK writes the end), `getIterAtOffset`, start/end iters, apply/remove_tag, `getSelectionBounds(&$start, &$end): bool`, select_range, insert mark, iter at mark, line_count; `changed`, `begin-user-action`, `end-user-action`, `insert-text` (a GtkTextIter) |
| `GtkTextIter` | a copy PHP owns that keeps its buffer alive, valid until the buffer's text changes (then its methods throw `GtkException`, site `text-iter-stale`): line, line_offset, offset, has_tag, get_tags |
| `GtkTextMark`, `GtkTextTag`, `GtkTextTagTable` | —; new(?name), properties via g_object_set_property; add, remove, lookup |
| `GtkScale` | `newWithRange(…): ?GtkScale` (NULL for min ≥ max or step 0), value, set_range, set_increments, draw_value; `value-changed` |
| `GtkStringList`, `GtkStringObject`, `GListModel` | `new(string[])`, append, remove, splice, `getString(int): ?string`; get_string; n_items, item |
| `GtkDropDown` | new_from_strings, selected, selected item, `setModel(?GListModel)`; `notify::selected` |
| `GtkCalendar`, `GDateTime` | new, get_date, select_day; `day-selected`. GDateTime: `newLocal(…): ?GDateTime`, year, month, day_of_month, to_unix |
| `GtkProgressBar`, `GtkSpinner`, `GtkSeparator`, `GtkScrolledWindow`, `GtkAdjustment` | fraction, pulse, pulse_step; spinning; new(orientation); child, policy, h/v adjustment; value, lower, upper, page_size, `value-changed` |
| `GtkEventController` + Key/Motion/Scroll/Focus/Legacy, `GtkGesture`, `GtkGestureSingle`, `GtkGestureClick`, `GtkGestureLongPress` | new, propagation_phase, widget, current_event, scroll unit, set_state, button, current_button, touch_only |
| `GdkEvent` + `GdkButtonEvent`/`GdkTouchEvent`/`GdkScrollEvent` | event_type, `getPosition(?float &$x, ?float &$y): bool` (surface coords), pointer_emulated, modifier_state; button; emulating_pointer; relative_direction (4.20+). Signal GdkEvent arguments are boxed by type |
| `GtkIMContext`, `GtkIMMulticontext` | new; client_widget, filter_keypress, focus_in/out, reset; `commit` |
| `GtkSettings` | get_default (read with g_object_get_property) |
| `GtkPicture` | new, new_for_filename, `set_filename(?string)`, content_fit, `getPaintable(): ?GdkPaintable`, `setPaintable(?GdkPaintable)`, can_shrink |
| `GtkColumnView`, `GtkColumnViewColumn`, `GtkSignalListItemFactory`, `GtkListItem`, `GtkSingleSelection` | `new(?GtkSelectionModel)`, append/remove_column, model, separators; `new(?string, ?GtkListItemFactory)`, title, expand, resizable; `setup`/`bind`/`unbind`/`teardown`; position, item, child; `new(?GListModel)`, selected, autoselect, can_unselect; `GTK_INVALID_LIST_POSITION`; column view `scrollTo(pos, ?column, flags, ?GtkScrollInfo)` with `GTK_LIST_SCROLL_*` |
| `GtkTreeListModel`, `GtkTreeListRow`, `GtkTreeExpander`, `GtkScrollInfo` | `new(GListModel, passthrough, autoexpand, callable)` (callable(GObject item): ?GListModel; anything else = leaf; held until finalize), getRow / getChildRow (null past the end); row item, expanded (+set), isExpandable, depth, position, parent, getChildRow (null while collapsed); expander `new()`, child, listRow; scroll info (boxed, refcounted) `new()`, enableHorizontal / enableVertical (+set) |
| `GtkMediaStream`, `GtkMediaFile`, `GtkVideo` | play, pause, playing, ended, `get_error(): ?GError`, seek (µs), is_seekable, timestamp, duration, muted, loop, has_video; `notify::playing/ended/error`. MediaFile: `new()`, `new_for_filename` (both need GTK initialised), set_filename, clear. Video: new, media_stream, autoplay, loop. Without a media backend `GtkMediaFile::new()->typeName()` is `GtkNoMediaFile` |
| functions, enums, constants | gdk_keyval_to_unicode, gdk_keyval_to_lower; GtkPropagationPhase, GdkScrollUnit, GdkScrollRelativeDirection (4.20+); GTK_EVENT_CONTROLLER_SCROLL_*, GDK_*_MASK |

GTK judges its own arguments: a missing parent, a scale range, a list position, an action name, a bad UTF-8 string reaches GTK, which answers with its critical or warning and its own result. The ext checks only what has no native form (an int outside the C type, a value of the wrong kind for a GValue) and the crash guards in [errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/errors-and-threads).

Behaviour confirmed on both platforms: `register()` emits `startup`, which initialises GTK. `run()` ends with shutdown, after which the app is unregistered. macOS: GTK's backend makes the process a regular app on startup (Dock icon). Linux: registration owns the app id on the session bus.

[^stubs]: Stub files, one per type
[^headers]: GIO enums (GApplicationFlags)
