# Errors and threads

NSException becomes AppKitException; main-thread AppKit calls refuse other threads.

## Overview

`APPKIT_BEGIN`/`APPKIT_END` wrap each binding in `@autoreleasepool { @try … @catch (NSException *) }`. Caught exception → `AppKitException("<name>: <reason>")`, e.g. `NSInternalInconsistencyException` from `otherEventWithType:` given a key type.[^header]

`APPKIT_REQUIRE_MAIN_THREAD()` (`pthread_main_np()`) guards every `NSApplication` method except `postEvent:atStart:`, which AppKit allows from any thread. Off-main call → `AppKitException("NSApplication::x() must be called on the main thread")` instead of AppKit's assertion crash. CF run-loop calls carry no guard: CFRunLoop is thread-safe, and `getCurrent()` on another thread is that thread's loop.

`NSApplication::activate()` needs macOS 14; older → AppKitException. `activateIgnoringOtherApps()` binds the deprecated selector as-is.

[^header]: APPKIT_BEGIN/END, APPKIT_REQUIRE_MAIN_THREAD
