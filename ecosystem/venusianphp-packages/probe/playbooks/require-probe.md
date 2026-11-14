# Require probe

Install venusian/probe 0.11 in a Venusian application on framework 0.11.

## Steps

1. In a Venusian application on framework **0.11**:

```bash
composer require venusian/probe:^0.11.0
```

2. Confirm Composer discovery lists the provider:

```json
"extra": {
  "venusian": {
    "providers": [
      "Venusian\\Probe\\ProbeServiceProvider"
    ]
  }
}
```

(Already declared by this package — the app’s package discovery / services manifest should pick it up.)[^composer]

3. Ensure console bootstrap loads deferred providers (`loadDeferredProviders()`), or `computer probe` will not see `command.probe`.

4. Optionally publish config:

```bash
computer vendor:publish --provider="Venusian\\Probe\\ProbeServiceProvider"
```

## Verify

- `composer show venusian/probe` reports `0.11.x` (or your lock).
- `computer list` / `computer probe --help` shows the probe command after deferred providers load.
- Class exists: `Venusian\Probe\Console\ProbeCommand`.

## Related

- [Use probe](/docs/{{version}}/ecosystem/venusianphp-packages/probe/playbooks/use-probe)
- [Companion provider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/conventions/companion-provider-not-voyager-domain)
- [0.10 import paths](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/010-import-paths)

[^composer]: Package require + venusian.providers
