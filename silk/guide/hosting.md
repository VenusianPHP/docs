# A tree in a window

Two hosts bind a widget tree to a window: `StagedHost` owns a whole staged window, `CanvasHost` lives inside a `TKCanvas` of a toolkit window. The same tree runs on either.

## A staged window

The app opens the window, asks Surface for the engine, composes the root, then hands tree, engine and window to the host. `app('silk')->attach(host)` joins the tree to the [frame loop](/docs/{{version}}/silk/architecture/hosts); the session must join the event loop or nothing pumps the window:

```php
$this->session = app('toolkit-bridge')->driver()->connect();
$this->session->joinLoop(app('event-loop'));

$window = app('staged-windows')->open('silk', 480, 320);
$engine = app('drawing')->renderer(getenv('SILK_ENGINE') ?: null, ['output' => $window]);

$root = new Column('window', 6, 16);
$root->label('title', 'Silk on a staged window');
$root->button('press', 'Press me');
$root->toggle('dark', true);

$tree = new Tree($root, app('silk.looks')->current(), app('event-loop'), 'silk');
app('silk.looks')->watch($tree);

$this->host = new StagedHost($window, $tree, $engine);
$this->host->font = app('fonts')->face();
app('silk')->attach($this->host);
```

In the sketch's `loop()`, give each mail to the host first — `$this->host->handles($item)` — and the tree takes its input; read the rest yourself:

```php
public function loop(array $mail = []): SketchLoopResult
{
    foreach ($mail as $item) {
        if ($item instanceof WindowCloseRequested) {
            return SketchLoopResult::STOP;
        }
        if ($this->host->handles($item)) {
            continue;
        }
        if ($item instanceof ButtonClicked && str_ends_with($item->path, '.press')) {
            // the user pressed the button
        }
    }

    return SketchLoopResult::CONTINUE;
}
```

`shutdown()` is the mirror: `app('silk')->detach($this->host)` and close the windows — the canvas sketch also leaves and disconnects the session.

## A canvas in a toolkit window

Inside a native window, a Silk tree runs in a `TKCanvas` next to the native widgets, taking the canvas as its host:

```php
$window = app('toolkit-windows')->open('main', 640, 260, 'main');
$canvas = $window->column('page', 0, 0)->canvas('silk');
$canvas->fill()->minSize(600, 220);

$root = new Column('bar', 6, 10);
$root->row('controls', 8)->button('zoom-in', 'Zoom in');
$root->progressBar('zoom', $this->fraction());   // the zoom as a linear share of 1/8x..8x, as in examples/canvas-demo.php

$tree = new Tree($root, app('silk.looks')->current(), app('event-loop'), 'main');
app('silk.looks')->watch($tree);

$this->host = new CanvasHost($canvas, $tree);
$this->host->font = app('fonts')->face();
app('silk')->attach($this->host);

$window->present();
$this->host->rebind();   // a resize may have arrived before the host listened
```

The canvas host watches pointer, keys and size itself, converts points to pixels with the canvas scale, and keeps [overlays](/docs/{{version}}/silk/architecture/overlays) inside the canvas.

## The engine

The engine is Surface's, never Silk's: `app('drawing')->renderer(name, ['output' => ...])`, name from `config('drawing.default')` — Velvet unless the app says otherwise — and `SILK_ENGINE` overrides it for one run. Nothing picks a GPU engine automatically. See Surface's [drawing](/docs/{{version}}/surface/architecture/drawing).

Both hosts appear working in the `examples/` directory of the Silk repository: `staged-demo.php` and `canvas-demo.php`, each a complete sketch to copy into an app and run with `php rocket`.

[^hosts]: src/Silk/Hosts/CanvasHost.php, StagedHost.php, examples/staged-demo.php, examples/canvas-demo.php.
