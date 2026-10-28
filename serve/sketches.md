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

<a id="stopping-the-server"></a>
## Stopping the Server

`drain($timeout)` stops taking connections, answers the requests in flight, and returns a promise that settles once they are done or the timeout passes. To stop on the sketch's own terms rather than on a signal, call it from `loop()` and return `STOP` once it settles. `stop()` is the same without the deadline or the promise: it stops taking connections, closes the idle ones, and leaves the loop once the requests in flight are answered.
