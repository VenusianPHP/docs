# 0.7 import paths

Historical wrench 0.7 Fabricate import map. Superseded by 0.8 Voyager paths in venusian/probe.

## Historical (do not copy)

This trap described `scrapyard-io/wrench` **0.7** against Fabricate. Live 0.8 source uses Voyager / `$this->app` / Computer — see [0.8 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/08-import-paths).[^current]

| Was (0.6-ish) | Used (0.7 wrench) |
|---------------|-------------------|
| `$this->program` | `$this->container` |
| `Fabricate\Contracts\NutsAndBolts\DeferrableProvider` | `Fabricate\NutsAndBolts\Contracts\DeferrableProvider` |
| `Fabricate\Contracts\Chassis\BindingResolutionException` | `Fabricate\Chassis\Exceptions\BindingResolutionException` |
| Hard `HtmlString` caster import | Remove or `class_exists` — HtmlString not in 0.7 |
| Unguarded Process caster | `class_exists('Fabricate\Process\ProcessResult')` |

[^changelog]: 0.7.0 historical notes
[^current]: 0.8 import paths
