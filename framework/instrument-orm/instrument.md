# Instrument: Getting Started

Venusian includes Instrument, an object-relational mapper (ORM) that makes it enjoyable to interact with your database.

## Introduction

Venusian includes Instrument, an object-relational mapper (ORM) that makes it enjoyable to interact with your database. When using Instrument, each database table has a corresponding "Model" that is used to interact with that table. In addition to retrieving records from the database table, Instrument models allow you to insert, update, and delete records from the table as well.

> [!NOTE]
> Before getting started, be sure to configure a database connection in your application's `config/database.php` configuration file. For more information on configuring your database, check out [the database configuration documentation](/docs/{{version}}/framework/database/database#configuration).

## Defining Model Classes

To get started, let's create an Instrument model. Models typically live in the `app/Models` directory and extend the `Voyager\Database\Instrument\Model` class. Venusian has no generator command for models, so create the class by hand. The `make:migration` and `make:factory` [Computer commands](/docs/{{version}}/framework/digging-deeper/computer) generate the [migration](/docs/{{version}}/framework/database/migrations) and [factory](/docs/{{version}}/framework/instrument-orm/instrument-factories) that usually accompany a model; [seeders](/docs/{{version}}/framework/database/seeding) are written by hand:

```shell
php computer make:migration create_flights_table
php computer make:factory FlightFactory --model=Flight
```

## Instrument Model Conventions

Models live in the `app/Models` directory by convention. Let's examine a basic model class and discuss some of Instrument's key conventions:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    // ...
}
```

### Table Names

After glancing at the example above, you may have noticed that we did not tell Instrument which database table corresponds to our `Flight` model. By convention, the "snake case", plural name of the class will be used as the table name unless another name is explicitly specified. So, in this case, Instrument will assume the `Flight` model stores records in the `flights` table, while an `AirTrafficController` model would store records in an `air_traffic_controllers` table.

If your model's corresponding database table does not fit this convention, you may manually specify the model's table name by defining a `table` property on the model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'my_flights';
}
```

### Primary Keys

Instrument will also assume that each model's corresponding database table has a primary key column named `id`. If necessary, you may define a protected `$primaryKey` property on your model to specify a different column that serves as your model's primary key:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    /**
     * The primary key associated with the table.
     *
     * @var string
     */
    protected $primaryKey = 'flight_id';
}
```

In addition, Instrument assumes that the primary key is an incrementing integer value, which means that Instrument will automatically cast the primary key to an integer. If you wish to use a non-incrementing or a non-numeric primary key, you must define a public `$incrementing` property on your model that is set to `false`:

```php
<?php

class Flight extends Model
{
    /**
     * Indicates if the model's ID is auto-incrementing.
     *
     * @var bool
     */
    public $incrementing = false;
}
```

If your model's primary key is not an integer, you should define a protected `$keyType` property on your model. This property should have a value of `string`:

```php
<?php

class Flight extends Model
{
    /**
     * The data type of the primary key ID.
     *
     * @var string
     */
    protected $keyType = 'string';
}
```

#### "Composite" Primary Keys

Instrument requires each model to have at least one uniquely identifying "ID" that can serve as its primary key. "Composite" primary keys are not supported by Instrument models. However, you are free to add additional multi-column, unique indexes to your database tables in addition to the table's uniquely identifying primary key.

### UUID and ULID Keys

Instead of using auto-incrementing integers as your Instrument model's primary keys, you may choose to use UUIDs instead. UUIDs are universally unique alpha-numeric identifiers that are 36 characters long.

If you would like a model to use a UUID key instead of an auto-incrementing integer key, you may use the `Voyager\Database\Instrument\Concerns\HasUuids` trait on the model. Of course, you should ensure that the model has a [UUID equivalent primary key column](/docs/{{version}}/framework/database/migrations#column-method-uuid):

```php
use Voyager\Database\Instrument\Concerns\HasUuids;
use Voyager\Database\Instrument\Model;

class Article extends Model
{
    use HasUuids;

    // ...
}

$article = Article::create(['title' => 'Traveling to Europe']);

$article->id; // "018f2b5c-6a7f-7b12-9d6f-2f8a4e0c9c11"
```

By default, the `HasUuids` trait will generate [UUIDv7](/docs/{{version}}/framework/digging-deeper/strings#method-str-uuid7) identifiers for your models. These UUIDs are more efficient for indexed database storage because they can be sorted lexicographically.

You can override the UUID generation process for a given model by defining a `newUniqueId` method on the model. In addition, you may specify which columns should receive UUIDs by defining a `uniqueIds` method on the model:

```php
use Ramsey\Uuid\Uuid;

/**
 * Generate a new UUID for the model.
 */
public function newUniqueId(): string
{
    return (string) Uuid::uuid4();
}

/**
 * Get the columns that should receive a unique identifier.
 *
 * @return array<int, string>
 */
public function uniqueIds(): array
{
    return ['id', 'discount_code'];
}
```

If you wish, you may choose to utilize "ULIDs" instead of UUIDs. ULIDs are similar to UUIDs; however, they are only 26 characters in length. Like ordered UUIDs, ULIDs are lexicographically sortable for efficient database indexing. To utilize ULIDs, you should use the `Voyager\Database\Instrument\Concerns\HasUlids` trait on your model. You should also ensure that the model has a [ULID equivalent primary key column](/docs/{{version}}/framework/database/migrations#column-method-ulid):

```php
use Voyager\Database\Instrument\Concerns\HasUlids;
use Voyager\Database\Instrument\Model;

class Article extends Model
{
    use HasUlids;

    // ...
}

$article = Article::create(['title' => 'Traveling to Asia']);

$article->id; // "01gd4d3tgrrfqeda94gdbtdk5c"
```

### Timestamps

By default, Instrument expects `created_at` and `updated_at` columns to exist on your model's corresponding database table. Instrument will automatically set these column's values when models are created or updated. If you do not want these columns to be automatically managed by Instrument, you should define a `$timestamps` property on your model with a value of `false`:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    /**
     * Indicates if the model should be timestamped.
     *
     * @var bool
     */
    public $timestamps = false;
}
```

If you need to customize the format of your model's timestamps, set the `$dateFormat` property on your model. This property determines how date attributes are stored in the database as well as their format when the model is serialized to an array or JSON:

```php
<?php

class Flight extends Model
{
    /**
     * The storage format of the model's date columns.
     *
     * @var string
     */
    protected $dateFormat = 'U';
}
```

If you need to customize the names of the columns used to store the timestamps, you may define `CREATED_AT` and `UPDATED_AT` constants on your model:

```php
<?php

class Flight extends Model
{
    /**
     * The name of the "created at" column.
     *
     * @var string|null
     */
    public const CREATED_AT = 'creation_date';

    /**
     * The name of the "updated at" column.
     *
     * @var string|null
     */
    public const UPDATED_AT = 'updated_date';
}
```

If you would like to perform model operations without the model having its `updated_at` timestamp modified, you may operate on the model within a closure given to the `withoutTimestamps` method:

```php
Model::withoutTimestamps(fn () => $post->increment('reads'));
```

### Database Connections

By default, all Instrument models will use the default database connection that is configured for your application. If you would like to specify a different connection that should be used when interacting with a particular model, you should define a `$connection` property on the model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    /**
     * The database connection that should be used by the model.
     *
     * @var string
     */
    protected $connection = 'mysql';
}
```

### Default Attribute Values

By default, a newly instantiated model instance will not contain any attribute values. If you would like to define the default values for some of your model's attributes, you may define an `$attributes` property on your model. Attribute values placed in the `$attributes` array should be in their raw, "storable" format as if they were just read from the database:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    /**
     * The model's default values for attributes.
     *
     * @var array<string, mixed>
     */
    protected $attributes = [
        'options' => '[]',
        'delayed' => false,
    ];
}
```

### Configuring Instrument Strictness

Venusian offers several methods that allow you to configure Instrument's behavior and "strictness" in a variety of situations.

First, the `preventLazyLoading` method accepts an optional boolean argument that indicates if lazy loading should be prevented. For example, you may wish to only disable lazy loading in non-production environments so that your production environment will continue to function normally even if a lazy loaded relationship is accidentally present in production code. Typically, this method should be invoked in the `boot` method of your application's `AppServiceProvider`:

```php
use Voyager\Database\Instrument\Model;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Model::preventLazyLoading(! $this->app->environment('production'));
}
```

Also, you may instruct Instrument to throw an exception when attempting to fill an unfillable attribute by invoking the `preventSilentlyDiscardingAttributes` method. This can help prevent unexpected errors during local development when attempting to set an attribute that has not been added to the model's `fillable` array:

```php
Model::preventSilentlyDiscardingAttributes(! $this->app->environment('production'));
```

## Retrieving Models

Once you have created a model and [its associated database table](/docs/{{version}}/framework/database/migrations#generating-migrations), you are ready to start retrieving data from your database. You can think of each Instrument model as a powerful [query builder](/docs/{{version}}/framework/database/queries) allowing you to fluently query the database table associated with the model. The model's `all` method will retrieve all of the records from the model's associated database table:

```php
use App\Models\Flight;

foreach (Flight::all() as $flight) {
    echo $flight->name;
}
```

#### Building Queries

The Instrument `all` method will return all of the results in the model's table. However, since each Instrument model serves as a [query builder](/docs/{{version}}/framework/database/queries), you may add additional constraints to queries and then invoke the `get` method to retrieve the results:

```php
$flights = Flight::where('active', 1)
    ->orderBy('name')
    ->limit(10)
    ->get();
```

> [!NOTE]
> Since Instrument models are query builders, you should review all of the methods provided by the [query builder](/docs/{{version}}/framework/database/queries). You may use any of these methods when writing your Instrument queries.

#### Refreshing Models

If you already have an instance of an Instrument model that was retrieved from the database, you can "refresh" the model using the `fresh` and `refresh` methods. The `fresh` method will re-retrieve the model from the database. The existing model instance will not be affected:

```php
$flight = Flight::where('number', 'FR 900')->first();

$freshFlight = $flight->fresh();
```

The `refresh` method will re-hydrate the existing model using fresh data from the database. In addition, all of its loaded relationships will be refreshed as well:

```php
$flight = Flight::where('number', 'FR 900')->first();

$flight->number = 'FR 456';

$flight->refresh();

$flight->number; // "FR 900"
```

### Collections

As we have seen, Instrument methods like `all` and `get` retrieve multiple records from the database. However, these methods don't return a plain PHP array. Instead, an instance of `Voyager\Database\Instrument\Collection` is returned.

The Instrument `Collection` class extends the base `Voyager\NutsAndBolts\Collection` class, which provides a [variety of helpful methods](/docs/{{version}}/framework/digging-deeper/collections#available-methods) for interacting with data collections. For example, the `reject` method may be used to remove models from a collection based on the results of an invoked closure:

```php
$flights = Flight::where('destination', 'Paris')->get();

$flights = $flights->reject(function (Flight $flight) {
    return $flight->cancelled;
});
```

In addition to the methods provided by the base collection class, the Instrument collection class provides [a few extra methods](/docs/{{version}}/framework/instrument-orm/instrument-collections#available-methods) that are specifically intended for interacting with collections of Instrument models.

Since all of Venusian's collections implement PHP's iterable interfaces, you may loop over collections as if they were an array:

```php
foreach ($flights as $flight) {
    echo $flight->name;
}
```

<a id="chunking-results"></a>
### Chunking Results

Your application may run out of memory if you attempt to load tens of thousands of Instrument records via the `all` or `get` methods. Instead of using these methods, the `chunk` method may be used to process large numbers of models more efficiently.

The `chunk` method will retrieve a subset of Instrument models, passing them to a closure for processing. Since only the current chunk of Instrument models is retrieved at a time, the `chunk` method will provide significantly reduced memory usage when working with a large number of models:

```php
use App\Models\Flight;
use Voyager\Database\Instrument\Collection;

Flight::chunk(200, function (Collection $flights) {
    foreach ($flights as $flight) {
        // ...
    }
});
```

The first argument passed to the `chunk` method is the number of records you wish to receive per "chunk". The closure passed as the second argument will be invoked for each chunk that is retrieved from the database. A database query will be executed to retrieve each chunk of records passed to the closure.

If you are filtering the results of the `chunk` method based on a column that you will also be updating while iterating over the results, you should use the `chunkById` method. Using the `chunk` method in these scenarios could lead to unexpected and inconsistent results. Internally, the `chunkById` method will always retrieve models with an `id` column greater than the last model in the previous chunk:

```php
Flight::where('departed', true)
    ->chunkById(200, function (Collection $flights) {
        $flights->each->update(['departed' => false]);
    }, column: 'id');
```

Since the `chunkById` and `lazyById` methods add their own "where" conditions to the query being executed, you should typically [logically group](/docs/{{version}}/framework/database/queries#logical-grouping) your own conditions within a closure:

```php
Flight::where(function ($query) {
    $query->where('delayed', true)->orWhere('cancelled', true);
})->chunkById(200, function (Collection $flights) {
    $flights->each->update([
        'departed' => false,
        'cancelled' => true
    ]);
}, column: 'id');
```

<a id="chunking-using-lazy-collections"></a>
### Chunking Using Lazy Collections

The `lazy` method works similarly to [the `chunk` method](#chunking-results) in the sense that, behind the scenes, it executes the query in chunks. However, instead of passing each chunk directly into a callback as is, the `lazy` method returns a flattened [LazyCollection](/docs/{{version}}/framework/digging-deeper/collections#lazy-collections) of Instrument models, which lets you interact with the results as a single stream:

```php
use App\Models\Flight;

foreach (Flight::lazy() as $flight) {
    // ...
}
```

If you are filtering the results of the `lazy` method based on a column that you will also be updating while iterating over the results, you should use the `lazyById` method. Internally, the `lazyById` method will always retrieve models with an `id` column greater than the last model in the previous chunk:

```php
Flight::where('departed', true)
    ->lazyById(200, column: 'id')
    ->each->update(['departed' => false]);
```

You may filter the results based on the descending order of the `id` using the `lazyByIdDesc` method.

### Cursors

Similar to the `lazy` method, the `cursor` method may be used to significantly reduce your application's memory consumption when iterating through tens of thousands of Instrument model records.

The `cursor` method will only execute a single database query; however, the individual Instrument models will not be hydrated until they are actually iterated over. Therefore, only one Instrument model is kept in memory at any given time while iterating over the cursor.

> [!WARNING]
> Since the `cursor` method only ever holds a single Instrument model in memory at a time, it cannot eager load relationships. If you need to eager load relationships, consider using [the `lazy` method](#chunking-using-lazy-collections) instead.

Internally, the `cursor` method uses PHP [generators](https://www.php.net/manual/en/language.generators.overview.php) to implement this functionality:

```php
use App\Models\Flight;

foreach (Flight::where('destination', 'Zurich')->cursor() as $flight) {
    // ...
}
```

The `cursor` returns an `Voyager\NutsAndBolts\LazyCollection` instance. [Lazy collections](/docs/{{version}}/framework/digging-deeper/collections#lazy-collections) allow you to use many of the collection methods available on typical collections while only loading a single model into memory at a time:

```php
use App\Models\User;

$users = User::cursor()->filter(function (User $user) {
    return $user->id > 500;
});

foreach ($users as $user) {
    echo $user->id;
}
```

Although the `cursor` method uses far less memory than a regular query (by only holding a single Instrument model in memory at a time), it will still eventually run out of memory. This is [due to PHP's PDO driver internally caching all raw query results in its buffer](https://www.php.net/manual/en/mysqlinfo.concepts.buffering.php). If you're dealing with a very large number of Instrument records, consider using [the `lazy` method](#chunking-using-lazy-collections) instead.

### Running Queries Off the Loop

PDO blocks while a query runs, so a query made on the event loop's thread holds up everything else the loop is doing. Calling `via` on an Instrument query runs the query's terminal method in a worker instead. The terminal returns a `Voyager\Contracts\IOPools\Promise` that settles with the value the blocking call would have returned:

```php
use App\Models\Flight;
use Voyager\Database\Instrument\Collection;

Flight::where('active', 1)
    ->orderBy('name')
    ->via()
    ->get()
    ->then(function (Collection $flights) {
        foreach ($flights as $flight) {
            echo $flight->name;
        }
    });
```

Build the query first, then call `via`. The query is captured when the terminal is called, so a method that builds rather than runs, such as `where`, rejects the promise with a `LogicException` when it is called after `via`. Reading terminals (`get`, `first`, `find`, `findOrFail`, `firstWhere`, `value`, `pluck`, `count`, `sum`, `max`, `exists`, `paginate`, and the rest) and writing terminals (`insert`, `update`, `delete`, `create`, `upsert`, and the rest) may all be offloaded:

```php
$count = Flight::where('active', 1)->via()->count();

$flight = Flight::query()->via()->create(['name' => 'London to Paris']);

Flight::where('destination', 'San Diego')->via()->update(['delayed' => 1]);
```

Where nothing else needs the loop, such as inside a command, the promise's `wait` method blocks until it settles and returns the result, or throws if the query failed. On the loop, register an `error` callback instead:

```php
$flights = Flight::where('active', 1)->via()->get()->wait();

Flight::query()->via()->findOrFail(1)
    ->then(fn (Flight $flight) => $flight->name)
    ->error(function (Throwable $e) {
        // ...
    });
```

Models come back from the worker with `exists` set, and the `retrieved` [Signal](#signals) fires in your process, once for each model, as they arrive. The worker does not fire it.

Calls offloaded on the same connection keep their order: reads run beside one another, while a write waits for everything offloaded before it, and everything offloaded after it waits for the write. A blocking query on that connection also waits for the offloaded writes made before it, so a read always sees them.

By default, `via` sends the query to the thread workers when `io-pools.pool_workers.threads.enabled` is on, and to the process workers otherwise. You may name the pool with `via('thread')` or `via('process')`; naming a pool that is not enabled throws an `InvalidArgumentException`.

> [!WARNING]
> `via` throws a `LogicException` when the connection cannot be reached from a worker: an in-memory SQLite connection (a worker would open a different, empty database) or a connection with a transaction open (the worker's write would land outside it). The `chunk`, `chunkById`, `lazy`, `lazyById`, `cursor`, and `each` methods take a callback or yield, which cannot cross to a worker, so calling them after `via` throws a `BadMethodCallException`. Use `stream` for those instead.

#### Streaming Models

The `stream` method pages through a query in a worker, a chunk at a time, keyed on the model's primary key, and posts each page to the loop as a `Voyager\Database\IOPools\QueryChunk` mail named `db-chunk:{connection}:{table}`. Each chunk carries its `page` number, its `rows` as an Instrument collection, and a `last` flag that is `true` on the final page. The promise `stream` returns settles with the total number of rows:

```php
use App\Models\Flight;
use Voyager\Database\IOPools\QueryChunk;

app('signals')->listen('db-chunk:sqlite:flights', function (QueryChunk $chunk) {
    foreach ($chunk->rows as $flight) {
        // ...
    }

    if ($chunk->last) {
        // ...
    }
});

Flight::where('active', 1)->stream(200)->then(function (int $count) {
    // ...
});
```

The `stream` method accepts the chunk size, the column to page by, and the pool as its arguments: `stream(int $chunk = 1000, ?string $column = null, ?string $pool = null)`. A query with no rows posts a single, empty chunk marked `last`.

### Advanced Subqueries

#### Subquery Selects

Instrument also offers advanced subquery support, which allows you to pull information from related tables in a single query. For example, let's imagine that we have a table of flight `destinations` and a table of `flights` to destinations. The `flights` table contains an `arrived_at` column which indicates when the flight arrived at the destination.

Using the subquery functionality available to the query builder's `select` and `addSelect` methods, we can select all of the `destinations` and the name of the flight that most recently arrived at that destination using a single query:

```php
use App\Models\Destination;
use App\Models\Flight;

return Destination::addSelect(['last_flight' => Flight::select('name')
    ->whereColumn('destination_id', 'destinations.id')
    ->orderByDesc('arrived_at')
    ->limit(1)
])->get();
```

#### Subquery Ordering

In addition, the query builder's `orderBy` function supports subqueries. Continuing to use our flight example, we may use this functionality to sort all destinations based on when the last flight arrived at that destination. Again, this may be done while executing a single database query:

```php
return Destination::orderByDesc(
    Flight::select('arrived_at')
        ->whereColumn('destination_id', 'destinations.id')
        ->orderByDesc('arrived_at')
        ->limit(1)
)->get();
```

## Retrieving Single Models / Aggregates

In addition to retrieving all of the records matching a given query, you may also retrieve single records using the `find`, `first`, or `firstWhere` methods. Instead of returning a collection of models, these methods return a single model instance:

```php
use App\Models\Flight;

// Retrieve a model by its primary key...
$flight = Flight::find(1);

// Retrieve the first model matching the query constraints...
$flight = Flight::where('active', 1)->first();

// Alternative to retrieving the first model matching the query constraints...
$flight = Flight::firstWhere('active', 1);
```

Sometimes you may wish to perform some other action if no results are found. The `findOr` and `firstOr` methods will return a single model instance or, if no results are found, execute the given closure. The value returned by the closure will be considered the result of the method:

```php
$flight = Flight::findOr(1, function () {
    // ...
});

$flight = Flight::where('legs', '>', 3)->firstOr(function () {
    // ...
});
```

#### Not Found Exceptions

Sometimes you may wish to throw an exception if a model is not found. The `findOrFail` and `firstOrFail` methods will retrieve the first result of the query; however, if no result is found, an `Voyager\Database\Instrument\ModelNotFoundException` will be thrown:

```php
$flight = Flight::findOrFail(1);

$flight = Flight::where('legs', '>', 3)->firstOrFail();
```

### Retrieving or Creating Models

The `firstOrCreate` method will attempt to locate a database record using the given column / value pairs. If the model cannot be found in the database, a record will be inserted with the attributes resulting from merging the first array argument with the optional second array argument.

The `firstOrNew` method, like `firstOrCreate`, will attempt to locate a record in the database matching the given attributes. However, if a model is not found, a new model instance will be returned. Note that the model returned by `firstOrNew` has not yet been persisted to the database. You will need to manually call the `save` method to persist it:

```php
use App\Models\Flight;

// Retrieve flight by name or create it if it doesn't exist...
$flight = Flight::firstOrCreate([
    'name' => 'London to Paris'
]);

// Retrieve flight by name or create it with the name, delayed, and arrival_time attributes...
$flight = Flight::firstOrCreate(
    ['name' => 'London to Paris'],
    ['delayed' => 1, 'arrival_time' => '11:30']
);

// Retrieve flight by name or instantiate a new Flight instance...
$flight = Flight::firstOrNew([
    'name' => 'London to Paris'
]);

// Retrieve flight by name or instantiate with the name, delayed, and arrival_time attributes...
$flight = Flight::firstOrNew(
    ['name' => 'Tokyo to Sydney'],
    ['delayed' => 1, 'arrival_time' => '11:30']
);
```

### Retrieving Aggregates

When interacting with Instrument models, you may also use the `count`, `sum`, `max`, and other [aggregate methods](/docs/{{version}}/framework/database/queries#aggregates) provided by the [query builder](/docs/{{version}}/framework/database/queries). As you might expect, these methods return a scalar value instead of an Instrument model instance:

```php
$count = Flight::where('active', 1)->count();

$max = Flight::where('active', 1)->max('price');
```

## Inserting and Updating Models

### Inserts

Of course, when using Instrument, we don't only need to retrieve models from the database. We also need to insert new records. Thankfully, Instrument makes it simple. To insert a new record into the database, you should instantiate a new model instance and set attributes on the model. Then, call the `save` method on the model instance:

```php
use App\Models\Flight;

$flight = new Flight;

$flight->name = 'London to Paris';

$flight->save();
```

In this example, we assign a value to the `name` attribute of the `App\Models\Flight` model instance. When we call the `save` method, a record will be inserted into the database. The model's `created_at` and `updated_at` timestamps will automatically be set when the `save` method is called, so there is no need to set them manually.

If you would like to save the model within a database transaction, you may use the `saveOrFail` method. If an exception is thrown during the save, the transaction will automatically be rolled back:

```php
$flight->saveOrFail();
```

Alternatively, you may use the `create` method to "save" a new model using a single PHP statement. The inserted model instance will be returned to you by the `create` method:

```php
use App\Models\Flight;

$flight = Flight::create([
    'name' => 'London to Paris',
]);
```

However, before using the `create` method, you will need to specify either a `fillable` or `guarded` property on your model class. These properties are required because all Instrument models are protected against mass assignment vulnerabilities by default. To learn more about mass assignment, please consult the [mass assignment documentation](#mass-assignment).

### Updates

The `save` method may also be used to update models that already exist in the database. To update a model, you should retrieve it and set any attributes you wish to update. Then, you should call the model's `save` method. Again, the `updated_at` timestamp will automatically be updated, so there is no need to manually set its value:

```php
use App\Models\Flight;

$flight = Flight::find(1);

$flight->name = 'Paris to London';

$flight->save();
```

If you would like to update the model within a database transaction, you may use the `updateOrFail` method. If an exception is thrown during the update, the transaction will automatically be rolled back:

```php
$flight->updateOrFail(['name' => 'Paris to London']);
```

Occasionally, you may need to update an existing model or create a new model if no matching model exists. Like the `firstOrCreate` method, the `updateOrCreate` method persists the model, so there's no need to manually call the `save` method.

In the example below, if a flight exists with a `departure` location of `Oakland` and a `destination` location of `San Diego`, its `price` and `discounted` columns will be updated. If no such flight exists, a new flight will be created which has the attributes resulting from merging the first argument array with the second argument array:

```php
$flight = Flight::updateOrCreate(
    ['departure' => 'Oakland', 'destination' => 'San Diego'],
    ['price' => 99, 'discounted' => 1]
);
```

When using methods such as `firstOrCreate` or `updateOrCreate`, you may not know whether a new model has been created or an existing one has been updated. The `wasRecentlyCreated` property indicates if the model was created during its current lifecycle:

```php
$flight = Flight::updateOrCreate(
    // ...
);

if ($flight->wasRecentlyCreated) {
    // New flight record was inserted...
}
```

#### Mass Updates

Updates can also be performed against models that match a given query. In this example, all flights that are `active` and have a `destination` of `San Diego` will be marked as delayed:

```php
Flight::where('active', 1)
    ->where('destination', 'San Diego')
    ->update(['delayed' => 1]);
```

The `update` method expects an array of column and value pairs representing the columns that should be updated. The `update` method returns the number of affected rows.

> [!WARNING]
> When issuing a mass update via Instrument, the `saving`, `saved`, `updating`, and `updated` model Signals will not be fired for the updated models. This is because the models are never actually retrieved when issuing a mass update.

#### Examining Attribute Changes

Instrument provides the `isDirty`, `isClean`, and `wasChanged` methods to examine the internal state of your model and determine how its attributes have changed from when the model was originally retrieved.

The `isDirty` method determines if any of the model's attributes have been changed since the model was retrieved. You may pass a specific attribute name or an array of attributes to the `isDirty` method to determine if any of the attributes are "dirty". The `isClean` method will determine if an attribute has remained unchanged since the model was retrieved. This method also accepts an optional attribute argument:

```php
use App\Models\User;

$user = User::create([
    'first_name' => 'Taylor',
    'last_name' => 'Otwell',
    'title' => 'Developer',
]);

$user->title = 'Painter';

$user->isDirty(); // true
$user->isDirty('title'); // true
$user->isDirty('first_name'); // false
$user->isDirty(['first_name', 'title']); // true

$user->isClean(); // false
$user->isClean('title'); // false
$user->isClean('first_name'); // true
$user->isClean(['first_name', 'title']); // false

$user->save();

$user->isDirty(); // false
$user->isClean(); // true
```

The `wasChanged` method determines if any attributes were changed when the model was last saved within the current process. If needed, you may pass an attribute name to see if a particular attribute was changed:

```php
$user = User::create([
    'first_name' => 'Taylor',
    'last_name' => 'Otwell',
    'title' => 'Developer',
]);

$user->title = 'Painter';

$user->save();

$user->wasChanged(); // true
$user->wasChanged('title'); // true
$user->wasChanged(['title', 'slug']); // true
$user->wasChanged('first_name'); // false
$user->wasChanged(['first_name', 'title']); // true
```

The `getOriginal` method returns an array containing the original attributes of the model regardless of any changes to the model since it was retrieved. If needed, you may pass a specific attribute name to get the original value of a particular attribute:

```php
$user = User::find(1);

$user->name; // John
$user->email; // john@example.com

$user->name = 'Jack';
$user->name; // Jack

$user->getOriginal('name'); // John
$user->getOriginal(); // Array of original attributes...
```

The `getChanges` method returns an array containing the attributes that changed when the model was last saved, while the `getPrevious` method returns an array containing the original attribute values before the model was last saved:

```php
$user = User::find(1);

$user->name; // John
$user->email; // john@example.com

$user->update([
    'name' => 'Jack',
    'email' => 'jack@example.com',
]);

$user->getChanges();

/*
    [
        'name' => 'Jack',
        'email' => 'jack@example.com',
    ]
*/

$user->getPrevious();

/*
    [
        'name' => 'John',
        'email' => 'john@example.com',
    ]
*/
```

<a id="mass-assignment"></a>
### Mass Assignment

You may use the `create` method to "save" a new model using a single PHP statement. The inserted model instance will be returned to you by the method:

```php
use App\Models\Flight;

$flight = Flight::create([
    'name' => 'London to Paris',
]);
```

However, before using the `create` method, you will need to specify either a `fillable` or `guarded` property on your model class. These properties are required because all Instrument models are protected against mass assignment vulnerabilities by default.

A mass assignment vulnerability occurs when outside input carries an unexpected field and that field changes a column in your database that you did not expect. For example, a malicious payload might include an `is_admin` field which is then passed to your model's `create` method, allowing its sender to escalate themselves to an administrator.

So, to get started, you should define which model attributes you want to make mass assignable. You may do this using the `$fillable` property on the model. For example, let's make the `name` attribute of our `Flight` model mass assignable:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = ['name'];
}
```

Once you have specified which attributes are mass assignable, you may use the `create` method to insert a new record in the database. The `create` method returns the newly created model instance:

```php
$flight = Flight::create(['name' => 'London to Paris']);
```

If you already have a model instance, you may use the `fill` method to populate it with an array of attributes:

```php
$flight->fill(['name' => 'Amsterdam to Frankfurt']);
```

#### Mass Assignment and JSON Columns

When assigning JSON columns, each column's mass assignable key must be specified in your model's `$fillable` array. For security, Instrument does not support updating nested JSON attributes when using the `$guarded` property:

```php
/**
 * The attributes that are mass assignable.
 *
 * @var array<int, string>
 */
protected $fillable = [
    'options->enabled',
];
```

#### Allowing Mass Assignment

If you would like to make all of your attributes mass assignable, you may define your model's `$guarded` property as an empty array. If you choose to unguard your model, you should take special care to always hand-craft the arrays passed to Instrument's `fill`, `create`, and `update` methods:

```php
/**
 * The attributes that aren't mass assignable.
 *
 * @var array<string>|bool
 */
protected $guarded = [];
```

#### Mass Assignment Exceptions

By default, attributes that are not included in the `$fillable` array are silently discarded when performing mass-assignment operations. In production, this is expected behavior; however, during local development it can lead to confusion as to why model changes are not taking effect.

If you wish, you may instruct Instrument to throw an exception when attempting to fill an unfillable attribute by invoking the `preventSilentlyDiscardingAttributes` method. Typically, this method should be invoked in the `boot` method of your application's `AppServiceProvider` class:

```php
use Voyager\Database\Instrument\Model;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Model::preventSilentlyDiscardingAttributes($this->app->environment('local'));
}
```

<a id="upserts"></a>
### Upserts

Instrument's `upsert` method may be used to update or create records in a single, atomic operation. The method's first argument consists of the values to insert or update, while the second argument lists the column(s) that uniquely identify records within the associated table. The method's third and final argument is an array of the columns that should be updated if a matching record already exists in the database. The `upsert` method will automatically set the `created_at` and `updated_at` timestamps if timestamps are enabled on the model:

```php
Flight::upsert([
    ['departure' => 'Oakland', 'destination' => 'San Diego', 'price' => 99],
    ['departure' => 'Chicago', 'destination' => 'New York', 'price' => 150]
], uniqueBy: ['departure', 'destination'], update: ['price']);
```

> [!WARNING]
> All databases except SQL Server require the columns in the second argument of the `upsert` method to have a "primary" or "unique" index. In addition, the MariaDB and MySQL database drivers ignore the second argument of the `upsert` method and always use the "primary" and "unique" indexes of the table to detect existing records.

## Deleting Models

To delete a model, you may call the `delete` method on the model instance:

```php
use App\Models\Flight;

$flight = Flight::find(1);

$flight->delete();
```

If you would like to delete the model within a database transaction, you may use the `deleteOrFail` method. If an exception is thrown during the delete, the transaction will automatically be rolled back:

```php
$flight->deleteOrFail();
```

#### Deleting an Existing Model by its Primary Key

In the example above, we are retrieving the model from the database before calling the `delete` method. However, if you know the primary key of the model, you may delete the model without explicitly retrieving it by calling the `destroy` method. In addition to accepting the single primary key, the `destroy` method will accept multiple primary keys, an array of primary keys, or a [collection](/docs/{{version}}/framework/digging-deeper/collections) of primary keys:

```php
Flight::destroy(1);

Flight::destroy(1, 2, 3);

Flight::destroy([1, 2, 3]);

Flight::destroy(collect([1, 2, 3]));
```

If you are utilizing [soft deleting models](#soft-deleting), you may permanently delete models via the `forceDestroy` method:

```php
Flight::forceDestroy(1);
```

> [!WARNING]
> The `destroy` method loads each model individually and calls the `delete` method so that the `deleting` and `deleted` Signals are properly dispatched for each model.

#### Deleting Models Using Queries

Of course, you may build an Instrument query to delete all models matching your query's criteria. In this example, we will delete all flights that are marked as inactive. Like mass updates, mass deletes will not dispatch model Signals for the models that are deleted:

```php
$deleted = Flight::where('active', 0)->delete();
```

To delete all models in a table, you should execute a query without adding any conditions:

```php
$deleted = Flight::query()->delete();
```

> [!WARNING]
> When executing a mass delete statement via Instrument, the `deleting` and `deleted` model Signals will not be dispatched for the deleted models. This is because the models are never actually retrieved when executing the delete statement.

<a id="soft-deleting"></a>
### Soft Deleting

In addition to actually removing records from your database, Instrument can also "soft delete" models. When models are soft deleted, they are not actually removed from your database. Instead, a `deleted_at` attribute is set on the model indicating the date and time at which the model was "deleted". To enable soft deletes for a model, add the `Voyager\Database\Instrument\SoftDeletes` trait to the model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;
use Voyager\Database\Instrument\SoftDeletes;

class Flight extends Model
{
    use SoftDeletes;
}
```

> [!NOTE]
> The `SoftDeletes` trait will automatically cast the `deleted_at` attribute to a `DateTime` / `Carbon` instance for you.

You should also add the `deleted_at` column to your database table. The [schema builder](/docs/{{version}}/framework/database/migrations) contains a helper method to create this column:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->table('flights', function (Blueprint $table) {
    $table->softDeletes();
});

app('db.schema')->table('flights', function (Blueprint $table) {
    $table->dropSoftDeletes();
});
```

Now, when you call the `delete` method on the model, the `deleted_at` column will be set to the current date and time. However, the model's database record will be left in the table. When querying a model that uses soft deletes, the soft deleted models will automatically be excluded from all query results.

To determine if a given model instance has been soft deleted, you may use the `trashed` method:

```php
if ($flight->trashed()) {
    // ...
}
```

#### Restoring Soft Deleted Models

Sometimes you may wish to "un-delete" a soft deleted model. To restore a soft deleted model, you may call the `restore` method on a model instance. The `restore` method will set the model's `deleted_at` column to `null`:

```php
$flight->restore();
```

You may also use the `restore` method in a query to restore multiple models. Again, like other "mass" operations, this will not dispatch any model Signals for the models that are restored:

```php
Flight::withTrashed()
    ->where('airline_id', 1)
    ->restore();
```

The `restore` method may also be used when building [relationship](/docs/{{version}}/framework/instrument-orm/instrument-relationships) queries:

```php
$flight->history()->restore();
```

#### Permanently Deleting Models

Sometimes you may need to truly remove a model from your database. You may use the `forceDelete` method to permanently remove a soft deleted model from the database table:

```php
$flight->forceDelete();
```

You may also use the `forceDelete` method when building Instrument relationship queries:

```php
$flight->history()->forceDelete();
```

### Querying Soft Deleted Models

#### Including Soft Deleted Models

As noted above, soft deleted models will automatically be excluded from query results. However, you may force soft deleted models to be included in a query's results by calling the `withTrashed` method on the query:

```php
use App\Models\Flight;

$flights = Flight::withTrashed()
    ->where('account_id', 1)
    ->get();
```

The `withTrashed` method may also be called when building a [relationship](/docs/{{version}}/framework/instrument-orm/instrument-relationships) query:

```php
$flight->history()->withTrashed()->get();
```

#### Retrieving Only Soft Deleted Models

The `onlyTrashed` method will retrieve **only** soft deleted models:

```php
$flights = Flight::onlyTrashed()
    ->where('airline_id', 1)
    ->get();
```

## Pruning Models

Sometimes you may want to periodically delete models that are no longer needed. To accomplish this, you may add the `Voyager\Database\Instrument\Prunable` or `Voyager\Database\Instrument\MassPrunable` trait to the models you would like to periodically prune. After adding one of the traits to the model, implement a `prunable` method which returns an Instrument query builder that resolves the models that are no longer needed:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\Model;
use Voyager\Database\Instrument\Prunable;
use Voyager\NutsAndBolts\DataObjects\Carbon;

class Flight extends Model
{
    use Prunable;

    /**
     * Get the prunable model query.
     */
    public function prunable(): Builder
    {
        return static::where('created_at', '<=', Carbon::now()->subMonth());
    }
}
```

When marking models as `Prunable`, you may also define a `pruning` method on the model. This method will be called before the model is deleted. This method can be useful for deleting any additional resources associated with the model, such as stored files, before the model is permanently removed from the database:

```php
/**
 * Prepare the model for pruning.
 */
protected function pruning(): void
{
    // ...
}
```

After configuring your prunable model, call `pruneAll` on it whenever you want the records removed, for example from your own [Computer command](/docs/{{version}}/framework/digging-deeper/computer) or from a long-running sketch. It returns the number of records deleted:

```php
use App\Models\Flight;

$deleted = (new Flight)->pruneAll();
```

Records are deleted in chunks of 1,000 by default. You may pass a different chunk size:

```php
$deleted = (new Flight)->pruneAll(chunkSize: 500);
```

To see how many records would go without deleting anything, count the `prunable` query:

```php
$count = (new Flight)->prunable()->count();
```

> [!WARNING]
> Soft deleting models will be permanently deleted (`forceDelete`) if they match the prunable query.

#### Mass Pruning

When models are marked with the `Voyager\Database\Instrument\MassPrunable` trait, models are deleted from the database using mass-deletion queries. Therefore, the `pruning` method will not be invoked, nor will the `deleting` and `deleted` model Signals be dispatched. This is because the models are never actually retrieved before deletion, thus making the pruning process much more efficient:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\MassPrunable;
use Voyager\Database\Instrument\Model;
use Voyager\NutsAndBolts\DataObjects\Carbon;

class Flight extends Model
{
    use MassPrunable;

    /**
     * Get the prunable model query.
     */
    public function prunable(): Builder
    {
        return static::where('created_at', '<=', Carbon::now()->subMonth());
    }
}
```

## Replicating Models

You may create an unsaved copy of an existing model instance using the `replicate` method. This method is particularly useful when you have model instances that share many of the same attributes:

```php
use App\Models\Address;

$shipping = Address::create([
    'type' => 'shipping',
    'line_1' => '123 Example Street',
    'city' => 'Victorville',
    'state' => 'CA',
    'postcode' => '90001',
]);

$billing = $shipping->replicate()->fill([
    'type' => 'billing'
]);

$billing->save();
```

To exclude one or more attributes from being replicated to the new model, you may pass an array to the `replicate` method:

```php
$flight = Flight::create([
    'destination' => 'LAX',
    'origin' => 'LHR',
    'last_flown' => '2020-03-04 11:00:00',
    'last_pilot_id' => 747,
]);

$flight = $flight->replicate([
    'last_flown',
    'last_pilot_id'
]);
```

## Query Scopes

### Global Scopes

Global scopes allow you to add constraints to all queries for a given model. Instrument's own [soft delete](#soft-deleting) functionality utilizes global scopes to only retrieve "non-deleted" models from the database. Writing your own global scopes can provide a convenient, easy way to make sure every query for a given model receives certain constraints.

#### Writing Global Scopes

Writing a global scope is simple. Define a class that implements the `Voyager\Database\Instrument\Scope` interface; this example places it in the `app/Models/Scopes` directory. The `Scope` interface requires you to implement one method: `apply`. The `apply` method may add `where` constraints or other types of clauses to the query as needed:

```php
<?php

namespace App\Models\Scopes;

use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\Model;
use Voyager\Database\Instrument\Scope;
use Voyager\NutsAndBolts\DataObjects\Carbon;

class AncientScope implements Scope
{
    /**
     * Apply the scope to a given Instrument query builder.
     */
    public function apply(Builder $builder, Model $model): void
    {
        $builder->where('created_at', '<', Carbon::now()->subYears(2000));
    }
}
```

> [!NOTE]
> If your global scope is adding columns to the select clause of the query, you should use the `addSelect` method instead of `select`. This will prevent the unintentional replacement of the query's existing select clause.

#### Applying Global Scopes

To assign a global scope to a model, you may simply place the `ScopedBy` attribute on the model:

```php
<?php

namespace App\Models;

use App\Models\Scopes\AncientScope;
use Voyager\Database\Instrument\Attributes\ScopedBy;

#[ScopedBy([AncientScope::class])]
class User extends Model
{
    //
}
```

Or, you may manually register the global scope by overriding the model's `booted` method and invoke the model's `addGlobalScope` method. The `addGlobalScope` method accepts an instance of your scope as its only argument:

```php
<?php

namespace App\Models;

use App\Models\Scopes\AncientScope;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * The "booted" method of the model.
     */
    protected static function booted(): void
    {
        static::addGlobalScope(new AncientScope);
    }
}
```

After adding the scope in the example above to the `App\Models\User` model, a call to the `User::all()` method will execute the following SQL query:

```sql
select * from `users` where `created_at` < 0021-02-18 00:00:00
```

#### Anonymous Global Scopes

Instrument also allows you to define global scopes using closures, which is particularly useful for simple scopes that do not warrant a separate class of their own. When defining a global scope using a closure, you should provide a scope name of your own choosing as the first argument to the `addGlobalScope` method:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\Model;
use Voyager\NutsAndBolts\DataObjects\Carbon;

class User extends Model
{
    /**
     * The "booted" method of the model.
     */
    protected static function booted(): void
    {
        static::addGlobalScope('ancient', function (Builder $builder) {
            $builder->where('created_at', '<', Carbon::now()->subYears(2000));
        });
    }
}
```

#### Removing Global Scopes

If you would like to remove a global scope for a given query, you may use the `withoutGlobalScope` method. This method accepts the class name of the global scope as its only argument:

```php
User::withoutGlobalScope(AncientScope::class)->get();
```

Or, if you defined the global scope using a closure, you should pass the string name that you assigned to the global scope:

```php
User::withoutGlobalScope('ancient')->get();
```

If you would like to remove several or even all of the query's global scopes, you may use the `withoutGlobalScopes` and `withoutGlobalScopesExcept` methods:

```php
// Remove all of the global scopes...
User::withoutGlobalScopes()->get();

// Remove some of the global scopes...
User::withoutGlobalScopes([
    FirstScope::class, SecondScope::class
])->get();

// Remove all global scopes except the given ones...
User::withoutGlobalScopesExcept([
    SecondScope::class,
])->get();
```

### Local Scopes

Local scopes allow you to define common sets of query constraints that you may easily re-use throughout your application. For example, you may need to frequently retrieve all users that are considered "popular". To define a scope, add the `Scope` attribute to an Instrument method.

Scopes should always return the same query builder instance or `void`:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Attributes\Scope;
use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Scope a query to only include popular users.
     */
    #[Scope]
    protected function popular(Builder $query): void
    {
        $query->where('votes', '>', 100);
    }

    /**
     * Scope a query to only include active users.
     */
    #[Scope]
    protected function active(Builder $query): void
    {
        $query->where('active', 1);
    }
}
```

#### Utilizing a Local Scope

Once the scope has been defined, you may call the scope methods when querying the model. You can even chain calls to various scopes:

```php
use App\Models\User;

$users = User::popular()->active()->orderBy('created_at')->get();
```

Combining multiple Instrument model scopes via an `or` query operator may require the use of closures to achieve the correct [logical grouping](/docs/{{version}}/framework/database/queries#logical-grouping):

```php
$users = User::popular()->orWhere(function (Builder $query) {
    $query->active();
})->get();
```

However, since this can be cumbersome, Instrument provides a "higher order" `orWhere` method that allows you to fluently chain scopes together without the use of closures:

```php
$users = User::popular()->orWhere->active()->get();
```

#### Dynamic Scopes

Sometimes you may wish to define a scope that accepts parameters. To get started, just add your additional parameters to your scope method's signature. Scope parameters should be defined after the `$query` parameter:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Attributes\Scope;
use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Scope a query to only include users of a given type.
     */
    #[Scope]
    protected function ofType(Builder $query, string $type): void
    {
        $query->where('type', $type);
    }
}
```

Once the expected arguments have been added to your scope method's signature, you may pass the arguments when calling the scope:

```php
$users = User::ofType('admin')->get();
```

Attributed scope methods should be `protected`. When calling an attributed scope from within the model class, call the scope through a query builder instance, such as `static::query()->ofType('admin')`, to ensure the call is routed through Instrument's scope handling.

### Pending Attributes

If you would like to use scopes to create models that have the same attributes as those used to constrain the scope, you may use the `withAttributes` method when building the scope query:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Attributes\Scope;
use Voyager\Database\Instrument\Builder;
use Voyager\Database\Instrument\Model;

class Post extends Model
{
    /**
     * Scope the query to only include drafts.
     */
    #[Scope]
    protected function draft(Builder $query): void
    {
        $query->withAttributes([
            'hidden' => true,
        ]);
    }
}
```

The `withAttributes` method will add `where` conditions to the query using the given attributes, and it will also add the given attributes to any models created via the scope:

```php
$draft = Post::draft()->create(['title' => 'In Progress']);

$draft->hidden; // true
```

To instruct the `withAttributes` method to not add `where` conditions to the query, you may set the `asConditions` argument to `false`:

```php
$query->withAttributes([
    'hidden' => true,
], asConditions: false);
```

## Comparing Models

Sometimes you may need to determine if two models are the "same" or not. The `is` and `isNot` methods may be used to quickly verify two models have the same primary key, table, and database connection or not:

```php
if ($post->is($anotherPost)) {
    // ...
}

if ($post->isNot($anotherPost)) {
    // ...
}
```

The `is` and `isNot` methods are also available when using the `belongsTo`, `hasOne`, `morphTo`, and `morphOne` [relationships](/docs/{{version}}/framework/instrument-orm/instrument-relationships). This method is particularly helpful when you would like to compare a related model without issuing a query to retrieve that model:

```php
if ($post->author()->is($user)) {
    // ...
}
```

## Signals

> [!NOTE]
> Want to broadcast your model Signals to other applications? Check out [model broadcasting](/docs/{{version}}/framework/digging-deeper/broadcasting#model-broadcasting).

Instrument models dispatch several [Signals](/docs/{{version}}/framework/digging-deeper/signals), allowing you to hook into the following moments in a model's lifecycle: `retrieved`, `creating`, `created`, `updating`, `updated`, `saving`, `saved`, `deleting`, `deleted`, `trashed`, `forceDeleting`, `forceDeleted`, `restoring`, `restored`, and `replicating`.

The `retrieved` Signal will dispatch when an existing model is retrieved from the database. When a new model is saved for the first time, the `creating` and `created` Signals will dispatch. The `updating` / `updated` Signals will dispatch when an existing model is modified and the `save` method is called. The `saving` / `saved` Signals will dispatch when a model is created or updated - even if the model's attributes have not been changed. Signal names ending with `-ing` are dispatched before any changes to the model are persisted, while Signals ending with `-ed` are dispatched after the changes to the model are persisted.

To start listening to model Signals, define a `$dispatchesEvents` property on your Instrument model. This property maps various points of the Instrument model's lifecycle to your own [Signal classes](/docs/{{version}}/framework/digging-deeper/signals). Each model Signal class should expect to receive an instance of the affected model via its constructor:

```php
<?php

namespace App\Models;

use App\Events\UserDeleted;
use App\Events\UserSaved;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * The event map for the model.
     *
     * @var array<string, string>
     */
    protected $dispatchesEvents = [
        'saved' => UserSaved::class,
        'deleted' => UserDeleted::class,
    ];
}
```

After defining and mapping your Instrument Signals, you may use [listeners](/docs/{{version}}/framework/digging-deeper/signals) to handle them.

> [!WARNING]
> When issuing a mass update or delete query via Instrument, the `saved`, `updated`, `deleting`, and `deleted` model Signals will not be dispatched for the affected models. This is because the models are never actually retrieved when performing mass updates or deletes.

### Using Closures

Instead of using custom Signal classes, you may register closures that execute when various model Signals are dispatched. Typically, you should register these closures in the `booted` method of your model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * The "booted" method of the model.
     */
    protected static function booted(): void
    {
        static::created(function (User $user) {
            // ...
        });
    }
}
```

If needed, you may wrap the closure in a `Voyager\Signals\QueuedClosure` when registering a model Signal listener. This will execute the listener in the background using your application's [queue](/docs/{{version}}/framework/digging-deeper/queues):

```php
use Voyager\Signals\QueuedClosure;

static::created(new QueuedClosure(function (User $user) {
    // ...
}));
```

The `QueuedClosure` may be sent to a specific connection and queue using its `onConnection` and `onQueue` methods.

### Observers

#### Defining Observers

If you are listening for many Signals on a given model, you may use observers to group all of your listeners into a single class. Observer classes have method names which reflect the Instrument Signals you wish to listen for. Each of these methods receives the affected model as their only argument. Observers are written by hand and conventionally live in `app/Observers`. An observer looks like the following:

```php
<?php

namespace App\Observers;

use App\Models\User;

class UserObserver
{
    /**
     * Handle the User "created" event.
     */
    public function created(User $user): void
    {
        // ...
    }

    /**
     * Handle the User "updated" event.
     */
    public function updated(User $user): void
    {
        // ...
    }

    /**
     * Handle the User "deleted" event.
     */
    public function deleted(User $user): void
    {
        // ...
    }

    /**
     * Handle the User "restored" event.
     */
    public function restored(User $user): void
    {
        // ...
    }

    /**
     * Handle the User "forceDeleted" event.
     */
    public function forceDeleted(User $user): void
    {
        // ...
    }
}
```

To register an observer, you may place the `ObservedBy` attribute on the corresponding model:

```php
use App\Observers\UserObserver;
use Voyager\Database\Instrument\Attributes\ObservedBy;

#[ObservedBy([UserObserver::class])]
class User extends Model
{
    //
}
```

Or, you may manually register an observer by invoking the `observe` method on the model you wish to observe. You may register observers in the `boot` method of your application's `AppServiceProvider` class:

```php
use App\Models\User;
use App\Observers\UserObserver;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    User::observe(UserObserver::class);
}
```

> [!NOTE]
> There are additional Signals an observer can listen to, such as `saving` and `retrieved`. These Signals are described within the [Signals](#signals) documentation.

#### Observers and Database Transactions

When models are being created within a database transaction, you may want to instruct an observer to only execute its handlers after the database transaction is committed. You may accomplish this by implementing the `ShouldHandleSignalsAfterCommit` interface on your observer. If a database transaction is not in progress, the handlers will execute immediately:

```php
<?php

namespace App\Observers;

use App\Models\User;
use Voyager\Contracts\Signals\ShouldHandleSignalsAfterCommit;

class UserObserver implements ShouldHandleSignalsAfterCommit
{
    /**
     * Handle the User "created" event.
     */
    public function created(User $user): void
    {
        // ...
    }
}
```

### Muting Signals

You may occasionally need to temporarily "mute" all Signals fired by a model. You may achieve this using the `withoutEvents` method. The `withoutEvents` method accepts a closure as its only argument. Any code executed within this closure will not dispatch model Signals, and any value returned by the closure will be returned by the `withoutEvents` method:

```php
use App\Models\User;

$user = User::withoutEvents(function () {
    User::findOrFail(1)->delete();

    return User::find(2);
});
```

#### Saving a Single Model Without Signals

Sometimes you may wish to "save" a given model without dispatching any Signals. You may accomplish this using the `saveQuietly` method:

```php
$user = User::findOrFail(1);

$user->name = 'Victoria Faith';

$user->saveQuietly();
```

You may also "update", "delete", "soft delete", "restore", and "replicate" a given model without dispatching any Signals:

```php
$user->updateQuietly(['name' => 'Victoria Faith']);
$user->deleteQuietly();
$user->forceDeleteQuietly();
$user->restoreQuietly();
$user->replicateQuietly();
```
