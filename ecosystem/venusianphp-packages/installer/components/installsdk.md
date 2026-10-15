# install:sdk

`install:sdk` requires `venusian/build`; `bin/venusian` adds commands of installed `venusian-tool` packages. (`draft`)

`#[AsCommand(name: 'install:sdk')]`, registered in `bin/venusian`.[^command][^binary-test]

| Piece | Value |
|-------|-------|
| Runs | `<composer> global require venusian/build --no-interaction` through `ProcessRunner`; `composer` found by `Host::find()`[^command][^command-test] |
| Package | `InstallerPackage::BUILD` = `venusian/build` |
| Exit 0 | composer succeeded; prints "Run `venusian build` inside a Venusian app"[^command-test] |
| Exit 1 | composer missing (named), or composer failed (its output repeated)[^command-test] |

## Tool discovery

`ToolCommands::fromInstalled()` asks `Composer\InstalledVersions::getInstalledPackagesByType('venusian-tool')`, reads each package's `composer.json` at its install path, and returns the class names under `extra.venusian.commands` in package order; non-list or non-string entries are skipped.[^tools][^tools-test] `bin/venusian` adds each class that exists after `new`, `install:ext` and `install:sdk`.[^bin][^binary-test]

A package is a tool by `"type": "venusian-tool"` plus that `extra` block. venusian/build declares `Venusian\Build\Console\BuildCommand`, which is how `venusian build` appears after `install:sdk`.

[^command]: InstallSdkCommand
[^tools]: ToolCommands
[^bin]: discovery loop
[^command-test]: Pest coverage for execute()
[^tools-test]: Pest coverage for ToolCommands
[^binary-test]: Pest coverage for registration and discovery in bin/venusian
