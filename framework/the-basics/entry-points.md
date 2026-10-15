# Entry Points

How a Venusian application starts: the computer and rocket front doors, the bootstrap/app.php file that configures the application, the boot sequence each front door runs, and Probe.

## Introduction

A Venusian application has no web server in front of it and no single process that serves requests. Instead, it has two front doors in its root directory, and every run of your application comes in through one of them:

| Front Door | Command | Runs | Kernel |
| --- | --- | --- | --- |
| Computer | `php computer` | [Computer commands](/docs/{{version}}/framework/digging-deeper/computer): generators, migrations, queue workers, your own commands, and Probe | `Voyager\Core\Console\Kernel` |
| Rocket | `php rocket` | [Sketches](/docs/{{version}}/framework/the-basics/sketches): long-running programs driven by the event loop, one frame at a time | `Voyager\Core\Sketches\Kernel` |

Both front doors load the same `bootstrap/app.php` file, so they build the same application with the same configuration, container bindings and service providers. What differs is the kernel each one hands its input to, and the few steps that kernel adds before it runs your code.

Understanding how a run starts makes the rest of the framework less mysterious. This page follows a run from the front door to your code.

## The Front Doors

### The `computer` File

The `computer` file is a small PHP script. It records the start time, loads Composer's autoloader, builds the application from `bootstrap/app.php`, and hands the command line to the application's `handleInquiry` method:

```php
#!/usr/bin/env php
<?php

use Voyager\Core\RenderedInstance;
use Symfony\Component\Console\Input\ArgvInput;

define('VENUSIAN_START', microtime(true));

// Register the Composer autoloader...
require __DIR__.'/vendor/autoload.php';

/** @var RenderedInstance $app */
$app = require_once __DIR__.'/bootstrap/app.php';

$status = $app->handleInquiry(new ArgvInput);

exit($status);
```

`handleInquiry` resolves the console kernel from the container, runs the command, calls the kernel's `terminate` method, and returns the command's exit code, which becomes the exit code of the process.

### The `rocket` File

The `rocket` file has the same shape. The only difference is the last step: it calls `handleSketch`, which resolves the sketch kernel instead:

```php
#!/usr/bin/env php
<?php

use Symfony\Component\Console\Input\ArgvInput;

define('VENUSIAN_START', microtime(true));

require __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';

$status = $app->handleSketch(new ArgvInput);

exit($status);
```

Rocket's console lists your sketches as its commands, and running one of them hands the sketch to the sketch runner, which drives its `loop` method on the event loop until it stops. Everything about writing and running sketches is on the [Sketches](/docs/{{version}}/framework/the-basics/sketches) page:

```shell
php rocket list

php rocket stargazer
```

## The Application File

The `bootstrap/app.php` file builds your application and returns it. A new application's file looks like this:

```php
<?php

use Voyager\Core\Bootstrap\Exceptions;
use Voyager\Core\VenusianVoyager;

return VenusianVoyager::setup(base_path: dirname(__DIR__))
    ->withExceptions(function (Exceptions $exceptions): void {})
    ->withSketches([__DIR__.'/../app/Runner/Sketches'])
    ->create();
```

`VenusianVoyager::setup` creates the application instance, a `Voyager\Core\RenderedInstance`, for the given base path, and returns a `Voyager\Core\Bootstrap\ConfigFactory` that you configure with a chain of `with*` calls. When you leave out `base_path`, Venusian uses the `APP_BASE_PATH` environment variable if it is set, and otherwise the directory that holds Composer's `vendor` directory.

Before it returns the factory, `setup` already calls `withKernels`, `withSignals`, `withCommands`, `withSketches` and `withProviders` with their defaults, so a bare `VenusianVoyager::setup()->create()` is a working application. Your own calls add to those defaults. The final `create` call returns the configured application.

### Kernels

The `withKernels` method binds the two kernels as singletons: `Voyager\Contracts\Console\Kernel` to `Voyager\Core\Console\Kernel`, and `Voyager\Contracts\Sketches\Kernel` to `Voyager\Core\Sketches\Kernel`. `setup` calls it for you. To use a kernel of your own, bind your class to the contract in the container before the front door resolves it.

### Service Providers

The `withProviders` method adds service providers to the application. The providers you pass are registered along with those listed in `bootstrap/providers.php`, which is where the `make:provider` command adds new providers:

```php
->withProviders([
    App\Providers\TelemetryServiceProvider::class,
])
```

Pass `false` as the second argument to stop Venusian from reading `bootstrap/providers.php`. See [Registering Providers](/docs/{{version}}/framework/architecture-concepts/providers#registering-providers) for the full picture, including the framework provider list in `config/app.php`.

### Commands

The `withCommands` method registers Computer commands by their class names:

```php
->withCommands([
    App\Console\Commands\ImportReadings::class,
])
```

Commands you generate with `make:command` are placed in `app/Console/Commands`; list each one here, or register it from a service provider, as described in [Registering Commands](/docs/{{version}}/framework/digging-deeper/computer#registering-commands).

### Sketches

The `withSketches` method tells Rocket where your sketches live. Each entry is a directory to scan or a sketch class name. `setup` always scans `app/Console/Sketches`, and the application skeleton adds `app/Runner/Sketches`:

```php
->withSketches([
    __DIR__.'/../app/Runner/Sketches',
    App\Devices\Thermometer::class,
])
```

See [Where Sketches Live](/docs/{{version}}/framework/the-basics/sketches#where-sketches-live) for how directories are scanned and how sketches are named.

### Signals

The `withSignals` method controls signal listener discovery. By default, Venusian discovers the listeners in your `app/Listeners` directory. Pass an array of directories to discover listeners somewhere else, or `false` to turn discovery off and register every listener yourself:

```php
->withSignals([
    __DIR__.'/../app/Telemetry/Listeners',
])

->withSignals(false)
```

See [Signal Discovery](/docs/{{version}}/framework/digging-deeper/signals#signal-discovery) for how discovered listeners are matched to signals.

### Exceptions

The `withExceptions` method binds the framework's exception handler, `Voyager\Core\Exceptions\Handler`, as the application's `Voyager\Contracts\Debug\ExceptionHandler`. The closure you pass receives a `Voyager\Core\Bootstrap\Exceptions` instance, through which you decide which exceptions are reported and how:

```php
use Voyager\Core\Bootstrap\Exceptions;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->dontReport(App\Exceptions\SensorOffline::class);
})
```

The closure runs the first time the handler is resolved. If your application file never calls `withExceptions`, `create` binds the same default handler for you, so an application built without it still has a handler to report to. A process worker boots your application through your `bootstrap/app.php`, so your `withExceptions` closure applies there too; a package without one is booted with `VenusianVoyager::setup($base_path)->create()` and gets the default handler. Everything the `Exceptions` object can do is on the [Error Handling](/docs/{{version}}/framework/the-basics/error-handling) page.

## The Boot Sequence

### Building the Application

Building the `RenderedInstance` does three things before any configuration is read:

1. It registers the application as the container's shared instance, under `app` and its class names, so `app()` returns it from anywhere. It also binds the package manifest, which lists the providers that installed packages declare.
2. It registers the base service providers, the ones everything else depends on: `Voyager\Signals\SignalServiceProvider` (`app('signals')`), `Voyager\Log\LogServiceProvider` (`app('log')`) and `Voyager\Log\ContextServiceProvider`.
3. It registers the core container aliases, so `app('config')`, `app('db')`, `app('event-loop')`, `app('cache')` and the rest resolve by their short names, their classes, and their contracts. The [Container](/docs/{{version}}/framework/architecture-concepts/container#resolving-framework-services) page lists them.

At this point the `.env` file has not been read and no configuration exists. That happens when a kernel bootstraps the application.

### Bootstrapping

When a front door hands its input to a kernel, the kernel runs a list of bootstrappers, once per process, in order:

| Bootstrapper | What It Does |
| --- | --- |
| `LoadEnvironmentVariables` | Loads `.env`, or `.env.[APP_ENV]` when the process has `APP_ENV` set and that file exists. Skipped when the configuration is cached. |
| `LoadConfiguration` | Loads the configuration cache, or the framework's configuration files with yours laid over them. Detects the environment from `app.env`, and sets PHP's default timezone from `app.timezone` (`UTC` when unset). |
| `HandleExceptions` | Turns PHP warnings and notices into `ErrorException`s, sends deprecations to the deprecation log channel, and installs the handlers that report uncaught exceptions and fatal errors. |
| `RegisterProviders` | Registers the framework providers from `config/app.php`, then the providers of installed packages, then your application's providers. Deferred providers are recorded, not loaded. |
| `BootProviders` | Calls each registered provider's `boot` method, then the application's `booted` callbacks. |

The sketch kernel runs the same list with one more step, `DeliverMailToSketches`, right after the configuration is loaded. It sets the event loop's mail handler (`io-pools.event_loop.mail_handlers.default`) to `sketch`, so [loop mail](/docs/{{version}}/framework/architecture-concepts/event-loop#loop-mail) is held for your sketch's next frame instead of going to the mail handler Computer uses (`signal` by default, which dispatches each piece of mail as a signal). The sketch kernel also marks the application as running under Rocket before any bootstrapper runs, which is what `app()->isRocketRunning()` reports; see [Telling Rocket and Computer Apart](/docs/{{version}}/framework/the-basics/sketches#telling-rocket-and-computer-apart).

After bootstrapping, both kernels load every remaining deferred provider, so commands registered by deferred providers appear in the command list. Then the kernel builds its console, Computer or Rocket, and runs the command or sketch you asked for.

> [!NOTE]
> `env:encrypt` and `env:decrypt` run every bootstrapper except `BootProviders`: providers are registered, but their `boot` methods never run for these two commands.

### Provider Order

The providers are registered in three groups. First the framework's own providers from the `providers` key in `config/app.php`, which `ServiceProvider::defaultProviders()` fills with the framework list. Then the providers that installed packages declare under `extra.venusian.providers` in their `composer.json`, which the `package:discover` command collects into the package manifest after every `composer install` or `composer update`. Last, your application's providers: the ones passed to `withProviders` and the ones in `bootstrap/providers.php`.

The framework list, in order, registers the bus, console support, cache, concurrency, database, migrations, filesystem, graph, hashing, encryption, HTTP client, log, queue, Redis, broadcasting, IOPools (the event loop and worker pools), pipeline, sketches and workflows providers. Because yours come last, your `register` and `boot` methods may use any framework service.

### Terminating

When the command or sketch returns, the front door calls the kernel's `terminate` method, which calls the application's `terminate` method before the process exits with the command's status. A sketch's own cleanup belongs in its `shutdown` method, which the sketch runner calls exactly once however the run ends; see [Continuing and Stopping](/docs/{{version}}/framework/the-basics/sketches#continuing-and-stopping).

### Errors While Starting

Each kernel wraps bootstrapping and the run in one `try` block. An exception thrown anywhere in that span, whether by a provider's `boot` method, a command or a sketch, is reported to the exception handler and rendered on the console, and the process exits with status `1`. An exception thrown outside a kernel, before or after it runs, reaches the uncaught-exception handler that `HandleExceptions` installed, which reports and renders it the same way. The [Error Handling](/docs/{{version}}/framework/the-basics/error-handling) page covers both.

An `.env` file that cannot be parsed stops the run before anything else: Venusian prints "The environment file is invalid!" and the parser's message to the error output, and exits with status `1`.

## Probe

Probe is the interactive front door. It is a REPL, built on [PsySH](https://github.com/bobthecow/psysh), that runs as a Computer command, so it boots your application exactly as any other command does, and then hands you a prompt inside it:

```shell
php computer probe
```

Every container binding, configuration value, helper and model is available at the prompt, which makes Probe the quickest way to try a query, inspect configuration, or poke at a service while you build:

```php
> config('app.id')
= "com.example.stargazer"

> app()->environment()
= "local"
```

You may run code without entering the shell by passing it to the `--execute` option, and include PHP files before the shell starts by passing them as arguments:

```shell
php computer probe --execute="config('app.name')"

php computer probe scratch/fixtures.php
```

Probe is installed with every new application as the `venusian/probe` package. Its configuration, command allow list and aliasing rules are covered under [Probe (REPL)](/docs/{{version}}/framework/digging-deeper/computer#probe-repl) on the Computer page.

> [!NOTE]
> Probe runs on the Computer side. `app()->isRocketRunning()` is `false` inside it, and loop mail goes to the configured mail handler (`signal` unless `IO_POOLS_MAIL_HANDLER` says otherwise) rather than being held for a sketch.
