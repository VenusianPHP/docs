# Binding surface

Classes, enums and constants ext-appkit binds, each method one AppKit or CoreFoundation call.

## Overview

Scope: calls that start AppKit, stage a window for a game engine (window modes, screens, display modes and capture, partial redraw, display-link pacing, swap interval, power assertions), present/withdraw app from OS, pump events, sleep with a budget, wake a sleep, open/close windows, build the main menu. Stubs = source of truth; `tests/SurfaceTest.php` fails if a stub declaration is missing from the build.[^stubs]

Naming, all fixed:

* Class = native class name, global namespace (`NSApplication`, `CFRunLoop`).
* ObjC selector = method named by joining selector parts, later parts capitalised: `nextEventMatchingMask:untilDate:inMode:dequeue:` → `nextEventMatchingMaskUntilDateInModeDequeue()`. Class methods static.
* CF function on a type = method with type prefix dropped: `CFRunLoopAddSource` → `CFRunLoop::addSource()`. Create/Get functions static.
* NS_ENUM / CF enum = backed int enum, prefix dropped, cases SCREAMING_SNAKE (`NSApplicationActivationPolicy::REGULAR`). Values from SDK headers.[^sdk]
* NS_OPTIONS param = `Enum|int`: pass a case or OR'd ints (`NSEventMask::ANY` = -1 = NSUIntegerMax).
* Enum return with values outside the header (private event types) = `Enum|int`.
* Void selector → `void`. BOOL → `bool`. NSInteger/NSUInteger → `int`. NSTimeInterval → `float`.
* Global C/ObjC constants = PHP global constants, same name, value read from framework at MINIT.

## Schema

| Class | Binds |
|---|---|
| `NSObject` | className, isKindOfClass:, respondsToSelector:, isEqual:, hash, description; `pointer()` = address for other exts; static `fromPointer(int)` = object at a trusted non-zero address, must be a kind of the called class (else `TypeError` "is an X, not a Y") |
| `CALayer` | static layer, contentsScale (+set), sublayers (list, each boxed as its nearest mapped class), addSublayer:; a `CAMetalLayer` from ext-metal boxes as `CALayer` via `CALayer::fromPointer($layer->pointer())` |
| `NSResponder` | hierarchy only |
| `NSApplication` | sharedApplication, finishLaunching, run, stop:, isRunning, isActive, activationPolicy, setActivationPolicy:, activate, activateIgnoringOtherApps:, deactivate, nextEventMatchingMask:untilDate:inMode:dequeue:, discardEventsMatchingMask:beforeEvent:, sendEvent:, postEvent:atStart:, currentEvent, updateWindows; applicationIconImage, setApplicationIconImage: (null restores the bundle icon), requestUserAttention: (`NSRequestUserAttentionType`), cancelUserAttentionRequest: |
| `NSWindow` | initWithContentRect:styleMask:backing:defer: (alloc+init, static, allocates the called class), title/setTitle:, makeKeyAndOrderFront:, orderOut:, close, performClose:, miniaturize:, isVisible, isKeyWindow, isMainWindow, makeKeyWindow, delegate/setDelegate:, isReleasedWhenClosed/setReleasedWhenClosed:, center, contentView, windowNumber, frame, setContentSize:, styleMask, backingScaleFactor; staged window: setStyleMask:, contentMin/MaxSize (+set), contentAspectRatio (+set), setFrameOrigin:, setFrame:display:, contentRectForFrameRect:, frameRectForContentRect:, convertRectToBacking:, orderFront:, zoom:, isZoomed, deminiaturize:, isMiniaturized, toggleFullScreen:, collectionBehavior (+set, `NSWindowCollectionBehavior`), level (+set, `NS*WindowLevel` or `CGDisplay::shieldingWindowLevel()`), screen, isOpaque/setOpaque:, backgroundColor (+set, null = default), hasShadow (+set), titlebarAppearsTransparent (+set), titleVisibility (+set), ignoresMouseEvents (+set), isMovableByWindowBackground (+set), occlusionState (`NSWindowOcclusionState` bits), alphaValue (+set), acceptsMouseMovedEvents (+set), static windowNumberAtPoint:belowWindowWithWindowNumber: (any app's window; one not yet on screen is not found), makeFirstResponder:, firstResponder |
| `NSView` | initWithFrame: (static, allocates the called class), frame/setFrame:, window, menu, superview, subviews, addSubview:, removeFromSuperview, isHidden/setHidden:, content hugging / compression resistance priority per orientation (+set), fittingSize, intrinsicContentSize, layoutSubtreeIfNeeded, visibleRect, scrollPoint:, translatesAutoresizingMaskIntoConstraints (+set), wantsLayer (+set), layer / setLayer: (`?CALayer`; set turns wantsLayer on and hosts the layer, null puts a fresh backing layer back: wantsLayer off and on), layerBackgroundColor (+set: turns the layer on, null clears), layerContents / layerContentsGravity / layerMasksToBounds (+set: layer.contents as an NSImage or a CGImage, kCAGravity*, masksToBounds; each turns the layer on), postsFrameChangedNotifications (+set), postsBoundsChangedNotifications (+set), setNeedsDisplay: / needsDisplay (an `NSOpenGLView` reads false at once; the draw it schedules still comes), width/height/leading/trailing/top/bottom/centerX/centerY anchors; bounds, convertRectToBacking:, convertSizeToBacking:, setNeedsDisplayInRect: (partial redraw), displayIfNeeded, layerContentsRedrawPolicy (+set), displayLinkWithTarget:selector: (macOS 14+, a `CADisplayLink` not yet on a run loop), safeAreaRect (macOS 11), hitTest: (point in the superview; null outside), convertPoint:fromView: (null view = window base), isFlipped |
| `NSLayoutAnchor` | constraintEqualToAnchor:, constraintEqualToAnchor:constant:, constraintEqualToConstant:, constraintGreaterThanOrEqualToAnchor: / constraintLessThanOrEqualToAnchor: (± constant:), constraintGreaterThanOrEqualToConstant:, constraintLessThanOrEqualToConstant: (constant-only forms: NSLayoutDimension only, else AppKitException); one PHP class for dimension/x-axis/y-axis anchors |
| `NSLayoutConstraint` | activateConstraints:, deactivateConstraints: (static, arrays type-checked), isActive/setActive:, constant/setConstant:, priority/setPriority: |
| `NSStackView` | stackViewWithViews:, orientation, spacing, edgeInsets, alignment, distribution (+ setters), addArrangedSubview:, insertArrangedSubview:atIndex:, removeArrangedSubview:, arrangedSubviews, customSpacingAfterView: / visibilityPriorityForView: / huggingPriorityForOrientation: (+ setters) |
| `NSGridView` | gridViewWithNumberOfColumns:rows:, numberOfRows, numberOfColumns, addRowWithViews:, insertRowAtIndex:withViews:, removeRowAtIndex:, addColumnWithViews:, rowSpacing/columnSpacing (+ setters), cellAtColumnIndex:rowIndex:, mergeCellsInHorizontalRange:verticalRange:, rowAtIndex:, columnAtIndex:; a null view = `NSGridCell.emptyContentView` |
| `NSGridCell`, `NSGridRow`, `NSGridColumn` | contentView (+set; empty sentinel ↔ null), x/yPlacement (+set); height, topPadding, bottomPadding, yPlacement (+set); width, leadingPadding, trailingPadding, xPlacement (+set) |
| `NSColor` | colorWithRed:green:blue:alpha:, red/green/blue/alphaComponent (via sRGB colour space) |
| `NSFont` | systemFontOfSize:weight:, monospacedSystemFontOfSize:weight:, fontWithName:size: (null when unknown), pointSize, familyName (nullable); `WEIGHT_*` = NSFontWeight* |
| `NSFontManager` | sharedFontManager, fontWithFamily:traits:weight:size: (0–15 weight scale; null when the family is missing), weightOfFont: |
| `NSControl` | sendAction:to:, isEnabled/setEnabled:, target/setTarget:, action/setAction: (selector name), stringValue/doubleValue/integerValue (+ setters), font/setFont:, alignment/setAlignment:, sizeToFit, performClick: |
| `NSTextField`, `NSSecureTextField` | labelWithString:, labelWithAttributedString:, attributedStringValue, allowsEditingTextAttributes, isSelectable, textFieldWithString:, placeholderString, isEditable, isBezeled, drawsBackground, textColor, backgroundColor, lineBreakMode, maximumNumberOfLines, preferredMaxLayoutWidth, delegate (+ setters); initWithFrame: |
| `NSAttributedString` | initWithString:attributes: (string keys; values strings, numbers, ext objects), string, length, attribute:atIndex: (boxed, string or number, null when absent), attribute:atIndex:effectiveRange: ([value, NSRange run]; index within the string, else ValueError); constants `NSLinkAttributeName`, `NSFontAttributeName`, `NSParagraphStyleAttributeName`, `NSForegroundColorAttributeName`, `NSBackgroundColorAttributeName` |
| `NSMutableAttributedString`, `NSTextStorage` | addAttribute:value:range:, removeAttribute:range: (range within the string, else ValueError; colour/paragraph-style/font/link values of the wrong class, here and in initWithString:attributes:, are TypeErrors), setAttributedString:, begin/endEditing; a text view's textStorage |
| `NSParagraphStyle`, `NSMutableParagraphStyle` | alignment, textBlocks; init, setAlignment: (an attributed value's alignment), setTextBlocks: |
| `NSTextBlock` | init, backgroundColor (+set), setValue:type:forDimension:, valueForDimension:, valueTypeForDimension: (`NSTextBlockValueType`, `NSTextBlockDimension`); NSParagraphStyle textBlocks, NSMutableParagraphStyle setTextBlocks: |
| `NSWorkspace` | sharedWorkspace, openURL: |
| `NSButton`, `NSSwitch` | buttonWithTitle:target:action:, checkboxWithTitle:target:action:, setButtonType:, title/setTitle:, state/setState:, contentTintColor/setContentTintColor:; initWithFrame:, state/setState: |
| `NSSlider` | sliderWithValue:minValue:maxValue:target:action:, minValue/maxValue (+ setters), isContinuous/setContinuous: |
| `NSPopUpButton` | initWithFrame:pullsDown:, addItemWithTitle:, addItemsWithTitles:, removeAllItems, numberOfItems, indexOfSelectedItem, selectItemAtIndex:, titleOfSelectedItem, itemTitles |
| `NSDatePicker`, `NSTimeZone` | initWithFrame:, dateValue/setDateValue:, timeZone/setTimeZone: (NSTimeZone timeZoneWithName:, name), setDatePickerStyle:, setDatePickerElements: (`ELEMENT_*` ints), setDatePickerMode: |
| `NSProgressIndicator` | initWithFrame:, setStyle:, minValue/maxValue/doubleValue (+ setters), isIndeterminate/setIndeterminate:, startAnimation:, stopAnimation:, setDisplayedWhenStopped: |
| `NSImage`, `NSImageView` | initWithContentsOfFile: (null when unreadable), initWithCGImage:size:, size; imageViewWithImage:, initWithFrame:, image/setImage:, imageScaling/setImageScaling: |
| `NSBox`, `NSScrollView` | initWithFrame:, boxType/setBoxType:; initWithFrame:, contentView (NSClipView), documentView/setDocumentView:, hasVerticalScroller, hasHorizontalScroller, drawsBackground (+ setters), contentSize, reflectScrolledClipView:, documentVisibleRect |
| `NSClipView` | scrollToPoint: (NSScrollView contentView, reflectScrolledClipView:, documentVisibleRect) |
| `NSTextView` | scrollableTextView (static, returns the NSScrollView), initWithFrame:, string/setString:, isEditable/setEditable:, backgroundColor/drawsBackground (+set), layoutManager, textContainer, textContainerInset (NSLayoutManager ensureLayoutForTextContainer:, usedRectForTextContainer:, glyphRangeForCharacterRange:, boundingRectForGlyphRange:inTextContainer:, allowsNonContiguousLayout (+set); NSTextContainer widthTracksTextView, size (+setters)), font/setFont:, textColor/setTextColor:, delegate/setDelegate:, textStorage, selectedRange/setSelectedRange:, scrollRangeToVisible:, horizontallyResizable (+set), maxSize (+set) |
| `NSTableView` | initWithFrame:, addTableColumn:, removeTableColumn:, tableColumns, dataSource/setDataSource:, delegate/setDelegate:, reloadData, numberOfRows, selectedRow, selectRowIndexes:byExtendingSelection:, deselectAll:, setAllowsEmptySelection:, setUsesAlternatingRowBackgroundColors:, backgroundColor/setBackgroundColor:, headerView/setHeaderView:, preparedCellAtColumn:row:, viewAtColumn:row:makeIfNecessary: |
| `NSTableColumn`, `NSTableHeaderView`, `NSCell`, `NSIndexSet` | initWithIdentifier:, identifier, title/setTitle:, width/setWidth:, setResizingMask: (`RESIZING_MASK_*`); initWithFrame: (inherited); objectValue (Foundation values as PHP scalars); indexSetWithIndex:, firstIndex, count |
| `NSNotificationCenter`, `NSNotification`, `NSOperationQueue` | defaultCenter, addObserverForName:object:queue:usingBlock: (block = PHP callable, returns the token), removeObserver:, postNotificationName:object:; name, object; mainQueue, init (alloc+init), waitUntilAllOperationsAreFinished; constants NSApplicationDidResignActiveNotification, NSViewBoundsDidChangeNotification |
| `NSURL` | fileURLWithPath:, URLWithString: (null when unparsable), path, absoluteString |
| `AVPlayerItem` | playerItemWithURL:, status, duration, error |
| `AVPlayer` | playerWithPlayerItem:, actionAtItemEnd/setActionAtItemEnd: (AVPlayerActionAtItemEnd), play, pause, rate/setRate:, currentTime, seekToTime:, isMuted/setMuted:, timeControlStatus, currentItem, replaceCurrentItemWithPlayerItem: |
| `AVPlayerView` | initWithFrame:, player/setPlayer:, controlsStyle/setControlsStyle: |
| `NSMenu` | initWithTitle:, title/setTitle:, addItem:, insertItem:atIndex:, removeItem:, removeAllItems, numberOfItems, itemAtIndex:, indexOfItem:, autoenablesItems/setAutoenablesItems:, update, performActionForItemAtIndex:, popUpMenuPositioningItem:atLocation:inView: (tracks until closed; true = an item chosen; runs common-mode run loop sources while open), cancelTracking |
| `NSMenuItem` | initWithTitle:action:keyEquivalent:, separatorItem, title/setTitle:, isSeparatorItem, hasSubmenu, submenu/setSubmenu:, menu, target/setTarget:, action/setAction: (selector name), state/setState:, isEnabled/setEnabled:, keyEquivalent/setKeyEquivalent:, keyEquivalentModifierMask/setKeyEquivalentModifierMask:, tag/setTag: |
| `NSRect`, `NSSize`, `NSEdgeInsets`, `NSRange`, `CMTime` | value classes like `NSPoint`; `NSRange` must be non-negative and is returned as well as taken; `CMTime` = value, timescale, flags (`FLAG_*`), epoch; `CMTime::withSeconds()` = CMTimeMakeWithSeconds, `seconds()` = CMTimeGetSeconds (NaN invalid/indefinite, ±INF) |
| `ObjCDelegate` | trampoline: `new ObjCDelegate(protocol)`, `on(selector, callable)`, `off(selector)`; answers the protocol's selectors by calling PHP (see [glue](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/glue-trampolines)) |
| `ObjCTarget` | trampoline: `new ObjCTarget(callable)`; `ObjCTarget::ACTION` (`action:`) calls PHP with the sender |
| `NSOpenGLPixelFormat`, `NSOpenGLContext`, `NSOpenGLView` (`OpenGL.framework`, built with `GL_SILENCE_DEPRECATION`) | pixel format: static initWithAttributes (a 0-terminated int list; not ending in 0 is a ValueError; null when no renderer matches); context: static initWithFormatShareContext (null when none), makeCurrentContext, static clearCurrentContext / currentContext, CGLContextObj (the address ext-opengl's `CGLContextObj::fromPointer()` takes), flushBuffer, update, view / setView; view: static initWithFramePixelFormat (null format = AppKit's default), openGLContext (+set), pixelFormat, wantsBestResolutionOpenGLSurface (+set); constants `NSOpenGLPFAOpenGLProfile`, `NSOpenGLProfileVersionLegacy`, `NSOpenGLProfileVersion3_2Core`, `NSOpenGLProfileVersion4_1Core`, `NSOpenGLPFAAccelerated`, `NSOpenGLPFAColorSize`, `NSOpenGLPFAAlphaSize`, `NSOpenGLPFADoubleBuffer`, `NSOpenGLPFADepthSize`, `NSOpenGLPFAStencilSize`; context setValues:forParameter: / getValues:forParameter: (`NSOpenGLContextParameter`, ≤ 4 ints; SWAP_INTERVAL 0/1 = vsync off/on) |
| `ObjCOpenGLView` | trampoline: static `initWithFramePixelFormatDraw(NSRect, ?NSOpenGLPixelFormat, callable)`; `drawRect:` makes the view's context current, calls `$draw(ObjCOpenGLView $view)` (framebuffer 0 is the view's), then flushes the context |
| `ObjCStageWindow` | NSWindow subclass: `canBecomeKey()` / `setCanBecomeKey(bool)` answer `canBecomeKeyWindow` and `canBecomeMainWindow`, YES by default, so a borderless window takes focus; made with the inherited `initWithContentRectStyleMaskBackingDefer()` |
| `ObjCDrawView` | trampoline: static `initWithFrameDraw(NSRect, callable)`; `drawRect:` calls PHP with `(view, NSRect dirty)` inside the view's graphics context: mark rects with `setNeedsDisplayInRect:` and AppKit asks for only those (partial redraw) |
| `NSGraphicsContext`, `CGContext` | currentContext, CGContext; CGContextSaveGState / RestoreGState / ClipToRect / TranslateCTM / ScaleCTM / SetInterpolationQuality / GetInterpolationQuality (`CGInterpolationQuality`, NONE = nearest) / DrawImage |
| `NSScreen` | mainScreen, screens (menu-bar screen first), frame, visibleFrame, backingScaleFactor, maximumFramesPerSecond, localizedName, deviceDescription (array: `NSScreenNumber` = CGDirectDisplayID, `NSDeviceSize`/`NSDeviceResolution` as `NSSize`), maximumExtendedDynamicRangeColorComponentValue, maximumPotentialExtendedDynamicRangeColorComponentValue |
| `CGDisplay`, `CGDisplayMode` | static CGMainDisplayID, CGGetActiveDisplayList, CGDisplayBounds, CGDisplayCopyDisplayMode, CGDisplayCopyAllDisplayModes (options array, `kCGDisplayShowDuplicateLowResolutionModes` lists the HiDPI modes), CGDisplaySetDisplayMode, CGDisplayCapture, CGDisplayRelease, CGShieldingWindowLevel (a display named by its int id; a CGError throws `AppKitException` with the error as code); mode GetWidth/GetHeight/GetPixelWidth/GetPixelHeight/GetRefreshRate/IsUsableForDesktopGUI |
| `CADisplayLink`, `CAFrameRateRange`, `NSRunLoop` | link timestamp, targetTimestamp, duration, preferredFrameRateRange (+set), addToRunLoop:forMode:, removeFromRunLoop:forMode:, isPaused/setPaused:, invalidate (macOS 14+); range value class (minimum, maximum, preferred); mainRunLoop, currentRunLoop, getCFRunLoop |
| `NSProcessInfo`, `IOPMAssertion` | processInfo, beginActivityWithOptions:reason: (`NSActivityOptions`, returns the token), endActivity:; static IOPMAssertionCreateWithName (returns the IOPMAssertionID), IOPMAssertionRelease (an IOReturn error throws `AppKitException`) |
| `ObjCObserver` | KVO trampoline: `new ObjCObserver(callable)`, `observe(object, keyPath, OPTION_*)`, `stop(object, keyPath)`; handler gets (keyPath, object, change['new'/'old'], geometry as NSRect/NSSize/NSPoint); a refused key path throws and is not recorded; observed objects retained until stop()/free, pairs still observed removed at free |
| `NSEvent` | otherEventWithType:location:modifierFlags:timestamp:windowNumber:context:subtype:data1:data2:, mouseEventWithType:location:modifierFlags:timestamp:windowNumber:context:eventNumber:clickCount:pressure: (a made event's buttonNumber is 0), type, buttonNumber, subtype, modifierFlags, timestamp, windowNumber, locationInWindow, data1, data2, keyEventWithType:location:modifierFlags:timestamp:windowNumber:context:characters:charactersIgnoringModifiers:isARepeat:keyCode: (KeyDown, KeyUp, FlagsChanged), eventWithCGEvent:, mouseLocation (screen, origin bottom left), pressedMouseButtons (bit mask), keyCode, characters / charactersIgnoringModifiers (key events only; others raise), isARepeat, clickCount, deltaX/deltaY, scrollingDeltaX/scrollingDeltaY, hasPreciseScrollingDeltas, isDirectionInvertedFromDevice, window |
| `CGEvent` (enums `CGEventType`, `CGMouseButton`, `CGScrollEventUnit`; constants `kCGMouseEvent*`) | static CGEventCreateMouseEvent, CGEventCreateScrollWheelEvent2 (1–3 wheels); Get/SetIntegerValueField, Get/SetLocation (Quartz: origin top left of the main screen). Source must be null: no CGEventSource is bound. For the NSEvents AppKit cannot construct (scroll, other buttons, motion deltas), through `NSEvent::eventWithCGEvent()`; such an event has window number 0 and a screen location. `CGEventSource` (enum `CGEventSourceStateID`): static keyState (CGEventSourceKeyState) only |
| `GCController`, `GCControllerPlayerIndex`, `GCPhysicalInputProfile`, `GCExtendedGamepad`, `GCMicroGamepad`, `GCControllerElement`, `GCControllerButtonInput`, `GCControllerAxisInput`, `GCControllerDirectionPad` (GameController.framework) | static controllers, startWirelessControllerDiscoveryWithCompletionHandler: (callout; macOS 15.4.1 never calls it, measured), stopWirelessControllerDiscovery, shouldMonitorBackgroundEvents (+set; 15.4.x reads it back false); vendorName, extendedGamepad, microGamepad, playerIndex (+set). Extended: dpad, buttonA/B/X/Y, thumbsticks, shoulders, triggers, buttonMenu, buttonOptions/buttonHome/thumbstick buttons (nullable). Micro: dpad, buttonA/X, buttonMenu. Button isPressed/value, axis value, direction pad x/yAxis and up/down/left/right. Constants GCControllerDidConnectNotification, GCControllerDidDisconnectNotification. Input reaches the active app only unless background events are granted |
| `NSDate` | date, dateWithTimeIntervalSinceNow:, dateWithTimeIntervalSince1970:, distantPast, distantFuture, timeIntervalSinceNow, timeIntervalSince1970 |
| `NSPoint` | value class: `float $x`, `float $y` |
| `CFType` | CFGetTypeID, CFHash, CFCopyDescription; `pointer()` |
| `CFRunLoop` | GetMain, GetCurrent, Run, RunInMode, Stop, WakeUp, IsWaiting, CopyCurrentMode, AddSource, RemoveSource, ContainsSource |
| `CFRunLoopSource` | GetOrder, Invalidate, IsValid, Signal |
| `CFFileDescriptor` | Create (fd = int, stream or Socket; callout = PHP callable), GetNativeDescriptor, EnableCallBacks, DisableCallBacks, Invalidate, IsValid, CreateRunLoopSource |
| `CFData`, `CGDataProvider`, `CGColorSpace`, `CGImage` | CFDataCreate (copies the bytes), GetLength; CGDataProviderCreateWithCFData (null for empty data); CGColorSpaceCreateWithName (null for an unknown name); CGImageCreate (no decode array; refuses a provider shorter than bytesPerRow × height; null when Core Graphics refuses), GetWidth, GetHeight; CGDataProviderCreateDirect (`createDirect(address, size)`: reads the memory in place, no copy, caller keeps it alive; `CGImage::create` checks a description against its size without copying, the last row needing only its pixels); CGImageCreateWithImageInRect (null when they do not meet) |
| `AppKitException` | extends RuntimeException |

Enums: `NSApplicationActivationPolicy`, `NSEventType`, `NSEventMask`, `NSEventModifierFlags`, `CFRunLoopRunResult`, `NSWindowStyleMask`, `NSBackingStoreType`, `NSWindowCollectionBehavior`, `NSWindowTitleVisibility`, `NSWindowOcclusionState`, `NSViewLayerContentsRedrawPolicy`, `NSOpenGLContextParameter`, `CGInterpolationQuality`, `NSActivityOptions`, `NSControlStateValue`, `NSTextBlockValueType`, `NSTextBlockDimension`.

Ownership: `init…` statics return an object the PHP wrapper owns (+1 from alloc/init, kept, not re-retained). `NSWindow` defaults to `releasedWhenClosed = YES`, which releases the window a second time on close; whoever holds the PHP object sets it to `false`. Weak references in AppKit (`delegate`, `target`) do not keep trampolines alive: hold the PHP object.

Constants: `kCGColorSpaceSRGB`, `kCGImageAlpha{None, PremultipliedLast, PremultipliedFirst, Last, First, NoneSkipLast, NoneSkipFirst}`, `kCGBitmapByteOrder{Default, 32Little, 32Big}`, `kCGRenderingIntentDefault`, `kCFFileDescriptorReadCallBack`, `kCFFileDescriptorWriteCallBack`, `kCFRunLoopDefaultMode`, `kCFRunLoopCommonModes`, `NSDefaultRunLoopMode`, `NSRunLoopCommonModes`, `NSEventTrackingRunLoopMode`, `NSModalPanelRunLoopMode`. Staged windows: `NS{Normal,Floating,Submenu,TornOffMenu,MainMenu,Status,ModalPanel,PopUpMenu,ScreenSaver}WindowLevel`, `kCGDisplayShowDuplicateLowResolutionModes` (value `kCGDisplayResolution`), `kIOPMAssertionType{PreventUserIdleSystemSleep,PreventUserIdleDisplaySleep,PreventSystemSleep}`, `kIOPMAssertionLevel{Off,On}`.

## Examples

Connect (Dock icon up), sleep with a budget, withdraw:

```php
$app = NSApplication::sharedApplication();
$app->finishLaunching();
$app->setActivationPolicy(NSApplicationActivationPolicy::REGULAR);
$app->activate();

$event = $app->nextEventMatchingMaskUntilDateInModeDequeue(
    NSEventMask::ANY, NSDate::dateWithTimeIntervalSinceNow(0.016), NSDefaultRunLoopMode, true,
);
if ($event) {
    $app->sendEvent($event);
}

$app->setActivationPolicy(NSApplicationActivationPolicy::PROHIBITED);
```

Wake a sleep from an fd (kqueue/epoll fd works: it turns readable when its own events are pending). Callout posts an application-defined event so `nextEventMatchingMask…` returns; callbacks are one-shot until `enableCallBacks()` again:

```php
$fd = CFFileDescriptor::create($waiterFd, false, function (CFFileDescriptor $f) use ($app): void {
    $app->postEventAtStart(NSEvent::otherEventWithTypeLocationModifierFlagsTimestampWindowNumberContextSubtypeData1Data2(
        NSEventType::APPLICATION_DEFINED, new NSPoint(), 0, 0.0, 0, null, 0, 0, 0,
    ), false);
    $f->enableCallBacks(kCFFileDescriptorReadCallBack);
});
$fd->enableCallBacks(kCFFileDescriptorReadCallBack);
CFRunLoop::getMain()->addSource($fd->createRunLoopSource(0), kCFRunLoopCommonModes);
```

[^stubs]: Stub files, one per SDK header group
[^sdk]: AppKit SDK headers
