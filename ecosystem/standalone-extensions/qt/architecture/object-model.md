# Object model

One PHP object per QObject, guarded by QPointer; PHP deletes what it created unless Qt owns it through a parent.

## Overview

`phpqt_object { QPointer<QObject> *guard; QObject *raw; bool owned; int argc; char **argv; char **strings; int string_count; zend_object std; }`. Qt members sit behind pointers so the struct stays standard-layout for `XtOffsetOf`.[^header]

* Guard: `QPointer` nulls itself when Qt deletes the object; every method goes through `PHPQT_THIS`, which throws `QtException("<Class> has been deleted by Qt")` instead of touching freed memory.
* Identity: module global `boxes` maps address → wrapper. Boxing returns the existing wrapper only while its guard still points at that address, so an address Qt reuses gets a fresh wrapper.
* Class choice when boxing: walk `metaObject()` → `superClass()`; first class name registered with `phpqt_map_class()` wins (e.g. `QCocoaEventDispatcher` → `QAbstractEventDispatcher`); fallback `QObject`.
* Ownership: constructors adopt (`owned = true`); boxed objects are borrowed. `free_obj` deletes an owned object only if it has no parent (a parent means Qt owns it). While PHP runs inside a Qt callback, a non-application object is `deleteLater()`d instead, since it may be the one emitting. The same holds while Qt destroys a slot (with its parent, or alone): its callable is freed with the slot's parent pushed on a stack of teardowns (freeing it can destroy further slots), and an owned, parentless object that is the parent, or an ancestor, of any slot on that stack is `deleteLater()`d, since deleting it there would delete the dying objects under it a second time.[^runtime]
* Applications: Qt keeps `argc` by reference and `argv` by pointer, so both live in the wrapper (persistent memory) and are freed after the application is deleted; Qt's argc after it strips its own options is written back to the PHP `$argc`. Qt rearranges `argv` as it strips them, so the strings are freed from their own array (`strings`). A second application is refused on macOS (site `second-application-macos`).
* One construction per wrapper: `phpqt_adopt` deletes the object a second `__construct()` made and throws `QtException("<Class>::__construct() called twice")`, so the first object keeps its wrapper and identity-map entry.
* Holds: a parentless widget added to a parentless layout is kept alive by a `PhpHold` (an unconnected `PhpSlot` holding the widget's wrapper) parented to the native layout; Qt deletes it with the layout, after the layout's items, and request shutdown releases it with the slots ([layout](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/layout-and-geometry)).

## Values

Qt's value classes (`QPoint`, `QPointF`, `QSize`, `QRect`, `QDate`, `QKeySequence`, `QUrl`, `QByteArray`, `QFont`, `QPixmap`, `QImage`, `QColor`, `QBrush`, the text values), `QTableWidgetItem` and `QTreeWidgetItem` are not QObjects. They use `phpqt_value_object { void *ptr; bool constructed; bool owned; void (*destroy)(void *); …; zend_object std; }`: a heap copy the PHP object owns and deletes through `destroy`. Copies in, copies out: `QWidget::font()` returns a new wrapper around a copy; `setFont()` copies the wrapped value in. No identity map; two reads give two objects. A second `__construct()` is refused by `phpqt_value_fresh`.[^values]

A `QImage` made from an address borrows that buffer, as Qt does: the image holds no copy, and the buffer (a `QByteArray`'s `pointer()`, a framebuffer's) must outlive every image sharing it. Its cleanup function is a `PhpSlot` holding the callable and the bound `cleanupInfo`; Qt's `cleanupInfo` is a `QPointer` to that slot, so after request end, when the slot is gone, nothing runs.

A value may also be borrowed from an owner (`phpqt_value_borrow`): a `QLayoutItem` read from a layout reads as deleted once the layout no longer lists it (`QLayout::indexOf`).

`QTableWidgetItem` and `QTreeWidgetItem` are the values with a second owner. Once `QTableWidget::setItem()` stored the item (`item->tableWidget()` is that table), the table owns it (`owned = false`); an item another table holds stays that table's, as Qt warns. The item is a `PhpTableWidgetItem` subclass whose destructor clears its wrapper's `ptr`, so a call after `clearContents()` or a row removal throws `QtException("QTableWidgetItem has been deleted by Qt")` instead of reading freed memory. `item(r, c)` and `horizontalHeaderItem(c)` return the wrapper the item already has, or a new table-owned one. Items Qt makes itself (header labels, a cell a user types into) are clones of an item prototype the `QTableWidget` constructor installs, so their wrappers learn of deletion the same way. A cell outside the table is refused (site `table-item-range`: Qt drops the item unstored, its view pointer on the table).[^values]

`QTreeWidgetItem` follows the same pattern. Once `QTreeWidget::addTopLevelItem()` or `QTreeWidgetItem::addChild()` stored the item (afterwards `item->treeWidget()` is that tree with no parent, or `child->parent()` is that item), the tree or parent owns it. Qt ignores an item that already has a tree or a parent, and that item stays where it was. The item is a `PhpTreeWidgetItem` whose destructor clears its wrapper's `ptr`. Qt's base destructor then deletes the children, and each child clears its own wrapper. So after `clear()`, after the tree goes, or after the last reference to a PHP-owned parent is dropped, a call on any of those items throws `QtException("QTreeWidgetItem has been deleted by Qt")`. `child()`, `parent()`, `currentItem()`, `selectedItems()` and the signal arguments return the wrapper the item already has, or a new tree-owned one. Only PHP adds items: Qt's header item is not bound, and Qt clones items only for drag and drop, which no bound call turns on.

`addChild()` passes through Qt's own behaviour for a cycle. An item added under itself or under one of its descendants, while neither belongs to a tree, makes Qt's subtree walk (`propagateDisabled`) loop forever. Probed 2026-10-18: the process spins with flat memory and does not crash, so this is not a refusal under rule 3.

`QTextEdit\ExtraSelection` is a plain object, the struct: typed public `cursor` and `format` properties holding PHP values, copied into Qt's list by `setExtraSelections()`.

[^runtime]: Boxing, adoption, free_obj
[^header]: phpqt_object
[^values]: phpqt_value_object, PhpTableWidgetItem
