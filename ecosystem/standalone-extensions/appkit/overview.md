# Overview

![CI](https://github.com/php-io-extensions/appkit/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/appkit/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/appkit/actions/workflows/ci.yml)
[![AppKit API](https://img.shields.io/badge/AppKit_API-9.3%25_%28669%2F7210%29-blue?style=flat-square)](https://github.com/php-io-extensions/appkit/blob/v0.11.0/SUPPORT.md)

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
| `NSObject`, `NSResponder` | `className`, `isKindOfClass:`, `respondsToSelector:`, `isEqual:`, `hash`, `description`; `pointer()` (the address, for another extension), `fromPointer()` (the object at an address, checked against the called class); `NSResponder`: `nextResponder`, `setNextResponder:`, `acceptsFirstResponder`; `NSString` (every string object AppKit hands back): `stringWithString:`, `UTF8String` |
| `CALayer` | `layer`, `contentsScale`/`setContentsScale:`, `sublayers`, `addSublayer:`, `backgroundColor`/`setBackgroundColor:`, `contents`/`setContents:`, `contentsGravity`/`setContentsGravity:`, `masksToBounds`/`setMasksToBounds:` |
| `NSApplication` | `sharedApplication`, `finishLaunching`, `run`, `stop:`, `activationPolicy`, `setActivationPolicy:`, `activate`, `activateIgnoringOtherApps:`, `deactivate`, `isActive`, `isRunning`, `nextEventMatchingMask:untilDate:inMode:dequeue:`, `discardEventsMatchingMask:beforeEvent:`, `sendEvent:`, `postEvent:atStart:`, `currentEvent`, `updateWindows`, `delegate`, `setDelegate:`, `mainMenu`, `setMainMenu:`, `keyWindow`, `mainWindow`, `windows`, `orderFrontStandardAboutPanel:`, `orderFrontStandardAboutPanelWithOptions:`; applicationIconImage, setApplicationIconImage: (null restores the bundle icon), requestUserAttention: (`NSRequestUserAttentionType`), cancelUserAttentionRequest: |
| `NSWindow` | `initWithContentRect:styleMask:backing:defer:` (allocates the called class), `title`, `setTitle:`, `makeKeyAndOrderFront:`, `orderOut:`, `close`, `performClose:`, `beginSheet:completionHandler:`, `endSheet:`, `endSheet:returnCode:`, `sheets`, `attachedSheet`, `sheetParent`, `miniaturize:`, `isVisible`, `isKeyWindow`, `isMainWindow`, `canBecomeKeyWindow`, `canBecomeMainWindow`, `makeKeyWindow`, `delegate`, `setDelegate:`, `isReleasedWhenClosed`, `setReleasedWhenClosed:`, `center`, `contentView`/`setContentView:`, `windowNumber`, `frame`, `setContentSize:`, `styleMask`, `backingScaleFactor`; window modes: setStyleMask:, contentMin/MaxSize (+set), contentAspectRatio (+set), setFrameOrigin:, setFrame:display:, contentRectForFrameRect:, frameRectForContentRect:, convertRectToBacking:, orderFront:, zoom:, isZoomed, deminiaturize:, isMiniaturized, toggleFullScreen:, collectionBehavior (+set, `NSWindowCollectionBehavior`), level (+set, `NS*WindowLevel` or `CGDisplay::shieldingWindowLevel()`), screen, isOpaque/setOpaque:, backgroundColor (+set, null = default), hasShadow (+set), titlebarAppearsTransparent (+set), titleVisibility (+set), ignoresMouseEvents (+set), isMovableByWindowBackground (+set), occlusionState (`NSWindowOcclusionState` bits), alphaValue (+set), `acceptsMouseMovedEvents` (+set), static `windowNumberAtPoint:belowWindowWithWindowNumber:`, `makeFirstResponder:`, `firstResponder`, `initialFirstResponder`/`setInitialFirstResponder:`, `selectNextKeyView:`, `selectPreviousKeyView:`, `setAutorecalculatesKeyViewLoop:` |
| `NSView` | `initWithFrame:` (allocates the class it is called on), `frame`/`setFrame:`, `window`, `menu`, `superview`, `subviews`, `addSubview:`, `removeFromSuperview`, `isHidden`/`setHidden:`, `isHiddenOrHasHiddenAncestor`, `contentHuggingPriorityForOrientation:`/`setContentHuggingPriority:forOrientation:`, `contentCompressionResistancePriorityForOrientation:`/`setContentCompressionResistancePriority:forOrientation:`, `fittingSize`, `intrinsicContentSize`, `layoutSubtreeIfNeeded`, `visibleRect`, `scrollPoint:`, `translatesAutoresizingMaskIntoConstraints`/`set…:`, `wantsLayer`/`setWantsLayer:`, `layer`/`setLayer:`, `postsFrameChangedNotifications`/`set…:`, `postsBoundsChangedNotifications`/`set…:`, `widthAnchor` … `centerYAnchor`; bounds, convertRectToBacking:, convertSizeToBacking:, setNeedsDisplayInRect: (partial redraw), displayIfNeeded, layerContentsRedrawPolicy (+set), displayLinkWithTarget:selector: (macOS 14+, a `CADisplayLink` not yet on a run loop), safeAreaRect (macOS 11), hitTest:, convertPoint:fromView:, isFlipped, nextKeyView (+set) |
| `NSLayoutAnchor`, `NSLayoutDimension`, `NSLayoutXAxisAnchor`, `NSLayoutYAxisAnchor`, `NSLayoutConstraint` | `constraintEqualToAnchor:`, `constraintEqualToAnchor:constant:`, `constraintGreaterThanOrEqualToAnchor:` / `constraintLessThanOrEqualToAnchor:` (± `constant:`); on `NSLayoutDimension`: `constraintEqualToConstant:`, `constraintGreaterThanOrEqualToConstant:`, `constraintLessThanOrEqualToConstant:`; `activateConstraints:`, `deactivateConstraints:`, `isActive`/`setActive:`, `constant`/`setConstant:`, `priority`/`setPriority:` |
| `NSStackView` | `stackViewWithViews:`, `orientation`, `spacing`, `edgeInsets`, `alignment`, `distribution` (+ setters), `addArrangedSubview:`, `insertArrangedSubview:atIndex:`, `removeArrangedSubview:`, `arrangedSubviews`, `customSpacingAfterView:`/`setCustomSpacing:afterView:`, `visibilityPriorityForView:`/`setVisibilityPriority:forView:`, `huggingPriorityForOrientation:`/`setHuggingPriority:forOrientation:` |
| `NSGridView`, `NSGridCell`, `NSGridRow`, `NSGridColumn` | `gridViewWithNumberOfColumns:rows:`, `numberOfRows`/`numberOfColumns`, `addRowWithViews:`, `insertRowAtIndex:withViews:`, `removeRowAtIndex:`, `addColumnWithViews:`, `rowSpacing`/`columnSpacing` (+ setters), `cellAtColumnIndex:rowIndex:`, `mergeCellsInHorizontalRange:verticalRange:`, `rowAtIndex:`, `columnAtIndex:`; cell `emptyContentView`, `contentView`/`setContentView:`, `xPlacement`/`yPlacement` (+ setters); row `height`, `topPadding`, `bottomPadding`, `yPlacement` (+ setters); column `width`, `leadingPadding`, `trailingPadding`, `xPlacement` (+ setters) |
| `NSColor`, `NSFont`, `NSFontManager` | `colorWithRed:green:blue:alpha:`, `redComponent` … `alphaComponent` (of the colour as it is), `CGColor`, `colorWithCGColor:`, `colorUsingColorSpace:`, `NSColorSpace`; `systemFontOfSize:weight:`, `monospacedSystemFontOfSize:weight:`, `fontWithName:size:`, `pointSize`, `familyName` (nullable); `sharedFontManager`, `fontWithFamily:traits:weight:size:`, `weightOfFont:`; `NSFont::WEIGHT_*` = `NSFontWeight*` |
| `NSControl` | `sendAction:to:`, `isEnabled`/`setEnabled:`, `target`/`setTarget:`, `action`/`setAction:`, `stringValue`, `doubleValue`, `integerValue` (+ setters), `font`/`setFont:`, `alignment`/`setAlignment:`, `sizeToFit`, `performClick:` |
| `NSTextField`, `NSSecureTextField` | `labelWithString:`, `labelWithAttributedString:`, `attributedStringValue`, `allowsEditingTextAttributes`, `isSelectable`, `textFieldWithString:`, `placeholderString`, `isEditable`, `isBezeled`, `drawsBackground`, `textColor`, `backgroundColor`, `lineBreakMode`, `maximumNumberOfLines`, `preferredMaxLayoutWidth`, `delegate` (+ setters); secure field `initWithFrame:` |
| `NSAttributedString`, `NSMutableAttributedString`, `NSTextStorage`, `NSWorkspace` | `initWithString:attributes:`, `string`, `length`, `attribute:atIndex:effectiveRange:` (value and run), `NSLinkAttributeName`, `NSFontAttributeName`, `NSParagraphStyleAttributeName`, `NSForegroundColorAttributeName`, `NSBackgroundColorAttributeName`; `addAttribute:value:range:`, `removeAttribute:range:` (a range past the string raises AppKitException `NSRangeException`; a foreground or background colour that is no NSColor is a TypeError), `setAttributedString:`, `beginEditing`, `endEditing`; `sharedWorkspace`, `openURL:` |
| `NSParagraphStyle`, `NSMutableParagraphStyle`, `NSTextBlock` | `alignment`, `textBlocks`; `init`, `setAlignment:`, `setTextBlocks:`; `NSTextBlock`: `init`, `backgroundColor`/`setBackgroundColor:`, `setValue:type:forDimension:`, `valueForDimension:`, `valueTypeForDimension:` |
| `NSButton`, `NSSwitch` | `buttonWithTitle:target:action:`, `checkboxWithTitle:target:action:`, `setButtonType:`, `title`/`setTitle:`, `state`/`setState:`, `contentTintColor`/`setContentTintColor:`, `keyEquivalent`/`setKeyEquivalent:`; switch `initWithFrame:`, `state`/`setState:` |
| `NSSlider`, `NSPopUpButton` | `sliderWithValue:minValue:maxValue:target:action:`, `minValue`/`maxValue` (+ setters), `isContinuous`/`setContinuous:`; `initWithFrame:pullsDown:`, `addItemWithTitle:`, `addItemsWithTitles:`, `removeAllItems`, `numberOfItems`, `indexOfSelectedItem`, `selectItemAtIndex:`, `titleOfSelectedItem`, `itemTitles`; an `NSPopUpButton` is an `NSButton` (`setBordered:` draws a flat pull-down) |
| `NSComboBox`, `NSScroller` | `addItemWithObjectValue:` (a string), `removeAllItems`, `numberOfItems`, `indexOfSelectedItem`, `selectItemAtIndex:`, `deselectItemAtIndex:`, `setNumberOfVisibleItems:`; `+scrollerWidthForControlSize:scrollerStyle:`, `+preferredScrollerStyle`, `scrollerStyle` (+ set), `knobProportion` (+ set), `hitPart`, `rectForPart:` (scroller coordinates), `testPart:` (window coordinates), `NSPreferredScrollerStyleDidChangeNotification` |
| `NSButton` images, `NSTrackingArea` | `image`/`setImage:`, `imagePosition`/`setImagePosition:` (`NSCellImagePosition`), `isBordered`/`setBordered:`; `NSMenuItem` `image`/`setImage:`; `NSControl` `refusesFirstResponder` (+ set); `initWithRect:options:owner:userInfo:`, `rect`, `options`, `owner`; `NSView` `addTrackingArea:`, `removeTrackingArea:`, `convertRect:toView:`; `NSEvent` `phase`, `momentumPhase`, `trackingArea`; `NSWindow` `addChildWindow:ordered:`, `removeChildWindow:`, `convertRectToScreen:`; `NSTabView` `insertTabViewItem:atIndex:` |
| `NSDatePicker`, `NSTimeZone`, `NSProgressIndicator` | `initWithFrame:`, `dateValue`/`setDateValue:`, `timeZone`/`setTimeZone:` (`NSTimeZone` `timeZoneWithName:`, `name`), `setDatePickerStyle:`, `setDatePickerElements:` (`ELEMENT_*`), `setDatePickerMode:`; `setStyle:`, `minValue`/`maxValue`/`doubleValue` (+ setters), `isIndeterminate`/`setIndeterminate:`, `startAnimation:`/`stopAnimation:`, `setDisplayedWhenStopped:` |
| `NSAlert`, `NSPanel`, `NSSavePanel`, `NSOpenPanel`, `UTType` | `init` (allocates the called class), `messageText`/`setMessageText:`, `informativeText`/`setInformativeText:`, `alertStyle`/`setAlertStyle:` (`NSAlertStyle`), `showsSuppressionButton` (+ set), `suppressionButton`, `addButtonWithTitle:`, `buttons`, `beginSheetModalForWindow:completionHandler:` (a `^(NSModalResponse)` block to the closure; the button at index i returns `NSAlertFirstButtonReturn` + i), `window`; `savePanel`, `URL`, `directoryURL`/`setDirectoryURL:`, `nameFieldStringValue`/`setNameFieldStringValue:`, `message`/`setMessage:`, `allowedContentTypes` (+ set, a list of `UTType`; entries of another type are skipped), `showsHiddenFiles` (+ set), `beginSheetModalForWindow:completionHandler:`; `openPanel`, `URLs`, `canChooseFiles`, `canChooseDirectories`, `allowsMultipleSelection` (each + set); `UTType` `typeWithFilenameExtension:`, `identifier` (any thread) |
| `NSPasteboard` | `generalPasteboard`, `clearContents` (the new change count), `setString:forType:`, `stringForType:`, `availableTypeFromArray:`, `changeCount`; any thread |
| `NSSplitView`, `NSTabView`, `NSTabViewItem` | `isVertical`/`setVertical:`, `dividerStyle`/`setDividerStyle:`, `dividerThickness`, `arrangesAllSubviews` (+ set), `addArrangedSubview:`, `insertArrangedSubview:atIndex:`, `removeArrangedSubview:`, `arrangedSubviews`, `setPosition:ofDividerAtIndex:`, `adjustSubviews`, `isSubviewCollapsed:`, `holdingPriorityForSubviewAtIndex:` (+ set); `addTabViewItem:`, `removeTabViewItem:`, `tabViewItems`, `numberOfTabViewItems`, `indexOfTabViewItemWithIdentifier:` (-1 when none), `selectTabViewItemWithIdentifier:`, `selectedTabViewItem`, `delegate` (+ set); `initWithIdentifier:` (an NSString), `identifier`, `label`/`setLabel:`, `view`/`setView:`, `tabView`. AppKit's own behaviour throughout: an insert past the end and an unknown identifier raise (`AppKitException`), a divider index out of range and a foreign item do nothing |
| `NSImage`, `NSImageView`, `NSBox`, `NSScrollView`, `NSClipView`, `NSTextView` | `initWithContentsOfFile:` (null when unreadable), `initWithCGImage:size:`, `size`; `imageViewWithImage:`, `image`/`setImage:`, `imageScaling`/`setImageScaling:`; `boxType`/`setBoxType:`; `contentView` (the clip view), `documentView`/`setDocumentView:`, `hasVerticalScroller`/`hasHorizontalScroller`/`drawsBackground` (+ setters), `contentSize`, `reflectScrolledClipView:`, `documentVisibleRect`; `NSClipView` `scrollToPoint:`; `scrollableTextView`, `string`/`setString:`, `backgroundColor`/`drawsBackground` (+ setters), `layoutManager`, `textContainer`, `textContainerInset`, `textStorage`, `selectedRange`/`setSelectedRange:`, `scrollRangeToVisible:`, `isHorizontallyResizable`/`setHorizontallyResizable:`, `maxSize`/`setMaxSize:`; `NSTextContainer` `widthTracksTextView`, `size` (+ setters); `NSLayoutManager` `ensureLayoutForTextContainer:`, `usedRectForTextContainer:`, `glyphRangeForCharacterRange:actualCharacterRange:` (both ranges), `boundingRectForGlyphRange:inTextContainer:`, `allowsNonContiguousLayout` (+ set); `isEditable`/`setEditable:`, `font`, `textColor`, `delegate` (+ setters) |
| `NSTableView`, `NSTableColumn`, `NSTableHeaderView`, `NSCell`, `NSIndexSet` | `addTableColumn:`/`removeTableColumn:`, `tableColumns`, `dataSource`/`delegate` (+ setters), `reloadData`, `numberOfRows`, `selectedRow`, `selectRowIndexes:byExtendingSelection:`, `deselectAll:`, `setAllowsEmptySelection:`, `setUsesAlternatingRowBackgroundColors:`, `backgroundColor`/`setBackgroundColor:`, `headerView`/`setHeaderView:`, `preparedCellAtColumn:row:`, `viewAtColumn:row:makeIfNecessary:`, `doubleAction`/`setDoubleAction:`, `clickedRow`, `scrollRowToVisible:`; `NSOutlineView` `outlineTableColumn` (+ setter), `expandItem:`, `collapseItem:`, `isItemExpanded:`, `itemAtRow:`, `rowForItem:`, `reloadItem:reloadChildren:`, `indentationPerLevel` (+ setter); `NSCell` `objectValue`; column `initWithIdentifier:`, `identifier`, `title`, `width`, `setResizingMask:` (`RESIZING_MASK_*`); `indexSetWithIndex:`, `firstIndex`, `count` |
| `NSNotificationCenter`, `NSNotification`, `NSOperationQueue` | `defaultCenter`, `addObserverForName:object:queue:usingBlock:` (PHP callable), `removeObserver:`, `postNotificationName:object:`; `name`, `object`, `userInfo`; `mainQueue`, `init`, `waitUntilAllOperationsAreFinished`. Constants `NSViewFrameDidChangeNotification`, `NSViewBoundsDidChangeNotification`, `NSWindowDidResizeNotification`, `AVPlayerItemDidPlayToEndTimeNotification`, `NSApplicationDidResignActiveNotification` |
| `NSURL`, `AVPlayerItem`, `AVPlayer`, `AVPlayerView` | `fileURLWithPath:`, `URLWithString:`, `path`, `absoluteString`; `playerItemWithURL:`, `status`, `duration`, `error`; `playerWithPlayerItem:`, `actionAtItemEnd`/`setActionAtItemEnd:` (`AVPlayerActionAtItemEnd`), `play`, `pause`, `rate`/`setRate:`, `currentTime`, `seekToTime:`, `isMuted`/`setMuted:`, `timeControlStatus`, `currentItem`, `replaceCurrentItemWithPlayerItem:`; `initWithFrame:`, `player`/`setPlayer:`, `controlsStyle`/`setControlsStyle:` |
| `NSMenu` | `initWithTitle:`, `title`, `setTitle:`, `addItem:`, `insertItem:atIndex:`, `removeItem:`, `removeAllItems`, `numberOfItems`, `itemAtIndex:`, `indexOfItem:`, `autoenablesItems`, `setAutoenablesItems:`, `update`, `performActionForItemAtIndex:`, `performKeyEquivalent:`, `popUpMenuPositioningItem:atLocation:inView:`, `cancelTracking` |
| `NSMenuItem` | `initWithTitle:action:keyEquivalent:`, `separatorItem`, `title`/`setTitle:`, `isSeparatorItem`, `hasSubmenu`, `submenu`/`setSubmenu:`, `menu`, `target`/`setTarget:`, `action`/`setAction:`, `state`/`setState:`, `isEnabled`/`setEnabled:`, `keyEquivalent`/`setKeyEquivalent:`, `keyEquivalentModifierMask`/`setKeyEquivalentModifierMask:`, `tag`/`setTag:` |
| `NSRect`, `NSSize`, `NSPoint`, `NSEdgeInsets`, `NSRange`, `CMTime` | value classes; `CMTime` carries value, timescale, flags, epoch (`FLAG_*`), `CMTime::make()`, `CMTime::makeWithSeconds()`, `getSeconds()`; every field is a required constructor argument |
| `NSColorSpace`, `NSWindow` colour space | `initWithCGColorSpace:`, `sRGBColorSpace`, `displayP3ColorSpace`, `localizedName`; `NSWindow::colorSpace` / `setColorSpace:` (null = the screen's) |
| `NSOpenGLPixelFormat`, `NSOpenGLContext`, `NSOpenGLView`, `ObjCOpenGLView` | `initWithAttributes:` (a list ending on an attribute that takes a value, with none after it, is a `ValueError`: AppKit would read past it); `initWithFormat:shareContext:`, `makeCurrentContext`, `clearCurrentContext`, `currentContext`, `CGLContextObj`, `flushBuffer`, `update`, `view`/`setView:`; `initWithFrame:pixelFormat:`, `openGLContext`/`setOpenGLContext:`, `pixelFormat`, `wantsBestResolutionOpenGLSurface` (+set); `NSOpenGLPFAColorFloat`; on any `NSView`: `wantsBestResolutionOpenGLSurface`, `wantsExtendedDynamicRangeOpenGLSurface` (+set); trampoline: an `NSOpenGLView` whose `drawRect:` calls PHP with the view and the dirty rect (the handler makes the context current and flushes); context setValues:forParameter: / getValues:forParameter: (`NSOpenGLContextParameter`, ≤ 4 ints; SWAP_INTERVAL 0/1 = vsync off/on) |
| `ObjCStageWindow` | NSWindow subclass: `on('canBecomeKeyWindow' \| 'canBecomeMainWindow', callable)` / `off()` set the PHP handler each override asks; without one it answers NSWindow's own (NO for a borderless window); made with the inherited `initWithContentRectStyleMaskBackingDefer()` |
| `ObjCFocusView` | NSView subclass conforming to `NSTextInputClient`: `on(selector, callable)` / `off()` set the PHP handler an override asks: `acceptsFirstResponder` (no handler = NSView's own, NO); `keyDown:`, `keyUp:`, `flagsChanged:` with the `NSEvent`; `insertText:replacementRange:` with the text; `doCommandBySelector:` with the selector's name; for those five, false or no handler = NSView's own; `cut:`, `copy:`, `paste:`, `selectAll:`, `undo:`, `redo:` with the sender, false or no handler = the next responder, and `respondsToSelector:` answers each only while its handler is set. The marked text of a dead key stays in the glue; PHP sees only what `interpretKeyEvents()` commits. Made with the inherited `initWithFrame()` |
| `ObjCKeyWindow` | NSWindow subclass: `on('keyDown:', callable)` / `off()`; `keyDown:` hands PHP the `NSEvent`, and passes it on to NSWindow's own `keyDown:` (Tab walks the key-view loop) when no handler ran or it returned false; made with the inherited `initWithContentRectStyleMaskBackingDefer()` |
| `ObjCDrawView` | trampoline: static `initWithFrameDraw(NSRect, callable)`; `drawRect:` calls PHP with `(view, NSRect dirty)` inside the view's graphics context: mark rects with `setNeedsDisplayInRect:` and AppKit asks for only those (partial redraw) |
| `NSGraphicsContext`, `CGContext` | currentContext, CGContext; CGContextSaveGState / RestoreGState / ClipToRect / TranslateCTM / ScaleCTM / SetInterpolationQuality / GetInterpolationQuality (`CGInterpolationQuality`, NONE = nearest) / DrawImage |
| `NSScreen` | mainScreen, screens (menu-bar screen first), frame, visibleFrame, backingScaleFactor, maximumFramesPerSecond, localizedName, deviceDescription (array: `NSScreenNumber` = CGDirectDisplayID, `NSDeviceSize`/`NSDeviceResolution` as `NSSize`), maximumExtendedDynamicRangeColorComponentValue, maximumPotentialExtendedDynamicRangeColorComponentValue |
| `CGDisplay`, `CGDisplayMode` | static CGMainDisplayID, CGGetActiveDisplayList (`$activeDisplays` and `$displayCount` by reference), CGDisplayBounds, CGDisplayCopyDisplayMode, CGDisplayCopyAllDisplayModes (options array, `kCGDisplayShowDuplicateLowResolutionModes` lists the HiDPI modes), CGDisplaySetDisplayMode (mode and options nullable), CGDisplayCapture, CGDisplayRelease, CGShieldingWindowLevel (a display named by its int id; the CGError functions return the CGError, compared with `kCGError*`); mode GetWidth/GetHeight/GetPixelWidth/GetPixelHeight/GetRefreshRate/IsUsableForDesktopGUI |
| `CADisplayLink`, `CAFrameRateRange`, `NSRunLoop` | link timestamp, targetTimestamp, duration, preferredFrameRateRange (+set), addToRunLoop:forMode:, removeFromRunLoop:forMode:, isPaused/setPaused:, invalidate (macOS 14+); range value class (minimum, maximum, preferred); mainRunLoop, currentRunLoop, getCFRunLoop |
| `NSProcessInfo`, `IOPMAssertion` | processInfo, beginActivityWithOptions:reason: (`NSActivityOptions`, returns the token), endActivity:; static IOPMAssertionCreateWithName (returns the IOReturn, the IOPMAssertionID by reference), IOPMAssertionRelease (returns the IOReturn); compare with `kIOReturnSuccess` |
| `CFData`, `CGDataProvider`, `CGColorSpace`, `CGColor`, `CGImage` | CFDataCreate (allocator or null, a string or an address, the byte count; copies; a count past the string or a null address with a count above 0 is a `ValueError`: Core Foundation would read past it), CGDataProviderCreateWithCFData, CGColorSpaceCreateWithName, `CGColor` (a CGColorRef, from `NSColor::CGColor()` and `CALayer::backgroundColor()`); CGImageCreate (nullable space and provider, an optional decode list of two floats per colour component, fewer is a `ValueError`), GetWidth, GetHeight; CGDataProviderCreateDirect (`createDirect(address, size)`: reads the memory in place, no copy, caller keeps it alive; null for a size below 1); `CGImage::create` answers null for any description Core Graphics refuses, a provider shorter than it included (the last row needs only its pixels); CGImageCreateWithImageInRect (null when they do not meet) |
| `ObjCDelegate`, `ObjCTarget`, `ObjCObserver` | trampolines: an object answering a protocol's selectors by calling PHP (struct arguments as their value classes, a `char` as int; returns written back by the selector's type: objects, numbers, NSRect/NSSize/NSPoint/NSRange/NSEdgeInsets, a selector or class name, an address), a target whose `action:` calls PHP, and a KVO observer (`observe`/`stop` with options, `OPTION_*`, and context) handing `(keyPath, object, change, context)` to PHP with KVO's whole change dictionary |
| `NSEvent` | `otherEventWithType:…data2:`, `mouseEventWithType:…pressure:`, `type`, `buttonNumber`, `subtype`, `modifierFlags`, `timestamp`, `windowNumber`, `locationInWindow`, `data1`, `data2`, `keyEventWithType:…keyCode:`, `eventWithCGEvent:`, static `mouseLocation`, static `pressedMouseButtons`, static `addLocalMonitorForEventsMatchingMask:handler:` (AppKit gets the NSEvent the handler returns, nil for `null`; any other return hands AppKit its own event) / `removeMonitor:` (a second removal of one monitor, which crashes AppKit, is a `ValueError`), `keyCode`, `characters`/`charactersIgnoringModifiers` (key events only), `isARepeat`, `clickCount`, `deltaX`/`deltaY`, `scrollingDeltaX`/`scrollingDeltaY`, `hasPreciseScrollingDeltas`, `isDirectionInvertedFromDevice`, `window` |
| `CGEvent`, `CGEventSource` | `CGEventCreateMouseEvent`, `CGEventCreateScrollWheelEvent2`, `CGEventCreateKeyboardEvent` (each takes a `?CGEventSource` first), `Get`/`SetFlags`, `Get`/`SetIntegerValueField`, `Get`/`SetLocation`; enums `CGEventType`, `CGMouseButton`, `CGScrollEventUnit`, constants `kCGMouseEvent*`. The NSEvents AppKit cannot construct (scroll, other buttons), via `NSEvent::eventWithCGEvent()`. `CGEventSource::create` (`CGEventSourceCreate`), `CGEventSource::keyState` (`CGEventSourceKeyState`, enum `CGEventSourceStateID`) |
| `GCController` and its profiles and elements (GameController.framework) | `controllers`, `startWirelessControllerDiscoveryWithCompletionHandler:`, `stopWirelessControllerDiscovery`, `shouldMonitorBackgroundEvents` (+set), `vendorName`, `extendedGamepad`, `microGamepad`, `playerIndex` (+set, `GCControllerPlayerIndex`); extended and micro gamepads, buttons, axes, direction pads; `GCControllerDidConnectNotification`, `GCControllerDidDisconnectNotification` |
| `NSDate` | `date`, `dateWithTimeIntervalSinceNow:`, `dateWithTimeIntervalSince1970:`, `distantPast`, `distantFuture`, `timeIntervalSinceNow`, `timeIntervalSince1970` |
| `CFRunLoop`, `CFRunLoopSource` | `CFRunLoopGetMain/GetCurrent/Run/RunInMode/Stop/WakeUp/IsWaiting/CopyCurrentMode/AddSource/RemoveSource/ContainsSource`, `CFRunLoopSourceGetOrder/Invalidate/IsValid/Signal` |
| `CFFileDescriptor` | `Create` (allocator or null, fd as int, PHP callable callout), `GetNativeDescriptor`, `EnableCallBacks`, `DisableCallBacks`, `Invalidate`, `IsValid`, `CreateRunLoopSource` (allocator or null, order) |
| `CFType`, `CFAllocator` | `CFGetTypeID`, `CFHash`, `CFCopyDescription` (`copyDescription()`), `pointer()`; `CFAllocatorGetDefault` (every allocator parameter takes it or null) |
| `NSError` | `domain`, `code`, `localizedDescription`, `userInfo` |
| `AppKitException` | extends `RuntimeException`: an NSException AppKit raised during the call, as `"<name>: <reason>"`, and the main-thread refusal |

A `CAMetalLayer` made by ext-metal is set as a view's layer through `CALayer::fromPointer($layer->pointer())`, and comes back from `layer()` as a `CALayer`.

Enums: `NSApplicationActivationPolicy`, `NSEventType`, `NSEventMask`,
`NSEventModifierFlags`, `CFRunLoopRunResult`, `NSWindowStyleMask`,
`NSBackingStoreType`, `NSWindowCollectionBehavior`, `NSWindowTitleVisibility`, `NSWindowOcclusionState`, `NSViewLayerContentsRedrawPolicy`, `NSOpenGLContextParameter`, `CGInterpolationQuality`, `NSActivityOptions`, `NSControlStateValue`, `NSUserInterfaceLayoutOrientation`,
`NSLayoutConstraintOrientation`, `NSStackViewGravity`, `NSLayoutAttribute`,
`NSStackViewDistribution`, `NSGridCellPlacement`, `NSTextAlignment` (values from
the SDK: arm64 and x86_64 differ), `NSLineBreakMode`, `NSButtonType`,
`NSDatePickerStyle`, `NSDatePickerMode`, `NSProgressIndicatorStyle`,
`NSImageScaling`, `NSBoxType`, `NSTextBlockValueType`, `NSTextBlockDimension`, `NSSplitViewDividerStyle`, `NSCellImagePosition`, `NSControlSize`, `NSScrollerStyle`, `NSScrollerPart`, `NSEventPhase`, `NSTrackingAreaOptions`, `NSWindowOrderingMode`, `NSAlertStyle`, `AVPlayerItemStatus`, `AVPlayerTimeControlStatus`,
`AVPlayerViewControlsStyle`. Constants: run-loop modes, `kCFFileDescriptor*CallBack`,
`NSTextAlignment*`, `NSCarriageReturnCharacter`, `NSEnterCharacter`, `NSBackspaceCharacter`, `NSTabCharacter`, `NS{Up,Down,Left,Right}ArrowFunctionKey`, `NSF1FunctionKey` … `NSF12FunctionKey`, `NS{Delete,Home,End,PageUp,PageDown}FunctionKey`, `NSForegroundColorAttributeName`, `NSBackgroundColorAttributeName`, `NSViewBoundsDidChangeNotification`, `NSSplitViewDidResizeSubviewsNotification`, `kCAGravity*`, `kCGImageAlpha*`, `kCGBitmapByteOrder*`, `kCGRenderingIntentDefault`, `kCGColorSpaceSRGB`, `kCGError*`, `kIOReturnSuccess`, `NS{Normal,Floating,Submenu,TornOffMenu,MainMenu,Status,ModalPanel,PopUpMenu,ScreenSaver}WindowLevel`, `kCGDisplayShowDuplicateLowResolutionModes`, `kIOPMAssertionType{PreventUserIdleSystemSleep,PreventUserIdleDisplaySleep,PreventSystemSleep}`, `kIOPMAssertionLevel{Off,On}`, `NSControlTextDidChangeNotification`, `NSTextDidChangeNotification`, `NSAlertFirstButtonReturn`, `NSModalResponseOK`, `NSModalResponseCancel`, `NSPasteboardTypeString`, the notification names above. The stubs in `stubs/` are the
full declaration; every enum's values are `_Static_assert`-checked against the SDK.

Static constructors and `instancetype` factories build the class they are called
on: `NSTextField::initWithFrame()` is `[[NSTextField alloc] initWithFrame:]`.

A PHP callable handed to native code (delegate, target, observer, notification
block, file-descriptor callout) only ever runs on the PHP thread that handed it
over; a native call on any other thread does not enter PHP. Route notifications
that may be posted elsewhere (AVFoundation's) through `NSOperationQueue::mainQueue()`.

The AppKit UI classes (NSApplication, NSWindow, NSView and its subclasses, NSMenu,
NSMenuItem, NSScreen, the NSEvent monitors, the layout anchors, CADisplayLink) throw
`AppKitException` when called off the main thread: AppKit traps the process there.
Every other class runs on whichever thread calls it.

Results are AppKit's own: nil is `null`, CGError and IOReturn codes are returned
as `int` (compare with `kCGErrorSuccess` / `kIOReturnSuccess`), C out-parameters
are by-reference arguments, and an NSException AppKit raises arrives as
`AppKitException`. The extension declines a call only where a probe shows the call
would crash the process or use memory it does not own: the main-thread gate
above, the `CFData` byte-count and null-address checks, a `CGImage` decode list
too short for its colour space, a pixel-format attribute missing its value, a
colour attribute that is no `NSColor`, a second glue constructor call, and a
second `removeMonitor:`.

Selectors become methods by joining their parts:
`nextEventMatchingMask:untilDate:inMode:dequeue:` is
`nextEventMatchingMaskUntilDateInModeDequeue()`.

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/appkit/blob/v0.11.0/SUPPORT.md) lists every method and property accessor that the SDK's AppKit headers
declare and do not mark deprecated or unavailable on macOS, each marked bound or not; the API badge
is computed from it. Regenerate both after a binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

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
php vendor/bin/pest             # tests/Probes skip: they need a build configured with --enable-appkit-probes
php examples/smoke.php          # bridge: Dock icon, pump, sleep, wake; prints SMOKE_OK
php examples/window-smoke.php   # window, menu bar, target/action, delegate close; prints SMOKE_OK
```

Each kept refusal has a probe in `tests/Probes` that shows the crash it prevents.
They run against a probe build, configured with `--enable-appkit-probes` in a
scratch copy and never installed; in that build `APPKIT_PROBE_OFF=<site id>` turns
one site's check off:

```bash
P=$(mktemp -d)/appkit && rsync -a --exclude vendor --exclude .git ./ "$P"/
(cd "$P" && phpize && ./configure --enable-appkit --enable-appkit-probes && make)
APPKIT_PROBE_EXT="$P/modules/appkit.so" php -n -d memory_limit=128M \
    -d extension="$P/modules/appkit.so" vendor/bin/pest tests/Probes
```

The main-thread probe needs a ZTS PHP with ext-parallel.

Design notes live in the OKF bundle under `.okf/`.

## License

MIT
