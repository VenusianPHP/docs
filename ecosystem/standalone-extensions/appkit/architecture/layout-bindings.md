# Layout bindings

NSStackView, NSGridView and Auto Layout anchors/constraints as bound; what PHP must set for constraints to apply.

## Overview

Three ways to place a view, all AppKit's own; PHP never computes geometry.

* **Stack**: `NSStackView::stackViewWithViews([...])`, then orientation, spacing, edge insets, alignment, distribution. Arranged subviews are the stack's own list (`arrangedSubviews`), distinct from `subviews`.[^stack]
* **Grid**: `NSGridView::gridViewWithNumberOfColumnsRows(c, r)`; rows added as arrays of views, `null` = empty cell (bound as `NSGridCell.emptyContentView`; reads back as `null`). Merged cells block `removeRowAtIndex` for their rows (AppKit raises → `AppKitException`).[^grid]
* **Constraints**: anchors from `NSView` (`leadingAnchor()` …); `constraintEqualToConstant`/`GreaterThanOrEqual` only on dimension anchors (width/height), `AppKitException` otherwise. Activate with `NSLayoutConstraint::activateConstraints([...])`.[^layout]

Constructors build the class they are called on: `NSStackView::initWithFrame()` is an `NSStackView`, `NSGridView::gridViewWithNumberOfColumnsRows()` called on a subclass makes that subclass.

Auto Layout only applies to a view with `setTranslatesAutoresizingMaskIntoConstraints(false)`; leave it `true` and the frame wins. `layoutSubtreeIfNeeded()` resolves the frame synchronously for reading.

## Lifetime

Views are retained by their superview and by the PHP box; `removeFromSuperview()` drops the native side's reference, PHP's box keeps the view alive until released. Constraints hold their anchors' views weakly as AppKit does.

[^stack]: NSStackView
[^grid]: NSGridView, NSGridCell, NSGridRow, NSGridColumn
[^layout]: NSEdgeInsets, NSLayoutAnchor, NSLayoutConstraint, appkit_view_array
