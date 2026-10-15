# Contracts

Venusian's "contracts" are a set of interfaces that define the core services provided by the framework.

## Introduction

Venusian's "contracts" are a set of interfaces that define the core services provided by the framework. For example, a `Voyager\Contracts\Queue\Queue` contract defines the methods needed for queueing jobs, while the `Voyager\Contracts\Cache\Repository` contract defines the methods needed for reading and writing a cache store.

Each contract has a corresponding implementation provided by the framework. For example, Venusian provides a queue implementation with a variety of drivers, and a cache implementation with array, database, file, null and redis stores.

All of the Venusian contracts live in the framework's `Voyager\Contracts` component, which carries its own `composer.json` as `venusian-voyager/contracts` and requires nothing beyond the PSR container and simple-cache interfaces and Monolog. This provides a quick reference point for all available contracts, as well as a single, decoupled component that may be utilized when building packages that interact with Venusian services.

### Contracts and Container Keys

Venusian has no facades. Its services are reached through the [service container](/docs/{{version}}/framework/architecture-concepts/container): by type-hinting a contract, by resolving a container key such as `app('cache')`, or through a helper such as `config()` or `signal()`. The core service contracts are aliased to their container keys, listed in the [reference](#contract-reference) below, so type-hinting such a contract and resolving its key hand you the same object.

## When to Use Contracts

Type-hinting a contract makes a class's dependencies explicit: anyone reading its constructor sees exactly which services it uses, and a test can hand it any implementation of that contract. Resolving a container key with `app()` is shorter when you need a service in one place. Both reach the same objects, so you may mix them freely. As long as you are keeping your class' responsibilities focused, you will notice very few practical differences between them.

If you are building a package that integrates with Venusian's services, you may depend on the contracts alone to define your integration without the need to require Venusian's concrete implementations in your package's `composer.json` file.

## How to Use Contracts

So, how do you get an implementation of a contract? It's actually quite simple.

Many types of classes in Venusian are resolved through the [service container](/docs/{{version}}/framework/architecture-concepts/container), including signal listeners, sketches, Computer commands' `handle` methods, and queued jobs' `handle` methods. So, to get an implementation of a contract, you can just "type-hint" the interface in the constructor of the class being resolved.

For example, take a look at this signal listener:

```php
<?php

namespace App\Listeners;

use App\Signals\OrderWasPlaced;
use Voyager\Contracts\Cache\Repository;

class CacheOrderInformation
{
    /**
     * Create the listener.
     */
    public function __construct(
        protected Repository $cache,
    ) {}

    /**
     * Handle the signal.
     */
    public function handle(OrderWasPlaced $signal): void
    {
        // ...
    }
}
```

When the listener is resolved, the service container will read the type-hints on the constructor of the class, and inject the appropriate value. To learn more about registering things in the service container, check out [its documentation](/docs/{{version}}/framework/architecture-concepts/container).

<a id="contract-reference"></a>
## Contract Reference

This table provides a quick reference to the Venusian contracts. Where the container binds a contract under a key, the key is listed; resolving the key or type-hinting the contract gives the same service:

| Contract | Container Key |
| --- | --- |
| `Voyager\Contracts\Broadcasting\Broadcaster` | `broadcast.connection` |
| `Voyager\Contracts\Broadcasting\Factory` | `broadcast` |
| `Voyager\Contracts\Broadcasting\HasBroadcastChannel` | &nbsp; |
| `Voyager\Contracts\Broadcasting\ShouldBeUnique` | &nbsp; |
| `Voyager\Contracts\Broadcasting\ShouldBroadcast` | &nbsp; |
| `Voyager\Contracts\Broadcasting\ShouldBroadcastNow` | &nbsp; |
| `Voyager\Contracts\Broadcasting\ShouldRescue` | &nbsp; |
| `Voyager\Contracts\Bus\Dispatcher` | &nbsp; |
| `Voyager\Contracts\Bus\QueueingDispatcher` | &nbsp; |
| `Voyager\Contracts\Cache\Factory` | `cache` |
| `Voyager\Contracts\Cache\Lock` | &nbsp; |
| `Voyager\Contracts\Cache\LockProvider` | &nbsp; |
| `Voyager\Contracts\Cache\Repository` | `cache.store` |
| `Voyager\Contracts\Cache\Store` | &nbsp; |
| `Voyager\Contracts\Concurrency\AsyncDriver` | &nbsp; |
| `Voyager\Contracts\Concurrency\Driver` | &nbsp; |
| `Voyager\Contracts\Config\Repository` | `config` |
| `Voyager\Contracts\Console\ConsoleApplication` | &nbsp; |
| `Voyager\Contracts\Console\Isolatable` | &nbsp; |
| `Voyager\Contracts\Console\Kernel` | &nbsp; |
| `Voyager\Contracts\Console\PromptsForMissingInput` | &nbsp; |
| `Voyager\Contracts\Core\CachesConfiguration` | &nbsp; |
| `Voyager\Contracts\Core\ExceptionRenderer` | &nbsp; |
| `Voyager\Contracts\Core\FrameworkCore` | `app` |
| `Voyager\Contracts\Database\ConcurrencyErrorDetector` | &nbsp; |
| `Voyager\Contracts\Database\Events\MigrationEvent` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\Builder` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\Castable` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\CastsAttributes` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\CastsInboundAttributes` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\ComparesCastableAttributes` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\DeviatesCastableAttributes` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\SerializesCastableAttributes` | &nbsp; |
| `Voyager\Contracts\Database\Instrument\SupportsPartialRelations` | &nbsp; |
| `Voyager\Contracts\Database\LostConnectionDetector` | &nbsp; |
| `Voyager\Contracts\Database\Query\Builder` | &nbsp; |
| `Voyager\Contracts\Database\Query\ConditionExpression` | &nbsp; |
| `Voyager\Contracts\Database\Query\Expression` | &nbsp; |
| `Voyager\Contracts\Debug\ExceptionHandler` | &nbsp; |
| `Voyager\Contracts\Debug\ShouldntReport` | &nbsp; |
| `Voyager\Contracts\Encryption\Encrypter` | `encrypter` |
| `Voyager\Contracts\Encryption\StringEncrypter` | `encrypter` |
| `Voyager\Contracts\Filesystem\Cloud` | `filesystem.cloud` |
| `Voyager\Contracts\Filesystem\Factory` | `filesystem` |
| `Voyager\Contracts\Filesystem\Filesystem` | `filesystem.disk` |
| `Voyager\Contracts\Hashing\Hasher` | `hash.driver` |
| `Voyager\Contracts\IOPools\Loop` | `event-loop` |
| `Voyager\Contracts\IOPools\LoopResource` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Background` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Deadlined` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Resumable` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Sleepable` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Tickable` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Timer` | &nbsp; |
| `Voyager\Contracts\IOPools\LoopResources\Wakeable` | &nbsp; |
| `Voyager\Contracts\IOPools\MailHandler` | &nbsp; |
| `Voyager\Contracts\IOPools\Promise` | &nbsp; |
| `Voyager\Contracts\IOPools\PromiseEngine` | &nbsp; |
| `Voyager\Contracts\IOPools\Pumpable` | &nbsp; |
| `Voyager\Contracts\IOPools\Task` | &nbsp; |
| `Voyager\Contracts\IOPools\Waiter` | &nbsp; |
| `Voyager\Contracts\IOPools\WaiterBackendDriver` | &nbsp; |
| `Voyager\Contracts\IOPools\Wake` | &nbsp; |
| `Voyager\Contracts\IOPools\WorkerPools\PoolWorker` | &nbsp; |
| `Voyager\Contracts\IOPools\WorkerPools\ShouldPool` | &nbsp; |
| `Voyager\Contracts\IOPools\WorkerPools\WorkerPool` | &nbsp; |
| `Voyager\Contracts\Log\ContextLogProcessor` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\Arrayable` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\CanBeEscapedWhenCastToString` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\DeferrableProvider` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\DeferringDisplayableValue` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\Handleable` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\HasOnceHash` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\Htmlable` | &nbsp; |
| `Voyager\Contracts\NutsAndBolts\Jsonable` | &nbsp; |
| `Voyager\Contracts\Pagination\CursorPaginator` | &nbsp; |
| `Voyager\Contracts\Pagination\LengthAwarePaginator` | &nbsp; |
| `Voyager\Contracts\Pagination\Paginator` | &nbsp; |
| `Voyager\Contracts\Pipeline\Hub` | &nbsp; |
| `Voyager\Contracts\Pipeline\Pipeline` | &nbsp; |
| `Voyager\Contracts\Process\InvokedProcess` | &nbsp; |
| `Voyager\Contracts\Process\ProcessResult` | &nbsp; |
| `Voyager\Contracts\Queue\ClearableQueue` | &nbsp; |
| `Voyager\Contracts\Queue\EntityResolver` | &nbsp; |
| `Voyager\Contracts\Queue\Factory` | `queue` |
| `Voyager\Contracts\Queue\Job` | &nbsp; |
| `Voyager\Contracts\Queue\Monitor` | `queue` |
| `Voyager\Contracts\Queue\Queue` | `queue.connection` |
| `Voyager\Contracts\Queue\QueueableCollection` | &nbsp; |
| `Voyager\Contracts\Queue\QueueableEntity` | &nbsp; |
| `Voyager\Contracts\Queue\ShouldBeEncrypted` | &nbsp; |
| `Voyager\Contracts\Queue\ShouldBeUnique` | &nbsp; |
| `Voyager\Contracts\Queue\ShouldBeUniqueUntilProcessing` | &nbsp; |
| `Voyager\Contracts\Queue\ShouldQueue` | &nbsp; |
| `Voyager\Contracts\Queue\ShouldQueueAfterCommit` | &nbsp; |
| `Voyager\Contracts\Redis\Connection` | &nbsp; |
| `Voyager\Contracts\Redis\Connector` | &nbsp; |
| `Voyager\Contracts\Redis\Factory` | &nbsp; |
| `Voyager\Contracts\Signals\NamedSignal` | &nbsp; |
| `Voyager\Contracts\Signals\ShouldDispatchAfterCommit` | &nbsp; |
| `Voyager\Contracts\Signals\ShouldHandleSignalsAfterCommit` | &nbsp; |
| `Voyager\Contracts\Signals\Signal` | &nbsp; |
| `Voyager\Contracts\Signals\SignalDispatcher` | `signals` |
| `Voyager\Contracts\Sketches\Kernel` | &nbsp; |
| `Voyager\Contracts\Sketches\Sketch` | &nbsp; |
| `Voyager\Contracts\Sketches\SketchRegistry` | `sketches.registry` |
| `Voyager\Contracts\Vessel\ContextualAttribute` | &nbsp; |
| `Voyager\Contracts\Vessel\ContextualBindingBuilder` | &nbsp; |
| `Voyager\Contracts\Vessel\SelfBuilding` | &nbsp; |
| `Voyager\Contracts\Vessel\TheServiceContainer` | `app` |
| `Voyager\Contracts\Workflows\AsyncRunnable` | &nbsp; |
| `Voyager\Contracts\Workflows\AsyncRuntime` | &nbsp; |
| `Voyager\Contracts\Workflows\RuntimeAware` | &nbsp; |
