# Mail

The mail Silk widgets post: Surface's view mail where the toolkit twin's mail is toolkit-free, and a twin of it in `Silk\Contracts\Mail` where the twin's mail is not.

## Schema

Every class is a readonly `NamedSignal` implementing Surface's `PrimitiveMail` (`window()`, `path()`, `uuid()`), extending `PrimitiveEventOccurred(window, path, uuid)`, and named `view.<verb>.<window>.<path>` — the same schema as Surface's [view mail](/docs/{{version}}/surface/api/view-mail).[^mail] A widget posts the mail its `TK*` twin's driver posts: where Surface's class does not depend on `TKPrimitive` (ButtonClicked, Toggled, ValueChanged, SelectionChanged, TextChanged, TextSubmitted, RowSelected, and the rest), Silk posts it unchanged; for the widgets whose twin's mail could not travel, Silk defines the twin:

| Class | `name()` | When |
|---|---|---|
| `BlockEditorClicked` | `view.block-clicked.…` | the user clicked a script (to run it); `$block` is its top block |
| `BlockEditorContext` | `view.block-context.…` | right click: `$block` under the pointer (0: the canvas) at `$x`, `$y` |
| `BlockEditorChanged` | `view.block-changed.…` | the user changed the scripts: moved, attached, took out, deleted or typed into a block; `$block` is the block (0: several, or one was deleted) |
| `NodeGraphEdited` | `view.node-graph-edited.…` | a NodeGraph gesture ended with a change: a link made or taken away, nodes moved or removed |
| `NodeContextRequested` | `view.node-context-requested.…` | right click on a node (selected first) or, `$node` 0, the empty canvas |
| `NodeActivated` | `view.node-activated.…` | double click on a node, to open what it stands for |
| `NodeRemoved` | `view.node-removed.…` | a node deleted with the Delete key; its links went first (NodeUnlinked each) |
| `NodeSelectionChanged` | `view.node-selection-changed.…` | the selection changed; `$node` is the node just clicked, or 0 |
| `NodeMoved` | `view.node-moved.…` | a node moved, when the button went up or an arrow key nudged it |
| `NodeLinked` | `view.node-linked.…` | an output linked to an input; `$link` is the new link |
| `NodeUnlinked` | `view.node-unlinked.…` | a link taken away; the link is gone, so its pins come with the mail |
| `TimelineEdited` | `view.timeline-edited.…` | a gesture, a mute or a lock ended with a change: one for the whole gesture |
| `TimelineItemRemoved` | `view.timeline-item-removed.…` | a Timeline item deleted |
| `TimelineItemActivated` | `view.timeline-item-activated.…` | a Timeline item double clicked |
| `TimelineSelectionChanged` | `view.timeline-selection.…` | a Timeline's selection changed; item 0: several or none |
| `TimelineItemChanged` | `view.timeline-item-changed.…` | an item moved or stretched |
| `TimelineTimeChanged` | `view.timeline-time.…` | the playhead moved, or it played |
| `IslandChanged` | `view.island-changed.…` | an Island unfolded or folded by the user, the pointer or its time |
| `DockChanged` | `view.dock-changed.…` | the user moved, resized, showed or closed a panel of a DockArea |
| `FileSelectionChanged` | `view.file-selection-changed.…` | the entry under a FileBrowser's cursor changed; null: none |
| `FileAccepted` | `view.file-accepted.…` | the user chose a file or a folder in a FileBrowser |
| `FileCancelled` | `view.file-cancelled.…` | the user cancelled a FileBrowser |
| `TabClosed` | `view.tab-closed.…` | a documents tab closed by its close button or a middle click, page removed |
| `LinkActivated` | `view.link-activated.…` | a link of a Markdown label clicked |
| `TilesSelected` | `view.tiles-selected.…` | a TileView's selection changed: the selected tiles, ascending, and the current one (-1: none) |
| `ColorChanged` | `view.color-changed.…` | a ColorPicker's colour changed (every step of a drag) |
| `TimeChanged` | `view.time-changed.…` | a TimePicker changed; `$second` is null when it shows HH:MM |
| `ColumnSorted` | `view.column-sorted.…` | a table sorted by `$column` (a column id) |
| `RowActivated` | `view.row-activated.…` | a row activated: Enter, or a double click; `$row` is the row's index in the widget's own data |
| `ZoomChanged` | `view.zoom-changed.…` | a TextEditor zoomed: to zoom others the same, or keep it for next time |

## Rules

* User action only: a programmatic setter posts nothing.
* A host takes its tree's input first: `$host->handles($item)` consumes the staged and canvas mail the adapters translate, before the sketch sees the rest (see [hosting](/docs/{{version}}/silk/guide/hosting)).

[^mail]: src/Silk/Contracts/Mail/, over Surface's view mail contracts.
