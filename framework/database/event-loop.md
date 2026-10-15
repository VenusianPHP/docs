# Database: Event Loop

Run database queries from code on the event loop without blocking it, by offloading them to worker pools.

## Introduction

Every Venusian database connection is built on PDO, and PDO never yields: a query blocks the process until the database answers. Venusian has no asynchronous database driver, and a connection's socket is not registered with the [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop). When your code runs on the loop, you hand the blocking call to a [worker pool](/docs/{{version}}/framework/architecture-concepts/event-loop#worker-pools) instead: the worker runs the query, and you receive a `Voyager\Contracts\IOPools\Promise` of the result while the loop keeps turning.

This page gathers the pieces in one place. Each section links to the full reference.

## Enabling the Worker Pools

Offloaded queries run in the pools configured in your application's `config/io-pools.php` file. The process workers are enabled by default; the thread workers need a ZTS build of PHP with ext-parallel loaded:

```php
'pool_workers' => [
    'process' => [
        'enabled' => true,
        'max_workers' => env('IO_POOLS_PROCESS_WORKERS', 4),
    ],
    'threads' => [
        'enabled' => false,
        'max_workers' => env('IO_POOLS_THREAD_WORKERS', 4),
    ],
],
```

Every `via` method below takes the pool to use, `'process'` or `'thread'`. With no argument it picks the thread workers when they are enabled and the process workers otherwise. Naming a pool that is not enabled throws an `InvalidArgumentException`. See [Offloading Queries to Worker Pools](/docs/{{version}}/framework/database/database#offloading-queries-to-worker-pools).

## Offloading Queries

Call `via` on a connection, a query builder, or an Instrument builder, then call the method you would have called anyway. It answers with a promise of the value the blocking call returns:

```php
use App\Models\User;

$rows = app('db')->connection('pgsql')->via()->select('select * from users where active = ?', [1]);

$names = app('db')->table('users')->where('active', 1)->via()->pluck('name');

$users = User::where('active', 1)->via()->get();

$users->wait();
```

- Raw SQL: [Offloading Queries to Worker Pools](/docs/{{version}}/framework/database/database#offloading-queries-to-worker-pools)
- Query builder: [Offloading Queries to Worker Pools](/docs/{{version}}/framework/database/queries#offloading-queries-to-worker-pools)
- Pagination: [Paginating on the Event Loop](/docs/{{version}}/framework/database/pagination#paginating-on-the-event-loop)
- Instrument models and collections: [Instrument](/docs/{{version}}/framework/instrument-orm/instrument) and [Instrument Collections](/docs/{{version}}/framework/instrument-orm/instrument-collections)

### Streaming Large Results

Methods that take a callback or yield rows, such as `cursor`, `lazy`, or `chunk`, can not cross to a worker. Use `stream` instead: it reads the query page by page in a worker and delivers each page to your process as a `Voyager\Database\IOPools\QueryChunk` signal. See [Streaming Results as Signals](/docs/{{version}}/framework/database/queries#streaming-results-as-signals).

## Transactions

To run a whole transaction in a worker, pass a closure to the offloaded connection's `transaction` method. The closure runs in the worker and receives that worker's connection. `beginTransaction` can not be offloaded on its own. See [Offloading Transactions](/docs/{{version}}/framework/database/database#offloading-transactions).

## Mixing Blocking and Offloaded Calls

Venusian keeps the calls offloaded on one connection in order, and blocking calls on that connection wait for the offloaded calls they must not overtake, so a read always sees the writes you made before it. See [Ordering Offloaded Calls](/docs/{{version}}/framework/database/database#ordering-offloaded-calls).

## What Can Not Be Offloaded

A worker opens its own connection, so `via` throws a `LogicException` for a connection it could not reach the same way:

- a connection with no name,
- an in-memory SQLite database (`:memory:`),
- a connection with a transaction open.

## Worker Connections

Each offloaded call carries the connection's name and its current configuration to the worker, so a connection whose configuration you changed at runtime is the one the worker queries. The worker keeps its connection open between calls and reopens it only when that configuration has changed.
