# Companion provider (not Voyager domain)

probe keeps Venusian\Probe\ProbeServiceProvider and discovers via composer extra.venusian.providers — not a Voyager component.

## Rule

`venusian/probe` is a **companion** to `venusian/framework` 0.11, not a Voyager component under `Voyager\*`.[^composer]

Therefore:

1. It **owns** `Venusian\Probe\ProbeServiceProvider` in this package.[^provider]
2. Discovery uses Composer `extra.venusian.providers`, read by the app's `PackageManifest` on `package:discover`.[^composer]
3. Provider stays here, never in framework `DefaultProviders`.

## Related

- [Package](/docs/{{version}}/ecosystem/venusianphp-packages/probe/orientation/package)
- [ProbeServiceProvider](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probeserviceprovider)

[^composer]: extra.venusian.providers
[^provider]: ProbeServiceProvider
