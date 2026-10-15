# Helpers

Venusian includes a variety of global "helper" PHP functions.

## Introduction

Venusian includes a variety of global "helper" PHP functions. Many of these functions are used by the framework itself; however, you are free to use them in your own applications if you find them convenient.

## Available Methods

### Arrays & Objects

[Arr::accessible](#method-array-accessible)
[Arr::add](#method-array-add)
[Arr::array](#method-array-array)
[Arr::boolean](#method-array-boolean)
[Arr::collapse](#method-array-collapse)
[Arr::crossJoin](#method-array-crossjoin)
[Arr::divide](#method-array-divide)
[Arr::dot](#method-array-dot)
[Arr::every](#method-array-every)
[Arr::except](#method-array-except)
[Arr::exceptValues](#method-array-except-values)
[Arr::exists](#method-array-exists)
[Arr::first](#method-array-first)
[Arr::flatten](#method-array-flatten)
[Arr::float](#method-array-float)
[Arr::forget](#method-array-forget)
[Arr::from](#method-array-from)
[Arr::get](#method-array-get)
[Arr::has](#method-array-has)
[Arr::hasAll](#method-array-hasall)
[Arr::hasAny](#method-array-hasany)
[Arr::integer](#method-array-integer)
[Arr::isAssoc](#method-array-isassoc)
[Arr::isList](#method-array-islist)
[Arr::join](#method-array-join)
[Arr::keyBy](#method-array-keyby)
[Arr::last](#method-array-last)
[Arr::map](#method-array-map)
[Arr::mapSpread](#method-array-map-spread)
[Arr::mapWithKeys](#method-array-map-with-keys)
[Arr::only](#method-array-only)
[Arr::onlyValues](#method-array-only-values)
[Arr::partition](#method-array-partition)
[Arr::pluck](#method-array-pluck)
[Arr::prepend](#method-array-prepend)
[Arr::prependKeysWith](#method-array-prependkeyswith)
[Arr::pull](#method-array-pull)
[Arr::push](#method-array-push)
[Arr::query](#method-array-query)
[Arr::random](#method-array-random)
[Arr::reject](#method-array-reject)
[Arr::select](#method-array-select)
[Arr::set](#method-array-set)
[Arr::shuffle](#method-array-shuffle)
[Arr::sole](#method-array-sole)
[Arr::some](#method-array-some)
[Arr::sort](#method-array-sort)
[Arr::sortDesc](#method-array-sort-desc)
[Arr::sortRecursive](#method-array-sort-recursive)
[Arr::string](#method-array-string)
[Arr::take](#method-array-take)
[Arr::toCssClasses](#method-array-to-css-classes)
[Arr::toCssStyles](#method-array-to-css-styles)
[Arr::undot](#method-array-undot)
[Arr::where](#method-array-where)
[Arr::whereNotNull](#method-array-where-not-null)
[Arr::wrap](#method-array-wrap)
[data_fill](#method-data-fill)
[data_get](#method-data-get)
[data_set](#method-data-set)
[data_forget](#method-data-forget)
[head](#method-head)
[last](#method-last)
### Numbers

[Number::abbreviate](#method-number-abbreviate)
[Number::clamp](#method-number-clamp)
[Number::currency](#method-number-currency)
[Number::defaultCurrency](#method-default-currency)
[Number::defaultLocale](#method-default-locale)
[Number::fileSize](#method-number-file-size)
[Number::forHumans](#method-number-for-humans)
[Number::format](#method-number-format)
[Number::ordinal](#method-number-ordinal)
[Number::pairs](#method-number-pairs)
[Number::parse](#method-number-parse)
[Number::parseInt](#method-number-parse-int)
[Number::parseFloat](#method-number-parse-float)
[Number::percentage](#method-number-percentage)
[Number::spell](#method-number-spell)
[Number::spellOrdinal](#method-number-spell-ordinal)
[Number::trim](#method-number-trim)
[Number::useLocale](#method-number-use-locale)
[Number::withLocale](#method-number-with-locale)
[Number::useCurrency](#method-number-use-currency)
[Number::withCurrency](#method-number-with-currency)

### Paths

[app_path](#method-app-path)
[base_path](#method-base-path)
[config_path](#method-config-path)
[database_path](#method-database-path)
[storage_path](#method-storage-path)

### Miscellaneous

[app](#method-app)
[blank](#method-blank)
[broadcast](#method-broadcast)
[broadcast_if](#method-broadcast-if)
[class_uses_recursive](#method-class-uses-recursive)
[collect](#method-collect)
[computer_binary](#method-computer-binary)
[config](#method-config)
[cypher](#method-cypher)
[cypher_one](#method-cypher-one)
[cypher_run](#method-cypher-run)
[dd](#method-dd)
[device_os_family](#method-device-os-family)
[dispatch](#method-dispatch)
[dump](#method-dump)
[env](#method-env)
[filled](#method-filled)
[literal](#method-literal)
[neo4j_connection](#method-neo4j-connection)
[now](#method-now)
[once](#method-once)
[optional](#method-optional)
[php_binary](#method-php-binary)
[report](#method-report)
[rescue](#method-rescue)
[retry](#method-retry)
[rocket_binary](#method-rocket-binary)
[signal](#method-signal)
[storage](#method-storage)
[tap](#method-tap)
[throw_if](#method-throw-if)
[throw_unless](#method-throw-unless)
[trait_uses_recursive](#method-trait-uses-recursive)
[transform](#method-transform)
[value](#method-value)
[with](#method-with)
[when](#method-when)

## Arrays & Objects

<a id="method-array-accessible"></a>
#### `Arr::accessible()`

The `Arr::accessible` method determines if the given value is array accessible:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;
use Voyager\NutsAndBolts\Collection;

$isAccessible = Arr::accessible(['a' => 1, 'b' => 2]);

// true

$isAccessible = Arr::accessible(new Collection);

// true

$isAccessible = Arr::accessible('abc');

// false

$isAccessible = Arr::accessible(new stdClass);

// false
```

<a id="method-array-add"></a>
#### `Arr::add()`

The `Arr::add` method adds a given key / value pair to an array if the given key doesn't already exist in the array or is set to `null`:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = Arr::add(['name' => 'Desk'], 'price', 100);

// ['name' => 'Desk', 'price' => 100]

$array = Arr::add(['name' => 'Desk', 'price' => null], 'price', 100);

// ['name' => 'Desk', 'price' => 100]
```

<a id="method-array-array"></a>
#### `Arr::array()`

The `Arr::array` method retrieves a value from a deeply nested array using "dot" notation (just as [Arr::get()](#method-array-get) does), but throws an `InvalidArgumentException` if the requested value is not an `array`:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Joe', 'languages' => ['PHP', 'Ruby']];

$value = Arr::array($array, 'languages');

// ['PHP', 'Ruby']

$value = Arr::array($array, 'name');

// throws InvalidArgumentException
```

<a id="method-array-boolean"></a>
#### `Arr::boolean()`

The `Arr::boolean` method retrieves a value from a deeply nested array using "dot" notation (just as [Arr::get()](#method-array-get) does), but throws an `InvalidArgumentException` if the requested value is not a `boolean`:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Joe', 'available' => true];

$value = Arr::boolean($array, 'available');

// true

$value = Arr::boolean($array, 'name');

// throws InvalidArgumentException
```


<a id="method-array-collapse"></a>
#### `Arr::collapse()`

The `Arr::collapse` method collapses an array of arrays or collections into a single array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = Arr::collapse([[1, 2, 3], [4, 5, 6], [7, 8, 9]]);

// [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

<a id="method-array-crossjoin"></a>
#### `Arr::crossJoin()`

The `Arr::crossJoin` method cross joins the given arrays, returning a Cartesian product with all possible permutations:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$matrix = Arr::crossJoin([1, 2], ['a', 'b']);

/*
    [
        [1, 'a'],
        [1, 'b'],
        [2, 'a'],
        [2, 'b'],
    ]
*/

$matrix = Arr::crossJoin([1, 2], ['a', 'b'], ['I', 'II']);

/*
    [
        [1, 'a', 'I'],
        [1, 'a', 'II'],
        [1, 'b', 'I'],
        [1, 'b', 'II'],
        [2, 'a', 'I'],
        [2, 'a', 'II'],
        [2, 'b', 'I'],
        [2, 'b', 'II'],
    ]
*/
```

<a id="method-array-divide"></a>
#### `Arr::divide()`

The `Arr::divide` method returns two arrays: one containing the keys and the other containing the values of the given array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

[$keys, $values] = Arr::divide(['name' => 'Desk']);

// $keys: ['name']

// $values: ['Desk']
```

<a id="method-array-dot"></a>
#### `Arr::dot()`

The `Arr::dot` method flattens a multi-dimensional array into a single level array that uses "dot" notation to indicate depth:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

$flattened = Arr::dot($array);

// ['products.desk.price' => 100]
```

<a id="method-array-every"></a>
#### `Arr::every()`

The `Arr::every` method ensures that all values in the array pass a given truth test:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [1, 2, 3];

Arr::every($array, fn ($i) => $i > 0);

// true

Arr::every($array, fn ($i) => $i > 2);

// false
```

<a id="method-array-except"></a>
#### `Arr::except()`

The `Arr::except` method removes the given key / value pairs from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Desk', 'price' => 100];

$filtered = Arr::except($array, ['price']);

// ['name' => 'Desk']
```

<a id="method-array-except-values"></a>
#### `Arr::exceptValues()`

The `Arr::exceptValues` method removes the specified values from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['foo', 'bar', 'baz', 'qux'];

$filtered = Arr::exceptValues($array, ['foo', 'baz']);

// ['bar', 'qux']
```

You may also pass `true` to the `strict` argument to use strict type comparisons when filtering:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [1, '1', 2, '2'];

$filtered = Arr::exceptValues($array, [1, 2], strict: true);

// ['1', '2']
```

<a id="method-array-exists"></a>
#### `Arr::exists()`

The `Arr::exists` method checks that the given key exists in the provided array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'John Doe', 'age' => 17];

$exists = Arr::exists($array, 'name');

// true

$exists = Arr::exists($array, 'salary');

// false
```

<a id="method-array-first"></a>
#### `Arr::first()`

The `Arr::first` method returns the first element of an array passing a given truth test:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [100, 200, 300];

$first = Arr::first($array, function (int $value, int $key) {
    return $value >= 150;
});

// 200
```

A default value may also be passed as the third parameter to the method. This value will be returned if no value passes the truth test:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$first = Arr::first($array, $callback, $default);
```

<a id="method-array-flatten"></a>
#### `Arr::flatten()`

The `Arr::flatten` method flattens a multi-dimensional array into a single level array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Joe', 'languages' => ['PHP', 'Ruby']];

$flattened = Arr::flatten($array);

// ['Joe', 'PHP', 'Ruby']
```

<a id="method-array-float"></a>
#### `Arr::float()`

The `Arr::float` method retrieves a value from a deeply nested array using "dot" notation (just as [Arr::get()](#method-array-get) does), but throws an `InvalidArgumentException` if the requested value is not a `float`:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Joe', 'balance' => 123.45];

$value = Arr::float($array, 'balance');

// 123.45

$value = Arr::float($array, 'name');

// throws InvalidArgumentException
```

<a id="method-array-forget"></a>
#### `Arr::forget()`

The `Arr::forget` method removes a given key / value pairs from a deeply nested array using "dot" notation:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

Arr::forget($array, 'products.desk');

// ['products' => []]
```

<a id="method-array-from"></a>
#### `Arr::from()`

The `Arr::from` method converts various input types into a plain PHP array. It supports a range of input types, including arrays, objects, and several common interfaces, such as `Voyager\Contracts\NutsAndBolts\Arrayable`, `Voyager\NutsAndBolts\Contracts\Enumerable`, `Voyager\Contracts\NutsAndBolts\Jsonable`, and `JsonSerializable`. Additionally, it handles `Traversable` and `WeakMap` instances:

```php
use Voyager\Contracts\NutsAndBolts\Jsonable;
use Voyager\NutsAndBolts\DataObjects\Arr;

Arr::from((object) ['foo' => 'bar']); // ['foo' => 'bar']

class TestJsonableObject implements Jsonable
{
    public function toJson(int $options = 0): string
    {
        return json_encode(['foo' => 'bar']);
    }
}

Arr::from(new TestJsonableObject); // ['foo' => 'bar']
```

<a id="method-array-get"></a>
#### `Arr::get()`

The `Arr::get` method retrieves a value from a deeply nested array using "dot" notation:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

$price = Arr::get($array, 'products.desk.price');

// 100
```

The `Arr::get` method also accepts a default value, which will be returned if the specified key is not present in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$discount = Arr::get($array, 'products.desk.discount', 0);

// 0
```

<a id="method-array-has"></a>
#### `Arr::has()`

The `Arr::has` method checks whether a given item or items exists in an array using "dot" notation:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['product' => ['name' => 'Desk', 'price' => 100]];

$contains = Arr::has($array, 'product.name');

// true

$contains = Arr::has($array, ['product.price', 'product.discount']);

// false
```

<a id="method-array-hasall"></a>
#### `Arr::hasAll()`

The `Arr::hasAll` method determines if all of the specified keys exist in the given array using "dot" notation:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Taylor', 'language' => 'PHP'];

Arr::hasAll($array, ['name']); // true
Arr::hasAll($array, ['name', 'language']); // true
Arr::hasAll($array, ['name', 'IDE']); // false
```

<a id="method-array-hasany"></a>
#### `Arr::hasAny()`

The `Arr::hasAny` method checks whether any item in a given set exists in an array using "dot" notation:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['product' => ['name' => 'Desk', 'price' => 100]];

$contains = Arr::hasAny($array, 'product.name');

// true

$contains = Arr::hasAny($array, ['product.name', 'product.discount']);

// true

$contains = Arr::hasAny($array, ['category', 'product.discount']);

// false
```

<a id="method-array-integer"></a>
#### `Arr::integer()`

The `Arr::integer` method retrieves a value from a deeply nested array using "dot" notation (just as [Arr::get()](#method-array-get) does), but throws an `InvalidArgumentException` if the requested value is not an `int`:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Joe', 'age' => 42];

$value = Arr::integer($array, 'age');

// 42

$value = Arr::integer($array, 'name');

// throws InvalidArgumentException
```

<a id="method-array-isassoc"></a>
#### `Arr::isAssoc()`

The `Arr::isAssoc` method returns `true` if the given array is an associative array. An array is considered "associative" if it doesn't have sequential numerical keys beginning with zero:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$isAssoc = Arr::isAssoc(['product' => ['name' => 'Desk', 'price' => 100]]);

// true

$isAssoc = Arr::isAssoc([1, 2, 3]);

// false
```

<a id="method-array-islist"></a>
#### `Arr::isList()`

The `Arr::isList` method returns `true` if the given array's keys are sequential integers beginning from zero:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$isList = Arr::isList(['foo', 'bar', 'baz']);

// true

$isList = Arr::isList(['product' => ['name' => 'Desk', 'price' => 100]]);

// false
```

<a id="method-array-join"></a>
#### `Arr::join()`

The `Arr::join` method joins array elements with a string. Using this method's third argument, you may also specify the joining string for the final element of the array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['Collections', 'Signals', 'Instrument', 'Sketches'];

$joined = Arr::join($array, ', ');

// Collections, Signals, Instrument, Sketches

$joined = Arr::join($array, ', ', ', and ');

// Collections, Signals, Instrument, and Sketches
```

<a id="method-array-keyby"></a>
#### `Arr::keyBy()`

The `Arr::keyBy` method keys the array by the given key. If multiple items have the same key, only the last one will appear in the new array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    ['product_id' => 'prod-100', 'name' => 'Desk'],
    ['product_id' => 'prod-200', 'name' => 'Chair'],
];

$keyed = Arr::keyBy($array, 'product_id');

/*
    [
        'prod-100' => ['product_id' => 'prod-100', 'name' => 'Desk'],
        'prod-200' => ['product_id' => 'prod-200', 'name' => 'Chair'],
    ]
*/
```

<a id="method-array-last"></a>
#### `Arr::last()`

The `Arr::last` method returns the last element of an array passing a given truth test:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [100, 200, 300, 110];

$last = Arr::last($array, function (int $value, int $key) {
    return $value >= 150;
});

// 300
```

A default value may be passed as the third argument to the method. This value will be returned if no value passes the truth test:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$last = Arr::last($array, $callback, $default);
```

<a id="method-array-map"></a>
#### `Arr::map()`

The `Arr::map` method iterates through the array and passes each value and key to the given callback. The array value is replaced by the value returned by the callback:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['first' => 'james', 'last' => 'kirk'];

$mapped = Arr::map($array, function (string $value, string $key) {
    return ucfirst($value);
});

// ['first' => 'James', 'last' => 'Kirk']
```

<a id="method-array-map-spread"></a>
#### `Arr::mapSpread()`

The `Arr::mapSpread` method iterates over the array, passing each nested item value into the given closure. The closure is free to modify the item and return it, thus forming a new array of modified items:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    [0, 1],
    [2, 3],
    [4, 5],
    [6, 7],
    [8, 9],
];

$mapped = Arr::mapSpread($array, function (int $even, int $odd) {
    return $even + $odd;
});

/*
    [1, 5, 9, 13, 17]
*/
```

<a id="method-array-map-with-keys"></a>
#### `Arr::mapWithKeys()`

The `Arr::mapWithKeys` method iterates through the array and passes each value to the given callback. The callback should return an associative array containing a single key / value pair:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    [
        'name' => 'John',
        'department' => 'Sales',
        'email' => 'john@example.com',
    ],
    [
        'name' => 'Jane',
        'department' => 'Marketing',
        'email' => 'jane@example.com',
    ]
];

$mapped = Arr::mapWithKeys($array, function (array $item, int $key) {
    return [$item['email'] => $item['name']];
});

/*
    [
        'john@example.com' => 'John',
        'jane@example.com' => 'Jane',
    ]
*/
```

<a id="method-array-only"></a>
#### `Arr::only()`

The `Arr::only` method returns only the specified key / value pairs from the given array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Desk', 'price' => 100, 'orders' => 10];

$slice = Arr::only($array, ['name', 'price']);

// ['name' => 'Desk', 'price' => 100]
```

<a id="method-array-only-values"></a>
#### `Arr::onlyValues()`

The `Arr::onlyValues` method returns only the specified values from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['foo', 'bar', 'baz', 'qux'];

$filtered = Arr::onlyValues($array, ['foo', 'baz']);

// ['foo', 'baz']
```

You may also pass `true` to the `strict` argument to use strict type comparisons when filtering:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [1, '1', 2, '2'];

$filtered = Arr::onlyValues($array, [1, 2], strict: true);

// [1, 2]
```

<a id="method-array-partition"></a>
#### `Arr::partition()`

The `Arr::partition` method may be combined with PHP array destructuring to separate elements that pass a given truth test from those that do not:

```php
<?php

use Voyager\NutsAndBolts\DataObjects\Arr;

$numbers = [1, 2, 3, 4, 5, 6];

[$underThree, $equalOrAboveThree] = Arr::partition($numbers, function (int $i) {
    return $i < 3;
});

dump($underThree);

// [1, 2]

dump($equalOrAboveThree);

// [3, 4, 5, 6]
```

<a id="method-array-pluck"></a>
#### `Arr::pluck()`

The `Arr::pluck` method retrieves all of the values for a given key from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    ['developer' => ['id' => 1, 'name' => 'Taylor']],
    ['developer' => ['id' => 2, 'name' => 'Abigail']],
];

$names = Arr::pluck($array, 'developer.name');

// ['Taylor', 'Abigail']
```

You may also specify how you wish the resulting list to be keyed:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$names = Arr::pluck($array, 'developer.name', 'developer.id');

// [1 => 'Taylor', 2 => 'Abigail']
```

<a id="method-array-prepend"></a>
#### `Arr::prepend()`

The `Arr::prepend` method will push an item onto the beginning of an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['one', 'two', 'three', 'four'];

$array = Arr::prepend($array, 'zero');

// ['zero', 'one', 'two', 'three', 'four']
```

If needed, you may specify the key that should be used for the value:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['price' => 100];

$array = Arr::prepend($array, 'Desk', 'name');

// ['name' => 'Desk', 'price' => 100]
```

<a id="method-array-prependkeyswith"></a>
#### `Arr::prependKeysWith()`

The `Arr::prependKeysWith` prepends all key names of an associative array with the given prefix:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    'name' => 'Desk',
    'price' => 100,
];

$keyed = Arr::prependKeysWith($array, 'product.');

/*
    [
        'product.name' => 'Desk',
        'product.price' => 100,
    ]
*/
```

<a id="method-array-pull"></a>
#### `Arr::pull()`

The `Arr::pull` method returns and removes a key / value pair from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Desk', 'price' => 100];

$name = Arr::pull($array, 'name');

// $name: Desk

// $array: ['price' => 100]
```

A default value may be passed as the third argument to the method. This value will be returned if the key doesn't exist:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$value = Arr::pull($array, $key, $default);
```

<a id="method-array-push"></a>
#### `Arr::push()`

The `Arr::push` method pushes an item into an array using "dot" notation. If an array does not exist at the given key, it will be created:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [];

Arr::push($array, 'office.furniture', 'Desk');

// $array: ['office' => ['furniture' => ['Desk']]]
```

<a id="method-array-query"></a>
#### `Arr::query()`

The `Arr::query` method converts the array into a query string:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    'name' => 'Taylor',
    'order' => [
        'column' => 'created_at',
        'direction' => 'desc'
    ]
];

Arr::query($array);

// name=Taylor&order%5Bcolumn%5D=created_at&order%5Bdirection%5D=desc
```

<a id="method-array-random"></a>
#### `Arr::random()`

The `Arr::random` method returns a random value from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [1, 2, 3, 4, 5];

$random = Arr::random($array);

// 4 - (retrieved randomly)
```

You may also specify the number of items to return as an optional second argument. Note that providing this argument will return an array even if only one item is desired:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$items = Arr::random($array, 2);

// [2, 5] - (retrieved randomly)
```

<a id="method-array-reject"></a>
#### `Arr::reject()`

The `Arr::reject` method removes items from an array using the given closure:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [100, '200', 300, '400', 500];

$filtered = Arr::reject($array, function (string|int $value, int $key) {
    return is_string($value);
});

// [0 => 100, 2 => 300, 4 => 500]
```

<a id="method-array-select"></a>
#### `Arr::select()`

The `Arr::select` method selects an array of values from an array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    ['id' => 1, 'name' => 'Desk', 'price' => 200],
    ['id' => 2, 'name' => 'Table', 'price' => 150],
    ['id' => 3, 'name' => 'Chair', 'price' => 300],
];

Arr::select($array, ['name', 'price']);

// [['name' => 'Desk', 'price' => 200], ['name' => 'Table', 'price' => 150], ['name' => 'Chair', 'price' => 300]]
```

<a id="method-array-set"></a>
#### `Arr::set()`

The `Arr::set` method sets a value within a deeply nested array using "dot" notation:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

Arr::set($array, 'products.desk.price', 200);

// ['products' => ['desk' => ['price' => 200]]]
```

<a id="method-array-shuffle"></a>
#### `Arr::shuffle()`

The `Arr::shuffle` method randomly shuffles the items in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = Arr::shuffle([1, 2, 3, 4, 5]);

// [3, 2, 5, 1, 4] - (generated randomly)
```

<a id="method-array-sole"></a>
#### `Arr::sole()`

The `Arr::sole` method retrieves a single value from an array using the given closure. If more than one value within the array matches the given truth test, an `Voyager\NutsAndBolts\Exceptions\MultipleItemsFoundException` exception will be thrown. If no values match the truth test, an `Voyager\NutsAndBolts\Exceptions\ItemNotFoundException` exception will be thrown:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['Desk', 'Table', 'Chair'];

$value = Arr::sole($array, fn (string $value) => $value === 'Desk');

// 'Desk'
```

<a id="method-array-some"></a>
#### `Arr::some()`

The `Arr::some` method ensures that at least one of the values in the array passes a given truth test:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [1, 2, 3];

Arr::some($array, fn ($i) => $i > 2);

// true
```

<a id="method-array-sort"></a>
#### `Arr::sort()`

The `Arr::sort` method sorts an array by its values:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['Desk', 'Table', 'Chair'];

$sorted = Arr::sort($array);

// ['Chair', 'Desk', 'Table']
```

You may also sort the array by the results of a given closure:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    ['name' => 'Desk'],
    ['name' => 'Table'],
    ['name' => 'Chair'],
];

$sorted = array_values(Arr::sort($array, function (array $value) {
    return $value['name'];
}));

/*
    [
        ['name' => 'Chair'],
        ['name' => 'Desk'],
        ['name' => 'Table'],
    ]
*/
```

<a id="method-array-sort-desc"></a>
#### `Arr::sortDesc()`

The `Arr::sortDesc` method sorts an array in descending order by its values:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['Desk', 'Table', 'Chair'];

$sorted = Arr::sortDesc($array);

// ['Table', 'Desk', 'Chair']
```

You may also sort the array by the results of a given closure:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    ['name' => 'Desk'],
    ['name' => 'Table'],
    ['name' => 'Chair'],
];

$sorted = array_values(Arr::sortDesc($array, function (array $value) {
    return $value['name'];
}));

/*
    [
        ['name' => 'Table'],
        ['name' => 'Desk'],
        ['name' => 'Chair'],
    ]
*/
```

<a id="method-array-sort-recursive"></a>
#### `Arr::sortRecursive()`

The `Arr::sortRecursive` method recursively sorts an array using the `sort` function for numerically indexed sub-arrays and the `ksort` function for associative sub-arrays:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    ['Roman', 'Taylor', 'Li'],
    ['PHP', 'Ruby', 'JavaScript'],
    ['one' => 1, 'two' => 2, 'three' => 3],
];

$sorted = Arr::sortRecursive($array);

/*
    [
        ['JavaScript', 'PHP', 'Ruby'],
        ['one' => 1, 'three' => 3, 'two' => 2],
        ['Li', 'Roman', 'Taylor'],
    ]
*/
```

If you would like the results sorted in descending order, you may use the `Arr::sortRecursiveDesc` method.

```php
$sorted = Arr::sortRecursiveDesc($array);
```

<a id="method-array-string"></a>
#### `Arr::string()`

The `Arr::string` method retrieves a value from a deeply nested array using "dot" notation (just as [Arr::get()](#method-array-get) does), but throws an `InvalidArgumentException` if the requested value is not a `string`:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = ['name' => 'Joe', 'languages' => ['PHP', 'Ruby']];

$value = Arr::string($array, 'name');

// Joe

$value = Arr::string($array, 'languages');

// throws InvalidArgumentException
```

<a id="method-array-take"></a>
#### `Arr::take()`

The `Arr::take` method returns a new array with the specified number of items:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [0, 1, 2, 3, 4, 5];

$chunk = Arr::take($array, 3);

// [0, 1, 2]
```

You may also pass a negative integer to take the specified number of items from the end of the array:

```php
$array = [0, 1, 2, 3, 4, 5];

$chunk = Arr::take($array, -2);

// [4, 5]
```

<a id="method-array-to-css-classes"></a>
#### `Arr::toCssClasses()`

The `Arr::toCssClasses` method conditionally compiles a CSS class string. The method accepts an array of classes where the array key contains the class or classes you wish to add, while the value is a boolean expression. If the array element has a numeric key, it will always be included in the rendered class list:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$isActive = false;
$hasError = true;

$array = ['p-4', 'font-bold' => $isActive, 'bg-red' => $hasError];

$classes = Arr::toCssClasses($array);

/*
    'p-4 bg-red'
*/
```

<a id="method-array-to-css-styles"></a>
#### `Arr::toCssStyles()`

The `Arr::toCssStyles` method conditionally compiles a CSS style string. The method accepts an array of CSS declarations where the array key contains the CSS declaration you wish to add, while the value is a boolean expression. If the array element has a numeric key, it will always be included in the compiled CSS style string:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$hasColor = true;

$array = ['background-color: blue', 'color: blue' => $hasColor];

$classes = Arr::toCssStyles($array);

/*
    'background-color: blue; color: blue;'
*/
```

<a id="method-array-undot"></a>
#### `Arr::undot()`

The `Arr::undot` method expands a single-dimensional array that uses "dot" notation into a multi-dimensional array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [
    'user.name' => 'Kevin Malone',
    'user.occupation' => 'Accountant',
];

$array = Arr::undot($array);

// ['user' => ['name' => 'Kevin Malone', 'occupation' => 'Accountant']]
```

<a id="method-array-where"></a>
#### `Arr::where()`

The `Arr::where` method filters an array using the given closure:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [100, '200', 300, '400', 500];

$filtered = Arr::where($array, function (string|int $value, int $key) {
    return is_string($value);
});

// [1 => '200', 3 => '400']
```

<a id="method-array-where-not-null"></a>
#### `Arr::whereNotNull()`

The `Arr::whereNotNull` method removes all `null` values from the given array:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = [0, null];

$filtered = Arr::whereNotNull($array);

// [0 => 0]
```

<a id="method-array-wrap"></a>
#### `Arr::wrap()`

The `Arr::wrap` method wraps the given value in an array. If the given value is already an array it will be returned without modification:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$string = 'Venusian';

$array = Arr::wrap($string);

// ['Venusian']
```

If the given value is `null`, an empty array will be returned:

```php
use Voyager\NutsAndBolts\DataObjects\Arr;

$array = Arr::wrap(null);

// []
```

<a id="method-data-fill"></a>
#### `data_fill()`

The `data_fill` function sets a missing value within a nested array or object using "dot" notation:

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_fill($data, 'products.desk.price', 200);

// ['products' => ['desk' => ['price' => 100]]]

data_fill($data, 'products.desk.discount', 10);

// ['products' => ['desk' => ['price' => 100, 'discount' => 10]]]
```

This function also accepts asterisks as wildcards and will fill the target accordingly:

```php
$data = [
    'products' => [
        ['name' => 'Desk 1', 'price' => 100],
        ['name' => 'Desk 2'],
    ],
];

data_fill($data, 'products.*.price', 200);

/*
    [
        'products' => [
            ['name' => 'Desk 1', 'price' => 100],
            ['name' => 'Desk 2', 'price' => 200],
        ],
    ]
*/
```

<a id="method-data-get"></a>
#### `data_get()`

The `data_get` function retrieves a value from a nested array or object using "dot" notation:

```php
$data = ['products' => ['desk' => ['price' => 100]]];

$price = data_get($data, 'products.desk.price');

// 100
```

The `data_get` function also accepts a default value, which will be returned if the specified key is not found:

```php
$discount = data_get($data, 'products.desk.discount', 0);

// 0
```

The function also accepts wildcards using asterisks, which may target any key of the array or object:

```php
$data = [
    'product-one' => ['name' => 'Desk 1', 'price' => 100],
    'product-two' => ['name' => 'Desk 2', 'price' => 150],
];

data_get($data, '*.name');

// ['Desk 1', 'Desk 2'];
```

The `{first}` and `{last}` placeholders may be used to retrieve the first or last items in an array:

```php
$flight = [
    'segments' => [
        ['from' => 'LHR', 'departure' => '9:00', 'to' => 'IST', 'arrival' => '15:00'],
        ['from' => 'IST', 'departure' => '16:00', 'to' => 'PKX', 'arrival' => '20:00'],
    ],
];

data_get($flight, 'segments.{first}.arrival');

// 15:00
```

<a id="method-data-set"></a>
#### `data_set()`

The `data_set` function sets a value within a nested array or object using "dot" notation:

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_set($data, 'products.desk.price', 200);

// ['products' => ['desk' => ['price' => 200]]]
```

This function also accepts wildcards using asterisks and will set values on the target accordingly:

```php
$data = [
    'products' => [
        ['name' => 'Desk 1', 'price' => 100],
        ['name' => 'Desk 2', 'price' => 150],
    ],
];

data_set($data, 'products.*.price', 200);

/*
    [
        'products' => [
            ['name' => 'Desk 1', 'price' => 200],
            ['name' => 'Desk 2', 'price' => 200],
        ],
    ]
*/
```

By default, any existing values are overwritten. If you wish to only set a value if it doesn't exist, you may pass `false` as the fourth argument to the function:

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_set($data, 'products.desk.price', 200, overwrite: false);

// ['products' => ['desk' => ['price' => 100]]]
```

<a id="method-data-forget"></a>
#### `data_forget()`

The `data_forget` function removes a value within a nested array or object using "dot" notation:

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_forget($data, 'products.desk.price');

// ['products' => ['desk' => []]]
```

This function also accepts wildcards using asterisks and will remove values on the target accordingly:

```php
$data = [
    'products' => [
        ['name' => 'Desk 1', 'price' => 100],
        ['name' => 'Desk 2', 'price' => 150],
    ],
];

data_forget($data, 'products.*.price');

/*
    [
        'products' => [
            ['name' => 'Desk 1'],
            ['name' => 'Desk 2'],
        ],
    ]
*/
```

<a id="method-head"></a>
#### `head()`

The `head` function returns the first element in the given array. If the array is empty, `false` will be returned:

```php
$array = [100, 200, 300];

$first = head($array);

// 100
```

<a id="method-last"></a>
#### `last()`

The `last` function returns the last element in the given array. If the array is empty, `false` will be returned:

```php
$array = [100, 200, 300];

$last = last($array);

// 300
```

## Numbers

<a id="method-number-abbreviate"></a>
#### `Number::abbreviate()`

The `Number::abbreviate` method returns the human-readable format of the provided numerical value, with an abbreviation for the units:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::abbreviate(1000);

// 1K

$number = Number::abbreviate(489939);

// 490K

$number = Number::abbreviate(1230000, precision: 2);

// 1.23M
```

<a id="method-number-clamp"></a>
#### `Number::clamp()`

The `Number::clamp` method ensures a given number stays within a specified range. If the number is lower than the minimum, the minimum value is returned. If the number is higher than the maximum, the maximum value is returned:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::clamp(105, min: 10, max: 100);

// 100

$number = Number::clamp(5, min: 10, max: 100);

// 10

$number = Number::clamp(10, min: 10, max: 100);

// 10

$number = Number::clamp(20, min: 10, max: 100);

// 20
```

<a id="method-number-currency"></a>
#### `Number::currency()`

The `Number::currency` method returns the currency representation of the given value as a string:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$currency = Number::currency(1000);

// $1,000.00

$currency = Number::currency(1000, in: 'EUR');

// €1,000.00

$currency = Number::currency(1000, in: 'EUR', locale: 'de');

// 1.000,00 €

$currency = Number::currency(1000, in: 'EUR', locale: 'de', precision: 0);

// 1.000 €
```

<a id="method-default-currency"></a>
#### `Number::defaultCurrency()`

The `Number::defaultCurrency` method returns the default currency being used by the `Number` class:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$currency = Number::defaultCurrency();

// USD
```

<a id="method-default-locale"></a>
#### `Number::defaultLocale()`

The `Number::defaultLocale` method returns the default locale being used by the `Number` class:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$locale = Number::defaultLocale();

// en
```

<a id="method-number-file-size"></a>
#### `Number::fileSize()`

The `Number::fileSize` method returns the file size representation of the given byte value as a string:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$size = Number::fileSize(1024);

// 1 KB

$size = Number::fileSize(1024 * 1024);

// 1 MB

$size = Number::fileSize(1024, precision: 2);

// 1.00 KB
```

<a id="method-number-for-humans"></a>
#### `Number::forHumans()`

The `Number::forHumans` method returns the human-readable format of the provided numerical value:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::forHumans(1000);

// 1 thousand

$number = Number::forHumans(489939);

// 490 thousand

$number = Number::forHumans(1230000, precision: 2);

// 1.23 million
```

<a id="method-number-format"></a>
#### `Number::format()`

The `Number::format` method formats the given number into a locale specific string:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::format(100000);

// 100,000

$number = Number::format(100000, precision: 2);

// 100,000.00

$number = Number::format(100000.123, maxPrecision: 2);

// 100,000.12

$number = Number::format(100000, locale: 'de');

// 100.000
```

<a id="method-number-ordinal"></a>
#### `Number::ordinal()`

The `Number::ordinal` method returns a number's ordinal representation:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::ordinal(1);

// 1st

$number = Number::ordinal(2);

// 2nd

$number = Number::ordinal(21);

// 21st
```

<a id="method-number-pairs"></a>
#### `Number::pairs()`

The `Number::pairs` method generates an array of number pairs (sub-ranges) based on a specified range and step value. This method can be useful for dividing a larger range of numbers into smaller, manageable sub-ranges for things like pagination or batching tasks. The `pairs` method returns an array of arrays, where each inner array represents a pair (sub-range) of numbers:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$result = Number::pairs(25, 10);

// [[0, 9], [10, 19], [20, 25]]

$result = Number::pairs(25, 10, offset: 0);

// [[0, 10], [10, 20], [20, 25]]
```

<a id="method-number-parse"></a>
#### `Number::parse()`

The `Number::parse` method parses a localized numeric string using PHP's `NumberFormatter`:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$result = Number::parse('10,123', locale: 'en');

// 10123.0

$result = Number::parse('10,123', locale: 'fr');

// 10.123
```

<a id="method-number-parse-int"></a>
#### `Number::parseInt()`

The `Number::parseInt` method parse a string into an integer according to the specified locale:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$result = Number::parseInt('10.123');

// (int) 10

$result = Number::parseInt('10,123', locale: 'fr');

// (int) 10
```

<a id="method-number-parse-float"></a>
#### `Number::parseFloat()`

The `Number::parseFloat` method parse a string into a float according to the specified locale:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$result = Number::parseFloat('10');

// (float) 10.0

$result = Number::parseFloat('10', locale: 'fr');

// (float) 10.0
```

<a id="method-number-percentage"></a>
#### `Number::percentage()`

The `Number::percentage` method returns the percentage representation of the given value as a string:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$percentage = Number::percentage(10);

// 10%

$percentage = Number::percentage(10, precision: 2);

// 10.00%

$percentage = Number::percentage(10.123, maxPrecision: 2);

// 10.12%

$percentage = Number::percentage(10, precision: 2, locale: 'de');

// 10,00%
```

<a id="method-number-spell"></a>
#### `Number::spell()`

The `Number::spell` method transforms the given number into a string of words:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::spell(102);

// one hundred and two

$number = Number::spell(88, locale: 'fr');

// quatre-vingt-huit
```

The `after` argument allows you to specify a value after which all numbers should be spelled out:

```php
$number = Number::spell(10, after: 10);

// 10

$number = Number::spell(11, after: 10);

// eleven
```

The `until` argument allows you to specify a value before which all numbers should be spelled out:

```php
$number = Number::spell(5, until: 10);

// five

$number = Number::spell(10, until: 10);

// 10
```

<a id="method-number-spell-ordinal"></a>
#### `Number::spellOrdinal()`

The `Number::spellOrdinal` method returns the number's ordinal representation as a string of words:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::spellOrdinal(1);

// first

$number = Number::spellOrdinal(2);

// second

$number = Number::spellOrdinal(21);

// twenty-first
```

<a id="method-number-trim"></a>
#### `Number::trim()`

The `Number::trim` method removes any trailing zero digits after the decimal point of the given number:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::trim(12.0);

// 12

$number = Number::trim(12.30);

// 12.3
```

<a id="method-number-use-locale"></a>
#### `Number::useLocale()`

The `Number::useLocale` method sets the default number locale globally, which affects how numbers and currency are formatted by subsequent invocations to the `Number` class's methods:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Number::useLocale('de');
}
```

<a id="method-number-with-locale"></a>
#### `Number::withLocale()`

The `Number::withLocale` method executes the given closure using the specified locale and then restores the original locale after the callback has executed:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::withLocale('de', function () {
    return Number::format(1500);
});
```

<a id="method-number-use-currency"></a>
#### `Number::useCurrency()`

The `Number::useCurrency` method sets the default number currency globally, which affects how the currency is formatted by subsequent invocations to the `Number` class's methods:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Number::useCurrency('GBP');
}
```

<a id="method-number-with-currency"></a>
#### `Number::withCurrency()`

The `Number::withCurrency` method executes the given closure using the specified currency and then restores the original currency after the callback has executed:

```php
use Voyager\NutsAndBolts\DataObjects\Number;

$number = Number::withCurrency('GBP', function () {
    // ...
});
```

## Paths

<a id="method-app-path"></a>
#### `app_path()`

The `app_path` function returns the fully qualified path to your application's `app` directory. You may also use the `app_path` function to generate a fully qualified path to a file relative to the application directory:

```php
$path = app_path();

$path = app_path('Providers/AppServiceProvider.php');
```

<a id="method-base-path"></a>
#### `base_path()`

The `base_path` function returns the fully qualified path to your application's root directory. You may also use the `base_path` function to generate a fully qualified path to a given file relative to the project root directory:

```php
$path = base_path();

$path = base_path('vendor/bin');
```

<a id="method-config-path"></a>
#### `config_path()`

The `config_path` function returns the fully qualified path to your application's `config` directory. You may also use the `config_path` function to generate a fully qualified path to a given file within the application's configuration directory:

```php
$path = config_path();

$path = config_path('app.php');
```

<a id="method-database-path"></a>
#### `database_path()`

The `database_path` function returns the fully qualified path to your application's `database` directory. You may also use the `database_path` function to generate a fully qualified path to a given file within the database directory:

```php
$path = database_path();

$path = database_path('factories/UserFactory.php');
```

<a id="method-storage-path"></a>
#### `storage_path()`

The `storage_path` function returns the fully qualified path to your application's `storage` directory. You may also use the `storage_path` function to generate a fully qualified path to a given file within the storage directory:

```php
$path = storage_path();

$path = storage_path('app/file.txt');
```

## Miscellaneous

<a id="method-app"></a>
#### `app()`

The `app` function returns the [service container](/docs/{{version}}/framework/architecture-concepts/container) instance:

```php
$container = app();
```

You may pass a class or interface name to resolve it from the container:

```php
$api = app('HelpSpot\API');
```

<a id="method-blank"></a>
#### `blank()`

The `blank` function determines whether the given value is "blank":

```php
blank('');
blank('   ');
blank(null);
blank(collect());

// true

blank(0);
blank(true);
blank(false);

// false
```

For the inverse of `blank`, see the [filled](#method-filled) function.

<a id="method-broadcast"></a>
#### `broadcast()`

The `broadcast` function [broadcasts](/docs/{{version}}/framework/digging-deeper/broadcasting) the given [signal](/docs/{{version}}/framework/digging-deeper/signals) to its listeners. `toOthers` takes the socket ID to leave out:

```php
broadcast(new UserRegistered($user));

broadcast(new UserRegistered($user))->toOthers($socketId);
```

<a id="method-broadcast-if"></a>
#### `broadcast_if()`

The `broadcast_if` function [broadcasts](/docs/{{version}}/framework/digging-deeper/broadcasting) the given [signal](/docs/{{version}}/framework/digging-deeper/signals) to its listeners if a given boolean expression evaluates to `true`:

```php
broadcast_if($user->isActive(), new UserRegistered($user));

broadcast_if($user->isActive(), new UserRegistered($user))->toOthers($socketId);
```

<a id="method-class-uses-recursive"></a>
#### `class_uses_recursive()`

The `class_uses_recursive` function returns all traits used by a class, including traits used by all of its parent classes:

```php
$traits = class_uses_recursive(App\Models\User::class);
```

<a id="method-collect"></a>
#### `collect()`

The `collect` function creates a [collection](/docs/{{version}}/framework/digging-deeper/collections) instance from the given value:

```php
$collection = collect(['Taylor', 'Abigail']);
```

<a id="method-computer-binary"></a>
#### `computer_binary()`

The `Voyager\NutsAndBolts\computer_binary` function returns the name of the Computer executable: the `COMPUTER_BINARY` constant when your application defines one, otherwise `computer`. It is useful when building a command line that runs another Computer command:

```php
use function Voyager\NutsAndBolts\computer_binary;
use function Voyager\NutsAndBolts\php_binary;

$command = [php_binary(), computer_binary(), 'queue:work'];
```

<a id="method-config"></a>
#### `config()`

The `config` function gets the value of a configuration variable. The configuration values may be accessed using "dot" syntax, which includes the name of the file and the option you wish to access. You may also provide a default value that will be returned if the configuration option does not exist:

```php
$value = config('app.timezone');

$value = config('app.timezone', $default);
```

You may set configuration variables at runtime by passing an array of key / value pairs. However, note that this function only affects the configuration value for the running process and does not update your actual configuration files:

```php
config(['app.debug' => true]);
```

<a id="method-cypher"></a>
#### `cypher()`

The `cypher` function runs a Cypher query on a Neo4j connection and returns its records as an array of associative arrays. It uses the default database connection when that is a Neo4j connection, and the `neo4j` connection otherwise; pass a connection name as the third argument to choose one. The Graph component's `Voyager\Graph\GraphServiceProvider` must be registered:

```php
$people = cypher('MATCH (p:Person) WHERE p.age > $age RETURN p.name AS name', ['age' => 30]);

$people = cypher('MATCH (p:Person) RETURN p', [], 'neo4j');
```

<a id="method-cypher-one"></a>
#### `cypher_one()`

The `cypher_one` function runs a Cypher query and returns its first record:

```php
$person = cypher_one('MATCH (p:Person {name: $name}) RETURN p.name AS name', ['name' => 'Ada']);
```

<a id="method-cypher-run"></a>
#### `cypher_run()`

The `cypher_run` function runs a Cypher write statement and returns whether it succeeded:

```php
cypher_run('CREATE (p:Person {name: $name})', ['name' => 'Ada']);
```

<a id="method-dd"></a>
#### `dd()`

The `dd` function dumps the given variables and ends the execution of the script:

```php
dd($value);

dd($value1, $value2, $value3, ...);
```

If you do not want to halt the execution of your script, use the [dump](#method-dump) function instead.

<a id="method-device-os-family"></a>
#### `device_os_family()`

The `device_os_family` function returns `mac` when PHP is running on macOS and `linux` otherwise:

```php
if (device_os_family() === 'mac') {
    // ...
}
```

<a id="method-dispatch"></a>
#### `dispatch()`

The `dispatch` function pushes the given job onto the Venusian [job queue](/docs/{{version}}/framework/digging-deeper/queues):

```php
dispatch(new App\Jobs\SendEmails);
```

<a id="method-dump"></a>
#### `dump()`

The `dump` function dumps the given variables:

```php
dump($value);

dump($value1, $value2, $value3, ...);
```

If you want to stop executing the script after dumping the variables, use the [dd](#method-dd) function instead.

<a id="method-env"></a>
#### `env()`

The `env` function retrieves the value of an environment variable or returns a default value:

```php
$env = env('APP_ENV');

$env = env('APP_ENV', 'production');
```

> [!WARNING]
> If you execute the `php computer config:cache` command during your deployment process, you should be sure that you are only calling the `env` function from within your configuration files. Once the configuration has been cached, the `.env` file will not be loaded and all calls to the `env` function will return external environment variables such as server-level or system-level environment variables or `null`.

<a id="method-filled"></a>
#### `filled()`

The `filled` function determines whether the given value is not "blank":

```php
filled(0);
filled(true);
filled(false);

// true

filled('');
filled('   ');
filled(null);
filled(collect());

// false
```

For the inverse of `filled`, see the [blank](#method-blank) function.

<a id="method-literal"></a>
#### `literal()`

The `literal` function creates a new [stdClass](https://www.php.net/manual/en/class.stdclass.php) instance with the given named arguments as properties:

```php
$obj = literal(
    name: 'Joe',
    languages: ['PHP', 'Ruby'],
);

$obj->name; // 'Joe'
$obj->languages; // ['PHP', 'Ruby']
```

<a id="method-neo4j-connection"></a>
#### `neo4j_connection()`

The `neo4j_connection` function resolves a `Voyager\Graph\Database\Neo4jConnection` from the database manager. Given no name, it uses the default database connection when that is a Neo4j connection, and the `neo4j` connection otherwise. It throws a `RuntimeException` when neither is a Neo4j connection:

```php
$connection = neo4j_connection();

$connection = neo4j_connection('graph');
```

<a id="method-now"></a>
#### `now()`

The `now` function creates a new `Voyager\NutsAndBolts\DataObjects\Carbon` instance for the current time:

```php
$now = now();
```

<a id="method-once"></a>
#### `once()`

The `once` function executes the given callback and caches the result in memory for the life of the process. Any subsequent calls to the `once` function with the same callback will return the previously cached result:

```php
function random(): int
{
    return once(function () {
        return random_int(1, 1000);
    });
}

random(); // 123
random(); // 123 (cached result)
random(); // 123 (cached result)
```

When the `once` function is executed from within an object instance, the cached result will be unique to that object instance:

```php
<?php

class NumberService
{
    public function all(): array
    {
        return once(fn () => [1, 2, 3]);
    }
}

$service = new NumberService;

$service->all();
$service->all(); // (cached result)

$secondService = new NumberService;

$secondService->all();
$secondService->all(); // (cached result)
```
<a id="method-optional"></a>
#### `optional()`

The `optional` function accepts any argument and allows you to access properties or call methods on that object. If the given object is `null`, properties and methods will return `null` instead of causing an error:

```php
return optional($user->address)->street;
```

The `optional` function also accepts a closure as its second argument. The closure will be invoked if the value provided as the first argument is not null:

```php
return optional(User::find($id), function (User $user) {
    return $user->name;
});
```

<a id="method-php-binary"></a>
#### `php_binary()`

The `Voyager\NutsAndBolts\php_binary` function returns the path to the PHP executable running your application, as found by Symfony's `PhpExecutableFinder`, falling back to `php`:

```php
use function Voyager\NutsAndBolts\php_binary;

$php = php_binary();
```

<a id="method-report"></a>
#### `report()`

The `report` function will report an exception using your exception handler (`Voyager\Contracts\Debug\ExceptionHandler`):

```php
report($e);
```

The `report` function also accepts a string as an argument. When a string is given to the function, the function will create an exception with the given string as its message:

```php
report('Something went wrong.');
```

<a id="method-rescue"></a>
#### `rescue()`

The `rescue` function executes the given closure and catches any exceptions that occur during its execution. All exceptions that are caught will be sent to your exception handler; however, your code will continue running:

```php
return rescue(function () {
    return $this->method();
});
```

You may also pass a second argument to the `rescue` function. This argument will be the "default" value that should be returned if an exception occurs while executing the closure:

```php
return rescue(function () {
    return $this->method();
}, false);

return rescue(function () {
    return $this->method();
}, function () {
    return $this->failure();
});
```

A `report` argument may be provided to the `rescue` function to determine if the exception should be reported via the `report` function:

```php
return rescue(function () {
    return $this->method();
}, report: function (Throwable $throwable) {
    return $throwable instanceof InvalidArgumentException;
});
```

<a id="method-retry"></a>
#### `retry()`

The `retry` function attempts to execute the given callback until the given maximum attempt threshold is met. If the callback does not throw an exception, its return value will be returned. If the callback throws an exception, it will automatically be retried. If the maximum attempt count is exceeded, the exception will be thrown:

```php
return retry(5, function () {
    // Attempt 5 times while resting 100ms between attempts...
}, 100);
```

The sleep duration also accepts a `CarbonInterval` instance:

```php
return retry(5, function () {
    // Attempt 5 times while resting 5 seconds between attempts...
}, seconds(5));
```

If you would like to manually calculate the number of milliseconds to sleep between attempts, you may pass a closure as the third argument to the `retry` function:

```php
use Exception;

return retry(5, function () {
    // ...
}, function (int $attempt, Exception $exception) {
    return $attempt * 100;
});
```

For convenience, you may provide an array as the first argument to the `retry` function. This array will be used to determine how many milliseconds to sleep between subsequent attempts:

```php
return retry([100, 200], function () {
    // Sleep for 100ms on first retry, 200ms on second retry...
});
```

To only retry under specific conditions, you may pass a closure as the fourth argument to the `retry` function:

```php
use App\Exceptions\TemporaryException;
use Exception;

return retry(5, function () {
    // ...
}, 100, function (Exception $exception) {
    return $exception instanceof TemporaryException;
});
```

<a id="method-rocket-binary"></a>
#### `rocket_binary()`

The `Voyager\NutsAndBolts\rocket_binary` function returns the name of the Rocket executable: the `ROCKET_BINARY` constant when your application defines one, otherwise `rocket`:

```php
use function Voyager\NutsAndBolts\rocket_binary;

$rocket = rocket_binary();
```

<a id="method-signal"></a>
#### `signal()`

The `signal` function dispatches the given [signal](/docs/{{version}}/framework/digging-deeper/signals) to its listeners through `app('signals')`. Pass a signal object, or a signal name with its payload. It returns every listener's answer, in order; when its third argument is `true`, it returns the first non-null answer instead:

```php
signal(new OrderShipped($order));

signal('orders.shipped', [$order]);

$answer = signal('orders.shipped', [$order], halt: true);
```

<a id="method-storage"></a>
#### `storage()`

The `storage` function returns the `Voyager\Filesystem\Storage` instance, your application's entry point to its [filesystem](/docs/{{version}}/framework/digging-deeper/filesystem) disks. Calls it does not define are passed to the default disk:

```php
storage()->disk('local')->put('example.txt', 'Contents');

$contents = storage()->get('example.txt');
```

<a id="method-tap"></a>
#### `tap()`

The `tap` function accepts two arguments: an arbitrary `$value` and a closure. The `$value` will be passed to the closure and then be returned by the `tap` function. The return value of the closure is irrelevant:

```php
$user = tap(User::first(), function (User $user) {
    $user->name = 'Taylor';

    $user->save();
});
```

If no closure is passed to the `tap` function, you may call any method on the given `$value`. The return value of the method you call will always be `$value`, regardless of what the method actually returns in its definition. For example, the Instrument `update` method typically returns an integer. However, we can force the method to return the model itself by chaining the `update` method call through the `tap` function:

```php
$user = tap($user)->update([
    'name' => $name,
    'email' => $email,
]);
```

To add a `tap` method to a class, you may add the `Voyager\NutsAndBolts\Concerns\Tappable` trait to the class. The `tap` method of this trait accepts a Closure as its only argument. The object instance itself will be passed to the Closure and then be returned by the `tap` method:

```php
return $user->tap(function (User $user) {
    // ...
});
```

<a id="method-throw-if"></a>
#### `throw_if()`

The `throw_if` function throws the given exception if a given boolean expression evaluates to `true`:

```php
throw_if(! $user->isAdmin(), RuntimeException::class);

throw_if(
    ! $user->isAdmin(),
    RuntimeException::class,
    'Only administrators may run this command.'
);
```

<a id="method-throw-unless"></a>
#### `throw_unless()`

The `throw_unless` function throws the given exception if a given boolean expression evaluates to `false`:

```php
throw_unless($user->isAdmin(), RuntimeException::class);

throw_unless(
    $user->isAdmin(),
    RuntimeException::class,
    'Only administrators may run this command.'
);
```

<a id="method-trait-uses-recursive"></a>
#### `trait_uses_recursive()`

The `trait_uses_recursive` function returns all traits used by a trait:

```php
$traits = trait_uses_recursive(\Voyager\Database\Instrument\Concerns\HasVersion4Uuids::class);
```

<a id="method-transform"></a>
#### `transform()`

The `transform` function executes a closure on a given value if the value is not [blank](#method-blank) and then returns the return value of the closure:

```php
$callback = function (int $value) {
    return $value * 2;
};

$result = transform(5, $callback);

// 10
```

A default value or closure may be passed as the third argument to the function. This value will be returned if the given value is blank:

```php
$result = transform(null, $callback, 'The value is blank');

// The value is blank
```

<a id="method-value"></a>
#### `value()`

The `value` function returns the value it is given. However, if you pass a closure to the function, the closure will be executed and its returned value will be returned:

```php
$result = value(true);

// true

$result = value(function () {
    return false;
});

// false
```

Additional arguments may be passed to the `value` function. If the first argument is a closure then the additional parameters will be passed to the closure as arguments, otherwise they will be ignored:

```php
$result = value(function (string $name) {
    return $name;
}, 'Taylor');

// 'Taylor'
```

<a id="method-with"></a>
#### `with()`

The `with` function returns the value it is given. If a closure is passed as the second argument to the function, the closure will be executed and its returned value will be returned:

```php
$callback = function (mixed $value) {
    return is_numeric($value) ? $value * 2 : 0;
};

$result = with(5, $callback);

// 10

$result = with(null, $callback);

// 0

$result = with(5, null);

// 5
```

<a id="method-when"></a>
#### `when()`

The `when` function returns the value it is given if a given condition evaluates to `true`. Otherwise, `null` is returned. If a closure is passed as the second argument to the function, the closure will be executed and its returned value will be returned:

```php
$value = when(true, 'Hello World');

$value = when(true, fn () => 'Hello World');
```

## Other Utilities

### Dates and Time

Venusian includes [Carbon](https://carbon.nesbot.com/guide/getting-started/introduction.html), a powerful date and time manipulation library. To create a new `Carbon` instance, you may invoke the `now` function. This function is globally available within your Venusian application:

```php
$now = now();
```

Or, you may create a new `Carbon` instance using the `Voyager\NutsAndBolts\DataObjects\Carbon` class:

```php
use Voyager\NutsAndBolts\DataObjects\Carbon;

$now = Carbon::now();
```

Venusian also augments `Carbon` instances with `plus` and `minus` methods, allowing easy manipulation of the instance's date and time:

```php
return now()->plus(minutes: 5);
return now()->plus(hours: 8);
return now()->plus(weeks: 4);

return now()->minus(minutes: 5);
return now()->minus(hours: 8);
return now()->minus(weeks: 4);
```

For a thorough discussion of Carbon and its features, please consult the [official Carbon documentation](https://carbon.nesbot.com/guide/getting-started/introduction.html).

#### Interval Functions

Venusian also offers global `microseconds`, `milliseconds`, `seconds`, `minutes`, `hours`, `days`, `weeks`, `months`, and `years` functions that return `CarbonInterval` instances, which extend PHP's [DateInterval](https://www.php.net/manual/en/class.dateinterval.php) class. These functions may be used anywhere that Venusian accepts a `DateInterval` instance:

```php
app('cache')->put('metrics', $metrics, minutes(10));
```

<a id="deferred-functions"></a>
### Deferred Functions

While Venusian's [queued jobs](/docs/{{version}}/framework/digging-deeper/queues) allow you to queue tasks for background processing, sometimes you may have simple tasks you would like to defer without configuring or maintaining a long-running queue worker.

Deferred functions allow you to defer the execution of a closure until the Computer command or queued job that is running finishes. To defer the execution of a closure, pass the closure to the `Voyager\NutsAndBolts\defer` function. The function is namespaced, so import it with `use function`:

```php
use App\Services\Metrics;

use function Voyager\NutsAndBolts\defer;

defer(fn () => Metrics::reportOrder($order));
```

By default, deferred functions will only be executed if the Computer command exits with code `0`, or the queued job from which `Voyager\NutsAndBolts\defer` is invoked completes successfully. Jobs on the `sync` and `deferred` queue connections leave their deferred functions to the command or job that dispatched them. If you would like a deferred function to always execute, you may chain the `always` method onto your deferred function:

```php
defer(fn () => Metrics::reportOrder($order))->always();
```

#### Cancelling Deferred Functions

If you need to cancel a deferred function before it is executed, you can use the `forget` method to cancel the function by its name. To name a deferred function, provide a second argument to the `Voyager\NutsAndBolts\defer` function:

```php
defer(fn () => Metrics::report(), 'reportMetrics');

defer()->forget('reportMetrics');
```

### Lottery

Venusian's lottery class may be used to execute callbacks based on a set of given odds. This can be particularly useful when you only want to execute code for a percentage of the times it runs:

```php
use Voyager\NutsAndBolts\Lottery;

Lottery::odds(1, 20)
    ->winner(fn () => $user->won())
    ->loser(fn () => $user->lost())
    ->choose();
```

You may combine Venusian's lottery class with other Venusian features. For example, you may wish to only report a small percentage of slow queries to your exception handler. And, since the lottery class is callable, we may pass an instance of the class into any method that accepts callables:

```php
use Carbon\CarbonInterval;
use Voyager\NutsAndBolts\Lottery;

app('db')->whenQueryingForLongerThan(
    CarbonInterval::seconds(2),
    Lottery::odds(1, 100)->winner(fn () => report('Querying > 2 seconds.')),
);
```

#### Testing Lotteries

Venusian provides some simple methods to allow you to easily test your application's lottery invocations:

```php
// Lottery will always win...
Lottery::alwaysWin();

// Lottery will always lose...
Lottery::alwaysLose();

// Lottery will win then lose, and finally return to normal behavior...
Lottery::fix([true, false]);

// Lottery will return to normal behavior...
Lottery::determineResultsNormally();
```

### Pipeline

Venusian's pipeline, resolved from the container as `pipeline`, provides a convenient way to "pipe" a given input through a series of invokable classes, closures, or callables, giving each class the opportunity to inspect or modify the input and invoke the next callable in the pipeline:

```php
use Closure;
use App\Models\User;

$user = app('pipeline')
    ->send($user)
    ->through([
        function (User $user, Closure $next) {
            // ...

            return $next($user);
        },
        function (User $user, Closure $next) {
            // ...

            return $next($user);
        },
    ])
    ->then(fn (User $user) => $user);
```

As you can see, each invokable class or closure in the pipeline is provided the input and a `$next` closure. Invoking the `$next` closure will invoke the next callable in the pipeline.

When the last callable in the pipeline invokes the `$next` closure, the callable provided to the `then` method will be invoked. Typically, this callable will simply return the given input. For convenience, if you simply want to return the input after it has been processed, you may use the `thenReturn` method.

Of course, as discussed previously, you are not limited to providing closures to your pipeline. You may also provide invokable classes. If a class name is provided, the class will be instantiated via Venusian's [service container](/docs/{{version}}/framework/architecture-concepts/container), allowing dependencies to be injected into the invokable class:

```php
$user = app('pipeline')
    ->send($user)
    ->through([
        GenerateProfilePhoto::class,
        ActivateSubscription::class,
        SendWelcomeEmail::class,
    ])
    ->thenReturn();
```

The `withinTransaction` method may be invoked on the pipeline to automatically wrap all steps of the pipeline within a single database transaction:

```php
$user = app('pipeline')
    ->send($user)
    ->withinTransaction()
    ->through([
        ProcessOrder::class,
        TransferFunds::class,
        UpdateInventory::class,
    ])
    ->thenReturn();
```

### Sleep

Venusian's `Sleep` class is a light-weight wrapper around PHP's native `sleep` and `usleep` functions, offering greater testability while also exposing a developer friendly API for working with time:

```php
use Voyager\NutsAndBolts\Sleep;

$waiting = true;

while ($waiting) {
    Sleep::for(1)->second();

    $waiting = /* ... */;
}
```

The `Sleep` class offers a variety of methods that allow you to work with different units of time:

```php
// Return a value after sleeping...
$result = Sleep::for(1)->second()->then(fn () => 1 + 1);

// Sleep while a given value is true...
Sleep::for(1)->second()->while(fn () => shouldKeepSleeping());

// Pause execution for 90 seconds...
Sleep::for(1.5)->minutes();

// Pause execution for 2 seconds...
Sleep::for(2)->seconds();

// Pause execution for 500 milliseconds...
Sleep::for(500)->milliseconds();

// Pause execution for 5,000 microseconds...
Sleep::for(5000)->microseconds();

// Pause execution until a given time...
Sleep::until(now()->plus(minutes: 1));

// Alias of PHP's native "sleep" function...
Sleep::sleep(2);

// Alias of PHP's native "usleep" function...
Sleep::usleep(5000);
```

To easily combine units of time, you may use the `and` method:

```php
Sleep::for(1)->second()->and(10)->milliseconds();
```

#### Testing Sleep

When testing code that utilizes the `Sleep` class or PHP's native sleep functions, your test will pause execution. As you might expect, this makes your test suite significantly slower. For example, imagine you are testing the following code:

```php
$waiting = /* ... */;

$seconds = 1;

while ($waiting) {
    Sleep::for($seconds++)->seconds();

    $waiting = /* ... */;
}
```

Typically, testing this code would take _at least_ one second. Luckily, the `Sleep` class allows us to "fake" sleeping so that our test suite stays fast:

```php tab=Pest
it('waits until ready', function () {
    Sleep::fake();

    // ...
});
```

```php tab=PHPUnit
public function test_it_waits_until_ready()
{
    Sleep::fake();

    // ...
}
```

When faking the `Sleep` class, the actual execution pause is bypassed, leading to a substantially faster test.

Once the `Sleep` class has been faked, it is possible to make assertions against the expected "sleeps" that should have occurred. To illustrate this, let's imagine we are testing code that pauses execution three times, with each pause increasing by a single second. Using the `assertSequence` method, we can assert that our code "slept" for the proper amount of time while keeping our test fast:

```php tab=Pest
it('checks if ready three times', function () {
    Sleep::fake();

    // ...

    Sleep::assertSequence([
        Sleep::for(1)->second(),
        Sleep::for(2)->seconds(),
        Sleep::for(3)->seconds(),
    ]);
});
```

```php tab=PHPUnit
public function test_it_checks_if_ready_three_times()
{
    Sleep::fake();

    // ...

    Sleep::assertSequence([
        Sleep::for(1)->second(),
        Sleep::for(2)->seconds(),
        Sleep::for(3)->seconds(),
    ]);
}
```

Of course, the `Sleep` class offers a variety of other assertions you may use when testing:

```php
use Carbon\CarbonInterval as Duration;
use Voyager\NutsAndBolts\Sleep;

// Assert that sleep was called 3 times...
Sleep::assertSleptTimes(3);

// Assert against the duration of sleep...
Sleep::assertSlept(function (Duration $duration): bool {
    return /* ... */;
}, times: 1);

// Assert that the Sleep class was never invoked...
Sleep::assertNeverSlept();

// Assert that, even if Sleep was called, no execution paused occurred...
Sleep::assertInsomniac();
```

Sometimes it may be useful to perform an action whenever a fake sleep occurs. To achieve this, you may provide a callback to the `whenFakingSleep` method. In the following example, we freeze Carbon's clock and instantly progress it by the duration of each sleep:

```php
use Carbon\CarbonInterval as Duration;
use Voyager\NutsAndBolts\DataObjects\Carbon;

Carbon::setTestNow(now());

Sleep::fake();

Sleep::whenFakingSleep(function (Duration $duration) {
    // Progress time when faking sleep...
    Carbon::setTestNow(now()->add($duration));
});
```

As progressing time is a common requirement, the `fake` method accepts a `syncWithCarbon` argument to keep Carbon in sync when sleeping within a test:

```php
Sleep::fake(syncWithCarbon: true);

$start = now();

Sleep::for(1)->second();

$start->diffForHumans(); // 1 second ago
```

Venusian uses the `Sleep` class internally whenever it is pausing execution. For example, the [retry](#method-retry) helper uses the `Sleep` class when sleeping, allowing for improved testability when using that helper.
