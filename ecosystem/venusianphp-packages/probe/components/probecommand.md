# ProbeCommand

Computer console command probe — PsySH REPL with casters, aliases, and optional execute.

## Role

`Venusian\Probe\Console\ProbeCommand` is the Computer command named `probe`. It boots a PsySH shell against the Venusian application container.[^command]

## Surface

| Piece | Detail |
|-------|--------|
| Name | `probe` |
| Description | Interact with your application |
| Argument | `include` (array) — files to include before the shell |
| Option | `--execute=` — run code non-interactively |
| Container exception | `Voyager\Contracts\Vessel\DataBindingException`[^binding] |
| App accessor | `getVenusian()` |

## Behavior (high level)

1. Build PsySH `Configuration` from input; disable update checks (`Checker::NEVER`).
2. `trust_project` from `config('probe.trust_project')`.
3. `use_pcntl` from `config('probe.use_pcntl')` — **default false** (hardware-safe).[^config]
4. Register [ProbeCaster](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecaster) (and config `probe.casters`).
5. Register [ClassAliasAutoloader](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/classaliasautoloader) from Composer classmap + `probe.alias` / `probe.dont_alias`.
6. Pass through whitelisted Computer commands when registered (`clear-compiled`, `down`, `env`, `inspire`, `migrate`, `migrate:install`, `optimize`, `up`); resolve and add each class in `probe.commands`.
7. Interactive `run()` or `--execute` path (raw output; returns `1` on exception, else `0`); always unregister the alias loader.

## Related

- [ProbeCaster](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecaster)
- [ClassAliasAutoloader](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/classaliasautoloader)
- [pcntl trap](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/pcntl-hardware-fork)
- [Use probe](/docs/{{version}}/ecosystem/venusianphp-packages/probe/playbooks/use-probe)

[^command]: ProbeCommand
[^config]: probe config
[^binding]: DataBindingException
