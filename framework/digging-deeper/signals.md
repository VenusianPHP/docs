# Signals

Venusian's signals provide a simple observer pattern implementation, allowing you to subscribe and listen for various signals that occur within your application.

## Introduction

Venusian's signals provide a simple observer pattern implementation, allowing you to subscribe and listen for various signals that occur within your application. Signal classes are typically stored in the `app/Events` directory, while their listeners are stored in `app/Listeners`. Don't worry if you don't see these directories in your application as they will be created for you as you generate signals and listeners using Computer console commands.

Signals serve as a great way to decouple various aspects of your application, since a single signal can have multiple listeners that do not depend on each other. For example, you may wish to notify a customer each time an order has shipped. Instead of coupling your order processing code to your notification code, you can raise an `App\Events\OrderShipped` signal which a listener can receive and use to send the notification.

The signal dispatcher is bound in the service container as `signals`. It is an instance of `Voyager\Signals\SignalDispatcher`, which implements the `Voyager\Contracts\Signals\SignalDispatcher` contract, so you may resolve it with `app('signals')` or type-hint the contract in any class the container builds.

## Writing Signals and Listeners

Signals and listeners are plain classes that you write by hand. By convention, signals live in `app/Signals` and listeners in `app/Listeners`. A signal is any object, and a listener is any class with a `handle` method that receives it. Examples of both follow below, and the [queued listener](#queued-signal-listeners) section shows the extra interface a listener needs to run on the queue.

## Registering Signals and Listeners

### Signal Discovery

By default, Venusian will automatically find and register your listeners by scanning your application's `Listeners` directory. When Venusian finds any listener class method that begins with `handle` or `__invoke`, Venusian will register those methods as listeners for the signal that is type-hinted in the method's signature:

```php
use App\Events\PodcastProcessed;

class SendPodcastNotification
{
    /**
     * Handle the signal.
     */
    public function handle(PodcastProcessed $event): void
    {
        // ...
    }
}
```

You may listen to multiple signals using PHP's union types:

```php
/**
 * Handle the signal.
 */
public function handle(PodcastProcessed|PodcastPublished $event): void
{
    // ...
}
```

If you plan to store your listeners in a different directory or within multiple directories, you may instruct Venusian to scan those directories using the `withSignals` method in your application's `bootstrap/app.php` file:

```php
->withSignals(discover: [
    __DIR__.'/../app/Domain/Orders/Listeners',
])
```

You may scan for listeners in multiple similar directories using the `*` character as a wildcard:

```php
->withSignals(discover: [
    __DIR__.'/../app/Domain/*/Listeners',
])
```

Passing `false` turns discovery off, leaving only the listeners you register yourself:

```php
->withSignals(discover: false)
```

The `signal:list` command may be used to list all of the listeners registered within your application. The `--event` option filters the list by signal name, and `--json` prints it as JSON:

```shell
php computer signal:list

php computer signal:list --event=PodcastProcessed
```

#### Signal Discovery in Production

To give your application a speed boost, you should cache a manifest of all of your application's listeners using the `signal:cache` Computer command. Typically, this command should be run as part of your application's deployment process. This manifest will be used by the framework to speed up the signal registration process. The `signal:clear` command may be used to destroy the signal cache.

```shell
php computer signal:cache

php computer signal:clear
```

### Manually Registering Signals

Using the `signals` dispatcher, you may manually register signals and their corresponding listeners within the `boot` method of your application's `AppServiceProvider`:

```php
use App\Domain\Orders\Events\PodcastProcessed;
use App\Domain\Orders\Listeners\SendPodcastNotification;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('signals')->listen(
        PodcastProcessed::class,
        SendPodcastNotification::class,
    );
}
```

A signal does not have to be a class. You may listen for, and dispatch, a plain string name:

```php
app('signals')->listen('podcast.processed', function (string $title) {
    // ...
});
```

The `signal:list` command may be used to list all of the listeners registered within your application:

```shell
php computer signal:list
```

### Closure Listeners

Typically, listeners are defined as classes; however, you may also manually register closure-based listeners in the `boot` method of your application's `AppServiceProvider`. The dispatcher reads the signal from the closure's first parameter type:

```php
use App\Events\PodcastProcessed;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('signals')->listen(function (PodcastProcessed $event) {
        // ...
    });
}
```

#### Queueable Anonymous Listeners

When registering closure-based listeners, you may wrap the listener closure in a `Voyager\Signals\QueuedClosure` to instruct Venusian to execute the listener using the [queue](/docs/{{version}}/framework/digging-deeper/queues):

```php
use App\Events\PodcastProcessed;
use Voyager\Signals\QueuedClosure;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('signals')->listen(new QueuedClosure(function (PodcastProcessed $event) {
        // ...
    }));
}
```

Like queued jobs, you may use the `onConnection`, `onQueue`, and `delay` methods to customize the execution of the queued listener:

```php
app('signals')->listen(new QueuedClosure(function (PodcastProcessed $event) {
    // ...
})->onConnection('redis')->onQueue('podcasts')->delay(now()->addSeconds(10)));
```

If you would like to handle anonymous queued listener failures, you may provide a closure to the `catch` method while defining the queued closure. This closure will receive the signal instance and the `Throwable` instance that caused the listener's failure:

```php
use App\Events\PodcastProcessed;
use Throwable;
use Voyager\Signals\QueuedClosure;

app('signals')->listen(new QueuedClosure(function (PodcastProcessed $event) {
    // ...
})->catch(function (PodcastProcessed $event, Throwable $e) {
    // The queued listener failed...
}));
```

The closure and its `catch` callbacks are serialized onto the queue, so they should not capture objects that cannot be serialized.

#### Wildcard Listeners

You may also register listeners using the `*` character as a wildcard parameter, allowing you to catch multiple signals on the same listener. Wildcard listeners receive the signal name as their first argument and the entire signal data array as their second argument:

```php
app('signals')->listen('event.*', function (string $eventName, array $data) {
    // ...
});
```

A signal dispatched as an object answers to its class name, to every interface it implements, and to any wildcard that matches one of those names. A listener registered under more than one of them still hears the signal once.

#### Instrument Model Signals

Instrument models dispatch their lifecycle signals on the `signals` dispatcher under names of the form `instrument.{event}: {model class}`. You may listen for one by name, with the model as the listener's argument, or for many at once with a wildcard such as `instrument.created: *`:

```php
use App\Models\User;

app('signals')->listen('instrument.created: '.User::class, function (User $user) {
    // ...
});
```

A model may also map its lifecycle events to signal classes of your own through its `$dispatchesEvents` property. See the [Instrument documentation](/docs/{{version}}/framework/instrument-orm/instrument) for model observers and the full list of lifecycle events.

## Defining Signals

A signal class is essentially a data container which holds the information related to the signal. For example, let's assume an `App\Events\OrderShipped` signal receives an [Instrument ORM](/docs/{{version}}/framework/instrument-orm/instrument) object:

```php
<?php

namespace App\Events;

use App\Models\Order;
use Voyager\Broadcasting\InteractsWithSockets;
use Voyager\Queue\SerializesModels;

class OrderShipped
{
    use InteractsWithSockets, SerializesModels;

    /**
     * Create a new signal instance.
     */
    public function __construct(
        public Order $order,
    ) {}
}
```

As you can see, this signal class contains no logic. It is a container for the `App\Models\Order` instance that was purchased. The `SerializesModels` trait used by the signal will gracefully serialize any Instrument models if the signal object is serialized using PHP's `serialize` function, such as when utilizing [queued listeners](#queued-signal-listeners).

### Named Signals

By default, a signal object is dispatched under its class name. A signal implementing `Voyager\Contracts\Signals\NamedSignal` is dispatched under the name its `name` method returns instead, so string listeners for that name hear it as well:

```php
<?php

namespace App\Events;

use Voyager\Contracts\Signals\NamedSignal;

class PodcastProcessed implements NamedSignal
{
    public function __construct(
        public string $title,
    ) {}

    /**
     * Get the name the signal is dispatched under.
     */
    public function name(): string
    {
        return 'podcast.processed';
    }
}
```

## Defining Listeners

Next, let's take a look at the listener for our example signal. Listeners receive signal instances in their `handle` method. Type-hint the signal in the `handle` method so the dispatcher can match it. Within the `handle` method, you may perform any actions necessary to respond to the signal:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;

class SendShipmentNotification
{
    /**
     * Create the listener.
     */
    public function __construct() {}

    /**
     * Handle the signal.
     */
    public function handle(OrderShipped $event): void
    {
        // Access the order using $event->order...
    }
}
```

> [!NOTE]
> Your listeners may also type-hint any dependencies they need on their constructors. All listeners are resolved via the Venusian [service container](/docs/{{version}}/framework/architecture-concepts/container), so dependencies will be injected automatically.

#### Stopping The Propagation Of A Signal

Sometimes, you may wish to stop the propagation of a signal to other listeners. You may do so by returning `false` from your listener's `handle` method.

## Queued Signal Listeners

Queueing listeners can be beneficial if your listener is going to perform a slow task such as sending an email or making an HTTP request. Before using queued listeners, make sure to [configure your queue](/docs/{{version}}/framework/digging-deeper/queues) and start a queue worker on your server or local development environment.

To specify that a listener should be queued, add the `ShouldQueue` interface to the listener class:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Voyager\Contracts\Queue\ShouldQueue;

class SendShipmentNotification implements ShouldQueue
{
    /**
     * Handle the signal.
     */
    public function handle(?OrderShipped $event = null): mixed
    {
        // ...

        return null;
    }
}
```

That's it! Now, when a signal handled by this listener is dispatched, the listener will automatically be queued by the signal dispatcher using Venusian's [queue system](/docs/{{version}}/framework/digging-deeper/queues). If no exceptions are thrown when the listener is executed by the queue, the queued job will automatically be deleted after it has finished processing.

> [!NOTE]
> `ShouldQueue` extends `Voyager\Contracts\NutsAndBolts\Handleable`, which declares `handle(): mixed`. A queued listener therefore declares its `handle` method with the signal as an optional parameter and a `mixed` return type, as shown above. The worker passes the signal in when it runs the listener.

#### Customizing The Queue Connection, Name, & Delay

If you would like to customize the queue connection, queue name, or queue delay time of a listener, you may define the `connection`, `queue`, or `delay` properties on your listener class. The dispatcher reads these properties without calling the listener's constructor, so give them their values in the declaration:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Voyager\Contracts\Queue\ShouldQueue;

class SendShipmentNotification implements ShouldQueue
{
    /**
     * The name of the connection the job should be sent to.
     */
    public ?string $connection = 'redis';

    /**
     * The name of the queue the job should be sent to.
     */
    public ?string $queue = 'listeners';

    /**
     * The time (seconds) before the job should be processed.
     */
    public int $delay = 60;

    // ...
}
```

If you would like to define the listener's queue connection, queue name, or delay at runtime, you may define `viaConnection`, `viaQueue`, or `withDelay` methods on the listener. Each method receives the signal:

```php
/**
 * Get the name of the listener's queue connection.
 */
public function viaConnection(OrderShipped $event): string
{
    return 'redis';
}

/**
 * Get the name of the listener's queue.
 */
public function viaQueue(OrderShipped $event): string
{
    return 'listeners';
}

/**
 * Get the number of seconds before the job should be processed.
 */
public function withDelay(OrderShipped $event): int
{
    return $event->highPriority ? 0 : 60;
}
```

#### Conditionally Queueing Listeners

Sometimes, you may need to determine whether a listener should be queued based on some data that are only available at runtime. To accomplish this, a `shouldQueue` method may be added to a listener to determine whether the listener should be queued. If the `shouldQueue` method returns `false`, the listener will not be queued:

```php
<?php

namespace App\Listeners;

use App\Events\OrderCreated;
use Voyager\Contracts\Queue\ShouldQueue;

class RewardGiftCard implements ShouldQueue
{
    /**
     * Reward a gift card to the customer.
     */
    public function handle(?OrderCreated $event = null): mixed
    {
        // ...

        return null;
    }

    /**
     * Determine whether the listener should be queued.
     */
    public function shouldQueue(OrderCreated $event): bool
    {
        return $event->order->subtotal >= 5000;
    }
}
```

### Manually Interacting With the Queue

If you need to manually access the listener's underlying queue job's `delete` and `release` methods, you may do so using the `Voyager\Queue\InteractsWithQueue` trait. This trait is imported by default on generated queued listeners and provides access to these methods:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Queue\InteractsWithQueue;

class SendShipmentNotification implements ShouldQueue
{
    use InteractsWithQueue;

    /**
     * Handle the signal.
     */
    public function handle(?OrderShipped $event = null): mixed
    {
        if ($condition) {
            $this->release(30);
        }

        return null;
    }
}
```

### Queued Listeners and Database Transactions

When queued listeners are dispatched within database transactions, they may be processed by the queue before the database transaction has committed. When this happens, any updates you have made to models or database records during the database transaction may not yet be reflected in the database. In addition, any models or database records created within the transaction may not exist in the database. If your listener depends on these models, unexpected errors can occur when the job that dispatches the queued listener is processed.

If your queue connection's `after_commit` configuration option is set to `false`, you may still indicate that a particular queued listener should be dispatched after all open database transactions have been committed by implementing the `ShouldQueueAfterCommit` interface on the listener class:

```php
<?php

namespace App\Listeners;

use Voyager\Contracts\Queue\ShouldQueueAfterCommit;
use Voyager\Queue\InteractsWithQueue;

class SendShipmentNotification implements ShouldQueueAfterCommit
{
    use InteractsWithQueue;
}
```

A listener that is not queued may run after the commit as well, by implementing `Voyager\Contracts\Signals\ShouldHandleSignalsAfterCommit` or declaring a public `$afterCommit = true` property.

> [!NOTE]
> To learn more about working around these issues, please review the documentation regarding [queued jobs and database transactions](/docs/{{version}}/framework/digging-deeper/queues#jobs-and-database-transactions).

### Queued Listener Middleware

Queued listeners can also utilize [job middleware](/docs/{{version}}/framework/digging-deeper/queues#job-middleware). Job middleware allow you to wrap custom logic around the execution of queued listeners, reducing boilerplate in the listeners themselves. After creating job middleware, they may be attached to a listener by returning them from the listener's `middleware` method:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use App\Jobs\Middleware\RateLimited;
use Voyager\Contracts\Queue\ShouldQueue;

class SendShipmentNotification implements ShouldQueue
{
    /**
     * Handle the signal.
     */
    public function handle(?OrderShipped $event = null): mixed
    {
        // Process the signal...

        return null;
    }

    /**
     * Get the middleware the listener should pass through.
     *
     * @return array<int, object>
     */
    public function middleware(OrderShipped $event): array
    {
        return [new RateLimited];
    }
}
```

#### Encrypted Queued Listeners

Venusian allows you to ensure the privacy and integrity of a queued listener's data via [encryption](/docs/{{version}}/framework/security/encryption). To get started, simply add the `ShouldBeEncrypted` interface to the listener class. Once this interface has been added to the class, Venusian will automatically encrypt your listener before pushing it onto a queue:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Voyager\Contracts\Queue\ShouldBeEncrypted;
use Voyager\Contracts\Queue\ShouldQueue;

class SendShipmentNotification implements ShouldQueue, ShouldBeEncrypted
{
    // ...
}
```

### Unique Listeners

> [!WARNING]
> Unique listeners require a cache driver that supports [locks](/docs/{{version}}/framework/digging-deeper/cache#atomic-locks). Currently, the `redis`, `database`, `file`, and `array` cache drivers support atomic locks.

Sometimes, you may want to ensure that only one instance of a specific listener is on the queue at any point in time. You may do so by implementing the `ShouldBeUnique` interface on your listener class:

```php
<?php

namespace App\Listeners;

use App\Events\LicenseSaved;
use Voyager\Contracts\Queue\ShouldBeUnique;
use Voyager\Contracts\Queue\ShouldQueue;

class AcquireProductKey implements ShouldQueue, ShouldBeUnique
{
    public function handle(?LicenseSaved $event = null): mixed
    {
        // ...

        return null;
    }
}
```

In the example above, the `AcquireProductKey` listener is unique. So, the listener will not be queued if another instance of the listener is already on the queue and has not finished processing. This ensures that only one product key is acquired for each license, even if the license is saved multiple times in quick succession.

In certain cases, you may want to define a specific "key" that makes the listener unique or you may want to specify a timeout beyond which the listener no longer stays unique. To accomplish this, you may define `uniqueId` and `uniqueFor` properties or methods on your listener class. The methods receive the signal instance, allowing you to use signal data to construct the return value:

```php
<?php

namespace App\Listeners;

use App\Events\LicenseSaved;
use Voyager\Contracts\Queue\ShouldBeUnique;
use Voyager\Contracts\Queue\ShouldQueue;

class AcquireProductKey implements ShouldQueue, ShouldBeUnique
{
    /**
     * The number of seconds after which the listener's unique lock will be released.
     *
     * @var int
     */
    public $uniqueFor = 3600;

    public function handle(?LicenseSaved $event = null): mixed
    {
        // ...

        return null;
    }

    /**
     * Get the unique ID for the listener.
     */
    public function uniqueId(LicenseSaved $event): string
    {
        return 'listener:'.$event->license->id;
    }
}
```

In the example above, the `AcquireProductKey` listener is unique by license ID. So, any new dispatches of the listener for the same license will be ignored until the existing listener has completed processing. This prevents duplicate product keys from being acquired for the same license. In addition, if the existing listener is not processed within one hour, the unique lock will be released and another listener with the same unique key can be queued.

> [!WARNING]
> If your application dispatches signals from multiple servers or containers, you should ensure that all of your servers are communicating with the same central cache server so that Venusian can accurately determine if a listener is unique.

#### Keeping Listeners Unique Until Processing Begins

By default, unique listeners are "unlocked" after a listener completes processing or fails all of its retry attempts. However, there may be situations where you would like your listener to unlock immediately before it is processed. To accomplish this, your listener should implement the `ShouldBeUniqueUntilProcessing` contract instead of the `ShouldBeUnique` contract:

```php
<?php

namespace App\Listeners;

use App\Events\LicenseSaved;
use Voyager\Contracts\Queue\ShouldBeUniqueUntilProcessing;
use Voyager\Contracts\Queue\ShouldQueue;

class AcquireProductKey implements ShouldQueue, ShouldBeUniqueUntilProcessing
{
    // ...
}
```

#### Unique Listener Locks

Behind the scenes, when a `ShouldBeUnique` listener is dispatched, Venusian attempts to acquire a [lock](/docs/{{version}}/framework/digging-deeper/cache#atomic-locks) with the `uniqueId` key. If the lock is already held, the listener is not dispatched. This lock is released when the listener completes processing or fails all of its retry attempts. By default, Venusian will use the default cache driver to obtain this lock. However, if you wish to use another driver for acquiring the lock, you may define a `uniqueVia` method that returns the cache driver that should be used:

```php
<?php

namespace App\Listeners;

use App\Events\LicenseSaved;
use Voyager\Contracts\Cache\Repository;
use Voyager\Contracts\Queue\ShouldBeUnique;
use Voyager\Contracts\Queue\ShouldQueue;

class AcquireProductKey implements ShouldQueue, ShouldBeUnique
{
    // ...

    /**
     * Get the cache driver for the unique listener lock.
     */
    public function uniqueVia(LicenseSaved $event): Repository
    {
        return app('cache')->store('redis');
    }
}
```

> [!NOTE]
> If you only need to limit the concurrent processing of a listener, use the [WithoutOverlapping](/docs/{{version}}/framework/digging-deeper/queues#preventing-job-overlaps) job middleware instead.

### Handling Failed Jobs

Sometimes your queued listeners may fail. If the queued listener exceeds the maximum number of attempts as defined by your queue worker, the `failed` method will be called on your listener. The `failed` method receives the signal instance and the `Throwable` that caused the failure:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Throwable;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Queue\InteractsWithQueue;

class SendShipmentNotification implements ShouldQueue
{
    use InteractsWithQueue;

    /**
     * Handle the signal.
     */
    public function handle(?OrderShipped $event = null): mixed
    {
        // ...

        return null;
    }

    /**
     * Handle a job failure.
     */
    public function failed(OrderShipped $event, Throwable $exception): void
    {
        // ...
    }
}
```

#### Specifying Queued Listener Maximum Attempts

If one of your queued listeners is encountering an error, you likely do not want it to keep retrying indefinitely. Therefore, Venusian provides various ways to specify how many times or for how long a listener may be attempted.

You may define a `tries` property or method on your listener class to specify how many times the listener may be attempted before it is considered to have failed:

```php
<?php

namespace App\Listeners;

use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Queue\InteractsWithQueue;

class SendShipmentNotification implements ShouldQueue
{
    use InteractsWithQueue;

    /**
     * The number of times the queued listener may be attempted.
     *
     * @var int
     */
    public $tries = 5;

    // ...
}
```

As an alternative to defining how many times a listener may be attempted before it fails, you may define a time at which the listener should no longer be attempted. This allows a listener to be attempted any number of times within a given time frame. To define the time at which a listener should no longer be attempted, add a `retryUntil` method to your listener class. This method should return a `DateTimeInterface` instance:

```php
use DateTimeInterface;

/**
 * Determine the time at which the listener should timeout.
 */
public function retryUntil(): DateTimeInterface
{
    return now()->addMinutes(5);
}
```

If both `retryUntil` and `tries` are defined, Venusian gives precedence to the `retryUntil` method.

#### Specifying Queued Listener Backoff

If you would like to configure how many seconds Venusian should wait before retrying a listener that has encountered an exception, you may define a `backoff` property on your listener class:

```php
<?php

namespace App\Listeners;

use Voyager\Contracts\Queue\ShouldQueue;

class SendShipmentNotification implements ShouldQueue
{
    /**
     * The number of seconds to wait before retrying the queued listener.
     *
     * @var int
     */
    public $backoff = 3;

    // ...
}
```

If you require more complex logic for determining the listener's backoff time, you may define a `backoff` method on your listener class:

```php
/**
 * Calculate the number of seconds to wait before retrying the queued listener.
 */
public function backoff(OrderShipped $event): int
{
    return 3;
}
```

You may easily configure "exponential" backoffs by returning an array of backoff values from the `backoff` method. In this example, the retry delay will be 1 second for the first retry, 5 seconds for the second retry, 10 seconds for the third retry, and 10 seconds for every subsequent retry if there are more attempts remaining:

```php
/**
 * Calculate the number of seconds to wait before retrying the queued listener.
 *
 * @return list<int>
 */
public function backoff(OrderShipped $event): array
{
    return [1, 5, 10];
}
```

#### Specifying Queued Listener Max Exceptions

Sometimes you may wish to specify that a queued listener may be attempted many times, but should fail if the retries are triggered by a given number of unhandled exceptions (as opposed to being released by the `release` method directly). To accomplish this, you may define the `tries` and `maxExceptions` properties on your listener class:

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Voyager\Contracts\Queue\ShouldQueue;
use Voyager\Queue\InteractsWithQueue;

class SendShipmentNotification implements ShouldQueue
{
    use InteractsWithQueue;

    /**
     * The number of times the queued listener may be attempted.
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
     * Handle the signal.
     */
    public function handle(?OrderShipped $event = null): mixed
    {
        // Process the signal...

        return null;
    }
}
```

In this example, the listener will be retried up to 25 times. However, the listener will fail if three unhandled exceptions are thrown by the listener.

#### Specifying Queued Listener Timeout

Often, you know roughly how long you expect your queued listeners to take. For this reason, Venusian allows you to specify a "timeout" value. If a listener is processing for longer than the number of seconds specified by the timeout value, the worker processing the listener will exit with an error. You may define the maximum number of seconds a listener should be allowed to run by defining a `timeout` property on your listener class:

```php
<?php

namespace App\Listeners;

use Voyager\Contracts\Queue\ShouldQueue;

class SendShipmentNotification implements ShouldQueue
{
    /**
     * The number of seconds the listener can run before timing out.
     *
     * @var int
     */
    public $timeout = 120;

    // ...
}
```

If you would like to indicate that a listener should be marked as failed on timeout, you may define the `failOnTimeout` property on the listener class:

```php
/**
 * Indicate if the listener should be marked as failed on timeout.
 *
 * @var bool
 */
public $failOnTimeout = true;
```

> [!WARNING]
> The worker enforces timeouts with the `pcntl` PHP extension. Without it, a listener that runs too long is not stopped.

## Dispatching Signals

To dispatch a signal, you may pass a signal instance to the `signal` helper. The helper hands the signal to the `signals` dispatcher, which calls every registered listener and returns their responses:

```php
<?php

namespace App\Orders;

use App\Events\OrderShipped;
use App\Models\Order;

class ShipOrder
{
    /**
     * Ship the given order.
     */
    public function __invoke(int $orderId): void
    {
        $order = Order::findOrFail($orderId);

        // Order shipment logic...

        signal(new OrderShipped($order));
    }
}
```

The helper is a shortcut for `app('signals')->dispatch(...)`. A string signal name takes its payload as the second argument, and the listeners receive the payload's values as their arguments:

```php
signal('podcast.processed', ['My first podcast']);

app('signals')->dispatch('podcast.processed', ['My first podcast']);
```

If you would like only the first listener's answer, pass `halt: true`, or call the dispatcher's `until` method. Dispatching stops at the first listener that returns a value other than `null`, and that value is returned:

```php
$answer = signal('podcast.processed', ['My first podcast'], halt: true);

$answer = app('signals')->until('podcast.processed', ['My first podcast']);
```

### Dispatching Signals After Database Transactions

Sometimes, you may want to instruct Venusian to only dispatch a signal after the active database transaction has committed. To do so, you may implement the `ShouldDispatchAfterCommit` interface on the signal class.

This interface instructs Venusian to not dispatch the signal until the current database transaction is committed. If the transaction fails, the signal will be discarded. If no database transaction is in progress when the signal is dispatched, the signal will be dispatched immediately:

```php
<?php

namespace App\Events;

use App\Models\Order;
use Voyager\Broadcasting\InteractsWithSockets;
use Voyager\Contracts\Signals\ShouldDispatchAfterCommit;
use Voyager\Queue\SerializesModels;

class OrderShipped implements ShouldDispatchAfterCommit
{
    use InteractsWithSockets, SerializesModels;

    /**
     * Create a new signal instance.
     */
    public function __construct(
        public Order $order,
    ) {}
}
```

### Pushing Signals for Later

The dispatcher's `push` method registers a signal and its payload without dispatching it. Calling `flush` with the same name dispatches everything that was pushed under it:

```php
app('signals')->push('report.ready', ['monthly']);

// ...

app('signals')->flush('report.ready');
```

The `forgetPushed` method discards every pushed signal that has not been flushed, and `forget` removes all listeners for a given signal name.

## Signal Subscribers

### Writing Signal Subscribers

Signal subscribers are classes that may subscribe to multiple signals from within the subscriber class itself, allowing you to define several handlers within a single class. Subscribers should define a `subscribe` method, which receives a signal dispatcher instance. You may call the `listen` method on the given dispatcher to register listeners:

```php
<?php

namespace App\Listeners;

use App\Events\PodcastProcessed;
use App\Events\PodcastPublished;
use Voyager\Signals\SignalDispatcher;

class PodcastSignalSubscriber
{
    /**
     * Handle podcast processed signals.
     */
    public function handlePodcastProcessed(PodcastProcessed $event): void {}

    /**
     * Handle podcast published signals.
     */
    public function handlePodcastPublished(PodcastPublished $event): void {}

    /**
     * Register the listeners for the subscriber.
     */
    public function subscribe(SignalDispatcher $signals): void
    {
        $signals->listen(
            PodcastProcessed::class,
            [PodcastSignalSubscriber::class, 'handlePodcastProcessed']
        );

        $signals->listen(
            PodcastPublished::class,
            [PodcastSignalSubscriber::class, 'handlePodcastPublished']
        );
    }
}
```

If your listener methods are defined within the subscriber itself, you may find it more convenient to return an array of signals and method names from the subscriber's `subscribe` method. Venusian will automatically determine the subscriber's class name when registering the listeners:

```php
<?php

namespace App\Listeners;

use App\Events\PodcastProcessed;
use App\Events\PodcastPublished;
use Voyager\Signals\SignalDispatcher;

class PodcastSignalSubscriber
{
    /**
     * Handle podcast processed signals.
     */
    public function handlePodcastProcessed(PodcastProcessed $event): void {}

    /**
     * Handle podcast published signals.
     */
    public function handlePodcastPublished(PodcastPublished $event): void {}

    /**
     * Register the listeners for the subscriber.
     *
     * @return array<string, string>
     */
    public function subscribe(SignalDispatcher $signals): array
    {
        return [
            PodcastProcessed::class => 'handlePodcastProcessed',
            PodcastPublished::class => 'handlePodcastPublished',
        ];
    }
}
```

### Registering Signal Subscribers

After writing the subscriber, Venusian will automatically register handler methods within the subscriber if they follow Venusian's [signal discovery conventions](#signal-discovery). Otherwise, you may manually register your subscriber using the `subscribe` method of the `signals` dispatcher. Typically, this should be done within the `boot` method of your application's `AppServiceProvider`:

```php
<?php

namespace App\Providers;

use App\Listeners\PodcastSignalSubscriber;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        app('signals')->subscribe(PodcastSignalSubscriber::class);
    }
}
```
