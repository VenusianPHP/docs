# Changelog

What changed in this package, newest first.

### 2026-10-10

* GtkLinkButton, GtkLabel markup and current URI, GCancellable, GAsyncResult, GtkUriLauncher (ext-gtk's first ready callback); GdkGLContext::realize frees its GError (toolkit links). [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)
* `GtkWindow::getFocus`, `GtkWidget::grabFocus`/`hasFocus` for the Edit menu and Mac text keys (HumanInput slice 29). [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)

### 2026-10-09

* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkPopover and GtkPopoverMenu with their own setParent / unparent (popovers only; GtkWidget still has no unparent), GtkGesture::setState and GtkEventSequenceState. For context menus (HumanInput slice 27).
* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): g_set_prgname / g_get_prgname: GTK's X11 WM_CLASS follows the program name.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): event controllers for HumanInput's gtk engine. GtkEventController and its key, motion, scroll and focus controllers; GtkGesture, GtkGestureSingle, GtkGestureClick; GtkWidget add/removeController; gdk_keyval_to_unicode and gdk_keyval_to_lower; GtkPropagationPhase and GdkScrollUnit; the scroll-flag and modifier-mask constants. Signals hand keyvals, keycodes and modifier state over as ints.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkEventController::getCurrentEvent(), GdkEvent and GdkScrollEvent; on GTK 4.20+ GdkScrollEvent::getRelativeDirection() and GdkScrollRelativeDirection, so a reader can undo natural scrolling. SurfaceTest skips stub blocks the running GTK is older than.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkEventControllerLegacy; GdkEvent getEventType/getPosition/getPointerEmulated, GdkButtonEvent, GdkTouchEvent, GdkEventType; GtkIMContext and GtkIMMulticontext; GtkWidget::computePoint, GtkWindow::getSurfaceTransform. Signal GdkEvent arguments arrive as GdkEvent objects.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkWidget::pick and GTK_PICK_*; GdkEvent::getModifierState; GtkGestureSingle touch_only; GtkGestureLongPress. For right-click mail (HumanInput slice 26).
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkSettings::getDefault and g_object_get_property, so a reader takes gtk-long-press-time and gtk-dnd-drag-threshold from GTK.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GdkDisplay::sync. GTK 4.18's Wayland input method binds its text-input on a round trip after the display's first use of it; a context focused before then stays GTK's focus past its finalize and the next focused window crashes. The IM test focuses with no client widget. Suite 165 + 5 skipped on Homebrew PHP 8.4 NTS and ZTS, 167 + 1 on the Pi.

### 2026-10-06

* `GdkDmabufTextureBuilder::build()` takes a destroy callback (GTK's destroy notify); `GdkDmabufFormats` from `GdkDisplay::getDmabufFormats()`; `GtkWidget::getDisplay()`. Suite 145 + 5 skipped on Homebrew PHP 8.4 NTS and ZTS, 150 on the Pi. [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)
* `GdkDmabufTextureBuilder` (Linux, GTK 4.14+): a texture over a dmabuf, the fd borrowed. `SurfaceTest` skips Linux-only stub blocks elsewhere. Suite 142 + 4 skipped on Homebrew PHP 8.4 NTS and ZTS, 146 on the Pi. [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)
* GL views: `GtkGLArea` and `GdkGLContext` with `GdkGLAPI`; the `render` signal hands PHP the area and its context, the context current and the area's framebuffer bound. Suite 143 on Homebrew PHP 8.4 NTS and ZTS (1 skipped there) and on the Pi. [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)

### 2026-10-04

* Extension version is 0.10.1. Memory textures from an address: `GdkMemoryTexture::new()` takes `string|int` bytes, an address trusted to hold the rows the width, height and stride name. New `GdkMemoryTextureBuilder` (GTK 4.16+, compiled only when headers are 4.16+): fluent setters, `setBytes` from a string or an address with a byte count, `setUpdateRegion` of `[x, y, width, height]` rects, `build(): ?GdkTexture` (null when unset). [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)

### 2026-10-03

* Pixels from bytes: `GdkTexture`, `GdkMemoryTexture::new()`, `GdkMemoryFormat`; `GtkPicture` set_paintable and can_shrink; `GtkWidget::getScaleFactor()`. [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface)

### 2026-10-02

* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): widget alignment, sizing, margins, CSS classes; GtkBox ordering; GtkGrid, GtkFixed; GtkCssProvider, GdkDisplay, style-context functions; GdkSurface. New concept [layout and styling](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/layout-and-styling).
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkLabel, GtkButton, GtkCheckButton, GtkSwitch, GtkToggleButton, GtkEntry/GtkEntryBuffer, GtkTextView/GtkTextBuffer, GtkScale, GtkWidget activate.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkDropDown, GtkStringList, GtkStringObject, GtkCalendar, GDateTime (new boxed kind, [object model](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/object-model)), GtkProgressBar, GtkSpinner, GtkPicture, GtkSeparator, GtkScrolledWindow.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkColumnView, GtkColumnViewColumn, GtkSignalListItemFactory, GtkListItem, GtkSingleSelection; (transfer full) arguments in [object model](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/object-model).
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkMediaStream, GtkMediaFile, GtkVideo, `gtk_media_backend_available()`; installers check or warn about the media backend. New concept [video and the media backend](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/video-and-the-media-backend).
* Review fixes: `gtk_widget_unparent` dropped; entry and text buffer lengths and UTF-8, scale ranges, list positions, native int ranges, child parents and column membership refused before GTK asserts; GTK floor raised to 4.12 for `gtk_css_provider_load_from_string`.

### 2026-10-01

* Runbook [adding a binding](/docs/{{version}}/ecosystem/standalone-extensions/gtk/runbooks/adding-a-binding).
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkWidget, GtkWindow, GtkApplicationWindow, GtkAboutDialog, GtkBox, GtkPopoverMenuBar, GMenuModel/GMenu/GMenuItem, GSimpleAction/GSimpleActionGroup, GVariant, GtkOrientation, GtkApplication window and menubar calls. [Object model](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/object-model): GVariant kind and constructor ownership.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GtkWidget get_realized/get_mapped. [Errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/errors-and-threads): widget constructors refuse an uninitialised GTK.
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface): GApplication GActionMap/GActionGroup calls (the "app" actions).

### 2026-09-30

* Bundle created with ext-gtk 0.10.0: [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface), [object model](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/object-model), [callouts](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/callouts), [errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/gtk/architecture/errors-and-threads), [build](/docs/{{version}}/ecosystem/standalone-extensions/gtk/runbooks/build-install-test).
