# `function_exists` load order

Helpers skip definition when the name exists; first autoloaded definition wins.

## Symptom

A `gpiod_*` call behaves unlike this package’s wrap — or a redefinition / “missing helper” confusion appears when multiple packages define the same global name.

## Cause

Every helper is defined only when the name is free:[^helpers-chip][^readme]

```php
if (! function_exists('gpiod_chip_open')) {
    function gpiod_chip_open(string $path): ?GPIOChip
    {
        return Chip::gpioChipOpen($path);
    }
}
```

Under the guard, **whichever package’s autoload files run first keeps the definition**. Composer `autoload.files` order depends on require graph / install order.[^composer]

## Mitigation

- Treat this package as the **canonical** `gpiod_*` helper source when present.[^readme]
- Avoid defining overlapping global `gpiod_*` helpers in application code or peer packages.
- Prefer calling facade classes directly (`Microscrap\Bindings\GPIO\Chip::*`, `LineRequest::*`, …) when you must avoid global-name collisions entirely (same underlying API).[^helpers-chip]

## Related

* [Helpers → gpiod facades → posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi)
* [1:1 libgpiod wrap](/docs/{{version}}/ecosystem/gpio-modules/gpio/conventions/11-libgpiod-wrap)

[^readme]: README note on function_exists guards
[^helpers-chip]: function_exists guard pattern
[^composer]: Autoload files entries
