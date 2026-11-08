# Overlays

Menus, combo lists, pickers, tooltips, dialogs and toasts are drawn by the host's own tree in a layer above the root, clamped to the host's bounds — a canvas host's menu cannot leave the canvas. No child OS windows are needed.[^layer]

## The layer

`OverlayLayer` holds the tree's popups in push order, the last on top. Popups are hit top-down before the root; closing popups paint but are never hit. The drag chip and the target frame of an in-app [drag](/docs/{{version}}/silk/architecture/input) paint in the same layer.

## The popups

| Kind | How it draws |
|---|---|
| `Popup` | a column drawn in the layer; grows out of its anchor point on a BOUNCY [spring](/docs/{{version}}/silk/architecture/motion): scale 0.72 + 0.28 × shown, opacity min(1, shown × 1.8); once closed it keeps painting without input until shown reaches 0. `Placement` says where it sits against its anchor: Below, Above, Right, Left, AtPoint |
| `Tooltip` | passive (never hit or focused): text + 16 wide, 4-radius box in the Tooltip role with a shadow, at the pointer +12, +20, flipped above when there is no room; BOUNCY in on a springy look, Smooth on a platform look; opacity min(1, shown × 2) springy, × 1 platform |
| `Dialog` | a modal popup centred over a veil (black 0.42 × shown), card radius 10, shadow y+6 blur 28, scale 0.9 + 0.1 × shown, rising from 60 units; the veil takes every event under it. `MessageBox` is a dialog with a message |
| `Toast` / `ToastQueue` | rise 14 units as they show (SNAPPY) and wait in sequence or stack; a hidden toast lets the pointer through |

## Looks and glass

A popup of a glass [look](/docs/{{version}}/silk/architecture/looks), and a macOS 26 look's popups, are painted as glass (`Popup` checks `material()->isGlass()` and `liquid()`): they go through `Painter::glass()` like any pane (see [painter](/docs/{{version}}/silk/architecture/painter)); a tooltip of a glass look is a drop of glass in the tooltip colour. Their shadow rides in the glass look, so rounded corners meet it.

[^layer]: Class docblock of OverlayLayer, Popup, Tooltip, Dialog; src/Silk/Widgets/Toast.php, ToastQueue.php.
