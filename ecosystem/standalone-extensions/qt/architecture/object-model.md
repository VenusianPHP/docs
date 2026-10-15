# Object model

One PHP object per QObject, guarded by QPointer; PHP deletes what it created unless Qt owns it through a parent.

## Overview

`phpqt_object { QPointer<QObject> *guard; QObject *raw; bool owned; int argc; char **argv; zend_object std; }`. Qt members sit behind pointers so the struct stays standard-layout for `XtOffsetOf`.[^header]

* Guard: `QPointer` nulls itself when Qt deletes the object; every method goes through `PHPQT_THIS`, which throws `QtException("<Class> has been deleted by Qt")` instead of touching freed memory.
* Identity: module global `boxes` maps address → wrapper. Boxing returns the existing wrapper only while its guard still points at that address, so an address Qt reuses gets a fresh wrapper.
* Class choice when boxing: walk `metaObject()` → `superClass()`; first class name registered with `phpqt_map_class()` wins (e.g. `QCocoaEventDispatcher` → `QAbstractEventDispatcher`); fallback `QObject`.
* Ownership: constructors adopt (`owned = true`); boxed objects are borrowed. `free_obj` deletes an owned object only if it has no parent (a parent means Qt owns it). While PHP runs inside a Qt callback, a non-application object is `deleteLater()`d instead, since it may be the one emitting. The same holds while Qt destroys a slot (with its parent, or alone): its callable is freed with the slot's parent pushed on a stack of teardowns (freeing it can destroy further slots), and an owned, parentless object that is the parent, or an ancestor, of any slot on that stack is `deleteLater()`d, since deleting it there would delete the dying objects under it a second time.[^runtime]
* Applications: Qt keeps `argc` by reference and `argv` by pointer, so both live in the wrapper (persistent memory) and are freed after the application is deleted. One application per process: a second constructor throws.
* One construction per wrapper: `phpqt_adopt` deletes the object a second `__construct()` made and throws `QtException("<Class>::__construct() called twice")`, so the first object keeps its wrapper and identity-map entry.
* Holds: a parentless widget added to a parentless layout is kept alive by a `PhpHold` (an unconnected `PhpSlot` holding the widget's wrapper) parented to the native layout; Qt deletes it with the layout, after the layout's items, and request shutdown releases it with the slots ([layout](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/layout-and-geometry)).

## Values

`QFont`, `QPixmap`, `QUrl` and `QTableWidgetItem` are not QObjects. They use `phpqt_value_object { void *ptr; bool constructed; bool owned; void (*destroy)(void *); zend_object std; }`: a heap copy the PHP object owns and deletes through `destroy`. Copies in, copies out: `QWidget::font()` returns a new wrapper around a copy; `setFont()` copies the wrapped value in. No identity map; two reads give two objects.[^values]

`QTableWidgetItem` is the one value with a second owner. `QTableWidget::setItem()` hands the item to the table (`owned = false`), and the item is a `PhpTableWidgetItem` subclass whose destructor clears its wrapper's `ptr`, so a call after `clearContents()` or a row removal throws `QtException("QTableWidgetItem has been deleted by Qt")` instead of reading freed memory. `item(r, c)` and `horizontalHeaderItem(c)` return the wrapper the item already has, or a new table-owned one. Items Qt makes itself (header labels, a cell a user types into) are clones of an item prototype the `QTableWidget` constructor installs, so they are `PhpTableWidgetItem`s too and their wrappers learn of deletion the same way. An item that already belongs to a table, or a cell outside the table, is refused by `setItem()` (Qt would drop the item unstored, its view pointer dangling).[^values]

[^runtime]: Boxing, adoption, free_obj
[^header]: phpqt_object
[^values]: phpqt_value_object, PhpTableWidgetItem
