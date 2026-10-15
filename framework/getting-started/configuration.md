# Configuration

Venusian's configuration files, the .env file and env(), the app's name and reverse-DNS id, environment detection, the config cache, encrypted environment files, and where a packaged app keeps its data.

## Introduction

All of the configuration files for the Venusian framework are stored in your application's `config` directory. Each option is documented, so feel free to look through the files and get familiar with the options available to you.

These files let you configure things like your database connection, your log channels, your worker pools and event loop, the refresh rate of your sketches, and the encryption key your application uses. A new application ships with one file per framework component:

| File | Configures |
| --- | --- |
| `app.php` | The application's name, id, environment, encryption key, and framework providers |
| `broadcasting.php` | [Outbound broadcasting](/docs/{{version}}/framework/digging-deeper/broadcasting) connections |
| `cache.php` | [Cache](/docs/{{version}}/framework/digging-deeper/cache) stores |
| `concurrency.php` | The [concurrency](/docs/{{version}}/framework/digging-deeper/concurrency) driver |
| `database.php` | [Database](/docs/{{version}}/framework/database/database) and [Redis](/docs/{{version}}/framework/database/redis) connections |
| `filesystems.php` | [Filesystem](/docs/{{version}}/framework/digging-deeper/filesystem) disks |
| `hashing.php` | [Hashing](/docs/{{version}}/framework/security/hashing) drivers |
| `http.php` | The [HTTP client](/docs/{{version}}/framework/digging-deeper/http-client)'s async driver |
| `io-pools.php` | The [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop), its waiter backend, promise engine, mail handler and worker pools |
| `logging.php` | [Log](/docs/{{version}}/framework/the-basics/logging) channels |
| `queue.php` | [Queue](/docs/{{version}}/framework/digging-deeper/queues) connections and failed job storage |
| `sketches.php` | The [sketch](/docs/{{version}}/framework/the-basics/sketches) refresh rate and extra sketch classes |
| `workflows.php` | The [workflow](/docs/{{version}}/framework/the-basics/workflows) runtime |

### How Configuration Files Are Loaded

Venusian loads the framework's own copy of every configuration file first, then lays your application's files over it. For each file in your `config` directory, your top-level keys replace the framework's, and a few nested groups are merged one level deeper so you can add one entry without restating the rest: `stores` in `cache.php`, `connections` in `database.php`, `queue.php` and `broadcasting.php`, `disks` in `filesystems.php`, `channels` in `logging.php`, and `event_loop`, `pool_waiters`, `promise_engines` and `pool_workers` in `io-pools.php`.

This means you only need the files, and the keys, you want to change. If you delete `config/hashing.php`, the framework's hashing defaults still apply. A file you add yourself, such as `config/stargazer.php`, becomes its own top-level key (`stargazer.*`), and a file inside a subdirectory, such as `config/services/nasa.php`, is read as `services.nasa.*`.

You may generate a new, empty configuration file with the `make:config` Computer command:

```shell
php computer make:config stargazer
```

### Publishing Framework Configuration Files

If you have removed one of the framework's configuration files and want it back, the `config:publish` command copies the framework's version into your `config` directory. Run it without arguments to pick a file from a list, name the file you want, or publish all of them with `--all`:

```shell
php computer config:publish

php computer config:publish logging

php computer config:publish --all
```

The command will not overwrite a file you already have unless you pass `--force`.

### Application Overview

The `about` Computer command gives a quick overview of your application's configuration: its environment, whether configuration and signals are cached, the drivers in use, and how the event loop is set up. You may limit the output to one section with `--only`, or print it as JSON with `--json`:

```shell
php computer about

php computer about --only=environment --json
```

## Accessing Configuration Values

You may access your configuration values from anywhere in your application using the `config` helper. Configuration values are accessed using "dot" syntax, which includes the name of the file and the option you wish to access. A default value may be specified and is returned if the option does not exist:

```php
$name = config('app.name');

// Retrieve a default value if the configuration value does not exist...
$rate = config('sketches.refresh_rate', 60);
```

To set a configuration value while your application is running, pass an array to the `config` helper. The change lasts for the current process only; it is never written back to the file:

```php
config(['app.timezone' => 'America/Chicago']);
```

Calling `config()` with no arguments returns the configuration repository itself, a `Voyager\Config\Repository`. You may also resolve it from the container as `app('config')`, or inject `Voyager\Contracts\Config\Repository`. The repository offers `has`, `get`, `set`, `push`, `prepend` and `all`:

```php
if (config()->has('services.nasa.key')) {
    // ...
}

config()->push('sketches.load', App\Runner\Sketches\Telemetry::class);
```

### Typed Configuration Retrieval

When you need a value of a particular type, the repository's typed methods return it, or throw an `InvalidArgumentException` if the configured value has a different type. They are `string`, `integer`, `float`, `boolean`, `array`, and `collection`, which wraps an array value in a collection:

```php
$name = config()->string('app.name');

$rate = config()->float('sketches.refresh_rate');

$channels = config()->array('logging.channels');
```

> [!NOTE]
> Values read from the `.env` file are strings unless they are one of the special values described [below](#environment-variable-types). `IO_POOLS_PROCESS_WORKERS=4` arrives as the string `"4"`, so `integer` would throw on it. Cast it in the configuration file, as in `(int) env('IO_POOLS_PROCESS_WORKERS', 4)`, if you want to read it back with a typed method.

## Environment Configuration

It is often helpful to have different configuration values based on where the application is running. For example, you may want a `sqlite` database on your workstation and MySQL on the device the application is deployed to, or a different log level while you develop.

To make this easy, Venusian uses the [DotEnv](https://github.com/vlucas/phpdotenv) PHP library. A new application's root directory contains a `.env.example` file that lists the common environment variables. When you create an application, it is copied to `.env` and an `APP_KEY` is generated for you.

Your `.env` file should not be committed to your application's source control, since each developer or machine using your application could require a different environment configuration. It is also a security risk if an intruder gains access to your source control repository, since any sensitive credentials would be exposed. If you need to keep an environment file in source control, [encrypt it](#encrypting-environment-files) first.

### Additional Environment Files

Before loading your application's environment variables, Venusian checks whether an `APP_ENV` environment variable has been set on the process. If it has, and a file named `.env.[APP_ENV]` exists, Venusian loads that file instead of `.env`:

```shell
APP_ENV=staging php computer about
```

With the command above, `.env.staging` is loaded if it exists, and `.env` otherwise.

### Environment Variable Types

All variables in your `.env` file are read as strings, so a few reserved values let `env()` return other types:

| `.env` Value | `env()` Value |
| --- | --- |
| `true` | `(bool) true` |
| `(true)` | `(bool) true` |
| `false` | `(bool) false` |
| `(false)` | `(bool) false` |
| `empty` | `(string) ''` |
| `(empty)` | `(string) ''` |
| `null` | `(null) null` |
| `(null)` | `(null) null` |

If you need to define an environment variable with a value that contains spaces, enclose the value in double quotes:

```ini
APP_NAME="Deep Field"
```

### Retrieving Environment Configuration

All of the variables listed in the `.env` file are loaded when your application boots. The `env` helper retrieves them, and you will see it used throughout the configuration files. The second argument is the default value, returned when no environment variable exists for the key:

```php
'env' => env('APP_ENV', 'production'),
```

Variables that are already set in the process environment win over the `.env` file: Venusian never overwrites an existing environment variable with a value from the file. This lets a service manager or a shell override a single value without editing `.env`.

> [!WARNING]
> Only call `env` from your configuration files. Once the configuration is [cached](#configuration-caching), the `.env` file is no longer loaded, and `env` calls outside the configuration files only see variables set on the process itself. Read configuration values with `config` everywhere else.

### Determining the Current Environment

The current application environment is the `app.env` configuration value, which comes from the `APP_ENV` variable. The configuration file defaults it to `production`. You may read it through the `environment` method on the application:

```php
$environment = app()->environment();
```

You may also pass arguments to `environment` to check whether the environment matches a given value. The method returns `true` if the environment matches any of them, and accepts `*` wildcards:

```php
if (app()->environment('local')) {
    // The environment is local
}

if (app()->environment(['local', 'staging'])) {
    // The environment is either local OR staging...
}

if (app()->environment('stag*')) {
    // ...
}
```

The `env` Computer command prints the current environment:

```shell
php computer env
```

Commands that change or destroy data, such as `migrate`, `migrate:fresh`, `migrate:refresh`, `migrate:reset`, `migrate:rollback` and `queue:clear`, show an "Application In Production" alert and ask for confirmation before running when the environment is `production`. Pass `--force` to run them without the prompt.

### Encrypting Environment Files

Unencrypted environment files should never be stored in source control. However, Venusian allows you to encrypt your environment files so that they may safely be added to source control with the rest of your application.

#### Encryption

To encrypt an environment file, you may use the `env:encrypt` command:

```shell
php computer env:encrypt
```

Running the `env:encrypt` command will encrypt your `.env` file and place the encrypted contents in an `.env.encrypted` file. The decryption key is presented in the output of the command and should be stored in a secure password manager. If you would like to provide your own encryption key, you may use the `--key` option:

```shell
php computer env:encrypt --key=3UVsEgGVK36XN82KKeyLFMhvosbZN1aF
```

> [!NOTE]
> The length of the key provided should match the key length required by the encryption cipher being used. By default, Venusian uses the `AES-256-CBC` cipher, which requires a 32 character key. You are free to use any cipher supported by Venusian's [encrypter](/docs/{{version}}/framework/security/encryption) by passing the `--cipher` option when invoking the command.

If your application has multiple environment files, such as `.env` and `.env.staging`, you may specify the environment file that should be encrypted by providing the environment name via the `--env` option:

```shell
php computer env:encrypt --env=staging
```

The `--readable` option encrypts each value on its own and keeps the variable names in plain text, so a diff of the encrypted file shows which variables changed. The `--prune` option deletes the original file once it is encrypted, and `--force` overwrites an existing encrypted file:

```shell
php computer env:encrypt --readable --prune
```

#### Decryption

To decrypt an environment file, you may use the `env:decrypt` command. Pass the decryption key with the `--key` option; when you leave it out on an interactive terminal, the command asks for it:

```shell
php computer env:decrypt --key=3UVsEgGVK36XN82KKeyLFMhvosbZN1aF
```

When the `env:decrypt` command is invoked, Venusian will decrypt the contents of the `.env.encrypted` file and place the decrypted contents in the `.env` file. A file encrypted with `--readable` is recognized and decrypted the same way.

The `--cipher` option may be provided to the `env:decrypt` command in order to use a custom encryption cipher, and `--env` picks which environment's encrypted file to decrypt:

```shell
php computer env:decrypt --key=qUWuNRdfuImXcKxZ --cipher=AES-128-CBC --env=staging
```

In order to overwrite an existing environment file, you may provide the `--force` option. The `--path` and `--filename` options write the decrypted file somewhere other than your application's `.env`:

```shell
php computer env:decrypt --force

php computer env:decrypt --path=/etc/stargazer --filename=.env
```

Venusian only ever loads the plain `.env` file at boot, so an encrypted file must be decrypted on the machine before the application runs there.

## The Application's Name and Id

The `config/app.php` file carries two names for your application.

`app.name`, from `APP_NAME`, is the name people read: it appears in the output of `about` and anywhere your own code shows it.

`app.id`, from `APP_ID`, is the application's reverse-DNS identity, such as `com.example.stargazer`. On the desktop it is the macOS bundle identifier, the GTK application id and the Qt desktop file name all at once. The toolkit drivers read `config('app.id')` instead of carrying a default of their own, and a packaged build writes the same value into the packaged app's `.env`, so the window the desktop shows and the app it installed are known by one id:

```ini
APP_NAME=Stargazer
APP_ID=com.example.stargazer
```

A new application defaults `APP_ID` to `com.venusian.app`. Give each application its own id before you ship it, since the desktop treats two applications with the same id as one. The packaging tool reads `app.id` from `config/app.php` and refuses to build an application whose `config/app.php` has no `id` key, so keep the entry when you edit that file:

```php
'name' => env('APP_NAME', 'Venusian'),

'id' => env('APP_ID', 'com.venusian.app'),
```

### Timezone

Venusian sets PHP's default timezone from the `app.timezone` configuration value as it loads your configuration, and uses `UTC` when the key is not set. A new application's `config/app.php` does not define it; add it if your application should run in another zone:

```php
'timezone' => 'America/Chicago',
```

## Configuration Caching

To give your application a speed boost, you should cache all of your configuration files into a single file using the `config:cache` command. This combines all of the configuration options for your application into one file that is loaded quickly by the framework. This matters most on small devices, where reading and merging a dozen files on every start is noticeable:

```shell
php computer config:cache
```

The cache is written to `bootstrap/cache/config.php`. You may point it somewhere else with the `APP_CONFIG_CACHE` environment variable, either an absolute path or one relative to your application's root.

You should typically run `config:cache` as part of your deployment process. It should not be run during local development, since configuration options will frequently need to be changed while you develop.

Once the configuration has been cached, your application's `.env` file is not loaded by the framework during boot. Every value comes from the cache, including the ones that were read with `env` when the cache was built.

Every value in your configuration must be serializable to be cached. If a configuration file holds a closure or an object, `config:cache` removes the partial cache file and fails with "Your configuration files are not serializable."

You may use the `config:clear` command to purge the cached configuration:

```shell
php computer config:clear
```

Running `composer dump-autoload` also deletes the configuration cache, along with the service, package and signal caches in the same directory, so a dependency change never leaves a stale cache behind.

> [!WARNING]
> If you execute the `config:cache` command during your deployment process, you should be sure that you are only calling the `env` function from within your configuration files. Once the configuration has been cached, the `.env` file will not be loaded; therefore, the `env` function will only return process environment variables.

## Packaged Applications

An application built into a phar, a packaged app, cannot write inside its own archive. When its base path is inside a phar, Venusian moves everything it writes into the user's data directory, named after the app:

| Operating System | Data Directory |
| --- | --- |
| macOS | `~/Library/Application Support/<name>` |
| Linux | `$XDG_DATA_HOME/<name>`, or `~/.local/share/<name>` when `XDG_DATA_HOME` is not set |
| Windows | `%APPDATA%\<name>` |

The name is the `name` entry in the phar's metadata, or the phar's file name without a `.phar` or `-bin` suffix.

Inside that directory:

- `storage_path()` points at `<data>/storage`, unless the `VENUSIAN_STORAGE_PATH` environment variable names another directory.
- `database_path()` points at `<data>/database`, so an SQLite database lives with the user's data.
- The configuration, services, packages and signals caches are written to `<data>/bootstrap/cache/`, unless their `APP_CONFIG_CACHE`, `APP_SERVICES_CACHE`, `APP_PACKAGES_CACHE` or `APP_SIGNALS_CACHE` variables name another path.
- `bootstrap/providers.php` and your `config` files are still read from inside the phar.

The first time the app runs, Venusian creates the data directory and copies the phar's `storage` and `database` directories into it. After that the copy is never repeated, so a newer version of the app never overwrites the user's files.

On every start, Venusian compares the running phar's size and modification time with the ones it recorded last time. When they differ, as they do after an upgrade or a rebuild, it deletes the cached `bootstrap/cache/*.php` files so they are rebuilt from the phar that is now running. A cache written by an older version could name providers or classes the new one no longer has. The user's storage and database are left alone.

You may ask the application whether it is running packaged:

```php
if (app()->runningPackaged()) {
    $data = app()->packagedPaths()->dataPath();
}
```

`packagedPaths` returns a `Voyager\Core\PackagedPaths` instance inside a phar and `null` everywhere else.
