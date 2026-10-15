# SummarizeExtensions

Turns the extension step's bag keys into callout content for the success box.

## Behavior (tested)

`SummarizeExtensions::run(array $shared): array` — content items for `callout()`.[^action][^action-test]

| Bag | Returns |
|---|---|
| `extension_results` set | `['PHP extensions:', Element::keyValueList($results)]` |
| else `extensions_note` set | `["PHP extensions: {$note}"]` |
| neither | `[]` |

[NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand) spreads the result into the `Installation Successful!` callout, after the "Application ready at" line. The two keys never coexist: a note means the flow stopped before installing ([ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow)).

[^action]: SummarizeExtensions::run
[^action-test]: Pest coverage for the three shapes
