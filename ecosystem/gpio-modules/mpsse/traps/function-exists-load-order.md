# `function_exists` load order

Helpers skip definition when the name exists; first autoloaded definition wins.

## Symptom

An `mpsse_*` call behaves unlike this package’s wrap — or a redefinition / “missing helper” confusion appears when multiple packages define the same global name.

## Cause

Every helper is defined only when the name is free:[^helpers][^readme]

```php
if (! function_exists('mpsse_open')) {
    function mpsse_open(...): ?MPSSEContext
    {
        // ...
    }
}
```

Under the guard, **whichever package’s autoload files run first keeps the definition**. Composer `autoload.files` order depends on require graph / install order.[^composer]

## Mitigation

- Treat this package as the **canonical** `mpsse_*` helper source when present.[^readme]
- Avoid defining overlapping global `mpsse_*` helpers in application code or peer packages.
- Prefer calling `Microscrap\Bindings\MPSSE\MPSSE::*` directly when you must avoid global-name collisions entirely (same underlying API; fuller surface than the eight helpers).[^helpers]

## Related

* [Helpers → MPSSE → FTDI](/docs/{{version}}/ecosystem/gpio-modules/mpsse/architecture/helpers-mpsse-ftdi)
* [1:1 libmpsse wrap](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/11-libmpsse-wrap)

[^readme]: README note on function_exists guards
[^helpers]: function_exists guard pattern
[^composer]: Autoload files entry
