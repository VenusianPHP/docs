# Errors and threads

NSException becomes AppKitException after the call; results pass through; the only refusals are probed crash sites, the main-thread gate on AppKit UI classes among them.

## Overview

Translation: `APPKIT_BEGIN`/`APPKIT_END` wrap each binding in `@autoreleasepool { @try … @catch (NSException *) }`. NSException AppKit raised, after the native call → `AppKitException("<name>: <reason>")`, e.g. `NSInternalInconsistencyException` from `otherEventWithType:` given a key type, `NSRangeException` from an out-of-range text range. Not a refusal: the call was made.[^header]

Pass-through: nil → `null`, NO → `false`, clamped values (`setSelectedRange:` past the end), CGError / IOReturn as returned `int` (compare with `kCGErrorSuccess` / `kIOReturnSuccess`), null from a CF/CG create. Availability too: a selector missing on an older macOS (`NSApplication::activate` before 14, `CADisplayLink` before 14, `GCController.shouldMonitorBackgroundEvents` before 11.3) raises the runtime's `NSInvalidArgumentException` (unrecognized selector) → `AppKitException`. No pre-checks.

## Kept refusals

Only where the native call would cause memory unsafety, uncatchable process death or VM corruption, each shown by a probe on a real build. Each site: `/* binding:<id> */` on its throw line, a `sites` entry in `bindings.json`, a test in `tests/Probes`.[^bindings]

| Site | Call | Without it | Refused with |
|---|---|---|---|
| `main-thread-appkit-ui` | `APPKIT_REQUIRE_MAIN_THREAD()` on NSApplication (all but `postEvent:atStart:`), NSWindow, NSView and subclasses, NSControl, NSMenu/NSMenuItem, NSScreen, NSResponder, NSEvent monitors, NSLayoutAnchor, CADisplayLink, the glue view constructors | AppKit raises, then SIGTRAP | `AppKitException("X::y() must be called on the main thread")` |
| `cfdata-null-address` | `CFData::create(null, 0, length > 0)` | SIGTRAP | ValueError |
| `cfdata-string-length` | `CFData::create` with `length` past the string | Core Foundation reads past it: SIGSEGV (libgmalloc) | ValueError |
| `cgimage-decode-length` | `CGImage::create` decode list shorter than 2 × components | Core Graphics reads past it: SIGSEGV (libgmalloc) | ValueError |
| `attribute-value-class` | foreground/background colour attribute that is no NSColor | SIGTRAP when drawn | TypeError |
| `glue-construct-once` | second `__construct` on a glue object | SIGSEGV | Error |
| `monitor-remove-once` | `NSEvent::removeMonitor` twice on one monitor | SIGSEGV | ValueError |
| `pixel-format-value` | `NSOpenGLPixelFormat::initWithAttributes` ending on a value-taking attribute with no value | SIGSEGV | ValueError |

Foundation, text, graphics, media, GameController, CMTime, CALayer, OpenGL context/pixel format and the non-view grid/table helpers (NSGridCell/Row/Column, NSTableColumn, NSCell, NSIndexSet) carry no gate: they run on the calling thread. CF run-loop calls carry none: CFRunLoop is thread-safe, `getCurrent()` on another thread is that thread's loop. Callouts' own thread check (a native callback on a foreign thread never enters PHP) is in [callouts](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/callouts).

Marshal checks (a PHP value with no native form: wrong type, out-of-range int) are argument errors before the call, not refusals; `calayer-contents-value` (`setContents` given an object that is neither NSObject nor CFType) is one.

## Probe build

`./configure --enable-appkit-probes` defines `APPKIT_PROBES`: `APPKIT_PROBE_OFF("<id>")` reads env `APPKIT_PROBE_OFF`, so `APPKIT_PROBE_OFF=<id>` turns that one site's check off. Any other build compiles the macro to 0. `tests/Probes` skip unless the loaded build defines the `APPKIT_PROBES` constant; each runs the call in a child twice (site on: refused, clean exit; site off: the signal). Never a release build. Steps: [build](/docs/{{version}}/ecosystem/standalone-extensions/appkit/runbooks/build-install-test).[^probes]

[^header]: APPKIT_BEGIN/END, APPKIT_REQUIRE_MAIN_THREAD, APPKIT_PROBE_OFF
[^bindings]: sites
[^probes]: probe tests
