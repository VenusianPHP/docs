# Config

`config/silk.php`, published under the `silk-config` tag. Themes and looks are registered and switched through the container, never through files.

## Keys

| Key | Holds |
|---|---|
| `look` | the look every [tree](/docs/{{version}}/silk/architecture/tree) starts with (`raven-dark`) |
| `accent` | `auto` (the system's, when the toolkit reports one; otherwise the look's own), `system` (an error when the toolkit reports none), `theme` (the look's own, the system is not asked) or `custom` |
| `accent_color` | `'#RRGGBB'`, used when `accent` is `custom` |
| `scale` | UI scale, 0.25..4, multiplied by the window scale |
| `reduced_motion` | snap every [spring](/docs/{{version}}/silk/architecture/motion) to its target |
| `font.family` / `font.mono` | fontconfig families for the UI and monospace text |

There is no engine key: the engine is Surface's `drawing.default`, and `SILK_ENGINE` overrides it for one run. A GPU engine is always a manual choice — see [hosts](/docs/{{version}}/silk/architecture/hosts).

## Looks at runtime

`app('silk.looks')` is the LookManager: `extend(name, fn)` registers a theme, `use(name)` switches the active one and updates every watched tree live, `current()` answers it and `watch(tree)` starts watching. A theme is a PHP array or a `Theme` class — see [looks](/docs/{{version}}/silk/architecture/looks).

## Provider

`Silk\Core\Providers\SilkServiceProvider` is discovered through `extra.venusian.providers` and binds the `silk` singleton (host attach/detach), `silk.looks` and `silk.translator`. Publish with `php computer vendor:publish --tag=silk-config`.

[^config]: config/silk.php; src/Silk/Looks/LookManager.php; src/Silk/Core/Providers/SilkServiceProvider.php.
