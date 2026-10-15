# Changelog

What changed in this package, newest first.

### 2026-10-10

* `NSParagraphStyle` alignment, `NSMutableParagraphStyle` init / setAlignment:, `NSParagraphStyleAttributeName`: attributed text draws by its paragraph style, not the field's alignment, so a centred link needs one. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* NSAttributedString, NSLinkAttributeName and NSFontAttributeName, NSTextField attributed text, selectable and editing-attributes, NSURL URLWithString / absoluteString, NSWorkspace openURL (toolkit links). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* `NSWindow` makeFirstResponder: / firstResponder, `NSMenu` update: for the Edit menu (HumanInput slice 29). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-09

* `NSEvent::pressedMouseButtons` and `CGEventSource::keyState` (`CGEventSourceKeyState`, `CGEventSourceStateID`): the button and key state AppKit's own tracking loops (controls, menus) keep the release events of. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* Input for HumanInput's appkit engine and the macOS pad source (slice 19): key `NSEvent`s and the key, wheel and delta accessors, `eventWithCGEvent:` over a new `CGEvent` binding (scroll wheels, other buttons, motion deltas), `mouseLocation`, moved-event tracking and the window at a point on `NSWindow`, `NSApplicationDidResignActiveNotification`, and GameController.framework (`GCController` with wireless discovery, background events and player index; extended and micro gamepads; elements). `PHPAppKitBlockCallout` is declared in `runtime.h` for every block-taking selector. Measured on macOS 15.4.1: GameController input reaches the active app only; 15.4.x reads `shouldMonitorBackgroundEvents` back false; discovery's completion handler is never called; a `CGEvent` scroll or mouse event has window number 0 and a screen location. Linking GameController costs no measurable launch time. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* `NSMenu` popUpMenuPositioningItem:atLocation:inView: and cancelTracking. For context menus (HumanInput slice 27). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* `NSView` hitTest:, convertPoint:fromView:, isFlipped; `NSEvent` mouseEventWithType:…pressure:, buttonNumber. For right-click mail (HumanInput slice 26). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-08

* Staged-window scaffold: everything a game engine's window layer asks of a bare AppKit window, no input (HumanInput comes after). Window modes (min/max/aspect, origin, frame↔content rect, zoom, minimize, native full screen + collection behavior, borderless + level, see-through/shadowless/click-through, occlusion), `NSScreen`, `CGDisplay`/`CGDisplayMode` (modes incl. HiDPI, set, capture/release, shielding level), partial redraw (`ObjCDrawView` + `setNeedsDisplayInRect:` + `NSGraphicsContext`/`CGContext`, `CGDataProvider::createDirect` reading a framebuffer in place, `CGImage::createWithImageInRect`), vsync (`CADisplayLink` + `CAFrameRateRange` + `NSRunLoop`, `NSOpenGLContext` swap interval), `NSProcessInfo` activities + `IOPMAssertion`, Dock icon. Links IOKit. Suite 199 on Homebrew PHP 8.4 NTS and ZTS. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface), [glue](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines)
* For the staged-window stager: `NSWindow` alphaValue (+set), `NSView` safeAreaRect, `NSApplication` requestUserAttention: / cancelUserAttentionRequest: with `NSRequestUserAttentionType`, `NSImage::initWithCGImageSize`. `ObjCStageWindow` (key status as a flag; borderless windows take focus); `NSWindow` init allocates the called class. Suite 204.
* `CGImage::create` measures a `createDirect` provider by its recorded size, not a copy; its short-provider error reads "must provide N bytes for that description, it holds M".

### 2026-10-06

* OpenGL views: `NSOpenGLPixelFormat`, `NSOpenGLContext`, `NSOpenGLView`, the `ObjCOpenGLView` trampoline (`drawRect:` calls PHP with the view's context current, then flushes), the `NSOpenGLPFA*` constants, and `NSView::setNeedsDisplay()` / `needsDisplay()`. Built with `GL_SILENCE_DEPRECATION`, linked against `OpenGL.framework`. Suite 159 on Homebrew PHP 8.4 NTS and ZTS. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-05

* `CALayer::sublayers()` / `addSublayer()`: a layer a toolkit nests (Qt's container layer holds its `CAMetalLayer`) is reached from the view's layer. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* Extension version is 0.10.2. Layers: `CALayer` (`layer`, `contentsScale`), `NSView::layer()` / `setLayer()`, `NSObject::fromPointer()` checked against the called class. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-04

* Extension version is 0.10.1. `CFData::create()` also copies `$length` bytes at a trusted address.

### 2026-10-03

* Pixels from bytes: `CFData`, `CGDataProvider`, `CGColorSpace`, `CGImage` and their constants; `NSView::setLayerContents()` takes a `CGImage` as well as an `NSImage`; `NSWindow::backingScaleFactor()`. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-02

* Toolkit primitives slice: view/layout/colour/font, stack and grid, controls, table, KVO + notification observers, AVKit video. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface) rows, new [layout](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/layout-bindings) and [video](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/video-bindings); delegate `@` returns now box PHP strings and numbers.
* Review fixes: delegate object returns retained (+1 autoreleased); callouts refuse foreign threads; `ObjCObserver` rolls back a refused key path; notification blocks take the 1:1 queue (`NSOperationQueue`); constructors/factories build the called class; `CMTime` carries flags/epoch; `NSRange`/`CMTime` readers checked; KVO geometry as value classes; getters for every new setter; `NSCell` + table cell/view readers. [callouts](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/callouts), [video](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/video-bindings), [layout](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/layout-bindings), [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface).
* NSView content hugging / compression resistance, NSScrollView contentView, anchor inequalities, NSView visibleRect / scrollPoint:, NSFontManager, layer contents/gravity/masking + kCAGravity*, NSControlTextDidChangeNotification / NSTextDidChangeNotification, NSView menu, NSControl sendAction:to:, NSTimeZone + NSDatePicker timeZone, AVPlayer actionAtItemEnd, NSTextView/NSTableView background colour, NSTextView layout manager / text container measuring (AppKit driver containers need them). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface).

### 2026-10-01

* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface): NSWindow, NSView, NSMenu, NSMenuItem, NSRect, NSSize, the window/menu enums, NSApplication menu and About calls; ownership note. New [glue trampolines](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines).

### 2026-09-30

* Bundle created with ext-appkit 0.10.0: [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface), [run-loop modes](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/run-loop-modes), [object model](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/object-model), [callouts](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/callouts), [errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/errors-and-threads), [build](/docs/{{version}}/ecosystem/standalone-extensions/appkit/runbooks/build-install-test), [adding a binding](/docs/{{version}}/ecosystem/standalone-extensions/appkit/runbooks/adding-a-binding).
