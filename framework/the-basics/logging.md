# Logging

Venusian provides robust logging services that write messages to files, the system log, or any Monolog handler, blocking or through a worker pool.

## Introduction

To help you learn more about what's happening within your application, Venusian provides robust logging services that allow you to log messages to files, the system error log, or any handler Monolog offers.

Venusian logging is based on "channels". Each channel represents a specific way of writing log information. For example, the `single` channel writes log files to a single log file, while the `syslog` channel sends log messages to the system log. Log messages may be written to multiple channels based on their severity.

Under the hood, Venusian utilizes the [Monolog](https://github.com/Seldaek/monolog) library, which provides support for a variety of powerful log handlers. Venusian makes it a cinch to configure these handlers, allowing you to mix and match them to customize your application's log handling.

## Configuration

All of the configuration options that control your application's logging behavior are housed in the `config/logging.php` configuration file. This file allows you to configure your application's log channels, so be sure to review each of the available channels and their options. We'll review a few common options below.

By default, Venusian will use the `stack` channel when logging messages. The `stack` channel is used to aggregate multiple log channels into a single channel. The `stack` channel's members are read from the comma-separated `LOG_STACK` environment variable, which defaults to `single`. For more information on building stacks, check out the [documentation below](#building-log-stacks).

### Available Channel Drivers

Each log channel is powered by a "driver". The driver determines how and where the log message is actually recorded. The following log channel drivers are available in every Venusian application. An entry for most of these drivers is already present in your application's `config/logging.php` configuration file, so be sure to review this file to become familiar with its contents:

| Name         | Description                                                          |
| ------------ | -------------------------------------------------------------------- |
| `custom`     | A driver that calls a specified factory to create a channel.         |
| `daily`      | A `RotatingFileHandler` based Monolog driver which rotates daily.    |
| `errorlog`   | An `ErrorLogHandler` based Monolog driver.                           |
| `monolog`    | A Monolog factory driver that may use any supported Monolog handler. |
| `single`     | A single file or path based logger channel (`StreamHandler`).        |
| `stack`      | A wrapper to facilitate creating "multi-channel" channels.           |
| `syslog`     | A `SyslogHandler` based Monolog driver.                              |

> [!NOTE]
> Check out the documentation on [advanced channel customization](#monolog-channel-customization) to learn more about the `monolog` and `custom` drivers.

#### Configuring the Channel Name

By default, Monolog is instantiated with a "channel name" that matches the current environment, such as `production` or `local`. To change this value, you may add a `name` option to your channel's configuration:

```php
'stack' => [
    'driver' => 'stack',
    'name' => 'channel-name',
    'channels' => ['single', 'syslog'],
],
```

### Channel Prerequisites

#### Configuring the Single and Daily Channels

The `single` and `daily` channels have three optional configuration options: `bubble`, `permission`, and `locking`.

| Name         | Description                                                                   | Default |
| ------------ | ----------------------------------------------------------------------------- | ------- |
| `bubble`     | Indicates if messages should bubble up to other channels after being handled. | `true`  |
| `locking`    | Attempt to lock the log file before writing to it.                            | `false` |
| `permission` | The log file's permissions. When omitted, Monolog's default applies.         | `null`  |

Additionally, the retention policy for the `daily` channel can be configured via the `days` configuration option, which defaults to `7` when omitted. Your application's `config/logging.php` file sets it from the `LOG_DAILY_DAYS` environment variable, defaulting to `14`.

### Logging Deprecation Warnings

PHP, Venusian, and other libraries often notify their users that some of their features have been deprecated and will be removed in a future version. If you would like to log these deprecation warnings, you may specify your preferred `deprecations` log channel using the `LOG_DEPRECATIONS_CHANNEL` environment variable, or within your application's `config/logging.php` configuration file:

```php
'deprecations' => [
    'channel' => env('LOG_DEPRECATIONS_CHANNEL', 'null'),
    'trace' => env('LOG_DEPRECATIONS_TRACE', false),
],

'channels' => [
    // ...
]
```

Or, you may define a log channel named `deprecations`. If a log channel with this name exists, it will always be used to log deprecations:

```php
'channels' => [
    'deprecations' => [
        'driver' => 'single',
        'path' => storage_path('logs/php-deprecation-warnings.log'),
    ],
],
```

<a id="building-log-stacks"></a>
## Building Log Stacks

As mentioned previously, the `stack` driver allows you to combine multiple channels into a single log channel for convenience. To illustrate how to use log stacks, let's take a look at an example configuration that you might see in a production application:

```php
'channels' => [
    'stack' => [
        'driver' => 'stack',
        'channels' => ['syslog', 'daily'], // [tl! add]
        'ignore_exceptions' => false,
    ],

    'syslog' => [
        'driver' => 'syslog',
        'level' => env('LOG_LEVEL', 'debug'),
        'facility' => env('LOG_SYSLOG_FACILITY', LOG_USER),
        'replace_placeholders' => true,
    ],

    'daily' => [
        'driver' => 'daily',
        'path' => storage_path('logs/venusian.log'),
        'level' => 'critical',
        'days' => env('LOG_DAILY_DAYS', 14),
        'replace_placeholders' => true,
    ],
],
```

Let's dissect this configuration. First, notice our `stack` channel aggregates two other channels via its `channels` option: `syslog` and `daily`. So, when logging messages, both of these channels will have the opportunity to log the message. However, as we will see below, whether these channels actually log the message may be determined by the message's severity / "level".

#### Log Levels

Take note of the `level` configuration option present on the `syslog` and `daily` channel configurations in the example above. This option determines the minimum "level" a message must be in order to be logged by the channel. Monolog, which powers Venusian's logging services, offers all of the log levels defined in the [RFC 5424 specification](https://tools.ietf.org/html/rfc5424). In descending order of severity, these log levels are: **emergency**, **alert**, **critical**, **error**, **warning**, **notice**, **info**, and **debug**.

So, imagine we log a message using the `debug` method:

```php
app('log')->debug('An informational message.');
```

Given our configuration, the `syslog` channel will write the message to the system log; however, since the error message is not `critical` or above, it will not be written to the daily log file. However, if we log an `emergency` message, it will be written to both the system log and the daily log file since the `emergency` level is above our minimum level threshold for both channels:

```php
app('log')->emergency('The system is down!');
```

## Writing Log Messages

You may write information to the logs using the log manager, which the container resolves as `app('log')`. You may also inject it as `Psr\Log\LoggerInterface` or `Voyager\Log\LogManager`. As previously mentioned, the logger provides the eight logging levels defined in the [RFC 5424 specification](https://tools.ietf.org/html/rfc5424): **emergency**, **alert**, **critical**, **error**, **warning**, **notice**, **info** and **debug**:

```php
app('log')->emergency($message);
app('log')->alert($message);
app('log')->critical($message);
app('log')->error($message);
app('log')->warning($message);
app('log')->notice($message);
app('log')->info($message);
app('log')->debug($message);
```

You may call any of these methods to log a message for the corresponding level. By default, the message will be written to the default log channel as configured by your `logging` configuration file:

```php
<?php

namespace App\Services;

use Psr\Log\LoggerInterface;

class Importer
{
    public function __construct(protected LoggerInterface $log) {}

    public function import(string $id): void
    {
        $this->log->info('Importing record: {id}', ['id' => $id]);

        // ...
    }
}
```

Each of these calls writes the message before it returns. To write without blocking, see [writing logs through a worker pool](#writing-logs-through-a-worker-pool).

### Contextual Information

An array of contextual data may be passed to the log methods. This contextual data will be formatted and displayed with the log message:

```php
app('log')->info('User {id} failed to login.', ['id' => $user->id]);
```

Occasionally, you may wish to specify some contextual information that should be included with all subsequent log entries in a particular channel. For example, you may wish to log a run ID that is associated with each run of an import. To accomplish this, you may call the `withContext` method, which adds the context to the default channel, or to the channel you call it on:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

app('log')->withContext([
    'run-id' => (string) Str::uuid(),
]);
```

If you would like to share contextual information across _all_ logging channels, you may invoke the log manager's `shareContext` method. This method will provide the contextual information to all created channels and any channels that are created subsequently:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

app('log')->shareContext([
    'run-id' => (string) Str::uuid(),
]);
```

The `withoutContext` method removes the given keys, or all context when called with no arguments, from every channel created so far, and `flushSharedContext` forgets the shared context.

> [!NOTE]
> If you need to share log context while processing queued jobs, you may utilize [job middleware](/docs/{{version}}/framework/digging-deeper/queues#job-middleware).

### Writing to Specific Channels

Sometimes you may wish to log a message to a channel other than your application's default channel. You may use the log manager's `channel` method to retrieve and log to any channel defined in your configuration file:

```php
app('log')->channel('syslog')->info('Something happened!');
```

If you would like to create an on-demand logging stack consisting of multiple channels, you may use the `stack` method:

```php
app('log')->stack(['single', 'syslog'])->info('Something happened!');
```

#### On-Demand Channels

It is also possible to create an on-demand channel by providing the configuration at runtime without that configuration being present in your application's `logging` configuration file. To accomplish this, you may pass a configuration array to the log manager's `build` method:

```php
app('log')->build([
  'driver' => 'single',
  'path' => storage_path('logs/custom.log'),
])->info('Something happened!');
```

You may also wish to include an on-demand channel in an on-demand logging stack. This can be achieved by including your on-demand channel instance in the array passed to the `stack` method:

```php
$channel = app('log')->build([
  'driver' => 'single',
  'path' => storage_path('logs/custom.log'),
]);

app('log')->stack(['syslog', $channel])->info('Something happened!');
```

## Writing Logs Through a Worker Pool

Every logging method has an `Async` twin: `emergencyAsync`, `alertAsync`, `criticalAsync`, `errorAsync`, `warningAsync`, `noticeAsync`, `infoAsync`, `debugAsync`, and `logAsync`, which accepts the level as its first argument. Instead of writing the message itself, an async call hands it to an IOPools worker pool and returns a `Voyager\Contracts\IOPools\Promise` at once. The promise is fulfilled once a worker has written the line:

```php
app('log')->infoAsync('Import started.', ['id' => $id]);

app('log')->channel('daily')->errorAsync('Payment failed.', ['exception' => $e])
    ->then(function () {
        // The line has been written...
    });
```

The async methods are available on the log manager, which writes to the default channel, and on every channel it returns, including stacks and on-demand channels. They write through the thread workers when the `io-pools.pool_workers.threads.enabled` configuration option is on, and through the process workers otherwise. If neither pool is enabled, the call throws an `InvalidArgumentException`.

Everything up to the write happens where the call is made: the level check, the message formatting, the context merge, and the `Voyager\Log\Signals\MessageLogged` signal, so your own process's [log signal listeners](#listening-for-log-messages) hear async messages too. A message below the channel's level never leaves your process; its promise is already fulfilled. Exceptions in the context are flattened so they cross to the worker and are formatted there as the original exception would be.

Lines written through a channel land in the order the calls were made, however many workers the pool has: one batch of calls per channel is out at a time, and calls made meanwhile go in the next batch. The worker builds the channel from its configuration, including its `tap` classes and processors.

> [!WARNING]
> Everything an async call carries must be serializable. A call whose context, [Context](/docs/{{version}}/framework/digging-deeper/context) data, or channel configuration holds a closure rejects with an `InvalidArgumentException`; the calls around it are still written. A channel built by a closure in its `via` option cannot write asynchronously, nor can an on-demand stack given a channel instance instead of a channel name.

When the event loop stops, the calls still waiting for a worker are written in your own process, blocking, in the order they were made. A script that exits without running the loop or waiting on its promises still has its async lines written before it ends.

### Listening for Log Messages

Every channel dispatches a `Voyager\Log\Signals\MessageLogged` signal for each message it logs, blocking or async. The `listen` method registers a listener for that signal; since the signal is shared by every channel, the listener hears the messages of all of them. You may equally listen through `app('signals')->listen(MessageLogged::class, ...)`:

```php
use Voyager\Log\Signals\MessageLogged;

app('log')->listen(function (MessageLogged $logged) {
    // $logged->level, $logged->message, $logged->context...
});
```

<a id="monolog-channel-customization"></a>
## Monolog Channel Customization

### Customizing Monolog for Channels

Sometimes you may need complete control over how Monolog is configured for an existing channel. For example, you may want to configure a custom Monolog `FormatterInterface` implementation for Venusian's built-in `single` channel.

To get started, define a `tap` array on the channel's configuration. The `tap` array should contain a list of classes that should have an opportunity to customize (or "tap" into) the Monolog instance after it is created. There is no conventional location where these classes should be placed, so you are free to create a directory within your application to contain these classes:

```php
'single' => [
    'driver' => 'single',
    'tap' => [App\Logging\CustomizeFormatter::class],
    'path' => storage_path('logs/venusian.log'),
    'level' => env('LOG_LEVEL', 'debug'),
    'replace_placeholders' => true,
],
```

Once you have configured the `tap` option on your channel, you're ready to define the class that will customize your Monolog instance. This class only needs a single method: `__invoke`, which receives a `Voyager\Log\Logger` instance. The `Voyager\Log\Logger` instance proxies all method calls to the underlying Monolog instance:

```php
<?php

namespace App\Logging;

use Voyager\Log\Logger;
use Monolog\Formatter\LineFormatter;

class CustomizeFormatter
{
    /**
     * Customize the given logger instance.
     */
    public function __invoke(Logger $logger): void
    {
        foreach ($logger->getHandlers() as $handler) {
            $handler->setFormatter(new LineFormatter(
                '[%datetime%] %channel%.%level_name%: %message% %context% %extra%'
            ));
        }
    }
}
```

> [!NOTE]
> All of your "tap" classes are resolved by the [service container](/docs/{{version}}/framework/architecture-concepts/container), so any constructor dependencies they require will automatically be injected.

### Creating Monolog Handler Channels

Monolog has a variety of [available handlers](https://github.com/Seldaek/monolog/tree/main/src/Monolog/Handler) and Venusian does not include a built-in channel for each one. In some cases, you may wish to create a custom channel that is merely an instance of a specific Monolog handler that does not have a corresponding Venusian log driver. These channels can be easily created using the `monolog` driver.

When using the `monolog` driver, the `handler` configuration option is used to specify which handler will be instantiated. Optionally, any constructor parameters the handler needs may be specified using the `handler_with` configuration option:

```php
'logentries' => [
    'driver'  => 'monolog',
    'handler' => Monolog\Handler\SyslogUdpHandler::class,
    'handler_with' => [
        'host' => 'my.logentries.internal.datahubhost.company.com',
        'port' => '10000',
    ],
],
```

#### Monolog Formatters

When using the `monolog` driver, the Monolog `LineFormatter` will be used as the default formatter. However, you may customize the type of formatter passed to the handler using the `formatter` and `formatter_with` configuration options:

```php
'json' => [
    'driver' => 'monolog',
    'handler' => Monolog\Handler\StreamHandler::class,
    'handler_with' => [
        'stream' => storage_path('logs/venusian.json'),
    ],
    'formatter' => Monolog\Formatter\JsonFormatter::class,
    'formatter_with' => [
        'appendNewline' => true,
    ],
],
```

If you are using a Monolog handler that is capable of providing its own formatter, you may set the value of the `formatter` configuration option to `default`:

```php
'newrelic' => [
    'driver' => 'monolog',
    'handler' => Monolog\Handler\NewRelicHandler::class,
    'formatter' => 'default',
],
```

#### Monolog Processors

Monolog can also process messages before logging them. You can create your own processors or use the [existing processors offered by Monolog](https://github.com/Seldaek/monolog/tree/main/src/Monolog/Processor).

If you would like to customize the processors for a `monolog` driver, add a `processors` configuration value to your channel's configuration:

```php
'memory' => [
    'driver' => 'monolog',
    'handler' => Monolog\Handler\StreamHandler::class,
    'handler_with' => [
        'stream' => 'php://stderr',
    ],
    'processors' => [
        // Simple syntax...
        Monolog\Processor\MemoryUsageProcessor::class,

        // With options...
        [
            'processor' => Monolog\Processor\PsrLogMessageProcessor::class,
            'with' => ['removeUsedContextFields' => true],
        ],
    ],
],
```

### Creating Custom Channels via Factories

If you would like to define an entirely custom channel in which you have full control over Monolog's instantiation and configuration, you may specify a `custom` driver type in your `config/logging.php` configuration file. Your configuration should include a `via` option that contains the name of the factory class which will be invoked to create the Monolog instance:

```php
'channels' => [
    'example-custom-channel' => [
        'driver' => 'custom',
        'via' => App\Logging\CreateCustomLogger::class,
    ],
],
```

Once you have configured the `custom` driver channel, you're ready to define the class that will create your Monolog instance. This class only needs a single `__invoke` method which should return the Monolog logger instance. The method will receive the channels configuration array as its only argument:

```php
<?php

namespace App\Logging;

use Monolog\Logger;

class CreateCustomLogger
{
    /**
     * Create a custom Monolog instance.
     */
    public function __invoke(array $config): Logger
    {
        return new Logger(/* ... */);
    }
}
```
