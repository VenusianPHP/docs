# Callouts

Sources and signal handlers that call PHP; GLib owns the record, detached at request end.

## Overview

`phpgtk_callout` = persistent record: PHP callable, refcount, and what to detach (source id, or instance + handler id).[^runtime] GLib holds the one base reference: a source's `GDestroyNotify`, or a closure's finalize notifier, releases it. So a source or handler keeps working after PHP drops every handle, until GLib removes it.

Sources (`g_timeout_add`, `g_idle_add`, `g_unix_fd_add`): the callable's truthiness is the gboolean return (`G_SOURCE_CONTINUE` keeps the source). A throwing callable removes its source; the exception surfaces when the PHP call that iterated (`GMainContext::iteration`, `GApplication::run`) returns.[^module]

Signals: `g_closure_new_simple` + a marshaller that boxes each param GValue, calls PHP, and writes the result into the return GValue. Unknown signal names are rejected up front with `g_signal_parse_name`.

Invocation holds the record and a copy of the callable, so a callable may remove its own source or disconnect its own handler. Skipped while a PHP exception is pending.

RSHUTDOWN: every attached record's source is removed / handler disconnected and its callable freed while the engine can still free it.

[^runtime]: phpgtk_callout_*
[^module]: Source functions, closure marshaller
