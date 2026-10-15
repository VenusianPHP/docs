# ClassAliasAutoloader

PsySH session autoloader that aliases short class names from the Composer classmap.

## Role

`Venusian\Probe\ClassAliasAutoloader` registers an SPL autoloader for the probe session. Typing a bare class basename in PsySH can resolve to a full FQCN via `class_alias`.[^loader]

## Rules

- Vendor paths under the Composer vendor root are **not** aliased by default.
- `probe.alias` forces include (namespace/class prefixes).[^config]
- `probe.dont_alias` excludes matches.[^config]
- Only bare names (no `\`) trigger aliasing; namespaced lookups pass through.
- Unregistered in `finally` / destructor after the shell exits.[^command]

## Related

- [config/probe.php](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/config)
- [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand)

[^loader]: ClassAliasAutoloader
[^config]: alias / dont_alias
[^command]: register / unregister lifecycle
