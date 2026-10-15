# Directory Structure

The files and directories a new Venusian application ships with, the ones Computer's generator commands create later, and what the framework writes into bootstrap/cache and storage.

## Introduction

The default Venusian application structure is intended to provide a good starting point for both large and small applications. But you are free to organize your application however you like. Venusian imposes almost no restrictions on where any given class is located, as long as Composer can autoload the class.

A new application, created with `venusian new` or `composer create-project venusian/venusian`, is small. It has no web root, no routes and no views: it is a set of [Computer](/docs/{{version}}/framework/digging-deeper/computer) commands and [sketches](/docs/{{version}}/framework/the-basics/sketches) that run on the [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop). Most of the directories described on this page are created later, the first time a generator command needs them.

## The Root Directory

A new application's root contains these directories:

| Directory | Contents |
| --- | --- |
| `app` | Your application's classes |
| `bootstrap` | The application file, the provider list and the framework's cache files |
| `config` | Configuration files |
| `database` | The SQLite database file and seeders |
| `storage` | Logs, file caches and files your application writes |
| `tests` | Pest tests |
| `vendor` | Composer dependencies |
| `.okf` | The application's knowledge bundle |

And these files:

| File | Purpose |
| --- | --- |
| `computer` | The [Computer](/docs/{{version}}/framework/digging-deeper/computer) console entry point, `php computer …` |
| `rocket` | The [sketch](/docs/{{version}}/framework/the-basics/sketches) entry point, `php rocket …` |
| `.env.example` | The environment template; Composer copies it to `.env` when the application is created |
| `composer.json` | Dependencies, autoloading and Composer scripts |
| `phpunit.xml` | Test suite configuration |
| `README.md`, `LICENSE` | The skeleton's readme and MIT license |
| `.editorconfig`, `.gitattributes`, `.gitignore` | Editor and Git settings |

How `computer` and `rocket` start the application is covered in [entry points](/docs/{{version}}/framework/the-basics/entry-points#the-front-doors).

### The App Directory

The `app` directory contains the core code of your application. We'll explore this directory in more detail below; almost all of the classes in your application will be in this directory.

### The Bootstrap Directory

The `bootstrap` directory contains the `app.php` file, which builds the application with `Voyager\Core\VenusianVoyager::setup()` and tells it where your sketches live, and the `providers.php` file, which lists your application's [service providers](/docs/{{version}}/framework/architecture-concepts/providers). Both are covered in [entry points](/docs/{{version}}/framework/the-basics/entry-points#the-application-file).

This directory also houses a `cache` directory for files the framework generates. It must stay writable:

| File | Written by |
| --- | --- |
| `packages.php` | `php computer package:discover`, which Composer runs after every install, update and `dump-autoload` |
| `config.php` | `php computer config:cache` |
| `signals.php` | `php computer signal:cache` |

Git ignores everything in `bootstrap/cache` except its `.gitignore`. Running `composer dump-autoload` deletes the configuration and signal caches before it rebuilds the package manifest. See [configuration caching](/docs/{{version}}/framework/getting-started/configuration#configuration-caching).

### The Config Directory

The `config` directory, as the name implies, contains all of your application's configuration files, one per framework component. It's a good idea to read through these files and familiarize yourself with the options available to you. See [configuration](/docs/{{version}}/framework/getting-started/configuration).

### The Database Directory

The `database` directory contains an empty `database.sqlite` file, the default SQLite database, and a `seeders` directory holding `DatabaseSeeder` in the `Database\Seeders` namespace. If the SQLite file is missing when the application is created, Composer creates it. Git ignores SQLite files in this directory. See [seeding](/docs/{{version}}/framework/database/seeding).

Two more directories appear here on demand:

- `database/migrations` is created by `make:migration`, and by the `make:cache-table`, `make:queue-table`, `make:queue-failed-table` and `make:queue-batches-table` commands. See [migrations](/docs/{{version}}/framework/database/migrations).
- `database/factories` is created by `make:factory`. Factories use the `Database\Factories` namespace, which a new application's `composer.json` does not autoload yet; see [generating factories](/docs/{{version}}/framework/instrument-orm/instrument-factories#generating-factories).

### The Storage Directory

The `storage` directory contains your logs, file caches, and other files generated by the framework. It is split into `app`, `framework`, and `logs` directories, and Git ignores their contents:

| Path | Used for |
| --- | --- |
| `storage/app/private` | The root of the default `local` [filesystem disk](/docs/{{version}}/framework/digging-deeper/filesystem) |
| `storage/app/public` | The root of the `public` disk |
| `storage/framework/cache/data` | The `file` [cache](/docs/{{version}}/framework/digging-deeper/cache) store, the default `CACHE_STORE` |
| `storage/framework/cache/failed-jobs.json` | Failed [queue](/docs/{{version}}/framework/digging-deeper/queues) jobs, with the default `file` failed job driver |
| `storage/framework/testing/disks` | Disks swapped in by `storage()->fake()` in [tests](/docs/{{version}}/framework/digging-deeper/filesystem#testing) |
| `storage/logs` | `venusian.log` from the `single` [log channel](/docs/{{version}}/framework/the-basics/logging), or dated `venusian-*.log` files from the `daily` channel |

A [packaged application](/docs/{{version}}/framework/getting-started/configuration#packaged-applications) cannot write inside its own phar, so it copies `storage` and `database` into the user's data directory the first time it runs and works from there.

### The Tests Directory

The `tests` directory contains your automated tests, written with [Pest](https://pestphp.com). A new application includes `tests/Unit/ExampleTest.php` and `tests/Feature/HelloWorldTest.php`, which runs `php rocket hello-world` in a child process and checks its output. `phpunit.xml` forces `APP_ENV=testing` and fails when the suite is empty. You may run your tests with Composer's `test` script or with Pest directly:

```shell
composer test

./vendor/bin/pest
```

The `make:test` command writes a feature test to `tests/Feature`, or a unit test to `tests/Unit` with `--unit`. A new application has no `tests/Pest.php`, so pass `--pest` to get a Pest test rather than a PHPUnit class:

```shell
php computer make:test SensorReadingTest --pest
```

### The Vendor Directory

The `vendor` directory contains your [Composer](https://getcomposer.org) dependencies: `venusian/framework` and [Probe](/docs/{{version}}/framework/digging-deeper/computer#probe-repl), plus Pest, Mockery and Faker for development.

### The `.okf` Directory

The `.okf` directory is the application's Open Knowledge Format bundle: markdown files that describe the application's layout, configuration and sketches, written for coding agents and for you. Start at `.okf/index.md`. See [agentic development](/docs/{{version}}/framework/getting-started/agentic-development#the-application-bundle).

### The Stubs Directory

This directory does not exist by default, but will be created for you if you execute the `stub:publish` command. It holds copies of the stubs the `make:*` commands generate classes from; once a stub is published, its command uses your copy. See [stub customization](/docs/{{version}}/framework/digging-deeper/computer#stub-customization).

### The Build Directory

This directory does not exist by default. The `venusian build` command, covered in [deployment](/docs/{{version}}/framework/getting-started/deployment), writes the packaged apps it builds into `build/`, with a `.gitignore` that ignores everything in it, and keeps its settings in a `build.json` file in your application's root.

## The App Directory

The majority of your application is housed in the `app` directory. By default, this directory is namespaced under `App` and is autoloaded by Composer using the [PSR-4 autoloading standard](https://www.php-fig.org/psr/psr-4/).

By default, the `app` directory contains the `Providers` and `Runner` directories. However, over time, a variety of other directories will be generated inside the app directory as you use the `make` Computer commands to generate classes. For example, the `app/Console` directory will not exist until you execute the `make:command` command to generate a command class.

Think of the `Console` and `Runner` directories as providing an API into the core of your application. Computer commands and sketches are both ways to start your application, but do not actually contain application logic. The `Console` directory contains your Computer commands, which do one job and exit, while the `Runner` directory contains your sketches, which keep running on the event loop.

> [!NOTE]
> Many of the classes in the `app` directory can be generated by Computer. To review the available commands, run `php computer list make` in your terminal.

### The Console Directory

This directory does not exist by default, but will be created for you if you execute the `make:command` command. `app/Console/Commands` holds your custom [Computer commands](/docs/{{version}}/framework/digging-deeper/computer#writing-commands). Each command is registered by its class name, with `withCommands` in `bootstrap/app.php` or a provider's `commands` method; see [registering commands](/docs/{{version}}/framework/digging-deeper/computer#registering-commands).

### The Exceptions Directory

This directory does not exist by default, but will be created for you if you execute the `make:exception` command. The `Exceptions` directory contains the custom exceptions for your application. See [error handling](/docs/{{version}}/framework/the-basics/error-handling).

### The Models Directory

This directory does not exist by default, and no command generates models: you create [Instrument model](/docs/{{version}}/framework/instrument-orm/instrument) classes by hand. By convention they live in `app/Models`, and model factories look there when they resolve the model a factory belongs to. Once `app/Models` exists, `make:factory` uses it for a factory's default model.

### The Providers Directory

The `Providers` directory contains the [service providers](/docs/{{version}}/framework/architecture-concepts/providers) for your application. Service providers bootstrap your application by binding services in the service container, registering signals, or performing any other tasks to prepare your application before a command or sketch runs.

In a new application, this directory already contains `AppServiceProvider`, listed in `bootstrap/providers.php`. The `make:provider` command writes new providers here and adds each one to `bootstrap/providers.php` for you.

### The Runner Directory

The `Runner/Sketches` directory contains your [sketches](/docs/{{version}}/framework/the-basics/sketches). It is the directory `bootstrap/app.php` passes to `withSketches`, so Rocket finds every sketch in it. A new application includes an abstract `Sketch` base class, which every generated sketch extends, and the `HelloWorld` sketch, which you may run with Rocket:

```shell
php rocket hello-world
```

The `make:sketch` command writes new sketches into this directory:

```shell
php computer make:sketch Heartbeat
```

### The Workflows Directory

This directory does not exist by default, but will be created for you if you execute the `make:node` command. The `Workflows` directory contains the nodes of your [workflows](/docs/{{version}}/framework/the-basics/workflows#generating-nodes), in the `App\Workflows` namespace.

### Other Generated Classes

The `make:class`, `make:enum`, `make:interface` and `make:trait` commands write directly into `app` unless a matching directory already exists. Create the directory first to collect them there:

| Command | Directories it looks for, in order |
| --- | --- |
| `make:class` | None; it always writes into `app` |
| `make:enum` | `app/Enums`, `app/Enumerations` |
| `make:interface` | `app/Contracts`, `app/Interfaces` |
| `make:trait` | `app/Concerns`, `app/Traits` |

[Signal discovery](/docs/{{version}}/framework/digging-deeper/signals#signal-discovery) scans `app/Listeners` for listeners. No command creates it; add the directory when you write your first listener.
