# Changelog

What changed in this package, newest first.

### 2026-10-11

* Slice 3e: the box2d driver inside terran (`Terran\Physics\Box2D`), picked by `auto` with ext-box2d loaded; the behaviour tests run on both drivers. [physics](/docs/{{version}}/ecosystem/venusianphp-packages/terran/physics)
* Slice 3c: 2D physics: `PhysicsDriver`, `PhysicsManager`, the php driver, `PhysicsBridge`, `World::physics()`, Godot's physics nodes and shapes. [physics](/docs/{{version}}/ecosystem/venusianphp-packages/terran/physics)

### 2026-10-10

* Slice 3b: `Colors`, `Gradient` + `bake()`, `Scene2D::screenSpace()`, `Backdrop2D`, `Particles2D`, `Tween` + `Scene::tween()`, sprite `filter`, `Shape2D::polyline()`; `backdrop2d` and `particles2d` slugs. [scenes](/docs/{{version}}/ecosystem/venusianphp-packages/terran/scenes)
* Slice 3: math, assets, 2D/UI/3D primitives, Viewport passes and cameras, UI-first input walk, `ScenePrimitives` and `make:scene:<slug>`. [scenes](/docs/{{version}}/ecosystem/venusianphp-packages/terran/scenes)

### 2026-10-09

* Slice 2b: `Seats` over each frame's pad listing (hardware id key, reservations, namesake rule, takeover, lobby `assign()`/`release()`, player lights), per-seat `InputMap`/`PhysicsLatch` views, seat on pad and action events, `actions(?int $seat)`, config `seats` / `keyboard_seat` / `seat_on_connect`. [input](/docs/{{version}}/ecosystem/venusianphp-packages/terran/input).
* `terran.stager` (`TERRAN_STAGER`): the stager every staged target opens through unless its `options.toolkit` names one; null leaves Surface's default. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
* Slice 2a: fixed-step accumulator with `max_physics_steps`, hook passes and the `until()` guard, `World::async()`, Interrupts, Autoloads, Viewport re-mint on resize and `toPixels()`. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
* Slice 2a input: `InputReader`, events, `InputMap`, `PhysicsLatch`, `Scene::input()` / `actions()`. [input](/docs/{{version}}/ecosystem/venusianphp-packages/terran/input).

### 2026-10-08

* Slice 1: package scaffold; `GameEngine` (sketch `game`), `GameLoop` over `'event-loop'`, `World`, `Viewport`, `Scene` with five hooks, `TargetOpener` with `staged` / `canvas` / `display`, `config/terran.php`. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
* Staged windows join their toolkit session to the loop; `OwnedTarget::alive()` stops the engine on a closed window. [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine).
