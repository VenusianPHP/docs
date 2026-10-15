# Changelog

What changed in this package, newest first.

### 2026-10-14

* Releasing: `split.yml` on a `v*` tag; `tests.yml` (PHP 8.4/8.5) gates it; `.github/split.sh` splits every component to `venusian-surface` with the same tag. [releasing](/docs/{{version}}/surface/runbooks/releasing)

### 2026-10-10

* `TKLink`: `link(name, text, url)`, a link the toolkit opens; URL needs a scheme; posts nothing (toolkit links). [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives)
* Edit menu roles: undo, redo, cut, copy, paste, select-all; no hotkey on them; Surface's default main profile has an Edit folder (HumanInput slice 29). [menu profiles](/docs/{{version}}/surface/api/menu-profiles)

### 2026-10-09

* `View\CanvasClicked`: a click on a canvas posts `view.clicked` with the point (HumanInput slice 28). [view mail](/docs/{{version}}/surface/api/view-mail)
* Context menus: `TKPrimitive::setContextMenu()` / `contextMenu()`, `ContextMenu`; a chosen item posts `MenuActivated` (HumanInput slice 27). [menu profiles](/docs/{{version}}/surface/api/menu-profiles)
* `View\RightClicked` and `WindowRightClicked`: right-click mail for toolkit windows (HumanInput slice 26). [view mail](/docs/{{version}}/surface/api/view-mail), [mail](/docs/{{version}}/surface/api/window-mail)

### 2026-10-08

* Staged windows phase 5, staged frames: [drawing](/docs/{{version}}/surface/architecture/drawing) gains vsync, HDR targets, pacing, fixed resolution and `DamageHistory` on GPU engines; [framebuffers](/docs/{{version}}/surface/architecture/framebuffers) gains `HdrImage` and `HdrReadback`; [windows](/docs/{{version}}/surface/architecture/windows) gains scaling and HDR on lent surfaces; [testing](/docs/{{version}}/surface/runbooks/testing) names the staged GPU fakes.
* `HostsDrawing::applyPixels()` takes the damage list like `applyAddress()`: a PHP-held framebuffer's damage reaches the host.
* Staged windows grow what a game engine asks of its window: `WindowMode` incl. exclusive fullscreen at a `DisplayMode`, `Display` and display modes, position, limits, aspect, safe area, style toggles, `WindowCapability` per backend, vsync carried to `LentSurface`, scaling fit and filter with `presentRect()`, keep-awake, attention, icon, hit tests, HDR, and ten mail types incl. `confirm_close`. `fullscreen(bool)` and the `fullscreen` option replaced by `setMode()` and `mode`. [windows](/docs/{{version}}/surface/architecture/windows).

### 2026-10-05

* GPU engine contracts: [drawing](/docs/{{version}}/surface/architecture/drawing) gains GPU engines, the draw list and the manager's shared arguments; [framebuffers](/docs/{{version}}/surface/architecture/framebuffers) gains GLFramebuffer; [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives) gains surface lending on the canvas; [embedded displays](/docs/{{version}}/surface/architecture/embeddeddisplays) gains output size and format and the staging copy; [testing](/docs/{{version}}/surface/runbooks/testing) names the GPU fakes and the parity suite.

### 2026-10-04

* Slice 0, Tasks 5 and 11: `renderer('velvet', ['output' => $target])` draws over a target's `framebuffer()`; `keepsFrame()` keeps a ring's frame for every engine. Added `DirectEDisplay` (`Pipeable`): regions piped from ext-fb memory through a gpio/contracts `PipeablePanel`'s `WritesFromMemory` bus; `attach()` / `panel()` take `direct: true`. Measured on the Pi 5's ST7796. [embedded-displays](/docs/{{version}}/surface/architecture/embeddeddisplays), [drawing](/docs/{{version}}/surface/architecture/drawing).
* Slice 0, Task 4: `Output` renamed `OutputTarget` and gains `framebuffer()`; added `Pipeable` (`canPipe()`); `TKCanvas` is pipeable — an extended RGBA8 framebuffer reaches the toolkit by address (`applyAddress`) with its damage, default kind `dirty`. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [embedded-displays](/docs/{{version}}/surface/architecture/embeddeddisplays).
* EmbeddedDisplays on 0.10: added [embedded-displays](/docs/{{version}}/surface/architecture/embeddeddisplays); `Output` shared with `TKCanvas`; `app('displays')`, `config/embedded-displays.php`. [drawing](/docs/{{version}}/surface/architecture/drawing) gains partial frames, `damage()`, `invalidate()`, the region `clear`. [components](/docs/{{version}}/surface/guide/components), [config](/docs/{{version}}/surface/api/config).
* Fonts ported to 0.10: added [fonts](/docs/{{version}}/surface/architecture/fonts); `text()` / `textBounds()` on `RenderingEngine`, the `spans` command; `app('fonts')`, `config/fonts.php`, `make:font`. [drawing](/docs/{{version}}/surface/architecture/drawing), [components](/docs/{{version}}/surface/guide/components).
* Framebuffers, Rasterize, Images: `auto` driver, the new config default (`FRAMEBUFFERS_DRIVER`, `RASTERIZE_DRIVER`, `IMAGES_DRIVER`), extended when the extension is loaded, native when not. [config](/docs/{{version}}/surface/api/config), [components](/docs/{{version}}/surface/guide/components).
* Surface 0.10 phase 4, Images: added [images](/docs/{{version}}/surface/architecture/images); [framebuffers](/docs/{{version}}/surface/architecture/framebuffers) gains `writeRgba8()`; [components](/docs/{{version}}/surface/guide/components), [config](/docs/{{version}}/surface/api/config) and [testing](/docs/{{version}}/surface/runbooks/testing) gain the split, its config and its tests.

### 2026-10-03

* Surface 0.10 phase 4, canvas: [toolkit primitives](/docs/{{version}}/surface/architecture/toolkit-primitives) gains `TKCanvas` (framebuffer + present); [components](/docs/{{version}}/surface/guide/components): Windows now requires Framebuffers.
* Surface 0.10 phase 4, Drawing: added [drawing](/docs/{{version}}/surface/architecture/drawing); [framebuffers](/docs/{{version}}/surface/architecture/framebuffers) gains image painting; [components](/docs/{{version}}/surface/guide/components), [config](/docs/{{version}}/surface/api/config) and [testing](/docs/{{version}}/surface/runbooks/testing) gain the split, `Affine`, its config and its tests.
* Surface 0.10 phase 4, Rasterize: added [rasterize](/docs/{{version}}/surface/architecture/rasterize); [framebuffers](/docs/{{version}}/surface/architecture/framebuffers) gains span painting; [components](/docs/{{version}}/surface/guide/components), [config](/docs/{{version}}/surface/api/config) and [testing](/docs/{{version}}/surface/runbooks/testing) gain the split, its config and its tests.
* Surface 0.10 phase 4, Framebuffers: added [framebuffers](/docs/{{version}}/surface/architecture/framebuffers); [components](/docs/{{version}}/surface/guide/components), [config](/docs/{{version}}/surface/api/config) and [testing](/docs/{{version}}/surface/runbooks/testing) gain the split, its config and its tests.

### 2026-10-02

* Surface 0.10 slice 3 (toolkit primitives), Surface layer: added [toolkit primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [view mail](/docs/{{version}}/surface/api/view-mail), [styling](/docs/{{version}}/surface/api/styling); [components](/docs/{{version}}/surface/guide/components) gains the `venusian-surface/nuts-and-bolts` split; [windows](/docs/{{version}}/surface/architecture/windows) gains the content container and lookups; [window mail](/docs/{{version}}/surface/api/window-mail) gains `WindowResized`; [bridge](/docs/{{version}}/surface/architecture/bridge) gains `postLatest`/`flushLatest`; [testing](/docs/{{version}}/surface/runbooks/testing) names the primitive fakes. Review fixes the same day: `Placement`/`PrimitiveRegistry` in contracts, reorder on the child, `TKFixed::frameOf()`, `forgetLatest()`, guarded forgets, finite-float and trailing-newline guards.

### 2026-10-01

* Bundle created with Surface 0.10 slices 1-2 (bridge, toolkit windows): [components](/docs/{{version}}/surface/guide/components), [bridge](/docs/{{version}}/surface/architecture/bridge), [windows](/docs/{{version}}/surface/architecture/windows), [mail](/docs/{{version}}/surface/api/window-mail), [menu profiles](/docs/{{version}}/surface/api/menu-profiles), [config](/docs/{{version}}/surface/api/config), [composing an app](/docs/{{version}}/surface/runbooks/composing-an-app), [testing](/docs/{{version}}/surface/runbooks/testing).
