# Signals

String-signature connect through a moc-free dynamic slot; argument marshalling; slot lifetime.

## Overview

`PhpSlot` = a `QObject` subclass holding a PHP callable. `QObject::connect()` normalises the signature (`QMetaObject::normalizedSignature`), finds the signal with `indexOfSignal`, and calls `QMetaObject::connect(sender, index, slot, QObject::staticMetaObject.methodCount(), Qt::DirectConnection)`. Activation arrives in `PhpSlot::qt_metacall`; after `QObject::qt_metacall` subtracts QObject's own methods the id is 0, which invokes the callable. No moc, no generated metaobject. A signal the class lacks gets what Qt's own string connect gives: Qt's warning and the invalid connection.[^qobject]

Arguments, typed by the signal's `QMetaMethod::parameterMetaType`: bool, integer and float types as PHP scalars; `QString`/`QByteArray` as strings; `QDate`, `QPoint`, `QPointF`, `QSize`, `QRect`, `QUrl` and `QKeySequence` as copies in their PHP classes (`QDateEdit::dateChanged` hands a `QDate` over); `QSocketDescriptor` as the int fd; enums as ints (`QMediaPlayer::MediaStatus` arrives as the `QMediaPlayer\MediaStatus` case value); `QObject*` boxed. A `QObject*` that is the emitting sender maps to the sender's own wrapper even during `destroyed()`, when Qt has already cleared its QPointers.[^runtime]

Lifetime:

* Slots live in a per-request list. The sender's `destroyed` `deleteLater`s its slot.
* `QObject::disconnect(Connection)` severs the connection, frees the callable, and deletes the slot (`deleteLater` when called from inside a callback).
* `QMetaObject\Connection` going out of scope does not disconnect, as in Qt.
* `QTimer::singleShot(msec, callable)`: the slot is the functor's context; it fires, frees the callable, `deleteLater`s itself.
* `QImage`'s cleanup function: a slot with one bound argument (`cleanupInfo`), fired once on its own thread (queued there from another), then freed.
* RSHUTDOWN deletes every remaining slot (disconnecting it) and frees its callable while the engine can still free it.

`QEventFilter` is a `PhpSlot` subclass overriding `eventFilter(watched, event)`: it shares the slot's call path and request-end teardown, hands PHP every event as `(watched, event)` and returns PHP's bool to Qt. The callable reads `$event->type()` itself.

`QMetaObject::invokeMethod()` converts PHP arguments the other way, to the parameter types of the member of that name and arity (`phpqt_zval_to_variant`), the value classes included, and makes the native call with the connection type given.

A callable that throws leaves the exception pending; later callbacks in the same Qt call are skipped and the exception surfaces when `processEvents`/`exec` returns to PHP.

[^runtime]: PhpSlot, argument conversion
[^qobject]: QObject::connect / disconnect
