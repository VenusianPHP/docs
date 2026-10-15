# Errors and threads

QtException for refusals; applications only on the main thread.

## Overview

`QtException` covers what the binding refuses before reaching Qt: a second application, a wrapper whose object Qt deleted, a wrapper never constructed (a PHP subclass that skipped `parent::__construct`), an application or `exec()` off the main thread (`pthread_main_np()` on macOS, `gettid() == getpid()` on Linux).[^header]

Argument errors are PHP's own: `ValueError` for an unknown signal signature, an empty argv, out-of-range milliseconds or descriptors; `TypeError` for a non-callable or non-descriptor.

`QAbstractEventDispatcher::wakeUp()` and `interrupt()` are thread-safe in Qt and carry no guard.

[^header]: PHPQT_REQUIRE_MAIN_THREAD, PHPQT_THIS
