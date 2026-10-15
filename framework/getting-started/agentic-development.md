# Agentic Development

The Open Knowledge Format bundles and agent guidelines Venusian ships, how a coding agent should read them, and the commands an agent can use to inspect your application.

## Introduction

AI coding agents like [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenCode](https://opencode.ai), [Cursor](https://cursor.com), and [GitHub Copilot](https://github.com/features/copilot) can generate features, debug issues, and refactor code quickly, but their output depends on how well they understand your codebase.

Venusian gives agents that understanding in plain files. Every new application ships an Open Knowledge Format (OKF) knowledge bundle in its `.okf/` directory, and the framework, Probe, the installer, and the build tool each keep their own bundle in their source repositories. There is no extra package to install and no server to run: an agent reads markdown.

### Why Venusian for Agentic Development?

A Venusian application has a fixed shape. Sketches live in `app/Runner/Sketches` and run with `php rocket`, commands run with `php computer`, configuration lives in `config/`, and services come from the [service container](/docs/{{version}}/framework/architecture-concepts/container) rather than facades. When an agent needs to add a sketch or a migration, the location and naming are predictable.

The bundles add what the file layout cannot say on its own: how the event loop turns, which drivers exist, what each Composer hook does, and the step-by-step procedures for common changes. Every claim in a bundle cites the source file it came from, so an agent can check the claim before acting on it.

## Knowledge Bundles

An OKF bundle is a directory of markdown files with YAML frontmatter that humans and agents both read. Each bundle has three kinds of file:

- `index.md` - the entry point. It declares the format version (`okf_version`) and links every concept with a one-line summary.
- Concepts - one topic per file. The frontmatter carries a `type`, `title`, `description`, `tags`, a `status`, and a `sources` list naming the files the concept was written from; the body cites those sources in footnotes.
- `log.md` - the bundle's changelog: dated entries marked **Creation**, **Update**, **Correction**, or **Verification**.

A concept's `status` says how far to trust it. `stable` concepts have been checked against the code, and may carry a `verification_key` naming the agent and commit that checked them. `draft` concepts were written or changed by an agent and have not yet been verified by a human. `deprecated` concepts are historical.

### The Application Bundle

When you create an application with `venusian new` or `composer create-project venusian/venusian`, the skeleton's `.okf/` directory comes with it. It describes your application, not the framework, and is meant as a seed you extend as the application grows:

| File | Covers |
| ---- | ------ |
| `index.md` | Entry point linking every file below. |
| `overview.md` | What the application is, PHP requirements, the Composer hooks that write `.env`, `APP_KEY` and `database/database.sqlite`, and the first commands to run. |
| `structure.md` | The directory layout, the `computer` and `rocket` binaries, autoloading, and Composer hooks. See [Directory Structure](/docs/{{version}}/framework/getting-started/directory-structure). |
| `configuration.md` | How `config/*.php` overrides the framework defaults, and the `.env` keys. See [Configuration](/docs/{{version}}/framework/getting-started/configuration). |
| `sketches.md` | How `php rocket <sketch>` boots a sketch and calls `loop()` every frame until it stops. See [Sketches](/docs/{{version}}/framework/the-basics/sketches). |
| `playbooks/` | Step-by-step procedures for the application. |
| `log.md` | Changes to the bundle. |

### Playbooks

Playbooks are procedures an agent can follow step by step. These are the playbooks the Venusian bundles ship:

| Bundle | Playbook | Procedure |
| ------ | -------- | --------- |
| Application | `playbooks/creating-a-sketch.md` | Write a sketch class, run it with `php rocket`, and test it. |
| Installer | `playbooks/new-application.md` | Run `venusian new` and turn off its update check. |
| Installer | `playbooks/local-development.md` | Work on the installer from a checkout: Pest, `php bin/venusian`, path repositories. |
| Probe | `playbooks/require-probe.md` | Require Probe with Composer and let package discovery register it. |
| Probe | `playbooks/use-probe.md` | Run the REPL, execute code, and publish Probe's configuration. |

> [!NOTE]
> The application's `creating-a-sketch.md` playbook still says there is no `make:sketch` command. Since framework 0.10.5, `php computer make:sketch` generates the class for you; the run and test steps are unchanged.

### Package Bundles

The framework, Probe, the installer, and the build tool each keep a bundle at the root of their repository. These describe the package itself: the framework's bundle covers the event loop, loop mail, worker pools, Signals, logging, cache, Redis, queues, broadcasting, concurrency, processes, workflows, hashing, encryption, the database layer and [Instrument](/docs/{{version}}/framework/instrument-orm/instrument), the HTTP client, and packaged mode.

These bundles are excluded from the Composer dist archives through `export-ignore` in each package's `.gitattributes`, so they are not in your `vendor` directory after a normal install. Read them in the package's repository under [github.com/VenusianPHP](https://github.com/VenusianPHP), or install from source so Composer clones each repository whole:

```shell
composer install --prefer-source
```

## Agent Guidelines

The installer, Probe, and the build tool each ship an `AGENTS.md` at their repository root. It tells an agent how to use the package's bundle and lists the package's rules: version, PHP constraint, namespaces, dependencies, and how its tests run. Like the bundles, these files are excluded from the dist archive.

The rules for reading a bundle are the same in each `AGENTS.md`, and apply to your application's bundle too:

1. Read `.okf/index.md` first.
2. Open only the concepts the task needs.
3. Prefer `stable` concepts, and treat `deprecated` ones as historical.
4. Keep the bundle at the package root; do not nest `.okf` directories under `app/`, `src/`, or `tests/`.
5. Keep knowledge in the bundle it belongs to: framework knowledge lives in the framework's bundle, not your application's.

The application skeleton does not ship an `AGENTS.md`. If your agent reads an instruction file, add one to your application with these rules.

## Keeping Your Bundle Current

No command creates or updates a bundle; you and your agent edit the files directly. When you learn something durable about your application, update the concept it belongs to, or add a concept and link it from `index.md`, then append a dated entry to `log.md`:

```markdown
## 2026-10-12

* **Update**: [Configuration](/docs/framework/getting-started/configuration) — `APP_ID` added to `.env.example`.
```

List the files a concept was written from in its `sources` frontmatter and cite them in footnotes, so the next reader can check the claim. Leave a concept an agent wrote at `status: draft` until a human has verified it.

### Excluding the Bundle From Deploys

The skeleton does not `export-ignore` its bundle, so `.okf/` stays in your development clone. To keep it out of `git archive` and other export archives you deploy from, add this line to your application's `.gitattributes`:

```gitattributes
/.okf export-ignore
```

## Inspecting Your Application

Beyond the bundle, an agent can ask the application itself. To see the environment, cache state, drivers, event loop settings, extensions, and sketches as JSON:

```shell
php computer about --json
```

To list every Computer command, or every registered sketch:

```shell
php computer list
php rocket list
```

To run a line of PHP inside the booted application with [Probe](/docs/{{version}}/framework/digging-deeper/computer#probe-repl), without opening the interactive shell:

```shell
php computer probe --execute="echo config('app.name');"
```

To run the test suite:

```shell
composer test
```
