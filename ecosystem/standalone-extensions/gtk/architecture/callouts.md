# Callouts

Sources, signal handlers, async callbacks and destroy notifies that call PHP; GLib owns the record, the owner thread only, detached at request end.

## Overview

`phpgtk_callout` = persistent record: PHP callable, refcount, owner thread, and what to detach (source id, or instance + handler id).[^runtime] GLib holds the one base reference: a source's `GDestroyNotify`, a closure's finalize notifier, an async call's completion, or a texture's destroy notify releases it. So a source or handler keeps working after PHP drops every handle, until GLib removes it.

Trampolines forward only. Sources (`g_timeout_add`, `g_idle_add`, `g_unix_fd_add`): the callable's truthiness is the gboolean return (`G_SOURCE_CONTINUE` keeps the source). Signals: `g_closure_new_simple` + a marshaller that boxes each param GValue, calls PHP, and writes the result into the return GValue. `GtkUriLauncher::launch`: `(source, result)` boxed; a null callable is GIO's fire and forget, with no record. `GdkDmabufTextureBuilder::build`: the destroy callable runs once when GTK finalizes the texture, never when the build failed. `GtkTreeListModel::new`: the create func gets the item boxed; a returned GListModel goes to GTK with a new reference, anything else (null, another value, a throw) is NULL; `user_destroy` releases the record when the model is finalized.[^module]

Off-thread: every trampoline asks `phpgtk_callout_foreign` first. A dispatch or release on a thread other than the record's owner is dropped (site `callout-owner-thread`: it would run PHP on another thread's engine).

GValue → PHP: objects and interfaces boxed, GdkEvent as its class, GParamSpec, GtkTextIter (a copy holding its buffer) and GBytes as objects, GVariant boxed, enums and flags as ints, pointers and other boxed types as addresses. PHP → GValue (`phpgtk_zval_to_gvalue`, for handler returns, emit parameters and `g_object_set_property`): written only when the value is of the GType's kind; otherwise the GValue keeps its default. Parameters are checked first by `phpgtk_signal_param`, which raises the TypeError naming the GType.

Invocation holds the record and a copy of the callable, so a callable may remove its own source or disconnect its own handler. Skipped while a PHP exception is pending; a throwing source callable removes its source and the exception surfaces when the PHP call that iterated returns.

RSHUTDOWN: every attached record's source is removed / handler disconnected and its callable freed while the engine can still free it.

[^runtime]: phpgtk_callout_*, phpgtk_gvalue_to_zval, phpgtk_zval_to_gvalue
[^module]: Source functions, closure marshaller, g_signal_emit_by_name, g_object_set_property
