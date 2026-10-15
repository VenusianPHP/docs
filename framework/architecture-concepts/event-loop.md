# Event Loop

How Venusian's event loop turns, and how to use its timers, deferred work, promises, fibers, resources, waiter backends and worker pools.

## Introduction

Venusian is built around one event loop per process. Every slow thing your application does, such as reading a socket, waiting on a child process, running a query in a worker pool or sleeping until a timer is due, is registered with the loop. The loop sleeps until one of those things can make progress, lets it make progress, and goes back to sleep. Nothing busy-waits, and one process can keep many pieces of work in flight at once.

The cache, queues, Redis, the HTTP client, processes, the filesystem and concurrency all expose promise-based calls that ride this loop. This page explains the loop itself: what one turn does, how to schedule work on it, how promises and fibers wait on it, how resources tell it what to wait for, and which PHP extension it uses to do the waiting.

The loop is `Voyager\IOPools\EventLoop`, which implements the `Voyager\Contracts\IOPools\Loop` contract. Its configuration lives in your application's `config/io-pools.php` file.

<a id="one-turn-of-the-loop"></a>
## One Turn of the Loop

The loop does its work in turns. Knowing what happens in a turn, and in what order, tells you when your callbacks will run. Each turn does the following, once:

1. **Wait.** The loop waits once, for at most the time until the soonest timer is due. The wait ends early if a stream, signal or process it is watching fires. If deferred work or a parked fiber can run right away, the wait is only a glance: a zero-length check.
2. **Wakes.** Each resource whose stream, signal or process fired is told which of its wakes fired.
3. **Deadlines.** Every timer whose due time has passed fires.
4. **Ticks.** Every polled resource is ticked.
5. **Follow-ons.** Promise callbacks run, then deferred work and resumed fibers run. The loop repeats this step until a pass runs nothing, so a callback that settles another promise is handled in the same turn.
6. **Mail.** Resources hand over any mail they collected, and the loop gives the turn's mail to the [mail handler](#loop-mail).

If a timer callback, a tick or a wake handler throws, the loop finishes the turn and then rethrows the first exception, which ends `run()`. Work you hand to `defer()` or `async()` is different: its exception rejects its promise instead of ending the loop.

The loop keeps turning while it has work: a registered resource, a pending timer, or deferred work not yet run. When the last of these is gone, `run()` returns on its own.

<a id="getting-the-loop"></a>
## Getting the Loop

The loop is a singleton bound under the `event-loop` key in the [container](/docs/{{version}}/framework/architecture-concepts/container#resolving-framework-services). The `Voyager\IOPools\EventLoop` class and the `Voyager\Contracts\IOPools\Loop` contract are aliased to that key, so all three give you the same instance:

```php
use Voyager\Contracts\IOPools\Loop;

$loop = app('event-loop');

$loop === app(Loop::class); // true
```

In your own classes, type-hint the contract and let the container inject it:

```php
use Voyager\Contracts\IOPools\Loop;

class SensorPoller
{
    public function __construct(
        protected Loop $loop,
    ) {}
}
```

When your application is launched with Rocket, the sketch runner calls `run()` for you and keeps the loop turning while the sketch runs. Inside a Computer command, nothing is turning the loop until you call `run()`, or until you wait on a promise, which turns the loop for as long as the wait lasts.

You may check how the loop is configured in your environment with the `about` command:

```shell
php computer about --only=event-loop
```

<a id="timers"></a>
## Timers

Timers run a callback after a delay, once or repeatedly. Delays and intervals are given in seconds as floats, so `0.25` is a quarter of a second.

<a id="one-shot-timers"></a>
### One-Shot Timers

The `at` method runs a callback once, after the given delay. After it fires, the timer is removed from the loop:

```php
$loop->at(1.5, function () {
    app('log')->info('A second and a half has passed.');
});
```

<a id="repeating-timers"></a>
### Repeating Timers

The `every` method runs a callback at a fixed interval. A repeating timer must be given a name, which registers it with the loop under that name. Registering another resource under the same name replaces it:

```php
$loop->every(0.5, function () {
    app('log')->info('Heartbeat.');
}, 'heartbeat');
```

The timer stays on a fixed grid. If a callback runs long enough to overrun several intervals, the missed beats are skipped rather than fired back to back, and the next beat lands on the grid.

> [!WARNING]
> A repeating timer is work: it keeps `run()` turning until it is cancelled or forgotten. If your loop never ends, look for a repeating timer you didn't stop.

<a id="cancelling-timers"></a>
### Cancelling Timers

Both `at` and `every` return a `Voyager\Contracts\IOPools\LoopResources\Timer`. Calling its `cancel` method stops it, and the loop removes it on its next turn:

```php
$count = 0;

$timer = $loop->every(0.1, function () use (&$count, &$timer) {
    if (++$count === 10) {
        $timer->cancel();
    }
}, 'countdown');
```

Because a repeating timer has a name, you may also remove it by name with `forget`:

```php
$loop->forget('heartbeat');
```

The `Timer` also reports its state: `dueAt()` returns the next due time as an `hrtime(true)` value in nanoseconds, or `null` once a one-shot timer has fired or any timer is cancelled; `cancelled()` tells you whether it was cancelled; and `interval()` returns the interval in nanoseconds, or `null` for a one-shot timer.

<a id="running-and-stopping-the-loop"></a>
## Running and Stopping the Loop

The `run` method turns the loop until it is stopped or runs out of work, and returns an integer status:

```php
$status = $loop->run();
```

The `stop` method asks the loop to stop after the current turn. The status you pass becomes the return value of `run()`, and defaults to `0`:

```php
$loop->at(30, fn () => $loop->stop(1));

$status = $loop->run(); // 1
```

When `run()` ends, for any reason, the loop cancels any fibers still parked on it, runs the promise callbacks that are still queued, and then calls each hook you registered with `onStop`. Worker pools use this hook to shut their workers down. Your hooks are kept for the life of the loop, so a hook registered once runs at the end of every later `run()` as well:

```php
$loop->onStop(function () {
    app('log')->info('The loop has stopped.');
});
```

An exception thrown by an `onStop` hook is discarded, so one failing hook never stops the others from running.

<a id="stop-signals"></a>
### Stop Signals

While `run()` is turning, the loop listens for `SIGINT` (Ctrl+C) and `SIGTERM`. The first one stops the loop as `stop()` would, with the status a shell reports for a process killed by that signal: `130` for `SIGINT`, `143` for `SIGTERM`. Your `onStop` hooks then run, so worker pools shut their workers down instead of leaving them orphaned.

After the first signal, the default handlers are restored, so a second Ctrl+C kills the process immediately if shutting down is stuck. The next `run()` listens again.

Listening for stop signals requires the `pcntl` extension. Without it, the loop does not listen, and a signal ends the process the way PHP's default handler does, without running your `onStop` hooks. The signal watcher never keeps the loop running on its own: a loop with nothing else to do still returns from `run()` right away.

<a id="deferring-work"></a>
## Deferring Work

The `defer` method runs a closure on the loop's next turn, instead of right now. It returns a promise that is fulfilled with the closure's return value, or rejected with whatever it threw:

```php
$promise = $loop->defer(function () {
    return app('db')->table('users')->count();
});

$promise->then(function (int $count) {
    app('log')->info("There are {$count} users.");
});
```

All work deferred before a turn starts runs together in that turn. Work deferred from inside a deferred closure runs on the turn after, so a closure that keeps deferring itself never starves the rest of the loop. Pending deferred work keeps the loop running, and makes the loop's next wait a glance rather than a sleep, so it runs promptly.

The `deferred` queue driver uses this to run jobs on a later turn of the loop; see [Queues](/docs/{{version}}/framework/digging-deeper/queues#deferred).

<a id="promises"></a>
## Promises

A promise stands for a result that isn't ready yet. Every asynchronous call in Venusian returns a `Voyager\Contracts\IOPools\Promise`, and you can make your own for work you finish later.

<a id="creating-promises"></a>
### Creating Promises

The `promise` method makes a new pending promise. Whoever does the work settles it once, with `resolve` on success or `reject` with a `Throwable` on failure:

```php
$promise = $loop->promise();

$loop->at(0.5, fn () => $promise->resolve(42));
```

```php
$promise = $loop->promise();

$loop->at(0.5, fn () => $promise->reject(new RuntimeException('The sensor did not answer.')));
```

The `settled`, `fulfilled` and `rejected` methods report the promise's state.

<a id="reacting-to-a-promise"></a>
### Reacting to a Promise

The `then` method registers a callback that receives the value once the promise is fulfilled. It returns a new promise, which is fulfilled with your callback's return value, so calls can be chained:

```php
$loop->defer(fn () => 21)
    ->then(fn (int $value) => $value * 2)
    ->then(function (int $value) {
        // $value is 42...
    });
```

The `error` method registers a callback that receives the `Throwable` if the promise is rejected. Whatever the callback returns fulfills the next promise in the chain, so `error` can recover from a failure:

```php
$promise->error(function (Throwable $e) {
    app('log')->warning($e->getMessage());

    return 'fallback';
})->then(function (string $value) {
    // 'fallback' if $promise was rejected...
});
```

The `finally` method registers a callback that runs on either outcome and receives nothing. The value or the rejection passes through it unchanged to the next promise:

```php
$promise->finally(function () {
    app('log')->info('The reading is done, one way or another.');
});
```

If a library rejects a promise with something that isn't a `Throwable`, your `error` callback receives a `Voyager\Contracts\IOPools\IOPoolsException` describing it instead.

<a id="waiting-on-a-promise"></a>
### Waiting on a Promise

The `wait` method blocks until the promise settles. It returns the value, or throws the rejection:

```php
$promise = $loop->promise();

$loop->at(0.5, fn () => $promise->resolve(42));

$value = $promise->wait(); // 42
```

A wait is not a busy loop and does not stall the rest of your application: it turns the event loop until the promise settles, so timers, resources and other promises keep making progress while you wait. How it does this depends on where you call it; see [Waiting With `until`](#waiting-with-until).

The loop's `await` method does the same for any value. Given a loop promise, it waits on it. Given any other object with a `then` method, such as a Guzzle or React promise, it adopts it and waits. Given anything else, it returns the value unchanged:

```php
$value = $loop->await($promise);

$value = $loop->await(5); // 5
```

<a id="promise-engines"></a>
### Promise Engines

Under the hood, loop promises are backed by a promise library, chosen by the `io-pools.promise_engines.default` configuration option or the `IO_POOLS_PROMISE_ENGINE` environment variable:

| Engine | Library | Callbacks run |
| --- | --- | --- |
| `guzzle` (default) | `guzzlehttp/promises` ^2.0 | Queued, then run in the follow-on step of a turn |
| `react` | `react/promise` ^3.0 | Synchronously, as soon as the promise settles |

```php
'promise_engines' => [
    'default' => env('IO_POOLS_PROMISE_ENGINE', 'guzzle'),
],
```

The `guzzle` engine's library is installed with the framework. To use the `react` engine, install its library first; if it is missing, building the loop throws an `IOPoolsException` telling you so:

```shell
composer require react/promise
```

Either way, your code sees the same `Voyager\Contracts\IOPools\Promise`, and `await` accepts promises from both libraries.

<a id="fibers"></a>
## Fibers

A wait on the main stack of your program blocks that code until the promise settles. When you want several waits to make progress side by side, run each one in a fiber with the `async` method. The fiber starts immediately and runs until its first wait. Each `await` or `wait` inside the fiber then parks the fiber and gives control back to the loop, instead of blocking:

```php
$task = $loop->async(function () use ($loop) {
    $reading = $loop->promise();
    $loop->at(0.5, fn () => $reading->resolve(21));

    $value = $loop->await($reading);
    $doubled = $loop->await($loop->defer(fn () => $value * 2));

    return $doubled;
});
```

`async` returns a `Voyager\Contracts\IOPools\Task`, which is a promise for the fiber's return value. You may use `then`, `error`, `finally` and `wait` on it like any other promise. If the fiber throws, the task is rejected with that exception; the loop itself carries on:

```php
$value = $task->wait(); // 42
```

A parked fiber resumes in the follow-on step of the turn in which the thing it was waiting for becomes true.

<a id="cancelling-tasks"></a>
### Cancelling Tasks

The task's `cancel` method throws a `Voyager\Contracts\IOPools\CancelledException` into the fiber where it is parked. Unless the fiber catches it, the task is rejected with it. Cancelling a fiber that has already finished does nothing:

```php
use Voyager\Contracts\IOPools\CancelledException;

$reply = $loop->promise();

$task = $loop->async(fn () => $loop->await($reply));

$task->cancel();

try {
    $task->wait();
} catch (CancelledException $e) {
    // The task was cancelled...
}
```

The loop cancels parked fibers the same way when `run()` ends, and when a wait finds that only parked fibers are left and nothing could ever wake them.

<a id="waiting-with-until"></a>
## Waiting With `until`

Every wait in Venusian, including `Promise::wait()` and `await`, is built on the loop's `until` method. It takes a closure and returns once the closure returns `true`, turning the loop as needed:

```php
$done = false;

$loop->at(1, function () use (&$done) {
    $done = true;
});

$loop->until(fn () => $done);
```

If the condition is already true, `until` returns immediately. Otherwise it does one of two things, depending on where it is called:

- **Suspending.** Inside a fiber started by `async`, `until` parks the fiber with the condition and returns control to the loop. The fiber resumes once the condition holds.
- **Borrowing.** Anywhere else, `until` borrows the loop: it runs turns itself until the condition holds, then returns. This works whether or not `run()` is already turning; a timer callback can wait on a promise, and the loop keeps serving every other resource while it does.

A fiber that cannot be suspended, because PHP's C code sits between the fiber and the wait (a callback invoked from inside an extension, for example), falls back to borrowing.

Borrowed turns are quiet: they do everything a turn does except deliver mail. Mail collected while a wait borrows the loop is kept and delivered on the next turn of `run()`, so a listener never runs in the middle of the code that is waiting.

<a id="when-a-wait-cannot-finish"></a>
### When a Wait Cannot Finish

A borrowed wait checks whether anything is left that could make its condition true. When the loop has no work left, it first runs any queued promise callbacks and checks again, then cancels any parked fibers and checks again. If the condition still does not hold, it throws a `Voyager\Contracts\IOPools\IOPoolsException`:

```text
until() ran out of work before its condition was met.
```

This usually means you are waiting on a promise that nothing will ever settle: a promise you made with `$loop->promise()` but never resolved, or one whose resource you forgot. The exception saves you from a process that hangs forever:

```php
use Voyager\Contracts\IOPools\IOPoolsException;

try {
    $loop->promise()->wait();
} catch (IOPoolsException $e) {
    // until() ran out of work before its condition was met.
}
```

If `stop()` is called while a wait is borrowing the loop, the wait throws an `IOPoolsException` with the message `The loop was stopped while until() was still waiting.`, since the result it was waiting for will never arrive.

<a id="resources"></a>
## Resources

Everything the loop waits on is a resource: an object you register under a name with the `resource` method. The framework's own components are built this way, and you can write your own to bring any stream, signal or periodic check onto the loop:

```php
$loop->resource('sensor', new SensorReader($stream));
```

Registering a resource under a name that is already taken replaces the old resource. The `forget` method removes one:

```php
$loop->forget('sensor');
```

A registered resource is work, so it keeps `run()` turning until you forget it.

<a id="resource-kinds"></a>
### Resource Kinds

What the loop does with a resource depends on which interfaces it implements, all in the `Voyager\Contracts\IOPools` namespace. A resource may implement several; the loop files it under each. A resource that implements none of them is refused with an `IOPoolsException`. Abstract base classes in `Voyager\IOPools\Resources` implement each kind for you to extend:

| Kind | Interface | Base class | What the loop does |
| --- | --- | --- | --- |
| Wake source | `LoopResources\Wakeable` | `WakeSource` | Asks `wakes()` for what to wait on every turn, then calls `woke($fired)` with the ones that fired |
| Deadline | `LoopResources\Deadlined` | `Deadline` | Calls `fire()` once `dueAt()` (an `hrtime(true)` value in nanoseconds) has passed |
| Polled | `LoopResources\Tickable` | `Pollable` | Calls `tick()` every turn, and keeps waits no longer than the [pace](#the-pace) |
| Sleeper | `LoopResources\Sleepable` | `Sleeper` | Lets the resource do the turn's waiting itself through `sleep($budget_ns)`, then ticks it |
| Follow-on | `LoopResources\Resumable` | `FollowOnResource` | Calls `resume()` in the follow-on step; while `pending()` is true, waits are only a glance |
| Mailer | `Pumpable` | — | Collects mail from `pump()` at the end of every turn, and once more when it is forgotten |
| Background | `LoopResources\Background` | — | A marker: the resource is served, but never keeps `run()` alive on its own |

`Pumpable` and `Background` add to a kind rather than being one: a resource that implements only one of them, or only both, is refused. Timers are deadlines, and `defer` and `async` are follow-on resources the loop registers for itself.

<a id="writing-a-wake-source"></a>
### Writing a Wake Source

A wake source tells the loop what to wait for by returning a list of wakes from its `wakes` method. The loop asks again every turn, so a resource can start and stop watching streams as it goes. The wake classes live in `Voyager\IOPools\Waiter\Wakes`:

| Wake | Fires when |
| --- | --- |
| `Readable($stream)` | The stream has data to read |
| `Writable($stream)` | The stream can be written to |
| `ControlSignal($signo)` | The process receives the signal |
| `ProcessExit($pid)` | The process exits |
| `FileChange($path)` | The file changes |

The following resource reads lines from a non-blocking stream as they arrive, and hands each one to the loop as mail:

```php
use Voyager\Contracts\IOPools\Pumpable;
use Voyager\IOPools\Resources\WakeSource;
use Voyager\IOPools\Waiter\Wakes\Readable;

final class LineReader extends WakeSource implements Pumpable
{
    private string $buffer = '';

    /** @var list<LineArrived> */
    private array $lines = [];

    /** @param resource $stream */
    public function __construct(private readonly mixed $stream)
    {
        stream_set_blocking($stream, false);
    }

    public function wakes(): array
    {
        return [new Readable($this->stream)];
    }

    public function woke(array $fired): void
    {
        $this->buffer .= (string) fread($this->stream, 8192);

        while (($at = strpos($this->buffer, "\n")) !== false) {
            $this->lines[] = new LineArrived(substr($this->buffer, 0, $at));
            $this->buffer = substr($this->buffer, $at + 1);
        }
    }

    public function pump(): array
    {
        [$lines, $this->lines] = [$this->lines, []];

        return $lines;
    }
}
```

Not every backend can wait on every kind of wake (see [Choosing a Backend](#choosing-a-backend)). Before declaring a wake other than `Readable` or `Writable`, ask the loop whether it can wait on it with the `supports` method and the `Voyager\Contracts\IOPools\WakeReason` enum, whose cases are `READABLE`, `WRITEABLE`, `CONTROL_SIGNAL`, `PROCESS_EXIT` and `FILE_CHANGE`. Declaring a wake the loop cannot wait on throws an `IOPoolsException` naming your resource:

```php
use Voyager\Contracts\IOPools\WakeReason;

if ($loop->supports(WakeReason::PROCESS_EXIT)) {
    // Declare a ProcessExit wake...
} else {
    // Check on the process from a polled resource instead...
}
```

<a id="sleepers"></a>
### Sleepers

Some libraries can only wait inside their own blocking call, a GUI toolkit's event loop for example. A sleeper is a resource that does the turn's waiting itself: the loop calls its `sleep` method with the time it may block, in nanoseconds, then takes a zero-length look at everything else it watches.

Only one sleeper can hold the sleep. Sleepers line up in the order you register them; the first holds the sleep, and the others are ticked every turn like polled resources. Forgetting the holder passes the sleep to the next in line. The `crown` method moves a registered sleeper to the front:

```php
$loop->crown('window');
```

A native event loop that does the sleeping can still be woken by this one. The loop's `descriptor` method returns a file descriptor that turns readable whenever the loop has something to do, for the native loop to watch. It returns `null` under the `select` backend.

<a id="the-pace"></a>
### The Pace

When a polled resource is registered, the loop cannot sleep until a timer is due: it has to come back and tick that resource. The pace is the longest the loop will wait while anything polled is registered, and also the time a sleeper is given when no timer is due. It is set in milliseconds by the `io-pools.event_loop.pace_ms` option or the `IO_POOLS_PACE_MS` environment variable, and defaults to `16`, about sixty turns a second:

```php
'event_loop' => [
    'pace_ms' => env('IO_POOLS_PACE_MS', 16),
    // ...
],
```

A lower pace makes polled resources more responsive at the cost of more turns. A loop with nothing polled is not affected by the pace: it sleeps until a timer is due or a watched stream, signal or process fires.

<a id="waiters"></a>
## Waiters

The part of the loop that does the waiting is the waiter. It hands every wake your resources declare to a waiter backend, which asks the operating system to report when any of them fires. The backend is chosen by the `io-pools.pool_waiters.default` option or the `IO_POOLS_WAITER_BACKEND` environment variable:

```php
'pool_waiters' => [
    'default' => env('IO_POOLS_WAITER_BACKEND', 'auto'),
    'drivers' => [
        'epoll' => [],
        'kqueue' => [],
        'select' => [],
    ]
],
```

The default, `auto`, uses `epoll` when the `epoll` extension is loaded, then `kqueue` when the `kqueue` extension is loaded, and `select` otherwise. Naming `epoll` or `kqueue` explicitly when its extension isn't loaded throws an `IOPoolsException` (`ext-epoll not installed.` or `ext-kqueue not installed.`) when the loop is built.

| Backend | Requires | Waits on | `descriptor()` |
| --- | --- | --- | --- |
| `kqueue` | `ext-kqueue` (macOS) | Readable, writable, signals, process exits, file changes | The kqueue descriptor |
| `epoll` | `ext-epoll` (Linux) | Readable, writable | The epoll descriptor |
| `select` | Nothing | Readable, writable | `null` |

Under `epoll` and `select`, the loop still waits on signals when the `pcntl` extension is loaded: it relays each signal into a socket the backend can read. Under `kqueue`, signals also need `pcntl`.

<a id="choosing-a-backend"></a>
### Choosing a Backend

The `select` backend works everywhere and needs nothing installed, but it is built on PHP's `stream_select`, which rescans every watched stream on every wait and cannot wait on process exits or file changes. For anything beyond a handful of streams, install the extension for your operating system:

- **macOS:** `ext-kqueue`, which can also wait on process exits and file changes, so worker pools learn the moment a worker dies.
- **Linux:** `ext-epoll`.

Both are first-party extensions, and the `install:ext` Computer command installs them through PIE for the PHP binary that runs the command. Run without an argument, it lists the extensions; one built for another operating system, or already loaded, is shown but cannot be selected. You may also name the extension:

```shell
php computer install:ext

php computer install:ext kqueue
```

With the default `auto` setting, there is nothing to configure afterwards: the next time the loop is built, it picks up the extension. See [Installing Extensions](/docs/{{version}}/framework/digging-deeper/computer#installing-extensions) for more on the command.

<a id="worker-pools"></a>
## Worker Pools

Some work cannot be made asynchronous: a CPU-heavy calculation, or a blocking library call such as a PDO query. A worker pool runs that work in another PHP process or thread, so the loop keeps turning while it runs, and settles a promise when the result comes back.

A unit of pool work is a gig: a class implementing `Voyager\Contracts\IOPools\WorkerPools\ShouldPool`, whose `handle` method runs inside the worker. The gig crosses to the worker serialized, and its return value crosses back the same way, so a gig carries data, never open resources or closures, and its class must be autoloadable in the worker:

```php
namespace App\Gigs;

use Voyager\Contracts\IOPools\WorkerPools\ShouldPool;

final class ChecksumFile implements ShouldPool
{
    public function __construct(public readonly string $path) {}

    public function handle(): mixed
    {
        return hash_file('sha256', $this->path);
    }
}
```

<a id="named-pools"></a>
### Named Pools

There is no default pool. Each enabled pool is bound in the container under its own name, and you ask for the one you want:

| Key | Pool | Runs gigs in | Enabled by |
| --- | --- | --- | --- |
| `process-workers` | `Voyager\IOPools\WorkerPools\Process\ProcessWorkerPool` | PHP child processes; works on every PHP build | `io-pools.pool_workers.process.enabled` (default `true`) |
| `thread-workers` | `Voyager\IOPools\WorkerPools\Thread\ThreadWorkerPool` | Threads; needs a ZTS build of PHP with `ext-parallel` | `io-pools.pool_workers.threads.enabled` (default `false`) |

```php
'pool_workers' => [
    'process' => [
        'enabled' => true,
        'max_workers' => env('IO_POOLS_PROCESS_WORKERS', 4),
    ],
    'threads' => [
        'enabled' => false,
        'max_workers' => env('IO_POOLS_THREAD_WORKERS', 4),
    ]
]
```

A disabled pool is not bound at all. Enabling the thread pool on a PHP build that is not ZTS, or without `ext-parallel` loaded, throws an `IOPoolsException` when the application boots. A process worker boots your application from its base path before it runs gigs, so a gig may use your application's services.

<a id="submitting-gigs"></a>
### Submitting Gigs

The pool's `submit` method hands a gig to an idle worker, spawns a new worker if the pool has room under `max_workers`, or queues the gig until a worker is free. It returns a promise for the gig's return value:

```php
use App\Gigs\ChecksumFile;

$promise = app('process-workers')->submit(new ChecksumFile('/var/log/system.log'));

$promise->then(function (string $checksum) {
    // ...
});
```

If the gig throws inside the worker, the promise is rejected with a `Voyager\Contracts\IOPools\WorkerPools\RemoteException`. Only strings cross back from the worker, so it carries the original exception's class in `remote_class` and its trace in `remote_trace`, and its message reads `{class}: {message}`. If the worker exits before the gig finishes, the promise is rejected with a `DeadWorkerException` quoting the worker's last output, and the pool replaces the worker for the gigs still queued. A gig that cannot be serialized is rejected with an `IOPoolsException` before any worker is spent on it.

The `warm` method spawns workers ahead of time, up to `max_workers`, so the first gigs don't pay for a worker's startup. `workerCount` returns how many workers are alive, and `shutDown` rejects queued gigs and stops every worker:

```php
$pool = app('process-workers');

$pool->warm(2);
```

<a id="how-the-loop-settles-pool-promises"></a>
### How the Loop Settles Pool Promises

A worker is a wake source. While it holds a gig, the pool registers it on the loop, watching the worker's output and its exit. When the result arrives, the worker settles the gig's promise in that turn, and the pool either hands it the next queued gig or takes it off the loop. An idle worker is not on the loop, so idle workers never keep `run()` alive: a loop whose only work was a gig ends once the gig's promise settles.

The pool registers its `shutDown` method with `onStop`, so when `run()` ends, gigs still queued or running are rejected and every worker is stopped.

You rarely submit gigs by hand. The `background` queue driver, the concurrency manager's `pool` driver, and the database, filesystem, cache and hashing offloading all build gigs and submit them for you; unless you name a pool, they use the thread pool when it is enabled and the process pool otherwise. See [Queues](/docs/{{version}}/framework/digging-deeper/queues#background) and [Concurrency](/docs/{{version}}/framework/digging-deeper/concurrency#running-tasks-without-blocking).

<a id="loop-mail"></a>
## Loop Mail

Resources often produce results nobody is waiting on with a promise: a line read from a socket, a row streamed from a query, a message popped from a Redis list. These are handed to the loop as mail, which can be any object. A resource hands over mail through its `pump` method, and you may post mail yourself with `post`:

```php
$loop->post(new LineArrived('hello'));
```

At the end of every turn of `run()`, the loop collects the turn's mail, oldest first, and gives it to the mail handler chosen by the `io-pools.event_loop.mail_handlers.default` option or the `IO_POOLS_MAIL_HANDLER` environment variable. The default `signal` handler dispatches each piece of mail through Signals, so you listen for it as you would any signal:

```php
app('signals')->listen(LineArrived::class, function (LineArrived $mail) {
    app('log')->info($mail->line);
});
```

A Rocket run switches the handler to `sketch`, which holds the mail and passes it to your sketch's `loop` method on its next frame. Mail is not delivered during the quiet turns of a [borrowed wait](#waiting-with-until); it is kept for the next turn of `run()`.

For the full picture, including which components send mail and how sketches receive it, see [Loop Mail](/docs/{{version}}/framework/the-basics/loop-mail).

<a id="configuration-reference"></a>
## Configuration Reference

Every option the loop reads lives in your `config/io-pools.php` file:

| Option | Environment variable | Default | Purpose |
| --- | --- | --- | --- |
| `event_loop.pace_ms` | `IO_POOLS_PACE_MS` | `16` | Longest wait while anything polled is registered |
| `event_loop.mail_handlers.default` | `IO_POOLS_MAIL_HANDLER` | `signal` | Where a turn's mail goes: `signal` or `sketch` |
| `pool_waiters.default` | `IO_POOLS_WAITER_BACKEND` | `auto` | Waiter backend: `auto`, `epoll`, `kqueue` or `select` |
| `promise_engines.default` | `IO_POOLS_PROMISE_ENGINE` | `guzzle` | Promise library: `guzzle` or `react` |
| `pool_workers.process.enabled` | — | `true` | Binds the `process-workers` pool |
| `pool_workers.process.max_workers` | `IO_POOLS_PROCESS_WORKERS` | `4` | Most process workers alive at once |
| `pool_workers.threads.enabled` | — | `false` | Binds the `thread-workers` pool |
| `pool_workers.threads.max_workers` | `IO_POOLS_THREAD_WORKERS` | `4` | Most thread workers alive at once |
