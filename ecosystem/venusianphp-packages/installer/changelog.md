# Changelog

What changed in this package, newest first.

### 2026-10-14

* **Docs audit** against `VenusianPHP/installer` `0.10.3` (`d581c42`): version 0.10.2 → 0.10.3 in [Package](/docs/{{version}}/ecosystem/venusianphp-packages/installer/orientation/package) and [Application](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/application); `bin/venusian` registers `new`, `install:ext`, `install:sdk` plus `venusian-tool` commands; require constraints; `InstallerPackage::BUILD` in [Enums](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/enums); overview points at `build.json`, not the removed `config/build.php`.

### 2026-10-08

* **Creation**: [InstallSdkCommand and ToolCommands](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/installsdk) — `install:sdk` runs `composer global require venusian/build`; `bin/venusian` adds the commands of every installed `venusian-tool` package (`extra.venusian.commands`), which is how `venusian build` appears. `InstallerPackage::BUILD`. `status: draft`.

### 2026-10-04

* **Update**: [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) — an extension with no 0.10 tag installs from `0.10.x-dev`; `extension_tokens`.
* **Creation**: [InstallExtensionCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/installextensioncommand) — `install:ext {ext?}` over all eleven `FirstPartyExtension` cases. `status: draft`.
* **Update**: [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow) — catalog / `ask` / `preselect` / `extension_only`, Packagist release state, non-interactive rules, error containment. [enums](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/enums) — eight more cases, `offeredByNew()`, `named()`, `package()`, `line()`. [Host](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/host) — `releases()`.
* **Creation**: [ExtensionsFlow](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/extensionsflow), [Host](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/host), [ChecklistPrompt](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/checklistprompt), [SummarizeExtensions](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/summarizeextensions) — the extension step `new` runs after create-project. `status: draft`.
* **Update**: [Node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration) — fourth node `ExtensionsFlow`; rule "named actions, null stops"; finder returns `create-project`, creation returns `offer-extensions`; new bag keys.
* **Update**: [enums](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/enums) — `FirstPartyExtension`, `PiePackage`. [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand) — `rtrim` on `name`, success callout carries extension outcomes, `execute()` covered by `NewApplicationCommandTest`. [ProcessRunner](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/processrunner) — second caller. [New application](/docs/{{version}}/ecosystem/venusianphp-packages/installer/playbooks/new-application) — extension step. [Local development](/docs/{{version}}/ecosystem/venusianphp-packages/installer/playbooks/local-development), [package](/docs/{{version}}/ecosystem/venusianphp-packages/installer/orientation/package) — 15 files, 81 `it()` cases, 27 source files.
* **Verification**: updated concepts re-checked against the tree; `verification_key` `claude-fable-5-1@6689f865c8b40863d13dc520135c0217579d3224`.

### 2026-09-30

* **Update**: Bundle retargeted to **0.10.0** — skeleton pin `venusian/venusian:^0.10.0` in [package](/docs/{{version}}/ecosystem/venusianphp-packages/installer/orientation/package), [node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration), [ComposerProjectCreator](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/composerprojectcreator), [enums](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/enums), [new application](/docs/{{version}}/ecosystem/venusianphp-packages/installer/playbooks/new-application) (now lists what the skeleton's hooks do).
* **Update**: [Application](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/application) — `ApplicationTest` covers `doRun` order and arguments; `bin/venusian` section with `BinaryTest`. [Local development](/docs/{{version}}/ecosystem/venusianphp-packages/installer/playbooks/local-development) — 9 files, 36 `it()` cases.
* **Update**: Facts from the removed pages folded into their components — `USER_AGENT` literal ([enums](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/enums)), update-failure and PATH-miss messages ([PackagistReleaseWatcher](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/packagistreleasewatcher)), unused constructor arguments and `execute()` returning 0 ([NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand)), `actions` unwritten ([PrepareSharedBag](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/preparesharedbag)).
* **Removal**: `traps/stale-branding.md`, `traps/release-watcher-network.md`, `known-gaps.md`.
* **Verification**: every remaining concept re-checked against the tree; `verification_key` `claude-opus-5-5@1ce46f6f838641a45ffe4ab85272ad821b312ecd`.

### 2026-08-23

* **Initialization**: Created OKF v0.2 bundle for `venusian/installer` **0.8.0** — orientation, PocketFlow node orchestration, components (`new` / creator / process runner / release watcher / resolve-directory / prepare-shared-bag / enums / application), new-application and local-development playbooks, stale-branding and release-watcher-network traps, known-gaps. All concepts `status: draft` pending human verification.
* **Note**: Source pin is `SkeletonPackage::VENUSIAN = venusian/venusian:^0.8.2`. `AGENTS.md` at `693b56c` already matches. Do not rewrite the enum to `^0.8.0`.
* **Note**: `PackagistReleaseWatcher` and `InstallerPackage::USER_AGENT` still emit ScrapyardIO / `scrapyard-io` literals. Recorded in `traps/stale-branding.md` (removed 2026-09-30), not presented as intended product copy.
* **Agent verification (framework-auditor)**: Tree-checked at `693b56c0cf3a622988e1f7b8147370aec9ba492f`.
  * `verification_key`: `agent:framework-auditor@693b56c0cf3a622988e1f7b8147370aec9ba492f`
  * `verified`: `{ by: agent:framework-auditor, at: 2026-08-23T17:31:14Z }`
  * Verified concepts set to `status: stable` (OKF v0.2: verified ⇒ stable). No `human:` stamp.
  * Corrections: `trim` vs `rtrim` on `new` name; skip-env `true` and WARN line are source-only; only `USER_AGENT` is Pest-pinned; `.gitattributes` measured list; `CHANGELOG.md` and `docs/` (canvas + mermaid) absent; Pest map 7 files / 33 `it()`; CI PHP 8.4/8.5.
* **Unchanged (measured true)**: package `venusian/installer` `0.8.0`, PHP `^8.4|^8.5|^8.6`, bin `bin/venusian`, ns `Venusian\Installer\`; skeleton `venusian/venusian:^0.8.2`; flow Start → ComposerFinder → ProjectCreation; `actions => []`; enums FULLY UPPERCASE; README `# Laravel Installer`; unused command ctor deps; `execute()` always `0`; Pest v4 (`^4`, resolved `v4.7.8` on the audit machine).
