# Database: Getting Started

Configure database connections and run raw SQL, transactions, and worker-pool offloaded queries through Venusian's database manager.

## Introduction

Almost every modern application interacts with a database. Venusian makes interacting with databases extremely simple across a variety of supported databases using raw SQL, a [fluent query builder](/docs/{{version}}/framework/database/queries), and the [Instrument ORM](/docs/{{version}}/framework/instrument-orm/instrument). Currently, Venusian provides first-party support for five databases:

- MariaDB 10.3+ ([Version Policy](https://mariadb.org/about/#maintenance-policy))
- MySQL 5.7+ ([Version Policy](https://en.wikipedia.org/wiki/MySQL#Release_history))
- PostgreSQL 10.0+ ([Version Policy](https://www.postgresql.org/support/versioning/))
- SQLite 3.26.0+
- SQL Server 2017+ ([Version Policy](https://docs.microsoft.com/en-us/lifecycle/products/?products=sql-server))

The database manager is bound in the container as `db`. It is a `Voyager\Database\DatabaseManager`, and every connection it hands out is a `Voyager\Database\Connection`. You may reach it through `app('db')`, or by type-hinting `Voyager\Database\DatabaseManager` or `Voyager\Database\ConnectionResolverInterface` in a constructor. The default connection itself is bound as `db.connection`, and its schema builder as `db.schema`.

To query the database from code running on the event loop without blocking it, see [Using the Database on the Event Loop](/docs/{{version}}/framework/database/event-loop).

<a id="configuration"></a>
### Configuration

The configuration for Venusian's database services is located in your application's `config/database.php` configuration file. In this file, you may define all of your database connections, as well as specify which connection should be used by default. Most of the configuration options within this file are driven by the values of your application's environment variables. Examples for each of Venusian's supported database systems are provided in this file, and the default connection is `sqlite`.

> [!NOTE]
> The `neo4j` connection listed in `config/database.php` is not served by the SQL database manager described on this page. It belongs to the separate Graph component (`Voyager\Graph`), which needs the `laudis/neo4j-php-client` package.

<a id="sqlite-configuration"></a>
#### SQLite Configuration

SQLite databases are contained within a single file on your filesystem. You can create a new SQLite database using the `touch` command in your terminal: `touch database/database.sqlite`. The default `sqlite` connection already points at `database/database.sqlite`. To use a database elsewhere, place the absolute path to the database in the `DB_DATABASE` environment variable:

```ini
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite
```

By default, foreign key constraints are enabled for SQLite connections. If you would like to disable them, you should set the `DB_FOREIGN_KEYS` environment variable to `false`:

```ini
DB_FOREIGN_KEYS=false
```

#### Microsoft SQL Server Configuration

To use a Microsoft SQL Server database, you should ensure that you have the `sqlsrv` and `pdo_sqlsrv` PHP extensions installed as well as any dependencies they may require such as the Microsoft SQL ODBC driver.

#### Configuration Using URLs

Typically, database connections are configured using multiple configuration values such as `host`, `database`, `username`, `password`, etc. Each of these configuration values has its own corresponding environment variable. This means that when configuring your database connection information on a production server, you need to manage several environment variables.

Some managed database providers such as AWS and Heroku provide a single database "URL" that contains all of the connection information for the database in a single string. An example database URL may look something like the following:

```html
mysql://root:password@127.0.0.1/venusian?charset=UTF-8
```

These URLs typically follow a standard schema convention:

```html
driver://username:password@host:port/database?options
```

For convenience, Venusian supports these URLs as an alternative to configuring your database with multiple configuration options. If the `url` (or corresponding `DB_URL` environment variable) configuration option is present, it will be used to extract the database connection and credential information.

### Read and Write Connections

Sometimes you may wish to use one database connection for SELECT statements, and another for INSERT, UPDATE, and DELETE statements. Venusian makes this a breeze, and the proper connections will always be used whether you are using raw queries, the query builder, or the Instrument ORM.

To see how read / write connections should be configured, let's look at this example:

```php
'mysql' => [
    'driver' => 'mysql',

    'read' => [
        'host' => [
            '192.168.1.1',
            '196.168.1.2',
        ],
    ],
    'write' => [
        'host' => [
            '192.168.1.3',
        ],
    ],
    'sticky' => true,

    'port' => env('DB_PORT', '3306'),
    'database' => env('DB_DATABASE', 'venusian'),
    'username' => env('DB_USERNAME', 'root'),
    'password' => env('DB_PASSWORD', ''),
    'unix_socket' => env('DB_SOCKET', ''),
    'charset' => env('DB_CHARSET', 'utf8mb4'),
    'collation' => env('DB_COLLATION', 'utf8mb4_unicode_ci'),
    'prefix' => '',
    'prefix_indexes' => true,
    'strict' => true,
    'engine' => null,
],
```

Note that three keys have been added to the configuration array: `read`, `write` and `sticky`. The `read` and `write` keys have array values containing a single key: `host`. The rest of the database options for the `read` and `write` connections will be merged from the main `mysql` configuration array.

You only need to place items in the `read` and `write` arrays if you wish to override the values from the main `mysql` array. So, in this case, `192.168.1.1` will be used as the host for the "read" connection, while `192.168.1.3` will be used for the "write" connection. The database credentials, prefix, character set, and all other options in the main `mysql` array will be shared across both connections. When multiple values exist in the `host` configuration array, a database host will be randomly chosen each time the connection is made.

#### The `sticky` Option

The `sticky` option is an *optional* value that can be used to allow the immediate reading of records that have been written to the database by the same connection. If the `sticky` option is enabled and a "write" operation has been performed against the database, any further "read" operations on that connection will use the "write" connection. This ensures that any data written can be immediately read back from the database. It is up to you to decide if this is the desired behavior for your application.

## Running SQL Queries

Once you have configured your database connection, you may run queries using the database manager. Its default connection provides methods for each type of query: `select`, `update`, `insert`, `delete`, and `statement`.

#### Running a Select Query

To run a basic SELECT query, you may use the `select` method:

```php
<?php

namespace App\Users;

use Voyager\Database\DatabaseManager;

class ActiveUsers
{
    public function __construct(private DatabaseManager $db) {}

    /**
     * Get all of the active users.
     */
    public function all(): array
    {
        return $this->db->select('select * from users where active = ?', [1]);
    }
}
```

The first argument passed to the `select` method is the SQL query, while the second argument is any parameter bindings that need to be bound to the query. Typically, these are the values of the `where` clause constraints. Parameter binding provides protection against SQL injection.

The `select` method will always return an `array` of results. Each result within the array will be a PHP `stdClass` object representing a record from the database:

```php
$users = app('db')->select('select * from users');

foreach ($users as $user) {
    echo $user->name;
}
```

#### Selecting Scalar Values

Sometimes your database query may result in a single, scalar value. Instead of being required to retrieve the query's scalar result from a record object, Venusian allows you to retrieve this value directly using the `scalar` method:

```php
$burgers = app('db')->scalar(
    "select count(case when food = 'burger' then 1 end) as burgers from menu"
);
```

#### Selecting Multiple Result Sets

If your application calls stored procedures that return multiple result sets, you may use the `selectResultSets` method to retrieve all of the result sets returned by the stored procedure:

```php
[$options, $notifications] = app('db')->selectResultSets(
    "CALL get_user_options_and_notifications(?)", [$userId]
);
```

#### Using Named Bindings

Instead of using `?` to represent your parameter bindings, you may execute a query using named bindings:

```php
$results = app('db')->select('select * from users where id = :id', ['id' => 1]);
```

#### Running an Insert Statement

To execute an `insert` statement, you may use the `insert` method. Like `select`, this method accepts the SQL query as its first argument and bindings as its second argument:

```php
app('db')->insert('insert into users (id, name) values (?, ?)', [1, 'Marc']);
```

#### Running an Update Statement

The `update` method should be used to update existing records in the database. The number of rows affected by the statement is returned by the method:

```php
$affected = app('db')->update(
    'update users set votes = 100 where name = ?',
    ['Anita']
);
```

#### Running a Delete Statement

The `delete` method should be used to delete records from the database. Like `update`, the number of rows affected will be returned by the method:

```php
$deleted = app('db')->delete('delete from users');
```

#### Running a General Statement

Some database statements do not return any value. For these types of operations, you may use the `statement` method:

```php
app('db')->statement('drop table users');
```

#### Running an Unprepared Statement

Sometimes you may want to execute an SQL statement without binding any values. You may use the `unprepared` method to accomplish this:

```php
app('db')->unprepared('update users set votes = 100 where name = "Dries"');
```

> [!WARNING]
> Since unprepared statements do not bind parameters, they may be vulnerable to SQL injection. You should never allow user controlled values within an unprepared statement.

#### Implicit Commits

When using the `statement` and `unprepared` methods within transactions you must be careful to avoid statements that cause [implicit commits](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html). These statements will cause the database engine to indirectly commit the entire transaction, leaving Venusian unaware of the database's transaction level. An example of such a statement is creating a database table:

```php
app('db')->unprepared('create table a (col varchar(1) null)');
```

Please refer to the MySQL manual for [a list of all statements](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html) that trigger implicit commits.

### Using Multiple Database Connections

If your application defines multiple connections in your `config/database.php` configuration file, you may access each connection via the `connection` method of the database manager. The connection name passed to the `connection` method should correspond to one of the connections listed in your `config/database.php` configuration file or configured at runtime using the `config` helper:

```php
$users = app('db')->connection('sqlite')->select(/* ... */);
```

You may access the raw, underlying PDO instance of a connection using the `getPdo` method on a connection instance:

```php
$pdo = app('db')->connection()->getPdo();
```

### Listening for Query Signals

If you would like to specify a closure that is invoked for each SQL query executed by your application, you may use the `listen` method. Each executed query dispatches a `Voyager\Database\Events\QueryExecuted` signal through the `signals` dispatcher, which this method listens for. This can be useful for logging queries or debugging. You may register your query listener closure in the `boot` method of a [service provider](/docs/{{version}}/framework/architecture-concepts/providers):

```php
<?php

namespace App\Providers;

use Voyager\Database\Events\QueryExecuted;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // ...
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        app('db')->listen(function (QueryExecuted $query) {
            // $query->sql;
            // $query->bindings;
            // $query->time;
            // $query->toRawSql();
        });
    }
}
```

The listener is registered on the connection the manager hands out, so `app('db')->listen(...)` listens to the default connection; call `app('db')->connection('pgsql')->listen(...)` to listen to another.

### Monitoring Cumulative Query Time

A common performance bottleneck of modern applications is the amount of time they spend querying databases. Thankfully, Venusian can invoke a closure or callback of your choice when a connection spends too much time querying the database. To get started, provide a query time threshold (in milliseconds) and closure to the `whenQueryingForLongerThan` method. You may invoke this method in the `boot` method of a [service provider](/docs/{{version}}/framework/architecture-concepts/providers):

```php
<?php

namespace App\Providers;

use Voyager\Database\Connection;
use Voyager\Database\Events\QueryExecuted;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // ...
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        app('db')->whenQueryingForLongerThan(500, function (Connection $connection, QueryExecuted $event) {
            // Notify development team...
        });
    }
}
```

The threshold is measured against the connection's total query time, and each handler runs once. A queue worker lets the handlers run again after every job it processes.

<a id="database-transactions"></a>
## Database Transactions

You may use the `transaction` method to run a set of operations within a database transaction. If an exception is thrown within the transaction closure, the transaction will automatically be rolled back and the exception is re-thrown. If the closure executes successfully, the transaction will automatically be committed. You don't need to worry about manually rolling back or committing while using the `transaction` method:

```php
app('db')->transaction(function () {
    app('db')->update('update users set votes = 1');

    app('db')->delete('delete from posts');
});
```

#### Handling Deadlocks

The `transaction` method accepts an optional second argument which defines the number of times a transaction should be retried when a deadlock occurs. Once these attempts have been exhausted, an exception will be thrown:

```php
app('db')->transaction(function () {
    app('db')->update('update users set votes = 1');

    app('db')->delete('delete from posts');
}, attempts: 5);
```

#### Manually Using Transactions

If you would like to begin a transaction manually and have complete control over rollbacks and commits, you may use the `beginTransaction` method:

```php
app('db')->beginTransaction();
```

You can rollback the transaction via the `rollBack` method:

```php
app('db')->rollBack();
```

Lastly, you can commit a transaction via the `commit` method:

```php
app('db')->commit();
```

> [!NOTE]
> A connection's transaction methods control the transactions for both the [query builder](/docs/{{version}}/framework/database/queries) and [Instrument ORM](/docs/{{version}}/framework/instrument-orm/instrument).

## Offloading Queries to Worker Pools

PDO never yields, so every query above blocks the process until the database answers. When your code runs on the event loop, a connection's `via` method moves its raw statements into a worker pool instead: the worker runs the blocking call, and you receive a `Voyager\Contracts\IOPools\Promise` of the result while the loop keeps running:

```php
$connection = app('db')->connection('pgsql');

$users = $connection->via()->select('select * from users where active = ?', [1]);

$affected = $connection->via()->update('update users set votes = 100 where name = ?', ['Anita']);

$users->wait(); // the same array select() returns
```

An offloaded connection accepts the reads `select`, `selectOne`, `selectFromWriteConnection`, and `scalar`, and the writes `insert`, `update`, `delete`, `statement`, `affectingStatement`, and `unprepared`. Any other method throws a `BadMethodCallException`. Query builder and Instrument queries offload the same way; see [offloading queries](/docs/{{version}}/framework/database/queries#offloading-queries-to-worker-pools).

The `via` method takes the pool to use: `'process'` for the process workers or `'thread'` for the thread workers. With no argument, it picks the thread workers when they are enabled and the process workers otherwise. The pools are switched on in your application's `config/io-pools.php` file; the process workers are enabled by default:

```php
'pool_workers' => [
    'process' => [
        'enabled' => true,
        'max_workers' => env('IO_POOLS_PROCESS_WORKERS', 4),
    ],
    'threads' => [
        'enabled' => false,
        'max_workers' => env('IO_POOLS_THREAD_WORKERS', 4),
    ],
],
```

The thread workers need a ZTS build of PHP with ext-parallel loaded. Naming a pool that is not enabled throws an `InvalidArgumentException`.

Each call carries the connection's name and its current configuration to the worker, so a connection whose configuration you changed at runtime is the one the worker queries. A connection can not be offloaded when the worker could not reach the same database: a connection with no name, an in-memory SQLite database (`:memory:`), or a connection with a transaction open all throw a `LogicException`.

#### Offloading Transactions

To run a whole transaction in a worker, pass a closure to the offloaded connection's `transaction` method. The closure runs inside the worker's own `transaction` call and receives that worker's connection; its return value resolves the promise. When the closure throws, the worker rolls the transaction back and the promise rejects with a `Voyager\Contracts\IOPools\WorkerPools\RemoteException`:

```php
use Voyager\Database\Connection;

$count = app('db')->connection('pgsql')->via()->transaction(static function (Connection $worker) {
    $worker->table('orders')->insert(['status' => 'paid']);

    return $worker->table('orders')->count();
}, attempts: 3);

$count->wait();
```

The closure crosses to the worker serialized, and it keeps the class it was written in as its scope, so that class must be one your application can load in the worker. `beginTransaction` can not be offloaded on its own and throws a `BadMethodCallException`.

#### Ordering Offloaded Calls

Venusian keeps the calls offloaded on one connection in order. Offloaded reads run beside each other; an offloaded write waits for every call offloaded before it, and every call after it waits for the write. Different connections run side by side. Blocking calls take part as well: a blocking `select` waits for the writes you offloaded on that connection, and a blocking `statement`, `affectingStatement`, `unprepared`, or `beginTransaction` waits for everything offloaded before it. A read always sees the writes you made before it, whichever way each was sent:

```php
$connection = app('db')->connection('pgsql');

$connection->via()->insert('insert into users (name) values (?)', ['offloaded']);

// Waits for the offloaded insert first...
$users = $connection->select('select * from users');
```

## Inspecting Your Databases

You may use the following schema builder methods to inspect your database:

```php
$schema = app('db.schema');

$tables = $schema->getTables();
$views = $schema->getViews();
$columns = $schema->getColumns('users');
$indexes = $schema->getIndexes('users');
$foreignKeys = $schema->getForeignKeys('users');
```

If you would like to inspect a database connection that is not your application's default connection, you may ask that connection for its schema builder:

```php
$columns = app('db')->connection('sqlite')->getSchemaBuilder()->getColumns('users');
```
