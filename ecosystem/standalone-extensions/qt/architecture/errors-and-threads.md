# Errors and threads

Qt answers for itself; kept refusals only where a probe shows a crash, each with its site and probe test.

## Overview

Qt has no error object. What it does with a call passes through: an invalid value (`QColor(256, 0, 0)` is invalid, `findBlockByNumber()` past the end is the invalid block), false, nullptr, a clamp (`QFont::setWeight(0)` sets 1), or a qWarning on stderr (an insert index past the end, an item another table owns, an unknown signal, a cursor position off the document, a negative timer interval). The binding refuses a call only where making it was shown to crash.[^bindings]

## Kept refusals

Each reads `if (!PHPQT_PROBE_OFF("<id>") && (<check>))`, marks its throw line `/* binding:<id> */`, and has a probe test in `tests/Probes` that shows the crash with the check off.[^header]

| Site | Calls | Outcome |
|---|---|---|
| `qapp-widget`, `qapp-text-widget`, `qapp-slider`, `qapp-table`, `qapp-tree-widget`, `qapp-splitter`, `qapp-gl-painter`, `qapp-menubar`, `qapp-menu` | widget constructors before a `QApplication` | qFatal abort |
| `qguiapp-window`, `qguiapp-pixmap`, `qguiapp-pixmap-from-image` | `QWindow`, `QPixmap`, `QPixmap::fromImage` before a `QGuiApplication` | qFatal abort |
| `qguiapp-vulkan-create` | `QVulkanInstance::create()` before a `QGuiApplication` | SIGSEGV |
| `main-thread-macos` | an application, widget or `QWindow` constructor off the process main thread, macOS only | AppKit's uncaught NSException |
| `second-application-macos` | a second application, macOS only (Linux hangs in the constructor, none of the three outcomes) | SIGSEGV at teardown |
| `table-item-range` | `QTableWidget::setItem()` outside the table: Qt leaves the item's view pointer on the table | read of freed memory |
| `spacer-owned` | a spacer item a layout already owns, added to another | double delete |
| `qevent-plain-type` | a plain `QEvent` of a type Qt delivers as a subclass | read past the event |
| `qbytearray-string-length` | `QByteArray(data, size)` with a size past the string | read past the string |

Refusals throw `QtException`, or a `ValueError` where an argument is the cause.

## Marshal errors

Marshalling raises PHP's own errors before the call: a `TypeError` for a value the C++ type cannot hold (a non-callable, a non-descriptor, a list entry of the wrong type, a value class of the wrong class for a `QVariant` parameter), a `ValueError` for an int outside its C type's range (`phpqt_long_fits`) or an `argc` above `count($argv)`. A wrapper whose object Qt deleted, or that was never constructed, throws `QtException` (`phpqt_this`, `phpqt_value_this`); a second `__construct()` likewise.

## Threads

Off macOS no call is gated by thread. `QAbstractEventDispatcher::wakeUp()` and `interrupt()` are thread-safe in Qt. A `QImage` cleanup function runs on the thread that made the image, queued there from any other.

[^header]: PHPQT_PROBE_OFF, PHPQT_REQUIRE_MAIN_THREAD, PHPQT_THIS
[^bindings]: sites
