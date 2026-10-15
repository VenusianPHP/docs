# Layout and geometry

Qt owns geometry; PHP installs layouts, adds widgets with stretch and alignment, and reads sizes back as arrays.

## Overview

Three ways a child lands in a parent, each one Qt call:[^layout]

| Arrangement | Calls |
|---|---|
| Column / row | `new QVBoxLayout($host)` / `new QHBoxLayout($host)` installs the layout on `$host`, which owns it; `addWidget($w, $stretch, $alignment)` reparents `$w` into the host; `insertWidget` (negative index appends, past `count()` is a ValueError), `addLayout`, `addStretch`, `setStretch`, `setAlignment` as in Qt |
| Grid | `new QGridLayout($host)`, `addWidget($w, $row, $col, $rowSpan, $colSpan, $alignment)`; `rowCount`/`columnCount` grow with what was added |
| Absolute | no layout on the parent: `new QWidget($host)` then `move($x, $y)` / `setGeometry($x, $y, $w, $h)`; `$host->layout()` stays null |

Removal: `removeWidget($w)` takes the item out of the layout only; the widget keeps its parent until `setParent(null)` (or deletion). `itemAtWidget($i)` and `itemAtPosition($r, $c)` return the widget at a slot, null for a spacer, a nested layout or an empty slot.[^layout]

Sizes come back as arrays, never computed in PHP: `size()`, `sizeHint()`, `pos()` as `[w, h]` / `[x, y]`, `geometry()` as `['x', 'y', 'width', 'height']`. Constraints: `setMinimumSize`, `setFixedSize`, `setSizePolicy(QSizePolicy\Policy $h, QSizePolicy\Policy $v)`. `Qt\AlignmentFlag` is a QFlags parameter: pass a case or an OR'd int (`Qt\AlignmentFlag::TOP->value | Qt\AlignmentFlag::LEFT->value`).[^widget]

Ownership follows the [object model](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/object-model): a layout made with a parent, or later passed to `setLayout()`/`addLayout()`, has a Qt parent and is not deleted by PHP; a parentless layout is deleted with its PHP object.

Building before installing, Qt's usual order, works with temporaries: `$col = new QVBoxLayout(); $col->addWidget(new QLabel('x')); $host->setLayout($col);`. Qt reparents a widget only when the layout already sits on a widget, so until `setLayout()` the label has no parent; the layout holds the label's wrapper (a hold, a QObject child of the native layout) so PHP does not delete it while the layout lists it. Holds die with the native layout, after its items: a layout dropped without ever being installed frees its widgets; `removeWidget()` releases the widget's hold at once. Nested layouts (`addLayout($inner)` before installing) keep their own holds until the outer layout is deleted.[^layout]

Qt lays out lazily: after `show()` a `QCoreApplication::processEvents()` lets the first layout pass run before sizes are read.[^test]

[^layout]: QLayout family
[^widget]: QWidget geometry methods
[^test]: Box, grid, absolute placement
