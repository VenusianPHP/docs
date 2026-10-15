# Service Providers

Service providers are the central place of all Venusian application bootstrapping.

## Introduction

Service providers are the central place of all Venusian application bootstrapping. Your own application, as well as all of Venusian's core services, are bootstrapped via service providers.

But, what do we mean by "bootstrapped"? In general, we mean **registering** things, including registering service container bindings, signal listeners, and Computer commands. Service providers are the central place to configure your application.

Venusian uses dozens of service providers internally to bootstrap its core services, such as the queue, cache, database, and others. Many of these providers are "deferred" providers, meaning they will not be loaded on every run, but only when the services they provide are actually needed.

All user-defined service providers are registered in the `bootstrap/providers.php` file. In the following documentation, you will learn how to write your own service providers and register them with your Venusian application.

## Writing Service Providers

All service providers extend the `Voyager\NutsAndBolts\ServiceProvider` class. Most service providers contain a `register` and a `boot` method. Within the `register` method, you should **only bind things into the [service container](/docs/{{version}}/framework/architecture-concepts/container)**. You should never attempt to register any signal listeners or any other piece of functionality within the `register` method.

The Computer CLI can generate a new provider via the `make:provider` command. Venusian will automatically register your new provider in your application's `bootstrap/providers.php` file:

```shell
php computer make:provider RiakServiceProvider
```

### The Register Method

As mentioned previously, within the `register` method, you should only bind things into the [service container](/docs/{{version}}/framework/architecture-concepts/container). You should never attempt to register any signal listeners or any other piece of functionality within the `register` method. Otherwise, you may accidentally use a service that is provided by a service provider which has not loaded yet.

Let's take a look at a basic service provider. Within any of your service provider methods, you always have access to the `$app` property which provides access to the service container:

```php
<?php

namespace App\Providers;

use App\Services\Riak\Connection;
use Voyager\Contracts\Core\FrameworkCore;
use Voyager\NutsAndBolts\ServiceProvider;

class RiakServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->registerSingleton(Connection::class, function (FrameworkCore $app) {
            return new Connection(config('riak'));
        });
    }
}
```

This service provider only defines a `register` method, and uses that method to define an implementation of `App\Services\Riak\Connection` in the service container. If you're not yet familiar with Venusian's service container, check out [its documentation](/docs/{{version}}/framework/architecture-concepts/container).

#### The `bindings` and `singletons` Properties

If your service provider registers many simple bindings, you may wish to use the `bindings` and `singletons` properties instead of manually registering each container binding. When the service provider is loaded by the framework, it will automatically check for these properties and register their bindings:

```php
<?php

namespace App\Providers;

use App\Contracts\DowntimeNotifier;
use App\Contracts\ServerProvider;
use App\Services\DigitalOceanServerProvider;
use App\Services\PingdomDowntimeNotifier;
use App\Services\ServerToolsProvider;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * All of the container bindings that should be registered.
     *
     * @var array
     */
    public $bindings = [
        ServerProvider::class => DigitalOceanServerProvider::class,
    ];

    /**
     * All of the container singletons that should be registered.
     *
     * @var array
     */
    public $singletons = [
        DowntimeNotifier::class => PingdomDowntimeNotifier::class,
        ServerProvider::class => ServerToolsProvider::class,
    ];
}
```

An entry in `singletons` without a key registers the class as a singleton of itself:

```php
public $singletons = [
    ServerToolsProvider::class,
];
```

### The Boot Method

So, what if we need to register a [signal](/docs/{{version}}/framework/digging-deeper/signals) listener within our service provider? This should be done within the `boot` method. **This method is called after all other service providers have been registered**, meaning you have access to all other services that have been registered by the framework:

```php
<?php

namespace App\Providers;

use App\Listeners\SendPodcastNotification;
use App\Signals\PodcastProcessed;
use Voyager\NutsAndBolts\ServiceProvider;

class SignalListenerServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        $this->app['signals']->listen(PodcastProcessed::class, SendPodcastNotification::class);
    }
}
```

#### Boot Method Dependency Injection

You may type-hint dependencies for your service provider's `boot` method. The [service container](/docs/{{version}}/framework/architecture-concepts/container) will automatically inject any dependencies you need:

```php
use App\Listeners\SendPodcastNotification;
use App\Signals\PodcastProcessed;
use Voyager\Contracts\Signals\SignalDispatcher;

/**
 * Bootstrap any application services.
 */
public function boot(SignalDispatcher $signals): void
{
    $signals->listen(PodcastProcessed::class, SendPodcastNotification::class);
}
```

## Registering Providers

All service providers are registered in the `bootstrap/providers.php` configuration file. This file returns an array that contains the class names of your application's service providers:

```php
<?php

return [
    App\Providers\AppServiceProvider::class,
];
```

When you invoke the `make:provider` Computer command, Venusian will automatically add the generated provider to the `bootstrap/providers.php` file. However, if you have manually created the provider class, you should manually add the provider class to the array:

```php
<?php

return [
    App\Providers\AppServiceProvider::class,
    App\Providers\SignalListenerServiceProvider::class, // [tl! add]
];
```

You may also pass providers to `withProviders` in your application's `bootstrap/app.php` file. They are merged with the ones listed in `bootstrap/providers.php`:

```php
use Voyager\Core\Bootstrap\Exceptions;
use Voyager\Core\VenusianVoyager;

return VenusianVoyager::setup(base_path: dirname(__DIR__))
    ->withExceptions(function (Exceptions $exceptions): void {})
    ->withProviders([
        App\Providers\RiakServiceProvider::class,
    ])
    ->create();
```

Packages register their providers through package discovery: a package lists them under `extra.venusian.providers` in its `composer.json`, and Venusian records them in its package manifest the first time it boots without one. The `package:discover` Computer command rebuilds that manifest. Venusian registers its own providers first, then discovered package providers, then your application's.

### Framework Providers

The framework's own providers are listed in the `providers` key of your application's `config/app.php` file. `ServiceProvider::defaultProviders()` returns the default list, which you may extend with `merge`, trim with `except`, or swap entries in with `replace`:

```php
use Voyager\NutsAndBolts\ServiceProvider;

'providers' => ServiceProvider::defaultProviders()
    ->except([
        \Voyager\Broadcasting\BroadcastServiceProvider::class,
    ])
    ->replace([
        \Voyager\Cache\CacheServiceProvider::class => \App\Providers\CacheServiceProvider::class,
    ])
    ->merge([
        // Package Service Providers...
    ])
    ->toArray(),
```

## Deferred Providers

If your provider is **only** registering bindings in the [service container](/docs/{{version}}/framework/architecture-concepts/container), you may choose to defer its registration until one of the registered bindings is actually needed. Deferring the loading of such a provider will improve the performance of your application, since it is not loaded from the filesystem on every run.

Venusian compiles and stores a list of all of the services supplied by deferred service providers, along with the name of its service provider class, in `bootstrap/cache/services.php` (a packaged app keeps it under its data directory). Then, only when you attempt to resolve one of these services does Venusian load the service provider.

To defer the loading of a provider, implement the `Voyager\Contracts\NutsAndBolts\DeferrableProvider` interface and define a `provides` method. The `provides` method should return the service container bindings registered by the provider:

```php
<?php

namespace App\Providers;

use App\Services\Riak\Connection;
use Voyager\Contracts\Core\FrameworkCore;
use Voyager\Contracts\NutsAndBolts\DeferrableProvider;
use Voyager\NutsAndBolts\ServiceProvider;

class RiakServiceProvider extends ServiceProvider implements DeferrableProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->registerSingleton(Connection::class, function (FrameworkCore $app) {
            return new Connection($app['config']['riak']);
        });
    }

    /**
     * Get the services provided by the provider.
     *
     * @return array<int, string>
     */
    public function provides(): array
    {
        return [Connection::class];
    }
}
```

A deferred provider may also define a `when` method returning the signals that should load it. When one of those signals is dispatched, Venusian registers the provider:

```php
use App\Signals\RiakRequested;

/**
 * Get the signals that trigger this service provider to register.
 *
 * @return array<int, string>
 */
public function when(): array
{
    return [RiakRequested::class];
}
```
