# Object model

One PHP object per GObject or GMainContext, referenced while PHP holds it, boxed as its nearest bound GType.

## Overview

One struct: `phpgtk_object { void *ptr; phpgtk_kind kind; zend_object std; }`. Kind picks the reference functions: GObject → `g_object_ref_sink` on box (sinks a floating ref, so widgets box the same way), `g_object_unref` on free; GMainContext → `g_main_context_ref/unref`; GVariant → `g_variant_ref_sink/unref`; GDateTime → the new reference handed in (`g_date_time_new_local`, `gtk_calendar_get_date`) is PHP's, `g_date_time_unref` on free.[^runtime]

Constructor ownership follows the C annotation. `(transfer none)` toplevels (`gtk_window_new`, `gtk_application_window_new`, `gtk_about_dialog_new`) box with PHP's own reference while GTK keeps its toplevel reference. Floating widgets (`gtk_box_new`, `gtk_popover_menu_bar_new_from_model`) are sunk by the box: PHP owns the reference until a parent takes its own. `(transfer full)` objects (`g_menu_new`, `g_simple_action_new`, `g_action_get_state`, …) box through `phpgtk_box_*_full`, which drops the returned reference after taking PHP's.

Identity: module global `boxes` maps native address → `zend_object*` (no refcount); the same native object always yields the same PHP object. Persistent per thread (GINIT/GSHUTDOWN).

Class choice: walk `G_OBJECT_TYPE` → `g_type_parent`; first GType name registered with `phpgtk_map_gtype()` wins; fallback `GObject`. Backend subclasses (`GdkMacosSurface`, `GdkWaylandSurface`, `GtkGstMediaFile`, `GtkNoMediaFile`) box as the bound parent.

Arguments annotated `(transfer full)` (`gtk_column_view_new`, `gtk_column_view_column_new`, `gtk_single_selection_new`) get a `g_object_ref()` of PHP's object: the native side owns that one, PHP keeps its own. Enum returns go through `phpgtk_return_enum()`: the native int becomes the stub's case.

Constructors (`GtkApplication::new`) box the new object, then drop the creation reference: PHP's own reference is the only one left.

Wrappers are not constructible, not cloneable, not serializable; identity is `===`.

[^runtime]: Boxing, handlers
