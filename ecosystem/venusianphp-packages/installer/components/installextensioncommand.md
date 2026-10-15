# InstallExtensionCommand

Symfony Console command `install:ext {ext?}` — installs any first-party PHP extension through PIE, from a list or by name.

## Surface

`#[AsCommand(name: 'install:ext')]`, registered in `bin/venusian`.[^command][^binary-test]

| Piece | Value |
|-------|-------|
| Argument | `ext` — optional — extension name; omit for the list |
| Flow | `new ExtensionsFlow(catalog: FirstPartyExtension::cases(), ask: false, preselect: false)`; the constructor takes a flow for tests |
| Bag | `interactive`, `extension_only` (the argument), `output_callback` |

Runs [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) alone: no composer, no application directory.

## Outcomes (tested)

| Bag after the flow | Shown | Exit |
|---|---|---|
| `extension_results`, all `installed` or `installed (0.10.x-dev)` | callout `Extensions Installed`, key/value list | 0 |
| `extension_results`, any other outcome | callout `Extensions Not All Installed` (warning) | 1 |
| note starts `Nothing to install`, or `None selected.` | `info` line | 0 |
| any other note | `error` line | 1 |

All rows, the catalog list with its disabled rows, named installs (interactive and not), and the no-download rule: `InstallExtensionCommandTest`.[^command-test]

[^command]: InstallExtensionCommand
[^command-test]: Pest coverage for execute()
[^binary-test]: Pest coverage for registration in bin/venusian
