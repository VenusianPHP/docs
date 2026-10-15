# Host

The machine the installer runs on and the PHP binary running it — binary path, OS family, loaded extensions, home, executable lookup, download.

## Role

Everything [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) asks of the machine that is not a process. Not final: `FakeHost` extends it and answers from its constructor arguments.[^host][^fake]

## Behavior (tested)

| Method | Result |
|---|---|
| `phpBinary()` | `PHP_BINARY` |
| `osFamily()` | `PHP_OS_FAMILY` |
| `loaded($extension)` | `extension_loaded()` in the running process |
| `home()` | `HOME`; `null` when unset or empty |
| `find($name, $extra_directories)` | Symfony `ExecutableFinder`: `PATH`, then the extra directories; `null` on a miss |
| `download($url, $path)` | Creates the directory, copies the URL to the path, `chmod 0755`. `false` on any I/O failure, and no file is left |
| `remove($path)` | Deletes the file |
| `releases($package)` | Versions Packagist lists (`repo.packagist.org/p2`, tagged file then `~dev` file), leading `v` stripped; `[]` on 404; `null` when Packagist cannot be asked. No Pest test: the suite uses no network, `FakeHost` overrides it |

The first seven: `tests/HostTest.php`. `download()` is tested with a `file://` URL; no test fetches over the network.[^host-test]

## Related

- [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow)
- [ProcessRunner](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/processrunner)

[^host]: Host
[^host-test]: Pest coverage for every method
[^fake]: The test double
