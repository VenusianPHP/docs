# Guards and errors

Checks run before every Box2D call, how Box2D assertions become exceptions, and the stepping-world allowlist.

## Before Box2D

- Id live (index + generation) → else `ValueError`. World id from another PHP thread (ZTS) → `Error`.[^guards]
- Def `internalValue` must be Box2D's cookie (made by `b2Default*Def()`) → else `ValueError`, nothing created.
- Narrow ints range-checked; counts inside list length.

## Assertions

`B2_ENABLE_ASSERT` on in every build. Handler records first failure per thread (condition, file, line), returns 0 so Box2D never traps. Binding checks after each call → `b2AssertionError`. Pool-thread failures are copied to the world and thrown after `b2World_Step`.

## Stepping world

During W's `b2World_Step`, callbacks may call anything not bound to W, other worlds, and on W only the fields Box2D does not write in a step (IsValid family, shape body/world/type/sensor/user data/filter/density/friction/restitution/material, body type/user data/name/world, world user data). Else `Error("world is stepping")`.[^guards]

## Callback errors

No callback runs while an exception is pending. Exception in a callback → that callable gives Box2D's default for the rest of the step; rethrown after the call. Bad return type → `TypeError`.

[^guards]: id, def, count, stepping and owner checks
