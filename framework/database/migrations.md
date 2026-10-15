# Database: Migrations

Migrations are like version control for your database, allowing your team to define and share the application's database schema definition.

## Introduction

Migrations are like version control for your database, allowing your team to define and share the application's database schema definition. If you have ever had to tell a teammate to manually add a column to their local database schema after pulling in your changes from source control, you've faced the problem that database migrations solve.

The Venusian schema builder, a `Voyager\Database\Schema\Builder` bound in the container as `db.schema`, provides database agnostic support for creating and manipulating tables across all of Venusian's supported database systems. Typically, migrations will use `app('db.schema')` to create and modify database tables and columns.

<a id="generating-migrations"></a>
## Generating Migrations

You may use the `make:migration` [Computer command](/docs/{{version}}/framework/digging-deeper/computer) to generate a database migration. The new migration will be placed in your `database/migrations` directory. Each migration filename contains a timestamp that allows Venusian to determine the order of the migrations:

```shell
php computer make:migration create_flights_table
```

Venusian will use the name of the migration to attempt to guess the name of the table and whether or not the migration will be creating a new table. If Venusian is able to determine the table name from the migration name, Venusian will pre-fill the generated migration file with the specified table. Otherwise, you may simply specify the table in the migration file manually.

If you would like to specify a custom path for the generated migration, you may use the `--path` option when executing the `make:migration` command. The given path should be relative to your application's base path. The `--create` and `--table` options name the table yourself, for a migration that creates it or one that updates it.

> [!NOTE]
> Migration stubs may be customized using [stub publishing](/docs/{{version}}/framework/digging-deeper/computer#stub-customization).

## Migration Structure

A migration class contains two methods: `up` and `down`. The `up` method is used to add new tables, columns, or indexes to your database, while the `down` method should reverse the operations performed by the `up` method.

Within both of these methods, you may use the Venusian schema builder to expressively create and modify tables. To learn about all of the methods available on the schema builder, [check out its documentation](#creating-tables). For example, the following migration creates a `flights` table:

```php
<?php

use Voyager\Database\Migrations\Migration;
use Voyager\Database\Schema\Blueprint;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        app('db.schema')->create('flights', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('airline');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        app('db.schema')->drop('flights');
    }
};
```

#### Setting the Migration Connection

If your migration will be interacting with a database connection other than your application's default database connection, you should set the `$connection` property of your migration:

```php
/**
 * The database connection that should be used by the migration.
 *
 * @var string
 */
protected $connection = 'pgsql';

/**
 * Run the migrations.
 */
public function up(): void
{
    // ...
}
```

#### Skipping Migrations

Sometimes a migration might be meant to support a feature that is not yet active and you do not want it to run yet. In this case you may define a `shouldRun` method on the migration. If the `shouldRun` method returns `false`, the migration will be skipped:

```php
/**
 * Determine if this migration should run.
 */
public function shouldRun(): bool
{
    return config('flights.enabled', false);
}
```

A skipped migration dispatches a `Voyager\Database\Events\MigrationSkipped` signal.

## Running Migrations

To run all of your outstanding migrations, execute the `migrate` Computer command:

```shell
php computer migrate
```

If you would like to see which migrations have already run and which are still pending, you may use the `migrate:status` Computer command:

```shell
php computer migrate:status
```

The `migrate` command creates the `migrations` table, named by the `migrations.table` option in your `config/database.php` file, the first time it runs. To create that table on its own, use the `migrate:install` command:

```shell
php computer migrate:install
```

If you provide the `--step` option to the `migrate` command, the command will run each migration as its own batch, allowing you to roll back individual migrations later using the `migrate:rollback` command:

```shell
php computer migrate --step
```

If you would like to see the SQL statements that will be executed by the migrations without actually running them, you may provide the `--pretend` flag to the `migrate` command:

```shell
php computer migrate --pretend
```

#### Isolating Migration Execution

If you are deploying your application across multiple servers and running migrations as part of your deployment process, you likely do not want two servers attempting to migrate the database at the same time. To avoid this, you may use the `isolated` option when invoking the `migrate` command.

When the `isolated` option is provided, Venusian will acquire an atomic lock using your application's cache driver before attempting to run your migrations. All other attempts to run the `migrate` command while that lock is held will not execute; however, the command will still exit with a successful exit status code:

```shell
php computer migrate --isolated
```

> [!WARNING]
> To utilize this feature, your application must be using the `redis`, `database`, `file`, or `array` cache driver as your application's default cache driver. In addition, all servers must be communicating with the same central cache server.

#### Forcing Migrations to Run in Production

Some migration operations are destructive, which means they may cause you to lose data. In order to protect you from running these commands against your production database, you will be prompted for confirmation before the commands are executed. To force the commands to run without a prompt, use the `--force` flag:

```shell
php computer migrate --force
```

### Rolling Back Migrations

To roll back the latest migration operation, you may use the `rollback` Computer command. This command rolls back the last "batch" of migrations, which may include multiple migration files:

```shell
php computer migrate:rollback
```

You may roll back a limited number of migrations by providing the `step` option to the `rollback` command. For example, the following command will roll back the last five migrations:

```shell
php computer migrate:rollback --step=5
```

You may roll back a specific "batch" of migrations by providing the `batch` option to the `rollback` command, where the `batch` option corresponds to a batch value within your application's `migrations` database table. For example, the following command will roll back all migrations in batch three:

```shell
php computer migrate:rollback --batch=3
```

If you would like to see the SQL statements that will be executed by the migrations without actually running them, you may provide the `--pretend` flag to the `migrate:rollback` command:

```shell
php computer migrate:rollback --pretend
```

The `migrate:reset` command will roll back all of your application's migrations:

```shell
php computer migrate:reset
```

#### Roll Back and Migrate Using a Single Command

The `migrate:refresh` command will roll back all of your migrations and then execute the `migrate` command. This command effectively re-creates your entire database:

```shell
php computer migrate:refresh
```

You may roll back and re-migrate a limited number of migrations by providing the `step` option to the `refresh` command. For example, the following command will roll back and re-migrate the last five migrations:

```shell
php computer migrate:refresh --step=5
```

#### Drop All Tables and Migrate

The `migrate:fresh` command will drop all tables from the database and then execute the `migrate` command:

```shell
php computer migrate:fresh
```

By default, the `migrate:fresh` command only drops tables from the default database connection. However, you may use the `--database` option to specify the database connection that should be migrated. The database connection name should correspond to a connection defined in your application's `config/database.php` configuration file:

```shell
php computer migrate:fresh --database=admin
```

> [!WARNING]
> The `migrate:fresh` command will drop all database tables regardless of their prefix. This command should be used with caution when developing on a database that is shared with other applications.

## Tables

<a id="creating-tables"></a>
### Creating Tables

To create a new database table, use the schema builder's `create` method. The `create` method accepts two arguments: the first is the name of the table, while the second is a closure which receives a `Blueprint` object that may be used to define the new table:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->create('users', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email');
    $table->timestamps();
});
```

When creating the table, you may use any of the schema builder's [column methods](#creating-columns) to define the table's columns.

#### Determining Table / Column Existence

You may determine the existence of a table, column, or index using the `hasTable`, `hasColumn`, and `hasIndex` methods:

```php
if (app('db.schema')->hasTable('users')) {
    // The "users" table exists...
}

if (app('db.schema')->hasColumn('users', 'email')) {
    // The "users" table exists and has an "email" column...
}

if (app('db.schema')->hasIndex('users', ['email'], 'unique')) {
    // The "users" table exists and has a unique index on the "email" column...
}
```

#### Database Connection and Table Options

If you want to perform a schema operation on a database connection that is not your application's default connection, use the `connection` method:

```php
app('db')->connection('sqlite')->getSchemaBuilder()->create('users', function (Blueprint $table) {
    $table->id();
});
```

In addition, a few other properties and methods may be used to define other aspects of the table's creation. The `engine` property may be used to specify the table's storage engine when using MariaDB or MySQL:

```php
app('db.schema')->create('users', function (Blueprint $table) {
    $table->engine('InnoDB');

    // ...
});
```

The `charset` and `collation` properties may be used to specify the character set and collation for the created table when using MariaDB or MySQL:

```php
app('db.schema')->create('users', function (Blueprint $table) {
    $table->charset('utf8mb4');
    $table->collation('utf8mb4_unicode_ci');

    // ...
});
```

The `temporary` method may be used to indicate that the table should be "temporary". Temporary tables are only visible to the current connection's database session and are dropped automatically when the connection is closed:

```php
app('db.schema')->create('calculations', function (Blueprint $table) {
    $table->temporary();

    // ...
});
```

If you would like to add a "comment" to a database table, you may invoke the `comment` method on the table instance. Table comments are currently only supported by MariaDB, MySQL, and PostgreSQL:

```php
app('db.schema')->create('calculations', function (Blueprint $table) {
    $table->comment('Business calculations');

    // ...
});
```

### Updating Tables

The schema builder's `table` method may be used to update existing tables. Like the `create` method, the `table` method accepts two arguments: the name of the table and a closure that receives a `Blueprint` instance you may use to add columns or indexes to the table:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->table('users', function (Blueprint $table) {
    $table->integer('votes');
});
```

### Renaming / Dropping Tables

To rename an existing database table, use the `rename` method:

```php
app('db.schema')->rename($from, $to);
```

To drop an existing table, you may use the `drop` or `dropIfExists` methods:

```php
app('db.schema')->drop('users');

app('db.schema')->dropIfExists('users');
```

#### Renaming Tables With Foreign Keys

Before renaming a table, you should verify that any foreign key constraints on the table have an explicit name in your migration files instead of letting Venusian assign a convention based name. Otherwise, the foreign key constraint name will refer to the old table name.

## Columns

<a id="creating-columns"></a>
### Creating Columns

The schema builder's `table` method may be used to update existing tables. Like the `create` method, the `table` method accepts two arguments: the name of the table and a closure that receives an `Voyager\Database\Schema\Blueprint` instance you may use to add columns to the table:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->table('users', function (Blueprint $table) {
    $table->integer('votes');
});
```

<a id="available-column-types"></a>
### Available Column Types

The schema builder blueprint offers a variety of methods that correspond to the different types of columns you can add to your database tables. Each of the available methods are listed in the table below:

#### Boolean Types

[boolean](#column-method-boolean)

#### String & Text Types

[char](#column-method-char)
[longText](#column-method-longText)
[mediumText](#column-method-mediumText)
[string](#column-method-string)
[text](#column-method-text)
[tinyText](#column-method-tinyText)

#### Numeric Types

[bigIncrements](#column-method-bigIncrements)
[bigInteger](#column-method-bigInteger)
[decimal](#column-method-decimal)
[double](#column-method-double)
[float](#column-method-float)
[id](#column-method-id)
[increments](#column-method-increments)
[integer](#column-method-integer)
[mediumIncrements](#column-method-mediumIncrements)
[mediumInteger](#column-method-mediumInteger)
[smallIncrements](#column-method-smallIncrements)
[smallInteger](#column-method-smallInteger)
[tinyIncrements](#column-method-tinyIncrements)
[tinyInteger](#column-method-tinyInteger)
[unsignedBigInteger](#column-method-unsignedBigInteger)
[unsignedInteger](#column-method-unsignedInteger)
[unsignedMediumInteger](#column-method-unsignedMediumInteger)
[unsignedSmallInteger](#column-method-unsignedSmallInteger)
[unsignedTinyInteger](#column-method-unsignedTinyInteger)

#### Date & Time Types

[dateTime](#column-method-dateTime)
[dateTimeTz](#column-method-dateTimeTz)
[date](#column-method-date)
[time](#column-method-time)
[timeTz](#column-method-timeTz)
[timestamp](#column-method-timestamp)
[timestamps](#column-method-timestamps)
[timestampsTz](#column-method-timestampsTz)
[softDeletes](#column-method-softDeletes)
[softDeletesTz](#column-method-softDeletesTz)
[year](#column-method-year)

#### Binary Types

[binary](#column-method-binary)

#### Object & Json Types

[json](#column-method-json)
[jsonb](#column-method-jsonb)

#### UUID & ULID Types

[ulid](#column-method-ulid)
[ulidMorphs](#column-method-ulidMorphs)
[uuid](#column-method-uuid)
[uuidMorphs](#column-method-uuidMorphs)
[nullableUlidMorphs](#column-method-nullableUlidMorphs)
[nullableUuidMorphs](#column-method-nullableUuidMorphs)

#### Spatial Types

[geography](#column-method-geography)
[geometry](#column-method-geometry)

#### Relationship Types

[foreignId](#column-method-foreignId)
[foreignIdFor](#column-method-foreignIdFor)
[foreignUlid](#column-method-foreignUlid)
[foreignUuid](#column-method-foreignUuid)
[morphs](#column-method-morphs)
[nullableMorphs](#column-method-nullableMorphs)

#### Specialty Types

[enum](#column-method-enum)
[set](#column-method-set)
[macAddress](#column-method-macAddress)
[ipAddress](#column-method-ipAddress)
[rememberToken](#column-method-rememberToken)
[vector](#column-method-vector)

<a id="column-method-bigIncrements"></a>
#### `bigIncrements()`

The `bigIncrements` method creates an auto-incrementing `UNSIGNED BIGINT` (primary key) equivalent column:

```php
$table->bigIncrements('id');
```

<a id="column-method-bigInteger"></a>
#### `bigInteger()`

The `bigInteger` method creates a `BIGINT` equivalent column:

```php
$table->bigInteger('votes');
```

<a id="column-method-binary"></a>
#### `binary()`

The `binary` method creates a `BLOB` equivalent column:

```php
$table->binary('photo');
```

When utilizing MySQL, MariaDB, or SQL Server, you may pass `length` and `fixed` arguments to create `VARBINARY` or `BINARY` equivalent column:

```php
$table->binary('data', length: 16); // VARBINARY(16)

$table->binary('data', length: 16, fixed: true); // BINARY(16)
```

<a id="column-method-boolean"></a>
#### `boolean()`

The `boolean` method creates a `BOOLEAN` equivalent column:

```php
$table->boolean('confirmed');
```

<a id="column-method-char"></a>
#### `char()`

The `char` method creates a `CHAR` equivalent column with of a given length:

```php
$table->char('name', length: 100);
```

<a id="column-method-dateTimeTz"></a>
#### `dateTimeTz()`

The `dateTimeTz` method creates a `DATETIME` (with timezone) equivalent column with an optional fractional seconds precision:

```php
$table->dateTimeTz('created_at', precision: 0);
```

<a id="column-method-dateTime"></a>
#### `dateTime()`

The `dateTime` method creates a `DATETIME` equivalent column with an optional fractional seconds precision:

```php
$table->dateTime('created_at', precision: 0);
```

<a id="column-method-date"></a>
#### `date()`

The `date` method creates a `DATE` equivalent column:

```php
$table->date('created_at');
```

<a id="column-method-decimal"></a>
#### `decimal()`

The `decimal` method creates a `DECIMAL` equivalent column with the given precision (total digits) and scale (decimal digits):

```php
$table->decimal('amount', total: 8, places: 2);
```

<a id="column-method-double"></a>
#### `double()`

The `double` method creates a `DOUBLE` equivalent column:

```php
$table->double('amount');
```

<a id="column-method-enum"></a>
#### `enum()`

The `enum` method creates a `ENUM` equivalent column with the given valid values:

```php
$table->enum('difficulty', ['easy', 'hard']);
```

Of course, you may use the `Enum::cases()` method instead of manually defining an array of allowed values:

```php
use App\Enums\Difficulty;

$table->enum('difficulty', Difficulty::cases());
```

<a id="column-method-float"></a>
#### `float()`

The `float` method creates a `FLOAT` equivalent column with the given precision:

```php
$table->float('amount', precision: 53);
```

<a id="column-method-foreignId"></a>
#### `foreignId()`

The `foreignId` method creates an `UNSIGNED BIGINT` equivalent column:

```php
$table->foreignId('user_id');
```

<a id="column-method-foreignIdFor"></a>
#### `foreignIdFor()`

The `foreignIdFor` method adds a `{column}_id` equivalent column for a given model class. The column type will be `UNSIGNED BIGINT`, `CHAR(36)`, or `CHAR(26)` depending on the model key type:

```php
$table->foreignIdFor(User::class);
```

<a id="column-method-foreignUlid"></a>
#### `foreignUlid()`

The `foreignUlid` method creates a `ULID` equivalent column:

```php
$table->foreignUlid('user_id');
```

<a id="column-method-foreignUuid"></a>
#### `foreignUuid()`

The `foreignUuid` method creates a `UUID` equivalent column:

```php
$table->foreignUuid('user_id');
```

<a id="column-method-geography"></a>
#### `geography()`

The `geography` method creates a `GEOGRAPHY` equivalent column with the given spatial type and SRID (Spatial Reference System Identifier):

```php
$table->geography('coordinates', subtype: 'point', srid: 4326);
```

> [!NOTE]
> Support for spatial types depends on your database driver. Please refer to your database's documentation. If your application is utilizing a PostgreSQL database, you must install the [PostGIS](https://postgis.net) extension before the `geography` method may be used.

<a id="column-method-geometry"></a>
#### `geometry()`

The `geometry` method creates a `GEOMETRY` equivalent column with the given spatial type and SRID (Spatial Reference System Identifier):

```php
$table->geometry('positions', subtype: 'point', srid: 0);
```

> [!NOTE]
> Support for spatial types depends on your database driver. Please refer to your database's documentation. If your application is utilizing a PostgreSQL database, you must install the [PostGIS](https://postgis.net) extension before the `geometry` method may be used.

<a id="column-method-id"></a>
#### `id()`

The `id` method is an alias of the `bigIncrements` method. By default, the method will create an `id` column; however, you may pass a column name if you would like to assign a different name to the column:

```php
$table->id();
```

<a id="column-method-increments"></a>
#### `increments()`

The `increments` method creates an auto-incrementing `UNSIGNED INTEGER` equivalent column as a primary key:

```php
$table->increments('id');
```

<a id="column-method-integer"></a>
#### `integer()`

The `integer` method creates an `INTEGER` equivalent column:

```php
$table->integer('votes');
```

<a id="column-method-ipAddress"></a>
#### `ipAddress()`

The `ipAddress` method creates a `VARCHAR` equivalent column:

```php
$table->ipAddress('visitor');
```

When using PostgreSQL, an `INET` column will be created.

<a id="column-method-json"></a>
#### `json()`

The `json` method creates a `JSON` equivalent column:

```php
$table->json('options');
```

When using SQLite, a `TEXT` column will be created.

<a id="column-method-jsonb"></a>
#### `jsonb()`

The `jsonb` method creates a `JSONB` equivalent column:

```php
$table->jsonb('options');
```

When using SQLite, a `TEXT` column will be created.

<a id="column-method-longText"></a>
#### `longText()`

The `longText` method creates a `LONGTEXT` equivalent column:

```php
$table->longText('description');
```

When utilizing MySQL or MariaDB, you may apply a `binary` character set to the column in order to create a `LONGBLOB` equivalent column:

```php
$table->longText('data')->charset('binary'); // LONGBLOB
```

<a id="column-method-macAddress"></a>
#### `macAddress()`

The `macAddress` method creates a column that is intended to hold a MAC address. Some database systems, such as PostgreSQL, have a dedicated column type for this type of data. Other database systems will use a string equivalent column:

```php
$table->macAddress('device');
```

<a id="column-method-mediumIncrements"></a>
#### `mediumIncrements()`

The `mediumIncrements` method creates an auto-incrementing `UNSIGNED MEDIUMINT` equivalent column as a primary key:

```php
$table->mediumIncrements('id');
```

<a id="column-method-mediumInteger"></a>
#### `mediumInteger()`

The `mediumInteger` method creates a `MEDIUMINT` equivalent column:

```php
$table->mediumInteger('votes');
```

<a id="column-method-mediumText"></a>
#### `mediumText()`

The `mediumText` method creates a `MEDIUMTEXT` equivalent column:

```php
$table->mediumText('description');
```

When utilizing MySQL or MariaDB, you may apply a `binary` character set to the column in order to create a `MEDIUMBLOB` equivalent column:

```php
$table->mediumText('data')->charset('binary'); // MEDIUMBLOB
```

<a id="column-method-morphs"></a>
#### `morphs()`

The `morphs` method is a convenience method that adds a `{column}_type` `VARCHAR` equivalent column and a `{column}_id` equivalent column. The column type for the `{column}_id` will be `UNSIGNED BIGINT`, `CHAR(36)`, or `CHAR(26)` depending on the model key type.

This method is intended to be used when defining the columns necessary for a polymorphic [Instrument relationship](/docs/{{version}}/framework/instrument-orm/instrument-relationships#polymorphic-relationships). In the following example, `taggable_type` and `taggable_id` columns would be created:

```php
$table->morphs('taggable');
```

<a id="column-method-nullableMorphs"></a>
#### `nullableMorphs()`

The method is similar to the [morphs](#column-method-morphs) method; however, the columns that are created will be "nullable":

```php
$table->nullableMorphs('taggable');
```

<a id="column-method-nullableUlidMorphs"></a>
#### `nullableUlidMorphs()`

The method is similar to the [ulidMorphs](#column-method-ulidMorphs) method; however, the columns that are created will be "nullable":

```php
$table->nullableUlidMorphs('taggable');
```

<a id="column-method-nullableUuidMorphs"></a>
#### `nullableUuidMorphs()`

The method is similar to the [uuidMorphs](#column-method-uuidMorphs) method; however, the columns that are created will be "nullable":

```php
$table->nullableUuidMorphs('taggable');
```

<a id="column-method-rememberToken"></a>
#### `rememberToken()`

The `rememberToken` method creates a nullable, `VARCHAR(100)` equivalent column that is intended to store a "remember me" token:

```php
$table->rememberToken();
```

<a id="column-method-set"></a>
#### `set()`

The `set` method creates a `SET` equivalent column with the given list of valid values:

```php
$table->set('flavors', ['strawberry', 'vanilla']);
```

<a id="column-method-smallIncrements"></a>
#### `smallIncrements()`

The `smallIncrements` method creates an auto-incrementing `UNSIGNED SMALLINT` equivalent column as a primary key:

```php
$table->smallIncrements('id');
```

<a id="column-method-smallInteger"></a>
#### `smallInteger()`

The `smallInteger` method creates a `SMALLINT` equivalent column:

```php
$table->smallInteger('votes');
```

<a id="column-method-softDeletesTz"></a>
#### `softDeletesTz()`

The `softDeletesTz` method adds a nullable `deleted_at` `TIMESTAMP` (with timezone) equivalent column with an optional fractional seconds precision. This column is intended to store the `deleted_at` timestamp needed for Instrument's ["soft delete"](/docs/{{version}}/framework/instrument-orm/instrument#soft-deleting) functionality:

```php
$table->softDeletesTz('deleted_at', precision: 0);
```

<a id="column-method-softDeletes"></a>
#### `softDeletes()`

The `softDeletes` method adds a nullable `deleted_at` `TIMESTAMP` equivalent column with an optional fractional seconds precision. This column is intended to store the `deleted_at` timestamp needed for Instrument's ["soft delete"](/docs/{{version}}/framework/instrument-orm/instrument#soft-deleting) functionality:

```php
$table->softDeletes('deleted_at', precision: 0);
```

<a id="column-method-string"></a>
#### `string()`

The `string` method creates a `VARCHAR` equivalent column of the given length:

```php
$table->string('name', length: 100);
```

<a id="column-method-text"></a>
#### `text()`

The `text` method creates a `TEXT` equivalent column:

```php
$table->text('description');
```

When utilizing MySQL or MariaDB, you may apply a `binary` character set to the column in order to create a `BLOB` equivalent column:

```php
$table->text('data')->charset('binary'); // BLOB
```

<a id="column-method-timeTz"></a>
#### `timeTz()`

The `timeTz` method creates a `TIME` (with timezone) equivalent column with an optional fractional seconds precision:

```php
$table->timeTz('sunrise', precision: 0);
```

<a id="column-method-time"></a>
#### `time()`

The `time` method creates a `TIME` equivalent column with an optional fractional seconds precision:

```php
$table->time('sunrise', precision: 0);
```

#### `timestampTz()`

The `timestampTz` method creates a `TIMESTAMP` (with timezone) equivalent column with an optional fractional seconds precision:

```php
$table->timestampTz('added_at', precision: 0);
```

<a id="column-method-timestamp"></a>
#### `timestamp()`

The `timestamp` method creates a `TIMESTAMP` equivalent column with an optional fractional seconds precision:

```php
$table->timestamp('added_at', precision: 0);
```

<a id="column-method-timestampsTz"></a>
#### `timestampsTz()`

The `timestampsTz` method creates `created_at` and `updated_at` `TIMESTAMP` (with timezone) equivalent columns with an optional fractional seconds precision:

```php
$table->timestampsTz(precision: 0);
```

<a id="column-method-timestamps"></a>
#### `timestamps()`

The `timestamps` method creates `created_at` and `updated_at` `TIMESTAMP` equivalent columns with an optional fractional seconds precision:

```php
$table->timestamps(precision: 0);
```

<a id="column-method-tinyIncrements"></a>
#### `tinyIncrements()`

The `tinyIncrements` method creates an auto-incrementing `UNSIGNED TINYINT` equivalent column as a primary key:

```php
$table->tinyIncrements('id');
```

<a id="column-method-tinyInteger"></a>
#### `tinyInteger()`

The `tinyInteger` method creates a `TINYINT` equivalent column:

```php
$table->tinyInteger('votes');
```

<a id="column-method-tinyText"></a>
#### `tinyText()`

The `tinyText` method creates a `TINYTEXT` equivalent column:

```php
$table->tinyText('notes');
```

When utilizing MySQL or MariaDB, you may apply a `binary` character set to the column in order to create a `TINYBLOB` equivalent column:

```php
$table->tinyText('data')->charset('binary'); // TINYBLOB
```

<a id="column-method-unsignedBigInteger"></a>
#### `unsignedBigInteger()`

The `unsignedBigInteger` method creates an `UNSIGNED BIGINT` equivalent column:

```php
$table->unsignedBigInteger('votes');
```

<a id="column-method-unsignedInteger"></a>
#### `unsignedInteger()`

The `unsignedInteger` method creates an `UNSIGNED INTEGER` equivalent column:

```php
$table->unsignedInteger('votes');
```

<a id="column-method-unsignedMediumInteger"></a>
#### `unsignedMediumInteger()`

The `unsignedMediumInteger` method creates an `UNSIGNED MEDIUMINT` equivalent column:

```php
$table->unsignedMediumInteger('votes');
```

<a id="column-method-unsignedSmallInteger"></a>
#### `unsignedSmallInteger()`

The `unsignedSmallInteger` method creates an `UNSIGNED SMALLINT` equivalent column:

```php
$table->unsignedSmallInteger('votes');
```

<a id="column-method-unsignedTinyInteger"></a>
#### `unsignedTinyInteger()`

The `unsignedTinyInteger` method creates an `UNSIGNED TINYINT` equivalent column:

```php
$table->unsignedTinyInteger('votes');
```

<a id="column-method-ulidMorphs"></a>
#### `ulidMorphs()`

The `ulidMorphs` method is a convenience method that adds a `{column}_type` `VARCHAR` equivalent column and a `{column}_id` `CHAR(26)` equivalent column.

This method is intended to be used when defining the columns necessary for a polymorphic [Instrument relationship](/docs/{{version}}/framework/instrument-orm/instrument-relationships#polymorphic-relationships) that use ULID identifiers. In the following example, `taggable_type` and `taggable_id` columns would be created:

```php
$table->ulidMorphs('taggable');
```

<a id="column-method-uuidMorphs"></a>
#### `uuidMorphs()`

The `uuidMorphs` method is a convenience method that adds a `{column}_type` `VARCHAR` equivalent column and a `{column}_id` `CHAR(36)` equivalent column.

This method is intended to be used when defining the columns necessary for a [polymorphic Instrument relationship](/docs/{{version}}/framework/instrument-orm/instrument-relationships#polymorphic-relationships) that use UUID identifiers. In the following example, `taggable_type` and `taggable_id` columns would be created:

```php
$table->uuidMorphs('taggable');
```

<a id="column-method-ulid"></a>
#### `ulid()`

The `ulid` method creates a `ULID` equivalent column:

```php
$table->ulid('id');
```

<a id="column-method-uuid"></a>
#### `uuid()`

The `uuid` method creates a `UUID` equivalent column:

```php
$table->uuid('id');
```

<a id="column-method-vector"></a>
#### `vector()`

The `vector` method creates a `vector` equivalent column:

```php
$table->vector('embedding', dimensions: 1536);
```

Vector columns are supported on PostgreSQL connections using the `pgvector` extension and MariaDB 11.7 or later. When utilizing PostgreSQL, `pgvector` must be loaded before `vector` columns can be created:

```php
app('db.schema')->ensureVectorExtensionExists();
```

To speed up [vector similarity queries](/docs/{{version}}/framework/database/queries#vector-similarity-clauses), you may add a vector index to the column. Calling the `index` method on a `vector` column creates a vector index using cosine distance:

```php
$table->vector('embedding', dimensions: 1536)->index();
```

<a id="column-method-year"></a>
#### `year()`

The `year` method creates a `YEAR` equivalent column:

```php
$table->year('birth_year');
```

<a id="column-modifiers"></a>
### Column Modifiers

In addition to the column types listed above, there are several column "modifiers" you may use when adding a column to a database table. For example, to make the column "nullable", you may use the `nullable` method:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->table('users', function (Blueprint $table) {
    $table->string('email')->nullable();
});
```

The following table contains all of the available column modifiers. This list does not include [index modifiers](#creating-indexes):

| Modifier                            | Description                                                                                    |
| ----------------------------------- | ---------------------------------------------------------------------------------------------- |
| `->after('column')`                 | Place the column "after" another column (MariaDB / MySQL).                                     |
| `->autoIncrement()`                 | Set `INTEGER` columns as auto-incrementing (primary key).                                      |
| `->charset('utf8mb4')`              | Specify a character set for the column (MariaDB / MySQL).                                      |
| `->collation('utf8mb4_unicode_ci')` | Specify a collation for the column.                                                            |
| `->comment('my comment')`           | Add a comment to a column (MariaDB / MySQL / PostgreSQL).                                      |
| `->default($value)`                 | Specify a "default" value for the column.                                                      |
| `->first()`                         | Place the column "first" in the table (MariaDB / MySQL).                                       |
| `->from($integer)`                  | Set the starting value of an auto-incrementing field (MariaDB / MySQL / PostgreSQL).           |
| `->instant()`                       | Add or modify the column using an instant operation (MySQL).                                   |
| `->invisible()`                     | Make the column "invisible" to `SELECT *` queries (MariaDB / MySQL).                           |
| `->lock($mode)`                     | Specify a lock mode for the column operation (MySQL).                                          |
| `->nullable($value = true)`         | Allow `NULL` values to be inserted into the column.                                            |
| `->storedAs($expression)`           | Create a stored generated column (MariaDB / MySQL / PostgreSQL / SQLite).                      |
| `->unsigned()`                      | Set `INTEGER` columns as `UNSIGNED` (MariaDB / MySQL).                                         |
| `->using($expression)`              | Specify a casting expression when changing the column type (PostgreSQL).                       |
| `->useCurrent()`                    | Set `TIMESTAMP` columns to use `CURRENT_TIMESTAMP` as default value.                           |
| `->useCurrentOnUpdate()`            | Set `TIMESTAMP` columns to use `CURRENT_TIMESTAMP` when a record is updated (MariaDB / MySQL). |
| `->virtualAs($expression)`          | Create a virtual generated column (MariaDB / MySQL / SQLite).                                  |
| `->generatedAs($expression)`        | Create an identity column with specified sequence options (PostgreSQL).                        |
| `->always()`                        | Defines the precedence of sequence values over input for an identity column (PostgreSQL).      |

#### Default Expressions

The `default` modifier accepts a value or an `Voyager\Database\Query\Expression` instance. Using an `Expression` instance will prevent Venusian from wrapping the value in quotes and allow you to use database specific functions. One situation where this is particularly useful is when you need to assign default values to JSON columns:

```php
<?php

use Voyager\Database\Schema\Blueprint;
use Voyager\Database\Query\Expression;
use Voyager\Database\Migrations\Migration;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        app('db.schema')->create('flights', function (Blueprint $table) {
            $table->id();
            $table->json('movies')->default(new Expression('(JSON_ARRAY())'));
            $table->timestamps();
        });
    }
};
```

> [!WARNING]
> Support for default expressions depends on your database driver, database version, and the field type. Please refer to your database's documentation.

#### Column Order

When using the MariaDB or MySQL database, the `after` method may be used to add columns after an existing column in the schema:

```php
$table->after('password', function (Blueprint $table) {
    $table->string('address_line1');
    $table->string('address_line2');
    $table->string('city');
});
```

#### Instant Column Operations

When using MySQL, you may chain the `instant` modifier onto a column definition to indicate that the column should be added or modified using MySQL's "instant" algorithm. This algorithm allows certain schema changes to be performed without a full table rebuild, making them nearly instantaneous regardless of table size:

```php
$table->string('name')->nullable()->instant();
```

Instant column additions can only append columns to the end of the table, so the `instant` modifier cannot be combined with the `after` or `first` modifiers. In addition, the algorithm does not support all column types or operations. If the requested operation is incompatible, MySQL will raise an error.

Please refer to [MySQL's documentation](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html) to determine which operations are compatible with instant column modifications.

<a id="ddl-locking"></a>
#### DDL Locking

When using MySQL, you may chain the `lock` modifier onto column, index, or foreign key definitions to control table locking during schema operations. MySQL supports several lock modes: `none` allows concurrent reads and writes, `shared` allows concurrent reads but blocks writes, `exclusive` blocks all concurrent access, and `default` lets MySQL choose the most appropriate mode:

```php
$table->string('name')->lock('none');

$table->index('email')->lock('shared');
```

If the requested lock mode is incompatible with the operation, MySQL will raise an error. The `lock` modifier may be combined with the `instant` modifier to further optimize schema changes:

```php
$table->string('name')->instant()->lock('none');
```

### Modifying Columns

The `change` method allows you to modify the type and attributes of existing columns. For example, you may wish to increase the size of a `string` column. To see the `change` method in action, let's increase the size of the `name` column from 25 to 50. To accomplish this, we simply define the new state of the column and then call the `change` method:

```php
app('db.schema')->table('users', function (Blueprint $table) {
    $table->string('name', 50)->change();
});
```

When modifying a column, you must explicitly include all the modifiers you want to keep on the column definition - any missing attribute will be dropped. For example, to retain the `unsigned`, `default`, and `comment` attributes, you must call each modifier explicitly when changing the column:

```php
app('db.schema')->table('users', function (Blueprint $table) {
    $table->integer('votes')->unsigned()->default(1)->comment('my comment')->change();
});
```

The `change` method does not change the indexes of the column. Therefore, you may use index modifiers to explicitly add or drop an index when modifying the column:

```php
// Add an index...
$table->bigIncrements('id')->primary()->change();

// Drop an index...
$table->char('postal_code', 10)->unique(false)->change();
```

#### PostgreSQL Column Modifications

When changing a column's type on PostgreSQL, you may use the `using` modifier to specify the expression used to cast the existing values:

```php
app('db.schema')->table('users', function (Blueprint $table) {
    $table->date('birthday')->using('birthday::date')->change();
});
```

### Renaming Columns

To rename a column, you may use the `renameColumn` method provided by the schema builder:

```php
app('db.schema')->table('users', function (Blueprint $table) {
    $table->renameColumn('from', 'to');
});
```

### Dropping Columns

To drop a column, you may use the `dropColumn` method on the schema builder:

```php
app('db.schema')->table('users', function (Blueprint $table) {
    $table->dropColumn('votes');
});
```

You may drop multiple columns from a table by passing an array of column names to the `dropColumn` method:

```php
app('db.schema')->table('users', function (Blueprint $table) {
    $table->dropColumn(['votes', 'avatar', 'location']);
});
```

#### Available Command Aliases

Venusian provides several convenient methods related to dropping common types of columns. Each of these methods is described in the table below:

| Command                             | Description                                           |
| ----------------------------------- | ----------------------------------------------------- |
| `$table->dropMorphs('morphable');`  | Drop the `morphable_type` and `morphable_id` columns. |
| `$table->dropRememberToken();`      | Drop the `remember_token` column.                     |
| `$table->dropSoftDeletes();`        | Drop the `deleted_at` column.                         |
| `$table->dropSoftDeletesTz();`      | Alias of `dropSoftDeletes()` method.                  |
| `$table->dropTimestamps();`         | Drop the `created_at` and `updated_at` columns.       |
| `$table->dropTimestampsTz();`       | Alias of `dropTimestamps()` method.                   |

## Indexes

<a id="creating-indexes"></a>
### Creating Indexes

The Venusian schema builder supports several types of indexes. The following example creates a new `email` column and specifies that its values should be unique. To create the index, we can chain the `unique` method onto the column definition:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->table('users', function (Blueprint $table) {
    $table->string('email')->unique();
});
```

Alternatively, you may create the index after defining the column. To do so, you should call the `unique` method on the schema builder blueprint. This method accepts the name of the column that should receive a unique index:

```php
$table->unique('email');
```

You may even pass an array of columns to an index method to create a compound (or composite) index:

```php
$table->index(['account_id', 'created_at']);
```

When creating an index, Venusian will automatically generate an index name based on the table, column names, and the index type, but you may pass a second argument to the method to specify the index name yourself:

```php
$table->unique('email', 'unique_email');
```

<a id="available-index-types"></a>
#### Available Index Types

Venusian's schema builder blueprint class provides methods for creating each type of index supported by Venusian. Each index method accepts an optional second argument to specify the name of the index. If omitted, the name will be derived from the names of the table and column(s) used for the index, as well as the index type. Each of the available index methods is described in the table below:

| Command                                          | Description                                                    |
| ------------------------------------------------ | -------------------------------------------------------------- |
| `$table->primary('id');`                         | Adds a primary key.                                            |
| `$table->primary(['id', 'parent_id']);`          | Adds composite keys.                                           |
| `$table->unique('email');`                       | Adds a unique index.                                           |
| `$table->index('state');`                        | Adds an index.                                                 |
| `$table->fullText('body');`                      | Adds a full text index (MariaDB / MySQL / PostgreSQL).         |
| `$table->fullText('body')->language('english');` | Adds a full text index of the specified language (PostgreSQL). |
| `$table->spatialIndex('location');`              | Adds a spatial index (except SQLite).                          |
| `$table->vectorIndex('embedding');`              | Adds a vector index (MariaDB / PostgreSQL).                    |

#### Online Index Creation

By default, creating an index on a large table can lock the table and block reads or writes while the index is being built. When using PostgreSQL or SQL Server, you may chain the `online` method onto an index definition to create the index without locking the table, allowing your application to continue reading and writing data during index creation:

```php
$table->unique('email')->online();
```

When using PostgreSQL, this adds the `CONCURRENTLY` option to the index creation statement. When using SQL Server, this adds the `WITH (online = on)` option.

When using MySQL, you may chain the [`lock` modifier](#ddl-locking) onto an index or foreign key definition to control table locking while it is built:

```php
$table->index('email')->lock('none');
```

Refer to [MySQL's documentation](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html) to determine which operations support which lock modes.

### Renaming Indexes

To rename an index, you may use the `renameIndex` method provided by the schema builder blueprint. This method accepts the current index name as its first argument and the desired name as its second argument:

```php
$table->renameIndex('from', 'to');
```

### Dropping Indexes

To drop an index, you must specify the index's name. By default, Venusian automatically assigns an index name based on the table name, the name of the indexed column, and the index type. Here are some examples:

| Command                                                       | Description                                                 |
| ------------------------------------------------------------- | ----------------------------------------------------------- |
| `$table->dropPrimary('users_id_primary');`                    | Drop a primary key from the "users" table.                  |
| `$table->dropUnique('users_email_unique');`                   | Drop a unique index from the "users" table.                 |
| `$table->dropIndex('geo_state_index');`                       | Drop a basic index from the "geo" table.                    |
| `$table->dropFullText('posts_body_fulltext');`                | Drop a full text index from the "posts" table.              |
| `$table->dropSpatialIndex('geo_location_spatialindex');`      | Drop a spatial index from the "geo" table  (except SQLite). |

If you pass an array of columns into a method that drops indexes, the conventional index name will be generated based on the table name, columns, and index type:

```php
app('db.schema')->table('geo', function (Blueprint $table) {
    $table->dropIndex(['state']); // Drops index 'geo_state_index'
});
```

### Foreign Key Constraints

Venusian also provides support for creating foreign key constraints, which are used to force referential integrity at the database level. For example, let's define a `user_id` column on the `posts` table that references the `id` column on a `users` table:

```php
use Voyager\Database\Schema\Blueprint;

app('db.schema')->table('posts', function (Blueprint $table) {
    $table->unsignedBigInteger('user_id');

    $table->foreign('user_id')->references('id')->on('users');
});
```

Since this syntax is rather verbose, Venusian provides additional, terser methods that use conventions to provide a better developer experience. When using the `foreignId` method to create your column, the example above can be rewritten like so:

```php
app('db.schema')->table('posts', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained();
});
```

The `foreignId` method creates an `UNSIGNED BIGINT` equivalent column, while the `constrained` method will use conventions to determine the table and column being referenced. If your table name does not match Venusian's conventions, you may manually provide it to the `constrained` method. In addition, the name that should be assigned to the generated index may be specified as well:

```php
app('db.schema')->table('posts', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained(
        table: 'users', indexName: 'posts_user_id'
    );
});
```

You may also specify the desired action for the "on delete" and "on update" properties of the constraint:

```php
$table->foreignId('user_id')
    ->constrained()
    ->onUpdate('cascade')
    ->onDelete('cascade');
```

An alternative, expressive syntax is also provided for these actions:

| Method                        | Description                                       |
| ----------------------------- | ------------------------------------------------- |
| `$table->cascadeOnUpdate();`  | Updates should cascade.                           |
| `$table->restrictOnUpdate();` | Updates should be restricted.                     |
| `$table->nullOnUpdate();`     | Updates should set the foreign key value to null. |
| `$table->noActionOnUpdate();` | No action on updates.                             |
| `$table->cascadeOnDelete();`  | Deletes should cascade.                           |
| `$table->restrictOnDelete();` | Deletes should be restricted.                     |
| `$table->nullOnDelete();`     | Deletes should set the foreign key value to null. |
| `$table->noActionOnDelete();` | Prevents deletes if child records exist.          |

Any additional [column modifiers](#column-modifiers) must be called before the `constrained` method:

```php
$table->foreignId('user_id')
    ->nullable()
    ->constrained();
```

#### Dropping Foreign Keys

To drop a foreign key, you may use the `dropForeign` method, passing the name of the foreign key constraint to be deleted as an argument. Foreign key constraints use the same naming convention as indexes. In other words, the foreign key constraint name is based on the name of the table and the columns in the constraint, followed by a "\_foreign" suffix:

```php
$table->dropForeign('posts_user_id_foreign');
```

Alternatively, you may pass an array containing the column name that holds the foreign key to the `dropForeign` method. The array will be converted to a foreign key constraint name using Venusian's constraint naming conventions:

```php
$table->dropForeign(['user_id']);
```

#### Toggling Foreign Key Constraints

You may enable or disable foreign key constraints within your migrations by using the following methods:

```php
app('db.schema')->enableForeignKeyConstraints();

app('db.schema')->disableForeignKeyConstraints();

app('db.schema')->withoutForeignKeyConstraints(function () {
    // Constraints disabled within this closure...
});
```

> [!WARNING]
> SQLite disables foreign key constraints by default. When using SQLite, make sure to [enable foreign key support](/docs/{{version}}/framework/database/database#sqlite-configuration) in your database configuration before attempting to create them in your migrations.

## Signals

For convenience, each migration operation will dispatch a [signal](/docs/{{version}}/framework/digging-deeper/signals). With the exception of `SchemaLoaded`, all of the following signals implement the `Voyager\Contracts\Database\Events\MigrationEvent` interface:

| Class                                            | Description                                      |
| ------------------------------------------------ | ------------------------------------------------ |
| `Voyager\Database\Events\DatabaseRefreshed`   | The `migrate:fresh` or `migrate:refresh` command has finished. |
| `Voyager\Database\Events\MigrationsStarted`   | A batch of migrations is about to be executed.   |
| `Voyager\Database\Events\MigrationsEnded`     | A batch of migrations has finished.              |
| `Voyager\Database\Events\MigrationStarted`    | A single migration is about to be executed.      |
| `Voyager\Database\Events\MigrationEnded`      | A single migration has finished.                 |
| `Voyager\Database\Events\MigrationSkipped`    | A migration's `shouldRun` method returned `false`. |
| `Voyager\Database\Events\NoPendingMigrations` | A migration command found no pending migrations. |
| `Voyager\Database\Events\SchemaLoaded`        | An existing database schema file has loaded.     |
