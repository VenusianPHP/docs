# ResolveDirectory

Maps the `new` name argument to `.`, an absolute path, or `cwd + DIRECTORY_SEPARATOR + name`.

## Behavior (tested)

`ResolveDirectory::run(string $name): string`:[^resolve][^resolve-test]

| Input | Result |
|-------|--------|
| `'.'` | `'.'` (passthrough) |
| Absolute path (`Filesystem::isAbsolutePath`) | `$name` unchanged |
| Relative name | `getcwd() . DIRECTORY_SEPARATOR . $name` |

If `getcwd()` is `false`, the method returns `$name` unchanged. That branch is not in the Pest map.

## Related

- [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand)

[^resolve]: ResolveDirectory::run
[^resolve-test]: Pest coverage for passthrough and relative join
