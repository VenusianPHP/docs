# Error Handling

How Venusian reports and renders exceptions: configuring the exception handler, reporting, log levels, ignoring, mapping and throttling, console rendering, and what happens to exceptions thrown on the event loop, in promises, in queued jobs and in worker pool gigs.

## Introduction

When something goes wrong in a Venusian application, an exception handler decides what happens to the exception. It reports it, which by default means writing it to your [logs](/docs/{{version}}/framework/the-basics/logging), and it renders it on the console when a Computer command or a sketch ends because of it.

A Venusian application is often a long-running process. A sketch may run for days on a device, and a lot of its work happens in timer callbacks, promise callbacks, fibers and worker pools rather than in one straight line of code. Most of this page is the same as it would be for a command-line tool; the last sections explain where an exception goes when it is thrown somewhere on the [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop), because the answer is different for each kind of work.

## Configuration

The exception handler is `Voyager\Core\Exceptions\Handler`, bound in the container as `Voyager\Contracts\Debug\ExceptionHandler`. You configure it in your application's `bootstrap/app.php` file with the `withExceptions` method. Its closure receives a `Voyager\Core\Bootstrap\Exceptions` instance, and every method on this page is called on that object:

```php
use Voyager\Core\Bootstrap\Exceptions;
use Voyager\Core\VenusianVoyager;

return VenusianVoyager::setup(base_path: dirname(__DIR__))
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })
    ->withSketches([__DIR__.'/../app/Runner/Sketches'])
    ->create();
```

The closure runs the first time the handler is resolved, before it handles its first exception. If your application file does not call `withExceptions` at all, `create` binds the same handler with no configuration, so there is always a handler to report to.

## Handling Exceptions

### Reporting Exceptions

Exception reporting is used to log exceptions or send them to an external service. By default, an exception is written to your default log channel at the `error` level, with the exception itself in the log context. You are free to log exceptions however you wish.

If you need to report different types of exceptions in different ways, you may use the `report` method to register a closure that should be executed when an exception of a given type needs to be reported. Venusian will determine what type of exception the closure reports by examining the type-hint of the closure:

```php
use App\Exceptions\SensorTimeout;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->report(function (SensorTimeout $e) {
        // ...
    });
})
```

When you register a custom exception reporting callback using the `report` method, Venusian will still log the exception using the default logging configuration. If you wish to stop the propagation of the exception to the default logging stack, you may use the `stop` method when defining your reporting callback or return `false` from the callback:

```php
use App\Exceptions\SensorTimeout;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->report(function (SensorTimeout $e) {
        // ...
    })->stop();

    $exceptions->report(function (SensorTimeout $e) {
        return false;
    });
})
```

Callbacks run in the order you register them. A callback that stops propagation also stops the callbacks registered after it. `reportable` is an alias of `report`.

> [!NOTE]
> To customize the exception reporting for a given exception, you may also define a `report` method [on the exception itself](#reportable-exceptions).

#### The `report` Helper

Sometimes you may need to report an exception but continue running. The `report` helper sends an exception through the handler without throwing it, so your code carries on:

```php
public function loop(array $mail = []): SketchLoopResult
{
    try {
        $this->sensor->read();
    } catch (Throwable $e) {
        report($e);
    }

    return SketchLoopResult::CONTINUE;
}
```

You may also pass a string. Venusian wraps it in an `Exception` and reports that:

```php
report('The sensor stopped answering.');
```

#### The `rescue` Helper

The `rescue` helper runs a closure and catches any exception it throws. The exception is reported, and `rescue` returns `null`, or the result of the fallback closure you pass as the second argument, which receives the exception:

```php
$reading = rescue(fn () => $this->sensor->read());

$reading = rescue(
    fn () => $this->sensor->read(),
    fn (Throwable $e) => $this->lastReading,
);
```

The third argument decides whether the exception is reported. Pass `false` to rescue quietly, or a closure that receives the exception and returns whether to report it:

```php
$reading = rescue(fn () => $this->sensor->read(), fn () => null, report: false);
```

> [!WARNING]
> Pass the fallback as a closure. The second argument accepts a callable, a `bool` or `null`, so a plain string or number given as the fallback is converted to `true` and `rescue` returns `true` instead of your value.

#### Global Log Context

The `context` method registers a closure whose array is added to the log context of every reported exception. It receives the exception and the context built so far:

```php
->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->context(fn (Throwable $e, array $context) => [
        'device' => gethostname(),
    ]);
})
```

#### Exception Log Context

While adding context to every log message can be useful, sometimes a particular exception may have unique context that you would like to include in your logs. By defining a `context` method on one of your application's exceptions, you may specify any data relevant to that exception that should be added to the exception's log entry:

```php
<?php

namespace App\Exceptions;

use Exception;

class SensorTimeout extends Exception
{
    public function __construct(public readonly string $address, string $message = '')
    {
        parent::__construct($message);
    }

    /**
     * Get the exception's context information.
     *
     * @return array<string, mixed>
     */
    public function context(): array
    {
        return ['address' => $this->address];
    }
}
```

#### Deduplicating Reported Exceptions

If you use the `report` helper throughout your application, you may occasionally report the same exception multiple times, creating duplicate entries in your logs. To ensure that a single instance of an exception is only ever reported once, you may invoke the `dontReportDuplicates` method:

```php
->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->dontReportDuplicates();
})
```

Now, when the `report` helper is called with the same instance of an exception, only the first call will be reported. A different instance of the same exception class is still reported.

### Exception Log Levels

When messages are written to your application's [logs](/docs/{{version}}/framework/the-basics/logging), the messages are written at a specified [log level](/docs/{{version}}/framework/the-basics/logging#log-levels), which indicates the severity or importance of the message being logged.

As noted above, even when you register a custom exception reporting callback using the `report` method, Venusian will still log the exception using the default logging configuration for the application. However, since the log level can sometimes influence the channels on which a message is logged, you may wish to configure the log level that certain exceptions are logged at.

To accomplish this, you may use the `level` method. This method receives the exception type as its first argument and the log level as its second argument:

```php
use PDOException;
use Psr\Log\LogLevel;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->level(PDOException::class, LogLevel::CRITICAL);
})
```

Exceptions without a level of their own are logged at `error`.

### Ignoring Exceptions by Type

When building your application, there will be some types of exceptions you never want to report. To ignore these exceptions, you may use the `dontReport` method. Any class provided to this method will never be reported, and neither will its subclasses:

```php
use App\Exceptions\SensorTimeout;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->dontReport([
        SensorTimeout::class,
    ]);
})
```

Alternatively, you may simply "mark" an exception class with the `Voyager\Contracts\Debug\ShouldntReport` interface. When an exception is marked with this interface, it will never be reported by Venusian's exception handler:

```php
<?php

namespace App\Exceptions;

use Exception;
use Voyager\Contracts\Debug\ShouldntReport;

class SensorTimeout extends Exception implements ShouldntReport
{
    //
}
```

If you need even more control over when a particular type of exception is ignored, you may provide a closure to the `dontReportWhen` method. The exception is ignored when the closure returns `true`:

```php
use App\Exceptions\SensorTimeout;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->dontReportWhen(function (Throwable $e) {
        return $e instanceof SensorTimeout && $e->address === '0x48';
    });
})
```

Internally, Venusian already ignores the database's "not found" exceptions for you: `Voyager\Database\Instrument\ModelNotFoundException`, `Voyager\Database\RecordNotFoundException`, `Voyager\Database\RecordsNotFoundException` and `Voyager\Database\MultipleRecordsFoundException`. If you would like to report one of them, use the `stopIgnoring` method:

```php
use Voyager\Database\Instrument\ModelNotFoundException;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->stopIgnoring(ModelNotFoundException::class);
})
```

You may ask the handler whether an exception would be reported with its `shouldReport` method:

```php
use Voyager\Contracts\Debug\ExceptionHandler;

if (app(ExceptionHandler::class)->shouldReport($e)) {
    // ...
}
```

### Mapping Exceptions

The `map` method turns one exception into another before it is reported. This is useful for wrapping a library's exception in one of your own, so it is logged, leveled and ignored by your rules. Pass the class to map and a closure that builds the replacement:

```php
use App\Exceptions\PanelOffline;
use PDOException;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->map(PDOException::class, fn (PDOException $e) => new PanelOffline('The panel database is offline.', 0, $e));
})
```

You may instead pass only a closure, and the class it handles is read from its type-hint. Or pass two class names, and the replacement is built as `new $to('', 0, $e)`, with the original as its previous exception.

### Throttling Reported Exceptions

If your application reports a very large number of exceptions, for example when a sensor fails and every frame of a sketch reports the same error, you may want to throttle how many exceptions are actually logged.

To take a random sample rate of exceptions, use the `throttle` method and return a `Voyager\NutsAndBolts\Lottery` instance:

```php
use Voyager\NutsAndBolts\Lottery;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->throttle(function (Throwable $e) {
        return Lottery::odds(1, 1000);
    });
})
```

It is also possible to conditionally sample based on the exception type. If you would like to only sample instances of a specific exception class, you may return a `Lottery` instance only for that class, or type-hint the closure with it:

```php
use App\Exceptions\SensorTimeout;
use Voyager\NutsAndBolts\Lottery;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->throttle(function (SensorTimeout $e) {
        return Lottery::odds(1, 1000);
    });
})
```

You may also rate limit exceptions by returning a `Voyager\Cache\RateLimiting\Limit` instead of a `Lottery`. Rate limiting counts reports with the cache's rate limiter, so the count lives in your default [cache](/docs/{{version}}/framework/digging-deeper/cache) store; with a shared store such as `redis`, every process using it shares one limit:

```php
use App\Exceptions\SensorTimeout;
use Voyager\Cache\RateLimiting\Limit;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->throttle(function (SensorTimeout $e) {
        return Limit::perMinute(30);
    });
})
```

By default, limits use the exception's class as the rate limit key. You may customize this by specifying your own key using the `by` method on the `Limit`:

```php
->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->throttle(function (SensorTimeout $e) {
        return Limit::perMinute(30)->by($e->address);
    });
})
```

Return `null` from a throttle closure, or `Limit::none()`, to leave that exception unthrottled.

### Reportable Exceptions

Instead of registering a callback, you may define a `report` method directly on your exception. When it exists, the handler calls it instead of logging the exception. Its dependencies are injected by the [service container](/docs/{{version}}/framework/architecture-concepts/container):

```php
<?php

namespace App\Exceptions;

use Exception;

class SensorTimeout extends Exception
{
    /**
     * Report the exception.
     */
    public function report(): void
    {
        // ...
    }
}
```

If the method returns `false`, the exception continues to your report callbacks and the default logging, as if the method were not there. The `make:exception` command creates an exception class in `app/Exceptions`, and its `--report` option adds an empty `report` method:

```shell
php computer make:exception SensorTimeout --report
```

## Rendering Exceptions on the Console

When a Computer command or a sketch ends because of an exception, the kernel reports it, then renders it to the console with the handler's `renderForConsole` method, and the process exits with status `1`. The exception is rendered as a highlighted block with its message and the file and line it was thrown from. Run the command with `-v`, `-vv` or `-vvv` to include the exception's class and its stack trace.

When you mistype a command name, the handler renders a short error instead, and lists the commands with similar names when there are any:

```shell
php computer config:clr
```

PHP warnings, notices and errors that happen while your code runs are turned into `ErrorException` instances, so they are reported and rendered like any other exception. Deprecation warnings are not thrown: they are written to the deprecations log channel, as described in [Logging Deprecation Warnings](/docs/{{version}}/framework/the-basics/logging#logging-deprecation-warnings).

Fatal errors, such as running out of memory, cannot be caught. Venusian reserves a little memory when it boots, so that when PHP shuts down after a fatal error it can still report the error and render it to the console.

## Exceptions on the Event Loop

Work on the event loop runs in callbacks rather than in one call stack, so there is no single `try` block around all of it. Each kind of work hands its exceptions somewhere specific.

### In a Sketch's Loop Body

An exception thrown from a sketch's `boot` or `loop` method ends the sketch. The sketch runner calls your sketch's `shutdown` method exactly once, and the exception continues up to Rocket's kernel, which reports it, renders it, and exits with status `1`. The same happens when `boot` throws, except that no frame runs at all. See [Continuing and Stopping](/docs/{{version}}/framework/the-basics/sketches#continuing-and-stopping).

If one bad frame should not end the sketch, catch the exception inside `loop` and report it with the [`report` helper](#the-report-helper), so the sketch keeps running and the failure is still logged. When the same failure repeats every frame, [throttle](#throttling-reported-exceptions) its reports.

### In Loop Callbacks

Timer callbacks, repeating timers, ticks, and the wake handlers of loop resources run inside a turn of the loop. If one of them throws, the loop finishes the rest of the turn, so one failing callback does not starve the others, and then rethrows the first exception the turn raised. That ends `run()`: the loop's `onStop` hooks still run, and the exception continues to whoever called `run()`.

```php
$loop = app('event-loop');

$loop->at(0.5, function () {
    throw new RuntimeException('The sensor did not answer.');
});

try {
    $loop->run();
} catch (RuntimeException $e) {
    // The loop has stopped...
}
```

Under Rocket, the code that called `run()` is the sketch runner, so an exception from any loop callback ends the sketch just as one from `loop` does. Inside a Computer command, it ends the command.

The same applies to loop mail when it is handed off as signals, which is the default under Computer. A [signal listener](/docs/{{version}}/framework/digging-deeper/signals) that throws while handling a piece of mail ends `run()` the same way.

An exception thrown by an `onStop` hook is discarded, so one failing hook never stops the others from running.

### In Promises

A promise holds its exception rather than throwing it. A callback passed to `then` that throws rejects the promise `then` returned, and the rejection passes down the chain until a callback registered with `error` receives it. Whatever that callback returns fulfills the next promise, so the chain recovers:

```php
app('event-loop')->defer(fn () => $this->sensor->read())
    ->then(function (array $reading) {
        return $this->calibrate($reading);
    })
    ->error(function (Throwable $e) {
        report($e);

        return null;
    });
```

The `wait` method throws the rejection where you wait:

```php
try {
    $body = $promise->wait();
} catch (Throwable $e) {
    // ...
}
```

> [!WARNING]
> A rejected promise that nobody waits on and that has no `error` callback is not reported anywhere: the loop keeps running and the exception is silently dropped. Give every promise you start and do not wait on an `error` callback, and call `report` there if the failure should be logged.

Work you start with the loop's `defer` method, and fibers you start with `async`, follow the same rule. An exception thrown inside them rejects the promise or task they return, and never ends the loop. See [Deferring Work](/docs/{{version}}/framework/architecture-concepts/event-loop#deferring-work) and [Fibers](/docs/{{version}}/framework/architecture-concepts/event-loop#fibers).

### In Worker Pool Gigs

A gig runs in another process or thread, and exception objects do not cross back from it. When a gig's `handle` method throws, the gig's promise is rejected with a `Voyager\Contracts\IOPools\WorkerPools\RemoteException`. Its `remote_class` property holds the original exception's class, its `remote_trace` property holds the original stack trace as a string, and its message reads `{class}: {message}`:

```php
use App\Gigs\ChecksumFile;
use Voyager\Contracts\IOPools\WorkerPools\RemoteException;

app('process-workers')->submit(new ChecksumFile($path))
    ->error(function (Throwable $e) {
        if ($e instanceof RemoteException && $e->remote_class === ValueError::class) {
            // ...
        }

        report($e);
    });
```

The worker keeps running after a gig throws and takes the next gig. Two other failures reject a gig's promise without the gig having thrown:

- A gig that cannot be serialized is rejected with a `Voyager\Contracts\IOPools\IOPoolsException` before any worker is spent on it.
- If the worker exits before the gig finishes, the promise is rejected with a `Voyager\Contracts\IOPools\WorkerPools\DeadWorkerException` quoting the worker's last output, and the pool replaces the worker.

When the loop stops, gigs still queued or running are rejected as well. See [Submitting Gigs](/docs/{{version}}/framework/architecture-concepts/event-loop#submitting-gigs).

## Exceptions in Queued Jobs

Where a job's exception goes depends on where the job runs:

- **A queue worker** (`queue:work`) reports the exception through your exception handler, then releases the job back onto the queue to be attempted again, or marks it failed once it has used its attempts. A failed job's `failed` method runs, the `Voyager\Queue\Signals\JobFailed` signal is dispatched, and the job is recorded in failed job storage. The worker itself keeps running. See [Error Handling](/docs/{{version}}/framework/digging-deeper/queues#error-handling) and [Dealing With Failed Jobs](/docs/{{version}}/framework/digging-deeper/queues#dealing-with-failed-jobs) on the Queues page.
- **The `sync` connection** runs the job immediately. When it throws, the job's `failed` method runs and the exception is thrown back to the code that dispatched it. Nothing is recorded in failed job storage.
- **The `deferred` connection** runs the job on the loop's next turn. When it throws, the job's `failed` method runs and the promise the push returned is rejected with the original exception.
- **The `background` connection** runs the job in a pool worker. When it throws, the job's `failed` method runs in the worker, and the push's promise is rejected with a `RemoteException`, as for any [gig](#in-worker-pool-gigs).

The `deferred` and `background` connections hand their promise back only when you push through the queue manager, as in `app('queue')->connection('background')->push($job)`. Add an `error` callback to that promise if a failure should be reported in your own process:

```php
app('queue')->connection('background')->push(new RecordDelivery($order))
    ->error(fn (Throwable $e) => report($e));
```
