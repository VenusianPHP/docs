# Service Container

The Venusian service container is a powerful tool for managing class dependencies and performing dependency injection.

## Introduction

The Venusian service container is a powerful tool for managing class dependencies and performing dependency injection. Dependency injection is a fancy phrase that essentially means this: class dependencies are "injected" into the class via the constructor or, in some cases, "setter" methods.

The container is `Voyager\Vessel\ControlPanel`. Your application instance, `Voyager\Core\RenderedInstance`, extends it, so the application object you receive in service providers and from the `app()` helper *is* the container.

Let's look at a simple example:

```php
<?php

namespace App\Listeners;

use App\Services\AppleMusic;
use App\Signals\PodcastPublished;

class CachePodcastDetails
{
    /**
     * Create the listener.
     */
    public function __construct(
        protected AppleMusic $apple,
    ) {}

    /**
     * Handle the signal.
     */
    public function handle(PodcastPublished $signal): void
    {
        $podcast = $this->apple->findPodcast($signal->id);

        // ...
    }
}
```

In this example, the `CachePodcastDetails` listener needs to retrieve podcasts from a data source such as Apple Music. So, we will **inject** a service that is able to retrieve podcasts. Since the service is injected, we are able to easily "mock", or create a dummy implementation of the `AppleMusic` service when testing our application.

A deep understanding of the Venusian service container is essential to building a powerful, large application, as well as for contributing to the Venusian core itself.

### Zero Configuration Resolution

If a class has no dependencies or only depends on other concrete classes (not interfaces), the container does not need to be instructed on how to resolve that class. For example, you may type-hint such a class on the `handle` method of a [Computer](/docs/{{version}}/framework/digging-deeper/computer) command:

```php
<?php

namespace App\Console\Commands;

use App\Services\Service;
use Voyager\Console\Command;

class ShowService extends Command
{
    protected ?string $signature = 'service:show';

    protected string $description = 'Show the resolved service class';

    public function handle(Service $service): void
    {
        $this->info($service::class);
    }
}
```

In this example, running `php computer service:show` will automatically resolve the `Service` class and inject it into your command's handler. This is game changing. It means you can develop your application and take advantage of dependency injection without worrying about bloated configuration files.

Thankfully, many of the classes you will be writing when building a Venusian application automatically receive their dependencies via the container. Computer commands receive them in their `handle` method, [signal](/docs/{{version}}/framework/digging-deeper/signals) listeners and sketches are built by the container so their constructors are injected, and [queued jobs](/docs/{{version}}/framework/digging-deeper/queues) may type-hint dependencies in their `handle` method. Once you taste the power of automatic and zero configuration dependency injection it feels impossible to develop without it.

### When to Utilize the Container

Thanks to zero configuration resolution, you will often type-hint dependencies on commands, listeners, jobs, and elsewhere without ever manually interacting with the container. Even though you never have to interact with the container to write this code, it is managing the injection of these dependencies behind the scenes.

**So, when would you ever manually interact with the container?** Let's examine two situations.

First, if you write a class that implements an interface and you wish to type-hint that interface on a class constructor or method, you must [tell the container how to resolve that interface](#binding-interfaces-to-implementations). Secondly, if you are writing a Venusian package that you plan to share with other Venusian developers, you may need to bind your package's services into the container.

## Binding

### Binding Basics

<a id="simple-bindings"></a>
#### Simple Bindings

Almost all of your service container bindings will be registered within [service providers](/docs/{{version}}/framework/architecture-concepts/providers), so most of these examples will demonstrate using the container in that context.

Within a service provider, you always have access to the container via the `$this->app` property. We can register a binding using the `bind` method, passing the class or interface name that we wish to register along with a closure that returns an instance of the class:

```php
use App\Services\Transistor;
use App\Services\PodcastParser;
use Voyager\Contracts\Core\FrameworkCore;

$this->app->bind(Transistor::class, function (FrameworkCore $app) {
    return new Transistor($app->make(PodcastParser::class));
});
```

Note that we receive the container itself as an argument to the resolver. We can then use the container to resolve sub-dependencies of the object we are building. The resolver also receives, as its second argument, the array of parameters passed to [`make`](#the-make-method):

```php
$this->app->bind(Transistor::class, function (FrameworkCore $app, array $parameters) {
    return new Transistor($app->make(PodcastParser::class), $parameters['id'] ?? 0);
});
```

As mentioned, you will typically be interacting with the container within service providers; however, if you would like to interact with the container outside of a service provider, you may do so via the `app` helper, which returns the container when called without arguments:

```php
use App\Services\Transistor;
use Voyager\Contracts\Core\FrameworkCore;

app()->bind(Transistor::class, function (FrameworkCore $app) {
    // ...
});
```

For convenience, you may omit providing the class or interface name that you wish to register as a separate argument and instead allow Venusian to infer the type from the return type of the closure you provide to the `bind` method:

```php
$this->app->bind(function (FrameworkCore $app): Transistor {
    return new Transistor($app->make(PodcastParser::class));
});
```

> [!NOTE]
> There is no need to bind classes into the container if they do not depend on any interfaces. The container does not need to be instructed on how to build these objects, since it can automatically resolve these objects using reflection.

#### Binding A Singleton

The `registerSingleton` method binds a class or interface into the container that should only be resolved one time. Once a singleton binding is resolved, the same object instance will be returned on subsequent calls into the container:

```php
use App\Services\Transistor;
use App\Services\PodcastParser;
use Voyager\Contracts\Core\FrameworkCore;

$this->app->registerSingleton(Transistor::class, function (FrameworkCore $app) {
    return new Transistor($app->make(PodcastParser::class));
});
```

#### Singleton Attribute

Alternatively, you may mark a class with the `#[Singleton]` attribute to indicate to the container that it should be resolved one time:

```php
<?php

namespace App\Services;

use Voyager\Contracts\Vessel\Attributes\Singleton;

#[Singleton]
class Transistor
{
    // ...
}
```

#### Binding Scoped Singletons

The `scoped` method binds a class or interface into the container that should only be resolved one time within a given lifecycle. While this method is similar to the `registerSingleton` method, instances registered using the `scoped` method are dropped whenever the container's `forgetScopedInstances` method is called. The [queue worker](/docs/{{version}}/framework/digging-deeper/queues) calls it after every job, so each job starts with fresh scoped instances:

```php
use App\Services\Transistor;
use App\Services\PodcastParser;
use Voyager\Contracts\Core\FrameworkCore;

$this->app->scoped(Transistor::class, function (FrameworkCore $app) {
    return new Transistor($app->make(PodcastParser::class));
});
```

If your own long-running loop processes units of work, you may call `forgetScopedInstances` yourself between them:

```php
app()->forgetScopedInstances();
```

#### Scoped Attribute

Alternatively, you may mark a class with the `#[Scoped]` attribute to indicate to the container that it should be resolved one time per lifecycle:

```php
<?php

namespace App\Services;

use Voyager\Contracts\Vessel\Attributes\Scoped;

#[Scoped]
class Transistor
{
    // ...
}
```

#### Binding Instances

You may also bind an existing object instance into the container using the `registerInstance` method. The given instance will always be returned on subsequent calls into the container:

```php
use App\Services\Transistor;
use App\Services\PodcastParser;

$service = new Transistor(new PodcastParser);

$this->app->registerInstance(Transistor::class, $service);
```

#### Aliases

The `alias` method registers another name for a binding. Resolving the alias resolves the original:

```php
$this->app->registerSingleton(Transistor::class);

$this->app->alias(Transistor::class, 'transistor');

$transistor = $this->app->make('transistor');
```

<a id="binding-interfaces-to-implementations"></a>
### Binding Interfaces to Implementations

A very powerful feature of the service container is its ability to bind an interface to a given implementation. For example, let's assume we have an `EventPusher` interface and a `RedisEventPusher` implementation. Once we have coded our `RedisEventPusher` implementation of this interface, we can register it with the service container like so:

```php
use App\Contracts\EventPusher;
use App\Services\RedisEventPusher;

$this->app->bind(EventPusher::class, RedisEventPusher::class);
```

This statement tells the container that it should inject the `RedisEventPusher` when a class needs an implementation of `EventPusher`. Now we can type-hint the `EventPusher` interface in the constructor of a class that is resolved by the container. Remember, commands, listeners, sketches, and various other types of classes within Venusian applications are always resolved using the container:

```php
use App\Contracts\EventPusher;

/**
 * Create a new class instance.
 */
public function __construct(
    protected EventPusher $pusher,
) {}
```

### Contextual Binding

Sometimes you may have two classes that utilize the same interface, but you wish to inject different implementations into each class. For example, two services may depend on different implementations of the `Voyager\Contracts\Filesystem\Filesystem` [contract](/docs/{{version}}/framework/digging-deeper/contracts). Venusian provides a simple, fluent interface for defining this behavior:

```php
use App\Services\PhotoArchiver;
use App\Services\UploadArchiver;
use App\Services\VideoArchiver;
use Voyager\Contracts\Filesystem\Filesystem;

$this->app->when(PhotoArchiver::class)
    ->needs(Filesystem::class)
    ->give(function () {
        return app('filesystem')->disk('local');
    });

$this->app->when([VideoArchiver::class, UploadArchiver::class])
    ->needs(Filesystem::class)
    ->give(function () {
        return app('filesystem')->disk('s3');
    });
```

### Contextual Attributes

You may write your own contextual binding attributes, which let a class declare where a constructor argument comes from without any contextual binding in your service providers. A contextual attribute implements the `Voyager\Contracts\Vessel\ContextualAttribute` interface and provides a `resolve` method. The container calls `resolve` with the attribute instance and the container, and injects whatever it returns. In the example below, we will write an attribute that injects a configuration value:

```php
<?php

namespace App\Attributes;

use Attribute;
use Voyager\Contracts\Vessel\ContextualAttribute;
use Voyager\Contracts\Vessel\TheServiceContainer;

#[Attribute(Attribute::TARGET_PARAMETER)]
class Config implements ContextualAttribute
{
    /**
     * Create a new attribute instance.
     */
    public function __construct(public string $key, public mixed $default = null)
    {
    }

    /**
     * Resolve the configuration value.
     */
    public static function resolve(self $attribute, TheServiceContainer $container): mixed
    {
        return $container->make('config')->get($attribute->key, $attribute->default);
    }
}
```

Once defined, the attribute may be placed on any constructor parameter of a class the container builds:

```php
use App\Attributes\Config;

class ReportAggregator
{
    public function __construct(
        #[Config('app.name')] protected string $appName,
    ) {}
}
```

If a contextual attribute also defines an `after` method, the container calls it with the attribute, the resolved value, and the container, once that value has been resolved.

### Binding Primitives

Sometimes you may have a class that receives some injected classes, but also needs an injected primitive value such as an integer. You may easily use contextual binding to inject any value your class may need. Pass `give` a string, or a closure that returns the value:

```php
use App\Services\UserImporter;

$this->app->when(UserImporter::class)
    ->needs('$variableName')
    ->give(fn () => $value);
```

If you need to inject a value from one of your application's configuration files, you may use the `giveConfig` method:

```php
$this->app->when(ReportAggregator::class)
    ->needs('$appName')
    ->giveConfig('app.name');
```

### Binding Typed Variadics

Occasionally, you may have a class that receives an array of typed objects using a variadic constructor argument:

```php
<?php

use App\Services\Filter;
use App\Services\Logger;

class Firewall
{
    /**
     * The filter instances.
     *
     * @var array
     */
    protected $filters;

    /**
     * Create a new class instance.
     */
    public function __construct(
        protected Logger $logger,
        Filter ...$filters,
    ) {
        $this->filters = $filters;
    }
}
```

Using contextual binding, you may resolve this dependency by providing the `give` method with a closure that returns an array of resolved `Filter` instances:

```php
$this->app->when(Firewall::class)
    ->needs(Filter::class)
    ->give(function (FrameworkCore $app) {
          return [
              $app->make(NullFilter::class),
              $app->make(ProfanityFilter::class),
              $app->make(TooLongFilter::class),
          ];
    });
```

For convenience, you may also just provide an array of class names to be resolved by the container whenever `Firewall` needs `Filter` instances:

```php
$this->app->when(Firewall::class)
    ->needs(Filter::class)
    ->give([
        NullFilter::class,
        ProfanityFilter::class,
        TooLongFilter::class,
    ]);
```

## Resolving

<a id="the-make-method"></a>
### The `make` Method

You may use the `make` method to resolve a class instance from the container. The `make` method accepts the name of the class or interface you wish to resolve:

```php
use App\Services\Transistor;

$transistor = $this->app->make(Transistor::class);
```

If some of your class's dependencies are not resolvable via the container, you may inject them by passing them as an associative array as the second argument to `make`. For example, we may manually pass the `$id` constructor argument required by the `Transistor` service:

```php
use App\Services\Transistor;

$transistor = $this->app->make(Transistor::class, ['id' => 1]);
```

When the class is bound with a closure, those parameters arrive as the closure's second argument, as shown in [simple bindings](#simple-bindings).

The `isBound` method may be used to determine if a class or interface has been explicitly bound in the container, and the `isResolved` method tells you whether it has been resolved yet:

```php
if ($this->app->isBound(Transistor::class)) {
    // ...
}
```

If you are outside of a service provider in a location of your code that does not have access to the `$app` variable, you may use the `app` [helper](/docs/{{version}}/framework/digging-deeper/helpers) to resolve a class instance from the container:

```php
use App\Services\Transistor;

$transistor = app(Transistor::class);

$transistor = app(Transistor::class, ['id' => 1]);
```

The container also implements `ArrayAccess`, so a binding may be read or registered by key:

```php
$config = app()['config'];
```

If you would like to have the Venusian container instance itself injected into a class that is being resolved by the container, you may type-hint the `Voyager\Contracts\Vessel\TheServiceContainer` contract on your class's constructor. The `Voyager\Contracts\Core\FrameworkCore` contract, `Voyager\Core\RenderedInstance` and `Voyager\Vessel\ControlPanel` resolve to the same application instance:

```php
use Voyager\Contracts\Vessel\TheServiceContainer;

/**
 * Create a new class instance.
 */
public function __construct(
    protected TheServiceContainer $container,
) {}
```

### Resolving Framework Services

Venusian has no facades. Each framework service is bound under a short container key, and its classes and contracts are aliased to that key, so `app('cache')`, `app(\Voyager\Contracts\Cache\Factory::class)` and a constructor type-hinted with that contract all receive the same object:

| Key | Service |
| --- | --- |
| `app` | The application and container itself |
| `config` | Configuration repository |
| `signals` | Signal dispatcher |
| `log` | Log manager |
| `cache` / `cache.store` | Cache manager / default cache store |
| `db` / `db.connection` / `db.schema` | Database manager / default connection / schema builder |
| `files` | Local filesystem helper |
| `filesystem` / `filesystem.disk` / `filesystem.cloud` | Filesystem manager / default disk / cloud disk |
| `queue` / `queue.connection` / `queue.failer` | Queue manager / default connection / failed job provider |
| `broadcast` / `broadcast.connection` | Broadcast manager / default broadcaster |
| `hash` / `hash.driver` | Hash manager / default hasher |
| `encrypter` | Encrypter |
| `http` / `http.async` | HTTP client factory / async HTTP manager |
| `redis` / `redis.connection` | Redis manager / default connection |
| `concurrency` | Concurrency manager |
| `pipeline` | A new pipeline |
| `event-loop` | The IOPools event loop |

```php
$value = app('cache')->get('key');

app('log')->info('Podcast imported.');
```

### Automatic Injection

Alternatively, and importantly, you may type-hint the dependency in the constructor of a class that is resolved by the container, including signal listeners and sketches, or in the `handle` method of Computer commands and queued jobs. In practice, this is how most of your objects should be resolved by the container.

For example, you may type-hint a service defined by your application in a listener's constructor. The service will automatically be resolved and injected into the class:

```php
<?php

namespace App\Listeners;

use App\Services\AppleMusic;
use App\Signals\PodcastPublished;

class CachePodcastDetails
{
    /**
     * Create the listener.
     */
    public function __construct(
        protected AppleMusic $apple,
    ) {}

    /**
     * Handle the signal.
     */
    public function handle(PodcastPublished $signal): void
    {
        $this->apple->findPodcast($signal->id);
    }
}
```

## Method Invocation and Injection

Sometimes you may wish to invoke a method on an object instance while allowing the container to automatically inject that method's dependencies. For example, given the following class:

```php
<?php

namespace App;

use App\Services\AppleMusic;

class PodcastStats
{
    /**
     * Generate a new podcast stats report.
     */
    public function generate(AppleMusic $apple): array
    {
        return [
            // ...
        ];
    }
}
```

You may invoke the `generate` method via the container like so:

```php
use App\PodcastStats;

$stats = app()->call([new PodcastStats, 'generate']);
```

The `call` method accepts any PHP callable, as well as a `Class@method` string, and an array of parameters to pass alongside the injected ones. The container's `call` method may even be used to invoke a closure while automatically injecting its dependencies:

```php
use App\Services\AppleMusic;

$result = app()->call(function (AppleMusic $apple) {
    // ...
});

$stats = app()->call('App\PodcastStats@generate');
```

## Resolving Callbacks

The service container runs callbacks each time it resolves an object. You may register them using the `resolving` method:

```php
use App\Services\Transistor;
use Voyager\Contracts\Core\FrameworkCore;

$this->app->resolving(Transistor::class, function (Transistor $transistor, FrameworkCore $app) {
    // Called when container resolves objects of type "Transistor"...
});

$this->app->resolving(function (mixed $object, FrameworkCore $app) {
    // Called when container resolves object of any type...
});
```

As you can see, the object being resolved will be passed to the callback, allowing you to set any additional properties on the object before it is given to its consumer. The `afterResolving` method takes the same arguments and runs after every `resolving` callback has run.

The `afterResolvingAttribute` method runs a callback whenever the container builds a class, or injects a parameter, that carries the given attribute. The callback receives the attribute instance, the object, and the container:

```php
use App\Attributes\Audited;

$this->app->afterResolvingAttribute(Audited::class, function (Audited $attribute, object $object, FrameworkCore $app) {
    // ...
});
```

## PSR-11

Venusian's service container implements the [PSR-11](https://github.com/php-fig/fig-standards/blob/master/accepted/PSR-11-container.md) interface. Therefore, you may type-hint the PSR-11 container interface to obtain an instance of the Venusian container:

```php
use App\Services\Transistor;
use Psr\Container\ContainerInterface;

public function handle(ContainerInterface $container): void
{
    $service = $container->get(Transistor::class);

    // ...
}
```

An exception is thrown if the given identifier can't be resolved. The exception will be an instance of `Psr\Container\NotFoundExceptionInterface` if the identifier was never bound. If the identifier was bound but was unable to be resolved, an instance of `Psr\Container\ContainerExceptionInterface` will be thrown.
