# Errors and threads

GError becomes the GError exception; GTK entry points refuse other threads, widgets refuse an uninitialised GTK.

## Overview

`GError` exception: message = `error->message`, code = `error->code`, `$domain` = `g_quark_to_string(error->domain)`. Thrown by bindings with a `GError **` out-param (`GApplication::register`).

`GtkException`: a call refused before reaching GTK. `PHPGTK_REQUIRE_MAIN_THREAD()` guards `gtk_init`, `gtk_init_check`, `GtkApplication::new`, `GApplication::run` (main thread = `pthread_main_np()` on macOS, `gettid() == getpid()` on Linux). `PHPGTK_REQUIRE_INITIALIZED()` refuses widget constructors (`GtkWindow`, `GtkApplicationWindow`, `GtkAboutDialog`, `GtkBox`, `GtkPopoverMenuBar`) until `gtk_is_initialized()` (GTK would crash). `GApplication::getIsRemote()` before registration throws it (GIO would assert).[^header]

GLib main-context calls carry no guard: GMainContext is thread-safe, and `wakeup()` exists to be called from other threads.

GIOCondition values are the host's `poll(2)` bits; `src/gtk.c` static-asserts they match the stub enum.

[^header]: PHPGTK_REQUIRE_MAIN_THREAD, PHPGTK_REQUIRE_INITIALIZED
