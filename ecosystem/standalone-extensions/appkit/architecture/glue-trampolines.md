# Glue trampolines

The native code beyond 1:1 calls: subclasses and callbacks PHP cannot write (ObjCDelegate, ObjCTarget, ObjCObserver, ObjCDrawView, ObjCOpenGLView, ObjCStageWindow, blocks, CF callbacks), value marshalling and the pointer hand-off. Each forwards and adds nothing.

## Overview

AppKit asks objects and blocks, not functions: a window's delegate answers `windowWillClose:`, a menu item's target answers its action, a monitor takes a block. PHP cannot subclass an ObjC class or make a block, so glue stands in.[^glue]

Rule: glue forwards the native arguments it receives to PHP and returns PHP's result to the native caller. Nothing else: no flag combining, no context dropping, no make-current/flush, no result coercion, no request-end policy. A return PHP gives that has no native form leaves the native default (zeroed struct slot, nil object, AppKit's own event). Glue list = `bindings.json` `glue`; only the maintainer edits it.[^bindings]

| Glue | Forwards |
|---|---|
| `ObjCDelegate` | `forwardInvocation:` for the named protocol's selectors |
| `ObjCTarget` | `action:` with the sender |
| `ObjCObserver` | `observeValueForKeyPath:ofObject:change:context:` |
| `ObjCDrawView::initWithFrameDraw` | `drawRect:` |
| `ObjCOpenGLView::initWithFramePixelFormatDraw` | `drawRect:` |
| `ObjCStageWindow` `on` / `off` | `canBecomeKeyWindow`, `canBecomeMainWindow` |
| `NSEvent::addLocalMonitorForEventsMatchingMaskHandler` | handler block `^NSEvent *(NSEvent *)` |
| `NSNotificationCenter::addObserverForNameObjectQueueUsingBlock` | block `^(NSNotification *)` |
| `CFFileDescriptor::create` | `CFFileDescriptorCallBack` |
| `GCController::startWirelessControllerDiscoveryWithCompletionHandler` | completion block |
| `CGDataProvider::createDirect` | `CGDataProviderDirectCallbacks.getBytePointer` (the address itself is the info; nothing owned or freed) |
| `NSObject::pointer` / `fromPointer`, `CFType::pointer` | address hand-off to and from other extensions |
| `AppKitException` | NSException translation |

Handlers are [callouts](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/callouts): each ObjC object or block holder owns its records and releases them in `dealloc`; at request end the callables are freed and the records go inert. AppKit holds delegates and targets weakly: keep the PHP object referenced as long as the window or item should call back. A second `__construct` on a glue object = Error (kept refusal `glue-construct-once`: AppKit would be left holding a freed delegate, SIGSEGV).

## ObjCDelegate

`PHPAppKitDelegate` (NSObject subclass):

* `conformsToProtocol:` YES for the protocol named at construction; `respondsToSelector:` YES only for selectors with a handler, so AppKit's optional-method checks see exactly what PHP registered.
* `methodSignatureForSelector:` reads the signature from the protocol (`protocol_getMethodDescription`, optional then required). `on()` accepts any selector; one the protocol does not declare has no signature and is never sent.
* `forwardInvocation:` converts each argument by its type encoding: objects boxed, `B` as bool, `c` (a signed char on arm64) and other integers as int, floats, `SEL` and `Class` as names, pointers as addresses, `CGRect`/`CGSize`/`CGPoint`/`NSRange`/`NSEdgeInsets` as their value classes. Calls the handler; writes its return into the invocation by the return type: BOOL, integers, floats, objects (+1 autoreleased; strings → NSString, numbers/bools → NSNumber), the five structs, selector or class name, address.

## ObjCTarget

`PHPAppKitTarget`: `action:` calls the handler with the sender boxed. Set the item's action to `ObjCTarget::ACTION`.

## ObjCObserver

KVO observer. `observe(object, keyPath, options, context)` = `addObserver:forKeyPath:options:context:` (`OPTION_NEW/OLD/INITIAL/PRIOR` combined with `|`); `stop(object, keyPath, context)` = `removeObserver:forKeyPath:context:`. Handler gets `(keyPath, ?object, change, context)`: `change` = every entry of KVO's dictionary under its own key (`kind`, `new`, `old`, `indexes`, `notificationIsPrior`), geometry as value classes. Each observe() is one registration (twice = handler twice); stop() of a pair KVO does not hold raises `NSRangeException` → AppKitException. Bookkeeping kept only so a freed observer is never messaged: observed objects retained until stop()/free, pairs still registered removed at free.

## ObjCStageWindow

NSWindow subclass `PHPStageWindow`. `on('canBecomeKeyWindow' | 'canBecomeMainWindow', fn (): bool)` sets the handler that override asks; `off()` clears it. Without a handler, or when it did not run, the override answers `super`'s (NO for a borderless window). Other names are kept and never asked. Made through the inherited `initWithContentRectStyleMaskBackingDefer()`: `appkit_called_class` maps a glue class to its runtime class through the class map when no ObjC class carries the PHP name.

## ObjCDrawView

NSView subclass `PHPDrawView`; `drawRect:` boxes `(view, dirty NSRect)` → PHP callout, inside the view's graphics context (`NSGraphicsContext::currentContext()->CGContext()`). Partial redraw: `setNeedsDisplayInRect:` per damaged rect, AppKit asks once per dirty region; with `NSViewLayerContentsRedrawPolicy::ON_SET_NEEDS_DISPLAY` the layer keeps the rest. Callout lifetime = view's (released in `dealloc`).

## ObjCOpenGLView

NSOpenGLView subclass `PHPOpenGLView`; `drawRect:` calls `$draw(view, dirty NSRect)`, nothing more. The handler calls `openGLContext()->makeCurrentContext()` and `flushBuffer()` itself. `initWithFramePixelFormatDraw` returns null when AppKit makes no view.

## Blocks and CF callbacks

* Local event monitor: AppKit gets the NSEvent the handler returns, nil for `null`; any other return, or a handler that did not run, hands AppKit its own event. Kept until `removeMonitor:`; after request end the handler no longer runs (the callout is inert). A second removal = ValueError (kept refusal `monitor-remove-once`).
* Notification block: `(NSNotification)` to PHP; queue as given (`NSOperationQueue::mainQueue()` to deliver on the main thread).
* `CFFileDescriptor` callout: `(CFFileDescriptor, int callBackTypes)`.
* GameController discovery completion: no arguments.

[^glue]: PHPAppKitDelegate, PHPAppKitTarget, PHPAppKitObserver, PHPStageWindow, PHPDrawView, PHPOpenGLView
[^bindings]: glue
