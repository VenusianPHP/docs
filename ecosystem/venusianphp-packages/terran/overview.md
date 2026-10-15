# Overview

Godot-shaped game engine for Venusian Framework applications. Scenes in a tree, a World that owns it, one Viewport per output target. Physics ticks on the event loop at a fixed step; rendering ticks on the sketch at the refresh rate. Draws through Surface's rendering engines onto a staged window, a toolkit canvas or an embedded panel, and never names which.

## Install

```bash
composer require venusian/terran
php computer vendor:publish --tag=terran-config
```

Until the 0.10 `venusian-surface/*` splits publish, `composer.json` carries path repositories to the framework and surface checkouts beside this one.

## Run

```bash
php rocket game
```

Set `terran.main_scene` (or `TERRAN_MAIN_SCENE`) to a Scene class. The default target is a staged window, 960×540, on the Velvet software engine.

```php
use Terran\Scene;
use Surface\Contracts\Drawing\RenderingEngine;
use Surface\NutsAndBolts\Color;

final class Bounce extends Scene
{
    private float $x = 0.0;

    public function physicsProcess(float $delta): void { $this->x += 120 * $delta; }

    public function draw(RenderingEngine $ge): void { $ge->fillRect($this->x, 40, 40, 40, Color::hex('#FF8800')); }
}
```

## Hooks

| Hook | When |
|---|---|
| `ready()` | once, when the Scene's tree goes live |
| `physicsProcess(float $step)` | every fixed step on the GameLoop; `$step` is `1 / terran.physics_hz`, constant |
| `process(float $delta)` | every rendered frame, with the real frame delta |
| `input(InputEvent $event): bool` | every input event this frame, until a Scene returns true |
| `draw(RenderingEngine $ge)` | when a Viewport renders this Scene |
| `exit()` | once, when removed or the World is destroyed |

A step runs at most `terran.max_physics_steps` (8) times per advance; a longer stall is dropped, not replayed. A hook that waits on a promise throws; start I/O with `$this->world()->async(...)` and take the result in `->then()`.

## Interrupts

```php
#[Interrupt('hit', [Scene::class, 'int'])]
class Paddle extends Scene {}

$paddle->connect('hit', $score, 'onHit');   // or a callable: $score->onHit(...)
$paddle->emit('hit', $ball, 10);           // connections run; app('signals') hears terran.<path>.hit
```

Declarations inherit. A freed Scene's connections go with it, and connections to it are dropped.

## Autoloads

```php
#[Autoload(ScoreKeeper::class)]
class Level extends Scene { public function ready(): void { $this->autoload(ScoreKeeper::class)->reset(); } }
```

One instance per World, inherited by subclasses; `terran.autoloads` lists world-wide ones. A Scene class autoloads as a child of the root.

## Input

```php
// config/terran.php
'input' => ['actions' => ['jump' => ['key:space', 'pad:south'], 'left' => ['key:a', 'axis:left_x:-']]],

public function physicsProcess(float $delta): void
{
    if ($this->actions()->isPressed('jump')) { … }        // each tap reaches one step
    $this->x += 200 * $delta * $this->actions()->axis('left', 'right');
}
```

Bindings: `key:<Key>`, `mouse:<MouseButton>`, `pad:<GamepadButton>`, `axis:<GamepadAxis>:+|-[:dead zone]` (default 0.15), values as HumanInput's enums spell them. Terran reads HumanInput once a frame and only the devices the game uses: bound ones, plus `terran.input.events` (keyboard, mouse) while a live Scene overrides `input()`. Mouse event `x`, `y` and motion `dx`, `dy` are the Viewport's framebuffer pixels. A second binding going down under a held action is no new press.

### Seats

```php
'input' => ['seats' => 4, 'keyboard_seat' => 1, 'seat_on_connect' => true, …],

$p2 = $this->actions(2);                              // seat 2's pad only
$this->x += 200 * $delta * $p2->axis('left', 'right');
```

Pads take the lowest free seat as they connect and are lit as that player. A pad that leaves keeps its seat reserved and gets it back on reconnect: by hardware id, or by name for a pad with none. With no free seat a new pad takes over a reservation, else stays unseated (its presses carry seat null). Keyboard and mouse belong to `keyboard_seat`. `actions()` with no seat reads every source. Pad and action events carry `seat`. For a lobby set `seat_on_connect` to false and seat pads yourself with `app('terran.seats')->assign($seat, $event->pad)` / `release($seat)`. `seats` 0 turns seating off.

A Viewport whose target changes size re-mints its engine before drawing; a zero size skips the frame.

## Scenes

Primitives, as Godot's node types: extend them.

```php
$sheet = SpriteSheet::grid(Texture::load(base_path('assets/ship.png')), 4, 1);
$ship = new Sprite2D('ship', $sheet);
$ship->add((new Camera2D('camera'))->makeCurrent());     // the camera follows its parent

$hud = (new Panel('hud'))->setMargin(16, 16, 236, 150);
$stack = (new VBox('stack'))->setAnchor(Anchor::FULL_RECT)->setMargin(8, 8, -8, -8);
$button = new Button('start', 'START');
$button->connect('pressed', fn () => $this->begin());
$hud->add($stack->add($button));
```

| 2D | UI | 3D |
|---|---|---|
| `Scene2D`, `Sprite2D`, `AnimatedSprite2D`, `TileMap`, `Camera2D`, `Label2D`, `Shape2D`, `Backdrop2D`, `Particles2D` | `UIControl`, `Panel`, `Label`, `Button`, `ProgressBar`, `VBox`, `HBox` | `Scene3D`, `Camera3D`, `MeshInstance`, `DirectionalLight` |

The Viewport draws 2D Scenes by z through the current `Camera2D`, then UI in viewport pixels on top. 3D Scenes transform now and draw from slice 6. Mouse events reach UI controls under the pointer first; keys reach the focused control first; define `ui_next`, `ui_prev`, `ui_accept` actions for pad and keyboard menus. A subclass that overrides a hook calls the parent's.

Skies, weather and fades:

```php
$sky = new Backdrop2D('sky', Gradient::between(Color::hex('#2E6FD8'), Color::hex('#9CC8F0')));  // fills the viewport
$puff = Gradient::between(Color::hex('#FFFFFF'), Color::hex('#FFFFFF00'))->bake(96, 96, GradientFill::RADIAL);
$cloud = new Sprite2D('cloud', $puff);
$cloud->filter = Filter::LINEAR;

$rain = new Particles2D('rain');
$rain->shape = ParticleShape::STREAK;
$rain->amount = 300;
$rain->preprocess = 1.0;

$this->tween()->ease(Ease::IN_OUT)->property($sky, 'gradient', $night, 4.0);   // from a live Scene
```

```bash
php rocket make:scene Level                 # a plain Scene
php rocket make:scene:sprite2d Ship         # app/Scenes/Ship.php extends Sprite2D
php rocket make:scene:button StartButton
```

A package adds its own primitive, and gets its `make:scene:<slug>`, from its provider's `register()`:

```php
$this->callAfterResolving('terran.primitives', fn (ScenePrimitives $p) => $p->register('tetromino', Tetromino::class));
```

## Physics

Godot's 2D physics nodes. A stock app runs Terran's own `php` driver, with no extension. Terran's second driver, `box2d`, runs the same physics in C over ext-box2d; with the extension loaded, `terran.physics.driver` `auto` picks it.

```php
$floor = new StaticBody2D('floor');
$floor->add(new CollisionShape2D('shape', new RectangleShape2D(new Vector2(800, 20))));

$crate = new RigidBody2D('crate');
$crate->add(new CollisionShape2D('shape', new RectangleShape2D(new Vector2(20, 20))));
$crate->contactMonitor = true;
$crate->maxContactsReported = 4;
$crate->connect('bodyEntered', fn (Scene $body) => $this->thud($body));

final class Hero extends CharacterBody2D
{
    public function physicsProcess(float $delta): void
    {
        $run = $this->actions()->axis('left', 'right') * 200.0;
        $this->velocity = new Vector2($run, $this->velocity->y + 980.0 * $delta);
        if ($this->actions()->isPressed('jump') && $this->isOnFloor()) {
            $this->velocity = new Vector2($run, -500.0);
        }
        $this->moveAndSlide();
    }
}
```

| Bodies | Areas and shapes | Queries |
|---|---|---|
| `StaticBody2D`, `AnimatableBody2D`, `RigidBody2D`, `CharacterBody2D` | `Area2D`, `CollisionShape2D`, `CollisionPolygon2D`; shapes `RectangleShape2D`, `CircleShape2D`, `CapsuleShape2D`, `SegmentShape2D`, `ConvexPolygonShape2D`, `ConcavePolygonShape2D`, `WorldBoundaryShape2D`, `SeparationRayShape2D`; `PhysicsMaterial` | `RayCast2D`; `$this->world()->physics()->rayCast()`, `intersectPoint()`, `intersectShape()`, `castMotion()` |

Physics steps on the GameLoop after every `physicsProcess()`; rigid bodies write their pose back to their nodes, and moving a node by code teleports its body. Distances are pixels, gravity `terran.physics.gravity` (980 px/s² down). `terran.physics.debug` draws every shape.

`php` is plain PHP and needs no extension. `box2d` runs Box2D v3.1 in C through ext-box2d (`pie install php-io-extensions/box2d`); `terran.physics.driver` `auto` picks it when the extension is loaded, and `TERRAN_PHYSICS_DRIVER=php` keeps the php driver. Box2D steps the bodies; layers, one-way shapes, areas, materials and Godot's `move_and_slide` run the same code on both, so a game behaves the same and only speed differs: 100 crates on a 40-tile floor, through nodes, xdebug off, per step while awake: php 4.95 ms, box2d 1.69 ms on a Mac; php 8.32 ms, box2d 2.83 ms on the Pi.

## Own your window

Extend `GameEngine`, open the window in `openTargets()`, return its canvas as a `canvas` target, and return your root from `mainScene()`.

## Tests

```bash
php -d memory_limit=128M vendor/bin/pest
```

Hardware-free: a fake output target, Velvet over native framebuffers, a real EventLoop over stream_select.
