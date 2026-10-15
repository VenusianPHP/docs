# Context

Venusian's "context" capabilities enable you to capture, retrieve, and share information throughout commands, jobs, and sketches executing within your application.

## Introduction

Venusian's "context" capabilities enable you to capture, retrieve, and share information throughout commands, jobs, and sketches executing within your application. This captured information is also included in logs written by your application, giving you deeper insight into the surrounding code execution history that occurred before a log entry was written and allowing you to trace execution flows throughout a distributed system.

Context lives in a `Voyager\Log\Context\Repository`, which the framework registers on every boot. Venusian has no facades, so you work with the repository directly: type-hint it on a class the [service container](/docs/{{version}}/framework/architecture-concepts/container) builds, or resolve it with `app(Repository::class)`. The examples below use a `$context` variable holding that repository.

### How it Works

The best way to understand Venusian's context capabilities is to see it in action using the built-in logging features. To get started, you may [add information to the context](#capturing-context) using the repository's `add` method. In this example, a [Computer](/docs/{{version}}/framework/digging-deeper/computer) command adds the feed it is importing and a unique trace ID to the context before it does its work:

```php
<?php

namespace App\Console\Commands;

use Voyager\Console\Command;
use Voyager\Log\Context\Repository;
use Voyager\NutsAndBolts\Str;

class ImportFeed extends Command
{
    protected ?string $signature = 'feed:import {url}';

    protected string $description = 'Import a podcast feed';

    public function handle(Repository $context): void
    {
        $context->add('url', $this->argument('url'));
        $context->add('trace_id', Str::uuid()->toString());

        // ...
    }
}
```

Information added to the context is automatically appended as metadata to any [log entries](/docs/{{version}}/framework/the-basics/logging) that are written afterwards. Appending context as metadata allows information passed to individual log entries to be differentiated from the information shared via context. For example, imagine we write the following log entry:

```php
app('log')->info('Feed fetched.', ['episodes' => 27]);
```

The written log will contain the `episodes` passed to the log entry, but it will also contain the context's `url` and `trace_id` as metadata:

```text
Feed fetched. {"episodes":27} {"url":"https://example.com/feed.xml","trace_id":"e04e1a11-e75c-4db3-b5b5-cfef4ef56697"}
```

Information added to the context is also made available to jobs dispatched to the queue. For example, imagine we dispatch a `ProcessPodcast` job to the queue after adding some information to the context:

```php
$context->add('url', $this->argument('url'));
$context->add('trace_id', Str::uuid()->toString());

dispatch(new ProcessPodcast($podcast));
```

When the job is dispatched, any information currently stored in the context is captured and shared with the job. The captured information is then hydrated back into the current context while the job is executing. So, if our job's handle method was to write to the log:

```php
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    // ...

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        app('log')->info('Processing podcast.', [
            'podcast_id' => $this->podcast->id,
        ]);

        // ...
    }
}
```

The resulting log entry would contain the information that was added to the context by the command that originally dispatched the job:

```text
Processing podcast. {"podcast_id":95} {"url":"https://example.com/feed.xml","trace_id":"e04e1a11-e75c-4db3-b5b5-cfef4ef56697"}
```

The repository is a [scoped](/docs/{{version}}/framework/architecture-concepts/container#binding-scoped-singletons) binding, so a queue worker drops it after every job. Each job therefore starts from the context it was dispatched with, never from whatever the previous job left behind.

Although we have focused on the built-in logging related features of Venusian's context, the following documentation will illustrate how context allows you to share information across the queued job boundary and even how to add [hidden context data](#hidden-context) that is not written with log entries.

<a id="capturing-context"></a>
## Capturing Context

You may store information in the current context using the repository's `add` method:

```php
use Voyager\Log\Context\Repository;

$context = app(Repository::class);

$context->add('key', 'value');
```

To add multiple items at once, you may pass an associative array to the `add` method:

```php
$context->add([
    'first_key' => 'value',
    'second_key' => 'value',
]);
```

The `add` method will override any existing value that shares the same key. If you only wish to add information to the context if the key does not already exist, you may use the `addIf` method:

```php
$context->add('key', 'first');

$context->get('key');
// "first"

$context->addIf('key', 'second');

$context->get('key');
// "first"
```

Context also provides convenient methods for incrementing or decrementing a given key. Both of these methods accept at least one argument: the key to track. A second argument may be provided to specify the amount by which the key should be incremented or decremented:

```php
$context->increment('records_added');
$context->increment('records_added', 5);

$context->decrement('records_added');
$context->decrement('records_added', 5);
```

#### Conditional Context

The `when` method may be used to add data to the context based on a given condition. The first closure provided to the `when` method will be invoked if the given condition evaluates to `true`, while the second closure will be invoked if the condition evaluates to `false`:

```php
$context->when(
    app()->environment('local'),
    fn ($context) => $context->add('debug', true),
    fn ($context) => $context->add('debug', false),
);
```

#### Scoped Context

The `scope` method provides a way to temporarily modify the context during the execution of a given callback and restore the context to its original state when the callback finishes executing. Additionally, you can pass extra data that should be merged into the context (as the second and third arguments) while the closure executes.

```php
$context->add('trace_id', 'abc-999');
$context->addHidden('user_id', 123);

$context->scope(
    function () use ($context) {
        $context->add('action', 'adding_friend');

        $userId = $context->getHidden('user_id');

        app('log')->debug("Adding user [{$userId}] to friends list.");
        // Adding user [987] to friends list.  {"trace_id":"abc-999","user_name":"ada_lovelace","action":"adding_friend"}
    },
    data: ['user_name' => 'ada_lovelace'],
    hidden: ['user_id' => 987],
);

$context->all();
// [
//     'trace_id' => 'abc-999',
// ]

$context->allHidden();
// [
//     'user_id' => 123,
// ]
```

> [!WARNING]
> If an object within the context is modified inside the scoped closure, that mutation will be reflected outside of the scope.

<a id="stacks"></a>
### Stacks

Context offers the ability to create "stacks", which are lists of data stored in the order that they were added. You can add information to a stack by invoking the `push` method:

```php
$context->push('breadcrumbs', 'first_value');

$context->push('breadcrumbs', 'second_value', 'third_value');

$context->get('breadcrumbs');
// [
//     'first_value',
//     'second_value',
//     'third_value',
// ]
```

Stacks can be useful to capture historical information about a run, such as signals that are dispatched throughout your application. For example, you could register a query listener that pushes to a stack every time a query is executed, capturing the query SQL and duration as a tuple:

```php
use Voyager\Database\Events\QueryExecuted;
use Voyager\Log\Context\Repository;

// In AppServiceProvider.php...
app('db')->listen(function (QueryExecuted $event) {
    app(Repository::class)->push('queries', [$event->time, $event->sql]);
});
```

You may determine if a value is in a stack using the `stackContains` and `hiddenStackContains` methods:

```php
if ($context->stackContains('breadcrumbs', 'first_value')) {
    //
}

if ($context->hiddenStackContains('secrets', 'first_value')) {
    //
}
```

The `stackContains` and `hiddenStackContains` methods also accept a closure as their second argument, allowing more control over the value comparison operation:

```php
use Voyager\NutsAndBolts\Str;

return $context->stackContains('breadcrumbs', function ($value) {
    return Str::startsWith($value, 'query_');
});
```

## Retrieving Context

You may retrieve information from the context using the repository's `get` method:

```php
$value = $context->get('key');
```

The `only` and `except` methods may be used to retrieve a subset of the information in the context:

```php
$data = $context->only(['first_key', 'second_key']);

$data = $context->except(['first_key']);
```

The `pull` method may be used to retrieve information from the context and immediately remove it from the context:

```php
$value = $context->pull('key');
```

If context data is stored in a [stack](#stacks), you may pop items from the stack using the `pop` method:

```php
$context->push('breadcrumbs', 'first_value', 'second_value');

$context->pop('breadcrumbs');
// second_value

$context->get('breadcrumbs');
// ['first_value']
```

The `remember` and `rememberHidden` methods may be used to retrieve information from the context, while setting the context value to the value returned by the given closure if the requested information doesn't exist:

```php
$permissions = $context->remember(
    'user-permissions',
    fn () => $user->permissions,
);
```

If you would like to retrieve all of the information stored in the context, you may invoke the `all` method:

```php
$data = $context->all();
```

### Determining Item Existence

You may use the `has` and `missing` methods to determine if the context has any value stored for the given key:

```php
if ($context->has('key')) {
    // ...
}

if ($context->missing('key')) {
    // ...
}
```

The `has` method will return `true` regardless of the value stored. So, for example, a key with a `null` value will be considered present:

```php
$context->add('key', null);

$context->has('key');
// true
```

## Removing Context

The `forget` method may be used to remove a key and its value from the current context:

```php
$context->add(['first_key' => 1, 'second_key' => 2]);

$context->forget('first_key');

$context->all();

// ['second_key' => 2]
```

You may forget several keys at once by providing an array to the `forget` method:

```php
$context->forget(['first_key', 'second_key']);
```

The `flush` method removes every value, hidden ones included:

```php
$context->flush();
```

<a id="hidden-context"></a>
## Hidden Context

Context offers the ability to store "hidden" data. This hidden information is not appended to logs, and is not accessible via the data retrieval methods documented above. Context provides a different set of methods to interact with hidden context information:

```php
$context->addHidden('key', 'value');

$context->getHidden('key');
// 'value'

$context->get('key');
// null
```

The "hidden" methods mirror the functionality of the non-hidden methods documented above:

```php
$context->addHidden(/* ... */);
$context->addHiddenIf(/* ... */);
$context->pushHidden(/* ... */);
$context->getHidden(/* ... */);
$context->pullHidden(/* ... */);
$context->popHidden(/* ... */);
$context->rememberHidden(/* ... */);
$context->onlyHidden(/* ... */);
$context->exceptHidden(/* ... */);
$context->allHidden(/* ... */);
$context->hasHidden(/* ... */);
$context->missingHidden(/* ... */);
$context->forgetHidden(/* ... */);
```

## Context and Async Logging

The `*Async()` log methods, such as `infoAsync`, write on a worker pool rather than in your process. Each call carries a snapshot of the context as it was when the call was made, and the worker writes the entry with that snapshot, so an async entry carries the same metadata a blocking one would:

```php
$context->add('trace_id', 'abc-999');

app('log')->infoAsync('Feed fetched.');

$context->forget('trace_id');

// The entry is still written with {"trace_id":"abc-999"}...
```

Because the snapshot travels to another process, every context value, hidden values included, must be serializable. When the context holds a value that can't be serialized, such as a closure, the async call writes nothing and its promise rejects with an `InvalidArgumentException`:

```php
$context->add('callback', fn () => null);

app('log')->infoAsync('Feed fetched.')->wait();
// InvalidArgumentException: This log call can't cross to a worker: Serialization of 'Closure' is not allowed
```

## Signals

Context dispatches two [signals](/docs/{{version}}/framework/digging-deeper/signals) that allow you to hook into the hydration and dehydration process of the context.

To illustrate how these signals may be used, imagine that a command of your application changes the `app.name` configuration value for the duration of its run. Context's signals allow you to capture this value when a job is dispatched and restore it on the queue, ensuring the job sees the same `app.name` value. We can use context's signals and [hidden](#hidden-context) data to achieve this, which the following documentation will illustrate.

### Dehydrating

Whenever a job is dispatched to the queue the data in the context is "dehydrated" and captured alongside the job's payload. The repository's `dehydrating` method allows you to register a closure that will be invoked during the dehydration process. Within this closure, you may make changes to the data that will be shared with the queued job. The closure runs when the `Voyager\Log\Context\Signals\ContextDehydrating` signal is dispatched, which also happens for every [async log call](#context-and-async-logging), since each one captures the context the same way.

Typically, you should register `dehydrating` callbacks within the `boot` method of your application's `AppServiceProvider` class:

```php
use Voyager\Log\Context\Repository;

/**
 * Bootstrap any application services.
 */
public function boot(Repository $context): void
{
    $context->dehydrating(function (Repository $context) {
        $context->addHidden('app_name', config('app.name'));
    });
}
```

> [!NOTE]
> You should not resolve the context repository from the container within the `dehydrating` callback, as that will change the context of the current process. Ensure you only make changes to the repository passed to the callback.

### Hydrated

Whenever a queued job begins executing on the queue, any context that was shared with the job will be "hydrated" back into the current context. The repository's `hydrated` method allows you to register a closure that will be invoked during the hydration process. The closure runs when the `Voyager\Log\Context\Signals\ContextHydrated` signal is dispatched.

Typically, you should register `hydrated` callbacks within the `boot` method of your application's `AppServiceProvider` class:

```php
use Voyager\Log\Context\Repository;

/**
 * Bootstrap any application services.
 */
public function boot(Repository $context): void
{
    $context->hydrated(function (Repository $context) {
        if ($context->hasHidden('app_name')) {
            config(['app.name' => $context->getHidden('app_name')]);
        }
    });
}
```

> [!NOTE]
> You should not resolve the context repository from the container within the `hydrated` callback and instead ensure you only make changes to the repository passed to the callback.
