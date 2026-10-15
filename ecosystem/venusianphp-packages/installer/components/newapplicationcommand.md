# NewApplicationCommand

Symfony Console command `new` that scaffolds a Venusian app via PocketFlow.

## Surface

`#[AsCommand(name: 'new', description: 'Create a new Venusian PHP application')]`.[^command]

| Piece | Value |
|-------|-------|
| Name | `new` |
| Argument | `name` — `InputArgument::REQUIRED` — "The name (or path) of the application" |

`execute()` passes `rtrim((string) $input->getArgument('name'), '/\\')` (trailing only) into [ResolveDirectory](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/resolvedirectory), so an absolute path keeps its leading slash. [PrepareSharedBag](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/preparesharedbag) stores the same value as `$shared['name']`.[^command][^resolve-test][^command-test]

It then [PrepareSharedBag](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/preparesharedbag), wires the [node flow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration), and `Flow::run($shared)`.[^command][^flow-test]

## Callout outcomes

After the flow, the command inspects `$shared['success']`:[^command]

| `$shared['success']` | Callout |
|----------------------|---------|
| `true` | `Installation Successful!` — "Application ready at {$directory}", then [SummarizeExtensions](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/summarizeextensions) (extension outcomes, or why the step ended) |
| `false` | `Installation Failed` (type `error`) — key/value list of `$shared['errors']` (fallback `"Unknown" => "No Message Provided"`) |
| other (including initial `null`) | `Installation Incomplete` (type `warning`) |
| key missing | `Installation Returned Malformed Response` (type `warn`) |

`execute()` returns `0` after every callout, failure included.

`NewApplicationCommandTest` runs `execute()` whole: `PATH` set to a private directory holding a stand-in `composer` script (or nothing), callouts read from `Prompt::fake()`. Three cases: composer missing, create-project succeeds, create-project fails. The runs are non-interactive, so the extension step ends at its offer; its paths are covered in [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow).[^command-test]

The constructor takes optional `ComposerProjectCreator` and `Filesystem`; `execute()` uses neither (creation runs inside `ProjectCreationNode`).

## Related

- [Node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration)
- [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow)
- [ResolveDirectory](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/resolvedirectory)
- [PrepareSharedBag](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/preparesharedbag)
- [Playbook: new application](/docs/{{version}}/ecosystem/venusianphp-packages/installer/playbooks/new-application)

[^command]: NewApplicationCommand
[^flow-test]: Pest coverage for the nodes the command wires
[^resolve-test]: Pest coverage for the name → directory step
[^command-test]: Pest coverage for execute(), end to end
