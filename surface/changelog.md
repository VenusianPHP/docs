# Changelog

What changed in this package, newest first.

### 2026-10-28

* **Version**: 0.11.0 with the Venusian 0.11 ecosystem: `venusian-surface/*`, `venusian-voyager/*` and `gpio/contracts` at `^0.11.0`, PHP `~8.4.27||^8.5.12`; ext-fb, ext-rasterize and ext-imgdec suggested at `^0.10.0|^0.11.0`. The jovian toolkit drivers and the panel drivers stay suggested at `^0.10.0`. [overview](/docs/{{version}}/surface/overview), [components](/docs/{{version}}/surface/guide/components)
* Services, Surface layer: `AlertStyle`, `DialogCapability` (`AlertTitle`, `ShowHidden`) and `Dialogs::supports()`; `Alert` style, suppression and title; `OpenRequest` / `SaveRequest` filters and showHidden; `AlertAnswered::$suppressed`; `Clipboard::requestText()` / `hasText()`, `ToolkitClipboard`, `ClipboardText`, `ClipboardChanged`. Released in v0.11.0. [windows](/docs/{{version}}/surface/architecture/windows), [mail](/docs/{{version}}/surface/api/window-mail)
* Canvas keys, Surface layer: `EditCommand` and the mail of a focused, focusable canvas: `KeyPressed`, `KeyReleased`, `TextCommitted`, `EditCommanded`. Released in v0.11.0. [view mail](/docs/{{version}}/surface/api/view-mail)
* Menus, Surface layer: radio items (`radio`, `on`), `MenuRadioChosen`, `setRadio()` / `radio()` / `setItemLabel()` / `itemLabel()`; context menus take toggles and radios and keep the user's choices; `TKPrimitive::popupMenu()`; `TKTabView::addPage(…, ?index)`. Released in v0.11.0. [menu profiles](/docs/{{version}}/surface/api/menu-profiles), [mail](/docs/{{version}}/surface/api/window-mail), [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives)
* Canvas scrolling, Surface layer: `TKScrollBar`, `ScrollChanged`, hover mail (`CanvasMoved`, `CanvasEntered`, `CanvasLeft`), `ScrollPhase` on `CanvasWheeled`; `Framebuffer::scroll()`, `RenderingEngine::canScroll()` / `scroll()`. Released in v0.11.0. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [view mail](/docs/{{version}}/surface/api/view-mail), [drawing](/docs/{{version}}/surface/architecture/drawing), [framebuffers](/docs/{{version}}/surface/architecture/framebuffers)
* Path bar and toolbar, Surface layer: `TKComboBox`, `TKMenuButton`, button images (`HasButtonImage`, `ImagePosition`) on push and toggle buttons. Released in v0.11.0. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives)

### 2026-10-23

* `TKPrimitive::focus()` refuses a primitive under a hidden container ("not shown") and one disabled itself or through a container ("cannot take focus"), without asking the native: a toolkit would focus a widget the user cannot see or use. Released in v0.10.5. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives)

### 2026-10-22

* Focus and window keys (compare-app toolkit C9), Surface layer: `TKPrimitive::focus()` / `hasFocus()`, `TKCanvas::setFocusable($on, $takesTab)` / `isFocusable()` / `takesTab()`, `ToolkitWindow::focused()` / `setInitialFocus()`; `FocusGained`, `FocusLost`, `WindowKeyPressed`; the key precedence. Released in v0.10.5. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [windows](/docs/{{version}}/surface/architecture/windows), [view mail](/docs/{{version}}/surface/api/view-mail), [mail](/docs/{{version}}/surface/api/window-mail)

### 2026-10-21

* Dialogs, clipboard and desktop (compare-app toolkit C7), Surface layer: `Dialogs`, `Clipboard`, `Desktop`, `Alert`, `OpenRequest`, `SaveRequest`; `AlertAnswered`, `FilesChosen`; `ToolkitDialogs` (request ids, one modal per parent, parent-close answers); `dialogs()` / `clipboard()` / `desktop()` on drivers and `ToolkitWindowManager`. Released in v0.10.5. [windows](/docs/{{version}}/surface/architecture/windows), [mail](/docs/{{version}}/surface/api/window-mail)

### 2026-10-20

* Modal children, close veto and button roles (compare-app toolkit C6), Surface layer: `ToolkitWindowDriver::open()` and `ToolkitWindowManager::open()` take a parent; `ToolkitWindow::parent()`, `confirmClose()`, `isConfirmingClose()`; `ChildWindows` (parent rules, `childOf`); `ButtonRole`, `TKButton::setRole()` / `role()` / `holder()`. Released in v0.10.5. [windows](/docs/{{version}}/surface/architecture/windows)
* Menu enabled state and accelerators (compare-app toolkit C5), Surface layer: `Accelerator`, `MenuStates`, node keys `keys` and `enabled`, `hotkey` limited to accelerator characters, id and accelerator collisions refused, `setItemEnabled()` / `isItemEnabled()` on windows, drivers and `ToolkitWindowManager`. Released in v0.10.5. [menu profiles](/docs/{{version}}/surface/api/menu-profiles)

### 2026-10-19

* Canvas pointer (compare-app toolkit C4), Surface layer: `TKCanvas::watchPointer()` / `isWatchingPointer()` (abstract flag, nothing written to the native, `WindowException` once removed); `CanvasPressed`, `CanvasDragged`, `CanvasReleased`, `CanvasWheeled` with the press and wheel rules. Released in v0.10.5. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [view mail](/docs/{{version}}/surface/api/view-mail)

### 2026-10-18

* Tree (compare-app toolkit C3): `TKTree` over `TreeNode`s (cells and colours per column, children), expansion record kept across collapse and `setNodes`; `NodeSelected`, `NodeActivated`, `NodeExpanded`. Released in v0.10.5. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [view mail](/docs/{{version}}/surface/api/view-mail)

### 2026-10-16

* Split and tabs: `TKSplitView` (`split(name, horizontal)`, panes, divider positions as fractions of visible panes) and `TKTabView` (`tabs(name)`, pages as columns, titles, selection); `SplitMoved` and `TabSelected` view mail. Released in v0.10.2. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [view mail](/docs/{{version}}/surface/api/view-mail)

### 2026-10-15

* Text panes: `TKTextArea` read-only, wrap, line backgrounds, range styles, line selection, scroll position and `ViewScrolled`; `FontSpec` monospace; `TextRangeStyle` and `ScrollPosition`. [primitives](/docs/{{version}}/surface/architecture/toolkit-primitives), [styling](/docs/{{version}}/surface/api/styling), [view mail](/docs/{{version}}/surface/api/view-mail)

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
