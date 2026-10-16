# Changelog

What changed in this package, newest first.

### 2026-10-15

* `AppkitTextArea`: read-only, wrap, monospace, text-block line backgrounds, range colours, line selection over UTF-16, clip-view scroll position and `ViewScrolled`. Requires ext-appkit ^0.10.1 and Surface ^0.10.1. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)

### 2026-10-10

* AppkitLink: TKLink over a selectable label with an NSLinkAttributeName attributed text (toolkit links).
* Edit menu: edit roles become first-responder NSMenuItems with the standard key equivalents; their folder autoenables (HumanInput slice 29).

### 2026-10-09

* HumanInput on AppKit: `AppkitInputEngine` (`SeenEvent`, `SeenKind`; keys through Surface's `MacKeycodes`), `GameControllerPadSource` (`GcReading`, `GameControllers`, `SystemGameControllers`); the provider registers both. Requires `venusian-surface/human-input`. [input](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/input)
* Canvas clicks: `AppkitCanvasClicks` posts `view.clicked` with the point for a press and release on a canvas (HumanInput slice 28). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/windows-and-menus)
* Context menus: `AppkitContextMenu`, an `NSMenu` popped up by `AppkitRightClicks` for the primitive or nearest group with a menu; items post `MenuActivated`. `AppkitSession::withhold()` / `withheld()`: a tap keeps the event it answered from being dispatched (HumanInput slice 27). Requires ext-appkit `NSMenu` popUp. [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/windows-and-menus)
* Right-click mail: `AppkitRightClicks` posts `view.right-clicked` / `window.right-clicked` for the right button and Ctrl-click; the session's pump shows each event to its taps before dispatching it (HumanInput slice 26). [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/windows-and-menus)

### 2026-10-08

* The driver stages windows: `AppkitStagedWindow` and `AppkitDisplays`. Lending moved from `AppkitCanvas` into `LendsAppkitSurfaces`, shared with staged windows. `applyPixels()` takes the damage list. [staged windows](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/staged-windows)

### 2026-10-06

* The `vulkan` engine presents through the canvas's `CAMetalLayer` (MoltenVK); tests only, no canvas change. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)
* `AppkitCanvas` lends an `NSOpenGLView`'s context to the `opengl` engine: the view pinned over the canvas, its `drawRect:` copying the frame. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)

### 2026-10-05

* `AppkitCanvas` lends an SDL window over its `NSWindow` to the `sdl3` engine: SDL's swapchain view moved into the canvas, the window destroyed once the device lets go. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)
* The session gives the application an empty `NSApplicationDelegate` trampoline when it has none (SDL takes an empty delegate slot) and sweeps parked SDL windows every pump; the canvas restores the responder chain SDL rewires. [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/session), [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)
* `AppkitCanvas` lends a `CAMetalLayer` (ext-metal) as the view's layer to the `metal` engine; reclaim restores a backing layer with gravity and clipping. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)

### 2026-10-04

* `AppkitCanvas` pipes an ext-fb framebuffer: `CFData::create` reads its memory by address, so no pixel byte passes through PHP. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)

### 2026-10-03

* `AppkitCanvas`: the framebuffer a `TKCanvas` hands out, shown as layer contents. [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives)

### 2026-10-02

* Stacks switch to FILL distribution while a child fills: [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives) — a filling column beside a hugging one now takes every spare point of its row.
* Review fixes: [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives) — grid in a frame view (no window shrink), fillers share equally, slot for main-axis align, priorities table (480 pull, 490 wrap), hidden fillers, natural sizes for table/text area, fixed min fitting, video loop/replay/setFile/disabled, own-background leaves.
* Toolkit primitives: [primitives](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/primitives) added; [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/windows-and-menus) gains content hosting, `WindowResized`, close order; [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/runbooks/testing) gains `pumpUntil`, primitive coverage, condition waits.

### 2026-10-01

* Bundle created: [session](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/session), [windows and menus](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/guide/windows-and-menus), [testing](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-appkit/runbooks/testing).
