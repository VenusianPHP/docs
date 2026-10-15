# Instrument: Collections

All Instrument methods that return more than one model result will return instances of the Voyager\Database\Instrument\Collection class, including results retrieved via the get method or accessed via a relationship.

## Introduction

All Instrument methods that return more than one model result will return instances of the `Voyager\Database\Instrument\Collection` class, including results retrieved via the `get` method or accessed via a relationship. The Instrument collection object extends the [base collection](/docs/{{version}}/framework/digging-deeper/collections), `Voyager\NutsAndBolts\Collection`, so it naturally inherits dozens of methods used to fluently work with the underlying array of Instrument models. Be sure to review the collection documentation to learn all about these helpful methods!

All collections also serve as iterators, allowing you to loop over them as if they were simple PHP arrays:

```php
use App\Models\User;

$users = User::where('active', 1)->get();

foreach ($users as $user) {
    echo $user->name;
}
```

However, as previously mentioned, collections are much more powerful than arrays and expose a variety of map / reduce operations that may be chained using an intuitive interface. For example, we may remove all inactive models and then gather the first name for each remaining user:

```php
$names = User::all()->reject(function (User $user) {
    return $user->active === false;
})->map(function (User $user) {
    return $user->name;
});
```

#### Collections From Offloaded Queries

A query offloaded to the worker pools with `via()` settles its promise with the same Instrument collection a blocking `get` returns. Your models' `retrieved` Signals fire in the calling process once the rows arrive:

```php
use App\Models\User;

$promise = User::where('active', 1)->via()->get();

$promise->then(function ($users) {
    // $users is a Voyager\Database\Instrument\Collection...
});

$users = $promise->wait();
```

`via()` accepts the pool to run in, `'thread'` or `'process'`; without one, the thread workers are used when they are enabled and the process workers otherwise.

#### Instrument Collection Conversion

While most Instrument collection methods return a new instance of an Instrument collection, the `collapse`, `flatten`, `flip`, `keys`, `pluck`, and `zip` methods return a [base collection](/docs/{{version}}/framework/digging-deeper/collections) instance. Likewise, if a `map` operation returns a collection that does not contain any Instrument models, it will be converted to a base collection instance.

<a id="available-methods"></a>
## Available Methods

All Instrument collections extend the base [collection](/docs/{{version}}/framework/digging-deeper/collections#available-methods) object; therefore, they inherit all of the powerful methods provided by the base collection class.

In addition, the `Voyager\Database\Instrument\Collection` class provides a superset of methods to aid with managing your model collections. Most methods return `Voyager\Database\Instrument\Collection` instances; however, some methods, like `pluck`, return a `Voyager\NutsAndBolts\Collection` instance.

[append](#method-append)
[contains](#method-contains)
[diff](#method-diff)
[except](#method-except)
[find](#method-find)
[findOrFail](#method-find-or-fail)
[fresh](#method-fresh)
[intersect](#method-intersect)
[load](#method-load)
[loadMissing](#method-loadMissing)
[modelKeys](#method-modelKeys)
[makeVisible](#method-makeVisible)
[makeHidden](#method-makeHidden)
[mergeVisible](#method-mergeVisible)
[mergeHidden](#method-mergeHidden)
[only](#method-only)
[partition](#method-partition)
[setAppends](#method-setAppends)
[setVisible](#method-setVisible)
[setHidden](#method-setHidden)
[toQuery](#method-toquery)
[unique](#method-unique)
[withoutAppends](#method-withoutAppends)

<a id="method-append"></a>
#### `append($attributes)`

The `append` method may be used to indicate that an attribute should be [appended](/docs/{{version}}/framework/instrument-orm/instrument-serialization#appending-values-to-json) for every model in the collection. This method accepts an array of attributes or a single attribute:

```php
$users->append('team');

$users->append(['team', 'is_admin']);
```

<a id="method-contains"></a>
#### `contains($key, $operator = null, $value = null)`

The `contains` method may be used to determine if a given model instance is contained by the collection. This method accepts a primary key or a model instance:

```php
$users->contains(1);

$users->contains(User::find(1));
```

<a id="method-diff"></a>
#### `diff($items)`

The `diff` method returns all of the models that are not present in the given collection:

```php
use App\Models\User;

$users = $users->diff(User::whereIn('id', [1, 2, 3])->get());
```

<a id="method-except"></a>
#### `except($keys)`

The `except` method returns all of the models that do not have the given primary keys:

```php
$users = $users->except([1, 2, 3]);
```

<a id="method-find"></a>
#### `find($key)`

The `find` method returns the model that has a primary key matching the given key. If `$key` is a model instance, `find` will attempt to return a model matching the primary key. If `$key` is an array of keys, `find` will return all models which have a primary key in the given array:

```php
$users = User::all();

$user = $users->find(1);
```

<a id="method-find-or-fail"></a>
#### `findOrFail($key)`

The `findOrFail` method returns the model that has a primary key matching the given key or throws an `Voyager\Database\Instrument\ModelNotFoundException` exception if no matching model can be found in the collection:

```php
$users = User::all();

$user = $users->findOrFail(1);
```

<a id="method-fresh"></a>
#### `fresh($with = [])`

The `fresh` method retrieves a fresh instance of each model in the collection from the database. In addition, any specified relationships will be eager loaded:

```php
$users = $users->fresh();

$users = $users->fresh('comments');
```

<a id="method-intersect"></a>
#### `intersect($items)`

The `intersect` method returns all of the models that are also present in the given collection:

```php
use App\Models\User;

$users = $users->intersect(User::whereIn('id', [1, 2, 3])->get());
```

<a id="method-load"></a>
#### `load($relations)`

The `load` method eager loads the given relationships for all models in the collection:

```php
$users->load(['comments', 'posts']);

$users->load('comments.author');

$users->load(['comments', 'posts' => fn ($query) => $query->where('active', 1)]);
```

<a id="method-loadMissing"></a>
#### `loadMissing($relations)`

The `loadMissing` method eager loads the given relationships for all models in the collection if the relationships are not already loaded:

```php
$users->loadMissing(['comments', 'posts']);

$users->loadMissing('comments.author');

$users->loadMissing(['comments', 'posts' => fn ($query) => $query->where('active', 1)]);
```

<a id="method-modelKeys"></a>
#### `modelKeys()`

The `modelKeys` method returns the primary keys for all models in the collection:

```php
$users->modelKeys();

// [1, 2, 3, 4, 5]
```

<a id="method-makeVisible"></a>
#### `makeVisible($attributes)`

The `makeVisible` method [makes attributes visible](/docs/{{version}}/framework/instrument-orm/instrument-serialization#hiding-attributes-from-json) that are typically "hidden" on each model in the collection:

```php
$users = $users->makeVisible(['address', 'phone_number']);
```

<a id="method-makeHidden"></a>
#### `makeHidden($attributes)`

The `makeHidden` method [hides attributes](/docs/{{version}}/framework/instrument-orm/instrument-serialization#hiding-attributes-from-json) that are typically "visible" on each model in the collection:

```php
$users = $users->makeHidden(['address', 'phone_number']);
```

<a id="method-mergeVisible"></a>
#### `mergeVisible($attributes)`

The `mergeVisible` method [makes additional attributes visible](/docs/{{version}}/framework/instrument-orm/instrument-serialization#hiding-attributes-from-json) while retaining existing visible attributes:

```php
$users = $users->mergeVisible(['middle_name']);
```

<a id="method-mergeHidden"></a>
#### `mergeHidden($attributes)`

The `mergeHidden` method [hides additional attributes](/docs/{{version}}/framework/instrument-orm/instrument-serialization#hiding-attributes-from-json) while retaining existing hidden attributes:

```php
$users = $users->mergeHidden(['last_login_at']);
```

<a id="method-only"></a>
#### `only($keys)`

The `only` method returns all of the models that have the given primary keys:

```php
$users = $users->only([1, 2, 3]);
```

<a id="method-partition"></a>
#### `partition`

The `partition` method returns an instance of `Voyager\NutsAndBolts\Collection` containing `Voyager\Database\Instrument\Collection` collection instances:

```php
$partition = $users->partition(fn ($user) => $user->age > 18);

dump($partition::class);    // Voyager\NutsAndBolts\Collection
dump($partition[0]::class); // Voyager\Database\Instrument\Collection
dump($partition[1]::class); // Voyager\Database\Instrument\Collection
```

<a id="method-setAppends"></a>
#### `setAppends($attributes)`

The `setAppends` method temporarily overrides all of the [appended attributes](/docs/{{version}}/framework/instrument-orm/instrument-serialization#appending-values-to-json) on each model in the collection:

```php
$users = $users->setAppends(['is_admin']);
```

<a id="method-setVisible"></a>
#### `setVisible($attributes)`

The `setVisible` method [temporarily overrides](/docs/{{version}}/framework/instrument-orm/instrument-serialization#temporarily-modifying-attribute-visibility) all of the visible attributes on each model in the collection:

```php
$users = $users->setVisible(['id', 'name']);
```

<a id="method-setHidden"></a>
#### `setHidden($attributes)`

The `setHidden` method [temporarily overrides](/docs/{{version}}/framework/instrument-orm/instrument-serialization#temporarily-modifying-attribute-visibility) all of the hidden attributes on each model in the collection:

```php
$users = $users->setHidden(['email', 'password', 'remember_token']);
```

<a id="method-toquery"></a>
#### `toQuery()`

The `toQuery` method returns an Instrument query builder instance containing a `whereIn` constraint on the collection model's primary keys:

```php
use App\Models\User;

$users = User::where('status', 'VIP')->get();

$users->toQuery()->update([
    'status' => 'Administrator',
]);
```

<a id="method-unique"></a>
#### `unique($key = null, $strict = false)`

The `unique` method returns all of the unique models in the collection. Any models with the same primary key as another model in the collection are removed:

```php
$users = $users->unique();
```

<a id="method-withoutAppends"></a>
#### `withoutAppends()`

The `withoutAppends` method temporarily removes all of the [appended attributes](/docs/{{version}}/framework/instrument-orm/instrument-serialization#appending-values-to-json) on each model in the collection:

```php
$users = $users->withoutAppends();
```

## Custom Collections

If you would like to use a custom `Collection` object when interacting with a given model, you may add the `CollectedBy` attribute to your model:

```php
<?php

namespace App\Models;

use App\Support\UserCollection;
use Voyager\Database\Instrument\Attributes\CollectedBy;
use Voyager\Database\Instrument\Model;

#[CollectedBy(UserCollection::class)]
class User extends Model
{
    // ...
}
```

Alternatively, you may define a `newCollection` method on your model:

```php
<?php

namespace App\Models;

use App\Support\UserCollection;
use Voyager\Database\Instrument\Collection;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Create a new Instrument Collection instance.
     *
     * @param  array<int, \Voyager\Database\Instrument\Model>  $models
     * @return \Voyager\Database\Instrument\Collection<int, \Voyager\Database\Instrument\Model>
     */
    public function newCollection(array $models = []): Collection
    {
        $collection = new UserCollection($models);

        if (Model::isAutomaticallyEagerLoadingRelationships()) {
            $collection->withRelationshipAutoloading();
        }

        return $collection;
    }
}
```

Once you have defined a `newCollection` method or added the `CollectedBy` attribute to your model, you will receive an instance of your custom collection anytime Instrument would normally return an `Voyager\Database\Instrument\Collection` instance.

If you would like to use a custom collection for every model in your application, you should define the `newCollection` method on a base model class that is extended by all of your application's models.
