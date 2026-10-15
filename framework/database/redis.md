# Redis

Redis is an open source, advanced key-value store, reached from Venusian through blocking connections or from the event loop through its own sockets.

## Introduction

[Redis](https://redis.io) is an open source, advanced key-value store. It is often referred to as a data structure server since keys can contain [strings](https://redis.io/docs/latest/develop/data-types/strings/), [hashes](https://redis.io/docs/latest/develop/data-types/hashes/), [lists](https://redis.io/docs/latest/develop/data-types/lists/), [sets](https://redis.io/docs/latest/develop/data-types/sets/), and [sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/).

Before using Redis with Venusian, we encourage you to install and use the [PhpRedis](https://github.com/phpredis/phpredis) PHP extension via PECL. The extension is more complex to install compared to "user-land" PHP packages but may yield better performance for applications that make heavy use of Redis.

If you are unable to install the PhpRedis extension, you may install the `predis/predis` package via Composer. Predis is a Redis client written entirely in PHP and does not require any additional extensions:

```shell
composer require predis/predis
```

Neither client is needed to talk to Redis [from the event loop](#redis-on-the-event-loop): the loop speaks the Redis protocol on PHP stream sockets of its own.

<a id="configuration"></a>
## Configuration

You may configure your application's Redis settings via the `config/database.php` configuration file. Within this file, you will see a `redis` array containing the Redis servers utilized by your application:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', 'venusian_database_'),
        'persistent' => env('REDIS_PERSISTENT', false),
    ],

    'default' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_DB', '0'),
        'max_retries' => env('REDIS_MAX_RETRIES', 3),
        'backoff_algorithm' => env('REDIS_BACKOFF_ALGORITHM', 'decorrelated_jitter'),
        'backoff_base' => env('REDIS_BACKOFF_BASE', 100),
        'backoff_cap' => env('REDIS_BACKOFF_CAP', 1000),
    ],

    'cache' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_CACHE_DB', '1'),
        'max_retries' => env('REDIS_MAX_RETRIES', 3),
        'backoff_algorithm' => env('REDIS_BACKOFF_ALGORITHM', 'decorrelated_jitter'),
        'backoff_base' => env('REDIS_BACKOFF_BASE', 100),
        'backoff_cap' => env('REDIS_BACKOFF_CAP', 1000),
    ],

],
```

Each Redis server defined in your configuration file is required to have a name, host, and a port unless you define a single URL to represent the Redis connection:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', 'venusian_database_'),
    ],

    'default' => [
        'url' => 'tcp://127.0.0.1:6379?database=0',
    ],

    'cache' => [
        'url' => 'tls://user:password@127.0.0.1:6380?database=1',
    ],

],
```

#### Configuring the Connection Scheme

By default, Redis clients will use the `tcp` scheme when connecting to your Redis servers; however, you may use TLS / SSL encryption by specifying a `scheme` configuration option in your Redis server's configuration array:

```php
'default' => [
    'scheme' => 'tls',
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
],
```

### Clusters

If your application is utilizing a cluster of Redis servers, you should define these clusters within a `clusters` key of your Redis configuration. This configuration key does not exist by default so you will need to create it within your application's `config/database.php` configuration file:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', 'venusian_database_'),
    ],

    'clusters' => [
        'default' => [
            [
                'url' => env('REDIS_URL'),
                'host' => env('REDIS_HOST', '127.0.0.1'),
                'username' => env('REDIS_USERNAME'),
                'password' => env('REDIS_PASSWORD'),
                'port' => env('REDIS_PORT', '6379'),
                'database' => env('REDIS_DB', '0'),
            ],
        ],
    ],

    // ...
],
```

By default, Venusian will use native Redis clustering since the `options.cluster` configuration value is set to `redis`. Redis clustering is a great default option, as it gracefully handles failover.

Venusian also supports client-side sharding when using Predis. However, client-side sharding does not handle failover; therefore, it is primarily suited for transient cached data that is available from another primary data store.

If you would like to use client-side sharding instead of native Redis clustering, you may remove the `options.cluster` configuration value within your application's `config/database.php` configuration file:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'clusters' => [
        // ...
    ],

    // ...
],
```

The event loop's Redis sockets connect to a single server, so the [loop pipes and list resources](#redis-on-the-event-loop) need a connection defined outside `clusters`.

### Predis

If you would like your application to interact with Redis via the Predis package, you should ensure the `REDIS_CLIENT` environment variable's value is `predis`:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'predis'),

    // ...
],
```

In addition to the default configuration options, Predis supports additional [connection parameters](https://github.com/nrk/predis/wiki/Connection-Parameters) that may be defined for each of your Redis servers. To utilize these additional configuration options, add them to your Redis server configuration in your application's `config/database.php` configuration file:

```php
'default' => [
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
    'read_write_timeout' => 60,
],
```

### PhpRedis

By default, Venusian will use the PhpRedis extension to communicate with Redis. The client that Venusian will use to communicate with Redis is dictated by the value of the `redis.client` configuration option, which typically reflects the value of the `REDIS_CLIENT` environment variable:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    // ...
],
```

In addition to the default configuration options, PhpRedis supports the following additional connection parameters: `name`, `persistent`, `persistent_id`, `prefix`, `read_timeout`, `retry_interval`, `max_retries`, `backoff_algorithm`, `backoff_base`, `backoff_cap`, `timeout`, `scan`, and `context`. You may add any of these options to your Redis server configuration in the `config/database.php` configuration file:

```php
'default' => [
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
    'read_timeout' => 60,
    'context' => [
        // 'auth' => ['username', 'secret'],
        // 'stream' => ['verify_peer' => false],
    ],
],
```

The `context.stream` options are also the TLS options the event loop's Redis sockets connect with.

#### Retry and Backoff Configuration

The `retry_interval`, `max_retries`, `backoff_algorithm`, `backoff_base`, and `backoff_cap` options may be used to configure how the PhpRedis client should attempt to reconnect to a Redis server. The following backoff algorithms are supported: `default`, `decorrelated_jitter`, `equal_jitter`, `exponential`, `uniform`, and `constant`:

```php
'default' => [
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
    'max_retries' => env('REDIS_MAX_RETRIES', 3),
    'backoff_algorithm' => env('REDIS_BACKOFF_ALGORITHM', 'decorrelated_jitter'),
    'backoff_base' => env('REDIS_BACKOFF_BASE', 100),
    'backoff_cap' => env('REDIS_BACKOFF_CAP', 1000),
],
```

#### Unix Socket Connections

Redis connections can also be configured to use Unix sockets instead of TCP. This can offer improved performance by eliminating TCP overhead for connections to Redis instances on the same server as your application. To configure Redis to use a Unix socket, set your `REDIS_HOST` environment variable to the path of the Redis socket and the `REDIS_PORT` environment variable to `0`:

```env
REDIS_HOST=/run/redis/redis.sock
REDIS_PORT=0
```

#### PhpRedis Serialization and Compression

The PhpRedis extension may also be configured to use a variety of serializers and compression algorithms. These algorithms can be configured via the `options` array of your Redis configuration:

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', 'venusian_database_'),
        'serializer' => Redis::SERIALIZER_MSGPACK,
        'compression' => Redis::COMPRESSION_LZ4,
    ],

    // ...
],
```

Currently supported serializers include: `Redis::SERIALIZER_NONE` (default), `Redis::SERIALIZER_PHP`, `Redis::SERIALIZER_JSON`, `Redis::SERIALIZER_IGBINARY`, and `Redis::SERIALIZER_MSGPACK`.

Supported compression algorithms include: `Redis::COMPRESSION_NONE` (default), `Redis::COMPRESSION_LZF`, `Redis::COMPRESSION_ZSTD`, and `Redis::COMPRESSION_LZ4`. You may set the level with the `compression_level` option.

## Interacting With Redis

The Redis manager, a `Voyager\Redis\RedisManager`, is registered in the service container as `redis`, so you may resolve it with `app('redis')`. The manager supports dynamic methods, meaning you may call any [Redis command](https://redis.io/commands) on it and the command will be passed directly to Redis on the default connection. In this example, we will call the Redis `GET` command by calling the `get` method on the manager:

```php
<?php

namespace App\Services;

class ProfileService
{
    /**
     * Get the cached profile for the given user.
     */
    public function profile(string $id): mixed
    {
        return app('redis')->get('user:profile:'.$id);
    }
}
```

As mentioned above, you may call any of Redis' commands on the manager. Venusian uses magic methods to pass the commands to the Redis server. If a Redis command expects arguments, you should pass those to the manager's corresponding method:

```php
app('redis')->set('name', 'Taylor');

$values = app('redis')->lrange('names', 5, 10);
```

Alternatively, you may pass commands to the server using the `command` method, which accepts the name of the command as its first argument and an array of values as its second argument:

```php
$values = app('redis')->command('lrange', ['name', 5, 10]);
```

These calls block the calling process until Redis replies. To send commands without blocking the event loop, use a [pipe](#pipes).

#### Using Multiple Redis Connections

Your application's `config/database.php` configuration file allows you to define multiple Redis connections / servers. You may obtain a connection to a specific Redis connection using the manager's `connection` method:

```php
$redis = app('redis')->connection('connection-name');
```

To obtain an instance of the default Redis connection, you may call the `connection` method without any additional arguments, or resolve `redis.connection` from the container:

```php
$redis = app('redis')->connection();

$redis = app('redis.connection');
```

### Transactions

The `transaction` method provides a convenient wrapper around Redis' native `MULTI` and `EXEC` commands. The `transaction` method accepts a closure as its only argument. This closure will receive a Redis connection instance and may issue any commands it would like to this instance. All of the Redis commands issued within the closure will be executed in a single, atomic transaction:

```php
use Redis;

app('redis')->transaction(function (Redis $redis) {
    $redis->incr('user_visits', 1);
    $redis->incr('total_visits', 1);
});
```

> [!WARNING]
> When defining a Redis transaction, you may not retrieve any values from the Redis connection. Remember, your transaction is executed as a single, atomic operation and that operation is not executed until your entire closure has finished executing its commands.

#### Lua Scripts

The `eval` method provides another method of executing multiple Redis commands in a single, atomic operation. However, the `eval` method has the benefit of being able to interact with and inspect Redis key values during that operation. Redis scripts are written in the [Lua programming language](https://www.lua.org).

The `eval` method can be a bit scary at first, but we'll explore a basic example to break the ice. The `eval` method expects several arguments. First, you should pass the Lua script (as a string) to the method. Secondly, you should pass the number of keys (as an integer) that the script interacts with. Thirdly, you should pass the names of those keys. Finally, you may pass any other additional arguments that you need to access within your script.

In this example, we will increment a counter, inspect its new value, and increment a second counter if the first counter's value is greater than five. Finally, we will return the value of the first counter:

```php
$value = app('redis')->eval(<<<'LUA'
    local counter = redis.call("incr", KEYS[1])

    if counter > 5 then
        redis.call("incr", KEYS[2])
    end

    return counter
LUA, 2, 'first-counter', 'second-counter');
```

> [!WARNING]
> Please consult the [Redis documentation](https://redis.io/commands/eval) for more information on Redis scripting.

### Pipelining Commands

Sometimes you may need to execute dozens of Redis commands. Instead of making a network trip to your Redis server for each command, you may use the `pipeline` method. The `pipeline` method accepts one argument: a closure that receives a Redis instance. You may issue all of your commands to this Redis instance and they will all be sent to the Redis server at the same time to reduce network trips to the server. The commands will still be executed in the order they were issued:

```php
use Redis;

app('redis')->pipeline(function (Redis $pipe) {
    for ($i = 0; $i < 1000; $i++) {
        $pipe->set("key:$i", $i);
    }
});
```

### Command Signals

Each connection can dispatch a `Voyager\Redis\Signals\CommandExecuted` signal after every command and a `Voyager\Redis\Signals\CommandFailed` signal when a command throws. Command signals are off by default; turn them on with `enableEvents` before the connection is first resolved, then register listeners on the connection:

```php
use Voyager\Redis\Signals\CommandExecuted;
use Voyager\Redis\Signals\CommandFailed;

app('redis')->enableEvents();

app('redis')->connection()->listen(function (CommandExecuted $signal) {
    // $signal->command, $signal->parameters, $signal->time...
});

app('redis')->connection()->listenForFailures(function (CommandFailed $signal) {
    // ...
});
```

## Pub / Sub

Venusian provides a convenient interface to the Redis `publish` and `subscribe` commands. These Redis commands allow you to listen for messages on a given "channel". You may publish messages to the channel from another application, or even using another programming language, allowing easy communication between applications and processes.

First, let's set up a channel listener using the `subscribe` method. We'll place this method call within a [Computer command](/docs/{{version}}/framework/digging-deeper/computer) since calling the `subscribe` method begins a long-running process:

```php
<?php

namespace App\Console\Commands;

use Voyager\Console\Command;

class RedisSubscribe extends Command
{
    /**
     * The name and signature of the console command.
     */
    protected ?string $signature = 'redis:subscribe';

    /**
     * The console command description.
     */
    protected string $description = 'Subscribe to a Redis channel';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        app('redis')->subscribe(['test-channel'], function (string $message) {
            echo $message;
        });
    }
}
```

Now we may publish messages to the channel using the `publish` method:

```php
app('redis')->publish('test-channel', json_encode([
    'name' => 'Adam Wathan'
]));
```

#### Wildcard Subscriptions

Using the `psubscribe` method, you may subscribe to a wildcard channel, which may be useful for catching all messages on all channels. The channel name will be passed as the second argument to the provided closure:

```php
app('redis')->psubscribe(['*'], function (string $message, string $channel) {
    echo $message;
});

app('redis')->psubscribe(['users.*'], function (string $message, string $channel) {
    echo $message;
});
```

## Redis on the Event Loop

The connections above block the calling process while they wait on Redis. When your application runs on the event loop, the Redis manager offers pipes and list resources that speak the Redis protocol on sockets of their own, so the loop keeps running while Redis answers. Each socket reads its host, port, credentials, database, and key prefix from the same connection configuration in `config/database.php`, so a socket and a connection of the same name agree on every key. Clustered connections are not supported.

### Pipes

The `pipe` method returns a `Voyager\Redis\Sockets\RedisPipe` for a connection. Its `send` method queues a command and returns a `Voyager\Contracts\IOPools\Promise` for its reply, which is a string, an integer, a list, or `null`. Replies come back in the order the commands were sent. The second argument names the command in error messages:

```php
$pipe = app('redis')->pipe();
$key = $pipe->prefix().'visits';

$pipe->send(['SET', $key, '0'], 'SET visits');

$pipe->send(['INCRBY', $key, '7'], 'INCRBY visits')->then(function (int $visits) {
    // ...
});
```

A pipe sends keys exactly as given, so prefix them with the connection's `prefix()`. Values travel as raw bytes: the connection's serializer and compression options do not apply. A command Redis refuses rejects its promise with a `Voyager\Redis\Sockets\RedisSocketException`, and the commands after it are still answered. A pipe connects on its first `send` and only holds the loop open while a reply is due, so an idle pipe never keeps `run()` alive.

### Pushing Onto a List

The `listPush` method returns a `Voyager\Redis\Lists\ListPush` for one list. Its `push` method sends an `RPUSH` through a pipe of its own, prefixes the key for you, and resolves with the list's new length:

```php
$push = app('redis')->listPush('jobs');

$push->push('job 1', 'job 2')->then(function (int $length) {
    // ...
});
```

### Popping a List as Mail

The `listPop` method returns a `Voyager\Redis\Lists\ListPop`, a loop resource that pops a list and hands each value to your application as mail. Register it on the loop under a name; every popped value is then dispatched as a `Voyager\Redis\RedisMessage` signal named `redis:{key}`, carrying the `key` and the `raw` bytes Redis stored:

```php
use Voyager\Contracts\IOPools\Loop;
use Voyager\Redis\RedisMessage;

$loop = app(Loop::class);

$loop->resource('jobs', app('redis')->listPop('jobs'));

app('signals')->listen('redis:jobs', function (RedisMessage $message) {
    // $message->raw...
});

$loop->run();
```

A `BLPOP` is always waiting on the resource's socket, and that socket is part of the loop's wait, so the loop wakes the moment a value lands. Each pop also takes up to `batch` more values behind the first, 64 by default:

```php
$loop->resource('backlog', app('redis')->listPop('backlog', batch: 256));
```

A popped value is gone from Redis, so values are never lost when popping stops. The `release` method unblocks the waiting `BLPOP`, reads any replies still on their way, and pushes every value that was popped but not yet dispatched back onto the head of the list in its original order. Release runs on its own when the loop stops and when the process exits; if you `forget` the resource while the loop keeps running, call `release` yourself:

```php
$pop = app('redis')->listPop('jobs');

$loop->resource('jobs', $pop);

// Later...
$loop->forget('jobs');
$pop->release();
```

If Redis drops the resource's socket, it reconnects and keeps popping.
