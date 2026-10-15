# ComposerProjectCreator

Builds and runs `composer create-project` for the Venusian skeleton with an injectable finder and process factory.

## Role

Standalone helper for `composer create-project`. The `new` flow currently duplicates the argv inside [ProjectCreationNode](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration) and does not call this class. Tests inject `executableFinder` and `processFactory`.[^creator][^creator-test]

## buildCreateProjectCommand

Given `$composerBinary` and `$directory`, returns:[^creator][^creator-test][^skeleton]

```
[$composerBinary, 'create-project', 'venusian/venusian:^0.10.0', $directory, '--remove-vcs', '--prefer-dist']
```

The skeleton token is `SkeletonPackage::VENUSIAN->value` (`venusian/venusian:^0.10.0`).

## create

1. `findComposer()` → `$executableFinder->find('composer')`.
2. If the finder returns `null`, throws `ComposerNotFoundException`.[^not-found][^creator-test]
3. Builds the command, runs it via `processFactory` with no cwd, forwards `$outputCallback($type, $buffer)` when the callback is not null.
4. Returns `$process->getExitCode()`, or `1` when the exit code is `null`.[^creator][^creator-test]

## Related

- [Enums](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/enums)
- [ProcessRunner](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/processrunner)
- [Node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration)

[^creator]: ComposerProjectCreator
[^skeleton]: SkeletonPackage::VENUSIAN
[^not-found]: ComposerNotFoundException message
[^creator-test]: Pest coverage for argv, missing composer, exit code, output callback
