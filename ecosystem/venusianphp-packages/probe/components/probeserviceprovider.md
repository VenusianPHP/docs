# ProbeServiceProvider

Deferred Venusian provider that registers command.probe and merges/publishes probe config.

## Role

`Venusian\Probe\ProbeServiceProvider` registers the Computer command binding and merges `config/probe.php`.[^provider][^composer]

It implements `DeferrableProvider` and `provides()` → `['command.probe']`, so it loads when that binding (or command list path) needs it. Console bootstrap must call `loadDeferredProviders()` so deferred probe is available for `computer probe` / help listing.[^provider]

## 0.10 API

| Concern | Target |
|---------|--------|
| Base | `Voyager\NutsAndBolts\ServiceProvider` |
| Deferrable | `Voyager\Contracts\NutsAndBolts\DeferrableProvider`[^deferrable] |
| App handle | `$this->app` (not `$this->container` / `$this->program`)[^nab-sp] |
| Singleton | `$this->app->registerSingleton('command.probe', …)` |
| Container exception | `Voyager\Contracts\Vessel\DataBindingException` |

See [0.10 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/010-import-paths).

## Lifecycle

1. **register** — under rocket (`$this->app->isRocketRunning()`), nothing: probe stays off `rocket list`, and rocket's loop holds mail for a sketch, so a shell there would never see loop mail. Otherwise singleton `command.probe` → `ProbeCommand`; `$this->commands(['command.probe'])`.
2. **boot** — `mergeConfigFrom` probe config; `publishes` to app `configPath('probe.php')`, ungated. No About entry.
3. **provides** — `command.probe` for deferred loading (console kernel `loadDeferredProviders()` loads this before Computer commands, so `computer probe` resolves).

## Related

- [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand)
- [config/probe.php](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/config)
- [Companion provider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/conventions/companion-provider-not-voyager-domain)

[^provider]: ProbeServiceProvider
[^composer]: venusian.providers discovery
[^nab-sp]: Voyager ServiceProvider ($app)
[^deferrable]: DeferrableProvider contract
