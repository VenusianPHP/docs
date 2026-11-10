# The tree

The object model: a widget's identity and four behaviours, the slot a child sits in, dirty flags, and how the Tree repaints only what moved.

## A widget

A widget has an identity — `name()`, `path()`, `uuid()` — a parent, visibility, enabled and focusable flags, and four behaviours:[^contract]

| Method | Does |
|---|---|
| `measure(Size $available): Size` | wanted size, bottom-up, cached per available size |
| `arrange(Rect $r)` | takes its place, top-down |
| `paint(Painter $p)` | describes itself to the [painter](/docs/{{version}}/silk/architecture/painter) in logical units; `render()` wraps it with the appear transition, opacity and overdraw |
| `handle(SilkEvent $e): bool` | takes an [input](/docs/{{version}}/silk/architecture/input) event; true stops it bubbling |

`Silk\Core\Tree\Widget` is the base; `Silk\Core\Tree\Container` is a widget with children, each in a `Slot(grow, align)` — `grow` is the child's share of the main axis, `align` its place on the cross axis. Layouts live in `src/Silk/Core/Layout`: Column, Row, Grid, UniformGrid, Stack, Anchored, Border, SizeBox, Spacer, Switcher, WrapBox.

## Dirty flags

A setter stores the value, marks the widget dirty and returns `static`: `invalidateLayout()` measures and arranges again up the ancestor chain, `invalidatePaint()` paints again. A widget draws within its bounds plus `OVERDRAW` (8 units, for shadows, the press squash and grown handles), or its own `paintExtent()`; the Tree repaints the union of where each dirty widget was and is now, and nothing else.

## Layout passes

The host lays the tree out to its viewport in measure/arrange passes — at most `Tree::MAX_PASSES` (4) while something re-dirties, as wrapped text does. A widget may carry a tooltip, a context menu (a [popup](/docs/{{version}}/silk/architecture/overlays)), an appear/disappear [transition](/docs/{{version}}/silk/architecture/motion), a drop callback ([input](/docs/{{version}}/silk/architecture/input)) and its own colour, metric and class overrides, which resolve above the [theme](/docs/{{version}}/silk/architecture/looks); only the text colour inherits down the tree, and a `LookScope` gives a subtree a look of its own.

The gallery holds every widget built so far; a built widget that is not in the gallery is not done — see [gallery and bench](/docs/{{version}}/silk/runbooks/gallery-and-bench).

[^contract]: src/Silk/Contracts/Widget/Widget.php, Container.php, Slot.php; src/Silk/Core/Tree/Widget.php, Container.php, Tree.php.
