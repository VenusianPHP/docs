# 0.8 import paths

Historical 0.7 → 0.8 import map. Superseded by 0.10 paths.

## Trap

0.7 wrench / Fabricate imports and `$this->container` break against Voyager 0.8. Prefer these targets:[^nab-sp][^deferrable][^binding]

| Was (0.7 wrench) | Use (0.8 probe) |
|------------------|-----------------|
| `ScrapyardIO\Wrench\` | `Venusian\Probe\` |
| `Fabricate\*` | `Voyager\*` |
| `$this->container` | `$this->app`[^nab-sp] |
| `getScrapyardIO()` | `getVenusian()` |
| `Fabricate\NutsAndBolts\Contracts\DeferrableProvider` | `Voyager\Contracts\NutsAndBolts\DeferrableProvider`[^deferrable] |
| `Fabricate\Chassis\Exceptions\BindingResolutionException` | `Voyager\Contracts\Vessel\BindingResolutionException`[^binding] |
| `Fabricate\Core\Machine` | `Voyager\System\Application` |
| `Fabricate\Core\Console\AboutCommand` | `Voyager\System\Console\AboutCommand` |
| Workshop binary | **computer** |
| Hard Process caster import | `class_exists('Voyager\Process\ProcessResult')`[^caster] |

## Deferred load

Console kernel bootstrap must call `loadDeferredProviders()` so the deferred probe provider actually registers `command.probe` before Computer lists/runs commands.[^console-kernel]

## Related

- [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider)
- [ProbeCaster](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecaster)
- Package [CHANGELOG.md](https://github.com/VenusianPHP/probe/blob/HEAD/CHANGELOG.md)
- Historical [0.7 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/07-import-paths)
- Current [0.10 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/010-import-paths)

[^nab-sp]: ServiceProvider::$app
[^deferrable]: DeferrableProvider
[^binding]: BindingResolutionException
[^console-kernel]: bootstrap loadDeferredProviders
[^provider]: Current provider
[^caster]: Casters (HtmlString / Process / Application)
