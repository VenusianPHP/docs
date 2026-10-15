# Package

venusian/installer 0.10.2 — global Composer CLI that scaffolds Venusian PHP applications.

## What it is

Composer package `venusian/installer` at **0.10.2** — a globally installable Symfony Console CLI (not a full Symfony HTTP app) whose bin is `bin/venusian`. Successor of `scrapyard-io/installer`.[^composer][^bin]

| Field | Value |
|-------|-------|
| Name | `venusian/installer`[^composer] |
| Version | `0.10.2`[^composer] |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Venusian\Installer\` → `src/`[^composer] |
| Bin | `bin/venusian`[^composer][^bin] |
| Role | Scaffold a Venusian app via `composer create-project`, then offer the first-party PHP extensions through PIE |
| Skeleton | `venusian/venusian:^0.10.0` (`SkeletonPackage::VENUSIAN`)[^skeleton][^enums-test] |

`.gitattributes` marks `/tests`, `/phpunit.xml`, `/.github`, `/.okf`, `/AGENTS.md`, `/CHANGELOG.md` `export-ignore`. No `CHANGELOG.md` in the tree.

## Requires

| Package | Constraint |
|---------|------------|
| `laravel/prompts` | `^0.3` |
| `projectsaturnstudios/pocketflow-php` | `^0.2` |
| `symfony/console` | `^7.0\|^8.0` |
| `symfony/filesystem` | `^7.0\|^8.0` |
| `symfony/process` | `^7.0\|^8.0` |

Does **not** require `venusian/framework` or `venusian/probe`.[^composer]

## What it is not

- Not a Voyager domain under `src/Voyager/*`. Framework architecture belongs in `venusian/framework` OKF.
- Not the PsySH REPL. That is `venusian/probe` (`computer probe`).
- Not the application skeleton. `new` installs `venusian/venusian:^0.10.0`.[^skeleton][^enums-test]

## Key files

| Path | Role |
|------|------|
| `bin/venusian` | Console entry (`Application` 0.10.2 + `NewApplicationCommand`); version equals `composer.json` (`BinaryTest`) |
| `src/Console/Application.php` | `doRun` → Packagist self-update offer |
| `src/Console/Commands/NewApplicationCommand.php` | `new` flow host |
| `src/Enums/SkeletonPackage.php` | Skeleton Composer constraint |
| `src/Workflows/Extensions/` | `ExtensionsFlow` and its six nodes |
| `src/Enums/FirstPartyExtension.php` | The extensions offered, as `pie install` tokens |
| `src/Host.php` | The machine and the running PHP binary |
| `src/Prompts/` | `ChecklistPrompt`: multi-select with disabled rows |
| `tests/` | Pest v4 specs (`pestphp/pest` `^4` in `require-dev`) |

## Tree (measured at 6689f86)

| Item | Measured |
|------|----------|
| `src/**/*.php` | 27 files |
| `src/Enums/` | 5 backed enums, all cases FULLY UPPERCASE; no `const` in `src/` |
| `tests/**/*Test.php` | 15 Pest spec files, 81 `it()` cases; `tests/Fakes/` holds 2 test doubles |
| `tests/Pest.php` | Pest v4 bootstrap (`Mockery::close()` in `afterEach`) |
| `bin/` | `bin/venusian` only |
| Root docs | `README.md` (install, usage, mermaid flow, update opt-out), `SECURITY.md`, `AGENTS.md`, `CLAUDE.md` → `AGENTS.md` |
| CI | `.github/workflows/tests.yml` — PHP `8.4` and `8.5`, `vendor/bin/pest`, `actions/checkout@v7` |
| `composer.lock` | gitignored (`.gitignore`); CI runs `composer update` |

## Related

| Topic | Concept |
|-------|---------|
| Flow | [Node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration) |
| Extension step | [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) |
| Command | [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand) |
| Run it | [New application](/docs/{{version}}/ecosystem/venusianphp-packages/installer/playbooks/new-application) |

[^composer]: Package name, version, require, bin, autoload
[^bin]: CLI entrypoint
[^skeleton]: create-project skeleton pin
[^enums-test]: Pest coverage for skeleton and installer enums
