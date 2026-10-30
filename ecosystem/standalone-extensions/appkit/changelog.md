# Changelog

What changed in this package, newest first.

### 2026-10-28

* **Version**: 0.11.0 in `PHP_APPKIT_VERSION` (`php_appkit.h`); `branch-alias` `dev-main` is `0.11.x-dev`. Promoted with the Venusian 0.11 ecosystem. No API or behaviour change. SurfaceTest expects `NSPopUpButton`'s parent `NSButton`, as the 2026-10-23 surface change declared. Built and loaded on Homebrew PHP 8.4 NTS and ZTS: 347 passed, 10 skipped on each.

### 2026-10-27

* `NSAlert` alertStyle (`NSAlertStyle`), showsSuppressionButton and suppressionButton (+set); `NSSavePanel` allowedContentTypes and showsHiddenFiles (+set), each with its own main-thread site; `UTType` typeWithFilenameExtension: and identifier (UniformTypeIdentifiers framework, any thread); `NSPasteboard` availableTypeFromArray: and changeCount. Array setters skip entries of the wrong type. 669 / 7210. Shipped in tag v0.11.0 (`PHP_APPKIT_VERSION` 0.11.0).

### 2026-10-26

* `NSResponder::interpretKeyEvents` (its own main-thread site); glue `ObjCFocusView` forwards `keyDown:`, `keyUp:`, `flagsChanged:`, `insertText:replacementRange:` and `doCommandBySelector:` to PHP handlers (false = NSView's own) and conforms to `NSTextInputClient`, holding a dead key's marked text itself. 658 / 7210. Shipped in tag v0.11.0 (`PHP_APPKIT_VERSION` 0.11.0). [glue](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines)
* Glue `ObjCFocusView` forwards the standard edit actions `cut:`, `copy:`, `paste:`, `selectAll:`, `undo:`, `redo:` with their sender (false = next responder), answering `respondsToSelector:` for each only while a handler is set. Shipped in tag v0.11.0 (`PHP_APPKIT_VERSION` 0.11.0). [glue](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines)

### 2026-10-24

* `NSScroller` `rectForPart:` (scroller coordinates) and `testPart:` (window coordinates, as an event's `locationInWindow`): a scroller that tracks its own knob drag, so the app's loop runs during it. Shipped in tag v0.11.0 (`PHP_APPKIT_VERSION` 0.11.0).

### 2026-10-23

* `NSComboBox` (object values as strings), `NSScroller` (style, knob proportion, hit part, width per style, the preferred-style notification), `NSTrackingArea`, `NSButton` image, image position (`NSCellImagePosition`) and bordered, `NSMenuItem` image, `NSControl` refusesFirstResponder, `NSView` convertRect:toView: and tracking areas, `NSEvent` phase / momentumPhase / trackingArea (`NSEventPhase`), `NSWindow` child windows (`NSWindowOrderingMode`) and convertRectToScreen:, `NSTabView` insertTabViewItem:atIndex:. `NSPopUpButton` extends `NSButton`, as the header declares. Each new UI method has its own main-thread site; NSEvent and NSTrackingArea readers have none. 655 / 7210. Shipped in tag v0.11.0 (`PHP_APPKIT_VERSION` 0.11.0). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-22

* Key-view loop: `NSView` nextKeyView (+set); `NSWindow` initialFirstResponder (+set), selectNextKeyView:, selectPreviousKeyView:, setAutorecalculatesKeyViewLoop:; `NSResponder` acceptsFirstResponder; glue `ObjCFocusView` (acceptsFirstResponder handler) and `ObjCKeyWindow` (keyDown: handler; false = NSWindow's own). Each with its own main-thread site. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface), [glue](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines)
* Coverage: `scripts/support.php` writes `SUPPORT.md` (every live AppKit method and property accessor from clang's AST dump of the SDK headers, bound or not; protocol methods not counted; a stub method on a subclass counts for the ancestor's member) and the README API badge; `--check` compares without the date. 609 / 7210 on the macOS SDK.
* Fix: an enum read with an int fallback (`NSEvent::type()`, button and menu item `state`) crashed on a value no case has: Zend answers it with SUCCESS and no case. It now returns the int. An `NSOpenPanel` sheet posts the private event type 21. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-21

* `NSAlert`, `NSPanel`, `NSSavePanel`, `NSOpenPanel` (each UI method with its own main-thread site; both `beginSheetModalForWindowCompletionHandler` forward a `^(NSModalResponse)` block), `NSPasteboard` (any thread), `NSAlertFirstButtonReturn`, `NSModalResponseOK`, `NSModalResponseCancel`, `NSPasteboardTypeString`. Shipped in tag v0.10.5 (`PHP_APPKIT_VERSION` 0.10.5; there are no v0.10.3 or v0.10.4 tags). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-20

* `NSWindow` sheets (`beginSheetCompletionHandler` forwards a `^(NSModalResponse)` block to the closure, `endSheet`, `endSheetReturnCode`, `sheets`, `attachedSheet`, `sheetParent`), `NSButton::keyEquivalent` / `setKeyEquivalent`, `NSView::isHiddenOrHasHiddenAncestor`; each with its own main-thread site. Shipped in tag v0.10.5 (`PHP_APPKIT_VERSION` 0.10.5; there are no v0.10.3 or v0.10.4 tags). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* `NSMenu::performKeyEquivalent` (its own main-thread site), `CGEvent::createKeyboardEvent`, `getFlags`, `setFlags`, the arrow, F1-F12, Delete, Home, End, Page Up and Page Down function-key characters, `NSBackspaceCharacter`, `NSTabCharacter`. AppKit matches a key equivalent's Shift exactly only for a key event that carries its Quartz event (`eventWithCGEvent`); one made with `keyEventWithType…` matches Shift loosely. Shipped in tag v0.10.5 (`PHP_APPKIT_VERSION` 0.10.5; there are no v0.10.3 or v0.10.4 tags). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-18

* `NSOutlineView` (outline column, expand/collapse, item ↔ row, reload, indentation), `NSTableView` double action, clicked row, `scrollRowToVisible:`, `NSString` (`stringWithString:`, `UTF8String`; every AppKit string boxes as it), `NSNotification::userInfo`, `NSCarriageReturnCharacter` / `NSEnterCharacter`. Each new UI method carries its own main-thread site. Shipped in tag v0.10.5 (`PHP_APPKIT_VERSION` 0.10.5; there are no v0.10.3 or v0.10.4 tags). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-16

* 1:1 remediation, 0.10.2. Names and types native: `CMTime::make` / `makeWithSeconds` / `getSeconds`, `CFType::copyDescription`, `NSRequestUserAttentionType::*_REQUEST`, `NSTextBlockValueType::*_VALUE_TYPE`, `glyphRangeForCharacterRangeActualCharacterRange`, `?CFAllocator` on CF creators, `?CGEventSource` on CGEvent creators, `?NSGraphicsContext` on NSEvent constructors, every struct field required. New 1:1 bindings: `CGColor`, `CFAllocator`, `CGEventSource::create`, `NSError`, `NSLayoutDimension` / `NSLayoutXAxisAnchor` / `NSLayoutYAxisAnchor` (the `…ToConstant` methods on the dimension), CALayer backgroundColor / contents / contentsGravity / masksToBounds, `NSColor` CGColor / colorWithCGColor: / colorUsingColorSpace:, `NSWindow` canBecomeKeyWindow / canBecomeMainWindow, `NSGridCell::emptyContentView`, `ObjCObserver::OPTION_PRIOR`, `kCGError*`, `kIOReturnSuccess`. Pass-through: CGError / IOReturn returned as `int` (out-parameters by reference), null from CF/CG creates, AppKit's clamps and exceptions, availability through the unrecognized-selector exception; the main-thread gate only on AppKit UI classes. Kept refusals only at eight probed crash sites, each `/* binding:<id> */` with a `tests/Probes` test and the `--enable-appkit-probes` build. Glue forwards only: `ObjCOpenGLView` hands `(view, dirty)` with no make-current/flush, `ObjCStageWindow` `on`/`off` handlers for both overrides, `ObjCObserver` native options + context + whole change dictionary, local monitor return passed to AppKit, delegate structs and `char` marshalled both ways, `createDirect` untagged. Invented API removed: NSView `layer*` helpers and `setLayer:` wantsLayer toggling, `NSAttributedString::attributeAtIndex`, NSColor sRGB conversion, NSGridView null ↔ empty cell, `ObjCStageWindow::canBecomeKey` / `setCanBecomeKey`, `CMTime::withSeconds` / `seconds`, `CFType::description`. AGENTS.md. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface), [glue](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines), [errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/errors-and-threads)
* NSSplitView (divider style, positions, arranged subviews, holding priorities), NSTabView and NSTabViewItem, NSEvent local event monitors (compare-app split and tabs, C2). 0.10.2. [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

### 2026-10-14

* Text storage attributes (NSMutableAttributedString, NSTextStorage, foreground and background colour names), NSTextBlock and paragraph text blocks, NSClipView scrolling and bounds notifications, NSTextView selection, resizing and max size, NSTextContainer size and width tracking, NSLayoutManager glyph ranges and rects, the monospaced system font; NSRange returned (compare-app text panes, C1). Shipped in tag v0.10.1 (`PHP_APPKIT_VERSION` 0.10.1). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)
* attribute:atIndex:effectiveRange:; colour, paragraph-style, font and link attribute values of the wrong class refused with TypeError instead of failing at draw time (C1 final review). [surface](/docs/{{version}}/ecosystem/standalone-extensions/appkit/guide/binding-surface)

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
