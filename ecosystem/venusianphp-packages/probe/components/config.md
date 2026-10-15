# Config

Publishable probe configuration — commands, aliases, trust_project, use_pcntl.

## Keys

| Key | Purpose | Default / env |
|-----|---------|----------------|
| `commands` | Extra Computer command classes available inside probe | `[]` |
| `alias` | Explicit namespaces/classes allowed to short-alias | `[]` |
| `dont_alias` | Namespaces/classes never aliased | `[]` |
| `trust_project` | PsySH project trust mode — accepts `"prompt"`, `"always"`, `"never"`, `true`, `false`, `null` | `env('PROBE_TRUST_PROJECT', env('TINKER_TRUST_PROJECT', 'always'))`[^config] |
| `use_pcntl` | PsySH process forking | `env('PROBE_USE_PCNTL', false)` — **keep false** for hardware[^config] |

`ProbeCommand` also merges optional `probe.casters` when present (custom caster map).[^command]

## Publish

`ProbeServiceProvider::boot()` always registers this file for publishing to the app `config/probe.php` (not gated on console), then merges it under the `probe` key. Publish with `computer vendor:publish --provider="Venusian\\Probe\\ProbeServiceProvider"`.

## Related

- [pcntl trap](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/pcntl-hardware-fork)
- [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider)

[^config]: probe.php
[^command]: config consumers
