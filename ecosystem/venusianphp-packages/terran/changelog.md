# Changelog

What changed in this package, newest first.

### 2026-10-14

* Docs audit against the published `VenusianPHP/terran-game-engine` `0.10.x` @ `5199fc5`: the slice 3b, 3c and 3e work below is not in that source, so its API (`Backdrop2D`, `Particles2D`, `Gradient`, `Tween`, physics drivers and nodes) was removed from [overview](/docs/{{version}}/ecosystem/venusianphp-packages/terran/overview), [scenes](/docs/{{version}}/ecosystem/venusianphp-packages/terran/scenes) and [physics](/docs/{{version}}/ecosystem/venusianphp-packages/terran/physics) until it is published; `ScenePrimitives` registers 18 Terran slugs.

### 2026-10-11

* Slice 3e (not in the published source yet): the box2d driver inside terran (`Terran\Physics\Box2D`), picked by `auto` with ext-box2d loaded; the behaviour tests run on both drivers. [physics](/docs/{{version}}/ecosystem/venusianphp-packages/terran/physics)
* Slice 3c (not in the published source yet): 2D physics: `PhysicsDriver`, `PhysicsManager`, the php driver, `PhysicsBridge`, `World::physics()`, Godot's physics nodes and shapes. [physics](/docs/{{version}}/ecosystem/venusianphp-packages/terran/physics)

### 2026-10-10

* Slice 3b (not in the published source yet): `Colors`, `Gradient` + `bake()`, `Scene2D::screenSpace()`, `Backdrop2D`, `Particles2D`, `Tween` + `Scene::tween()`, sprite `filter`, `Shape2D::polyline()`; `backdrop2d` and `particles2d` slugs. [scenes](/docs/{{version}}/ecosystem/venusianphp-packages/terran/scenes)
* Slice 3: math, assets, 2D/UI/3D primitives, Viewport passes and cameras, UI-first input walk, `ScenePrimitives` and `make:scene:<slug>`. [scenes](/docs/{{version}}/ecosystem/venusianphp-packages/terran/scenes)

### 2026-10-09

* Slice 2b: `Seats` over each frame's pad listing (hardware id key, reservations, namesake rule, takeover, lobby `assign()`/`release()`, player lights), per-seat `InputMap`/`PhysicsLatch` views, seat on pad and action events, `actions(?int $seat)`, config `seats` / `keyboard_seat` / `seat_on_connect`. [input](/docs/{{version}}/ecosystem/venusianphp-packages/terran/input).
* `terran.stager` (`TERRAN_STAGER`): the stager every staged target opens through unless its `options.toolkit` names one; null leaves Surface's default. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
* Slice 2a: fixed-step accumulator with `max_physics_steps`, hook passes and the `until()` guard, `World::async()`, Interrupts, Autoloads, Viewport re-mint on resize and `toPixels()`. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
* Slice 2a input: `InputReader`, events, `InputMap`, `PhysicsLatch`, `Scene::input()` / `actions()`. [input](/docs/{{version}}/ecosystem/venusianphp-packages/terran/input).

### 2026-10-08

* Slice 1: package scaffold; `GameEngine` (sketch `game`), `GameLoop` over `'event-loop'`, `World`, `Viewport`, `Scene` with five hooks, `TargetOpener` with `staged` / `canvas` / `display`, `config/terran.php`. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
* Staged windows join their toolkit session to the loop; `OwnedTarget::alive()` stops the engine on a closed window. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
