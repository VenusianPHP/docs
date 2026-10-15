# Package

venusian/probe 0.10.1 — PsySH REPL (Computer command probe) for Venusian applications.

## What it is

Composer package `venusian/probe` at **0.10.1** — a PsySH-based REPL exposed as the Computer console command `probe` for Venusian applications. Successor of `scrapyard-io/wrench`.[^composer][^command]

| Field | Value |
|-------|-------|
| Name | `venusian/probe` |
| Version | `0.10.1` (tag `v0.10.1`) |
| PHP | `^8.4\|^8.5\|^8.6`[^composer] |
| Namespace | `Venusian\Probe\` → `src/` |
| Role | REPL companion to `venusian/framework` 0.10 |
| Discovery | `extra.venusian.providers` → `Venusian\Probe\ProbeServiceProvider`[^composer] |

`.okf/`, `AGENTS.md`, `CHANGELOG.md`, and `tests/` are `export-ignore` from Composer dist.[^gitattributes]

## Requires

| Package | Constraint |
|---------|------------|
| `venusian-voyager/console` | `^0.10.0` |
| `venusian-voyager/contracts` | `^0.10.0` |
| `venusian-voyager/nuts-and-bolts` | `^0.10.0` |
| `psy/psysh` | `^0.12.0` |
| `symfony/var-dumper` | `^8.0` |

Components only, never the full framework. In an app, framework's root `replace` covers every `venusian-voyager/*` split → the three resolve to the framework itself, no second copy. `venusian/framework` is require-dev for tests.[^composer]

## What it is not

- Not a Voyager *domain* component under `src/Voyager/*`. It stays a companion package with its **own** service provider (see [companion provider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/conventions/companion-provider-not-voyager-domain)).
- Not a substitute for Computer itself — it *registers into* Computer via deferred `command.probe`.

## Key files

| Path | Role |
|------|------|
| `src/ProbeServiceProvider.php` | Deferred provider, config merge/publish |
| `src/Console/ProbeCommand.php` | PsySH shell + casters + aliases |
| `src/ProbeCaster.php` | Presenter casters |
| `src/ClassAliasAutoloader.php` | Short class aliases in session |
| `config/probe.php` | Commands, alias lists, trust, pcntl |
| `tests/` | Pest v4 specs ported from `laravel/tinker` |

## Related

| Topic | Concept |
|-------|---------|
| Provider | [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider) |
| Command | [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand) |
| Install | [Require probe](/docs/{{version}}/ecosystem/venusianphp-packages/probe/playbooks/require-probe) |
| 0.10 imports | [0.10 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/010-import-paths) |

[^composer]: Package name, version, require, autoload, venusian providers
[^readme]: Package README
[^gitattributes]: export-ignore for .okf, AGENTS.md, CHANGELOG.md, tests
[^command]: Computer probe command
[^provider]: ProbeServiceProvider entry
