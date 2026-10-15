# Installation

What Venusian is, how to install PHP and the venusian installer, create and run a new application, add the first-party PHP extensions, and set up its database.

## Meet Venusian

Venusian is a PHP framework for applications that run on an event loop. Instead of answering one request and exiting, a Venusian application is a long-running process: a command you run with `php computer`, a sketch that keeps going frame after frame with `php rocket`, worker pools that take blocking work off the loop, and, when you are ready to ship, a packaged build another machine installs and runs.

The same application can drive a desktop window, read a sensor on a Raspberry Pi, or talk to a database and an HTTP API, all without blocking the loop. A framework gives you the structure and starting point for that work, so you can focus on what your application does.

### Why Venusian?

#### Real Async I/O

The [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop) waits on file descriptors with the best backend your PHP has: `epoll` on Linux and `kqueue` on macOS when those extensions are loaded, and `stream_select` otherwise. The [HTTP client](/docs/{{version}}/framework/digging-deeper/http-client) can send asynchronous requests on the same loop, and with the `pcurl` extension it waits on curl's own sockets instead of polling them.

#### Programs That Keep Running

A [sketch](/docs/{{version}}/framework/the-basics/sketches) is a program with a boot step, a frame loop and a shutdown step. Rocket runs it on the event loop, and whatever the loop collects between frames arrives in the next frame as [loop mail](/docs/{{version}}/framework/the-basics/loop-mail).

#### Worker Pools

Work that would block the loop, such as a slow query, can be handed to a pool of worker processes, or to threads on a ZTS build of PHP with the `parallel` extension. The results come back as loop mail. The pools are configured in `config/io-pools.php`; see [concurrency](/docs/{{version}}/framework/digging-deeper/concurrency) and [offloading queries](/docs/{{version}}/framework/database/database#offloading-queries-to-worker-pools).

#### A Familiar Component Set

Venusian ships with a [service container](/docs/{{version}}/framework/architecture-concepts/container), [service providers](/docs/{{version}}/framework/architecture-concepts/providers), a [database](/docs/{{version}}/framework/database/database) layer with [migrations](/docs/{{version}}/framework/database/migrations) and the [Instrument ORM](/docs/{{version}}/framework/instrument-orm/instrument), [queues](/docs/{{version}}/framework/digging-deeper/queues), [cache](/docs/{{version}}/framework/digging-deeper/cache), [signals](/docs/{{version}}/framework/digging-deeper/signals), [broadcasting](/docs/{{version}}/framework/digging-deeper/broadcasting), [filesystems](/docs/{{version}}/framework/digging-deeper/filesystem), [collections](/docs/{{version}}/framework/digging-deeper/collections), [encryption](/docs/{{version}}/framework/security/encryption), [hashing](/docs/{{version}}/framework/security/hashing), [logging](/docs/{{version}}/framework/the-basics/logging), [workflows](/docs/{{version}}/framework/the-basics/workflows), the [Computer](/docs/{{version}}/framework/digging-deeper/computer) console and the Probe REPL.

#### Applications You Can Ship

The `venusian build` command, added by the [build tooling](#build-tooling), compiles an application into something another machine installs: a signed `.app` in a `.dmg` for Apple Silicon Macs, or a `.deb` for Linux on arm64 and x86_64. See [deployment](/docs/{{version}}/framework/getting-started/deployment) and [packaged applications](/docs/{{version}}/framework/getting-started/configuration#packaged-applications).

#### An Agent Ready Framework

Venusian's conventions put things in predictable places: commands in `app/Console/Commands`, sketches in `app/Runner/Sketches`, migrations in `database/migrations`, and generator commands that write each one from a stub. That consistency helps AI coding agents as much as it helps you. See [agentic development](/docs/{{version}}/framework/getting-started/agentic-development).

## Creating a Venusian Application

### Installing PHP and the Venusian Installer

Before creating your first Venusian application, make sure that your machine has [PHP](https://php.net) 8.4 or 8.5, [Composer](https://getcomposer.org/download/), and the Venusian installer. The framework requires these PHP extensions: `ctype`, `filter`, `hash`, `mbstring`, `openssl` and `pdo`, plus the PDO driver for your database. A new application uses SQLite, so it needs `pdo_sqlite`.

A few optional extensions unlock more of the framework:

| Extension | What it adds |
| --- | --- |
| `pcntl` | Signal handling: trapped command signals, queue worker timeouts, and loop stop signals |
| `posix` | Lets a timed-out worker kill itself |
| `curl` | The `curl` async HTTP driver |
| `parallel` | The thread worker pool (ZTS builds of PHP only) |
| `epoll`, `kqueue`, `pcurl` | Venusian's first-party extensions, offered by the installer (see [below](#installing-php-extensions)) |

Once PHP and Composer are installed, install the Venusian installer globally with Composer:

```shell
composer global require venusian/installer
```

Make sure Composer's global `vendor/bin` directory is on your `PATH` so the `venusian` command is available.

On each interactive run, the installer checks Packagist at most once a day for a newer `venusian/installer`, and offers to update itself and re-run your command on the new version. To skip the check, set `VENUSIAN_INSTALLER_NO_UPDATE_CHECK`:

```shell
VENUSIAN_INSTALLER_NO_UPDATE_CHECK=1 venusian new example-app
```

### Creating an Application

After you have installed PHP, Composer, and the Venusian installer, you are ready to create a new Venusian application:

```shell
venusian new example-app
```

The name may be a directory name, created under the current directory, `.` for the current directory, or an absolute path. The installer runs `composer create-project venusian/venusian:^0.10.0` into that directory. The skeleton's Composer scripts then copy `.env.example` to `.env`, write an `APP_KEY`, create the `database/database.sqlite` file, and discover your packages.

If you clone an existing Venusian application instead, the skeleton's `setup` Composer script does the same: it runs `composer install`, copies `.env.example` to `.env` if there is none, writes an `APP_KEY`, and creates the SQLite database file:

```shell
composer run setup
```

### Installing PHP Extensions

Once the application exists, an interactive `venusian new` asks whether to install Venusian's first-party PHP extensions:

| Extension | What it gives the framework | Offered on |
| --- | --- | --- |
| `epoll` | Event loop waiting on Linux | Linux |
| `kqueue` | Event loop waiting on macOS | macOS |
| `pcurl` | HTTP requests that run on the event loop | Everywhere but Windows |

An extension that belongs to another operating system, or that your PHP already loads, is shown but cannot be selected. Each selected extension is built and installed by [PIE](https://github.com/php/pie), run by the PHP binary that is running the installer, so the extensions land in that PHP. Building needs a C compiler and your PHP's development files (`phpize` and `php-config`).

If PIE is missing, the installer asks before downloading it to `~/.local/bin/pie`, and has PIE verify its own release attestation. PIE asks for your password itself when PHP's extension directory is not writable. A failed build is reported in the closing summary and does not undo the application: the framework runs without these extensions. A non-interactive run skips the step.

You may install the extensions later from inside your application with the `install:ext` Computer command, which offers the same three:

```shell
php computer install:ext

php computer install:ext pcurl
```

The installer's own `install:ext` command offers every first-party extension, including `epoll`, `kqueue` and `pcurl`, the `appkit`, `gtk` and `qt` toolkit bindings, `fb`, `rasterize`, `imgdec`, `posi` and `ftdi`. Without a terminal, name the extension and pass `--no-interaction`:

```shell
venusian install:ext

venusian install:ext imgdec

venusian install:ext posi --no-interaction
```

### Running Your Application

A new application ships with one sketch, `HelloWorld`, in `app/Runner/Sketches`. Rocket gives each sketch a command named after it, so you run it with:

```shell
cd example-app
php rocket hello-world
```

`php rocket list` lists your sketches, and `php computer list` lists the Computer commands. To explore your application interactively, start Probe:

```shell
php computer probe
```

When you are ready to write your own, `make:sketch` and `make:command` generate a new sketch or command:

```shell
php computer make:sketch Heartbeat

php computer make:command SyncReadings
```

## Initial Configuration

All configuration files for the Venusian framework are stored in the `config` directory. Each option is documented, so feel free to look through the files and get familiar with the options available to you.

Venusian needs almost no additional configuration out of the box. You are free to get started developing! However, you may wish to review `config/app.php`. Before you ship an application, give it its own `APP_ID`, the reverse-DNS identity the toolkit drivers and a packaged build share; see [the application's name and id](/docs/{{version}}/framework/getting-started/configuration#the-applications-name-and-id).

### Environment Based Configuration

Since many of Venusian's configuration values may vary depending on whether your application is running on your workstation or on the device it is deployed to, many important configuration values are defined using the `.env` file at the root of your application.

Your `.env` file should not be committed to your application's source control, since each developer or machine using your application could require a different environment configuration. Furthermore, this would be a security risk in the event an intruder gains access to your source control repository, since any sensitive credentials would be exposed.

> [!NOTE]
> For more information about the `.env` file and environment based configuration, check out the full [configuration documentation](/docs/{{version}}/framework/getting-started/configuration#environment-configuration).

### Databases and Migrations

Now that you have created your Venusian application, you probably want to store some data in a database. By default, your application's `.env` file sets `DB_CONNECTION=sqlite`, and the `sqlite` connection in `config/database.php` uses the `database/database.sqlite` file that was created with your application.

A new application has no migrations. Create one with `make:migration`, which writes it to `database/migrations`, then run your application's [database migrations](/docs/{{version}}/framework/database/migrations):

```shell
php computer make:migration create_readings_table

php computer migrate
```

The first `migrate` also creates the `migrations` table that records which migrations have run.

If you prefer to use another database driver, such as MySQL, MariaDB, PostgreSQL or SQL Server, update your `.env` file's `DB_*` variables. For example, to use MySQL:

```ini
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=venusian
DB_USERNAME=root
DB_PASSWORD=
```

If you choose a database other than SQLite, create the database first, then run `php computer migrate`. The skeleton also defines a `neo4j` connection, read from the `NEO4J_*` variables in `.env`; see the [database documentation](/docs/{{version}}/framework/database/database).

## Build Tooling

The `install:sdk` installer command installs `venusian/build` globally through Composer. The installer picks up the commands of any installed Composer package of type `venusian-tool`, so after `install:sdk` the `venusian` command has `build`:

```shell
venusian install:sdk

cd example-app
venusian build
```

`venusian build`, run inside a Venusian application, interviews you for the app's name, version and the sketch to run, then writes the result to `build/`. See [deployment](/docs/{{version}}/framework/getting-started/deployment) and [packaged applications](/docs/{{version}}/framework/getting-started/configuration#packaged-applications).

## Venusian and AI

If you work with an AI coding agent, the [agentic development](/docs/{{version}}/framework/getting-started/agentic-development) documentation covers how to give it the context it needs to follow Venusian's conventions.

## Next Steps

Now that you have created your Venusian application, you may be wondering what to learn next. First, we strongly recommend becoming familiar with how Venusian works by reading the following documentation:

- [Configuration](/docs/{{version}}/framework/getting-started/configuration)
- [Directory Structure](/docs/{{version}}/framework/getting-started/directory-structure)
- [Entry Points](/docs/{{version}}/framework/the-basics/entry-points)
- [The Event Loop](/docs/{{version}}/framework/architecture-concepts/event-loop)
- [Service Container](/docs/{{version}}/framework/architecture-concepts/container)
- [Service Providers](/docs/{{version}}/framework/architecture-concepts/providers)

How you want to use Venusian will dictate the next steps on your journey. If your application is a program that keeps running, read about [sketches](/docs/{{version}}/framework/the-basics/sketches), [loop mail](/docs/{{version}}/framework/the-basics/loop-mail), [workflows](/docs/{{version}}/framework/the-basics/workflows) and [concurrency](/docs/{{version}}/framework/digging-deeper/concurrency). If it is a set of commands that work with data, read about the [Computer console](/docs/{{version}}/framework/digging-deeper/computer), the [database](/docs/{{version}}/framework/database/database), the [Instrument ORM](/docs/{{version}}/framework/instrument-orm/instrument), and [queues](/docs/{{version}}/framework/digging-deeper/queues). When it is ready to leave your machine, read about [deployment](/docs/{{version}}/framework/getting-started/deployment).
