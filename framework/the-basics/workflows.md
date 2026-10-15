# Workflows

Build application behaviour as small logic nodes wired into decision graphs, then run them as flows, blocking or on the event loop.

## Introduction

Most of what an application does is a sequence of decisions: load something, look at it, then do one of several things depending on what you found. Written inline, that logic ends up as one long method full of branches. Venusian's workflows let you split it into independent **nodes**, each doing one job, and wire those nodes into a graph that decides which one runs next. A **flow** walks the graph.

Because each node only says *what happened* (an action name such as `approve` or `reject`) and the graph says *where that leads*, you can rearrange the decision tree without touching the nodes. Graphs may loop back on themselves, which makes them a natural fit for agentic loops: a "decide" node that picks a tool, a node per tool, and an edge from every tool back to "decide" until it answers.

Workflows live in the `Voyager\Workflows` namespace. Venusian uses them itself: the `install:ext` command runs a `Flow` of six nodes that check which extensions are already loaded, find `php-config`, find or install PIE, let you select extensions, and install them.

Throughout this page we'll build one workflow, a small editorial pipeline that reviews a draft, sends it back for revision when it is too short, archives it when it is spam, and publishes it otherwise.

## Generating Nodes

To create a node, use the `make:node` Computer command. The class is written into `app/Workflows`, in the `App\Workflows` namespace:

```shell
php computer make:node ReviewDraft
```

A name with a slash writes into a subdirectory, and the `--async` (`-a`) option generates an [async node](#async-nodes) instead. An existing file is left untouched unless you pass `--force` (`-f`):

```shell
php computer make:node Drafts/FetchDraft --async

php computer make:node ReviewDraft --force
```

The generated class extends `Voyager\Workflows\Node` (or `Voyager\Workflows\AsyncNode`) and contains the three lifecycle methods, each returning `null`. It runs as written. You may customize both stubs, `node.stub` and `node.async.stub`, with `stub:publish`; see [stub customization](/docs/{{version}}/framework/digging-deeper/computer#stub-customization).

## Writing Nodes

### The Node Lifecycle

When a node runs, it goes through three methods in order. Each one has a single job:

| Method | Receives | Returns | Job |
| --- | --- | --- | --- |
| `prep` | The `SharedBag` | Anything | Read what this node needs from shared state. |
| `exec` | What `prep` returned | Anything | Do the work. It does not see the bag. |
| `post` | The `SharedBag`, `prep`'s result, `exec`'s result | `?string` | Write results back to shared state, and return the action that picks the next node. |

Keeping `exec` away from the bag is deliberate: it takes an input and produces an output, so it is the part that may be [retried](#retries-and-fallbacks) safely. Every method has a default implementation that returns `null`, so you only override the ones you need.

Here is the review step of our pipeline. It reads the draft in `prep`, judges it in `exec`, and in `post` records the verdict and returns it as the action:

```php
<?php

namespace App\Workflows;

use Voyager\Workflows\Node;
use Voyager\Workflows\SharedBag;

class ReviewDraft extends Node
{
    public function prep(SharedBag $shared): mixed
    {
        return $shared->draft;
    }

    public function exec(mixed $draft): mixed
    {
        return match (true) {
            str_contains($draft, 'spam') => 'reject',
            strlen($draft) < 20 => 'revise',
            default => 'approve',
        };
    }

    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        $shared->trail[] = "review:{$execRes}";

        return $execRes;
    }
}
```

A node may also read `$this->params`, an array of runtime parameters that a [flow hands to every node it runs](#flow-parameters).

### The Shared Bag

A `Voyager\Workflows\SharedBag` is the one object every node in a run reads from and writes to. It is a plain object that accepts dynamic properties, so you set and read values as properties. The `put` method does the same as an assignment:

```php
use Voyager\Workflows\SharedBag;

$shared = new SharedBag;
$shared->draft = 'Short';
$shared->trail = [];

$shared->put('author', 'ada');
```

Nodes communicate only through the bag. Reading a property that has never been set raises PHP's "undefined property" warning, so read optional values with a default, as the framework's own tests do:

```php
public function prep(SharedBag $shared): mixed
{
    return $shared->trail ?? [];
}
```

When the run finishes, the bag holds everything the nodes wrote. The caller reads its results from there.

## Connecting Nodes

### Actions and Transitions

A node's successors are keyed by action name. The value `post` returns is looked up among the node's successors to pick the next node. To wire a successor for a named action, use `on(...)->next(...)`:

```php
$review = new ReviewDraft;
$publish = new PublishDraft;
$archive = new ArchiveDraft;

$review->on('approve')->next($publish);
$review->on('reject')->next($archive);
```

`PublishDraft` and `ArchiveDraft` are ordinary nodes. A node with nothing to compute may override only `post`. Here is the archive step, which records what happened and ends the run:

```php
class ArchiveDraft extends Node
{
    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        $shared->trail[] = 'archived';

        return 'archived';
    }
}
```

The `next` method on its own wires the `default` action. You may also pass the action name as its second argument; `$review->next($publish, 'approve')` is the same as the `on` form above:

```php
$revise->next($review);
```

The `default` action is also what a `post` returning `null` selects. A straight line of nodes therefore needs no action names at all, and since `next` returns the node it was given, you may chain the line:

```php
$first->next($second)->next($third);
```

> [!NOTE]
> Each action may have one successor. Wiring a second successor for an action that already has one throws a `Voyager\Contracts\Workflows\WorkflowLogicException`: `Cannot overwrite existing successor for action 'default'.`

### Ending a Flow

A flow stops when the action a node returns has no successor. There is no explicit "end" node: a node that returns `published` when nothing is wired for `published`, or returns `null` when it has no `default` successor, ends the run. The flow then returns that last action to its caller.

You may make the end explicit by wiring an action to `null`. The flow reaches a `null` successor and stops:

```php
$archive->on('archived')->next(null);
```

### Loops

Successors may point back at an earlier node, so a graph can loop. In our pipeline, a draft that is too short goes to a `ReviseDraft` node, whose `default` successor is the review again:

```php
$review->on('revise')->next($revise)->next($review);
```

`ReviseDraft` rewrites the draft in the bag and returns `null`, which follows `default` back to review:

```php
class ReviseDraft extends Node
{
    public function prep(SharedBag $shared): mixed
    {
        return $shared->draft;
    }

    public function exec(mixed $draft): mixed
    {
        return $draft.' with more detail added.';
    }

    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        $shared->draft = $execRes;
        $shared->trail[] = 'revise';

        return null;
    }
}
```

A flow walks the graph for as long as each action leads somewhere; it does not count steps. A loop ends when a node in it returns an action that leaves the loop. When the loop's exit depends on outside input, such as a model's answer in an agentic loop, keep a counter in the bag and return an exit action once it reaches your limit. Here `ReviseDraft::post` gives up after three revisions:

```php
public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
{
    $shared->draft = $execRes;
    $shared->trail[] = 'revise';
    $shared->revisions = ($shared->revisions ?? 0) + 1;

    return $shared->revisions >= 3 ? 'give-up' : null;
}
```

Wire the exit action like any other, here to the archive:

```php
$revise->on('give-up')->next($archive);
```

## Running Flows

### Running a Flow

A `Voyager\Workflows\Flow` takes the node to start at, then `run` walks the graph with the bag you give it. Here is the whole pipeline so far:

```php
use Voyager\Workflows\Flow;
use Voyager\Workflows\SharedBag;

$review = new ReviewDraft;
$revise = new ReviseDraft;

$review->on('approve')->next(new PublishDraft);
$review->on('revise')->next($revise)->next($review);
$review->on('reject')->next(new ArchiveDraft);

$shared = new SharedBag;
$shared->draft = 'Short';
$shared->trail = [];

$action = new Flow($review)->run($shared);

// $action: 'published'
// $shared->trail: ['review:revise', 'revise', 'review:approve', 'published to default']
```

`run` returns the action the last node returned. You may also set the start node after constructing the flow with `start`, which returns the node you gave it:

```php
$flow = new Flow;

$flow->start($review);
```

A flow is synchronous: each node runs to completion on the calling stack before the next one starts. To run a graph that waits on the event loop, use an [`AsyncFlow`](#async-flows).

### Running a Single Node

A node with no successors may run on its own with `run`, which goes through its lifecycle once and returns the action `post` chose. This is how you test a node in isolation:

```php
$shared = new SharedBag;
$shared->draft = 'A draft that is long enough to pass';
$shared->trail = [];

$action = new ReviewDraft()->run($shared); // 'approve'
```

> [!NOTE]
> Calling `run` on a node that has successors throws a `Voyager\Contracts\Workflows\WorkflowRuntimeException`: `Cannot run a node that has successors directly. Use a Flow to execute the full graph.`

### Flow Parameters

The `setParams` method gives a flow an array of runtime parameters. Before running each node, the flow hands that same array to the node, which reads it as `$this->params`:

```php
$flow = new Flow($review);
$flow->setParams(['channel' => 'blog']);

$flow->run($shared);

// $shared->trail ends with 'published to blog'
```

Use parameters for the settings of a run, such as which channel to publish to, and the bag for the data the nodes produce:

```php
class PublishDraft extends Node
{
    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        $shared->trail[] = 'published to '.($this->params['channel'] ?? 'default');

        return 'published';
    }
}
```

### Writing a Flow Class

When a graph is used in more than one place, wire it in a `Flow` subclass's constructor and pass the start node to the parent. This is how the framework's `install:ext` flow is built:

```php
<?php

namespace App\Workflows;

use Voyager\Workflows\Flow;

class EditorialFlow extends Flow
{
    public function __construct()
    {
        $review = new ReviewDraft;
        $revise = new ReviseDraft;

        $review->on('approve')->next(new PublishDraft);
        $review->on('revise')->next($revise)->next($review);
        $review->on('reject')->next(new ArchiveDraft);

        parent::__construct($review);
    }
}
```

The caller fills a bag, runs the flow, and reads the results:

```php
$shared = new SharedBag;
$shared->draft = $draft;
$shared->trail = [];

new EditorialFlow()->run($shared);
```

A flow has a lifecycle of its own around the walk. Its `prep` runs before the first node, and its `post` runs after the last, receiving the bag, `prep`'s result, and the final action of the walk. The default `post` returns that final action unchanged, so `EditorialFlow` returns `published` or `archived`. A subclass may override `post` to translate the walk's result into the action the flow itself returns. For callers that only care whether a draft went live:

```php
class GoLiveFlow extends EditorialFlow
{
    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        return $execRes === 'published' ? 'live' : 'held';
    }
}
```

### Nesting Flows

A `Flow` is itself a node, so a flow may be a step inside another flow. The inner flow runs its whole graph, and the action it returns picks the outer graph's next node. Wire a flow's successors exactly as you would a node's:

```php
$editorial = new EditorialFlow;
$editorial->on('published')->next(new NotifySubscribers);

new Flow($editorial)->run($shared);
```

`NotifySubscribers` is the outer graph's next step, a node like any other:

```php
class NotifySubscribers extends Node
{
    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        $shared->trail[] = 'subscribers notified';

        return null;
    }
}
```

Parameters come from the outermost flow: as it runs each step, it hands its own parameters to that step, and an inner flow passes them on to its nodes. Set parameters on the flow you call `run` on.

## Retries and Fallbacks

`exec` is the part of a node that talks to the outside world, so it is the part that fails. A `Node` takes two constructor arguments: `maxRetries`, the total number of attempts (default `1`), and `waitSeconds`, the pause between attempts (default `0`). When an attempt throws, the node tries again; when the last attempt throws, it calls `execFallback` with `prep`'s result and the exception. The default `execFallback` rethrows. Override it to return a fallback result, which `post` then receives as if `exec` had returned it:

```php
use Throwable;
use Voyager\Workflows\Node;
use Voyager\Workflows\SharedBag;

class PublishDraft extends Node
{
    public function __construct()
    {
        parent::__construct(maxRetries: 3);
    }

    public function prep(SharedBag $shared): mixed
    {
        return $shared->draft;
    }

    public function exec(mixed $draft): mixed
    {
        app('http')->post('https://cms.example.com/posts', [
            'channel' => $this->params['channel'] ?? 'default',
            'body' => $draft,
        ])->throw();

        return 'live';
    }

    public function execFallback(mixed $draft, Throwable $e): mixed
    {
        app('log')->warning('Publishing failed, draft held.', ['exception' => $e]);

        return 'held';
    }

    public function post(SharedBag $shared, mixed $prepRes, mixed $execRes): ?string
    {
        $shared->publish_status = $execRes;
        $shared->trail[] = 'published to '.($this->params['channel'] ?? 'default');

        return 'published';
    }
}
```

The HTTP client's `throw` method turns an error response into an exception, which is what counts as a failed attempt. Only `exec` is retried. `prep` and `post` run once.

> [!WARNING]
> A synchronous `Node` waits between attempts with PHP's `sleep`, which stops the whole process, event loop included, for `waitSeconds`. When a node that waits between retries runs in a process that has other work on the loop, make it an [`AsyncNode`](#async-nodes), which waits on a loop timer instead.

## Async Nodes

### Writing Async Nodes

An `AsyncNode` is a node whose work waits on the [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop) instead of blocking: an [async HTTP request](/docs/{{version}}/framework/digging-deeper/http-client#asynchronous-requests), an [async cache call](/docs/{{version}}/framework/digging-deeper/cache#async-cache-operations), a timer. Its lifecycle methods are `prepAsync`, `execAsync`, and `postAsync`, with the same arguments and jobs as `prep`, `exec`, and `post`. Each one may return a plain value or a `Voyager\Contracts\IOPools\Promise`; the node waits for a promise to settle and passes on what it holds. `postAsync` returns the action, or a promise of it.

The first step of our pipeline fetches the draft from a remote service. `execAsync` returns the HTTP client's promise, mapped to the field we want:

```php
<?php

namespace App\Workflows\Drafts;

use Voyager\Http\Client\Response;
use Voyager\Workflows\AsyncNode;
use Voyager\Workflows\SharedBag;

class FetchDraft extends AsyncNode
{
    public function prepAsync(SharedBag $shared): mixed
    {
        return $shared->draft_url;
    }

    public function execAsync(mixed $url): mixed
    {
        return app('http')->async()->get($url)->then(
            fn (Response $response) => $response->json('body')
        );
    }

    public function postAsync(SharedBag $shared, mixed $prepRes, mixed $execRes): mixed
    {
        $shared->draft = $execRes;
        $shared->trail = [];

        return null;
    }
}
```

An async node with no successors runs on its own with `runAsync`, which returns the action `postAsync` chose:

```php
$action = new FetchDraft()->runAsync($shared);
```

> [!NOTE]
> An async node cannot run synchronously. Its `run` method throws a `WorkflowRuntimeException`, `Cannot call sync 'run' on an async node. Use 'runAsync' instead.`, and a synchronous `Flow` that reaches one throws `Synchronous Flow cannot contain async nodes. Use AsyncFlow instead.`

### The Async Runtime

Inside an async node, `$this->runtime()` returns the `Voyager\Contracts\Workflows\AsyncRuntime` the node runs on. Its methods are the building blocks for `execAsync` bodies:

| Method | Description |
| --- | --- |
| `delay(float $seconds)` | A promise that resolves with `null` after `$seconds`, on a loop timer. |
| `async(Closure $work)` | Starts `$work` now on the loop and returns a promise of its result. A promise returned by `$work` is unwrapped. |
| `all(iterable $work, ?int $concurrency = null)` | Runs every closure in `$work`, at most `$concurrency` at once, and returns a promise of the results keyed like the input. Every entry settles before the first failure is rethrown. |
| `resolve(mixed $value)` | A promise already holding `$value`, or `$value` itself when it is a promise. |
| `await(mixed $value)` | Waits for a promise and returns its value, or throws its reason. Plain values pass straight through. |

The framework's tests wait on the loop with `delay`, which makes it a handy stand-in for slow work while you build a graph:

```php
public function execAsync(mixed $prepRes): mixed
{
    return $this->runtime()->delay(0.05)->then(fn () => 'waited');
}
```

In an application, the runtime is the `loop` driver of the `Voyager\Workflows\AsyncRuntimeManager`, a `Voyager\Workflows\Runtimes\LoopRuntime` on the application's own event loop (`app('event-loop')`). The driver is named by the `runtime` option of your `config/workflows.php` file, read from the `WORKFLOWS_RUNTIME` environment variable, and `loop` is the only driver Venusian ships:

```php
return [
    'runtime' => env('WORKFLOWS_RUNTIME', 'loop'),
];
```

You may resolve the runtime yourself from the manager:

```php
use Voyager\Workflows\AsyncRuntimeManager;

$runtime = app(AsyncRuntimeManager::class)->driver();
```

### Retries Without Blocking

An `AsyncNode` takes `maxRetries` and `wait` (seconds) as its constructor arguments, and an optional runtime as its third. Retries work as they do for a `Node`, with `execFallbackAsync` in place of `execFallback`, but the wait between attempts is a `delay` on the loop, so other work on the loop keeps running while the node waits:

Here is `FetchDraft` again, now trying the fetch three times, a second apart. When every attempt fails, the fallback answers `null`, and `postAsync` turns that into an `unavailable` action, which has no successor and so ends the run:

```php
<?php

namespace App\Workflows\Drafts;

use Throwable;
use Voyager\Http\Client\Response;
use Voyager\Workflows\AsyncNode;
use Voyager\Workflows\SharedBag;

class FetchDraft extends AsyncNode
{
    public function __construct()
    {
        parent::__construct(maxRetries: 3, wait: 1);
    }

    public function prepAsync(SharedBag $shared): mixed
    {
        return $shared->draft_url;
    }

    public function execAsync(mixed $url): mixed
    {
        return app('http')->async()->get($url)->then(function (Response $response) {
            $response->throw();

            return $response->json('body');
        });
    }

    public function execFallbackAsync(mixed $url, Throwable $e): mixed
    {
        return null;
    }

    public function postAsync(SharedBag $shared, mixed $prepRes, mixed $execRes): mixed
    {
        $shared->draft = $execRes;
        $shared->trail = [];

        return is_null($execRes) ? 'unavailable' : null;
    }
}
```

A connection failure rejects the HTTP client's promise, and `throw` turns an error response into a rejection, so both count as a failed attempt.

## Async Flows

### Running Async Flows

An `AsyncFlow` walks a graph that contains async nodes. It awaits each async node and runs synchronous nodes in place, so `FetchDraft` can lead straight into the `ReviewDraft` and `PublishDraft` nodes we already have. Run it with `runAsync`:

```php
use Voyager\Workflows\AsyncFlow;
use Voyager\Workflows\SharedBag;

$fetch = new FetchDraft;
$review = new ReviewDraft;

$fetch->next($review);
$review->on('approve')->next(new PublishDraft);
$review->on('reject')->next(new ArchiveDraft);

$shared = new SharedBag;
$shared->draft_url = 'https://drafts.example.com/posts/1';

$action = new AsyncFlow($fetch)->runAsync($shared);
```

Before running each node, the flow hands it the flow's runtime, so a whole graph runs on one loop. You may pass a runtime as the flow's second constructor argument; otherwise the flow resolves one as a node does. An `AsyncFlow` has `prepAsync` and `postAsync` around its walk, the async counterparts of a `Flow`'s `prep` and `post`, and may be [nested](#nesting-flows) inside another `AsyncFlow`.

> [!NOTE]
> `AsyncFlow`'s `run` method throws `Cannot call sync 'run' on an AsyncFlow. Use 'runAsync' instead.`, and since it is an async node, a synchronous `Flow` refuses to contain one. A synchronous `Flow` may sit inside an `AsyncFlow`, as long as it contains no async nodes itself.

The walk is sequential, because the next node is not known until the current one returns its action. Overlap comes from inside a node, through `all` or the [parallel batch classes](#batch-nodes), and from running several flows at once.

### Running Flows Alongside Other Work

`runAsync` returns the final action, not a promise. Called on the main stack, from a command for example, it turns the event loop until the flow finishes and then returns, so the command reads the bag on the next line. Called inside a loop fiber, it suspends only that fiber, and everything else on the loop keeps running.

Nodes keep their parameters and any properties you give them as state on the instance, so flows that run at the same time should each be built from their own node instances. An `AsyncFlow` subclass that wires its graph in the constructor gives you a fresh graph per instance:

```php
<?php

namespace App\Workflows;

use App\Workflows\Drafts\FetchDraft;
use Voyager\Workflows\AsyncFlow;

class FetchAndPublishFlow extends AsyncFlow
{
    public function __construct()
    {
        $fetch = new FetchDraft;
        $review = new ReviewDraft;

        $fetch->next($review);
        $review->on('approve')->next(new PublishDraft);
        $review->on('reject')->next(new ArchiveDraft);

        parent::__construct($fetch);
    }
}
```

To run a flow as a task of its own, start it with the runtime's `async` method, which returns a promise of the flow's final action. The code that started it carries on at once:

```php
use Voyager\Workflows\AsyncRuntimeManager;

$runtime = app(AsyncRuntimeManager::class)->driver();

$promise = $runtime->async(fn () => new FetchAndPublishFlow()->runAsync($shared));

$promise->then(function (?string $action) use ($shared) {
    app('log')->info('Draft run finished.', ['action' => $action, 'trail' => $shared->trail]);
});
```

Several flows started this way are in flight together. `all` starts them and waits for every one, so two flows that each wait 200 milliseconds on the loop finish in about 200 milliseconds, not 400. Each flow gets its own bag:

```php
$first = new SharedBag;
$first->draft_url = 'https://drafts.example.com/posts/1';

$second = new SharedBag;
$second->draft_url = 'https://drafts.example.com/posts/2';

$actions = $runtime->await($runtime->all([
    fn () => new FetchAndPublishFlow()->runAsync($first),
    fn () => new FetchAndPublishFlow()->runAsync($second),
]));
```

### Running Without an Application

An async node needs a loop, but it does not need an application. A node first uses the runtime its flow handed it; failing that, the application's runtime; and when no application is booted at all, as in a unit test or a plain script, it uses `LoopRuntime::standalone()`. That is one event loop per process, built from the IOPools parts directly: the epoll or kqueue waiter when the extension is loaded, `stream_select` otherwise. The same node runs unchanged in all three cases. In a test with no application booted, a node that waits on a loop timer runs, and its runtime is the standalone one:

```php
use Voyager\Workflows\AsyncNode;
use Voyager\Workflows\Runtimes\LoopRuntime;
use Voyager\Workflows\SharedBag;

$node = new class extends AsyncNode {
    public function execAsync(mixed $prepRes): mixed
    {
        return $this->runtime()->delay(0.05)->then(fn () => 'waited');
    }

    public function postAsync(SharedBag $shared, mixed $prepRes, mixed $execRes): mixed
    {
        $shared->result = $execRes;

        return null;
    }
};

$shared = new SharedBag;
$node->runAsync($shared);

expect($node->runtime())->toBe(LoopRuntime::standalone())
    ->and($shared->result)->toBe('waited');
```

You may hand a runtime to a node yourself with `usesRuntime`, or pass one to the `AsyncNode` and `AsyncFlow` constructors.

## Batch Nodes

A batch node runs `execAsync` once per item. Its `prepAsync` returns the items, `execAsync` receives one item at a time, and `postAsync` receives the array of results, keyed like the items. Each item gets the full [retry and fallback](#retries-without-blocking) treatment.

An `AsyncBatchNode` runs the items one after another. An `AsyncParallelBatchNode` runs them all at once, at most `concurrency` at a time when you pass that constructor argument. Its results keep the items' keys and order, not the order they finished in. When an item fails, its siblings still run to the end, and the first failure is rethrown once every item has settled.

Once a draft is published, our pipeline tells the people involved, at most two at a time:

```php
<?php

namespace App\Workflows;

use Voyager\Workflows\AsyncParallelBatchNode;
use Voyager\Workflows\SharedBag;

class NotifyReviewers extends AsyncParallelBatchNode
{
    public function __construct()
    {
        parent::__construct(maxRetries: 3, wait: 1, concurrency: 2);
    }

    public function prepAsync(SharedBag $shared): mixed
    {
        return ['editor' => 1, 'author' => 2, 'legal' => 3];
    }

    public function execAsync(mixed $userId): mixed
    {
        return $this->runtime()->delay(0.2)->then(fn () => "sent to {$userId}");
    }

    public function postAsync(SharedBag $shared, mixed $prepRes, mixed $execRes): mixed
    {
        $shared->notified = $execRes; // ['editor' => 'sent to 1', 'author' => ..., 'legal' => ...]

        return null;
    }
}
```

With three items and a cap of two, the node takes two rounds of 200 milliseconds. A retry's wait holds back only the item that failed.

Wire it after the publish step. A sync `PublishDraft` leading into an async `NotifyReviewers` is fine in an `AsyncFlow`:

```php
$publish = new PublishDraft;
$publish->on('published')->next(new NotifyReviewers);
```

## Batch Flows

A batch flow runs its whole graph once per set of parameters. Its `prepAsync` returns a list of parameter arrays; each one is merged over the flow's own parameters and handed to every node of that run, which reads it as `$this->params`. The flow's `postAsync` receives the parameter list. Nested in another `AsyncFlow`, a batch flow still runs its whole list.

To load a whole queue of drafts, the node of each run reads its draft's id from `$this->params`. The bag is shared by every run, so each run writes its result under its own id:

```php
<?php

namespace App\Workflows\Drafts;

use Voyager\Http\Client\Response;
use Voyager\Workflows\AsyncNode;
use Voyager\Workflows\SharedBag;

class FetchDraftById extends AsyncNode
{
    public function execAsync(mixed $prepRes): mixed
    {
        return app('http')->async()
            ->get("https://drafts.example.com/posts/{$this->params['draft_id']}")
            ->then(fn (Response $response) => $response->json('body'));
    }

    public function postAsync(SharedBag $shared, mixed $prepRes, mixed $execRes): mixed
    {
        $drafts = $shared->drafts ?? [];
        $drafts[$this->params['draft_id']] = $execRes;
        $shared->drafts = $drafts;

        return null;
    }
}
```

An `AsyncBatchFlow` runs the graph for each parameter set in turn. The flow's `prepAsync` turns the ids in the bag into one parameter set per draft:

```php
use App\Workflows\Drafts\FetchDraftById;
use Voyager\Workflows\AsyncBatchFlow;
use Voyager\Workflows\SharedBag;

class LoadDraftQueue extends AsyncBatchFlow
{
    public function prepAsync(SharedBag $shared): mixed
    {
        return array_map(fn (int $id) => ['draft_id' => $id], $shared->draft_ids);
    }
}

$shared = new SharedBag;
$shared->draft_ids = [3, 1, 2];

new LoadDraftQueue(new FetchDraftById)->runAsync($shared);

// $shared->drafts: [3 => '...', 1 => '...', 2 => '...']
```

An `AsyncParallelBatchFlow` runs every parameter set at once, at most `concurrency` at a time when you pass it as the second constructor argument. Because the parameters live on the nodes, each concurrent run gets its own copy of every node it visits. The `SharedBag` is still one object across every run, which is why `FetchDraftById` keys what it writes by its own parameters:

```php
use App\Workflows\Drafts\FetchDraftById;
use Voyager\Workflows\AsyncParallelBatchFlow;
use Voyager\Workflows\SharedBag;

class LoadDraftQueueAtOnce extends AsyncParallelBatchFlow
{
    public function prepAsync(SharedBag $shared): mixed
    {
        return array_map(fn (int $id) => ['draft_id' => $id], $shared->draft_ids);
    }
}

new LoadDraftQueueAtOnce(new FetchDraftById, concurrency: 4)->runAsync($shared);
```

The parallel flow's results arrive in the order the fetches finished, so the keys of `$shared->drafts` may be in a different order than `draft_ids`.

> [!NOTE]
> Since a parallel batch flow runs copies of your nodes, properties set on the node instances you wired are not updated by the runs. Read results from the bag.

## Workflow Exceptions

Mistakes in wiring and running graphs throw exceptions from the `Voyager\Contracts\Workflows` namespace:

| Exception | Thrown when |
| --- | --- |
| `WorkflowLogicException` | An action is given a second successor. |
| `WorkflowRuntimeException` | A node with successors is run directly; a synchronous `Flow` reaches an async node; `run` is called on an async node or an `AsyncFlow`. |

Exceptions thrown by your own lifecycle methods are not wrapped. An exception from `exec` or `execAsync` goes through the node's retries and fallback first; anything else reaches the caller of `run` or `runAsync` as it was thrown.
