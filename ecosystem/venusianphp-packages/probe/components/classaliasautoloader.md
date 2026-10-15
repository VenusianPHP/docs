# ClassAliasAutoloader

PsySH session autoloader that aliases short class names from the Composer classmap.

## Role

`Venusian\Probe\ClassAliasAutoloader` registers an SPL autoloader for the probe session. Typing a bare class basename in PsySH can resolve to a full FQCN via `class_alias`.[^loader]

## Rules

- Classes are read from `vendor/composer/autoload_classmap.php` (vendor dir from `COMPOSER_VENDOR_DIR`, else `basePath()/vendor`). Only namespaced classes are candidates; the first class seen for a basename wins.
- `probe.alias` prefixes are checked first and always allow aliasing, even for vendor classes.[^config]
- Otherwise classes whose file is under the vendor root are **not** aliased.
- `probe.dont_alias` prefixes exclude the remaining (non-vendor) matches.[^config]
- Only bare names (no `\`) trigger aliasing; namespaced lookups pass through. Each alias prints `[!] Aliasing 'X' to 'Full\X' for this Probe session.`
- Unregistered in `finally` / destructor after the shell exits.[^command]

## Related

- [config/probe.php](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/config)
- [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand)

[^loader]: ClassAliasAutoloader
[^config]: alias / dont_alias
[^command]: register / unregister lifecycle
