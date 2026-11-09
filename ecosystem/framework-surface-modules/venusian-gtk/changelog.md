# Changelog

What changed in this package, newest first.

### 2026-11-07

* System accent: a cached GTK accent service reads GNOME's `accent-color` setting and maps the known names to libadwaita's colours; null when the schema or key is missing, `WindowException` for a name it does not know. Released in v0.11.0.

### 2026-11-05

* Native text: `GTKFonts` turns a `FontSpec` into the Pango description the widget's CSS gives it (family or Monospace, italic, weight, px size) and measures it; the driver's `fontMetrics()` reads through one never-shown `GtkLabel`'s Pango context. Text areas: one tag per flag for bold, italic, underline and strikethrough runs, a one-stop `PangoTabArray` at columns × the font's character width (`setTabWidth()`), and justification; inputs align with `xalign`; a button's child aligns start, centre or end. Released in v0.11.0. [primitives](/docs/{version}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)

### 2026-10-28

* **v0.11.0** with the Venusian 0.11 ecosystem: requires PHP `~8.4.27||^8.5.12`, ext-gtk ^0.11 and `venusian-surface/*` and `venusian-voyager/*` ^0.11; `dev-main` is `0.11.x-dev`. Known: on the Pi (Wayland) a shown window's `setDefaultSize()` does not grow a split past its first width. [overview](/docs/{version}/ecosystem/framework-surface-modules/venusian-gtk/overview)

### 2026-10-27

* Services: `GTKComposedAlert` for an alert with a style, a suppression box or a title (a transient modal `GtkWindow`; Return, Esc and close answer with the check state); `supports()` gives `AlertTitle`, not `ShowHidden`; file dialog filters as `GtkFileFilter`s in a `GListStore`; `GTKClipboard` reads text asynchronously, answers `hasText()` from the formats and posts `ClipboardChanged` from the `changed` signal. Needs ext-gtk's `GtkFileFilter`, `GListStore`, file dialog filters, clipboard text reads and `GdkContentFormats`. Released in v0.11.0. [windows and menus](/docs/{version}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus)
* Canvas keys: `GTKCanvasKeys` replaces the canvas's Tab controller. A focused canvas takes every key and posts `KeyPressed`, `EditCommanded` and `KeyReleased`; keys with no command go to a `GtkIMMulticontext`, whose commit posts `TextCommitted`. A focusable canvas is one Tab stop. `GTKCanvas::tabKeys()` became `keys()`. Released in v0.11.0. [overview](/docs/{version}/ecosystem/framework-surface-modules/venusian-gtk/overview)

### 2026-10-26

* New primitives: `GTKComboBox` (an entry and an options popover, completions in `GTKCompletionList`), `GTKMenuButton` and `GTKScrollBar` (`ScrollChanged`, latest wins). Push and toggle buttons show a Framebuffer image (`GTKButtonImage`) and can drop their frame; `GTKTabView` inserts pages at an index. Released in v0.11.0. [primitives](/docs/{version}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)
* Canvas: hover mail (`CanvasEntered`, `CanvasMoved`, `CanvasLeft`), kinetic wheel phases and `GTKCanvasCoast` (decaying momentum wheels ticked by the session pump); the fractional scale is read from the surface and `WindowScaleChanged` posts when it changes. Released in v0.11.0.
* Menus: radio items (`MenuRadioChosen`), relabelling, and toggle and radio state kept in bars and context menus; a primitive can open its context menu from code. On macOS every bar names `app` actions so the app bar shows toggle and radio marks, and a relabel rebuilds the shown app bar. `WindowFocused` posts only after the window was inactive at a pump's end. Released in v0.11.0. [windows and menus](/docs/{version}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus)

### 2026-10-23

* v0.10.5 tracks Surface v0.10.5. Requires ext-gtk ^0.10.5 and Surface contracts and windows ^0.10.5. [overview](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/overview)
* `GTKSplitView` (a `GtkBox` over one `GtkPaned` slot per pane, equal first layout, positions as fractions, `SplitMoved` at the release of a handle drag) and `GTKTabView` (`GtkNotebook`, `TabSelected` for user switches). [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives#containers)
* `GTKTree`: TKTree over a `GtkColumnView` on a `GtkTreeListModel`, a `GtkTreeExpander` in the first column, cell colours from one CSS provider per tree; `NodeSelected`, `NodeExpanded` and `NodeActivated` post only for user actions. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives#leaves)
* Canvas pointer and wheel: `GTKCanvasPointer` posts `CanvasPressed`, `CanvasDragged` and `CanvasReleased` (one press owned at a time, clicks from GTK's double-click settings); `GTKCanvas::wheeled()` posts `CanvasWheeled` and keeps the wheel from an enclosing scroll view. [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus#canvas-pointer)
* Menu enabled state and accelerators: `setItemEnabled()` / `isItemEnabled()` on bars, windows and the default bar; `'keys'` accelerators through `GTKMenuBar::accelerator()` with GDK key names. [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus#menu-bar)
* Child windows are transient and modal to their parent; `confirmClose()` posts `WindowCloseRequested` from close-request; button roles (`GTKButtonKeys`); on macOS the default bar is blocked while a child is active. [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus#window)
* Focus and window keys: `focus()` / `hasFocus()` on every primitive, `focused()` / `setInitialFocus()` on the window, `FocusLost` / `FocusGained` from `notify::focus-widget` (`GTKFocus`), focusable canvases, `WindowKeyPressed` from a bubble-phase key controller (`GTKWindowKeys`). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus#window)
* Dialogs, clipboard and desktop: `GTKDialogs` (`GtkAlertDialog`, `GtkFileDialog`), `GTKClipboard`, `GTKDesktop` (`GtkFileLauncher`). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus#dialogs)
* Removed primitives are freed: the Mac text keys controller reaches its primitive through a `WeakReference`.

### 2026-10-18

* v0.10.4: composes on ext-gtk ^0.10.2's 1:1 bindings instead of the conveniences the extension used to provide (text buffer reads and iters, `register(null)`). The session throws `BridgeException` when GTK makes no application for `app.id` (GLib takes only a valid reverse-DNS id). Requires ext-gtk ^0.10.2.

### 2026-10-15

* `GTKTextArea`: read-only, wrap, monospace (CSS), tag line backgrounds and range colours, line selection, adjustment scroll position and `ViewScrolled`. Layout-changing hooks hold `ViewScrolled` (and any scroll asked for meanwhile) until adjustments settle or 500 ms pass; a user scroll inside the settle posts once at its end. Requires ext-gtk ^0.10.1 and Surface ^0.10.1. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)

### 2026-10-10

* GTKLink: TKLink over GtkLinkButton (toolkit links).
* Edit menu: edit roles run GTK's own actions on the focused widget, no accelerator; `GTKMacTextKeys` gives text inputs and areas the Mac navigation and deletion keys on macOS (HumanInput slice 29).

### 2026-10-09

* Canvas clicks: `GTKCanvasClicks` posts `view.clicked` with the point for a press and release on a canvas (HumanInput slice 28). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus)
* Context menus: `GTKContextMenu`, a `GtkPopoverMenu` opened by `GTKRightClicks` for the primitive or nearest group with a menu; items post `MenuActivated` (HumanInput slice 27). Requires the ext-gtk popover bindings. [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus)
* The session sets GLib's program name to `app.id` before `GtkApplication` starts, so X11 `WM_CLASS` is the app id and docks match the window to its `.desktop` file. Requires ext-gtk 0.10.1. [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/session)
* Right-click mail: `GTKRightClicks` posts `view.right-clicked` / `window.right-clicked` for the right button, Ctrl-click on macOS and a touchscreen long press (HumanInput slice 26). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus)
* HumanInput's `gtk` input engine: `GTKInputEngine`, `SeenEvent`, `SeenKind`; the provider registers it when HumanInput is bound. Requires `venusian-surface/human-input`. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/input)
* gtk engine on macOS: VoidSymbol presses dropped; modifiers from key events with the event's own key; natural scrolling undone on GTK 4.20+. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/input)
* gtk engine: each window's input method makes the display's first use of GTK's Wayland text-input and waits its round trip (`GdkDisplay::sync`) before any focus, so a context let go before the main loop runs no longer leaves GTK 4.18 focused on a freed context. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/input)
* gtk engine: buttons from raw events (legacy controller), text from a per-window input method, points in the content area. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/input)
* The desktop identity is `config/app.php` `app.id`; `bridge.gtk.application_id` and the `org.venusian.Surface` default are gone, and connect throws without `app.id`. A packaged build names its `.desktop` file after the same id. [Config](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/api/config).

### 2026-10-08

* `GTKCanvas::applyPixels()` takes the damage list Surface now passes; the whole frame is still shown.

### 2026-10-06

* Dmabuf review fixes: the texture's destroy notify hands the export back, XBGR8888 import (opaque), the widget's own display, a format probe before offering the surface. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)
* Canvas lends a dmabuf surface on Linux: the `vulkan` engine exports each frame, the canvas shows it as a `GdkDmabufTexture`. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)
* Canvas lends a GL context: the native view is a `GtkBox` holding the picture or, while lent, a `GtkGLArea` whose render callback copies the `opengl` engine's frame. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)

### 2026-10-04

* `GTKCanvas` pipes an ext-fb framebuffer: the texture is copied by address, and on GTK 4.16 or newer the next one is built with `GdkMemoryTextureBuilder` and an update region. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)

### 2026-10-03

* `GTKCanvas`: the framebuffer a `TKCanvas` hands out, shown as a memory texture on a `GtkPicture`. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives)

### 2026-10-02

* [Primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives): scoped style targets, escaped font family, datepicker follows month/year navigation and refuses years outside 1-9999, table splices from the first changed row, watched views keyed by uuid; window resize polled ([windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus), [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/session)).
* New [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/primitives): factory, containers, all leaves, styling, sizes, watched allocations, mail rules. [Windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus): content area, primitive tree on close, WindowResized. [Session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/session): watched sizes after each pump. [Testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/runbooks/testing): helpers, environment facts, fixtures.

### 2026-10-01

* Bundle created: [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/session), [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/guide/windows-and-menus), [config](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/api/config), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-gtk/runbooks/testing).
