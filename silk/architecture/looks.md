# Looks

A Look answers every colour, metric, font and part a widget paints; twelve themes ship built in; the accent follows the system; glass is a material, not a colour.

## The contract

A `Look` answers `color(Role)` (36 roles), `metric(Metric)` (20 metrics, including GlassFrost, GlassRefraction, GlassRim, GlassSaturation, GlassShadow), `font(FontRole)`, `motion()` (springy or smooth, see [motion](/docs/{{version}}/silk/architecture/motion)), `part(widget, part, State, classes): PartLook`, `dark()`, `darkTwin()`, `material()` and `liquid()`.[^contract] States: Normal, Hover, Pressed, Focused, Checked, Disabled, Selected. Widgets resolve what they paint from the look; a widget's own `setColor`, `setMetric` and classes resolve above it. Only the text colour inherits down the [tree](/docs/{{version}}/silk/architecture/tree); `LookScope` gives a subtree a look of its own.

## The twelve built-ins

`raven-dark` (the default), `raven-light`, `raven-high-contrast-dark`, `raven-high-contrast-light`, `macos-dark`, `macos-light`, `gnome-dark`, `gnome-light`, `raven-glass-dark`, `raven-glass-light`, `macos-glass-dark`, `macos-glass-light`.[^builtin] A theme is a PHP array (`look`, `accent`, `colors`, `metrics`, `font`, `motion`, `material`, `syntax`, `styles`) or a `Theme` class.

`app('silk.looks')` is the LookManager: `extend(name, fn)` registers a theme, `use(name)` switches the active one and updates every watched tree live, `current()` answers it and `watch(tree)` starts watching a tree.

## The style sheet

Styles are `[widget, class, part, state, props]`; a null widget, class or state matches any. Specificity: type 1, class 2, state 2; ties go to the last written.[^sheet] `ThemedLook` is a look built from a theme laid over its base (palette, metrics, style sheet).

## Accent

`Accent` derives the roles that follow the accent colour per family. The [`accent` config key](/docs/{{version}}/silk/api/config) picks its source: `auto` (the system's when the toolkit reports one), `system`, `theme`, `custom`.

## The glass material

`Material`: Solid, Glass (clear: barely tinted and blurred, a rim that bends like a lens), FrostedGlass, TintedGlass (frosted and coloured by the accent, stronger on what floats higher). A look whose material is glass paints its panels, controls, popups and bars as glass: `GlassStyle::of(look, SurfaceKind, hover, press, material)` answers the glass a kind of surface is in that look (tint, rim, frost, refraction, saturation, glow, bevel, shadow), tuned by the Glass* metrics. `SurfaceKind`: Control, Accent, Input, Bar, Panel, Popup, Lens. `Surfaces::paint` paints a surface as the look's glass, faded and shadowless when disabled. The glass is drawn by `Painter::glass()` ([painter](/docs/{{version}}/silk/architecture/painter)); glass looks need the backdrop under each pane, which is Surface's job.

[^contract]: src/Silk/Contracts/Look/Look.php, Role.php, Metric.php, PartLook.php, Material.php, State.php.
[^builtin]: src/Silk/Looks/BuiltInThemes.php; the roles, metrics and styles are the generated `src/Silk/Looks/tokens.php`.
[^sheet]: Class docblock of StyleSheet, src/Silk/Looks/ThemedLook.php, Accent.php, GlassStyle.php.
