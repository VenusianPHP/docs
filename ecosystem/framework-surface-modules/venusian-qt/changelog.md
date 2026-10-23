# Changelog

What changed in this package, newest first.

### 2026-10-18

* v0.10.4: composes on ext-qt ^0.10.2's 1:1 bindings: sizes, points and rects are `QSize`/`QPoint`/`QPointF`/`QRect`, the datepicker posts and takes `QDate`, menu shortcuts are `QKeySequence` text, canvas pixels go through a `QByteArray` (a NUL byte no longer cuts them short), and the application is built with `argc` and `argv`. Requires ext-qt ^0.10.2. [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/session)
* Lent GL views reach the screen: the session makes the canvas's GL format Qt's default and shares contexts before the application exists, so the window's compositor shares with the GL view (before, macOS showed the wrong image and Linux black). [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/session)

### 2026-10-14

* QtTextArea: read-only, wrap, monospace (system fixed font), extra-selection line backgrounds and range colours, line selection over UTF-16, scroll-bar scroll position and `ViewScrolled` (text panes).

### 2026-10-10

* QtLink: TKLink over a rich-text QLabel that opens its link (toolkit links).
* Edit menu: edit roles call the focused line edit's or plain text edit's own slot, no shortcut (HumanInput slice 29).

### 2026-10-09

* Canvas clicks: `QtCanvasClicks` posts `view.clicked` with the point for a press and release on a canvas (HumanInput slice 28). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/windows-and-menus)
* Context menus: `QtContextMenu`, a `QMenu` popped up by `QtRightClicks` for the primitive or nearest group with a menu, the widget's own menu kept shut; items post `MenuActivated` (HumanInput slice 27). Requires ext-qt `QMenu::popup`. [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/windows-and-menus)
* Right-click mail: `QtRightClicks` posts `view.right-clicked` / `window.right-clicked` for Qt's context-menu request (right button, Ctrl-click on macOS) and a touchscreen long press; `QtWindow::contentArea()` (HumanInput slice 26). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/windows-and-menus)
* The desktop identity is `config/app.php` `app.id`; `bridge.qt.desktop_file_name` and the `org.venusian.Surface` default are gone, and connect throws without `app.id`. A packaged build names its `.desktop` file after the same id. [Config](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/api/config).

### 2026-10-08

* `QtCanvas::applyPixels()` takes the damage list Surface now passes; the whole frame is still shown.

### 2026-10-06

* Vulkan lending review fixes: explicit Qt teardown on reclaim, the canvas takes the surface back when the device lets go first, Qt must load ext-vulkan's own loader; verified on xcb too. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)
* `QtCanvas` lends a Vulkan surface to the `vulkan` engine on macOS and Linux: a Vulkan `QWindow` whose `QVulkanInstance` is the engine's `VkInstance`, the surface Qt makes for it, first in `surfaces()`. macOS needs `QT_VULKAN_LIB`. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)
* `QtCanvas` lends its `QOpenGLWidget`'s context to the `opengl` engine on macOS and Linux: 4.1 core on macOS, ES 3 elsewhere; `paintGL()` copies the frame. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)

### 2026-10-05

* `QtCanvas` lends an SDL window over Qt's `NSWindow` to the `sdl3` engine on macOS: SDL's swapchain view moved into the Metal `QWindow`'s view, the window destroyed once the device lets go. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)
* The canvas restores the responder chain SDL rewires; the session sweeps parked SDL windows every pump. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)
* `QtCanvas` lends Qt's `CAMetalLayer` (a Metal `QWindow` in a window container, the layer read through ext-appkit) to the `metal` engine on macOS. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)

### 2026-10-04

* `QtCanvas` pipes an ext-fb framebuffer: the `QImage` copies its memory by address, so no pixel byte passes through PHP. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)

### 2026-10-03

* `QtCanvas`: the framebuffer a `TKCanvas` hands out, shown as a `QLabel`'s pixmap. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives)

### 2026-10-02

* New: [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/primitives) — factory, containers, shared hooks, leaves, table, video.
* Review fixes: fill = spare space by stretch factors (stack spacer, grid spare line); fixed covers its frames; image host sized by a spacer, smooth DPR scaling; literal button/label text; slider steps; date picker range 100..9999 and today-pick; `handling()` guard; push-button backgrounds with a border; filter closures hold owners weakly (no leaked images or closed windows). [Testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/runbooks/testing): lifetime test, `pendingLatest()`.
* [Windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/windows-and-menus): content hosting, `centralWidget()`, coalesced `WindowResized`, close removes the content tree. [Testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/runbooks/testing): `pumpFor()` through `ToolkitPump`, primitive coverage, `afterEach` close.

### 2026-10-01

* Bundle created: [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/session), [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/guide/windows-and-menus), [config](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/api/config), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-qt/runbooks/testing).
