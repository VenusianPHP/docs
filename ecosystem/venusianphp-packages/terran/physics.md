# Physics

Terran 2D physics: not in the published source yet.

## Status

The published `VenusianPHP/terran-game-engine` source (`0.10.x` @ `5199fc5`) has no physics code: no `Terran\Physics` namespace, no `PhysicsDriver`, `PhysicsManager` or `PhysicsBridge`, no physics nodes (`StaticBody2D`, `RigidBody2D`, `CharacterBody2D`, `Area2D`, …), and no `terran.physics` config. This page previously described that work (slices 3c and 3e in the [changelog](/docs/{{version}}/ecosystem/venusianphp-packages/terran/changelog)); it was removed until the code is published so the docs only describe what ships.

What ships today: the fixed-step physics *phase* on the `GameLoop` — `Scene::physicsProcess()` every `1 / terran.physics_hz` (`physics_hz` 60, `max_physics_steps` 8) and the input `PhysicsLatch`. See [engine](/docs/{{version}}/ecosystem/venusianphp-packages/terran/engine) and [input](/docs/{{version}}/ecosystem/venusianphp-packages/terran/input).

The C binding a box2d driver would use exists separately as [`php-io-extensions/box2d`](https://github.com/php-io-extensions/box2d).
