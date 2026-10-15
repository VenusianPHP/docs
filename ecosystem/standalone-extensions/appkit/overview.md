# Overview

![CI](https://github.com/php-io-extensions/appkit/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/appkit/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/appkit/actions/workflows/ci.yml)

1:1 PHP bindings of AppKit and the CoreFoundation run loop it runs on, written
directly in Objective-C against the Zend API. Each PHP class is its native
counterpart (`NSApplication`, `NSEvent`, `CFRunLoop`, …) and each method is one
native call. No defaults, no composites: behaviour is composed by the caller.

macOS only. PHP 8.4+, NTS and ZTS.

## What is bound

The calls that start AppKit, present the app to the OS and withdraw it, pump
events, sleep with a budget, wake a sleep from a file descriptor, open and close
windows, build the menu bar, lay out and populate views, observe changes, and
play video:

| Class | Native |
|---|---|
| `NSObject`, `NSResponder` | `className`, `isKindOfClass:`, `respondsToSelector:`, `isEqual:`, `hash`, `description`; `pointer()` (the address, for another extension), `fromPointer()` (the object at an address, checked against the called class); `NSResponder`: `nextResponder`, `setNextResponder:` |
| `CALayer` | `layer`, `contentsScale`/`setContentsScale:`, `sublayers`, `addSublayer:` |
| `NSApplication` | `sharedApplication`, `finishLaunching`, `run`, `stop:`, `activationPolicy`, `setActivationPolicy:`, `activate`, `activateIgnoringOtherApps:`, `deactivate`, `isActive`, `isRunning`, `nextEventMatchingMask:untilDate:inMode:dequeue:`, `discardEventsMatchingMask:beforeEvent:`, `sendEvent:`, `postEvent:atStart:`, `currentEvent`, `updateWindows`, `delegate`, `setDelegate:`, `mainMenu`, `setMainMenu:`, `keyWindow`, `mainWindow`, `windows`, `orderFrontStandardAboutPanel:`, `orderFrontStandardAboutPanelWithOptions:`; applicationIconImage, setApplicationIconImage: (null restores the bundle icon), requestUserAttention: (`NSRequestUserAttentionType`), cancelUserAttentionRequest: |
| `NSWindow` | `initWithContentRect:styleMask:backing:defer:` (allocates the called class), `title`, `setTitle:`, `makeKeyAndOrderFront:`, `orderOut:`, `close`, `performClose:`, `miniaturize:`, `isVisible`, `isKeyWindow`, `isMainWindow`, `makeKeyWindow`, `delegate`, `setDelegate:`, `isReleasedWhenClosed`, `setReleasedWhenClosed:`, `center`, `contentView`, `windowNumber`, `frame`, `setContentSize:`, `styleMask`; staged window: setStyleMask:, contentMin/MaxSize (+set), contentAspectRatio (+set), setFrameOrigin:, setFrame:display:, contentRectForFrameRect:, frameRectForContentRect:, convertRectToBacking:, orderFront:, zoom:, isZoomed, deminiaturize:, isMiniaturized, toggleFullScreen:, collectionBehavior (+set, `NSWindowCollectionBehavior`), level (+set, `NS*WindowLevel` or `CGDisplay::shieldingWindowLevel()`), screen, isOpaque/setOpaque:, backgroundColor (+set, null = default), hasShadow (+set), titlebarAppearsTransparent (+set), titleVisibility (+set), ignoresMouseEvents (+set), isMovableByWindowBackground (+set), occlusionState (`NSWindowOcclusionState` bits), alphaValue (+set), `acceptsMouseMovedEvents` (+set), static `windowNumberAtPoint:belowWindowWithWindowNumber:`, `makeFirstResponder:`, `firstResponder` |
| `NSView` | `initWithFrame:` (allocates the class it is called on), `frame`/`setFrame:`, `window`, `menu`, `superview`, `subviews`, `addSubview:`, `removeFromSuperview`, `isHidden`/`setHidden:`, `contentHuggingPriorityForOrientation:`/`setContentHuggingPriority:forOrientation:`, `contentCompressionResistancePriorityForOrientation:`/`setContentCompressionResistancePriority:forOrientation:`, `fittingSize`, `intrinsicContentSize`, `layoutSubtreeIfNeeded`, `visibleRect`, `scrollPoint:`, `translatesAutoresizingMaskIntoConstraints`/`set…:`, `wantsLayer`/`setWantsLayer:`, `layer`/`setLayer:` (null puts a fresh backing layer of the view's own in place), `layerBackgroundColor`/`setLayerBackgroundColor:` (layer.backgroundColor; setting turns the layer on), `layerContents`/`setLayerContents:` (an NSImage), `layerContentsGravity`/`setLayerContentsGravity:` (`kCAGravity*`), `layerMasksToBounds`/`setLayerMasksToBounds:`, `postsFrameChangedNotifications`/`set…:`, `widthAnchor` … `centerYAnchor`; bounds, convertRectToBacking:, convertSizeToBacking:, setNeedsDisplayInRect: (partial redraw), displayIfNeeded, layerContentsRedrawPolicy (+set), displayLinkWithTarget:selector: (macOS 14+, a `CADisplayLink` not yet on a run loop), safeAreaRect (macOS 11), hitTest:, convertPoint:fromView:, isFlipped |
| `NSLayoutAnchor`, `NSLayoutConstraint` | `constraintEqualToAnchor:`, `constraintEqualToAnchor:constant:`, `constraintEqualToConstant:`, `constraintGreaterThanOrEqualToConstant:`, `constraintLessThanOrEqualToConstant:` (dimension anchors only), `constraintGreaterThanOrEqualToAnchor:` / `constraintLessThanOrEqualToAnchor:` (± `constant:`); `activateConstraints:`, `deactivateConstraints:`, `isActive`/`setActive:`, `constant`/`setConstant:`, `priority`/`setPriority:` |
| `NSStackView` | `stackViewWithViews:`, `orientation`, `spacing`, `edgeInsets`, `alignment`, `distribution` (+ setters), `addArrangedSubview:`, `insertArrangedSubview:atIndex:`, `removeArrangedSubview:`, `arrangedSubviews`, `customSpacingAfterView:`/`setCustomSpacing:afterView:`, `visibilityPriorityForView:`/`setVisibilityPriority:forView:`, `huggingPriorityForOrientation:`/`setHuggingPriority:forOrientation:` |
| `NSGridView`, `NSGridCell`, `NSGridRow`, `NSGridColumn` | `gridViewWithNumberOfColumns:rows:`, `numberOfRows`/`numberOfColumns`, `addRowWithViews:`, `insertRowAtIndex:withViews:`, `removeRowAtIndex:`, `addColumnWithViews:`, `rowSpacing`/`columnSpacing` (+ setters), `cellAtColumnIndex:rowIndex:`, `mergeCellsInHorizontalRange:verticalRange:`, `rowAtIndex:`, `columnAtIndex:`; cell `contentView`/`setContentView:` (null = `emptyContentView`), `xPlacement`/`yPlacement` (+ setters); row `height`, `topPadding`, `bottomPadding`, `yPlacement` (+ setters); column `width`, `leadingPadding`, `trailingPadding`, `xPlacement` (+ setters) |
| `NSColor`, `NSFont`, `NSFontManager` | `colorWithRed:green:blue:alpha:`, `redComponent` … `alphaComponent` (sRGB); `systemFontOfSize:weight:`, `fontWithName:size:`, `pointSize`, `familyName` (nullable); `sharedFontManager`, `fontWithFamily:traits:weight:size:`, `weightOfFont:`; `NSFont::WEIGHT_*` = `NSFontWeight*` |
| `NSControl` | `sendAction:to:`, `isEnabled`/`setEnabled:`, `target`/`setTarget:`, `action`/`setAction:`, `stringValue`, `doubleValue`, `integerValue` (+ setters), `font`/`setFont:`, `alignment`/`setAlignment:`, `sizeToFit`, `performClick:` |
| `NSTextField`, `NSSecureTextField` | `labelWithString:`, `labelWithAttributedString:`, `attributedStringValue`, `allowsEditingTextAttributes`, `isSelectable`, `textFieldWithString:`, `placeholderString`, `isEditable`, `isBezeled`, `drawsBackground`, `textColor`, `backgroundColor`, `lineBreakMode`, `maximumNumberOfLines`, `preferredMaxLayoutWidth`, `delegate` (+ setters); secure field `initWithFrame:` |
| `NSAttributedString`, `NSWorkspace` | `initWithString:attributes:`, `string`, `length`, `attribute:atIndex:`, `NSLinkAttributeName`, `NSFontAttributeName`, `NSParagraphStyleAttributeName`; `sharedWorkspace`, `openURL:` |
| `NSParagraphStyle`, `NSMutableParagraphStyle` | `alignment`; `init`, `setAlignment:` |
| `NSButton`, `NSSwitch` | `buttonWithTitle:target:action:`, `checkboxWithTitle:target:action:`, `setButtonType:`, `title`/`setTitle:`, `state`/`setState:`, `contentTintColor`/`setContentTintColor:`; switch `initWithFrame:`, `state`/`setState:` |
| `NSSlider`, `NSPopUpButton` | `sliderWithValue:minValue:maxValue:target:action:`, `minValue`/`maxValue` (+ setters), `isContinuous`/`setContinuous:`; `initWithFrame:pullsDown:`, `addItemWithTitle:`, `addItemsWithTitles:`, `removeAllItems`, `numberOfItems`, `indexOfSelectedItem`, `selectItemAtIndex:`, `titleOfSelectedItem`, `itemTitles` |
| `NSDatePicker`, `NSTimeZone`, `NSProgressIndicator` | `initWithFrame:`, `dateValue`/`setDateValue:`, `timeZone`/`setTimeZone:` (`NSTimeZone` `timeZoneWithName:`, `name`), `setDatePickerStyle:`, `setDatePickerElements:` (`ELEMENT_*`), `setDatePickerMode:`; `setStyle:`, `minValue`/`maxValue`/`doubleValue` (+ setters), `isIndeterminate`/`setIndeterminate:`, `startAnimation:`/`stopAnimation:`, `setDisplayedWhenStopped:` |
| `NSImage`, `NSImageView`, `NSBox`, `NSScrollView`, `NSTextView` | `initWithContentsOfFile:` (null when unreadable), `initWithCGImage:size:`, `size`; `imageViewWithImage:`, `image`/`setImage:`, `imageScaling`/`setImageScaling:`; `boxType`/`setBoxType:`; `contentView` (the clip view), `documentView`/`setDocumentView:`, `hasVerticalScroller`/`hasHorizontalScroller`/`drawsBackground` (+ setters), `contentSize`; `scrollableTextView`, `string`/`setString:`, `backgroundColor`/`drawsBackground` (+ setters), `layoutManager`, `textContainer`, `textContainerInset`; `NSLayoutManager` `ensureLayoutForTextContainer:`, `usedRectForTextContainer:`; `isEditable`/`setEditable:`, `font`, `textColor`, `delegate` (+ setters) |
| `NSTableView`, `NSTableColumn`, `NSTableHeaderView`, `NSCell`, `NSIndexSet` | `addTableColumn:`/`removeTableColumn:`, `tableColumns`, `dataSource`/`delegate` (+ setters), `reloadData`, `numberOfRows`, `selectedRow`, `selectRowIndexes:byExtendingSelection:`, `deselectAll:`, `setAllowsEmptySelection:`, `setUsesAlternatingRowBackgroundColors:`, `backgroundColor`/`setBackgroundColor:`, `headerView`/`setHeaderView:`, `preparedCellAtColumn:row:`, `viewAtColumn:row:makeIfNecessary:`; `NSCell` `objectValue`; column `initWithIdentifier:`, `identifier`, `title`, `width`, `setResizingMask:` (`RESIZING_MASK_*`); `indexSetWithIndex:`, `firstIndex`, `count` |
| `NSNotificationCenter`, `NSNotification`, `NSOperationQueue` | `defaultCenter`, `addObserverForName:object:queue:usingBlock:` (PHP callable), `removeObserver:`, `postNotificationName:object:`; `name`, `object`; `mainQueue`, `init`, `waitUntilAllOperationsAreFinished`. Constants `NSViewFrameDidChangeNotification`, `NSWindowDidResizeNotification`, `AVPlayerItemDidPlayToEndTimeNotification`, `NSApplicationDidResignActiveNotification` |
| `NSURL`, `AVPlayerItem`, `AVPlayer`, `AVPlayerView` | `fileURLWithPath:`, `URLWithString:`, `path`, `absoluteString`; `playerItemWithURL:`, `status`, `duration`, `error`; `playerWithPlayerItem:`, `actionAtItemEnd`/`setActionAtItemEnd:` (`AVPlayerActionAtItemEnd`), `play`, `pause`, `rate`/`setRate:`, `currentTime`, `seekToTime:`, `isMuted`/`setMuted:`, `timeControlStatus`, `currentItem`, `replaceCurrentItemWithPlayerItem:`; `initWithFrame:`, `player`/`setPlayer:`, `controlsStyle`/`setControlsStyle:` |
| `NSMenu` | `initWithTitle:`, `title`, `setTitle:`, `addItem:`, `insertItem:atIndex:`, `removeItem:`, `removeAllItems`, `numberOfItems`, `itemAtIndex:`, `indexOfItem:`, `autoenablesItems`, `setAutoenablesItems:`, `update`, `performActionForItemAtIndex:`, `popUpMenuPositioningItem:atLocation:inView:`, `cancelTracking` |
| `NSMenuItem` | `initWithTitle:action:keyEquivalent:`, `separatorItem`, `title`/`setTitle:`, `isSeparatorItem`, `hasSubmenu`, `submenu`/`setSubmenu:`, `menu`, `target`/`setTarget:`, `action`/`setAction:`, `state`/`setState:`, `isEnabled`/`setEnabled:`, `keyEquivalent`/`setKeyEquivalent:`, `keyEquivalentModifierMask`/`setKeyEquivalentModifierMask:`, `tag`/`setTag:` |
| `NSRect`, `NSSize`, `NSPoint`, `NSEdgeInsets`, `NSRange`, `CMTime` | value classes; `CMTime` carries value, timescale, flags, epoch (`FLAG_*`), `CMTime::withSeconds()`, `seconds()` |
| `NSColorSpace`, `NSWindow` colour space | `initWithCGColorSpace:`, `sRGBColorSpace`, `displayP3ColorSpace`, `localizedName`; `NSWindow::colorSpace` / `setColorSpace:` (null = the screen's) |
| `NSOpenGLPixelFormat`, `NSOpenGLContext`, `NSOpenGLView`, `ObjCOpenGLView` | `initWithAttributes:`; `initWithFormat:shareContext:`, `makeCurrentContext`, `clearCurrentContext`, `currentContext`, `CGLContextObj`, `flushBuffer`, `update`, `view`/`setView:`; `initWithFrame:pixelFormat:`, `openGLContext`/`setOpenGLContext:`, `pixelFormat`, `wantsBestResolutionOpenGLSurface` (+set); `NSOpenGLPFAColorFloat`; on any `NSView`: `wantsBestResolutionOpenGLSurface`, `wantsExtendedDynamicRangeOpenGLSurface` (+set); trampoline: an `NSOpenGLView` whose `drawRect:` calls PHP with its context current, then flushes; context setValues:forParameter: / getValues:forParameter: (`NSOpenGLContextParameter`, ≤ 4 ints; SWAP_INTERVAL 0/1 = vsync off/on) |
| `ObjCStageWindow` | NSWindow subclass: `canBecomeKey()` / `setCanBecomeKey(bool)` answer `canBecomeKeyWindow` and `canBecomeMainWindow`, YES by default, so a borderless window takes focus; made with the inherited `initWithContentRectStyleMaskBackingDefer()` |
| `ObjCDrawView` | trampoline: static `initWithFrameDraw(NSRect, callable)`; `drawRect:` calls PHP with `(view, NSRect dirty)` inside the view's graphics context: mark rects with `setNeedsDisplayInRect:` and AppKit asks for only those (partial redraw) |
| `NSGraphicsContext`, `CGContext` | currentContext, CGContext; CGContextSaveGState / RestoreGState / ClipToRect / TranslateCTM / ScaleCTM / SetInterpolationQuality / GetInterpolationQuality (`CGInterpolationQuality`, NONE = nearest) / DrawImage |
| `NSScreen` | mainScreen, screens (menu-bar screen first), frame, visibleFrame, backingScaleFactor, maximumFramesPerSecond, localizedName, deviceDescription (array: `NSScreenNumber` = CGDirectDisplayID, `NSDeviceSize`/`NSDeviceResolution` as `NSSize`), maximumExtendedDynamicRangeColorComponentValue, maximumPotentialExtendedDynamicRangeColorComponentValue |
| `CGDisplay`, `CGDisplayMode` | static CGMainDisplayID, CGGetActiveDisplayList, CGDisplayBounds, CGDisplayCopyDisplayMode, CGDisplayCopyAllDisplayModes (options array, `kCGDisplayShowDuplicateLowResolutionModes` lists the HiDPI modes), CGDisplaySetDisplayMode, CGDisplayCapture, CGDisplayRelease, CGShieldingWindowLevel (a display named by its int id; a CGError throws `AppKitException` with the error as code); mode GetWidth/GetHeight/GetPixelWidth/GetPixelHeight/GetRefreshRate/IsUsableForDesktopGUI |
| `CADisplayLink`, `CAFrameRateRange`, `NSRunLoop` | link timestamp, targetTimestamp, duration, preferredFrameRateRange (+set), addToRunLoop:forMode:, removeFromRunLoop:forMode:, isPaused/setPaused:, invalidate (macOS 14+); range value class (minimum, maximum, preferred); mainRunLoop, currentRunLoop, getCFRunLoop |
| `NSProcessInfo`, `IOPMAssertion` | processInfo, beginActivityWithOptions:reason: (`NSActivityOptions`, returns the token), endActivity:; static IOPMAssertionCreateWithName (returns the IOPMAssertionID), IOPMAssertionRelease (an IOReturn error throws `AppKitException`) |
| `CFData`, `CGDataProvider`, `CGColorSpace`, `CGImage` | CFDataCreate (copies), CGDataProviderCreateWithCFData, CGColorSpaceCreateWithName, CGImageCreate, GetWidth, GetHeight; CGDataProviderCreateDirect (`createDirect(address, size)`: reads the memory in place, no copy, caller keeps it alive; `CGImage::create` checks a description against its size without copying, the last row needing only its pixels); CGImageCreateWithImageInRect (null when they do not meet) |
| `ObjCDelegate`, `ObjCTarget`, `ObjCObserver` | trampolines: an object answering a protocol's selectors by calling PHP (returns box PHP strings and numbers as `NSString`/`NSNumber`), a target whose `action:` calls PHP, and a KVO observer (`observe`/`stop`, `OPTION_*`) handing `(keyPath, object, change)` to PHP |
| `NSEvent` | `otherEventWithType:…data2:`, `mouseEventWithType:…pressure:`, `type`, `buttonNumber`, `subtype`, `modifierFlags`, `timestamp`, `windowNumber`, `locationInWindow`, `data1`, `data2`, `keyEventWithType:…keyCode:`, `eventWithCGEvent:`, static `mouseLocation`, static `pressedMouseButtons`, `keyCode`, `characters`/`charactersIgnoringModifiers` (key events only), `isARepeat`, `clickCount`, `deltaX`/`deltaY`, `scrollingDeltaX`/`scrollingDeltaY`, `hasPreciseScrollingDeltas`, `isDirectionInvertedFromDevice`, `window` |
| `CGEvent` | `CGEventCreateMouseEvent`, `CGEventCreateScrollWheelEvent2`, `Get`/`SetIntegerValueField`, `Get`/`SetLocation`; enums `CGEventType`, `CGMouseButton`, `CGScrollEventUnit`, constants `kCGMouseEvent*`. The NSEvents AppKit cannot construct (scroll, other buttons), via `NSEvent::eventWithCGEvent()`. `CGEventSource::keyState` (`CGEventSourceKeyState`, enum `CGEventSourceStateID`) |
| `GCController` and its profiles and elements (GameController.framework) | `controllers`, `startWirelessControllerDiscoveryWithCompletionHandler:`, `stopWirelessControllerDiscovery`, `shouldMonitorBackgroundEvents` (+set), `vendorName`, `extendedGamepad`, `microGamepad`, `playerIndex` (+set, `GCControllerPlayerIndex`); extended and micro gamepads, buttons, axes, direction pads; `GCControllerDidConnectNotification`, `GCControllerDidDisconnectNotification` |
| `NSDate` | `date`, `dateWithTimeIntervalSinceNow:`, `dateWithTimeIntervalSince1970:`, `distantPast`, `distantFuture`, `timeIntervalSinceNow`, `timeIntervalSince1970` |
| `CFRunLoop`, `CFRunLoopSource` | `CFRunLoopGetMain/GetCurrent/Run/RunInMode/Stop/WakeUp/IsWaiting/CopyCurrentMode/AddSource/RemoveSource/ContainsSource`, `CFRunLoopSourceGetOrder/Invalidate/IsValid/Signal` |
| `CFFileDescriptor` | `Create` (fd as int, stream or Socket; PHP callable callout), `GetNativeDescriptor`, `EnableCallBacks`, `DisableCallBacks`, `Invalidate`, `IsValid`, `CreateRunLoopSource` |

A `CAMetalLayer` made by ext-metal is set as a view's layer through `CALayer::fromPointer($layer->pointer())`, and comes back from `layer()` as a `CALayer`.

Enums: `NSApplicationActivationPolicy`, `NSEventType`, `NSEventMask`,
`NSEventModifierFlags`, `CFRunLoopRunResult`, `NSWindowStyleMask`,
`NSBackingStoreType`, `NSWindowCollectionBehavior`, `NSWindowTitleVisibility`, `NSWindowOcclusionState`, `NSViewLayerContentsRedrawPolicy`, `NSOpenGLContextParameter`, `CGInterpolationQuality`, `NSActivityOptions`, `NSControlStateValue`, `NSUserInterfaceLayoutOrientation`,
`NSLayoutConstraintOrientation`, `NSStackViewGravity`, `NSLayoutAttribute`,
`NSStackViewDistribution`, `NSGridCellPlacement`, `NSTextAlignment` (values from
the SDK: arm64 and x86_64 differ), `NSLineBreakMode`, `NSButtonType`,
`NSDatePickerStyle`, `NSDatePickerMode`, `NSProgressIndicatorStyle`,
`NSImageScaling`, `NSBoxType`, `AVPlayerItemStatus`, `AVPlayerTimeControlStatus`,
`AVPlayerViewControlsStyle`. Constants: run-loop modes, `kCFFileDescriptor*CallBack`,
`NSTextAlignment*`, `kCAGravity{Resize,ResizeAspect,ResizeAspectFill,Center}`, `NS{Normal,Floating,Submenu,TornOffMenu,MainMenu,Status,ModalPanel,PopUpMenu,ScreenSaver}WindowLevel`, `kCGDisplayShowDuplicateLowResolutionModes`, `kIOPMAssertionType{PreventUserIdleSystemSleep,PreventUserIdleDisplaySleep,PreventSystemSleep}`, `kIOPMAssertionLevel{Off,On}`, `NSControlTextDidChangeNotification`, `NSTextDidChangeNotification`, the notification names above. The stubs in `stubs/` are the
full declaration; every enum's values are `_Static_assert`-checked against the SDK.

Static constructors and `instancetype` factories build the class they are called
on: `NSTextField::initWithFrame()` is `[[NSTextField alloc] initWithFrame:]`.

A PHP callable handed to native code (delegate, target, observer, notification
block, file-descriptor callout) only ever runs on the PHP thread that handed it
over; a native call on any other thread does not enter PHP. Route notifications
that may be posted elsewhere (AVFoundation's) through `NSOperationQueue::mainQueue()`.

Selectors become methods by joining their parts:
`nextEventMatchingMask:untilDate:inMode:dequeue:` is
`nextEventMatchingMaskUntilDateInModeDequeue()`.

## Example

```php
$app = NSApplication::sharedApplication();
$app->finishLaunching();
$app->setActivationPolicy(NSApplicationActivationPolicy::REGULAR); // Dock icon
$app->activate();

// Sleep up to 16 ms for the next event, dispatch it.
$event = $app->nextEventMatchingMaskUntilDateInModeDequeue(
    NSEventMask::ANY, NSDate::dateWithTimeIntervalSinceNow(0.016), NSDefaultRunLoopMode, true,
);
if ($event) {
    $app->sendEvent($event);
}

$app->setActivationPolicy(NSApplicationActivationPolicy::PROHIBITED); // icon gone
```

A window with a menu item whose action runs PHP:

```php
$window = NSWindow::initWithContentRectStyleMaskBackingDefer(
    new NSRect(0, 0, 480, 320),
    NSWindowStyleMask::TITLED->value | NSWindowStyleMask::CLOSABLE->value,
    NSBackingStoreType::BUFFERED,
    false,
);
$window->setReleasedWhenClosed(false); // PHP holds the reference; AppKit must not release it on close

$delegate = new ObjCDelegate('NSWindowDelegate');
$delegate->on('windowWillClose:', fn (NSObject $notification) => print("closed\n"));
$window->setDelegate($delegate);       // AppKit holds delegates weakly: keep $delegate
$window->makeKeyAndOrderFront(null);

$target = new ObjCTarget(fn (?NSObject $sender) => print("refresh\n"));
$item = NSMenuItem::initWithTitleActionKeyEquivalent('Refresh', ObjCTarget::ACTION, 'r');
$item->setTarget($target);             // targets are weak too: keep $target
```

## Install

```bash
bash install-macos.sh                  # Homebrew php@8.4 and php@8.4-zts
bash install-macos.sh /path/to/php ... # specific PHP binaries
```

Or with PIE: `pie install php-io-extensions/appkit`.

## Test

```bash
composer install
php vendor/bin/pest
php examples/smoke.php          # bridge: Dock icon, pump, sleep, wake; prints SMOKE_OK
php examples/window-smoke.php   # window, menu bar, target/action, delegate close; prints SMOKE_OK
```

Design notes live in the OKF bundle under `.okf/`.

## License

MIT
