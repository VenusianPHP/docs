# Concurrency

Run several slow, independent tasks at the same time, blocking for their results or without blocking on the event loop.

## Introduction

Sometimes you may need to execute several slow tasks which do not depend on one another. In many cases, significant performance improvements can be realized by executing the tasks concurrently. Venusian's concurrency manager, available from the container as `app('concurrency')`, provides a simple, convenient API for executing closures concurrently.

#### How it Works

The `process` driver achieves concurrency by serializing the given closures and dispatching them to a hidden `invoke-serialized-closure` Computer command, which unserializes each closure and invokes it within its own PHP process. After the closure has been invoked, the resulting value is serialized back to the parent process.

The concurrency manager supports four drivers: `process` (the default), `fork`, `sync`, and `pool`.

The `fork` driver forks the current PHP process instead of starting a fresh one. Before using the `fork` driver, you need to install the `spatie/fork` package:

```shell
composer require spatie/fork
```

The `sync` driver is primarily useful during testing when you want to disable all concurrency and simply execute the given closures in sequence within the parent process.

The `pool` driver sends each closure to the IOPools worker pools as a `Voyager\Concurrency\RunTask` gig. Pool workers boot once and are reused, so a task does not pay for booting a fresh application. Its `pool` option picks the workers: `thread`, `process`, or `auto`, which uses the thread workers when they are enabled and the process workers otherwise. The thread workers are enabled by the `io-pools.pool_workers.threads.enabled` configuration option and need a ZTS build of PHP with the `parallel` extension.

## Running Concurrent Tasks

To run concurrent tasks, you may invoke the concurrency manager's `run` method. The `run` method accepts an array of closures which should be executed simultaneously and blocks until every one of them has returned:

```php
[$userCount, $orderCount] = app('concurrency')->run([
    fn () => app('db')->table('users')->count(),
    fn () => app('db')->table('orders')->count(),
]);
```

If any task throws, `run` throws that task's exception as its own class. When several tasks fail, the first failure in key order is thrown.

To use a specific driver, you may use the `driver` method:

```php
$results = app('concurrency')->driver('fork')->run(...);
```

Or, to change the default concurrency driver, you may set the `CONCURRENCY_DRIVER` environment variable, or publish the `concurrency` configuration file via the `config:publish` Computer command and update the `default` option within the file:

```shell
php computer config:publish concurrency
```

The `pool` driver's workers are chosen by the `CONCURRENCY_POOL` environment variable, or by the `drivers.pool.pool` option of the same file.

### Named Results

If you would like to access concurrent task results by name rather than by position, you may provide an associative array of closures. Each result will be returned using the same key as its corresponding closure:

```php
$results = app('concurrency')->run([
    'users' => fn () => app('db')->table('users')->count(),
    'orders' => fn () => app('db')->table('orders')->count(),
]);

$userCount = $results['users'];
$orderCount = $results['orders'];
```

> [!WARNING]
> Closures are serialized by the file and line they are written on, so two closures written on the same line serialize as the same closure. Write one task per line.

## Running Tasks Without Blocking

The `async` method starts the tasks and returns immediately with a `Voyager\Contracts\IOPools\Promise`, leaving the event loop free while they run. Only the `process` and `pool` drivers can run tasks without blocking; calling `async` on the `sync` or `fork` driver throws an `InvalidArgumentException`. The second argument names the batch:

```php
$promise = app('concurrency')->async([
    'users' => fn () => app('db')->table('users')->count(),
    'orders' => fn () => app('db')->table('orders')->count(),
], 'counts');

$promise->then(function (array $results) {
    // $results['users'], $results['orders']...
});
```

The promise settles once every task has settled: it is fulfilled with the results keyed as the tasks were, or rejected with the first failure in key order. A task that fails or times out fails on its own; the other tasks still come back. If you need to block for the outcome, `$promise->wait()` returns the results or throws the failure.

### Results as Loop Mail

When every task has settled, the results are also posted to the event loop as a `Voyager\Concurrency\ConcurrencyResults` mail named `concurrency:{name}`, where `{name}` is the name given to `async` (`default` when none is given). With the default `signal` mail handler, that mail is dispatched as a signal, so you may listen for it by name:

```php
use Voyager\Concurrency\ConcurrencyResults;

app('signals')->listen('concurrency:counts', function (ConcurrencyResults $results) {
    if ($results->successful()) {
        // $results->results['users'], $results->results['orders']...
    }

    foreach ($results->failures as $key => $exception) {
        // ...
    }
});
```

The `results` property holds the tasks that returned and the `failures` property holds the exceptions of the tasks that threw, both keyed as the tasks were.
