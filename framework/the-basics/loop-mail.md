# Loop Mail

How results and input travel from the event loop to your code: posting and pumping mail, the signal and sketch mail handlers, and the mail the framework delivers.

## Introduction

Much of the work in a Venusian application finishes somewhere other than the code that started it. A worker pool returns a page of query results, a Redis list receives a value, a set of concurrent tasks settles, a file is read a chunk at a time. The [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop) collects each of these results as **mail** and delivers it to your application at the end of a loop turn.

Mail is how input reaches your code without your code having to wait for it. Something on the loop puts a piece of mail in the loop's bag; at the end of the turn, the loop hands everything in the bag to its **mail handler**, which decides where it goes. Venusian ships two handlers:

- The `signal` handler dispatches each piece of mail as a [signal](/docs/{{version}}/framework/digging-deeper/signals), so any listener may receive it. This is the default for `php computer` runs and for anything else that runs the loop itself.
- The `sketch` handler holds the mail for the running [sketch](/docs/{{version}}/framework/the-basics/sketches), which receives it as the `$mail` argument of its next `loop` call. Every `php rocket` run uses it.

## What Counts as Mail

Any object can be mail. There is no base class or interface to implement, and the loop never inspects what it carries. A small readonly class with public properties is the usual shape:

```php
<?php

namespace App\Mail;

final readonly class ReadingTaken
{
    public function __construct(
        public string $sensor,
        public float $value,
    ) {}
}
```

Because the `signal` handler dispatches mail as signals, a mail class may implement `Voyager\Contracts\Signals\NamedSignal` to choose the name it is dispatched under. Every piece of mail the framework itself produces does this, so you may listen for it by a name such as `db-chunk:sqlite:users` instead of by class:

```php
<?php

namespace App\Mail;

use Voyager\Contracts\Signals\NamedSignal;

final readonly class ReadingTaken implements NamedSignal
{
    public function __construct(
        public string $sensor,
        public float $value,
    ) {}

    public function name(): string
    {
        return 'reading:'.$this->sensor;
    }
}
```

The name only matters to the `signal` handler. A sketch receives the object itself.

## Sending Mail

There are two ways to put mail in the loop's bag: post it, or return it from a pumpable resource.

### Posting Mail

The loop's `post` method queues one piece of mail for the next delivery. The loop is registered in the container as `event-loop` and may be injected as `Voyager\Contracts\IOPools\Loop`:

```php
use App\Mail\ReadingTaken;

app('event-loop')->post(new ReadingTaken('greenhouse', 21.5));
```

`post` returns at once. The mail is delivered at the end of the current loop turn, or at the end of the first turn once the loop starts running, so it is safe to post from a timer callback, a promise callback, a signal listener, or a sketch frame. Mail posted from inside a mail listener goes out on the next turn, never in the middle of the delivery that is running.

### Pumpable Resources

A loop resource that produces mail of its own implements `Voyager\Contracts\IOPools\Pumpable`. Its single method, `pump`, returns the mail the resource has collected since it was last asked, as a list of objects. The loop calls `pump` on every pumpable resource near the end of every turn, after timers, wakes, and promises have run, and once more when the resource is forgotten, so nothing a resource collected is lost when it leaves the loop.

`Pumpable` does not make a class a loop resource by itself. The resource must also be one of the loop's resource kinds, such as a `Voyager\IOPools\Resources\WakeSource`, which the loop wakes when one of its streams is ready. The following resource reads lines from a stream, such as `STDIN`, and delivers each line as mail. The mail it delivers is a small class of its own:

```php
<?php

namespace App\Mail;

final readonly class LineReceived
{
    public function __construct(
        public string $line,
    ) {}
}
```

The resource wakes whenever the stream is readable, keeps each complete line, and hands the lines over when the loop pumps it:

```php
<?php

namespace App\Loop;

use App\Mail\LineReceived;
use Voyager\Contracts\IOPools\Loop;
use Voyager\Contracts\IOPools\Pumpable;
use Voyager\IOPools\Resources\WakeSource;
use Voyager\IOPools\Waiter\Wakes\Readable;

final class LineReader extends WakeSource implements Pumpable
{
    /** @var list<LineReceived> */
    private array $received = [];

    private string $buffer = '';

    /**
     * @param resource $stream
     */
    public function __construct(
        private Loop $loop,
        private string $name,
        private mixed $stream,
    ) {
        stream_set_blocking($stream, false);
    }

    /**
     * Wake this resource whenever the stream has bytes to read.
     */
    public function wakes(): array
    {
        return [new Readable($this->stream)];
    }

    /**
     * Read what arrived and keep each complete line as mail.
     */
    public function woke(array $fired): void
    {
        $this->buffer .= (string) fread($this->stream, 65536);

        while (($end = strpos($this->buffer, "\n")) !== false) {
            $this->received[] = new LineReceived(substr($this->buffer, 0, $end));
            $this->buffer = substr($this->buffer, $end + 1);
        }

        if (feof($this->stream)) {
            if ($this->buffer !== '') {
                $this->received[] = new LineReceived($this->buffer);
                $this->buffer = '';
            }

            // Leaving the loop pumps one last time, so the final lines are still delivered.
            $this->loop->forget($this->name);
        }
    }

    /**
     * Hand the loop every line received since it last asked.
     */
    public function pump(): array
    {
        [$mail, $this->received] = [$this->received, []];

        return $mail;
    }
}
```

Register the resource on the loop under a name, and every line typed or piped into the process is delivered as a `LineReceived` piece of mail:

```php
use App\Loop\LineReader;

$loop = app('event-loop');

$loop->resource('stdin', new LineReader($loop, 'stdin', STDIN));
```

The resource kinds, wakes, and the `forget` method are covered in the [Event Loop](/docs/{{version}}/framework/architecture-concepts/event-loop) documentation.

### When Mail Is Delivered

Mail is collected in the order it arrived: mail posted during a turn comes first, followed by whatever the pumpable resources return at the end of that turn. The whole bag is handed to the mail handler once per turn, and each piece is delivered exactly once.

Only turns of `run` deliver mail. When you block on a promise with `wait`, or wait on a condition with the loop's `until` method, the loop turns without delivering anything, so a listener never fires in the middle of the code that is waiting. Mail that arrives during such a wait stays in the bag and is delivered at the end of the next turn of `run`.

Mail does not keep the loop running. `run` turns for as long as the loop has work, such as a timer, a watched stream, or a worker pool with gigs in flight, and returns as soon as it has none. Mail still in the bag at that point stays there until a later `run` turns again:

```php
$loop = app('event-loop');

$loop->post(new ReadingTaken('greenhouse', 21.5));

$loop->run(); // returns at once: nothing else to do, so nothing is delivered

$loop->at(0.5, fn () => null);

$loop->run(); // the first turn delivers ReadingTaken
```

The framework's own mail is posted by work the loop is already waiting on, such as a worker returning a page or a socket returning a value. When that work finishes during `run`, its mail goes out at the end of the same turn, before `run` can run out of work. When it finishes during a `wait`, the mail waits for the next `run`, as described above. A sketch never runs out of work while it runs: its frame timer is always set, so a sketch receives each piece of mail on the frame after it arrives, even when an earlier frame blocked on a promise.

## Mail Handlers

### Choosing a Handler

The loop is built with one mail handler, named by the `mail_handlers.default` option under `event_loop` in your `config/io-pools.php` file. It reads the `IO_POOLS_MAIL_HANDLER` environment variable and defaults to `signal`:

```php
'event_loop' => [
    'pace_ms' => env('IO_POOLS_PACE_MS', 16),
    'mail_handlers' => [
        'default' => env('IO_POOLS_MAIL_HANDLER', 'signal'),
    ],
],
```

Rocket does not use this setting. Every `php rocket` run sets `io-pools.event_loop.mail_handlers.default` to `sketch` right after the configuration is loaded, before any service provider can build the loop, so the running sketch always receives the loop's mail.

The handler is chosen when the loop is first built, and the loop is built once per process. Changing the configuration value after something has resolved `event-loop` does not change where its mail goes.

### The Signal Handler

The `signal` handler, `Voyager\IOPools\MailHandlers\SignalMailHandler`, dispatches each piece of mail through the `signals` dispatcher, one at a time, in the order the pieces arrived. Each piece is dispatched as a signal object, so it reaches every listener a signal of its type would:

- listeners registered for its class name, or for an interface it implements;
- closure listeners whose first parameter is typed with its class;
- for a `NamedSignal`, listeners registered for the name its `name` method returns;
- [wildcard listeners](/docs/{{version}}/framework/digging-deeper/signals#wildcard-listeners) matching any of those names.

A listener registered under more than one of those names still hears each piece once.

### The Sketch Handler

The `sketch` handler, `Voyager\IOPools\MailHandlers\SketchMailHandler`, keeps every piece of mail it is handed until the sketch runner takes it. On each frame the runner takes everything the handler is holding, oldest first, and passes it to the sketch's `loop` method; the handler is then empty until more mail arrives. Nothing is dispatched as a signal, so signal listeners do not receive loop mail during a Rocket run.

### Writing a Mail Handler

A mail handler implements `Voyager\Contracts\IOPools\MailHandler`. Its `handOff` method receives the turn's mail, oldest first, along with the loop that delivered it:

```php
<?php

namespace App\Loop;

use Voyager\Contracts\IOPools\Loop;
use Voyager\Contracts\IOPools\MailHandler;

final class LoggingMailHandler implements MailHandler
{
    /**
     * @param list<object> $mail
     */
    public function handOff(array $mail, Loop $loop): void
    {
        foreach ($mail as $piece) {
            app('log')->debug('Loop mail', ['type' => $piece::class]);

            app('signals')->dispatch($piece);
        }
    }
}
```

Handlers are drivers of the mail handler manager, which is registered in the container as `mail-handler-mgr`. Register your driver with the manager's `extend` method in the `register` method of a [service provider](/docs/{{version}}/framework/architecture-concepts/providers), which runs before anything builds the loop:

```php
use App\Loop\LoggingMailHandler;

/**
 * Register any application services.
 */
public function register(): void
{
    $this->app['mail-handler-mgr']->extend('logging', fn ($app) => new LoggingMailHandler());
}
```

Then select it in your application's `.env` file:

```ini
IO_POOLS_MAIL_HANDLER=logging
```

A custom handler applies to `php computer` runs and to any other code that runs the loop itself. Rocket always uses the `sketch` handler.

## Receiving Mail

### Receiving Mail as a Signal

When the `signal` handler is in use, receive mail by listening for it on the `signals` dispatcher, usually in the `boot` method of a service provider. You may listen by class or, for a named piece of mail, by its name:

```php
use App\Mail\ReadingTaken;

app('signals')->listen(function (ReadingTaken $reading) {
    // $reading->sensor, $reading->value...
});

app('signals')->listen('reading:greenhouse', function (ReadingTaken $reading) {
    // Only the greenhouse sensor...
});

app('signals')->listen('reading:*', function (string $name, array $data) {
    // Every sensor; $data[0] is the ReadingTaken...
});
```

Listeners only run while the loop is running, so the code that starts the work runs the loop afterwards. A Computer command that streams a table and reports each page looks like this:

```php
<?php

namespace App\Console\Commands;

use Voyager\Console\Command;
use Voyager\Database\IOPools\QueryChunk;

class CountActiveUsers extends Command
{
    protected ?string $signature = 'users:count-active';

    protected string $description = 'Count active users a page at a time.';

    public function handle(): int
    {
        app('signals')->listen('db-chunk:sqlite:users', function (QueryChunk $chunk) {
            $this->info("Page {$chunk->page}: {$chunk->rows->count()} users");
        });

        app('db')->table('users')->where('active', 1)->stream(500)
            ->then(fn (int $total) => $this->info("{$total} active users"));

        return app('event-loop')->run();
    }
}
```

The `run` method returns once the loop has no work left: here, after the last page has been delivered and the stream's promise has settled. Promise callbacks run before the turn's mail is handed off, so the promise may settle while the final pages are still on their way to your listener; use a chunk's `last` flag, not the promise, to know the final page has arrived.

### Receiving Mail in a Sketch

During a Rocket run, mail arrives as the `$mail` argument of your sketch's `loop` method: every piece delivered since the previous frame, oldest first, or an empty array when nothing arrived. Match each piece by its class:

```php
<?php

namespace App\Runner\Sketches;

use App\Mail\ReadingTaken;
use Voyager\Concurrency\ConcurrencyResults;
use Voyager\Contracts\Sketches\SketchLoopResult;
use Voyager\Database\IOPools\QueryChunk;

class Dashboard extends Sketch
{
    protected string $description = 'Show readings as they arrive.';

    public function loop(array $mail = []): SketchLoopResult
    {
        foreach ($mail as $piece) {
            match (true) {
                $piece instanceof ReadingTaken => $this->line("{$piece->sensor}: {$piece->value}"),
                $piece instanceof QueryChunk => $this->info("Loaded page {$piece->page}"),
                $piece instanceof ConcurrencyResults && $piece->name === 'forecast' => $this->line('Forecast: '.json_encode($piece->results)),
                default => null,
            };
        }

        return SketchLoopResult::CONTINUE;
    }
}
```

If you would rather keep the logic in listeners, a sketch may hand its mail on to the `signals` dispatcher itself. Each piece is then dispatched exactly as the `signal` handler would have dispatched it:

```php
public function loop(array $mail = []): SketchLoopResult
{
    foreach ($mail as $piece) {
        app('signals')->dispatch($piece);
    }

    return SketchLoopResult::CONTINUE;
}
```

## Mail the Framework Delivers

Several framework APIs report their results as mail. Each mail class implements `NamedSignal`, so with the `signal` handler you may listen for it by name, and in a sketch you may match it by class.

| Mail | Produced by | Signal name | Properties |
|---|---|---|---|
| `Voyager\Database\IOPools\QueryChunk` | A query builder's or Instrument query's `stream` method | `db-chunk:{connection}:{table}` | `connection`, `table`, `page`, `rows`, `last` |
| `Voyager\Filesystem\FileChunk` | `stream` on an offloaded disk or offloaded local filesystem | `disk:{disk}:{path}`, or `file:{path}` for the local filesystem | `source`, `path`, `offset`, `bytes`, `last` |
| `Voyager\Redis\RedisMessage` | A `Voyager\Redis\Lists\ListPop` resource from `app('redis')->listPop()` | `redis:{key}` | `key`, `raw` |
| `Voyager\Concurrency\ConcurrencyResults` | `app('concurrency')->async()`, once every task has settled | `concurrency:{name}` | `name`, `results`, `failures` |

### Query Chunks

The `stream` method pages through a query in a worker and posts each page as a `QueryChunk`. `page` counts from `1`, `rows` holds the page's rows (an Instrument collection for a model query), and `last` is `true` on the final page. A query that matches nothing still delivers one empty page marked `last`:

```php
app('db')->table('users')->where('active', 1)->stream(500);
```

See [Streaming Results as Signals](/docs/{{version}}/framework/database/queries#streaming-results-as-signals) and [Streaming Models](/docs/{{version}}/framework/instrument-orm/instrument#streaming-models).

### File Chunks

The `stream` method of an offloaded disk reads a file a chunk at a time, 1 MiB by default, and posts each chunk as a `FileChunk`. `offset` is where the chunk starts in the file, `bytes` holds its contents, and `last` marks the final chunk:

```php
storage()->disk('local')->via()->stream('exports/large.bin');
```

See [Streaming a File as Mail](/docs/{{version}}/framework/digging-deeper/filesystem#streaming-a-file-as-mail).

### Redis Messages

A `ListPop` resource pops a Redis list with `BLPOP` while it is registered on the loop. It is a pumpable resource: each popped value comes out of its `pump` method as a `RedisMessage` carrying the list's `key` and the `raw` bytes Redis stored:

```php
app('event-loop')->resource('jobs', app('redis')->listPop('jobs'));
```

See [Popping a List as Mail](/docs/{{version}}/framework/database/redis#popping-a-list-as-mail).

### Concurrency Results

`app('concurrency')->async()` runs a batch of tasks without blocking. When every task has settled, it posts a `ConcurrencyResults` named after the batch (`default` when you give no name): `results` holds the tasks that returned and `failures` the exceptions of the tasks that threw, both keyed as the tasks were, and `successful()` tells you whether nothing failed:

```php
app('concurrency')->async([
    'users' => fn () => app('db')->table('users')->count(),
    'orders' => fn () => app('db')->table('orders')->count(),
], 'counts');
```

See [Results as Loop Mail](/docs/{{version}}/framework/digging-deeper/concurrency#results-as-loop-mail).

### Window and Toolkit Mail

Windows, input devices, and toolkit widgets deliver their own mail through Surface; see the [Surface documentation](/docs/{{version}}/surface/overview).
