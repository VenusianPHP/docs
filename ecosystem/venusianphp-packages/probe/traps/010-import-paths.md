# 0.10 import paths

0.8 → 0.10 map — Voyager\System gone; FrameworkCore contract, DataBindingException, signalsAreCached, venusian-voyager splits, about moved to Core.

## Map

0.10 has no `Voyager\System` namespace. Targets:[^core][^binding]

| Was (0.8) | Use (0.10) |
|-----------|------------|
| `voyager/*` / `venusian-voyager/*` `^0.8` | `venusian-voyager/*` `^0.10.0` |
| `Voyager\System\Application` | `Voyager\Contracts\Core\FrameworkCore` (concrete `Voyager\Core\RenderedInstance`)[^core] |
| `class_exists('Voyager\System\Application')` caster guard | Unguarded `FrameworkCore` key — contracts is required[^command] |
| `Voyager\System\Console\AboutCommand` | `Voyager\Core\Console\AboutCommand` (`about`, registered by `ComputerServiceProvider`). Probe 0.10 adds no About entry. |
| `Voyager\Contracts\Vessel\BindingResolutionException` | `Voyager\Contracts\Vessel\DataBindingException`[^binding] |
| `eventsAreCached()` | `signalsAreCached()`[^caster] |
| `Voyager\System\Console\Kernel` | `Voyager\Core\Console\Kernel`[^console-kernel] |

## Deferred load

`Kernel::bootstrap()` calls `loadDeferredProviders()` → deferred probe provider registers `command.probe` before Computer lists or runs commands.[^console-kernel]

## Related

- [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider)
- [ProbeCaster](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecaster)
- Historical [0.8 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/08-import-paths)

[^core]: FrameworkCore
[^binding]: DataBindingException
[^console-kernel]: bootstrap loadDeferredProviders
[^command]: getCasters
[^caster]: ProbeCaster
