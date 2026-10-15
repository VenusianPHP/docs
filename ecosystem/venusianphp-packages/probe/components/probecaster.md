# ProbeCaster

Symfony VarDumper casters for FrameworkCore, Collection, Stringable, HtmlString, and optional Instrument Model and ProcessResult.

## Role

`Venusian\Probe\ProbeCaster` supplies presenter casters so PsySH dumps of Voyager types show useful virtual properties.[^caster]

## Casters (0.10)

| Target | Method | Registration |
|--------|--------|--------------|
| `Voyager\Contracts\Core\FrameworkCore` | `castApplication` | Always. Interface key → VarDumper matches `RenderedInstance` and any other core[^command] |
| `Voyager\NutsAndBolts\Collection` | `castCollection` | Always |
| `Voyager\NutsAndBolts\DataObjects\Stringable` | `castStringable` | Always |
| `Voyager\NutsAndBolts\HtmlString` | `castHtmlString` | Always |
| `Voyager\Database\Instrument\Model` | `castModel` | When `class_exists` — Database not required[^command] |
| `Voyager\Process\ProcessResult` | `castProcessResult` | When `class_exists` — Process not required[^command] |

`castApplication` calls each of `configurationIsCached`, `environment`, `environmentFile`, `signalsAreCached`, `runningUnitTests`, `version`, `path`, `basePath`, `configPath`, `databasePath`, `storagePath`, `bootstrapPath`; skips nulls and throwers.[^caster]

`castModel`: attributes + relations + evaluated `$appends`. Hidden keys → protected prefix; visible (or everything not hidden when `$visible` empty) → virtual prefix. Hidden wins.[^caster]

## Related

- [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand)
- [0.8 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/08-import-paths)

[^caster]: ProbeCaster
[^command]: getCasters registration
