# Layout and styling

GtkBox, GtkGrid and GtkFixed containers; alignment, expansion, size requests and margins on every widget; CSS classes and providers per display; GdkSurface size and layout signal.

## Overview

GTK owns geometry; PHP only states intent. Three containers: `GtkBox` (one axis, `append`/`prepend`/`insert_child_after`/`reorder_child_after`, spacing, homogeneous), `GtkGrid` (`attach(child, column, row, width, height)`; GTK criticals a width or height below 1), `GtkFixed` (`put`/`move` at float coordinates; the position reads back once the fixed has been allocated, since GTK stores it as a layout-child transform applied at allocate).[^widget]

Per widget: `halign`/`valign` (`GtkAlign`), `hexpand`/`vexpand`, `set_size_request` (minimum; `get_size_request` returns `[w, h]`, -1 = unset), `get_width`/`get_height` (allocated), margins, `measure(orientation, for_size)` (minimum/natural plus baselines), `sensitive`. Removal goes through the container's own `remove` or `setChild(null)`; `gtk_widget_unparent` is not bound (widget-implementation API; a window's child pointer would dangle after it).

Styling: `add/remove/has_css_class` on a widget; `GtkCssProvider::new()` + `load_from_string(css)`; `gtk_style_context_add_provider_for_display(GdkDisplay::getDefault(), provider, GTK_STYLE_PROVIDER_PRIORITY_APPLICATION)` installs it for every window on that display, `remove_provider_for_display` takes it out.[^css]

Window size: `GtkNative::getSurface()` (windows and popovers) answers the `GdkSurface` once realized, null before. Plain widgets have no surface: `getNative()` walks up to theirs. `get_width`/`get_height` read the surface; signal `layout(int width, int height)` fires on each size change. `get_native`/`get_root` walk up to the window.[^surface]

[^widget]: GtkWidget, GtkBox, GtkGrid, GtkFixed bindings
[^css]: GtkCssProvider, GdkDisplay, style context functions
[^surface]: GdkSurface
