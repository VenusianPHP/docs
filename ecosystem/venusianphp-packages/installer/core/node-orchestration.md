# Node orchestration

PocketFlow wiring for venusian new — Start → ComposerFinder → ProjectCreation → ExtensionsFlow over a shared bag; named actions, null stops.

## What it is

`new` builds a PocketFlow `Flow` and calls `run($shared)`. No plan → `$shared['actions']` → execute pipeline.[^command]

```
NewApplicationStartNode
        |  "find-composer"
        v
ComposerFinderNode ── miss: null, flow stops
        |  "create-project"
        v
ProjectCreationNode ── non-zero exit: null, flow stops
        |  "offer-extensions"
        v
ExtensionsFlow   (a Flow run as one node)
```

Wiring in `NewApplicationCommand::execute`:[^command]

1. `$start_node->next($finder_node, 'find-composer')`
2. `$finder_node->next($install_node, 'create-project')`
3. `$install_node->next($extensions_flow, 'offer-extensions')`
4. `new Flow($start_node)->run($shared)`

[ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) = the extension step, its own nodes inside.

## Rule: named actions, null stops

PocketFlow `Flow::get_next_node`: a `post()` return that is not a string is looked up as `'default'`. So:

* Every transition gets its own action name.
* A node stops the flow by returning `null`.
* No node has a `'default'` successor.

A `'default'` successor would run after a `null` return. `it fails without running create-project when composer is not on PATH` holds the finder to this.[^command-test]

## Shared bag

[PrepareSharedBag](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/preparesharedbag) seeds the bag.[^bag][^bag-test]

| Key | Initial | Who writes later |
|-----|---------|------------------|
| `success` | `null` | Finder miss → `false`. Creation `post` → `exit === 0`. The extension step never writes it. |
| `name` | `name` argument, trailing `/` `\` trimmed | — |
| `actions` | `[]` | No node writes it. |
| `interactive` | `$input->isInteractive()` | Read by `ExtensionOfferNode`. |
| `output_callback` | writes process buffer to `$output` | Passed through creation `prep`, PIE self-verify, `pie install`. |
| `directory` | unset | Start `post`. |
| `composer_binary` | unset | Finder `post` on hit. |
| `errors` | unset | Finder miss or creation failure. |
| `extension_*`, `extensions_*`, `php_config`, `pie_binary` | unset | [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow). |

## Node contracts (tested)

### NewApplicationStartNode::post

Sets `$shared['directory']`, returns `'find-composer'`.[^start][^flow-test]

### ComposerFinderNode::post

- Hit: sets `$shared['composer_binary']`, returns `'create-project'`.[^finder][^flow-test]
- Miss: `$shared['success'] = false`, `$shared['errors'] = ['composer' => 'Could not find the composer executable.']`, returns `null`. Creation does not run.[^finder][^flow-test][^command-test]

`exec()` calls `new ExecutableFinder()->find('composer')`, not injected. Node tests drive `post()` with a synthetic `$exec_res`; the command test points `PATH` at a private directory.

### ProjectCreationNode::prep

Builds:[^create][^flow-test]

```
[
  composer_binary,
  'create-project',
  'venusian/venusian:^0.10.0',
  directory,
  '--remove-vcs',
  '--prefer-dist',
]
```

plus a `Process` factory and the shared `output_callback`. `it creates the application and reports that extensions are not offered on a non-interactive run` reads these arguments back from a stand-in `composer`.[^command-test]

### ProjectCreationNode::post

`$shared['success'] = ($exec_res->getExitCode() === 0)`.[^create][^flow-test]

- Success: returns `'offer-extensions'`.
- Failure: `$shared['errors'] = ['message' => getExitCodeText(), 'code' => getExitCode()]`, returns `null`. The extension step does not run (`it does not reach the extension step when create-project fails`).[^command-test]

## Related

- [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow)
- [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand)
- [PrepareSharedBag](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/preparesharedbag)
- [ComposerProjectCreator](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/composerprojectcreator) — same argv shape, unused by this flow

[^command]: Flow construction in NewApplicationCommand::execute
[^bag]: Initial shared bag keys
[^start]: Start node post()
[^finder]: ComposerFinderNode post()
[^create]: ProjectCreationNode prep/post
[^flow-test]: Pest coverage for start / finder / creation nodes
[^command-test]: Pest coverage for the wired flow, end to end
[^bag-test]: Pest coverage for shared bag keys
