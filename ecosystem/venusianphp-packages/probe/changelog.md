# Changelog

What changed in this package, newest first.

### 2026-10-28

* **Update**: Bundle retargeted to **0.11.0** (`VenusianPHP/probe` `v0.11.0`, aligned with framework 0.11) — [Package](/docs/{{version}}/ecosystem/venusianphp-packages/probe/orientation/package) requires `venusian-voyager/*` `^0.11.0` and PHP `~8.4.27||^8.5.12`; [Require probe](/docs/{{version}}/ecosystem/venusianphp-packages/probe/playbooks/require-probe), [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider), [ProbeCaster](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecaster) and [Companion provider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/conventions/companion-provider-not-voyager-domain) versions.

### 2026-10-14

* **Update**: Docs audit against `VenusianPHP/probe` `v0.10.1` — version bumped to 0.10.1; [Config](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/config) publish is ungated; [ClassAliasAutoloader](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/classaliasautoloader) rule order; [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand) whitelist; [0.10 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/010-import-paths) — framework 0.10 now ships `about` in `Voyager\Core\Console`.

### 2026-10-07

* **Update**: [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider) — registers nothing when `isRocketRunning()`; About wording no longer claims 0.10 lacks `about`.

### 2026-09-30

* **Update**: Bundle retargeted to **0.10.0** — [Package](/docs/{{version}}/ecosystem/venusianphp-packages/probe/orientation/package) requires `venusian-voyager/*` `^0.10.0`; [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider) without About, `registerSingleton`, ungated publish; [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand) `DataBindingException`; [Companion provider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/conventions/companion-provider-not-voyager-domain), [Require probe](/docs/{{version}}/ecosystem/venusianphp-packages/probe/playbooks/require-probe).
* **Update**: [ProbeCaster](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecaster) — `castApplication` keyed on `FrameworkCore`, `signalsAreCached`; `castModel` for `Voyager\Database\Instrument\Model`.
* **Addition**: [0.10 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/010-import-paths). [0.8 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/08-import-paths) → `deprecated`.

### 2026-08-23

* **Update**: GitHub Actions Pest workflow (PHP 8.4/8.5) plus Dependabot for Actions; README tests badge points at `VenusianPHP/probe`.
* **Update**: Ported `laravel/tinker` tests to Pest v4 (`ClassAliasAutoloader`, `ProbeCaster`) with the tinker classmap fixtures.
* **Update**: Retargeted the bundle from `scrapyard-io/wrench` **0.7** to `venusian/probe` **0.8** — Wrench→Probe, ScrapyardIO→Venusian, Fabricate→Voyager, Workshop→computer, `$this->container`→`$this->app`. Concepts set `status: draft` pending human verification. Historical 0.7 import-path trap marked `deprecated`.

### 2026-08-07

* **Verification**: Angel marked all OKF concepts `status: stable` for 0.7.x publish prep (`verified` by `human:Angel Gonzalez (projectsaturnstudios)`). Index markers and AGENTS trust wording updated.
* **Update**: `WrenchServiceProvider::boot()` contributes to Workshop `about` — overrides Environment **Wrench Installed** from Core default `false`/`NO` to `true`/`YES` via `AboutCommand::add()`.
* **Update**: Applied 0.7 compatibility in source — `$this->container`, Nab `DeferrableProvider`, Chassis `BindingResolutionException`, HtmlString caster removed, Process caster untyped + `class_exists`, Machine caster drops `isLocal`, composer PHP/`branch-alias`/`suggest`, `WRENCH_TRUST_PROJECT`. App skeleton path-repo symlink for wrench.

* **Initialization**: Created OKF v0.2 bundle for `scrapyard-io/wrench` **0.7.0** — orientation, components (provider / command / caster / alias autoloader / config), companion-provider convention, pcntl + 0.7 import-path traps, require/use playbooks. All concepts `status: stable` pending human verification.
