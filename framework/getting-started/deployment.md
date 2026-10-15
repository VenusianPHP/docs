# Deployment

Shipping a Venusian application to the machines it runs on: packaged apps for consumer Macs and Linux desktops, edge devices, and long-running daemons, plus the caches, restarts and process monitors a source install needs.

## Introduction

A Venusian application is not served by a web server. It is a set of long-running processes, the sketches you start with `php rocket`, the queue workers you start with `php computer queue:work`, and the worker pools those processes spawn, and it runs where its work is: on a person's computer, on a device at the edge, or in the background as a daemon.

| Target | How it ships |
| --- | --- |
| A consumer Mac or Linux desktop | A [packaged application](#packaging-applications): a `.dmg` or `.deb` carrying its own PHP runtime. |
| An edge device, such as a Raspberry Pi or a Jetson | A packaged `.deb`, or the application's source [installed on the device](#running-from-source). |
| A daemon, with no window and no one watching | Either of the above, kept alive by a [process monitor](#running-as-a-daemon). |

## Packaging Applications

Packaging builds your application into something another machine installs and runs, with nothing else to set up: a signed `.app` in a `.dmg` for Apple Silicon Macs on macOS 14 and newer, or a `.deb` for Linux arm64 and x86_64 (Ubuntu 24.04 and newer, Debian 13, Raspberry Pi OS on trixie, JetPack 7). The packaged app carries its own compiled PHP runtime, so the user's machine needs no PHP.

The framework itself has no build commands. They come from the `venusian/build` package, a tool for the [`venusian` installer](/docs/{{version}}/framework/getting-started/installation). Install it with `install:sdk`, which runs `composer global require venusian/build` and adds the `build` command to the installer:

```shell
venusian install:sdk
```

### Building

Run `venusian build` from your application's root:

```shell
cd my-app

venusian build
```

The first run asks for the app's name, version, the sketch the app runs (only when there are several), and its author and one-line summary. Every answer is written to `build.json`, so the next run defaults to them. You may also pass the name, point at another application, or skip the questions:

```shell
venusian build "Night Sky"

venusian build --dir=../other-app

venusian build --no-interaction
```

Output lands in `build/`, which the build git-ignores. Before it finishes, each target runs the built binary once to boot the app, build its sketch and open its database, so an app that cannot start stops the build instead of failing on a user's first launch.

Building a macOS target needs an Apple Silicon Mac with the Xcode command line tools and `cmake`, `autoconf` and `pkg-config`; a macOS app's toolkit is AppKit. Building a Linux target needs Docker on a machine of the target's CPU, local or reached through a docker context. The [venusian/build README](https://github.com/VenusianPHP/build) covers build hosts, signing and notarizing.

### The Application Id

Every packaged app needs a reverse-DNS identity. The build reads it from `app.id` in your `config/app.php`, set by `APP_ID`, and refuses an application whose `config/app.php` has no `id` key. Give each application its own id before you ship it; see [The Application's Name and Id](/docs/{{version}}/framework/getting-started/configuration#the-applications-name-and-id):

```ini
APP_ID=com.example.stargazer
```

The build always writes `APP_ID` into the packaged app's `.env`. If `build.json` repeats the id, it must match `app.id` or the build stops.

### The `build.json` File

`build.json` sits at your application's root and is committed with it. It is optional: every key has a default, and an unknown key is refused by name. The common keys:

```json
{
    "id": null,
    "name": null,
    "version": "0.1.0",
    "build": 1,
    "sketch": null,
    "icon": null,
    "author": "",
    "extensions": [],
    "targets": [],
    "env": {},
    "env_except": []
}
```

| Key | Meaning |
| --- | --- |
| `id` | Reverse-DNS identity; when set, must equal `app.id`. |
| `name` | Display name; `null` uses `app.name`. |
| `version` | Starts with a digit; the `.deb` package version. |
| `build` | Whole number, one more each release; the `.app`'s bundle version. |
| `sketch` | The sketch the packaged app runs. |
| `icon` | A square PNG, at least 16 px. |
| `author` | `Name <email>`; required for Linux targets. |
| `extensions` | Extensions beyond the `ext-*` your `composer.lock` declares, such as `pdo_sqlite`, `imgdec`, or a Packagist php-ext package named in full, such as `phpredis/phpredis`. |
| `zts` | `true` or `false` for a thread-safe runtime; left out, the runtime follows the PHP running the build. |
| `targets` | Any of `macos-arm64`, `linux-arm64`, `linux-x86_64`; `[]` builds for the machine running the build. |
| `env`, `env_except` | Values laid over your `.env` in the packaged app, and `.env` keys left out of it, such as `DB_PASSWORD`. |

The build also accepts `summary`, `description`, `homepage`, `license`, `category` and macOS `permissions`. The README documents each one.

### Runtime PHP Version and Thread Safety

The packaged runtime is compiled from the newest release of the PHP minor version that runs `venusian build`: building with PHP 8.4 ships PHP 8.4.x. Its thread safety follows the same PHP: a ZTS PHP builds a ZTS runtime and an NTS PHP builds NTS, unless `build.json` sets `zts`. An extension that cannot build at that thread safety, such as `parallel`, which is ZTS only, stops the build by name.

The build scans your own code for calls into PHP extensions and compiles in the ones it finds, saying why. Calls found only in `vendor` are reported but not compiled in; add an extension to `extensions` when your application needs it.

### Databases in Packaged Apps

A packaged app's database is sqlite. A default connection other than `sqlite` stops the build; set `DB_CONNECTION=sqlite` in your `.env` or in `build.json` `env`. When the connection names `database/database.sqlite`, the build ships a fresh database migrated from `database/migrations`; your own database file never ships.

A packaged app cannot write inside its archive, so on first run Venusian copies its `storage` and `database` directories into the user's data directory and writes its caches there. See [Packaged Applications](/docs/{{version}}/framework/getting-started/configuration#packaged-applications) for the paths and how caches are refreshed after an upgrade.

## Running as a Daemon

A daemon is a sketch that runs in the background for as long as the machine is up: a sensor logger on a Pi, a queue worker, a bridge between a device and an API. Nothing in Venusian restarts a process after it exits, so a daemon runs under a process monitor that starts it at boot, restarts it when it exits, and stops it with `SIGTERM`.

Whatever starts it, a daemon needs `ext-pcntl` to stop cleanly: with it, `SIGTERM` or `SIGINT` stops the event loop, so the run returns, every stop hook runs and the worker pools shut their workers down instead of orphaning them. A second signal kills the process as if nothing were listening.

### A Packaged Daemon

A packaged app without a toolkit is headless: its `.deb` installs the runtime and archive under `/usr/lib/<name>/` and the command `/usr/bin/<name>`, which runs the `sketch` named in `build.json`, and no desktop entry. The build compiles in the extensions your own code calls, not the ones only the framework calls, so list `pcntl` in `build.json`:

```json
{
    "sketch": "sensor-logger",
    "extensions": ["pcntl"]
}
```

The `.deb` ships no service unit. Add one for systemd, for example `/etc/systemd/system/sensor-logger.service`:

```ini
[Unit]
Description=Sensor logger
After=network-online.target

[Service]
ExecStart=/usr/bin/sensor-logger
User=pi
Restart=always
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

The packaged app keeps its storage, database and caches in the data directory of the user it runs as (`$XDG_DATA_HOME/<Name>`, else `~/.local/share/<Name>`), so set `User` to the account that should own that data. Set `TimeoutStopSec` longer than your stop hooks take. Then enable and start it:

```shell
sudo systemctl enable --now sensor-logger
```

After installing a new `.deb`, restart the service so the new version runs:

```shell
sudo systemctl restart sensor-logger
```

### A Daemon From Source

On a device that runs your application from source, Supervisor is a process monitor for Linux that does the same job. The queue documentation shows how to [install and configure Supervisor](/docs/{{version}}/framework/digging-deeper/queues#supervisor-configuration) for `queue:work`. A sketch takes the same kind of program entry, pointed at `rocket`. For example, a `/etc/supervisor/conf.d/venusian-sketch.conf` that keeps the `hello-world` sketch running:

```ini
[program:venusian-sketch]
command=php /opt/app/rocket hello-world
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
user=app
redirect_stderr=true
stdout_logfile=/opt/app/storage/logs/sketch.log
stopwaitsecs=30
```

Supervisor stops a program with `SIGTERM`, which lets the loop stop cleanly. `stopasgroup` and `killasgroup` reach the sketch's pool workers too. Set `stopwaitsecs` longer than your stop hooks take.

After updating the source, restart the program:

```shell
sudo supervisorctl restart venusian-sketch
```

## Running From Source

An edge device you control, such as a Pi on a bench or a kiosk, can run your application straight from its source: copy or check out the application, run `composer install --no-dev`, and start its processes. The device then needs PHP itself, and the rest of this section applies. A packaged app needs none of it.

### Device Requirements

The device running your application needs the following minimum PHP version and extensions:

- PHP >= 8.4
- Ctype PHP Extension
- Filter PHP Extension
- Hash PHP Extension
- Mbstring PHP Extension
- OpenSSL PHP Extension
- PDO PHP Extension, plus the PDO driver for your database connection (`pdo_sqlite` for a new application's default `sqlite` connection)

#### Optional Extensions

Nothing else is required, but these extensions unlock parts of the framework. The framework checks for each one when it needs it:

| Extension | What it is for |
| --- | --- |
| `epoll` (Linux), `kqueue` (macOS) | The event loop's waiter backend. Without one the loop falls back to `select`; see [Choosing a Backend](/docs/{{version}}/framework/architecture-concepts/event-loop#choosing-a-backend). With `kqueue`, [worker pools](/docs/{{version}}/framework/architecture-concepts/event-loop#worker-pools) learn the moment a worker dies. |
| `pcntl` | Stops the event loop cleanly on `SIGINT` and `SIGTERM`, traps command signals, and enforces queue worker timeouts. |
| `posix` | Lets a timed-out queue worker kill itself. |
| `curl` | Both [async HTTP drivers](/docs/{{version}}/framework/digging-deeper/http-client#async-drivers). |
| `pcurl` | The `pcurl` async HTTP driver, whose sockets wait on the event loop instead of holding it. |
| `parallel` | The `thread-workers` pool. Needs a thread-safe (ZTS) PHP build. |
| `redis` | The phpredis [Redis](/docs/{{version}}/framework/database/redis) connector. |
| `fileinfo` | Detecting the MIME type of local files. |
| `intl` | Formatting numbers. |

`epoll`, `kqueue` and `pcurl` are first-party extensions. Install them through PIE, for the PHP binary that will run your application, with the `install:ext` command; see [Installing Extensions](/docs/{{version}}/framework/digging-deeper/computer#installing-extensions):

```shell
php computer install:ext epoll
```

### Directory Permissions

Venusian will need to write to the `bootstrap/cache` and `storage` directories, so you should ensure the user that runs your application's processes has permission to write to these directories. A sqlite application also writes its database file in `database/`.

### Optimization

When you deploy a new version of the source, there are files that should be cached. Run these commands after `composer install`, since `composer dump-autoload` deletes the configuration, service, package and signal caches.

#### Caching Configuration

You should run the `config:cache` Computer command during your deployment process:

```shell
php computer config:cache
```

This command combines all of your configuration files into a single cached file at `bootstrap/cache/config.php`, which greatly reduces the work the framework does every time a process starts. This matters most on small devices. See [Configuration Caching](/docs/{{version}}/framework/getting-started/configuration#configuration-caching) for details.

> [!WARNING]
> If you execute the `config:cache` command during your deployment process, you should be sure that you are only calling the `env` function from within your configuration files. Once the configuration has been cached, the `.env` file will not be loaded and the `env` function will only return process environment variables.

#### Caching Signals

If your application relies on [signal discovery](/docs/{{version}}/framework/digging-deeper/signals#signal-discovery-in-production), you should cache its signal to listener mappings during deployment:

```shell
php computer signal:cache
```

The `signal:clear` command removes the cache.

### Reloading Services

Long-running processes do not notice changes to your code. After deploying a new version of your application, every running sketch and queue worker must be restarted to use the new code.

Queue workers are restarted gracefully with the `queue:restart` command, which tells each worker to exit after it finishes its current job. See [Queue Workers and Deployment](/docs/{{version}}/framework/digging-deeper/queues#queue-workers-and-deployment):

```shell
php computer queue:restart
```

A sketch is restarted by stopping its process and starting it again; a sketch that runs [as a daemon](#running-as-a-daemon) is restarted through its process monitor.

### The Production Environment

The `env` option in your `config/app.php` file falls back to `production`, while a new application's `.env` sets `APP_ENV=local`. Set `APP_ENV=production` on the device that runs your application, or in `build.json` `env` for a packaged app.

In production, commands that destroy data, such as `migrate`, `migrate:fresh`, `migrate:refresh`, `migrate:reset`, `migrate:rollback` and `queue:clear`, ask you to confirm before they run. A deployment script has no one to answer, so pass `--force`:

```shell
php computer migrate --force
```
