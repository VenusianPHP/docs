# Package

venusian/build 0.10.9 — the venusian-tool package that adds `venusian build` to the installer.

## What it is

| Field | Value |
|---|---|
| Name | `venusian/build` 0.10.9 (tag `v0.10.9`)[^composer] |
| Type | `venusian-tool`[^composer][^test] |
| PHP | `^8.4\|^8.5\|^8.6`; needs `ext-phar`, `ext-zip` |
| Namespace | `Venusian\Build\` → `src/` |
| Bin | none; `extra.venusian.commands` names `Venusian\Build\Console\BuildCommand`[^composer][^test] |
| Install | `venusian install:sdk` = `composer global require venusian/build --no-interaction` |

The installer's `bin/venusian` reads every installed package of type `venusian-tool` through `Composer\InstalledVersions::getInstalledPackagesByType()` and adds the classes under `extra.venusian.commands`. No package → no `build` command.

## Boundary

The framework ships no build code. This package reads the app's files itself (`build.json`, `config/app.php`, `app/Runner/Sketches`, `composer.lock`) and packs the phar in a child PHP. The framework's only part is packaged mode: where a phar-based app writes.[^command]

[^composer]: name, type, extra.venusian.commands
[^command]: BuildCommand
[^test]: declared command classes exist
