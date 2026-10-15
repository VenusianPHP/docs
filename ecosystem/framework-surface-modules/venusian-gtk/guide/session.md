# Session

GtkApplication session - register once, hold while connected, budgeted context pump, one-shot fd wake, macOS activation.

## Overview

`GTKSession extends Surface\Bridge\BridgedToolkitSession`; built by `GTKBridgeDriver::connect()` from [config](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/api/config).[^session]

| Hook | GTK calls |
|---|---|
| initialize (once) | `g_set_prgname(id)` (GTK names the X11 `WM_CLASS` after it, so docks match the window to a packaged build's `<id>.desktop`), `GtkApplication::new(id, unique ? DEFAULT_FLAGS : NON_UNIQUE)`, no-op `activate` handler, `register()` (startup initialises GTK), default `GMainContext` |
| connect | `hold()` (alive with no windows), `activate()` |
| disconnect | `release()` |
| `pump($ns)` | budget > 0: `g_timeout_add(ceil ms)` + one blocking `iteration(true)`, remove the timeout if it did not fire; then up to `DRAIN_LIMIT` (64) non-blocking iterations while `pending()` |

The drain limit keeps an always-ready source (idle re-adding itself) from holding a pump. After the drain, `checkWatched()` reports window content areas and watched [primitive](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives) sizes that changed.

## Wake

`g_unix_fd_add(fd, IN)` returning `G_SOURCE_REMOVE`: ends a wait once, re-armed by the next `pump()`. Release: `g_source_remove`.

## macOS

GTK runs on NSApplication. GDK activates the app once, at display open; macOS declines that for a terminal-launched process and GDK has no other activation call. So on Darwin: initialize refuses without ext-appkit (`BridgeException`), and `bringForward()` (called by `present()`) runs `NSApplication::activateIgnoringOtherApps(true)`. Wayland/X11 focus on present.

## About

`showAbout(about, ?parent)`: one `GtkAboutDialog` while open (showing again updates and raises it); program name, version, copyright from `windows.about`, transient for the parent window, non-modal. `close-request` drops it so GTK destroys it: a hidden-but-alive toplevel keeps the macOS frame clock waking the process every frame. `aboutDialog()` = the open one.

[^session]: GTKSession
