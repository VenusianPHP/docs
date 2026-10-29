# Serving From a Sketch

Serve your application over HTTP from inside a running sketch, on the sketch's own event loop.

## Introduction

A [sketch](/docs/{{version}}/framework/the-basics/sketches) that runs for a while, such as a dashboard for hardware it drives, can serve the application's routes itself. The server is attached to the sketch's event loop, so the routes, services and state it serves are the sketch's own, with no second boot, and the sketch decides when serving starts and stops. Each request runs in its own scope, so the sketch's scoped instances are untouched.

<a id="starting-the-server"></a>
## Starting the Server

Make an `HttpServer` from the container. It takes `config/serve.php`, or the options you pass:

```php
use Mariner\Core\Server\HttpServer;
use Mariner\Core\Server\ServerOptions;
use Voyager\Contracts\Sketches\SketchLoopResult;
use Voyager\Sketches\Sketch;

final class Dashboard extends Sketch
{
    private ?HttpServer $server = null;

    private bool $done = false;

    public function boot(): void
    {
        $loop = app('event-loop');

        $this->server = app(HttpServer::class, ['options' => new ServerOptions(port: 8080)])
            ->listen()
            ->attach($loop);

        // Ctrl-C: answer what is in flight, then stop; shutdown() still runs afterwards.
        $loop->onStopSignal(function () {
            $this->server->drain(5.0)->then(fn () => $this->done = true);

            return true;
        });
    }

    public function loop(array $mail = []): SketchLoopResult
    {
        // ... the sketch's own work, every frame ...

        return $this->done ? SketchLoopResult::STOP : SketchLoopResult::CONTINUE;
    }

    public function shutdown(): void
    {
        // the sketch's own cleanup
    }
}
```

`ServerOptions` takes the same settings as [config/serve.php](/docs/{{version}}/serve/serving#configuration), as named arguments.

<a id="from-a-package"></a>
## From a Package

A package that serves over HTTP but does not require all of `venusian/serve` resolves the `Mariner\Contracts\Server\HttpServer` contract from `venusian-mariner/contracts` instead. The container makes the same server for it, and its `options` take plain config keys, laid over `config/serve.php`, so the package never names a `Mariner\Core` class:

```php
use Mariner\Contracts\Server\HttpServer;

$server = app(HttpServer::class, ['options' => ['port' => 0, 'host' => '127.0.0.1']])
    ->attach(app('event-loop'));

$server->port();                     // the port the system picked for 0
$server->onRequest(fn ($served) => logger()->info("{$served->method} {$served->path} {$served->status}"));
```

The contract declares `listen()`, `port()`, `attach($loop)`, `onRequest($observer)`, `stop()` and `drain($timeout)`, the same calls as the class, and `attach()` listens for you. Keys you leave out come from `config/serve.php`.

<a id="stopping-the-server"></a>
## Stopping the Server

`drain($timeout)` stops taking connections, answers the requests in flight, and returns a promise that settles once they are done or the timeout passes. To stop on the sketch's own terms rather than on a signal, call it from `loop()` and return `STOP` once it settles. `stop()` is the same without the deadline or the promise: it stops taking connections, closes the idle ones, and leaves the loop once the requests in flight are answered.
