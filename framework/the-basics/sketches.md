# Sketches

Sketches are long-running Venusian programs with a boot step, a frame loop and a shutdown step, run on the event loop by Rocket.

## Introduction

A Computer command does one job and exits. Many Venusian applications instead need a program that keeps running: a window that redraws, a sensor that is read many times a second, a worker that reacts to whatever the event loop delivers. A sketch is that program.

A sketch has three steps. `boot` runs once before anything else, `loop` runs once per frame for as long as the sketch wants to keep going, and `shutdown` runs once when it ends, however it ends. Rocket, the `php rocket` entry point, finds your sketches, gives each one a command named after it, and runs the one you ask for on the [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop).

Between frames the event loop keeps working: timers fire, sockets are read, worker pools return results. Whatever the loop collects for your application arrives in the next frame as [loop mail](/docs/{{version}}/framework/the-basics/loop-mail), passed to `loop` as its `$mail` argument.

## Writing Sketches

### Generating Sketches

To create a new sketch, use the `make:sketch` Computer command:

```shell
php computer make:sketch Heartbeat
```

The class is written into the sketch directory you passed to `withSketches` in `bootstrap/app.php` (the first one, if you passed several), as long as it lies under the `app` directory. In the application skeleton that is `app/Runner/Sketches`, so the command above creates `app/Runner/Sketches/Heartbeat.php` in the `App\Runner\Sketches` namespace. A name with slashes creates the class in a subdirectory and namespace:

```shell
php computer make:sketch Sensors/Thermometer
```

If no scanned directory lies under `app`, the class is written to `app/Console/Sketches` and the command warns you that Rocket will not find it until that directory, or the class, is passed to `withSketches` in `bootstrap/app.php`. The command will not overwrite an existing class unless you pass `--force` (or `-f`):

```shell
php computer make:sketch Heartbeat --force
```

The generated class extends the nearest abstract class named `Sketch` that it finds walking up from its own namespace towards `App`. In the skeleton that is `App\Runner\Sketches\Sketch`, so every sketch you generate shares that base. When there is none, the class extends `Voyager\Sketches\Sketch` directly. Like other generator commands, the stub can be customized by placing your own `stubs/sketch.stub` in the root of your application.

### Sketch Structure

A generated sketch looks like this:

```php
<?php

namespace App\Runner\Sketches;

use Voyager\Contracts\Sketches\SketchLoopResult;

class Heartbeat extends Sketch
{
    /**
     * The sketch description.
     *
     * @var string
     */
    protected string $description = '';

    /**
     * Prepare the sketch before the first frame.
     */
    public function boot(): void
    {
        //
    }

    /**
     * One frame. The runner calls it at the refresh rate.
     *
     * @param list<object> $mail what the loop delivered since the last frame; empty when nothing did
     */
    public function loop(array $mail = []): SketchLoopResult
    {
        return SketchLoopResult::CONTINUE;
    }

    /**
     * Release resources after the loop ends or fails.
     */
    public function shutdown(): void
    {
        //
    }
}
```

Every sketch extends `Voyager\Sketches\Sketch`, which implements the `Voyager\Contracts\Sketches\Sketch` contract. The base class gives you the following members:

| Member | Purpose |
|---|---|
| `boot(): void` | Runs once before the first frame. Empty by default. |
| `loop(array $mail = []): SketchLoopResult` | Abstract. Runs once per frame and returns whether the sketch continues. |
| `shutdown(): void` | Runs once after the last frame, or after a failure. Empty by default. |
| `protected string $description` | The text Rocket lists next to the sketch's name. Empty by default. |
| `protected ?float $refresh_rate` | Frames per second (Hz) for this sketch. `null`, the default, uses the configured rate. |
| `getDescription(): string` | Returns `$description`. |
| `refreshRate(): ?float` | Returns `$refresh_rate`. |
| `configureIO($input, $output)` | Called by Rocket before `boot` to hand the sketch its console input and output. |

Rocket reads `$description` from the property's default value without building the sketch, so give it a value in the property declaration rather than in the constructor.

### Continuing and Stopping

`loop` returns a `Voyager\Contracts\Sketches\SketchLoopResult`. Return `SketchLoopResult::CONTINUE` to be called again on the next frame, or `SketchLoopResult::STOP` to end the sketch. A sketch that returns `STOP` exits with status `0`:

```php
<?php

namespace App\Runner\Sketches;

use Voyager\Contracts\Sketches\SketchLoopResult;

class Countdown extends Sketch
{
    protected string $description = 'Count down from five, once a second.';

    protected ?float $refresh_rate = 1;

    private int $remaining = 5;

    public function loop(array $mail = []): SketchLoopResult
    {
        $this->info((string) $this->remaining--);

        return $this->remaining > 0
            ? SketchLoopResult::CONTINUE
            : SketchLoopResult::STOP;
    }

    public function shutdown(): void
    {
        $this->comment('Lift off.');
    }
}
```

A sketch also ends when something stops the loop it runs on:

- The `stop` method of the sketch runner, registered in the container as `sketches.runner`, ends the sketch with the status you give it. It may be called from the sketch itself or from any code running on the loop:

```php
app('sketches.runner')->stop(3); // php rocket exits with status 3
```

- Pressing Ctrl+C (SIGINT) or sending SIGTERM stops the loop when the `pcntl` extension is loaded. Rocket then exits with `130` or `143`, the statuses a shell reports for those signals. A second Ctrl+C while the sketch is still shutting down ends the process at once.
- An exception thrown from `loop` ends the run. Rocket reports it through your application's [exception handler](/docs/{{version}}/framework/the-basics/error-handling), renders it to the console, and exits with status `1`.

In each of these cases `shutdown` runs exactly once. It also runs when `boot` throws, in which case no frame runs at all. Put cleanup that must always happen, such as closing windows or releasing devices, in `shutdown`.

> [!WARNING]
> Without the `pcntl` extension the loop cannot watch for SIGINT and SIGTERM, so either signal ends the process immediately and `shutdown` does not run. Install `pcntl` wherever a sketch holds resources that must be released.

### Writing Output

A sketch has the same output helpers as a Computer command: `line`, `newLine`, `info`, `comment`, `question`, `warn`, `alert`, `error`, and `table`, along with `withProgressBar`. They write to the console Rocket was started from:

```php
public function boot(): void
{
    $this->info('Thermometer ready.');
    $this->table(['Sensor', 'Bus'], [['bme280', 'i2c-1']]);
}
```

The prompting helpers `ask`, `confirm`, `choice`, `anticipate`, `secret`, and `askWithCompletion` are also available. A prompt waits for the user and holds up the whole event loop while it waits, so ask your questions in `boot`, before the first frame.

See [Writing Output](/docs/{{version}}/framework/digging-deeper/computer#writing-output) in the Computer documentation for each helper's options.

## The Frame Loop

### Refresh Rate

Rocket calls `loop` at the sketch's refresh rate, in frames per second. The rate comes from the `refresh_rate` option of your `config/sketches.php` file, which reads the `SKETCH_REFRESH_RATE` environment variable and defaults to `60`:

```ini
SKETCH_REFRESH_RATE=60
```

A sketch that sets its own `$refresh_rate` uses that instead. When the sketch starts, its rate is written to the `sketches.refresh_rate` configuration key for the rest of the run:

```php
class Thermometer extends Sketch
{
    protected ?float $refresh_rate = 4; // four frames a second
}
```

The runner reads `sketches.refresh_rate` again after every frame, so a sketch may change its own pace while it runs:

```php
public function loop(array $mail = []): SketchLoopResult
{
    // Drop to 5 frames a second when nothing arrived; go back to 60 when mail does.
    app('config')->set('sketches.refresh_rate', $mail === [] ? 5 : 60);

    return SketchLoopResult::CONTINUE;
}
```

Rates below `1` are treated as `1`, so a frame always comes at least once a second.

### How Frames Are Timed

A frame is a one-shot timer on the event loop. When a frame finishes, the runner sets a new timer for one period (`1 / refresh_rate` seconds) later, and the loop is free to do other work until it fires. Because the next period starts when the current frame returns, a frame that takes a long time lowers the effective rate rather than causing frames to pile up; a frame never starts while the previous one is still running.

`loop` is called every frame whether or not anything happened. When the loop delivered [mail](/docs/{{version}}/framework/the-basics/loop-mail) since the last frame, `$mail` holds it, oldest first, and each piece is handed over exactly once. When nothing arrived, `$mail` is an empty array:

```php
use Voyager\Database\IOPools\QueryChunk;

public function loop(array $mail = []): SketchLoopResult
{
    foreach ($mail as $piece) {
        if ($piece instanceof QueryChunk) {
            $this->info("Page {$piece->page}: {$piece->rows->count()} rows");
        }
    }

    return SketchLoopResult::CONTINUE;
}
```

On a Rocket run, loop mail goes to the running sketch instead of being dispatched as [signals](/docs/{{version}}/framework/digging-deeper/signals). The [Loop Mail](/docs/{{version}}/framework/the-basics/loop-mail#receiving-mail-in-a-sketch) documentation explains how that switch is made.

## Naming and Registering Sketches

### Sketch Names

A sketch's name is its class name in kebab case: `HelloWorld` becomes `hello-world` and `Sensors\Thermometer` becomes `thermometer`. Only the class name counts, not its namespace. To choose a different name, add the `Voyager\Contracts\Sketches\Attributes\Sketch` attribute to the class:

```php
<?php

namespace App\Runner\Sketches;

use Voyager\Contracts\Sketches\Attributes\Sketch as SketchName;
use Voyager\Contracts\Sketches\SketchLoopResult;

#[SketchName('launch-pad')]
class LaunchPadController extends Sketch
{
    public function loop(array $mail = []): SketchLoopResult
    {
        return SketchLoopResult::STOP;
    }
}
```

Each name belongs to one sketch. When two sketches resolve to the same name, the first one registered keeps it and the other is not listed, so give one of them a `#[Sketch]` name.

### Where Sketches Live

Rocket looks for sketches in the places your `bootstrap/app.php` file gives to `withSketches`. The application skeleton scans `app/Runner/Sketches`:

```php
<?php

use Voyager\Core\Bootstrap\Exceptions;
use Voyager\Core\VenusianVoyager;

return VenusianVoyager::setup(base_path: dirname(__DIR__))
    ->withExceptions(function (Exceptions $exceptions): void {})
    ->withSketches([__DIR__.'/../app/Runner/Sketches'])
    ->create();
```

`VenusianVoyager::setup` always scans `app/Console/Sketches` as well. Each entry passed to `withSketches` may be a directory or a sketch class name, and both kinds may be mixed in the same array:

```php
->withSketches([
    __DIR__.'/../app/Runner/Sketches',
    \App\Devices\Thermometer::class,
])
```

A directory is searched recursively. Every PHP file in it is mapped to a class name from its path under `app`, in the `App` namespace, so `app/Runner/Sketches/Sensors/Thermometer.php` must hold `App\Runner\Sketches\Sensors\Thermometer`. Concrete classes that extend a sketch are registered; abstract classes, such as the skeleton's `App\Runner\Sketches\Sketch`, and everything else in the directory are skipped. A directory that does not exist is ignored.

Sketch classes that live outside the scanned directories, such as classes from a package, may be listed in the `load` option of `config/sketches.php`:

```php
'load' => [
    \Vendor\Package\Sketches\Telemetry::class,
],
```

Sketches are registered in this order: classes passed to `withSketches`, then the `load` list, then the classes found in the scanned directories. The registry behind them is in the container as `sketches.registry` (also resolvable as `Voyager\Contracts\Sketches\SketchRegistry`); its `all` method returns every registered name and class, and `has` tells you whether a name is taken.

## Running Sketches

### Listing Sketches

Running `php rocket` with no arguments lists the sketches your application has registered, with their descriptions:

```shell
php rocket
```

```text
Rocket 0.10.8

Usage:
  command [options] [arguments]

...

Available commands:
  completion   Dump the shell completion script
  hello-world  Print a greeting and stop.
  help         Display help for a command
  list         List commands
```

`php rocket list` prints the same listing. Each sketch is a Rocket command named after the sketch; a sketch is not a `php computer` command, and Computer commands such as `make:sketch` run through `php computer`.

### Running a Sketch

To run a sketch, pass its name to `php rocket`:

```shell
php rocket hello-world
```

Rocket boots your application, builds the sketch through the [service container](/docs/{{version}}/framework/architecture-concepts/container), hands it the console input and output, and runs it. The process exits with the sketch's status when the sketch ends.

### Rocket Lifecycle Signals

Rocket dispatches two [signals](/docs/{{version}}/framework/digging-deeper/signals) around every run. `Voyager\Sketches\Signals\SketchStarting` is dispatched before the sketch boots and `Voyager\Sketches\Signals\SketchFinished` after it ends. Both carry the sketch's name as `command`, plus the console `input` and `output`; `SketchFinished` also carries the `exit_code`. Since `SketchStarting` is dispatched before the sketch exists, listen for these in a [service provider's](/docs/{{version}}/framework/architecture-concepts/providers) `boot` method:

```php
use Voyager\Sketches\Signals\SketchFinished;
use Voyager\Sketches\Signals\SketchStarting;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('signals')->listen(function (SketchStarting $signal) {
        app('log')->info("Sketch {$signal->command} starting.");
    });

    app('signals')->listen(function (SketchFinished $signal) {
        app('log')->info("Sketch {$signal->command} exited with {$signal->exit_code}.");
    });
}
```

### Telling Rocket and Computer Apart

Rocket and Computer boot the same application with the same service providers. A provider that should only do its work on one of them may check `isRocketRunning`, which is `true` from the moment Rocket starts booting, including while providers register, and `false` on every `php computer` run.

The most common use is commands. Rocket's console also picks up commands a provider registers with `commands` unless the command class carries Symfony's `#[AsCommand]` attribute, so a provider whose commands belong to Computer alone should skip registering them under Rocket:

```php
use App\Console\Commands\ImportReadings;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    if ($this->app->isRocketRunning()) {
        return;
    }

    $this->commands([
        ImportReadings::class,
    ]);
}
```

## Using the Framework From a Sketch

### Dependency Injection

Rocket builds your sketch through the [service container](/docs/{{version}}/framework/architecture-concepts/container), so you may type-hint any dependency in the sketch's constructor:

```php
<?php

namespace App\Runner\Sketches;

use Voyager\Contracts\Cache\Repository;
use Voyager\Contracts\Sketches\SketchLoopResult;

class VisitorBoard extends Sketch
{
    protected string $description = 'Show the visitor count.';

    public function __construct(
        protected Repository $cache,
    ) {}

    public function loop(array $mail = []): SketchLoopResult
    {
        $this->line('Visitors: '.$this->cache->get('visitors', 0));

        return SketchLoopResult::CONTINUE;
    }
}
```

Services may also be resolved anywhere in the sketch with `app()`, such as `app('db')`, `app('cache')`, `app('signals')`, or `app('event-loop')`.

### Keeping Frames Short

Everything in a sketch runs on one event loop. While `loop` is running, no other loop work happens: timers wait, sockets wait, and the next frame waits. A blocking call, such as a slow query or a blocking HTTP request, therefore holds up the whole program for as long as it takes.

Prefer the framework's non-blocking APIs inside a sketch. Each returns a promise, or delivers mail, and lets the frame return at once:

- [Async cache operations](/docs/{{version}}/framework/digging-deeper/cache#async-cache-operations) with `app('cache')->store('redis')->async()`.
- [Asynchronous HTTP requests](/docs/{{version}}/framework/digging-deeper/http-client#asynchronous-requests) with `app('http')->async()`.
- [Pushing jobs without blocking](/docs/{{version}}/framework/digging-deeper/queues#pushing-without-blocking) with `app('queue')->connection('redis')->async()`.
- [Running tasks without blocking](/docs/{{version}}/framework/digging-deeper/concurrency#running-tasks-without-blocking) with `app('concurrency')->async()`.
- [Streaming query results](/docs/{{version}}/framework/database/queries#streaming-results-as-signals) a page at a time with `stream`.
- [Waiting on processes](/docs/{{version}}/framework/digging-deeper/processes#waiting-on-the-event-loop) from the event loop.

A promise's callbacks run on the loop once it settles, between frames. Start the work in one frame and pick up its result in a callback or, for APIs that deliver mail, in a later frame's `$mail`:

```php
<?php

namespace App\Runner\Sketches;

use Voyager\Contracts\Sketches\SketchLoopResult;
use Voyager\Http\Client\Response;

class StatusBoard extends Sketch
{
    protected string $description = 'Show the service status once it is known.';

    private ?string $status = null;

    public function boot(): void
    {
        app('http')->async()->get('https://example.com/status.json')
            ->then(function (Response $response) {
                $this->status = $response->json('status');
            });
    }

    public function loop(array $mail = []): SketchLoopResult
    {
        if ($this->status === null) {
            return SketchLoopResult::CONTINUE; // still waiting; the loop keeps working
        }

        $this->info("Status: {$this->status}");

        return SketchLoopResult::STOP;
    }
}
```

### Working With the Event Loop

The event loop a sketch runs on is in the container as `event-loop`, and may be injected as `Voyager\Contracts\IOPools\Loop`. You may add your own timers and resources to it from `boot` or from any frame, and they run alongside your frames:

```php
public function boot(): void
{
    app('event-loop')->every(30, fn () => $this->comment('Still running at '.date('H:i:s')), 'heartbeat');
}
```

Do not call `run` on the loop yourself; Rocket is already running it. To end the sketch from loop code, call `app('sketches.runner')->stop()`. The [Event Loop](/docs/{{version}}/framework/architecture-concepts/event-loop) documentation covers timers, resources, and worker pools in depth.

## The Application Skeleton

A new application ships one sketch and one base class in `app/Runner/Sketches`.

`App\Runner\Sketches\Sketch` is an empty abstract class extending `Voyager\Sketches\Sketch`. It is the shared parent for your sketches: anything you add to it, such as a helper method or a common `boot` step, is available in every sketch that extends it, and `make:sketch` extends it automatically. Because it is abstract, discovery never registers it as a sketch of its own.

`App\Runner\Sketches\HelloWorld` is the smallest working sketch. It prints a greeting on its first frame and stops:

```php
<?php

namespace App\Runner\Sketches;

use Voyager\Contracts\Sketches\SketchLoopResult;

class HelloWorld extends Sketch
{
    /**
     * The sketch description.
     *
     * @var string
     */
    protected string $description = 'Print a greeting and stop.';

    /**
     * Execute one cooperative tick of the sketch.
     */
    public function loop(array $mail = []): SketchLoopResult
    {
        $this->info('Hello, world.');

        return SketchLoopResult::STOP;
    }
}
```

Run it with:

```shell
php rocket hello-world
```
