# Queues

Venusian queues let you move slow tasks out of the code path that triggers them and run them on a queue worker, a worker pool, or a later turn of the event loop.

## Introduction

While building your application, you may have some tasks, such as parsing and storing an imported CSV file, that take too long to perform while the user waits. Thankfully, Venusian allows you to easily create queued jobs that may be processed in the background. By moving time intensive tasks to a queue, your application can stay responsive and provide a better experience to its users.

Venusian queues provide a unified queueing API across a variety of different queue backends, such as [Redis](https://redis.io), a relational database, a worker pool in your own process, or the next turn of the event loop.

Venusian's queue configuration options are stored in your application's `config/queue.php` configuration file. In this file, you will find connection configurations for each of the queue drivers that are included with the framework:

| Driver | Where the job runs |
|---|---|
| `sync` | Immediately, in the current process. This is the default connection. |
| `database` | Stored as a row in a database table until a worker runs it. |
| `redis` | Stored in Redis lists until a worker runs it. |
| `background` | On a process or thread worker pool, in your own process. The push returns a promise. |
| `deferred` | In the current process, on the event loop's next turn. The push returns a promise. |
| `failover` | Tries a list of other connections in order. |
| `null` | Nowhere. The job is discarded. |

The queue manager is bound in the service container as `queue`. You may resolve it with `app('queue')`, or type-hint the `Voyager\Contracts\Queue\Factory` contract.

### Connections vs. Queues

Before getting started with Venusian queues, it is important to understand the distinction between "connections" and "queues". In your `config/queue.php` configuration file, there is a `connections` configuration array. This option defines the connections to backend queue services such as Redis or a database. However, any given queue connection may have multiple "queues" which may be thought of as different stacks or piles of queued jobs.

Note that each connection configuration example in the `queue` configuration file contains a `queue` attribute. This is the default queue that jobs will be dispatched to when they are sent to a given connection. In other words, if you dispatch a job without explicitly defining which queue it should be dispatched to, the job will be placed on the queue that is defined in the `queue` attribute of the connection configuration:

```php
use App\Jobs\ProcessPodcast;

// This job is sent to the default connection's default queue...
ProcessPodcast::dispatch();

// This job is sent to the default connection's "emails" queue...
ProcessPodcast::dispatch()->onQueue('emails');
```

Some applications may not need to ever push jobs onto multiple queues, instead preferring to have one simple queue. However, pushing jobs to multiple queues can be especially useful for applications that wish to prioritize or segment how jobs are processed, since the Venusian queue worker allows you to specify which queues it should process by priority. For example, if you push jobs to a `high` queue, you may run a worker that gives them higher processing priority:

```shell
php computer queue:work --queue=high,default
```

### Driver Notes and Prerequisites

#### Database

In order to use the `database` queue driver, you will need a database table to hold the jobs. You may use the `make:queue-table` Computer command to create its [database migration](/docs/{{version}}/framework/database/migrations):

```shell
php computer make:queue-table

php computer migrate
```

The command writes the migration once. If a `jobs` table migration already exists in your application, it reports that and writes nothing.

When a worker pops a job, the `database` driver reserves the oldest available row inside a transaction. On MySQL 8.0.1+, MariaDB 10.6+, PostgreSQL 9.5+, and Vitess 19+ it uses `FOR UPDATE SKIP LOCKED`, so several workers may pull from one table without waiting on each other.

#### Redis

In order to use the `redis` queue driver, you should configure a Redis database connection in your `config/database.php` configuration file.

> [!WARNING]
> The `serializer` and `compression` Redis options are not supported by the `redis` queue driver.

##### Redis Cluster

If your Redis queue connection uses a [Redis Cluster](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering), your queue names must contain a [key hash tag](https://redis.io/docs/latest/develop/using-commands/keyspace/#hashtags). This is required in order to ensure all of the Redis keys for a given queue are placed into the same hash slot:

```php
'redis' => [
    'driver' => 'redis',
    'connection' => env('REDIS_QUEUE_CONNECTION', 'default'),
    'queue' => env('REDIS_QUEUE', '{default}'),
    'retry_after' => (int) env('REDIS_QUEUE_RETRY_AFTER', 90),
    'block_for' => null,
    'after_commit' => false,
],
```

##### Blocking

When using the Redis queue, you may use the `block_for` configuration option to specify how long the driver should wait for a job to become available before iterating through the worker loop and re-polling the Redis database.

Adjusting this value based on your queue load can be more efficient than continually polling the Redis database for new jobs. For instance, you may set the value to `5` to indicate that the driver should block for five seconds while waiting for a job to become available:

```php
'redis' => [
    'driver' => 'redis',
    'connection' => env('REDIS_QUEUE_CONNECTION', 'default'),
    'queue' => env('REDIS_QUEUE', 'default'),
    'retry_after' => (int) env('REDIS_QUEUE_RETRY_AFTER', 90),
    'block_for' => 5,
    'after_commit' => false,
],
```

> [!WARNING]
> Setting `block_for` to `0` will cause queue workers to block indefinitely until a job is available. This will also prevent signals such as `SIGTERM` from being handled until the next job has been processed.

#### Background

The `background` driver runs each pushed job on one of your application's worker pools, inside your own process, without a separate `queue:work` command. Its `pool` option chooses the pool: `thread` for the thread workers, `process` for the process workers, or leave it unset to use the thread workers when they are enabled and the process workers otherwise:

```php
'background' => [
    'driver' => 'background',
    'pool' => env('QUEUE_BACKGROUND_POOL'),
],
```

The chosen pool must be enabled in your `config/io-pools.php` file (`io-pools.pool_workers.process.enabled` or `io-pools.pool_workers.threads.enabled`). Because the job is serialized and run by a pool worker, its class must be autoloadable there and everything it carries must serialize.

#### Deferred

The `deferred` driver runs the job in the current process on the event loop's next turn, so the code that dispatched it finishes first. It needs no worker and no configuration beyond its driver:

```php
'deferred' => [
    'driver' => 'deferred',
],
```

#### Other Driver Prerequisites

The following dependencies are needed for the listed queue drivers. These dependencies may be installed via the Composer package manager:

- Redis: `predis/predis ^2.3|^3.0` or the phpredis PHP extension

<a id="creating-jobs"></a>
## Creating Jobs

### Generating Job Classes

By convention, the queueable jobs for your application live in the `app/Jobs` directory. Write each job class by hand. A job implements the `Voyager\Contracts\Queue\ShouldQueue` interface, indicating to Venusian that the job should be pushed onto the queue to run asynchronously. Add the `Batchable` trait to a job that takes part in [job batching](#job-batching).

> [!NOTE]
> Job stubs may be customized using [stub publishing](/docs/{{version}}/framework/digging-deeper/computer#stub-customization).

### Class Structure

Job classes are very simple, normally containing only a `handle` method that is invoked when the job is processed by the queue. To get started, let's take a look at an example job class. In this example, we'll pretend we manage a podcast publishing service and need to process the uploaded podcast files before they are published:

```php
<?php

namespace App\Jobs;

use App\Models\Podcast;
use App\Services\AudioProcessor;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public Podcast $podcast,
    ) {}

    /**
     * Execute the job.
     */
    public function handle(?AudioProcessor $processor = null): mixed
    {
        // Process uploaded podcast...

        return null;
    }
}
```

`ShouldQueue` extends `Voyager\Contracts\NutsAndBolts\Handleable`, which declares `handle(): mixed`. A queued job's `handle` method therefore takes no required parameters and declares a `mixed` return type. The value it returns is handed back to code that runs the job directly, such as `dispatchSync`.

In this example, note that we were able to pass an [Instrument model](/docs/{{version}}/framework/instrument-orm/instrument) directly into the queued job's constructor. Because of the `Queueable` trait that the job is using, Instrument models and their loaded relationships will be gracefully serialized and unserialized when the job is processing.

If your queued job accepts an Instrument model in its constructor, only the identifier for the model will be serialized onto the queue. When the job is actually handled, the queue system will automatically re-retrieve the full model instance and its loaded relationships from the database. This approach to model serialization allows for much smaller job payloads to be sent to your queue driver.

#### `handle` Method Dependency Injection

The `handle` method is invoked when the job is processed by the queue. Note that we are able to type-hint dependencies on the `handle` method of the job. The Venusian [service container](/docs/{{version}}/framework/architecture-concepts/container) resolves every class-typed parameter and injects it, even when the parameter is nullable with a `null` default as shown above.

> [!WARNING]
> Binary data, such as raw image contents, should be passed through the `base64_encode` function before being passed to a queued job. Otherwise, the job may not properly serialize to JSON when being placed on the queue.

#### Queued Relationships

Because all loaded Instrument model relationships also get serialized when a job is queued, the serialized job string can sometimes become quite large. Furthermore, when a job is deserialized and model relationships are re-retrieved from the database, they will be retrieved in their entirety. Any previous relationship constraints that were applied before the model was serialized during the job queueing process will not be applied when the job is deserialized. Therefore, if you wish to work with a subset of a given relationship, you should re-constrain that relationship within your queued job.

Or, to prevent relations from being serialized, you can call the `withoutRelations` method on the model when setting a property value. This method will return an instance of the model without its loaded relationships:

```php
/**
 * Create a new job instance.
 */
public function __construct(
    Podcast $podcast,
) {
    $this->podcast = $podcast->withoutRelations();
}
```

If you only need to remove specific relations while keeping the rest, you may use the `withoutRelation` method:

```php
$this->podcast = $podcast->withoutRelation('comments');
```

If you are using [PHP constructor property promotion](https://www.php.net/manual/en/language.oop5.decon.php#language.oop5.decon.constructor.promotion) and would like to indicate that an Instrument model should not have its relations serialized, you may use the `WithoutRelations` attribute:

```php
use Voyager\Queue\Attributes\WithoutRelations;

/**
 * Create a new job instance.
 */
public function __construct(
    #[WithoutRelations]
    public Podcast $podcast,
) {}
```

For convenience, if you wish to serialize all models without relationships, you may apply the `WithoutRelations` attribute to the entire class instead of applying the attribute to each model:

```php
<?php

namespace App\Jobs;

use App\Models\DistributionPlatform;
use App\Models\Podcast;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;
use Voyager\Queue\Attributes\WithoutRelations;

#[WithoutRelations]
class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public Podcast $podcast,
        public DistributionPlatform $platform,
    ) {}
}
```

If a job receives a collection or array of Instrument models instead of a single model, the models within that collection will not have their relationships restored when the job is deserialized and executed. This is to prevent excessive resource usage on jobs that deal with large numbers of models.

<a id="unique-jobs"></a>
### Unique Jobs

> [!WARNING]
> Unique jobs require a cache driver that supports [locks](/docs/{{version}}/framework/digging-deeper/cache#atomic-locks). Currently, the `redis`, `database`, `file`, and `array` cache drivers support atomic locks.

> [!WARNING]
> Unique job constraints do not apply to jobs within batches.

Sometimes, you may want to ensure that only one instance of a specific job is on the queue at any point in time. You may do so by implementing the `ShouldBeUnique` interface on your job class. This interface does not require you to define any additional methods on your class:

```php
<?php

use Voyager\Contracts\Queue\ShouldBeUnique;
use Voyager\Contracts\Queue\ShouldQueue;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    // ...
}
```

In the example above, the `UpdateSearchIndex` job is unique. So, the job will not be dispatched if another instance of the job is already on the queue and has not finished processing.

In certain cases, you may want to define a specific "key" that makes the job unique or you may want to specify a timeout beyond which the job no longer stays unique. To accomplish this, you may define a `uniqueFor` property and a `uniqueId` method on your job class:

```php
<?php

namespace App\Jobs;

use Voyager\Contracts\Queue\ShouldBeUnique;
use Voyager\Contracts\Queue\ShouldQueue;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    /**
     * The product instance.
     *
     * @var \App\Models\Product
     */
    public $product;

    /**
     * The number of seconds after which the job's unique lock will be released.
     *
     * @var int
     */
    public $uniqueFor = 3600;

    /**
     * Get the unique ID for the job.
     */
    public function uniqueId(): string
    {
        return $this->product->id;
    }
}
```

In the example above, the `UpdateSearchIndex` job is unique by a product ID. So, any new dispatches of the job with the same product ID will be ignored until the existing job has completed processing. In addition, if the existing job is not processed within one hour, the unique lock will be released and another job with the same unique key can be dispatched to the queue.

> [!WARNING]
> If your application dispatches jobs from multiple servers or containers, you should ensure that all of your servers are communicating with the same central cache server so that Venusian can accurately determine if a job is unique.

#### Keeping Jobs Unique Until Processing Begins

By default, unique jobs are "unlocked" after a job completes processing or fails all of its retry attempts. However, there may be situations where you would like your job to unlock immediately before it is processed. To accomplish this, your job should implement the `ShouldBeUniqueUntilProcessing` contract instead of the `ShouldBeUnique` contract:

```php
<?php

use Voyager\Contracts\Queue\ShouldBeUniqueUntilProcessing;
use Voyager\Contracts\Queue\ShouldQueue;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUniqueUntilProcessing
{
    // ...
}
```

#### Unique Job Locks

Behind the scenes, when a `ShouldBeUnique` job is dispatched, Venusian attempts to acquire a [lock](/docs/{{version}}/framework/digging-deeper/cache#atomic-locks) with the `uniqueId` key. If the lock is already held, the job is not dispatched. This lock is released when the job completes processing or fails all of its retry attempts. By default, Venusian will use the default cache driver to obtain this lock. However, if you wish to use another driver for acquiring the lock, you may define a `uniqueVia` method that returns the cache driver that should be used:

```php
use Voyager\Contracts\Cache\Repository;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    // ...

    /**
     * Get the cache driver for the unique job lock.
     */
    public function uniqueVia(): Repository
    {
        return app('cache')->store('redis');
    }
}
```

> [!NOTE]
> If you only need to limit the concurrent processing of a job, use the [WithoutOverlapping](#preventing-job-overlaps) job middleware instead.

### Encrypted Jobs

Venusian allows you to ensure the privacy and integrity of a job's data via [encryption](/docs/{{version}}/framework/security/encryption). To get started, simply add the `ShouldBeEncrypted` interface to the job class. Once this interface has been added to the class, Venusian will automatically encrypt your job before pushing it onto a queue:

```php
<?php

use Voyager\Contracts\Queue\ShouldBeEncrypted;
use Voyager\Contracts\Queue\ShouldQueue;

class UpdateSearchIndex implements ShouldQueue, ShouldBeEncrypted
{
    // ...
}
```

<a id="job-middleware"></a>
## Job Middleware

Job middleware allow you to wrap custom logic around the execution of queued jobs, reducing boilerplate in the jobs themselves. For example, consider the following `handle` method which leverages Venusian's Redis rate limiting features to allow only one job to process every five seconds:

```php
/**
 * Execute the job.
 */
public function handle(): mixed
{
    return app('redis')->throttle('key')->block(0)->allow(1)->every(5)->then(function () {
        app('log')->info('Lock obtained...');

        // Handle job...
    }, function () {
        // Could not obtain lock...

        return $this->release(5);
    });
}
```

While this code is valid, the implementation of the `handle` method becomes noisy since it is cluttered with Redis rate limiting logic. In addition, this rate limiting logic must be duplicated for any other jobs that we want to rate limit. Instead of rate limiting in the handle method, we could define a job middleware that handles rate limiting:

```php
<?php

namespace App\Jobs\Middleware;

use Closure;

class RateLimited
{
    /**
     * Process the queued job.
     *
     * @param  \Closure(object): void  $next
     */
    public function handle(object $job, Closure $next): void
    {
        app('redis')->throttle('key')
            ->block(0)->allow(1)->every(5)
            ->then(function () use ($job, $next) {
                // Lock obtained...

                $next($job);
            }, function () use ($job) {
                // Could not obtain lock...

                $job->release(5);
            });
    }
}
```

As you can see, job middleware receive the job being processed and a callback that should be invoked to continue processing the job.

Job middleware are plain classes, conventionally placed in `app/Jobs/Middleware`. Attach them to a job by returning them from the job's `middleware` method:

```php
use App\Jobs\Middleware\RateLimited;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new RateLimited];
}
```

> [!NOTE]
> Job middleware can also be assigned to [queued signal listeners](/docs/{{version}}/framework/digging-deeper/signals#queued-signal-listeners).

### Rate Limiting

Although we just demonstrated how to write your own rate limiting job middleware, Venusian actually includes a rate limiting middleware that you may utilize to rate limit jobs. Job rate limiters are defined using the `for` method of the `Voyager\Cache\RateLimiter`, which the container provides as a singleton.

For example, you may wish to allow users to backup their data once per hour while imposing no such limit on premium customers. To accomplish this, you may define a rate limiter in the `boot` method of your `AppServiceProvider`:

```php
use Voyager\Cache\RateLimiter;
use Voyager\Cache\RateLimiting\Limit;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app(RateLimiter::class)->for('backups', function (object $job) {
        return $job->user->vipCustomer()
            ? Limit::none()
            : Limit::perHour(1)->by($job->user->id);
    });
}
```

In the example above, we defined an hourly rate limit; however, you may easily define a rate limit based on minutes using the `perMinute` method. In addition, you may pass any value you wish to the `by` method of the rate limit; however, this value is most often used to segment rate limits by customer:

```php
return Limit::perMinute(50)->by($job->user->id);
```

Once you have defined your rate limit, you may attach the rate limiter to your job using the `Voyager\Queue\Middleware\RateLimited` middleware. Each time the job exceeds the rate limit, this middleware will release the job back to the queue with an appropriate delay based on the rate limit duration:

```php
use Voyager\Queue\Middleware\RateLimited;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new RateLimited('backups')];
}
```

Releasing a rate limited job back onto the queue will still increment the job's total number of `attempts`. You may wish to tune your `tries` and `maxExceptions` properties on your job class accordingly. Or, you may wish to use the [retryUntil method](#time-based-attempts) to define the amount of time until the job should no longer be attempted.

Using the `releaseAfter` method, you may also specify the number of seconds that must elapse before the released job will be attempted again:

```php
/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new RateLimited('backups'))->releaseAfter(60)];
}
```

If you do not want a job to be retried when it is rate limited, you may use the `dontRelease` method:

```php
/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new RateLimited('backups'))->dontRelease()];
}
```

#### Rate Limiting With Redis

If you are using Redis, you may use the `Voyager\Queue\Middleware\RateLimitedWithRedis` middleware, which is fine-tuned for Redis and more efficient than the basic rate limiting middleware:

```php
use Voyager\Queue\Middleware\RateLimitedWithRedis;

public function middleware(): array
{
    return [new RateLimitedWithRedis('backups')];
}
```

The `connection` method may be used to specify which Redis connection the middleware should use:

```php
return [(new RateLimitedWithRedis('backups'))->connection('limiter')];
```

<a id="preventing-job-overlaps"></a>
### Preventing Job Overlaps

Venusian includes a `Voyager\Queue\Middleware\WithoutOverlapping` middleware that allows you to prevent job overlaps based on an arbitrary key. This can be helpful when a queued job is modifying a resource that should only be modified by one job at a time.

For example, let's imagine you have a queued job that updates a user's credit score and you want to prevent credit score update job overlaps for the same user ID. To accomplish this, you can return the `WithoutOverlapping` middleware from your job's `middleware` method:

```php
use Voyager\Queue\Middleware\WithoutOverlapping;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new WithoutOverlapping($this->user->id)];
}
```

Releasing an overlapping job back onto the queue will still increment the job's total number of attempts. You may wish to tune your `tries` and `maxExceptions` properties on your job class accordingly. For example, leaving `tries` at 1 as it is by default would prevent any overlapping job from being retried later.

Any overlapping jobs of the same type will be released back to the queue. You may also specify the number of seconds that must elapse before the released job will be attempted again:

```php
/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->releaseAfter(60)];
}
```

If you wish to immediately delete any overlapping jobs so that they will not be retried, you may use the `dontRelease` method:

```php
/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->dontRelease()];
}
```

The `WithoutOverlapping` middleware is powered by Venusian's atomic lock feature. Sometimes, your job may unexpectedly fail or timeout in such a way that the lock is not released. Therefore, you may explicitly define a lock expiration time using the `expireAfter` method. For example, the example below will instruct Venusian to release the `WithoutOverlapping` lock three minutes after the job has started processing:

```php
/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->expireAfter(180)];
}
```

> [!WARNING]
> The `WithoutOverlapping` middleware requires a cache driver that supports [locks](/docs/{{version}}/framework/digging-deeper/cache#atomic-locks). Currently, the `redis`, `database`, `file`, and `array` cache drivers support atomic locks.

#### Sharing Lock Keys Across Job Classes

By default, the `WithoutOverlapping` middleware will only prevent overlapping jobs of the same class. So, although two different job classes may use the same lock key, they will not be prevented from overlapping. However, you can instruct Venusian to apply the key across job classes using the `shared` method:

```php
use Voyager\Queue\Middleware\WithoutOverlapping;

class ProviderIsDown
{
    // ...

    public function middleware(): array
    {
        return [
            (new WithoutOverlapping("status:{$this->provider}"))->shared(),
        ];
    }
}

class ProviderIsUp
{
    // ...

    public function middleware(): array
    {
        return [
            (new WithoutOverlapping("status:{$this->provider}"))->shared(),
        ];
    }
}
```

### Throttling Exceptions

Venusian includes a `Voyager\Queue\Middleware\ThrottlesExceptions` middleware that allows you to throttle exceptions. Once the job throws a given number of exceptions, all further attempts to execute the job are delayed until a specified time interval lapses. This middleware is particularly useful for jobs that interact with third-party services that are unstable.

For example, let's imagine a queued job that interacts with a third-party API that begins throwing exceptions. To throttle exceptions, you can return the `ThrottlesExceptions` middleware from your job's `middleware` method. Typically, this middleware should be paired with a job that implements [time based attempts](#time-based-attempts):

```php
use DateTimeInterface;
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new ThrottlesExceptions(10, 5 * 60)];
}

/**
 * Determine the time at which the job should timeout.
 */
public function retryUntil(): DateTimeInterface
{
    return now()->addMinutes(30);
}
```

The first constructor argument accepted by the middleware is the number of exceptions the job can throw before being throttled, while the second constructor argument is the number of seconds that should elapse before the job is attempted again once it has been throttled. In the code example above, if the job throws 10 consecutive exceptions, we will wait 5 minutes before attempting the job again, constrained by the 30-minute time limit.

When a job throws an exception but the exception threshold has not yet been reached, the job will typically be retried immediately. However, you may specify the number of minutes such a job should be delayed by calling the `backoff` method when attaching the middleware to the job:

```php
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 5 * 60))->backoff(5)];
}
```

The `backoff` method also accepts a closure that receives the thrown exception, allowing the delay to be determined dynamically:

```php
use App\Exceptions\RateLimitedException;
use Throwable;
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 5 * 60))->backoff(
        fn (Throwable $throwable) => $throwable instanceof RateLimitedException
            ? $throwable->retryAfterMinutes()
            : 5
    )];
}
```

Internally, this middleware uses Venusian's cache system to implement rate limiting, and the job's class name is utilized as the cache "key". You may override this key by calling the `by` method when attaching the middleware to your job. This may be useful if you have multiple jobs interacting with the same third-party service and you would like them to share a common throttling "bucket" ensuring they respect a single shared limit:

```php
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->by('key')];
}
```

By default, this middleware will throttle every exception. You can modify this behavior by invoking the `when` method when attaching the middleware to your job. The exception will then only be throttled if the closure provided to the `when` method returns `true`:

```php
use Throwable;
use Voyager\Http\Client\HttpClientException;
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->when(
        fn (Throwable $throwable) => $throwable instanceof HttpClientException
    )];
}
```

Unlike the `when` method, which releases the job back onto the queue or throws an exception, the `deleteWhen` method allows you to delete the job entirely when a given exception occurs:

```php
use App\Exceptions\CustomerDeletedException;
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(2, 10 * 60))->deleteWhen(CustomerDeletedException::class)];
}
```

The `failWhen` method works the same way, but marks the job as failed instead of deleting it.

If you would like to have the throttled exceptions reported to your application's exception handler, you can do so by invoking the `report` method when attaching the middleware to your job. Optionally, you may provide a closure to the `report` method and the exception will only be reported if the given closure returns `true`:

```php
use Throwable;
use Voyager\Http\Client\HttpClientException;
use Voyager\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->report(
        fn (Throwable $throwable) => $throwable instanceof HttpClientException
    )];
}
```

#### Throttling Exceptions With Redis

If you are using Redis, you may use the `Voyager\Queue\Middleware\ThrottlesExceptionsWithRedis` middleware, which is fine-tuned for Redis and more efficient than the basic exception throttling middleware:

```php
use Voyager\Queue\Middleware\ThrottlesExceptionsWithRedis;

public function middleware(): array
{
    return [new ThrottlesExceptionsWithRedis(10, 10 * 60)];
}
```

The `connection` method may be used to specify which Redis connection the middleware should use:

```php
return [(new ThrottlesExceptionsWithRedis(10, 10 * 60))->connection('limiter')];
```

### Skipping Jobs

The `Skip` middleware allows you to specify that a job should be skipped / deleted without needing to modify the job's logic. The `Skip::when` method will delete the job if the given condition evaluates to `true`, while the `Skip::unless` method will delete the job if the condition evaluates to `false`:

```php
use Voyager\Queue\Middleware\Skip;

/**
 * Get the middleware the job should pass through.
 */
public function middleware(): array
{
    return [
        Skip::when($condition),
    ];
}
```

You can also pass a `Closure` to the `when` and `unless` methods for more complex conditional evaluation:

```php
use Voyager\Queue\Middleware\Skip;

/**
 * Get the middleware the job should pass through.
 */
public function middleware(): array
{
    return [
        Skip::when(function (): bool {
            return $this->shouldSkip();
        }),
    ];
}
```

## Dispatching Jobs

Once you have written your job class, you may dispatch it using the `dispatch` method on the job itself. The arguments passed to the `dispatch` method will be given to the job's constructor:

```php
<?php

namespace App\Podcasts;

use App\Jobs\ProcessPodcast;
use App\Models\Podcast;

class StorePodcast
{
    /**
     * Store a new podcast.
     */
    public function __invoke(array $attributes): Podcast
    {
        $podcast = Podcast::create($attributes);

        // ...

        ProcessPodcast::dispatch($podcast);

        return $podcast;
    }
}
```

The `dispatch` helper does the same for a job instance you have already built:

```php
dispatch(new ProcessPodcast($podcast));
```

If you would like to conditionally dispatch a job, you may use the `dispatchIf` and `dispatchUnless` methods:

```php
ProcessPodcast::dispatchIf($accountActive, $podcast);

ProcessPodcast::dispatchUnless($accountSuspended, $podcast);
```

In new Venusian applications, the `sync` connection is defined as the default queue. You may specify a different default queue connection by changing the `QUEUE_CONNECTION` environment variable in your application's `.env` file.

A job carries the log [context](/docs/{{version}}/framework/digging-deeper/context) it was dispatched in. When a worker runs the job, that context is restored, so log entries written by the job share the values of the code that dispatched it.

### Delayed Dispatching

If you would like to specify that a job should not be immediately available for processing by a queue worker, you may use the `delay` method when dispatching the job. For example, let's specify that a job should not be available for processing until 10 minutes after it has been dispatched:

```php
ProcessPodcast::dispatch($podcast)
    ->delay(now()->addMinutes(10));
```

In some cases, jobs may have a default delay configured. If you need to bypass this delay and dispatch a job for immediate processing, you may use the `withoutDelay` method:

```php
ProcessPodcast::dispatch($podcast)->withoutDelay();
```

<a id="synchronous-dispatching"></a>
### Synchronous Dispatching

If you would like to dispatch a job immediately (synchronously), you may use the `dispatchSync` method. When using this method, the job will not be queued and will be executed immediately within the current process. The method returns whatever the job's `handle` method returned:

```php
$result = ProcessPodcast::dispatchSync($podcast);
```

#### Deferred and Background Dispatching

Dispatching a job to the `deferred` connection runs it within the current process on the event loop's next turn, after the code that dispatched it has finished:

```php
RecordDelivery::dispatch($order)->onConnection('deferred');
```

The `background` connection hands the job to one of your application's worker pools instead, so it runs alongside your code in a pool worker rather than in the code path that dispatched it:

```php
RecordDelivery::dispatch($order)->onConnection('background');
```

Neither connection needs a `queue:work` process. When you push to them through the queue manager, the push returns a `Voyager\Contracts\IOPools\Promise` that settles once the job has run:

```php
$promise = app('queue')->connection('background')->push(new RecordDelivery($order));

$promise->then(function () {
    // The job has run in a pool worker...
});

// Or block until it has finished...
$promise->wait();
```

The `deferred` connection also serves as the last entry of the default [failover queue](#queue-failover).

### Pushing Without Blocking

The queue's `async` method returns a `Voyager\Queue\Async\AsyncQueue` whose `push`, `pushOn`, `later`, `laterOn`, and `pushRaw` methods do not wait for the queue backend. Each one returns a promise of the pushed job's ID:

```php
use App\Jobs\ProcessPodcast;

$queue = app('queue')->connection('redis');

$pushed = $queue->async()->push(new ProcessPodcast($podcast));

$pushed->then(function (string $id) {
    // The job is on the queue...
});
```

The `redis` connection sends the push over the event loop's own Redis socket, and the `database` connection inserts the job's row from a pool worker, so neither blocks the current process. Any other connection performs its push right away, and a connection whose push already returns a promise, such as `background` or `deferred`, hands that promise back.

The payload, including a delayed job's availability time, is built when you make the call. Pushes keep the order you made them in, even when blocking and non-blocking pushes are mixed on the same queue:

```php
$queue->async()->push(new ProcessPodcast($first));
$queue->push(new ProcessPodcast($second));
$queue->async()->later(60, new ProcessPodcast($third));
```

A job marked [after commit](#jobs-and-database-transactions) inside a transaction is held until the transaction commits. If the transaction rolls back, the promise is rejected with a `RuntimeException` and a unique job's lock is released. A `database` push made while that database connection has a transaction open is rejected with a `LogicException`, since the row could not be part of that transaction.

### Bulk Dispatching

If you need to push many independent jobs at once and do not need [batch](#job-batching) tracking or callbacks, you may use the queue's `bulk` method. Every job in the array is pushed to the given queue on that connection:

```php
use App\Jobs\ProcessUser;

app('queue')->connection('redis')->bulk(
    $users->map(fn ($user) => new ProcessUser($user))->all()
);
```

### Jobs and Database Transactions

While it is perfectly fine to dispatch jobs within database transactions, you should take special care to ensure that your job will actually be able to execute successfully. When dispatching a job within a transaction, it is possible that the job will be processed by a worker before the parent transaction has committed. When this happens, any updates you have made to models or database records during the database transaction(s) may not yet be reflected in the database. In addition, any models or database records created within the transaction(s) may not exist in the database.

Thankfully, Venusian provides several methods of working around this problem. First, you may set the `after_commit` connection option in your queue connection's configuration array:

```php
'redis' => [
    'driver' => 'redis',
    // ...
    'after_commit' => true,
],
```

When the `after_commit` option is `true`, you may dispatch jobs within database transactions; however, Venusian will wait until the open parent database transactions have been committed before actually dispatching the job. Of course, if no database transactions are currently open, the job will be dispatched immediately.

If a transaction is rolled back due to an exception that occurs during the transaction, the jobs that were dispatched during that transaction will be discarded.

> [!NOTE]
> Setting the `after_commit` configuration option to `true` will also cause any queued signal listeners and broadcast signals to be dispatched after all open database transactions have been committed.

#### Specifying Commit Dispatch Behavior Inline

If you do not set the `after_commit` queue connection configuration option to `true`, you may still indicate that a specific job should be dispatched after all open database transactions have been committed. To accomplish this, you may chain the `afterCommit` method onto your dispatch operation:

```php
use App\Jobs\ProcessPodcast;

ProcessPodcast::dispatch($podcast)->afterCommit();
```

Likewise, if the `after_commit` configuration option is set to `true`, you may indicate that a specific job should be dispatched immediately without waiting for any open database transactions to commit:

```php
ProcessPodcast::dispatch($podcast)->beforeCommit();
```

<a id="job-chaining"></a>
### Job Chaining

Job chaining allows you to specify a list of queued jobs that should be run in sequence after the primary job has executed successfully. If one job in the sequence fails, the rest of the jobs will not be run. To execute a queued job chain, you may use the `chain` method provided by the command bus, `Voyager\Bus\Dispatcher`. The command bus is a lower-level component that queued job dispatching is built on top of:

```php
use App\Jobs\OptimizePodcast;
use App\Jobs\ProcessPodcast;
use App\Jobs\ReleasePodcast;
use Voyager\Bus\Dispatcher;

app(Dispatcher::class)->chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->dispatch();
```

A job class may also start a chain itself with the static `withChain` method. The jobs passed to `withChain` run after the job built from the `dispatch` arguments:

```php
ProcessPodcast::withChain([
    new OptimizePodcast,
    new ReleasePodcast,
])->dispatch($podcast);
```

In addition to chaining job class instances, you may also chain closures:

```php
app(Dispatcher::class)->chain([
    new ProcessPodcast,
    new OptimizePodcast,
    function () {
        // ...
    },
])->dispatch();
```

> [!WARNING]
> Deleting jobs using the `$this->delete()` method within the job will not prevent chained jobs from being processed. The chain will only stop executing if a job in the chain fails.

#### Chain Connection and Queue

If you would like to specify the connection and queue that should be used for the chained jobs, you may use the `onConnection` and `onQueue` methods. These methods specify the queue connection and queue name that should be used unless the queued job is explicitly assigned a different connection / queue:

```php
app(Dispatcher::class)->chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->onConnection('redis')->onQueue('podcasts')->dispatch();
```

<a id="adding-jobs-to-the-chain"></a>
#### Adding Jobs to the Chain

Occasionally, you may need to prepend or append a job to an existing job chain from within another job in that chain. You may accomplish this using the `prependToChain` and `appendToChain` methods:

```php
/**
 * Execute the job.
 */
public function handle(): mixed
{
    // ...

    // Prepend to the current chain, run job immediately after current job...
    $this->prependToChain(new TranscribePodcast);

    // Append to the current chain, run job at end of chain...
    $this->appendToChain(new TranscribePodcast);

    return null;
}
```

#### Chain Failures

When chaining jobs, you may use the `catch` method to specify a closure that should be invoked if a job within the chain fails. The given callback will receive the `Throwable` instance that caused the job failure:

```php
use Throwable;
use Voyager\Bus\Dispatcher;

app(Dispatcher::class)->chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->catch(function (Throwable $e) {
    // A job within the chain has failed...
})->dispatch();
```

> [!WARNING]
> Since chain callbacks are serialized and executed at a later time by the Venusian queue, you should not use the `$this` variable within chain callbacks.

### Customizing the Queue and Connection

#### Dispatching to a Particular Queue

By pushing jobs to different queues, you may "categorize" your queued jobs and even prioritize how many workers you assign to various queues. Keep in mind, this does not push jobs to different queue "connections" as defined by your queue configuration file, but only to specific queues within a single connection. To specify the queue, use the `onQueue` method when dispatching the job:

```php
ProcessPodcast::dispatch($podcast)->onQueue('processing');
```

Alternatively, you may specify the job's queue by calling the `onQueue` method within the job's constructor:

```php
<?php

namespace App\Jobs;

use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct()
    {
        $this->onQueue('processing');
    }
}
```

#### Dispatching to a Particular Connection

If your application interacts with multiple queue connections, you may specify which connection to push a job to using the `onConnection` method:

```php
ProcessPodcast::dispatch($podcast)->onConnection('redis');
```

You may chain the `onConnection` and `onQueue` methods together to specify the connection and the queue for a job:

```php
ProcessPodcast::dispatch($podcast)
    ->onConnection('redis')
    ->onQueue('processing');
```

Alternatively, you may specify the job's connection by calling the `onConnection` method within the job's constructor:

```php
<?php

namespace App\Jobs;

use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct()
    {
        $this->onConnection('redis');
    }
}
```

### Max Job Attempts and Timeout

#### Max Attempts

Job attempts are a core concept of Venusian's queue system and power many advanced features. While they may seem confusing at first, it's important to understand how they work before modifying the default configuration.

When a job is dispatched, it is pushed onto the queue. A worker then picks it up and attempts to execute it. This is a job attempt.

However, an attempt does not necessarily mean the job's `handle` method was executed. Attempts can also be "consumed" in several ways:

- The job encounters an unhandled exception during execution.
- The job is manually released back to the queue using `$this->release()`.
- Middleware such as `WithoutOverlapping` or `RateLimited` fails to acquire a lock and releases the job.
- The job timed out.
- The job's `handle` method runs and completes without throwing an exception.

You likely do not want to keep attempting a job indefinitely. Therefore, Venusian provides various ways to specify how many times or for how long a job may be attempted.

> [!NOTE]
> By default, Venusian will only attempt a job once. If your job uses middleware like `WithoutOverlapping` or `RateLimited`, or if you're manually releasing jobs, you will likely need to increase the number of allowed attempts via the `tries` option.

One approach to specifying the maximum number of times a job may be attempted is via the `--tries` switch on the Computer command line. This will apply to all jobs processed by the worker unless the job being processed specifies the number of times it may be attempted:

```shell
php computer queue:work --tries=3
```

If a job exceeds its maximum number of attempts, it will be considered a "failed" job. For more information on handling failed jobs, consult the [failed job documentation](#dealing-with-failed-jobs). If `--tries=0` is provided to the `queue:work` command, the job will be retried indefinitely.

You may take a more granular approach by defining the maximum number of times a job may be attempted on the job class itself using a `tries` property. If the maximum number of attempts is specified on the job, it will take precedence over the `--tries` value provided on the command line:

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * The number of times the job may be attempted.
     *
     * @var int
     */
    public $tries = 5;

    // ...
}
```

If you need dynamic control over a particular job's maximum attempts, you may define a `tries` method on the job:

```php
/**
 * Determine number of times the job may be attempted.
 */
public function tries(): int
{
    return 5;
}
```

<a id="time-based-attempts"></a>
#### Time Based Attempts

As an alternative to defining how many times a job may be attempted before it fails, you may define a time at which the job should no longer be attempted. This allows a job to be attempted any number of times within a given time frame. To define the time at which a job should no longer be attempted, add a `retryUntil` method to your job class. This method should return a `DateTimeInterface` instance:

```php
use DateTimeInterface;

/**
 * Determine the time at which the job should timeout.
 */
public function retryUntil(): DateTimeInterface
{
    return now()->addMinutes(10);
}
```

If both `retryUntil` and `tries` are defined, Venusian gives precedence to the `retryUntil` method.

> [!NOTE]
> You may also define a `tries` property or `retryUntil` method on your [queued signal listeners](/docs/{{version}}/framework/digging-deeper/signals#queued-signal-listeners).

#### Max Exceptions

Sometimes you may wish to specify that a job may be attempted many times, but should fail if the retries are triggered by a given number of unhandled exceptions (as opposed to being released by the `release` method directly). To accomplish this, you may define the `tries` and `maxExceptions` properties on your job class:

```php
<?php

namespace App\Jobs;

use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * The number of times the job may be attempted.
     *
     * @var int
     */
    public $tries = 25;

    /**
     * The maximum number of unhandled exceptions to allow before failing.
     *
     * @var int
     */
    public $maxExceptions = 3;

    /**
     * Execute the job.
     */
    public function handle(): mixed
    {
        return app('redis')->throttle('key')->allow(10)->every(60)->then(function () {
            // Lock obtained, process the podcast...
        }, function () {
            // Unable to obtain lock...
            return $this->release(10);
        });
    }
}
```

In this example, the job is released for ten seconds if the application is unable to obtain a Redis lock and will continue to be retried up to 25 times. However, the job will fail if three unhandled exceptions are thrown by the job.

#### Timeout

Often, you know roughly how long you expect your queued jobs to take. For this reason, Venusian allows you to specify a "timeout" value. By default, the timeout value is 60 seconds. If a job is processing for longer than the number of seconds specified by the timeout value, the worker processing the job will exit with an error. Typically, the worker will be restarted automatically by a [process manager configured on your server](#supervisor-configuration).

The maximum number of seconds that jobs can run may be specified using the `--timeout` switch on the Computer command line:

```shell
php computer queue:work --timeout=30
```

If the job exceeds its maximum attempts by continually timing out, it will be marked as failed.

You may also define the maximum number of seconds a job should be allowed to run using the `timeout` property on the job class. If the timeout is specified on the job, it will take precedence over any timeout specified on the command line:

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * The number of seconds the job can run before timing out.
     *
     * @var int
     */
    public $timeout = 120;

    // ...
}
```

Sometimes, IO blocking processes such as sockets or outgoing HTTP connections may not respect your specified timeout. Therefore, when using these features, you should always attempt to specify a timeout using their APIs as well. For example, when using the [HTTP client](/docs/{{version}}/framework/digging-deeper/http-client), you should always specify a connection and request timeout value.

> [!WARNING]
> The [PCNTL](https://www.php.net/manual/en/book.pcntl.php) PHP extension must be installed in order to specify job timeouts. In addition, a job's "timeout" value should always be less than its ["retry after"](#job-expiration) value. Otherwise, the job may be re-attempted before it has actually finished executing or timed out. The `--timeout` option has no effect when the `queue:work` command is invoked with the `--once` option.

#### Failing on Timeout

If you would like to indicate that a job should be marked as [failed](#dealing-with-failed-jobs) on timeout, you may define the `failOnTimeout` property on the job class:

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * Indicate if the job should be marked as failed on timeout.
     *
     * @var bool
     */
    public $failOnTimeout = true;

    // ...
}
```

> [!NOTE]
> By default, when a job times out, it consumes one attempt and is released back to the queue (if retries are allowed). However, if you configure the job to fail on timeout, it will not be retried, regardless of the value set for tries.

<a id="queue-failover"></a>
### Queue Failover

The `failover` queue driver provides automatic failover functionality when pushing jobs to the queue. If the primary queue connection of the `failover` configuration fails for any reason, Venusian will automatically attempt to push the job to the next configured connection in the list. This is particularly useful for ensuring high availability in production environments where queue reliability is critical.

To configure a failover queue connection, specify the `failover` driver and provide an array of connection names to attempt in order. By default, Venusian includes an example failover configuration in your application's `config/queue.php` configuration file:

```php
'failover' => [
    'driver' => 'failover',
    'connections' => [
        'redis',
        'deferred',
    ],
],
```

Once you have configured a connection that uses the `failover` driver, you will need to set the failover connection as your default queue connection in your application's `.env` file to make use of the failover functionality:

```ini
QUEUE_CONNECTION=failover
```

Next, start at least one worker for each connection in your failover connection list that stores its jobs:

```shell
php computer queue:work redis
```

> [!NOTE]
> You do not need to run a worker for connections using the `sync`, `background`, or `deferred` queue drivers since those drivers process jobs within the current PHP process.

When a queue connection operation fails and failover is activated, Venusian will dispatch the `Voyager\Queue\Signals\QueueFailedOver` signal, allowing you to report or log that a queue connection has failed.

### Error Handling

If an exception is thrown while the job is being processed, the job will automatically be released back onto the queue so it may be attempted again. The job will continue to be released until it has been attempted the maximum number of times allowed by your application. The maximum number of attempts is defined by the `--tries` switch used on the `queue:work` Computer command. Alternatively, the maximum number of attempts may be defined on the job class itself. More information on running the queue worker [can be found below](#running-the-queue-worker).

<a id="manually-releasing-a-job"></a>
#### Manually Releasing a Job

Sometimes you may wish to manually release a job back onto the queue so that it can be attempted again at a later time. You may accomplish this by calling the `release` method:

```php
/**
 * Execute the job.
 */
public function handle(): mixed
{
    // ...

    $this->release();

    return null;
}
```

By default, the `release` method will release the job back onto the queue for immediate processing. However, you may instruct the queue to not make the job available for processing until a given number of seconds has elapsed by passing an integer or date instance to the `release` method:

```php
$this->release(10);

$this->release(now()->addSeconds(10));
```

#### Manually Failing a Job

Occasionally you may need to manually mark a job as "failed". To do so, you may call the `fail` method:

```php
/**
 * Execute the job.
 */
public function handle(): mixed
{
    // ...

    $this->fail();

    return null;
}
```

If you would like to mark your job as failed because of an exception that you have caught, you may pass the exception to the `fail` method. Or, for convenience, you may pass a string error message which will be converted to an exception for you:

```php
$this->fail($exception);

$this->fail('Something went wrong.');
```

> [!NOTE]
> For more information on failed jobs, check out the [documentation on dealing with job failures](#dealing-with-failed-jobs).

#### Failing Jobs on Specific Exceptions

The `FailOnException` [job middleware](#job-middleware) allows you to short-circuit retries when specific exceptions are thrown. This allows retrying on transient exceptions such as external API errors, but failing the job permanently on persistent exceptions, such as an account being closed:

```php
<?php

namespace App\Jobs;

use App\Exceptions\AccountClosedException;
use App\Models\User;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;
use Voyager\Queue\Middleware\FailOnException;

class SyncChatHistory implements ShouldQueue
{
    use Queueable;

    /**
     * The number of times the job may be attempted.
     *
     * @var int
     */
    public $tries = 3;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public User $user,
    ) {}

    /**
     * Execute the job.
     */
    public function handle(): mixed
    {
        $this->user->ensureAccountIsOpen();

        $response = app('http')->throw()->get(
            "https://chat.example.com/?user={$this->user->uuid}"
        );

        // ...

        return null;
    }

    /**
     * Get the middleware the job should pass through.
     */
    public function middleware(): array
    {
        return [
            new FailOnException([AccountClosedException::class])
        ];
    }
}
```

<a id="job-batching"></a>
## Job Batching

Venusian's job batching feature allows you to easily execute a group of jobs in parallel and then perform some action when the batch of jobs has completed executing.

Batches are kept in a database table, which holds meta information about your job batches such as their completion percentage. The table lives on the connection named by `queue.batching.database` and is named by `queue.batching.table` (`job_batches` by default). Its migration may be generated using the `make:queue-batches-table` Computer command:

```shell
php computer make:queue-batches-table

php computer migrate
```

### Defining Batchable Jobs

To define a batchable job, you should [create a queueable job](#creating-jobs) as normal; however, you should add the `Voyager\Bus\Batchable` trait to the job class. This trait provides access to a `batch` method which may be used to retrieve the current batch that the job is executing within:

```php
<?php

namespace App\Jobs;

use Voyager\Bus\Batchable;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ImportCsv implements ShouldQueue
{
    use Batchable, Queueable;

    /**
     * Execute the job.
     */
    public function handle(): mixed
    {
        if ($this->batch()->cancelled()) {
            // Determine if the batch has been cancelled...

            return null;
        }

        // Import a portion of the CSV file...

        return null;
    }
}
```

### Dispatching Batches

To dispatch a batch of jobs, you should use the `batch` method of the command bus, `Voyager\Bus\Dispatcher`. Of course, batching is primarily useful when combined with completion callbacks. So, you may use the `then`, `catch`, and `finally` methods to define completion callbacks for the batch. Each of these callbacks will receive a `Voyager\Bus\Batch` instance when they are invoked.

When running multiple queue workers, the jobs in the batch will be processed in parallel. Therefore, the order in which the jobs complete may not be the same as the order in which they were added to the batch. Consult our documentation on [job chains and batches](#chains-and-batches) for information on how to run a series of jobs in sequence.

In this example, we will imagine we are queueing a batch of jobs that each process a given number of rows from a CSV file:

```php
use App\Jobs\ImportCsv;
use Throwable;
use Voyager\Bus\Batch;
use Voyager\Bus\Dispatcher;

$batch = app(Dispatcher::class)->batch([
    new ImportCsv(1, 100),
    new ImportCsv(101, 200),
    new ImportCsv(201, 300),
    new ImportCsv(301, 400),
    new ImportCsv(401, 500),
])->before(function (Batch $batch) {
    // The batch has been created but no jobs have been added...
})->progress(function (Batch $batch) {
    // A single job has completed successfully...
})->then(function (Batch $batch) {
    // All jobs completed successfully...
})->catch(function (Batch $batch, Throwable $e) {
    // Batch job failure detected...
})->finally(function (Batch $batch) {
    // The batch has finished executing...
})->dispatch();

return $batch->id;
```

The batch's ID, which may be accessed via the `$batch->id` property, may be used to [query the command bus](#inspecting-batches) for information about the batch after it has been dispatched.

> [!WARNING]
> Since batch callbacks are serialized and executed at a later time by the Venusian queue, you should not use the `$this` variable within the callbacks. In addition, since batched jobs are wrapped within database transactions, database statements that trigger implicit commits should not be executed within the jobs.

#### Naming Batches

Naming a batch makes its record easier to recognize when you inspect the `job_batches` table or a batch's JSON. To assign an arbitrary name to a batch, you may call the `name` method while defining the batch:

```php
$batch = app(Dispatcher::class)->batch([
    // ...
])->then(function (Batch $batch) {
    // All jobs completed successfully...
})->name('Import CSV')->dispatch();
```

#### Batch Connection and Queue

If you would like to specify the connection and queue that should be used for the batched jobs, you may use the `onConnection` and `onQueue` methods. All batched jobs must execute within the same connection and queue:

```php
$batch = app(Dispatcher::class)->batch([
    // ...
])->then(function (Batch $batch) {
    // All jobs completed successfully...
})->onConnection('redis')->onQueue('imports')->dispatch();
```

<a id="chains-and-batches"></a>
### Chains and Batches

You may define a set of [chained jobs](#job-chaining) within a batch by placing the chained jobs within an array. For example, we may execute two job chains in parallel and execute a callback when both job chains have finished processing:

```php
use App\Jobs\ReleasePodcast;
use App\Jobs\SendPodcastReleaseNotification;
use Voyager\Bus\Batch;
use Voyager\Bus\Dispatcher;

app(Dispatcher::class)->batch([
    [
        new ReleasePodcast(1),
        new SendPodcastReleaseNotification(1),
    ],
    [
        new ReleasePodcast(2),
        new SendPodcastReleaseNotification(2),
    ],
])->then(function (Batch $batch) {
    // All jobs completed successfully...
})->dispatch();
```

Conversely, you may run batches of jobs within a [chain](#job-chaining) by defining batches within the chain. For example, you could first run a batch of jobs to release multiple podcasts then a batch of jobs to send the release notifications:

```php
use App\Jobs\FlushPodcastCache;
use App\Jobs\ReleasePodcast;
use App\Jobs\SendPodcastReleaseNotification;
use Voyager\Bus\Dispatcher;

$bus = app(Dispatcher::class);

$bus->chain([
    new FlushPodcastCache,
    $bus->batch([
        new ReleasePodcast(1),
        new ReleasePodcast(2),
    ]),
    $bus->batch([
        new SendPodcastReleaseNotification(1),
        new SendPodcastReleaseNotification(2),
    ]),
])->dispatch();
```

### Adding Jobs to Batches

Sometimes it may be useful to add additional jobs to a batch from within a batched job. This pattern can be useful when you need to batch thousands of jobs which may take too long to dispatch up front. So, instead, you may wish to dispatch an initial batch of "loader" jobs that hydrate the batch with even more jobs:

```php
$batch = app(Dispatcher::class)->batch([
    new LoadImportBatch,
    new LoadImportBatch,
    new LoadImportBatch,
])->then(function (Batch $batch) {
    // All jobs completed successfully...
})->name('Import Contacts')->dispatch();
```

In this example, we will use the `LoadImportBatch` job to hydrate the batch with additional jobs. To accomplish this, we may use the `add` method on the batch instance that may be accessed via the job's `batch` method:

```php
use App\Jobs\ImportContacts;
use Voyager\NutsAndBolts\Collection;

/**
 * Execute the job.
 */
public function handle(): mixed
{
    if ($this->batch()->cancelled()) {
        return null;
    }

    $this->batch()->add(Collection::times(1000, function () {
        return new ImportContacts;
    }));

    return null;
}
```

> [!WARNING]
> You may only add jobs to a batch from within a job that belongs to the same batch.

<a id="inspecting-batches"></a>
### Inspecting Batches

The `Voyager\Bus\Batch` instance that is provided to batch completion callbacks has a variety of properties and methods to assist you in interacting with and inspecting a given batch of jobs:

```php
// The UUID of the batch...
$batch->id;

// The name of the batch (if applicable)...
$batch->name;

// The number of jobs assigned to the batch...
$batch->totalJobs;

// The number of jobs that have not been processed by the queue...
$batch->pendingJobs;

// The number of jobs that have failed...
$batch->failedJobs;

// The number of jobs that have been processed thus far...
$batch->processedJobs();

// The completion percentage of the batch (0-100)...
$batch->progress();

// Indicates if the batch has finished executing...
$batch->finished();

// Cancel the execution of the batch...
$batch->cancel();

// Indicates if the batch has been cancelled...
$batch->cancelled();

// Re-read the batch from storage...
$batch->fresh();
```

#### Finding Batches by ID

To retrieve a batch by its ID, you may use the command bus's `findBatch` method. All `Voyager\Bus\Batch` instances are JSON serializable, so you may hand the batch straight to anything that encodes JSON, for example to report its completion progress to another process:

```php
use Voyager\Bus\Dispatcher;

$batch = app(Dispatcher::class)->findBatch($batchId);

echo json_encode($batch);
```

### Cancelling Batches

Sometimes you may need to cancel a given batch's execution. This can be accomplished by calling the `cancel` method on the `Voyager\Bus\Batch` instance:

```php
/**
 * Execute the job.
 */
public function handle(): mixed
{
    if ($this->user->exceedsImportLimit()) {
        $this->batch()->cancel();

        return null;
    }

    if ($this->batch()->cancelled()) {
        return null;
    }

    return null;
}
```

As you may have noticed in the previous examples, batched jobs should typically determine if their corresponding batch has been cancelled before continuing execution. However, for convenience, you may assign the `SkipIfBatchCancelled` [middleware](#job-middleware) to the job instead. As its name indicates, this middleware will instruct Venusian to not process the job if its corresponding batch has been cancelled:

```php
use Voyager\Queue\Middleware\SkipIfBatchCancelled;

/**
 * Get the middleware the job should pass through.
 */
public function middleware(): array
{
    return [new SkipIfBatchCancelled];
}
```

### Batch Failures

When a batched job fails, the `catch` callback (if assigned) will be invoked. This callback is only invoked for the first job that fails within the batch.

#### Allowing Failures

When a job within a batch fails, Venusian will automatically mark the batch as "cancelled". If you wish, you may disable this behavior so that a job failure does not automatically mark the batch as cancelled. This may be accomplished by calling the `allowFailures` method while dispatching the batch:

```php
$batch = app(Dispatcher::class)->batch([
    // ...
])->then(function (Batch $batch) {
    // All jobs completed successfully...
})->allowFailures()->dispatch();
```

You may optionally provide a closure to the `allowFailures` method, which will be executed on each job failure:

```php
$batch = app(Dispatcher::class)->batch([
    // ...
])->allowFailures(function (Batch $batch, $exception) {
    // Handle individual job failures...
})->dispatch();
```

#### Retrying Failed Batch Jobs

For convenience, Venusian provides a `queue:retry-batch` Computer command that allows you to easily retry all of the failed jobs for a given batch. This command accepts the UUID of the batch whose failed jobs should be retried:

```shell
php computer queue:retry-batch 32dbc76c-4f82-4749-b610-a639fe0099b5
```

### Pruning Batches

Without pruning, the `job_batches` table can accumulate records very quickly. To mitigate this, you should run the `queue:prune-batches` Computer command daily, from your system's scheduler such as `cron`:

```shell
php computer queue:prune-batches
```

By default, all finished batches that are more than 24 hours old will be pruned. You may use the `hours` option when calling the command to determine how long to retain batch data. For example, the following command will delete all batches that finished over 48 hours ago:

```shell
php computer queue:prune-batches --hours=48
```

Sometimes, your `job_batches` table may accumulate batch records for batches that never completed successfully, such as batches where a job failed and that job was never retried successfully. You may instruct the `queue:prune-batches` command to prune these unfinished batch records using the `unfinished` option:

```shell
php computer queue:prune-batches --hours=48 --unfinished=72
```

Likewise, your `job_batches` table may also accumulate batch records for cancelled batches. You may instruct the `queue:prune-batches` command to prune these cancelled batch records using the `cancelled` option:

```shell
php computer queue:prune-batches --hours=48 --cancelled=72
```

## Queueing Closures

Instead of dispatching a job class to the queue, you may also dispatch a closure. This is great for quick, simple tasks that need to be executed outside of the current code path. When dispatching closures to the queue, the closure's code content is cryptographically signed so that it cannot be modified in transit:

```php
use App\Models\Podcast;

$podcast = Podcast::find(1);

dispatch(function () use ($podcast) {
    $podcast->publish();
});
```

To assign a name to the queued closure, which will be displayed by the `queue:work` command, you may use the `name` method:

```php
dispatch(function () {
    // ...
})->name('Publish Podcast');
```

Using the `catch` method, you may provide a closure that should be executed if the queued closure fails to complete successfully after exhausting all of your queue's [configured retry attempts](#max-job-attempts-and-timeout):

```php
use Throwable;

dispatch(function () use ($podcast) {
    $podcast->publish();
})->catch(function (Throwable $e) {
    // This job has failed...
});
```

> [!WARNING]
> Since `catch` callbacks are serialized and executed at a later time by the Venusian queue, you should not use the `$this` variable within `catch` callbacks.

<a id="running-the-queue-worker"></a>
## Running the Queue Worker

### The `queue:work` Command

Venusian includes a Computer command that will start a queue worker and process new jobs as they are pushed onto the queue. You may run the worker using the `queue:work` Computer command. Note that once the `queue:work` command has started, it will continue to run until it is manually stopped or you close your terminal:

```shell
php computer queue:work
```

> [!NOTE]
> To keep the `queue:work` process running permanently in the background, you should use a process monitor such as [Supervisor](#supervisor-configuration) to ensure that the queue worker does not stop running.

You may include the `-v` flag when invoking the `queue:work` command if you would like the processed job IDs, connection names, and queue names to be included in the command's output:

```shell
php computer queue:work -v
```

Remember, queue workers are long-lived processes and store the booted application state in memory. As a result, they will not notice changes in your code base after they have been started. So, during your deployment process, be sure to [restart your queue workers](#queue-workers-and-deployment). Between jobs, the worker flushes the log context and forgets scoped container instances, but any other static state created or modified by your application will not be automatically reset between jobs.

Alternatively, you may run the `queue:listen` command. When using the `queue:listen` command, you don't have to manually restart the worker when you want to reload your updated code or reset the application state; however, this command is significantly less efficient than the `queue:work` command:

```shell
php computer queue:listen
```

#### Running Multiple Queue Workers

To assign multiple workers to a queue and process jobs concurrently, you should simply start multiple `queue:work` processes. This can either be done locally via multiple tabs in your terminal or in production using your process manager's configuration settings. [When using Supervisor](#supervisor-configuration), you may use the `numprocs` configuration value.

#### Specifying the Connection and Queue

You may also specify which queue connection the worker should utilize. The connection name passed to the `work` command should correspond to one of the connections defined in your `config/queue.php` configuration file:

```shell
php computer queue:work redis
```

By default, the `queue:work` command only processes jobs for the default queue on a given connection. However, you may customize your queue worker even further by only processing particular queues for a given connection. For example, if all of your emails are processed in an `emails` queue on your `redis` queue connection, you may issue the following command to start a worker that only processes that queue:

```shell
php computer queue:work redis --queue=emails
```

#### Processing a Specified Number of Jobs

The `--once` option may be used to instruct the worker to only process a single job from the queue:

```shell
php computer queue:work --once
```

The `--max-jobs` option may be used to instruct the worker to process the given number of jobs and then exit. This option may be useful when combined with [Supervisor](#supervisor-configuration) so that your workers are automatically restarted after processing a given number of jobs, releasing any memory they may have accumulated:

```shell
php computer queue:work --max-jobs=1000
```

#### Processing All Queued Jobs and Then Exiting

The `--stop-when-empty` option may be used to instruct the worker to process all jobs and then exit gracefully. This option can be useful when processing Venusian queues within a Docker container if you wish to shutdown the container after the queue is empty:

```shell
php computer queue:work --stop-when-empty
```

#### Processing Jobs for a Given Number of Seconds

The `--max-time` option may be used to instruct the worker to process jobs for the given number of seconds and then exit. This option may be useful when combined with [Supervisor](#supervisor-configuration) so that your workers are automatically restarted after processing jobs for a given amount of time, releasing any memory they may have accumulated:

```shell
# Process jobs for one hour and then exit...
php computer queue:work --max-time=3600
```

#### Worker Sleep Duration

When jobs are available on the queue, the worker will keep processing jobs with no delay in between jobs. However, the `sleep` option determines how many seconds the worker will "sleep" if there are no jobs available. Of course, while sleeping, the worker will not process any new jobs:

```shell
php computer queue:work --sleep=3
```

The `--rest` option sets a number of seconds the worker waits between jobs even when more are available:

```shell
php computer queue:work --rest=1
```

#### Resource Considerations

The `--memory` option specifies the memory limit in megabytes at which the worker should exit. By default, this limit is 128 megabytes:

```shell
php computer queue:work --memory=256
```

A process monitor such as [Supervisor](#supervisor-configuration) can automatically restart the worker after it exits.

Daemon queue workers do not "reboot" the framework before processing each job. Therefore, you should release any heavy resources after each job completes. For example, if you are doing image manipulation with the [GD library](https://www.php.net/manual/en/book.image.php), you should free the memory with `imagedestroy` when you are done processing the image.

### Queue Priorities

Sometimes you may wish to prioritize how your queues are processed. For example, in your `config/queue.php` configuration file, you may set the default `queue` for your `redis` connection to `low`. However, occasionally you may wish to push a job to a `high` priority queue like so:

```php
dispatch((new Job)->onQueue('high'));
```

To start a worker that verifies that all of the `high` queue jobs are processed before continuing to any jobs on the `low` queue, pass a comma-delimited list of queue names to the `work` command:

```shell
php computer queue:work --queue=high,low
```

<a id="queue-workers-and-deployment"></a>
### Queue Workers and Deployment

Since queue workers are long-lived processes, they will not notice changes to your code without being restarted. So, the simplest way to deploy an application using queue workers is to restart the workers during your deployment process. You may gracefully restart all of the workers by issuing the `queue:restart` command:

```shell
php computer queue:restart
```

This command will instruct all queue workers to gracefully exit after they finish processing their current job so that no existing jobs are lost. Since the queue workers will exit when the `queue:restart` command is executed, you should be running a process manager such as [Supervisor](#supervisor-configuration) to automatically restart the queue workers.

> [!NOTE]
> The queue uses the default [cache](/docs/{{version}}/framework/digging-deeper/cache) store to store restart signals, so you should verify that a cache driver is properly configured for your application before using this feature.

### Job Expirations and Timeouts

<a id="job-expiration"></a>
#### Job Expiration

In your `config/queue.php` configuration file, the `database` and `redis` queue connections define a `retry_after` option. This option specifies how many seconds the queue connection should wait before retrying a job that is being processed. For example, if the value of `retry_after` is set to `90`, the job will be released back onto the queue if it has been processing for 90 seconds without being released or deleted. Typically, you should set the `retry_after` value to the maximum number of seconds your jobs should reasonably take to complete processing.

#### Worker Timeouts

The `queue:work` Computer command exposes a `--timeout` option. By default, the `--timeout` value is 60 seconds. If a job is processing for longer than the number of seconds specified by the timeout value, the worker processing the job will exit with an error. Typically, the worker will be restarted automatically by a [process manager configured on your server](#supervisor-configuration):

```shell
php computer queue:work --timeout=60
```

The `retry_after` configuration option and the `--timeout` CLI option are different, but work together to ensure that jobs are not lost and that jobs are only successfully processed once.

> [!WARNING]
> The `--timeout` value should always be at least several seconds shorter than your `retry_after` configuration value. This will ensure that a worker processing a frozen job is always terminated before the job is retried. If your `--timeout` option is longer than your `retry_after` configuration value, your jobs may be processed twice.

### Pausing and Resuming Queue Workers

Sometimes you may need to temporarily prevent a queue worker from processing new jobs without stopping the worker entirely. For example, you may want to pause job processing during system maintenance. Venusian provides the `queue:pause` and `queue:resume` Computer commands to pause and resume queue workers.

To pause a specific queue, provide the queue connection name and the queue name:

```shell
php computer queue:pause database:default
```

In this example, `database` is the queue connection name and `default` is the queue name. Once a queue is paused, any workers processing jobs from that queue will continue to finish their current job, but will not pick up any new jobs until the queue is resumed.

To resume processing jobs on a paused queue, use the `queue:resume` command:

```shell
php computer queue:resume database:default
```

After resuming a queue, workers will begin processing new jobs from that queue immediately. Note that pausing a queue does not stop the worker process itself - it only prevents the worker from processing new jobs from the specified queue.

The queue manager offers the same controls in code through its `pause`, `pauseFor`, `resume`, and `isPaused` methods:

```php
$queues = app('queue');

$queues->pause('database', 'default');

$queues->pauseFor('database', 'default', 300);

$queues->isPaused('database', 'default');

$queues->resume('database', 'default');
```

#### Worker Restart and Pause Signals

By default, queue workers poll the cache driver for restart and pause signals on each job iteration. While this polling is essential for responding to `queue:restart` and `queue:pause` commands, it does introduce a small performance overhead.

If you need to optimize performance and don't require these interruption features, you may disable this polling by calling the `withoutInterruptionPolling` method on the queue manager. This should typically be done in the `boot` method of your `AppServiceProvider`:

```php
/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('queue')->withoutInterruptionPolling();
}
```

> [!WARNING]
> When interruption polling is disabled, workers will not respond to `queue:restart` or `queue:pause` commands.

<a id="supervisor-configuration"></a>
## Supervisor Configuration

In production, you need a way to keep your `queue:work` processes running. A `queue:work` process may stop running for a variety of reasons, such as an exceeded worker timeout or the execution of the `queue:restart` command.

For this reason, you need to configure a process monitor that can detect when your `queue:work` processes exit and automatically restart them. In addition, process monitors can allow you to specify how many `queue:work` processes you would like to run concurrently. Supervisor is a process monitor commonly used in Linux environments and we will discuss how to configure it in the following documentation.

#### Installing Supervisor

Supervisor is a process monitor for the Linux operating system, and will automatically restart your `queue:work` processes if they fail. To install Supervisor on Ubuntu, you may use the following command:

```shell
sudo apt-get install supervisor
```

#### Configuring Supervisor

Supervisor configuration files are typically stored in the `/etc/supervisor/conf.d` directory. Within this directory, you may create any number of configuration files that instruct supervisor how your processes should be monitored. For example, let's create a `venusian-worker.conf` file that starts and monitors `queue:work` processes:

```ini
[program:venusian-worker]
process_name=%(program_name)s_%(process_num)02d
command=php /srv/app/computer queue:work --sleep=3 --tries=3 --max-time=3600
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
user=app
numprocs=8
redirect_stderr=true
stdout_logfile=/srv/app/worker.log
stopwaitsecs=3600
```

In this example, the `numprocs` directive will instruct Supervisor to run eight `queue:work` processes and monitor all of them, automatically restarting them if they fail. You should change the `command` directive of the configuration to reflect your desired queue connection and worker options.

> [!WARNING]
> You should ensure that the value of `stopwaitsecs` is greater than the number of seconds consumed by your longest running job. Otherwise, Supervisor may kill the job before it is finished processing.

#### Starting Supervisor

Once the configuration file has been created, you may update the Supervisor configuration and start the processes using the following commands:

```shell
sudo supervisorctl reread

sudo supervisorctl update

sudo supervisorctl start "venusian-worker:*"
```

For more information on Supervisor, consult the [Supervisor documentation](http://supervisord.org/index.html).

<a id="dealing-with-failed-jobs"></a>
## Dealing With Failed Jobs

Sometimes your queued jobs will fail. Don't worry, things don't always go as planned! Venusian includes a convenient way to [specify the maximum number of times a job should be attempted](#max-job-attempts-and-timeout). After an asynchronous job has exceeded this number of attempts, it is recorded as a failed job. [Synchronously dispatched jobs](#synchronous-dispatching) that fail are not recorded and their exceptions are immediately handled by the application.

Where failed jobs are recorded is set by the `queue.failed.driver` configuration option:

| Driver | Storage |
|---|---|
| `file` | A JSON file, `storage/framework/cache/failed-jobs.json` by default. This is the default driver. |
| `database-uuids` | The `failed_jobs` table on the `queue.failed.database` connection. |
| `null` | Nothing is stored. |

To use the `database-uuids` driver, set `QUEUE_FAILED_DRIVER=database-uuids` and create the `failed_jobs` table. You may use the `make:queue-failed-table` command to create its migration:

```shell
php computer make:queue-failed-table

php computer migrate
```

When running a [queue worker](#running-the-queue-worker) process, you may specify the maximum number of times a job should be attempted using the `--tries` switch on the `queue:work` command. If you do not specify a value for the `--tries` option, jobs will only be attempted once or as many times as specified by the job class' `tries` property:

```shell
php computer queue:work redis --tries=3
```

Using the `--backoff` option, you may specify how many seconds Venusian should wait before retrying a job that has encountered an exception. By default, a job is immediately released back onto the queue so that it may be attempted again:

```shell
php computer queue:work redis --tries=3 --backoff=3
```

If you would like to configure how many seconds Venusian should wait before retrying a job that has encountered an exception on a per-job basis, you may define a `backoff` property on your job class:

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * The number of seconds to wait before retrying the job.
     *
     * @var int
     */
    public $backoff = 3;

    // ...
}
```

If you require more complex logic for determining the job's backoff time, you may define a `backoff` method on your job class:

```php
/**
 * Calculate the number of seconds to wait before retrying the job.
 */
public function backoff(): int
{
    return 3;
}
```

You may easily configure "exponential" backoffs by defining an array of backoff values. In this example, the retry delay will be 1 second for the first retry, 5 seconds for the second retry, 10 seconds for the third retry, and 10 seconds for every subsequent retry if there are more attempts remaining:

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * The number of seconds to wait before each retry of the job.
     *
     * @var list<int>
     */
    public $backoff = [1, 5, 10];

    // ...
}
```

### Cleaning Up After Failed Jobs

When a particular job fails, you may want to send an alert to your users or revert any actions that were partially completed by the job. To accomplish this, you may define a `failed` method on your job class. The `Throwable` instance that caused the job to fail will be passed to the `failed` method:

```php
<?php

namespace App\Jobs;

use App\Models\Podcast;
use App\Services\AudioProcessor;
use Throwable;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Core\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public Podcast $podcast,
    ) {}

    /**
     * Execute the job.
     */
    public function handle(?AudioProcessor $processor = null): mixed
    {
        // Process uploaded podcast...

        return null;
    }

    /**
     * Handle a job failure.
     */
    public function failed(?Throwable $exception): void
    {
        // Send user notification of failure, etc...
    }
}
```

> [!WARNING]
> A new instance of the job is instantiated before invoking the `failed` method; therefore, any class property modifications that may have occurred within the `handle` method will be lost.

A failed job is not necessarily one that encountered an unhandled exception. A job may also be considered failed when it has exhausted all of its allowed attempts. These attempts can be consumed in several ways:

- The job timed out.
- The job encounters an unhandled exception during execution.
- The job is released back to the queue either manually or by a middleware.

If the final attempt fails due to an exception thrown during job execution, that exception will be passed to the job's `failed` method. However, if the job fails because it has reached the maximum number of allowed attempts, the `$exception` will be an instance of `Voyager\Queue\MaxAttemptsExceededException`. Similarly, if the job fails due to exceeding the configured timeout, the `$exception` will be an instance of `Voyager\Queue\TimeoutExceededException`.

### Retrying Failed Jobs

To view all of the failed jobs that have been recorded, you may use the `queue:failed` Computer command:

```shell
php computer queue:failed
```

The `queue:failed` command will list the job ID, connection, queue, failure time, and other information about the job. The job ID may be used to retry the failed job. For instance, to retry a failed job that has an ID of `ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece`, issue the following command:

```shell
php computer queue:retry ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece
```

If necessary, you may pass multiple IDs to the command:

```shell
php computer queue:retry ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece 91401d2c-0784-4f43-824c-34f94a33c24d
```

You may also retry all of the failed jobs for a particular queue:

```shell
php computer queue:retry --queue=name
```

To retry all of your failed jobs, execute the `queue:retry` command and pass `all` as the ID:

```shell
php computer queue:retry all
```

If you would like to delete a failed job, you may use the `queue:forget` command:

```shell
php computer queue:forget 91401d2c-0784-4f43-824c-34f94a33c24d
```

To delete all of your failed jobs, you may use the `queue:flush` command:

```shell
php computer queue:flush
```

The `queue:flush` command removes all failed job records from your queue, no matter how old the failed job is. You may use the `--hours` option to only delete jobs that failed a certain number of hours ago or earlier:

```shell
php computer queue:flush --hours=48
```

### Ignoring Missing Models

When injecting an Instrument model into a job, the model is automatically serialized before being placed on the queue and re-retrieved from the database when the job is processed. However, if the model has been deleted while the job was waiting to be processed by a worker, your job may fail with a `ModelNotFoundException`.

For convenience, you may choose to automatically delete jobs with missing models using the `DeleteWhenMissingModels` attribute on your job class. When this attribute is present, Venusian will quietly discard the job without raising an exception:

```php
<?php

namespace App\Jobs;

use Voyager\Queue\Attributes\DeleteWhenMissingModels;

#[DeleteWhenMissingModels]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

### Pruning Failed Jobs

You may prune your application's failed job records by invoking the `queue:prune-failed` Computer command:

```shell
php computer queue:prune-failed
```

By default, all the failed job records that are more than 24 hours old will be pruned. If you provide the `--hours` option to the command, only the failed job records that were inserted within the last N number of hours will be retained. For example, the following command will delete all the failed job records that were inserted more than 48 hours ago:

```shell
php computer queue:prune-failed --hours=48
```

### Disabling Failed Job Storage

You may instruct Venusian to discard failed jobs without storing them by setting the `queue.failed.driver` configuration option's value to `null`. Typically, this may be accomplished via the `QUEUE_FAILED_DRIVER` environment variable:

```ini
QUEUE_FAILED_DRIVER=null
```

### Failed Job Signals

If you would like to register a listener that will be invoked when a job fails, you may use the queue manager's `failing` method. For example, we may attach a closure to this signal from the `boot` method of the `AppServiceProvider` that is included with Venusian:

```php
<?php

namespace App\Providers;

use Voyager\NutsAndBolts\ServiceProvider;
use Voyager\Queue\Signals\JobFailed;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // ...
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        app('queue')->failing(function (JobFailed $event) {
            // $event->connectionName
            // $event->job
            // $event->exception
        });
    }
}
```

## Clearing Jobs From Queues

If you would like to delete all jobs from the default queue of the default connection, you may do so using the `queue:clear` Computer command:

```shell
php computer queue:clear
```

You may also provide the `connection` argument and `queue` option to delete jobs from a specific connection and queue:

```shell
php computer queue:clear redis --queue=emails
```

> [!WARNING]
> Clearing jobs from queues is only available for the Redis and database queue drivers.

## Monitoring Your Queues

If your queue receives a sudden influx of jobs, it could become overwhelmed, leading to a long wait time for jobs to complete. If you wish, Venusian can alert you when your queue job count exceeds a specified threshold.

To get started, you should run the `queue:monitor` command every minute, from your system's scheduler such as `cron`. The command accepts the names of the queues you wish to monitor as well as your desired job count threshold:

```shell
php computer queue:monitor redis:default,redis:deployments --max=100
```

Running this command alone is not enough to alert you of the queue's overwhelmed status. When the command encounters a queue that has a job count exceeding your threshold, a `Voyager\Queue\Signals\QueueBusy` signal will be dispatched. You may listen for this signal within your application's `AppServiceProvider` in order to alert you or your development team:

```php
use Voyager\Queue\Signals\QueueBusy;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('signals')->listen(function (QueueBusy $event) {
        app('log')->warning('Queue is busy.', [
            'connection' => $event->connection,
            'queue' => $event->queue,
            'size' => $event->size,
        ]);
    });
}
```

## Testing

To test a job itself, you may instantiate a job instance and invoke the `handle` method directly in your test. Venusian provides fakes for the two things a job most often talks to while it runs: its batch and its queue job.

### Testing Job Chain Modifications

If a chained job [prepends or appends jobs to an existing chain](#adding-jobs-to-the-chain), you may use the job's `assertHasChain` method to assert that the job has the expected chain of remaining jobs:

```php
$job = new ProcessPodcast;

$job->handle();

$job->assertHasChain([
    new TranscribePodcast,
    new OptimizePodcast,
    new ReleasePodcast,
]);
```

The `assertDoesntHaveChain` method may be used to assert that the job's remaining chain is empty:

```php
$job->assertDoesntHaveChain();
```

### Testing Job / Batch Interaction

You may occasionally need to test an individual job's interaction with its underlying batch. For example, you may need to test if a job cancelled further processing for its batch. To accomplish this, you need to assign a fake batch to the job via the `withFakeBatch` method. The `withFakeBatch` method returns a tuple containing the job instance and a `Voyager\Bus\Testing\BatchFake`, which records the jobs added to it and whether it was cancelled without touching the batch repository:

```php
[$job, $batch] = (new ShipOrder)->withFakeBatch();

$job->handle();

expect($batch->cancelled())->toBeTrue()
    ->and($batch->added)->toBeEmpty();
```

### Testing Job / Queue Interactions

Sometimes, you may need to test that a queued job [releases itself back onto the queue](#manually-releasing-a-job). Or, you may need to test that the job deleted itself. You may test these queue interactions by instantiating the job and invoking the `withFakeQueueInteractions` method.

Once the job's queue interactions have been faked, you may invoke the `handle` method on the job. After invoking the job, various assertion methods are available to verify the job's queue interactions:

```php
use App\Exceptions\CorruptedAudioException;
use App\Jobs\ProcessPodcast;

$job = (new ProcessPodcast)->withFakeQueueInteractions();

$job->handle();

$job->assertReleased(delay: 30);
$job->assertDeleted();
$job->assertNotDeleted();
$job->assertFailed();
$job->assertFailedWith(CorruptedAudioException::class);
$job->assertNotFailed();
```

## Job Signals

Using the `before` and `after` methods on the queue manager, you may specify callbacks to be executed before or after a queued job is processed. These callbacks are a great opportunity to perform additional logging or increment statistics for a dashboard. Typically, you should call these methods from the `boot` method of a [service provider](/docs/{{version}}/framework/architecture-concepts/providers). For example, we may use the `AppServiceProvider` that is included with Venusian:

```php
<?php

namespace App\Providers;

use Voyager\NutsAndBolts\ServiceProvider;
use Voyager\Queue\Signals\JobProcessed;
use Voyager\Queue\Signals\JobProcessing;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // ...
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        app('queue')->before(function (JobProcessing $event) {
            // $event->connectionName
            // $event->job
            // $event->job->payload()
        });

        app('queue')->after(function (JobProcessed $event) {
            // $event->connectionName
            // $event->job
            // $event->job->payload()
        });
    }
}
```

Using the `looping` method on the queue manager, you may specify callbacks that execute before the worker attempts to fetch a job from a queue. For example, you might register a closure to rollback any transactions that were left open by a previously failed job:

```php
app('queue')->looping(function () {
    while (app('db')->transactionLevel() > 0) {
        app('db')->rollBack();
    }
});
```

The queue manager also offers `exceptionOccurred`, `starting`, and `stopping` methods, which listen for the `JobExceptionOccurred`, `WorkerStarting`, and `WorkerStopping` signals. All of the queue's signals live in the `Voyager\Queue\Signals` namespace, and you may listen for any of them on the `signals` dispatcher. Pushing a job dispatches `JobQueueing` before the push and `JobQueued`, carrying the job's ID, after it:

```php
use Voyager\Queue\Signals\JobQueued;

app('signals')->listen(function (JobQueued $event) {
    // $event->id
});
```
