# Instrument: Factories

Model factories define default attributes for your Instrument models so tests and seeders can create records without spelling out every column.

## Introduction

When testing your application or seeding your database, you may need to insert a few records into your database. Instead of manually specifying the value of each column, Venusian allows you to define a set of default attributes for each of your [Instrument models](/docs/{{version}}/framework/instrument-orm/instrument) using model factories.

Factories live in your application's `database/factories` directory under the `Database\Factories` namespace. A factory for an `App\Models\User` model might look like the following:

```php
namespace Database\Factories;

use Voyager\Database\Instrument\Factories\Factory;
use Voyager\NutsAndBolts\DataObjects\Str;

/**
 * @extends \Voyager\Database\Instrument\Factories\Factory<\App\Models\User>
 */
class UserFactory extends Factory
{
    /**
     * The current password being used by the factory.
     */
    protected static ?string $password;

    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'name' => $this->faker->name(),
            'email' => $this->faker->unique()->safeEmail(),
            'email_verified_at' => now(),
            'password' => static::$password ??= app('hash')->make('password'),
            'remember_token' => Str::random(10),
        ];
    }

    /**
     * Indicate that the model's email address should be unverified.
     */
    public function unverified(): static
    {
        return $this->state(fn (array $attributes) => [
            'email_verified_at' => null,
        ]);
    }
}
```

As you can see, in their most basic form, factories are classes that extend the base `Voyager\Database\Instrument\Factories\Factory` class and define a `definition` method. The `definition` method returns the default set of attribute values that should be applied when creating a model using the factory.

Via the `$this->faker` property, factories have access to the [Faker](https://github.com/FakerPHP/Faker) PHP library, which allows you to conveniently generate various kinds of random data for testing and seeding. New applications require `fakerphp/faker` as a development dependency; the `$this->faker` property is `null` when the library is not installed.

A new application's `composer.json` only autoloads `Database\Seeders`, so add the factories namespace to its `autoload.psr-4` section and run `composer dump-autoload` before using your first factory:

```json
"autoload": {
    "psr-4": {
        "App\\": "app/",
        "Database\\Factories\\": "database/factories/",
        "Database\\Seeders\\": "database/seeders/"
    }
}
```

> [!NOTE]
> Faker uses the `en_US` locale unless your `config/app.php` configuration file defines a `faker_locale` option.

## Defining Model Factories

### Generating Factories

To create a factory, execute the `make:factory` [Computer command](/docs/{{version}}/framework/digging-deeper/computer):

```shell
php computer make:factory PostFactory
```

The new factory class will be placed in your `database/factories` directory. The command guesses the model from the factory's name; you may name it explicitly using the `--model` option:

```shell
php computer make:factory PostFactory --model=Post
```

#### Model and Factory Discovery Conventions

Once you have defined your factories, you may use the static `factory` method provided to your models by the `Voyager\Database\Instrument\Factories\HasFactory` trait in order to instantiate a factory instance for that model.

The `HasFactory` trait's `factory` method will use conventions to determine the proper factory for the model the trait is assigned to. Specifically, the method will look for a factory in the `Database\Factories` namespace that has a class name matching the model name and is suffixed with `Factory`. If these conventions do not apply to your particular application or factory, you may add the `UseFactory` attribute to the model to manually specify the model's factory:

```php
use Voyager\Database\Instrument\Attributes\UseFactory;
use Database\Factories\Administration\FlightFactory;

#[UseFactory(FlightFactory::class)]
class Flight extends Model
{
    // ...
}
```

You may also name the factory with a static `$factory` property on the model:

```php
use Database\Factories\Administration\FlightFactory;
use Voyager\Database\Instrument\Factories\HasFactory;
use Voyager\Database\Instrument\Model;

class Flight extends Model
{
    use HasFactory;

    /**
     * The factory for the model.
     */
    protected static string $factory = FlightFactory::class;
}
```

Alternatively, you may overwrite the `newFactory` method on your model to return an instance of the model's corresponding factory directly:

```php
use Database\Factories\Administration\FlightFactory;

/**
 * Create a new factory instance for the model.
 */
protected static function newFactory()
{
    return FlightFactory::new();
}
```

Then, define a `$model` property on the corresponding factory to specify the model:

```php
use App\Administration\Flight;
use Voyager\Database\Instrument\Factories\Factory;

class FlightFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var class-string<\App\Administration\Flight>
     */
    protected $model = Flight::class;

    // ...
}
```

<a id="factory-states"></a>
### Factory States

State manipulation methods allow you to define discrete modifications that can be applied to your model factories in any combination. For example, your `Database\Factories\UserFactory` factory might contain a `suspended` state method that modifies one of its default attribute values.

State transformation methods typically call the `state` method provided by the base factory class. The `state` method accepts a closure which will receive the array of raw attributes defined for the factory and should return an array of attributes to modify:

```php
use Voyager\Database\Instrument\Factories\Factory;

/**
 * Indicate that the user is suspended.
 */
public function suspended(): Factory
{
    return $this->state(function (array $attributes) {
        return [
            'account_status' => 'suspended',
        ];
    });
}
```

#### "Trashed" State

If your Instrument model can be [soft deleted](/docs/{{version}}/framework/instrument-orm/instrument#soft-deleting), you may invoke the built-in `trashed` state method to indicate that the created model should already be "soft deleted". You do not need to manually define the `trashed` state as it is automatically available to all factories:

```php
use App\Models\User;

$user = User::factory()->trashed()->create();
```

The `deleted_at` column is set to one day ago by default. You may pass the deletion time to the `trashed` method instead:

```php
$user = User::factory()->trashed(now()->subWeek())->create();
```

### Factory Callbacks

Factory callbacks are registered using the `afterMaking` and `afterCreating` methods and allow you to perform additional tasks after making or creating a model. You should register these callbacks by defining a `configure` method on your factory class. This method will be automatically called when the factory is instantiated:

```php
namespace Database\Factories;

use App\Models\User;
use Voyager\Database\Instrument\Factories\Factory;

class UserFactory extends Factory
{
    /**
     * Configure the model factory.
     */
    public function configure(): static
    {
        return $this->afterMaking(function (User $user) {
            // ...
        })->afterCreating(function (User $user) {
            // ...
        });
    }

    // ...
}
```

You may also register factory callbacks within state methods to perform additional tasks that are specific to a given state:

```php
use App\Models\User;
use Voyager\Database\Instrument\Factories\Factory;

/**
 * Indicate that the user is suspended.
 */
public function suspended(): Factory
{
    return $this->state(function (array $attributes) {
        return [
            'account_status' => 'suspended',
        ];
    })->afterMaking(function (User $user) {
        // ...
    })->afterCreating(function (User $user) {
        // ...
    });
}
```

## Creating Models Using Factories

### Instantiating Models

Once you have defined your factories, you may use the static `factory` method provided to your models by the `Voyager\Database\Instrument\Factories\HasFactory` trait in order to instantiate a factory instance for that model. Let's take a look at a few examples of creating models. First, we'll use the `make` method to create models without persisting them to the database:

```php
use App\Models\User;

$user = User::factory()->make();
```

You may create a collection of many models using the `count` method:

```php
$users = User::factory()->count(3)->make();
```

#### Applying States

You may also apply any of your [states](#factory-states) to the models. If you would like to apply multiple state transformations to the models, you may simply call the state transformation methods directly:

```php
$users = User::factory()->count(5)->suspended()->make();
```

#### Overriding Attributes

If you would like to override some of the default values of your models, you may pass an array of values to the `make` method. Only the specified attributes will be replaced while the rest of the attributes remain set to their default values as specified by the factory:

```php
$user = User::factory()->make([
    'name' => 'Abigail Otwell',
]);
```

Alternatively, the `state` method may be called directly on the factory instance to perform an inline state transformation:

```php
$user = User::factory()->state([
    'name' => 'Abigail Otwell',
])->make();
```

> [!NOTE]
> [Mass assignment protection](/docs/{{version}}/framework/instrument-orm/instrument#mass-assignment) is automatically disabled when creating models using factories.

### Persisting Models

The `create` method instantiates model instances and persists them to the database using Instrument's `save` method:

```php
use App\Models\User;

// Create a single App\Models\User instance...
$user = User::factory()->create();

// Create three App\Models\User instances...
$users = User::factory()->count(3)->create();
```

You may override the factory's default model attributes by passing an array of attributes to the `create` method:

```php
$user = User::factory()->create([
    'name' => 'Abigail',
]);
```

### Sequences

Sometimes you may wish to alternate the value of a given model attribute for each created model. You may accomplish this by defining a state transformation as a sequence. For example, you may wish to alternate the value of an `admin` column between `Y` and `N` for each created user:

```php
use App\Models\User;
use Voyager\Database\Instrument\Factories\Sequence;

$users = User::factory()
    ->count(10)
    ->state(new Sequence(
        ['admin' => 'Y'],
        ['admin' => 'N'],
    ))
    ->create();
```

In this example, five users will be created with an `admin` value of `Y` and five users will be created with an `admin` value of `N`.

If necessary, you may include a closure as a sequence value. The closure will be invoked each time the sequence needs a new value:

```php
use Voyager\Database\Instrument\Factories\Sequence;

$users = User::factory()
    ->count(10)
    ->state(new Sequence(
        fn (Sequence $sequence) => ['role' => UserRoles::all()->random()],
    ))
    ->create();
```

Within a sequence closure, you may access the `$index` property on the sequence instance that is injected into the closure. The `$index` property contains the number of iterations through the sequence that have occurred thus far:

```php
$users = User::factory()
    ->count(10)
    ->state(new Sequence(
        fn (Sequence $sequence) => ['name' => 'Name '.$sequence->index],
    ))
    ->create();
```

For convenience, sequences may also be applied using the `sequence` method, which simply invokes the `state` method internally. The `sequence` method accepts a closure or arrays of sequenced attributes:

```php
$users = User::factory()
    ->count(2)
    ->sequence(
        ['name' => 'First User'],
        ['name' => 'Second User'],
    )
    ->create();
```

## Factory Relationships

<a id="has-many-relationships"></a>
### Has Many Relationships

Next, let's explore building Instrument model relationships using the fluent factory methods. First, let's assume our application has an `App\Models\User` model and an `App\Models\Post` model. Also, let's assume that the `User` model defines a `hasMany` relationship with `Post`. We can create a user that has three posts using the `has` method provided by factories. The `has` method accepts a factory instance:

```php
use App\Models\Post;
use App\Models\User;

$user = User::factory()
    ->has(Post::factory()->count(3))
    ->create();
```

By convention, when passing a `Post` model to the `has` method, Instrument will assume that the `User` model must have a `posts` method that defines the relationship. If necessary, you may explicitly specify the name of the relationship that you would like to manipulate:

```php
$user = User::factory()
    ->has(Post::factory()->count(3), 'posts')
    ->create();
```

Of course, you may perform state manipulations on the related models. In addition, you may pass a closure-based state transformation if your state change requires access to the parent model:

```php
$user = User::factory()
    ->has(
        Post::factory()
            ->count(3)
            ->state(function (array $attributes, User $user) {
                return ['user_type' => $user->type];
            })
    )
    ->create();
```

#### Using Magic Methods

For convenience, you may use the magic factory relationship methods to build relationships. For example, the following example will use convention to determine that the related models should be created via a `posts` relationship method on the `User` model:

```php
$user = User::factory()
    ->hasPosts(3)
    ->create();
```

When using magic methods to create factory relationships, you may pass an array of attributes to override on the related models:

```php
$user = User::factory()
    ->hasPosts(3, [
        'published' => false,
    ])
    ->create();
```

You may provide a closure-based state transformation if your state change requires access to the parent model:

```php
$user = User::factory()
    ->hasPosts(3, function (array $attributes, User $user) {
        return ['user_type' => $user->type];
    })
    ->create();
```

### Belongs To Relationships

Now that we have explored how to build "has many" relationships using factories, let's explore the inverse of the relationship. The `for` method may be used to define the parent model that factory created models belong to. For example, we can create three `App\Models\Post` model instances that belong to a single user:

```php
use App\Models\Post;
use App\Models\User;

$posts = Post::factory()
    ->count(3)
    ->for(User::factory()->state([
        'name' => 'Jessica Archer',
    ]))
    ->create();
```

If you already have a parent model instance that should be associated with the models you are creating, you may pass the model instance to the `for` method:

```php
$user = User::factory()->create();

$posts = Post::factory()
    ->count(3)
    ->for($user)
    ->create();
```

#### Using Magic Methods

For convenience, you may use the magic factory relationship methods to define "belongs to" relationships. For example, the following example will use convention to determine that the three posts should belong to the `user` relationship on the `Post` model:

```php
$posts = Post::factory()
    ->count(3)
    ->forUser([
        'name' => 'Jessica Archer',
    ])
    ->create();
```

### Many to Many Relationships

Like [has many relationships](#has-many-relationships), "many to many" relationships may be created using the `has` method:

```php
use App\Models\Role;
use App\Models\User;

$user = User::factory()
    ->has(Role::factory()->count(3))
    ->create();
```

#### Pivot Table Attributes

If you need to define attributes that should be set on the pivot / intermediate table linking the models, you may use the `hasAttached` method. This method accepts an array of pivot table attribute names and values as its second argument:

```php
use App\Models\Role;
use App\Models\User;

$user = User::factory()
    ->hasAttached(
        Role::factory()->count(3),
        ['active' => true]
    )
    ->create();
```

You may provide a closure-based state transformation if your state change requires access to the related model:

```php
$user = User::factory()
    ->hasAttached(
        Role::factory()
            ->count(3)
            ->state(function (array $attributes, User $user) {
                return ['name' => $user->name.' Role'];
            }),
        ['active' => true]
    )
    ->create();
```

If you already have model instances that you would like to be attached to the models you are creating, you may pass the model instances to the `hasAttached` method. In this example, the same three roles will be attached to all three users:

```php
$roles = Role::factory()->count(3)->create();

$users = User::factory()
    ->count(3)
    ->hasAttached($roles, ['active' => true])
    ->create();
```

#### Using Magic Methods

For convenience, you may use the magic factory relationship methods to define many to many relationships. For example, the following example will use convention to determine that the related models should be created via a `roles` relationship method on the `User` model:

```php
$user = User::factory()
    ->hasRoles(1, [
        'name' => 'Editor'
    ])
    ->create();
```

### Polymorphic Relationships

[Polymorphic relationships](/docs/{{version}}/framework/instrument-orm/instrument-relationships#polymorphic-relationships) may also be created using factories. Polymorphic "morph many" relationships are created in the same way as typical "has many" relationships. For example, if an `App\Models\Post` model has a `morphMany` relationship with an `App\Models\Comment` model:

```php
use App\Models\Post;

$post = Post::factory()->hasComments(3)->create();
```

#### Morph To Relationships

Magic methods may not be used to create `morphTo` relationships. Instead, the `for` method must be used directly and the name of the relationship must be explicitly provided. For example, imagine that the `Comment` model has a `commentable` method that defines a `morphTo` relationship. In this situation, we may create three comments that belong to a single post by using the `for` method directly:

```php
$comments = Comment::factory()->count(3)->for(
    Post::factory(), 'commentable'
)->create();
```

#### Polymorphic Many to Many Relationships

Polymorphic "many to many" (`morphToMany` / `morphedByMany`) relationships may be created just like non-polymorphic "many to many" relationships:

```php
use App\Models\Tag;
use App\Models\Video;

$video = Video::factory()
    ->hasAttached(
        Tag::factory()->count(3),
        ['public' => true]
    )
    ->create();
```

Of course, the magic `has` method may also be used to create polymorphic "many to many" relationships:

```php
$video = Video::factory()
    ->hasTags(3, ['public' => true])
    ->create();
```

### Defining Relationships Within Factories

To define a relationship within your model factory, you will typically assign a new factory instance to the foreign key of the relationship. This is normally done for the "inverse" relationships such as `belongsTo` and `morphTo` relationships. For example, if you would like to create a new user when creating a post, you may do the following:

```php
use App\Models\User;

/**
 * Define the model's default state.
 *
 * @return array<string, mixed>
 */
public function definition(): array
{
    return [
        'user_id' => User::factory(),
        'title' => $this->faker->sentence(),
        'content' => $this->faker->paragraph(),
    ];
}
```

If the relationship's columns depend on the factory that defines it you may assign a closure to an attribute. The closure will receive the factory's evaluated attribute array:

```php
/**
 * Define the model's default state.
 *
 * @return array<string, mixed>
 */
public function definition(): array
{
    return [
        'user_id' => User::factory(),
        'user_type' => function (array $attributes) {
            return User::find($attributes['user_id'])->type;
        },
        'title' => $this->faker->sentence(),
        'content' => $this->faker->paragraph(),
    ];
}
```

### Recycling an Existing Model for Relationships

If you have models that share a common relationship with another model, you may use the `recycle` method to ensure a single instance of the related model is recycled for all of the relationships created by the factory.

For example, imagine you have `Airline`, `Flight`, and `Ticket` models, where the ticket belongs to an airline and a flight, and the flight also belongs to an airline. When creating tickets, you will probably want the same airline for both the ticket and the flight, so you may pass an airline instance to the `recycle` method:

```php
Ticket::factory()
    ->recycle(Airline::factory()->create())
    ->create();
```

You may find the `recycle` method particularly useful if you have models belonging to a common user or team.

The `recycle` method also accepts a collection of existing models. When a collection is provided to the `recycle` method, a random model from the collection will be chosen when the factory needs a model of that type:

```php
Ticket::factory()
    ->recycle($airlines)
    ->create();
```
