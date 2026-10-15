# ProcessRunner

Thin Symfony Process wrapper — run/succeeds/output with an injectable process factory.

## Role

Used by [PackagistReleaseWatcher](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/packagistreleasewatcher) for `composer global require` and re-exec, and by [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) for php-config, PIE and the load check. Constructor `processFactory` is injectable so tests never spawn a real process; the extension tests swap the whole runner for `tests/Fakes/FakeProcessRunner`.[^runner][^runner-test]

## Behavior (tested)

| Method | Result |
|--------|--------|
| `run(...)` | `$process->getExitCode()`, or `1` when the exit code is `null` |
| `succeeds(...)` | `true` iff `run(...) === 0` |
| `output(...)` | `trim($process->getOutput())` when exit code is `0`; `null` when exit code is `null` or non-zero |

`run()` forwards `$outputCallback` unless `inheritTty` is true **and** TTY attach succeeds. TTY attach (`canInheritTty` / `setTty`) has no Pest test; when it fails, `run()` falls back to the callback path. `pie install` runs with `inheritTty` so PIE can prompt for sudo.

## Related

- [PackagistReleaseWatcher](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/packagistreleasewatcher)
- [ComposerProjectCreator](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/composerprojectcreator)
- [Host](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/host)

[^runner]: ProcessRunner
[^runner-test]: Pest coverage for run / succeeds / output
