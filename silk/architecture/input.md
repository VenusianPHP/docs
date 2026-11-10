# Input

One event type, two adapters, a Router that bubbles and tracks the hover path, Tab focus, and in-app drag and drop.

## SilkEvent

`SilkEvent` carries a type, position (logical units), button, click count, key, modifiers, wheel deltas with a precise flag and scroll phase, text and edit commands. `EventType` cases: MouseMove, MouseDown, MouseUp, Wheel, Enter, Leave, KeyDown, KeyUp, Text, Edit, FocusGained, FocusLost.[^event]

Silk never synthesises events from polled input. Two adapters translate what arrives:

* `CanvasInputAdapter` maps `TKCanvas` view mail (CanvasPressed, CanvasWheeled, KeyPressed, TextCommitted, EditCommanded, FocusGained, ...) to SilkEvent.
* `StagedInputAdapter` maps Surface's ordered staged-window input mail (StagedPressed, StagedKeyPressed, ...) the same way.

Hosts queue events (`Host::enqueue()`) and the [frame loop](/docs/{{version}}/silk/architecture/hosts) drains them before anything else.

## Routing

`Router::dispatch(SilkEvent)` bubbles an event from the target widget to its ancestors, stopping when a handler returns true or at a popup root; it owns mouse capture (a press captures until release) and the hover path (Enter and Leave from path diffs). [Popups](/docs/{{version}}/silk/architecture/overlays) are hit top-down before the root; a dialog's veil takes every event under it. The Router also arms long press, opens context menus, shows the tooltip and starts drags.[^router]

## Focus

`FocusManager`: Tab order is [tree](/docs/{{version}}/silk/architecture/tree) order; the focus ring shows only after Tab and is cleared by any mouse press.[^focus]

## Drag and drop

`Router::beginDrag(source, DragPayload, x, y)` starts a `DragSession`. The target is the nearest enabled widget at or above the one under the pointer that has a drop callback; it gets Leave, Enter and Move, and its answer says whether it would take the drop. Release drops where taken; Escape or losing focus cancels. The chip of the label follows the pointer and the target's frame lands on a BOUNCY [spring](/docs/{{version}}/silk/architecture/motion) while it would take the drop.[^drag]

[^event]: src/Silk/Contracts/Input/SilkEvent.php, EventType.php.
[^router]: src/Silk/Core/Input/Router.php.
[^focus]: Class docblock of FocusManager.
[^drag]: Class docblock of DragSession.
