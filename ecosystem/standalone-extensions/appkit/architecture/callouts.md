# Callouts

PHP callables that native code calls back into; lifetime follows the native object, detached at request end.

## Overview

`appkit_callout` = persistent record holding a PHP callable, a native refcount, the owning native object (not retained) and a detach function.[^runtime] Native side owns the record through its context `info` + `retain`/`release` callbacks, so a callback keeps working after PHP drops every handle while the native object lives (run loop holds source → source holds descriptor → descriptor holds record).

Invocation (`appkit_callout_invoke`): boxes args, calls the callable with the record and callable both held (a callable may invalidate its own owner). Skipped while a PHP exception is pending; the exception surfaces when the native call that ran the callback returns to PHP.

Callbacks only run inside a PHP call that spins the run loop (`nextEventMatchingMask…`, `run`, `CFRunLoop::runInMode`), inside the request, on the thread that made the record: each record stores its creating thread and every native entry point (`appkit_callout_can_enter`) refuses any other thread before boxing an argument, so a delegate, target, KVO change, notification block or descriptor callback fired elsewhere never touches PHP. A record whose last native reference goes on another thread stays linked, owner cleared, and the owner thread's request end frees it.

Users: `ObjCDelegate` (returns: objects +1 autoreleased, strings → NSString, numbers/bools → NSNumber), `ObjCTarget`, `ObjCObserver`, `NSNotificationCenter` blocks, `CFFileDescriptor`.

RSHUTDOWN (`appkit_callouts_detach_all`): every attached record's owner is detached (`CFFileDescriptorInvalidate`) and its callable freed while the engine can still free it. Records stay until the native side releases them.

First user: `CFFileDescriptor::create(fd, closeOnInvalidate, callout)`; callout gets `(CFFileDescriptor $f, int $callBackTypes)`.[^fd]

[^runtime]: appkit_callout_*
[^fd]: CFFileDescriptor::create
