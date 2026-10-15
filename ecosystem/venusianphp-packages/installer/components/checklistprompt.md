# ChecklistPrompt

laravel/prompts multi-select with disabled rows — each carries a reason, the cursor steps over it, no key selects it.

## Role

`laravel/prompts` 0.3 `multiselect` has no disabled options. `ChecklistPrompt extends MultiSelectPrompt` adds them; `ChecklistPromptRenderer extends MultiSelectPromptRenderer` draws them.[^prompt][^renderer]

```php
$picked = (new ChecklistPrompt(
    label: 'Extensions to install',
    options: ['epoll' => 'epoll', 'kqueue' => 'kqueue'],   // value => label
    disabled: ['epoll' => 'Linux only'],                    // value => reason
    default: ['kqueue'],
    hint: 'Space to select, Enter to confirm.',
))->prompt();   // list of selected values
```

```
 │   – epoll (Linux only)
 │ › ◼ kqueue
```

## Behavior (tested)

| Key | Result |
|---|---|
| open | Cursor on the first enabled row |
| Up / Down | Step over disabled rows, wrap included |
| Home / End | Land on the nearest enabled row |
| Space | Toggles an enabled row; nothing on a disabled one |
| Ctrl+A | Selects, or clears, the enabled rows only |
| defaults | Disabled values dropped |

Rows: disabled = dim, dash for the checkbox, reason in brackets. Cancelled = every row struck through, as stock. All in `ChecklistPromptTest`, keys fed by `Prompt::fake()`.[^prompt-test]

## How it hooks in

* The package finds a renderer by the prompt's exact class and its `default` theme takes no additions → `getRenderer()` is overridden to return `ChecklistPromptRenderer`.
* The parent constructor's key handler calls `highlightNext/Previous`, `toggleHighlighted`, `toggleAll` on `$this` → the overrides take effect with no handler of their own. One extra `on('key')` listener moves Home/End off a disabled row.
* `renderOptions()` is re-implemented whole: the stock one builds its rows inside a closure.

Tied to `laravel/prompts` `^0.3` internals (`Scrolling` trait, `MultiSelectPromptRenderer::renderOptions`).

## Related

- [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) — `ExtensionSelectNode` is the one caller

[^prompt]: ChecklistPrompt
[^renderer]: ChecklistPromptRenderer
[^prompt-test]: Pest coverage for keys and rows
