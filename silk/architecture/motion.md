# Motion

Every animated value is a damped spring solved in closed form, with four presets; appear transitions run after paint; a theme switch blends live.

## Springs

A spring is (value, velocity, target) stepped with the exact solution, so it does not depend on the frame rate; retargeting is free. A spring is at rest when |value − target| ≤ 0.0015 and |velocity| ≤ 0.02, and a new spring starts on its target: no animation on appearance.[^spring] Raven's four motions:[^preset]

| Preset | Period (s) | Damping | Used for |
|---|---|---|---|
| Snappy | 0.16 | 0.90 | hover, highlights, caret glide, press down |
| Smooth | 0.30 | 1.00 | scrolling, fades, sizes, scrollbar fade |
| Bouncy | 0.38 | 0.52 | switches, popups, press release, tooltips |
| Wobbly | 0.50 | 0.32 | fly-ins, drops |

A [look](/docs/{{version}}/silk/architecture/looks)'s `Motion` is `Springy` (Raven's) or `Smooth` (the platform families: press release takes Snappy, nothing squashes, a tooltip fades Smooth — popups still grow out on Bouncy, drops and the node-wire sway stay Wobbly).

## Stepping

`FrameClock` turns the real gap since the last frame (0.001..0.25 s) into equal steps of at most 1/30 s; `Tree::advance(dt)` steps every moving spring, marks its widget for paint and reports whether anything still moves. After `advance()`, `Tree::needsPaint()` is how the [frame loop](/docs/{{version}}/silk/architecture/hosts) keeps painting while a spring moves, and stops when none does.

## Transitions

`Transition` kinds: Fade, Pop, Zoom, FlyUp, FlyDown, FlyLeft, FlyRight, Drop, SlideLeft, SlideRight. A widget's `appear()` / disappear transition runs as an `Appear` — a 0..1 spring applied after paint, so layout never moves; `paintExtent()` grows to cover it.

## Theme switches

`Tree::setLook()` starts a `LookBlend`: colours go from the old look to the new by the spring's value; metrics, fonts and part numbers are the new look's at once, because they move layout. With reduced motion ([`silk.reduced_motion`](/docs/{{version}}/silk/api/config), set on the tree by the host) every spring lands at once and a switch is assigned outright.

[^spring]: Class docblock of Spring (Raven anim.c).
[^preset]: src/Silk/Core/Motion/SpringPreset.php, Spring.php, FrameClock.php, LookBlend.php.
