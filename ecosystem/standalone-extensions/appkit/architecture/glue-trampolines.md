# Glue trampolines

ObjCDelegate, ObjCTarget and the drawRect: trampolines (ObjCOpenGLView, ObjCDrawView), the objects that let a PHP callable stand where AppKit wants a delegate, a target or a painter.

## Overview

AppKit asks objects, not functions: a window's delegate answers `windowWillClose:`, a menu item's target answers its action. Two runtime classes stand in for PHP.[^glue]

`ObjCDelegate` wraps `PHPAppKitDelegate` (NSObject subclass):

* `conformsToProtocol:` YES for the protocol named at construction; `respondsToSelector:` YES only for selectors with a handler, so AppKit's optional-method checks see exactly what PHP registered.
* `methodSignatureForSelector:` reads the signature from the protocol (`protocol_getMethodDescription`, optional then required); `forwardInvocation:` converts each argument by its type encoding (objects boxed, BOOL as bool, integers, floats, `SEL` and `Class` as names, `CGRect`/`CGSize`/`CGPoint` as value classes, pointers as addresses), calls the handler, and writes its return into the invocation by the return type (BOOL, integers, floats, objects).
* `on()` refuses a selector the protocol does not declare (ValueError), so a forwarded call always has a signature.

`ObjCTarget` wraps `PHPAppKitTarget`: `action:` calls the handler with the sender boxed. Set the item's action to `ObjCTarget::ACTION`.

Handlers are [callouts](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/callouts) without a detach: each Objective-C object holds its records and releases them in `dealloc`; at request end the callables are freed and the records go inert. AppKit holds delegates and targets weakly, so the PHP object must stay referenced for as long as the window or item should call back.

[^glue]: PHPAppKitDelegate, PHPAppKitTarget

## ObjCStageWindow
NSWindow subclass `PHPStageWindow`; `canBecomeKeyWindow` / `canBecomeMainWindow` answer one flag (`setCanBecomeKey`, YES by default). A borderless window takes focus; any window can refuse it. Made through the inherited `initWithContentRectStyleMaskBackingDefer()`: `appkit_called_class` maps a glue class to its runtime class through the class map when no ObjC class carries the PHP name.

## ObjCDrawView

NSView subclass `PHPDrawView`; `drawRect:` boxes `(view, dirty NSRect)` → PHP callout, inside the view's graphics context (`NSGraphicsContext::currentContext()->CGContext()`). Partial redraw: `setNeedsDisplayInRect:` per damaged rect, AppKit asks once per dirty region; with `NSViewLayerContentsRedrawPolicy::ON_SET_NEEDS_DISPLAY` the layer keeps the rest. Callout lifetime = view's (released in `dealloc`), like `ObjCOpenGLView`.
