# Errors and threads

GError after the call becomes the GError exception; the only refusals are the probe-backed crash guards listed under bindings.json sites.

## Overview

**Pass-through is the default.** GTK's NULL, FALSE, `g_critical`, `g_warning` and odd but documented results reach PHP unchanged. A call the ext would once have refused (a bad UTF-8 string, a range GTK clamps, a missing parent, an unknown signal or property) is made, and GTK answers it.

**Translation.** `GError` exception: message = `error->message`, code = `error->code`, `$domain` = `g_quark_to_string(error->domain)`. Thrown only after a native call with a `GError **` out-parameter reported one (`GApplication::register`, `GtkUriLauncher::launchFinish`, `GdkDmabufTextureBuilder::build`). `GtkGLArea::getError` returns the `?GError` object without throwing.

**Refusals** (`GtkException`, or `ValueError` for an argument) only where a probe showed the call crashing the process or corrupting the VM. Each carries `/* binding:<id> */` and a `sites` entry in `bindings.json`, with its probe in `tests/Probes`:[^bindings][^probes]

| Site | Outcome without it | Where |
|---|---|---|
| `gtk-initialized`, `gtk-initialized-media-file` | SIGSEGV (widgets), SIGTRAP (media lookup) | widget and `GtkMediaFile` constructors before `gtk_init` |
| `main-thread-macos` | SIGABRT (AppKit), SIGSEGV (`GMainContext::iteration`) | macOS only; the macro is empty on Linux, where GTK runs off the main thread |
| `callout-owner-thread` | `zend_mm_heap corrupted` | a callback dispatched or released on a thread other than its owner: dropped, the return GValue left at its default |
| `text-iter-stale` | SIGSEGV | a `GtkTextIter` used after its buffer's text changed (iter methods, `applyTag`, `selectRange`, …). `getText` is not guarded: GTK checks the stamp there itself |
| `text-iter-foreign-mark` | SIGSEGV | `getIterAtMark` with a deleted mark or another buffer's |
| `text-iter-line-offset-negative` | SIGTRAP (`g_error`) | `getIterAtLineOffset` with a negative char offset |
| `entry-set-text-nchars` | SIGBUS / SIGSEGV | `GtkEntryBuffer::setText` with more chars than the string holds |
| `gbytes-string-length` | SIGSEGV | `GBytes::new` string form with a size past the string |
| `cairo-region-nth` | SIGSEGV | `CairoRegion::getRectangle` outside `0 … numRectangles() - 1` |
| `gmenu-detailed-action` | SIGTRAP (`g_error`) | `GMenu` / `GMenuItem` detailed action names GLib cannot parse |
| `accels-action-name` | SIGABRT | `GtkApplication::setAccelsForAction` with an unparsable action name |
| `gtk-version-4-16`, `gtk-version-4-14`, `gtk-version-4-14-dmabuf-builder` | exit 127, symbol lookup error | a class built against newer headers called on an older GTK |

Plain marshalling is not a refusal: a PHP int outside the C parameter's type (`phpgtk_long_in_range`), a value of the wrong kind for a GValue, an enum case with no native value. These raise `TypeError` / `ValueError` before the call.

**Probe builds.** `./configure --enable-gtk --enable-gtk-probes` defines `PHPGTK_PROBES`; there `PHPGTK_PROBE_OFF("<id>")` reads env `PHPGTK_PROBE_OFF`, so one site's check can be turned off to show its crash. A release build compiles the switch to 0.[^header]

GLib main-context calls carry no guard: GMainContext is thread-safe, and `wakeup()` exists to be called from other threads.

GIOCondition values are the host's `poll(2)` bits; `src/gtk.c` static-asserts they match the stub enum.

[^header]: PHPGTK_REQUIRE_MAIN_THREAD, PHPGTK_REQUIRE_INITIALIZED, PHPGTK_PROBE_OFF
[^bindings]: sites
[^probes]: one probe per site
