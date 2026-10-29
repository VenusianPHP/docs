# Cache

Venusian provides an expressive, unified API for various cache backends, with blocking calls and promise-based calls on the event loop.

## Introduction

Some of the data retrieval or processing tasks performed by your application could be CPU intensive or take several seconds to complete. When this is the case, it is common to cache the retrieved data for a time so it can be retrieved quickly the next time the same data is needed. The cached data is usually stored in a very fast data store such as [Redis](https://redis.io).

Thankfully, Venusian provides an expressive, unified API for various cache backends, allowing you to take advantage of their blazing fast data retrieval and speed up your application. When your application runs on the event loop, the same API is available as [promises](#async-cache-operations), so a cache read or write never blocks the loop.

## Configuration

Your application's cache configuration file is located at `config/cache.php`. In this file, you may specify which cache store you would like to be used by default throughout your application. Venusian supports [Redis](https://redis.io), relational databases, and a file based cache driver out of the box, while `array` and `null` cache drivers provide convenient cache backends for your automated tests.

The cache configuration file also contains a variety of other options that you may review. By default, Venusian is configured to use the `file` cache driver, which stores the serialized, cached objects in your application's `storage/framework/cache/data` directory.

### Driver Prerequisites

#### Database

When using the `database` cache driver, you will need a database table to contain the cache data, and a second table for the store's atomic locks. A new application already has a [database migration](/docs/{{version}}/framework/database/migrations) for both, `database/migrations/0001_01_01_000001_create_cache_table.php`, so running `php computer migrate` is enough. If yours does not, the `make:cache-table` Computer command creates it:

```shell
php computer make:cache-table

php computer migrate
```

The `table` and `lock_table` options name the two tables (`cache` and `cache_locks` by default), and `lock_connection` puts the locks on a different database connection than the cached values.

#### Redis

Before using a Redis cache with Venusian, you will need to either install the PhpRedis PHP extension via PECL or install the `predis/predis` package via Composer.

For more information on configuring Redis, consult its [documentation page](/docs/{{version}}/framework/database/redis#configuration).

## Cache Usage

### Obtaining a Cache Instance

The cache manager is registered in the service container as `cache`, and the default store's repository as `cache.store`. You may resolve either with `app()`, or type-hint the `Voyager\Contracts\Cache\Factory` or `Voyager\Contracts\Cache\Repository` contract on any class the container builds. Calls on the manager go to the default store, so `app('cache')` is what we will use throughout this documentation:

```php
<?php

namespace App\Services;

use Voyager\Contracts\Cache\Repository;

class UserDirectory
{
    public function __construct(
        protected Repository $cache,
    ) {}

    /**
     * Get a list of all users of the application.
     */
    public function all(): array
    {
        $value = $this->cache->get('key');

        return [
            // ...
        ];
    }
}
```

#### Accessing Multiple Cache Stores

Using the cache manager, you may access various cache stores via the `store` method. The key passed to the `store` method should correspond to one of the stores listed in the `stores` configuration array in your `cache` configuration file:

```php
$value = app('cache')->store('file')->get('foo');

app('cache')->store('redis')->put('bar', 'baz', 600); // 10 Minutes
```

### Retrieving Items From the Cache

The `get` method is used to retrieve items from the cache. If the item does not exist in the cache, `null` will be returned. If you wish, you may pass a second argument to the `get` method specifying the default value you wish to be returned if the item doesn't exist:

```php
$value = app('cache')->get('key');

$value = app('cache')->get('key', 'default');
```

You may even pass a closure as the default value. The result of the closure will be returned if the specified item does not exist in the cache. Passing a closure allows you to defer the retrieval of default values from a database or other external service:

```php
$value = app('cache')->get('key', function () {
    return app('db')->table(/* ... */)->get();
});
```

#### Determining Item Existence

The `has` method may be used to determine if an item exists in the cache. This method will also return `false` if the item exists but its value is `null`:

```php
if (app('cache')->has('key')) {
    // ...
}
```

#### Incrementing / Decrementing Values

The `increment` and `decrement` methods may be used to adjust the value of integer items in the cache. Both of these methods accept an optional second argument indicating the amount by which to increment or decrement the item's value:

```php
// Initialize the value if it does not exist...
app('cache')->add('key', 0, now()->plus(hours: 4));

// Increment or decrement the value...
app('cache')->increment('key');
app('cache')->increment('key', $amount);
app('cache')->decrement('key');
app('cache')->decrement('key', $amount);
```

#### Retrieve and Store

Sometimes you may wish to retrieve an item from the cache, but also store a default value if the requested item doesn't exist. For example, you may wish to retrieve all users from the cache or, if they don't exist, retrieve them from the database and add them to the cache. You may do this using the `remember` method:

```php
$value = app('cache')->remember('users', $seconds, function () {
    return app('db')->table('users')->get();
});
```

If the item does not exist in the cache, the closure passed to the `remember` method will be executed and its result will be placed in the cache.

You may use the `rememberForever` method, or its alias `sear`, to retrieve an item from the cache or store it forever if it does not exist:

```php
$value = app('cache')->rememberForever('users', function () {
    return app('db')->table('users')->get();
});
```

#### Stale While Revalidate

When using the `remember` method, some callers may wait on a slow recalculation if the cached value has expired. For certain types of data, it can be useful to allow partially stale data to be served while the cached value is recalculated in the background. This is often referred to as the "stale-while-revalidate" pattern, and the `flexible` method provides an implementation of this pattern.

The flexible method accepts an array that specifies how long the cached value is considered "fresh" and when it becomes "stale". The first value in the array represents the number of seconds the cache is considered fresh, while the second value defines how long it can be served as stale data before recalculation is necessary.

If the value is read within the fresh period (before the first value), the cache is returned immediately without recalculation. If it is read during the stale period (between the two values), the stale value is returned, and a [deferred function](/docs/{{version}}/framework/digging-deeper/helpers#deferred-functions) is registered to refresh the cached value once the current Computer command or queued job has finished successfully. If it is read after the second value, the cache is considered expired, and the value is recalculated immediately:

```php
$value = app('cache')->flexible('users', [5, 10], function () {
    return app('db')->table('users')->get();
});
```

#### Retrieve and Delete

If you need to retrieve an item from the cache and then delete the item, you may use the `pull` method. Like the `get` method, `null` will be returned if the item does not exist in the cache:

```php
$value = app('cache')->pull('key');

$value = app('cache')->pull('key', 'default');
```

### Storing Items in the Cache

You may use the `put` method to store items in the cache:

```php
app('cache')->put('key', 'value', $seconds = 10);
```

If the storage time is not passed to the `put` method, the item will be stored indefinitely:

```php
app('cache')->put('key', 'value');
```

Instead of passing the number of seconds as an integer, you may also pass a `DateTime` instance representing the desired expiration time of the cached item:

```php
app('cache')->put('key', 'value', now()->plus(minutes: 10));
```

#### Store if Not Present

The `add` method will only add the item to the cache if it does not already exist in the cache store. The method will return `true` if the item is actually added to the cache. Otherwise, the method will return `false`. The `add` method is an atomic operation:

```php
app('cache')->add('key', 'value', $seconds);
```

#### Storing Items Forever

The `forever` method may be used to store an item in the cache permanently. Since these items will not expire, they must be manually removed from the cache using the `forget` method:

```php
app('cache')->forever('key', 'value');
```

### Removing Items From the Cache

You may remove items from the cache using the `forget` method:

```php
app('cache')->forget('key');
```

You may also remove items by providing a zero or negative number of expiration seconds:

```php
app('cache')->put('key', 'value', 0);

app('cache')->put('key', 'value', -5);
```

You may clear the entire cache using the `flush` method:

```php
app('cache')->flush();
```

> [!WARNING]
> Flushing the cache does not respect your configured cache "prefix" and will remove all entries from the cache. Consider this carefully when clearing a cache which is shared by other applications.

#### Clearing the Cache From the Command Line

The `cache:clear` Computer command flushes a store, the default store unless you name one, and `cache:forget` removes a single key:

```shell
php computer cache:clear

php computer cache:clear redis

php computer cache:forget key

php computer cache:forget key redis
```

On a store that supports [tags](#cache-tags), the `--tags` option flushes only the items with the given comma-separated tags:

```shell
php computer cache:clear redis --tags=people,authors
```

### Async Cache Operations

Every blocking cache call above waits for its store before it returns. When your application runs on the event loop, the `async` method on a store's repository returns a `Voyager\Cache\Async\AsyncRepository` whose `get`, `has`, `pull`, `put`, `forever`, `add`, `increment`, `decrement`, `forget`, and `remember` methods each return a `Voyager\Contracts\IOPools\Promise` instead:

```php
$async = app('cache')->store('redis')->async();

$async->put('greeting', ['hello' => 'world'], 60);

$async->get('greeting')->then(function (?array $greeting) {
    // ...
});

$value = $async->remember('users', 60, function () {
    return app('db')->table('users')->get();
})->wait();
```

These methods accept the same arguments as their blocking counterparts and resolve with the same answers. Defaults, TTLs, a `put` with no time left becoming a `forget`, `remember`'s callback, and the [cache signals](#signals) are all handled in the calling process; only the store's I/O leaves it:

| Store | Where the I/O runs |
|---|---|
| `file` | On a worker pool: the thread pool when `io-pools.pool_workers.threads` is enabled, the process pool otherwise. |
| `database` | Offloaded on the store's database connection, like any other offloaded query on that connection. |
| `redis` | On a [Redis pipe](/docs/{{version}}/framework/database/redis#pipes), a socket of the store's connection that the event loop waits on. |
| `array`, `null` | In the calling process. The promise is already settled. |

A key's operations complete in the order they were made. A value is captured and its expiration counted from the moment you make the call, so a queued `put` stores the value it was given, and a `put` whose time runs out while it waits stores nothing. A blocking call on a key first waits for the async operations already made on it, so you may freely mix the two:

```php
$cache = app('cache')->store('file');

$cache->async()->put('handed-over', 'async write', 60);

$cache->get('handed-over'); // "async write"
```

The `file` store throws an `InvalidArgumentException` if neither worker pool is enabled in your `config/io-pools.php` file. An async call on the `database` store while its connection has a transaction open rejects with a `LogicException`, since the work would run outside that transaction. A [tagged cache](#cache-tags) has no async operations: its `async` method throws a `BadMethodCallException`, so call `async` on the untagged store instead.

<a id="cache-tags"></a>
## Cache Tags

> [!WARNING]
> Cache tags are not supported when using the `file` or `database` cache drivers.

### Storing Tagged Cache Items

Cache tags allow you to tag related items in the cache and then flush all cached values that have been assigned a given tag. You may access a tagged cache by passing in an ordered array of tag names. For example, let's access a tagged cache and `put` a value into the cache:

```php
app('cache')->tags(['people', 'artists'])->put('John', $john, $seconds);
app('cache')->tags(['people', 'authors'])->put('Anne', $anne, $seconds);
```

### Accessing Tagged Cache Items

Items stored via tags may not be accessed without also providing the tags that were used to store the value. To retrieve a tagged cache item, pass the same ordered list of tags to the `tags` method, then call the `get` method with the key you wish to retrieve:

```php
$john = app('cache')->tags(['people', 'artists'])->get('John');

$anne = app('cache')->tags(['people', 'authors'])->get('Anne');
```

### Removing Tagged Cache Items

You may flush all items that are assigned a tag or list of tags. For example, the following code would remove all caches tagged with either `people`, `authors`, or both. So, both `Anne` and `John` would be removed from the cache:

```php
app('cache')->tags(['people', 'authors'])->flush();
```

In contrast, the code below would remove only cached values tagged with `authors`, so `Anne` would be removed, but not `John`:

```php
app('cache')->tags('authors')->flush();
```

<a id="atomic-locks"></a>
## Atomic Locks

> [!WARNING]
> To utilize this feature, your application must be using the `redis`, `database`, `file`, or `array` cache driver as your application's default cache driver. In addition, all servers must be communicating with the same central cache server.

### Managing Locks

Atomic locks allow for the manipulation of distributed locks without worrying about race conditions. For example, you may use an atomic lock to ensure that only one instance of a task is running at a time. You may create and manage locks using the `lock` method:

```php
$lock = app('cache')->lock('foo', 10);

if ($lock->get()) {
    // Lock acquired for 10 seconds...

    $lock->release();
}
```

The `get` method also accepts a closure. After the closure is executed, Venusian will automatically release the lock:

```php
app('cache')->lock('foo', 10)->get(function () {
    // Lock acquired for 10 seconds and automatically released...
});
```

If the lock is not available at the moment you request it, you may instruct Venusian to wait for a specified number of seconds. If the lock cannot be acquired within the specified time limit, a `Voyager\Contracts\Cache\LockTimeoutException` will be thrown:

```php
use Voyager\Contracts\Cache\LockTimeoutException;

$lock = app('cache')->lock('foo', 10);

try {
    $lock->block(5);

    // Lock acquired after waiting a maximum of 5 seconds...
} catch (LockTimeoutException $e) {
    // Unable to acquire lock...
} finally {
    $lock->release();
}
```

The example above may be simplified by passing a closure to the `block` method. When a closure is passed to this method, Venusian will attempt to acquire the lock for the specified number of seconds and will automatically release the lock once the closure has been executed:

```php
app('cache')->lock('foo', 10)->block(5, function () {
    // Lock acquired for 10 seconds after waiting a maximum of 5 seconds...
});
```

### Managing Locks Across Processes

Sometimes, you may wish to acquire a lock in one process and release it in another process. For example, you may acquire a lock in a Computer command and wish to release the lock at the end of a queued job that the command dispatches. In this scenario, you should pass the lock's scoped "owner token" to the queued job so that the job can re-instantiate the lock using the given token.

In the example below, we will dispatch a queued job if a lock is successfully acquired. In addition, we will pass the lock's owner token to the queued job via the lock's `owner` method:

```php
$podcast = Podcast::find($id);

$lock = app('cache')->lock('processing', 120);

if ($lock->get()) {
    dispatch(new ProcessPodcast($podcast, $lock->owner()));
}
```

Within our application's `ProcessPodcast` job, we can restore and release the lock using the owner token:

```php
app('cache')->restoreLock('processing', $this->owner)->release();
```

If you would like to release a lock without respecting its current owner, you may use the `forceRelease` method:

```php
app('cache')->lock('processing')->forceRelease();
```

### Refreshing Locks

If you need to extend the expiration of a lock that you currently own, you may use the `refresh` method. If no number of seconds is provided, the lock's original duration will be used. This is useful for long-running operations where you prefer to acquire a short lock and periodically extend it instead of acquiring a lock with a very long expiration time:

```php
$lock = app('cache')->lock('generate-reports', 60);

if ($lock->get()) {
    foreach ($reports as $report) {
        $report->generate();

        // Extend the lock for another 60 seconds...
        $lock->refresh();
    }

    $lock->release();
}
```

### Concurrency Limiting

Venusian's atomic lock functionality also provides a few ways to limit concurrent execution of closures. Use `withoutOverlapping` when you want to allow only one running instance across your infrastructure:

```php
app('cache')->withoutOverlapping('foo', function () {
    // Lock acquired after waiting a maximum of 10 seconds...
});
```

By default, the lock is held until the closure finishes executing, and the method waits up to 10 seconds to acquire the lock. You may customize these values using additional arguments:

```php
app('cache')->withoutOverlapping('foo', function () {
    // Lock acquired for 120 seconds after waiting a maximum of 5 seconds...
}, lockFor: 120, waitFor: 5);
```

If the lock cannot be acquired within the specified wait time, a `Voyager\Contracts\Cache\LockTimeoutException` will be thrown.

If you want controlled parallelism, use the `funnel` method to set a maximum number of concurrent executions. The `funnel` method works with any cache driver that supports locks:

```php
app('cache')->funnel('foo')
    ->limit(3)
    ->releaseAfter(60)
    ->block(10)
    ->then(function () {
        // Concurrency lock acquired...
    }, function () {
        // Could not acquire concurrency lock...
    });
```

The `funnel` key identifies the resource being limited. The `limit` method defines the maximum concurrent executions. The `releaseAfter` method sets a safety timeout in seconds before an acquired slot is automatically released. The `block` method sets how many seconds to wait for an available slot.

If you prefer to handle the timeout via exceptions instead of providing a failure closure, you may omit the second closure. A `Voyager\Cache\Limiters\LimiterTimeoutException` will be thrown if the lock cannot be acquired within the specified wait time:

```php
use Voyager\Cache\Limiters\LimiterTimeoutException;

try {
    app('cache')->funnel('foo')
        ->limit(3)
        ->releaseAfter(60)
        ->block(10)
        ->then(function () {
            // Concurrency lock acquired...
        });
} catch (LimiterTimeoutException $e) {
    // Unable to acquire concurrency lock...
}
```

If you would like to use a specific cache store for the concurrency limiter, you may invoke the `funnel` method on the desired store:

```php
app('cache')->store('redis')->funnel('foo')
    ->limit(3)
    ->block(10)
    ->then(function () {
        // Concurrency lock acquired using the "redis" store...
    });
```

> [!NOTE]
> The `funnel` method requires the cache store to implement the `Voyager\Contracts\Cache\LockProvider` interface. If you attempt to use `funnel` with a cache store that does not support locks, a `BadMethodCallException` will be thrown.

## Adding Custom Cache Drivers

### Writing the Driver

To create our custom cache driver, we first need to implement the `Voyager\Contracts\Cache\Store` [contract](/docs/{{version}}/framework/digging-deeper/contracts). So, a MongoDB cache implementation might look something like this:

```php
<?php

namespace App\Extensions;

use Voyager\Contracts\Cache\Store;

class MongoStore implements Store
{
    public function get(string $key): mixed {}
    public function many(array $keys): array {}
    public function put(string $key, mixed $value, int $seconds): bool {}
    public function putMany(array $values, int $seconds): bool {}
    public function increment(string $key, mixed $value = 1): bool|int {}
    public function decrement(string $key, mixed $value = 1): bool|int {}
    public function forever(string $key, mixed $value): bool {}
    public function forget(string $key): bool {}
    public function flush(): bool {}
    public function getPrefix(): string {}
}
```

We just need to implement each of these methods using a MongoDB connection. For an example of how to implement each of these methods, take a look at `Voyager\Cache\DatabaseStore` in the framework source. Once our implementation is complete, we can finish our custom driver registration by calling the cache manager's `extend` method:

```php
app('cache')->extend('mongo', function ($app, array $config) {
    return $this->repository(new MongoStore, $config);
});
```

> [!NOTE]
> If you're wondering where to put your custom cache driver code, you could create an `Extensions` namespace within your `app` directory. However, keep in mind that Venusian does not have a rigid application structure and you are free to organize your application according to your preferences.

### Registering the Driver

To register the custom cache driver with Venusian, we will use the `extend` method on the cache manager. Since other service providers may attempt to read cached values within their `boot` method, we will register our custom driver within a `booting` callback. By using the `booting` callback, we can ensure that the custom driver is registered just before the `boot` method is called on our application's service providers but after the `register` method is called on all of the service providers. We will register our `booting` callback within the `register` method of our application's `App\Providers\AppServiceProvider` class:

```php
<?php

namespace App\Providers;

use App\Extensions\MongoStore;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->booting(function () {
            app('cache')->extend('mongo', function ($app, array $config) {
                return $this->repository(new MongoStore, $config);
            });
        });
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // ...
    }
}
```

The first argument passed to the `extend` method is the name of the driver. This will correspond to your `driver` option in the `config/cache.php` configuration file. The second argument is a closure that should return a `Voyager\Cache\Repository` instance. The closure is bound to the cache manager, so `$this->repository` wraps your store the way the built-in drivers are wrapped, and it is passed the [service container](/docs/{{version}}/framework/architecture-concepts/container) instance and the store's configuration array. A repository built this way has [async operations](#async-cache-operations) that run in the calling process, since the manager only knows how to move the built-in stores' I/O off it.

Once your extension is registered, update the `CACHE_STORE` environment variable or `default` option within your application's `config/cache.php` configuration file to the name of your extension.

## Signals

To execute code on every cache operation, you may listen for various [signals](/docs/{{version}}/framework/digging-deeper/signals) dispatched by the cache:

| Signal Name                                 |
|---------------------------------------------|
| `Voyager\Cache\Signals\CacheFlushed`        |
| `Voyager\Cache\Signals\CacheFlushing`       |
| `Voyager\Cache\Signals\CacheFlushFailed`    |
| `Voyager\Cache\Signals\CacheHit`            |
| `Voyager\Cache\Signals\CacheMissed`         |
| `Voyager\Cache\Signals\ForgettingKey`       |
| `Voyager\Cache\Signals\KeyForgetFailed`     |
| `Voyager\Cache\Signals\KeyForgotten`        |
| `Voyager\Cache\Signals\KeyWriteFailed`      |
| `Voyager\Cache\Signals\KeyWritten`          |
| `Voyager\Cache\Signals\RetrievingKey`       |
| `Voyager\Cache\Signals\RetrievingManyKeys`  |
| `Voyager\Cache\Signals\WritingKey`          |
| `Voyager\Cache\Signals\WritingManyKeys`     |

```php
use Voyager\Cache\Signals\KeyWritten;

app('signals')->listen(KeyWritten::class, function (KeyWritten $written) {
    // $written->key...
});
```

Async cache operations dispatch the same signals, once each, in the calling process.

To increase performance, you may disable cache signals by setting the `events` configuration option to `false` for a given cache store in your application's `config/cache.php` configuration file:

```php
'database' => [
    'driver' => 'database',
    // ...
    'events' => false,
],
```
