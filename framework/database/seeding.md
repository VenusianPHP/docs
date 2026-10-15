# Database: Seeding

Venusian includes the ability to seed your database with data using seed classes.

## Introduction

Venusian includes the ability to seed your database with data using seed classes. All seed classes are stored in the `database/seeders` directory under the `Database\Seeders` namespace. By default, a `DatabaseSeeder` class is defined for you. From this class, you may use the `call` method to run other seed classes, allowing you to control the seeding order.

## Writing Seeders

A seeder is a class in the `database/seeders` directory that extends `Voyager\Database\Seeder`. To add one, create the file next to `DatabaseSeeder`, for example `database/seeders/UserSeeder.php`:

```php
<?php

namespace Database\Seeders;

use Voyager\Database\Seeder;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeders.
     */
    public function run(): void
    {
        // ...
    }
}
```

A seeder class only contains one method by default: `run`. This method is called when the seeder is [run](#running-seeders). Within the `run` method, you may insert data into your database however you wish. You may use the [query builder](/docs/{{version}}/framework/database/queries) to manually insert data or you may use [Instrument model factories](/docs/{{version}}/framework/instrument-orm/instrument-factories).

As an example, let's modify the default `DatabaseSeeder` class and add a database insert statement to the `run` method:

```php
<?php

namespace Database\Seeders;

use Voyager\Database\Seeder;
use Voyager\NutsAndBolts\DataObjects\Str;

class DatabaseSeeder extends Seeder
{
    /**
     * Run the database seeders.
     */
    public function run(): void
    {
        app('db')->table('users')->insert([
            'name' => Str::random(10),
            'email' => Str::random(10).'@example.com',
            'password' => app('hash')->make('password'),
        ]);
    }
}
```

> [!NOTE]
> When a seeder has been given the container with `setContainer`, you may type-hint any dependencies you need within the `run` method's signature. They will automatically be resolved via the Venusian [service container](/docs/{{version}}/framework/architecture-concepts/container).

### Using Model Factories

Of course, manually specifying the attributes for each model seed is cumbersome. Instead, you can use [model factories](/docs/{{version}}/framework/instrument-orm/instrument-factories) to conveniently generate large amounts of database records. First, review the [model factory documentation](/docs/{{version}}/framework/instrument-orm/instrument-factories) to learn how to define your factories.

For example, let's create 50 users that each has one related post:

```php
use App\Models\User;

/**
 * Run the database seeders.
 */
public function run(): void
{
    User::factory()
        ->count(50)
        ->hasPosts(1)
        ->create();
}
```

### Calling Additional Seeders

Within the `DatabaseSeeder` class, you may use the `call` method to execute additional seed classes. Using the `call` method allows you to break up your database seeding into multiple files so that no single seeder class becomes too large. The `call` method accepts an array of seeder classes that should be executed:

```php
/**
 * Run the database seeders.
 */
public function run(): void
{
    $this->call([
        UserSeeder::class,
        PostSeeder::class,
        CommentSeeder::class,
    ]);
}
```

The `callOnce` method skips any seeder that has already been called, `callSilent` runs seeders without printing their progress, and `callWith` passes an array of parameters to each seeder's `run` method:

```php
$this->callOnce(UserSeeder::class);

$this->callSilent(PostSeeder::class);

$this->callWith(CommentSeeder::class, ['count' => 10]);
```

### Muting Model Signals

While running seeds, you may want to prevent models from dispatching signals. You may achieve this using the `WithoutModelEvents` trait. When used, the `WithoutModelEvents` trait ensures no model signals are dispatched, even if additional seed classes are executed via the `call` method:

```php
<?php

namespace Database\Seeders;

use Voyager\Database\Seeder;
use Voyager\Database\Console\Seeds\WithoutModelEvents;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Run the database seeders.
     */
    public function run(): void
    {
        $this->call([
            UserSeeder::class,
        ]);
    }
}
```

<a id="running-seeders"></a>
## Running Seeders

A seeder runs when it is invoked. Resolve it from the container, hand it the container with `setContainer` so that the seeders it calls, and the dependencies its `run` method type-hints, are resolved through it, and invoke it. Wrap the call in `Model::unguarded` so that [mass assignment protection](/docs/{{version}}/framework/instrument-orm/instrument#mass-assignment) does not reject the attributes your seeders and factories fill:

```php
use Database\Seeders\DatabaseSeeder;
use Voyager\Database\Instrument\Model;

Model::unguarded(function () {
    app(DatabaseSeeder::class)->setContainer(app())->__invoke();
});
```

You may run this from [Probe](/docs/{{version}}/framework/digging-deeper/computer#probe-repl) with `php computer probe`, or from one of your own [Computer commands](/docs/{{version}}/framework/digging-deeper/computer#writing-commands). Inside a command, also pass the command to `setCommand`, and each seeder the `call` method runs prints its name and run time to the command's output:

```php
<?php

namespace App\Console\Commands;

use Database\Seeders\DatabaseSeeder;
use Voyager\Console\Command;
use Voyager\Database\Instrument\Model;

class SeedDatabase extends Command
{
    protected ?string $signature = 'app:seed';

    protected string $description = 'Seed the database';

    public function handle(): int
    {
        Model::unguarded(function () {
            app(DatabaseSeeder::class)
                ->setContainer(app())
                ->setCommand($this)
                ->__invoke();
        });

        return self::SUCCESS;
    }
}
```

To run a single seeder, invoke that class instead of `DatabaseSeeder`.
