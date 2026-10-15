# Instrument: Mutators & Casting

Accessors, mutators, and attribute casting allow you to transform Instrument attribute values when you retrieve or set them on model instances.

## Introduction

Accessors, mutators, and attribute casting allow you to transform Instrument attribute values when you retrieve or set them on model instances. For example, you may want to use the [Venusian encrypter](/docs/{{version}}/framework/security/encryption) to encrypt a value while it is stored in the database, and then automatically decrypt the attribute when you access it on an Instrument model. Or, you may want to convert a JSON string that is stored in your database to an array when it is accessed via your Instrument model.

## Accessors and Mutators

### Defining an Accessor

An accessor transforms an Instrument attribute value when it is accessed. To define an accessor, create a protected method on your model to represent the accessible attribute. This method name should correspond to the "camel case" representation of the true underlying model attribute / database column when applicable.

In this example, we'll define an accessor for the `first_name` attribute. The accessor will automatically be called by Instrument when attempting to retrieve the value of the `first_name` attribute. All attribute accessor / mutator methods must declare a return type-hint of `Voyager\Database\Instrument\Casts\Attribute`:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Casts\Attribute;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Get the user's first name.
     */
    protected function firstName(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
        );
    }
}
```

All accessor methods return an `Attribute` instance which defines how the attribute will be accessed and, optionally, mutated. In this example, we are only defining how the attribute will be accessed. To do so, we supply the `get` argument to the `Attribute` class constructor.

As you can see, the original value of the column is passed to the accessor, allowing you to manipulate and return the value. To access the value of the accessor, you may simply access the `first_name` attribute on a model instance:

```php
use App\Models\User;

$user = User::find(1);

$firstName = $user->first_name;
```

> [!NOTE]
> If you would like these computed values to be added to the array / JSON representations of your model, [you will need to append them](/docs/{{version}}/framework/instrument-orm/instrument-serialization#appending-values-to-json).

#### Building Value Objects From Multiple Attributes

Sometimes your accessor may need to transform multiple model attributes into a single "value object". To do so, your `get` closure may accept a second argument of `$attributes`, which will be automatically supplied to the closure and will contain an array of all of the model's current attributes:

```php
use App\Support\Address;
use Voyager\Database\Instrument\Casts\Attribute;

/**
 * Interact with the user's address.
 */
protected function address(): Attribute
{
    return Attribute::make(
        get: fn (mixed $value, array $attributes) => new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two'],
        ),
    );
}
```

#### Accessor Caching

When returning value objects from accessors, any changes made to the value object will automatically be synced back to the model before the model is saved. This is possible because Instrument retains instances returned by accessors so it can return the same instance each time the accessor is invoked:

```php
use App\Models\User;

$user = User::find(1);

$user->address->lineOne = 'Updated Address Line 1 Value';
$user->address->lineTwo = 'Updated Address Line 2 Value';

$user->save();
```

However, you may sometimes wish to enable caching for primitive values like strings and booleans, particularly if they are computationally intensive. To accomplish this, you may invoke the `shouldCache` method when defining your accessor:

```php
protected function hash(): Attribute
{
    return Attribute::make(
        get: fn (string $value) => app('hash')->make(gzuncompress($value)),
    )->shouldCache();
}
```

If you would like to disable the object caching behavior of attributes, you may invoke the `withoutObjectCaching` method when defining the attribute:

```php
/**
 * Interact with the user's address.
 */
protected function address(): Attribute
{
    return Attribute::make(
        get: fn (mixed $value, array $attributes) => new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two'],
        ),
    )->withoutObjectCaching();
}
```

### Defining a Mutator

A mutator transforms an Instrument attribute value when it is set. To define a mutator, you may provide the `set` argument when defining your attribute. Let's define a mutator for the `first_name` attribute. This mutator will be automatically called when we attempt to set the value of the `first_name` attribute on the model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Casts\Attribute;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Interact with the user's first name.
     */
    protected function firstName(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
            set: fn (string $value) => strtolower($value),
        );
    }
}
```

The mutator closure will receive the value that is being set on the attribute, allowing you to manipulate the value and return the manipulated value. To use our mutator, we only need to set the `first_name` attribute on an Instrument model:

```php
use App\Models\User;

$user = User::find(1);

$user->first_name = 'Sally';
```

In this example, the `set` callback will be called with the value `Sally`. The mutator will then apply the `strtolower` function to the name and set its resulting value in the model's internal `$attributes` array.

#### Mutating Multiple Attributes

Sometimes your mutator may need to set multiple attributes on the underlying model. To do so, you may return an array from the `set` closure. Each key in the array should correspond with an underlying attribute / database column associated with the model:

```php
use App\Support\Address;
use Voyager\Database\Instrument\Casts\Attribute;

/**
 * Interact with the user's address.
 */
protected function address(): Attribute
{
    return Attribute::make(
        get: fn (mixed $value, array $attributes) => new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two'],
        ),
        set: fn (Address $value) => [
            'address_line_one' => $value->lineOne,
            'address_line_two' => $value->lineTwo,
        ],
    );
}
```

<a id="attribute-casting"></a>
## Attribute Casting

Attribute casting provides functionality similar to accessors and mutators without requiring you to define any additional methods on your model. Instead, your model's `casts` method provides a convenient way of converting attributes to common data types.

The `casts` method should return an array where the key is the name of the attribute being cast and the value is the type you wish to cast the column to. The supported cast types are:

- `array`
- `AsFluent::class`
- `AsHtmlString::class`
- `AsStringable::class`
- `boolean`
- `collection`
- `date`
- `datetime`
- `immutable_date`
- `immutable_datetime`
- <code>decimal:&lt;precision&gt;</code>
- `double`
- `encrypted`
- `encrypted:array`
- `encrypted:collection`
- `encrypted:json`
- `encrypted:object`
- `float`
- `hashed`
- `integer`
- `json`
- `json:unicode`
- `object`
- `real`
- `string`
- `timestamp`

The `bool` and `int` aliases are accepted wherever `boolean` and `integer` are. The `AsFluent`, `AsHtmlString`, and `AsStringable` classes live in the `Voyager\Database\Instrument\Casts` namespace and cast the attribute to a `Voyager\NutsAndBolts\Fluent`, `Voyager\NutsAndBolts\HtmlString`, and `Voyager\NutsAndBolts\DataObjects\Stringable` instance respectively.

To demonstrate attribute casting, let's cast the `is_admin` attribute, which is stored in our database as an integer (`0` or `1`) to a boolean value:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'is_admin' => 'boolean',
        ];
    }
}
```

After defining the cast, the `is_admin` attribute will always be cast to a boolean when you access it, even if the underlying value is stored in the database as an integer:

```php
$user = App\Models\User::find(1);

if ($user->is_admin) {
    // ...
}
```

If you need to add a new, temporary cast at runtime, you may use the `mergeCasts` method. These cast definitions will be added to any of the casts already defined on the model:

```php
$user->mergeCasts([
    'is_admin' => 'integer',
    'options' => 'object',
]);
```

> [!WARNING]
> Attributes that are `null` will not be cast. In addition, you should never define a cast (or an attribute) that has the same name as a relationship or assign a cast to the model's primary key.

#### Stringable Casting

You may use the `Voyager\Database\Instrument\Casts\AsStringable` cast class to cast a model attribute to a [fluent Voyager\NutsAndBolts\DataObjects\Stringable object](/docs/{{version}}/framework/digging-deeper/strings#fluent-strings):

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Casts\AsStringable;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'directory' => AsStringable::class,
        ];
    }
}
```

### Array and JSON Casting

The `array` cast is particularly useful when working with columns that are stored as serialized JSON. For example, if your database has a `JSON` or `TEXT` field type that contains serialized JSON, adding the `array` cast to that attribute will automatically deserialize the attribute to a PHP array when you access it on your Instrument model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'options' => 'array',
        ];
    }
}
```

Once the cast is defined, you may access the `options` attribute and it will automatically be deserialized from JSON into a PHP array. When you set the value of the `options` attribute, the given array will automatically be serialized back into JSON for storage:

```php
use App\Models\User;

$user = User::find(1);

$options = $user->options;

$options['key'] = 'value';

$user->options = $options;

$user->save();
```

To update a single field of a JSON attribute with a more terse syntax, you may [make the attribute mass assignable](/docs/{{version}}/framework/instrument-orm/instrument#mass-assignment-and-json-columns) and use the `->` operator when calling the `update` method:

```php
$user = User::find(1);

$user->update(['options->key' => 'value']);
```

#### JSON and Unicode

If you would like to store an array attribute as JSON with unescaped Unicode characters, you may use the `json:unicode` cast:

```php
/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => 'json:unicode',
    ];
}
```

#### Array Object and Collection Casting

Although the standard `array` cast is sufficient for many applications, it does have some disadvantages. Since the `array` cast returns a primitive type, it is not possible to mutate an offset of the array directly. For example, the following code will trigger a PHP error:

```php
$user = User::find(1);

$user->options['key'] = $value;
```

To solve this, Instrument offers an `AsArrayObject` cast that casts your JSON attribute to an [ArrayObject](https://www.php.net/manual/en/class.arrayobject.php) class. This feature is implemented using Instrument's [custom cast](#custom-casts) implementation, which allows Instrument to intelligently cache and transform the mutated object such that individual offsets may be modified without triggering a PHP error. To use the `AsArrayObject` cast, simply assign it to an attribute:

```php
use Voyager\Database\Instrument\Casts\AsArrayObject;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsArrayObject::class,
    ];
}
```

Similarly, Instrument offers an `AsCollection` cast that casts your JSON attribute to a [Collection](/docs/{{version}}/framework/digging-deeper/collections) instance:

```php
use Voyager\Database\Instrument\Casts\AsCollection;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::class,
    ];
}
```

If you would like the `AsCollection` cast to instantiate a custom collection class instead of the base `Voyager\NutsAndBolts\Collection` class, you may provide the collection class name as a cast argument:

```php
use App\Collections\OptionCollection;
use Voyager\Database\Instrument\Casts\AsCollection;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::using(OptionCollection::class),
    ];
}
```

The `of` method may be used to indicate collection items should be mapped into a given class via the collection's [mapInto method](/docs/{{version}}/framework/digging-deeper/collections#method-mapinto):

```php
use App\ValueObjects\Option;
use Voyager\Database\Instrument\Casts\AsCollection;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::of(Option::class)
    ];
}
```

When mapping collections to objects, the object should implement the `Voyager\Contracts\NutsAndBolts\Arrayable` and `JsonSerializable` interfaces to define how their instances should be serialized into the database as JSON:

```php
<?php

namespace App\ValueObjects;

use Voyager\Contracts\NutsAndBolts\Arrayable;
use JsonSerializable;

class Option implements Arrayable, JsonSerializable
{
    public string $name;
    public mixed $value;
    public bool $isLocked;

    /**
     * Create a new Option instance.
     */
    public function __construct(array $data)
    {
        $this->name = $data['name'];
        $this->value = $data['value'];
        $this->isLocked = $data['is_locked'];
    }

    /**
     * Get the instance as an array.
     *
     * @return array{name: string, data: string, is_locked: bool}
     */
    public function toArray(): array
    {
        return [
            'name' => $this->name,
            'value' => $this->value,
            'is_locked' => $this->isLocked,
        ];
    }

    /**
     * Specify the data which should be serialized to JSON.
     *
     * @return array{name: string, data: string, is_locked: bool}
     */
    public function jsonSerialize(): array
    {
        return $this->toArray();
    }
}
```

### Binary Casting

If your Instrument model has a [binary type](/docs/{{version}}/framework/database/migrations#column-method-binary) `uuid` or `ulid` column in addition to your model's auto-incrementing ID column, you may use the `AsBinary` cast to automatically cast the value to and from its binary representation:

```php
use Voyager\Database\Instrument\Casts\AsBinary;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'uuid' => AsBinary::uuid(),
        'ulid' => AsBinary::ulid(),
    ];
}
```

Once the cast has been defined on the model, you may set the UUID / ULID attribute value to an object instance or a string. Instrument will automatically cast the value to its binary representation. When retrieving the attribute's value, you will always receive a plain-text string value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$user->uuid = Str::uuid();

return $user->uuid;

// "6e8cdeed-2f32-40bd-b109-1e4405be2140"
```

### Date Casting

By default, Instrument will cast the `created_at` and `updated_at` columns to instances of [Carbon](https://github.com/briannesbitt/Carbon), which extends the PHP `DateTime` class and provides an assortment of helpful methods. You may cast additional date attributes by defining additional date casts within your model's `casts` method. Typically, dates should be cast using the `datetime` or `immutable_datetime` cast types.

When defining a `date` or `datetime` cast, you may also specify the date's format. This format will be used when the [model is serialized to an array or JSON](/docs/{{version}}/framework/instrument-orm/instrument-serialization):

```php
/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'created_at' => 'datetime:Y-m-d',
    ];
}
```

When a column is cast as a date, you may set the corresponding model attribute value to a UNIX timestamp, date string (`Y-m-d`), date-time string, or a `DateTime` / `Carbon` instance. The date's value will be correctly converted and stored in your database.

You may customize the default serialization format for all of your model's dates by defining a `serializeDate` method on your model. This method does not affect how your dates are formatted for storage in the database:

```php
/**
 * Prepare a date for array / JSON serialization.
 */
protected function serializeDate(DateTimeInterface $date): string
{
    return $date->format('Y-m-d');
}
```

To specify the format that should be used when actually storing a model's dates within your database, you should define a `$dateFormat` property on your model:

```php
use Voyager\Database\Instrument\Model;

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

#### Date Casting, Serialization, and Timezones

By default, the `date` and `datetime` casts will serialize dates to a UTC ISO-8601 date string (`YYYY-MM-DDTHH:MM:SS.uuuuuuZ`), regardless of the timezone specified in your application's `timezone` configuration option. You are strongly encouraged to always use this serialization format, as well as to store your application's dates in the UTC timezone by not changing your application's `timezone` configuration option from its default `UTC` value. Consistently using the UTC timezone throughout your application will provide the maximum level of interoperability with other date manipulation libraries written in PHP and JavaScript.

If a custom format is applied to the `date` or `datetime` cast, such as `datetime:Y-m-d H:i:s`, the inner timezone of the Carbon instance will be used during date serialization. Typically, this will be the timezone specified in your application's `timezone` configuration option. However, it's important to note that `timestamp` columns such as `created_at` and `updated_at` are exempt from this behavior and are always formatted in UTC, regardless of the application's timezone setting.

### Enum Casting

Instrument also allows you to cast your attribute values to PHP [Enums](https://www.php.net/manual/en/language.enumerations.backed.php). To accomplish this, you may specify the attribute and enum you wish to cast in your model's `casts` method:

```php
use App\Enums\ServerStatus;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'status' => ServerStatus::class,
    ];
}
```

Once you have defined the cast on your model, the specified attribute will be automatically cast to and from an enum when you interact with the attribute:

```php
if ($server->status == ServerStatus::Provisioned) {
    $server->status = ServerStatus::Ready;

    $server->save();
}
```

#### Casting Arrays of Enums

Sometimes you may need your model to store an array of enum values within a single column. To accomplish this, you may utilize the `AsEnumArrayObject` or `AsEnumCollection` casts provided by Instrument:

```php
use App\Enums\ServerStatus;
use Voyager\Database\Instrument\Casts\AsEnumCollection;

/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'statuses' => AsEnumCollection::of(ServerStatus::class),
    ];
}
```

### Encrypted Casting

The `encrypted` cast will encrypt a model's attribute value using Venusian's built-in [encryption](/docs/{{version}}/framework/security/encryption) features. In addition, the `encrypted:array`, `encrypted:collection`, `encrypted:json`, `encrypted:object`, `AsEncryptedArrayObject`, and `AsEncryptedCollection` casts work like their unencrypted counterparts; however, as you might expect, the underlying value is encrypted when stored in your database.

As the final length of the encrypted text is not predictable and is longer than its plain text counterpart, make sure the associated database column is of `TEXT` type or larger. In addition, since the values are encrypted in the database, you will not be able to query or search encrypted attribute values.

#### Key Rotation

As you may know, Venusian encrypts strings using the `key` configuration value specified in your application's `app` configuration file. Typically, this value corresponds to the value of the `APP_KEY` environment variable. If you need to rotate your application's encryption key, you may [gracefully do so](/docs/{{version}}/framework/security/encryption#gracefully-rotating-encryption-keys).

By default, encrypted casts use the encrypter bound in the container. If your models should encrypt with a key other than the application's, you may hand Instrument another `Voyager\Contracts\Encryption\Encrypter` instance using the `encryptUsing` method. The encrypter is shared by every model:

```php
use Voyager\Database\Instrument\Model;
use Voyager\Encryption\Encrypter;

Model::encryptUsing(new Encrypter($key, config('app.cipher')));
```

### Query Time Casting

Sometimes you may need to apply casts while executing a query, such as when selecting a raw value from a table. For example, consider the following query:

```php
use App\Models\Post;
use App\Models\User;

$users = User::select([
    'users.*',
    'last_posted_at' => Post::selectRaw('MAX(created_at)')
        ->whereColumn('user_id', 'users.id')
])->get();
```

The `last_posted_at` attribute on the results of this query will be a simple string. It would be wonderful if we could apply a `datetime` cast to this attribute when executing the query. Thankfully, we may accomplish this using the `withCasts` method:

```php
$users = User::select([
    'users.*',
    'last_posted_at' => Post::selectRaw('MAX(created_at)')
        ->whereColumn('user_id', 'users.id')
])->withCasts([
    'last_posted_at' => 'datetime'
])->get();
```

<a id="custom-casts"></a>
## Custom Casts

Instrument has a variety of built-in, helpful cast types; however, you may occasionally need to define your own cast types. Custom cast classes are typically placed in your application's `app/Casts` directory.

All custom cast classes implement the `CastsAttributes` interface. Classes that implement this interface must define a `get` and `set` method. The `get` method is responsible for transforming a raw value from the database into a cast value, while the `set` method should transform a cast value into a raw value that can be stored in the database. As an example, we will re-implement the built-in `json` cast type as a custom cast type:

```php
<?php

namespace App\Casts;

use Voyager\Contracts\Database\Instrument\CastsAttributes;
use Voyager\Database\Instrument\Model;

class AsJson implements CastsAttributes
{
    /**
     * Cast the given value.
     *
     * @param  array<string, mixed>  $attributes
     * @return array<string, mixed>
     */
    public function get(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): array {
        return json_decode($value, true);
    }

    /**
     * Prepare the given value for storage.
     *
     * @param  array<string, mixed>  $attributes
     */
    public function set(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): string {
        return json_encode($value);
    }
}
```

Once you have defined a custom cast type, you may attach it to a model attribute using its class name:

```php
<?php

namespace App\Models;

use App\Casts\AsJson;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'options' => AsJson::class,
        ];
    }
}
```

### Value Object Casting

You are not limited to casting values to primitive types. You may also cast values to objects. Defining custom casts that cast values to objects is very similar to casting to primitive types; however, if your value object encompasses more than one database column, the `set` method must return an array of key / value pairs that will be used to set raw, storable values on the model. If your value object only affects a single column, you should simply return the storable value.

As an example, we will define a custom cast class that casts multiple model values into a single `Address` value object. We will assume the `Address` value object has two public properties: `lineOne` and `lineTwo`:

```php
<?php

namespace App\Casts;

use App\ValueObjects\Address;
use Voyager\Contracts\Database\Instrument\CastsAttributes;
use Voyager\Database\Instrument\Model;
use InvalidArgumentException;

class AsAddress implements CastsAttributes
{
    /**
     * Cast the given value.
     *
     * @param  array<string, mixed>  $attributes
     */
    public function get(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): Address {
        return new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two']
        );
    }

    /**
     * Prepare the given value for storage.
     *
     * @param  array<string, mixed>  $attributes
     * @return array<string, string>
     */
    public function set(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): array {
        if (! $value instanceof Address) {
            throw new InvalidArgumentException('The given value is not an Address instance.');
        }

        return [
            'address_line_one' => $value->lineOne,
            'address_line_two' => $value->lineTwo,
        ];
    }
}
```

When casting to value objects, any changes made to the value object will automatically be synced back to the model before the model is saved:

```php
use App\Models\User;

$user = User::find(1);

$user->address->lineOne = 'Updated Address Value';

$user->save();
```

> [!NOTE]
> If you plan to serialize your Instrument models containing value objects to JSON or arrays, you should implement the `Voyager\Contracts\NutsAndBolts\Arrayable` and `JsonSerializable` interfaces on the value object.

#### Value Object Caching

When attributes that are cast to value objects are resolved, they are cached by Instrument. Therefore, the same object instance will be returned if the attribute is accessed again.

If you would like to disable the object caching behavior of custom cast classes, you may declare a public `withoutObjectCaching` property on your custom cast class:

```php
class AsAddress implements CastsAttributes
{
    public bool $withoutObjectCaching = true;

    // ...
}
```

### Array / JSON Serialization

When an Instrument model is converted to an array or JSON using the `toArray` and `toJson` methods, your custom cast value objects will typically be serialized as well as long as they implement the `Voyager\Contracts\NutsAndBolts\Arrayable` and `JsonSerializable` interfaces. However, when using value objects provided by third-party libraries, you may not have the ability to add these interfaces to the object.

Therefore, you may specify that your custom cast class will be responsible for serializing the value object. To do so, your custom cast class should implement the `Voyager\Contracts\Database\Instrument\SerializesCastableAttributes` interface. This interface states that your class should contain a `serialize` method which should return the serialized form of your value object:

```php
/**
 * Get the serialized representation of the value.
 *
 * @param  array<string, mixed>  $attributes
 */
public function serialize(
    Model $model,
    string $key,
    mixed $value,
    array $attributes,
): string {
    return (string) $value;
}
```

### Inbound Casting

Occasionally, you may need to write a custom cast class that only transforms values that are being set on the model and does not perform any operations when attributes are being retrieved from the model.

Inbound only custom casts should implement the `CastsInboundAttributes` interface, which only requires a `set` method to be defined.

A classic example of an inbound only cast is a "hashing" cast. For example, we may define a cast that hashes inbound values via a given algorithm:

```php
<?php

namespace App\Casts;

use Voyager\Contracts\Database\Instrument\CastsInboundAttributes;
use Voyager\Database\Instrument\Model;

class AsHash implements CastsInboundAttributes
{
    /**
     * Create a new cast class instance.
     */
    public function __construct(
        protected string|null $algorithm = null,
    ) {}

    /**
     * Prepare the given value for storage.
     *
     * @param  array<string, mixed>  $attributes
     */
    public function set(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): string {
        return is_null($this->algorithm)
            ? app('hash')->make($value)
            : hash($this->algorithm, $value);
    }
}
```

### Cast Parameters

When attaching a custom cast to a model, cast parameters may be specified by separating them from the class name using a `:` character and comma-delimiting multiple parameters. The parameters will be passed to the constructor of the cast class:

```php
/**
 * Get the attributes that should be cast.
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'secret' => AsHash::class.':sha256',
    ];
}
```

### Comparing Cast Values

If you would like to define how two given cast values should be compared to determine if they have been changed, your custom cast class may implement the `Voyager\Contracts\Database\Instrument\ComparesCastableAttributes` interface. This allows you to have fine-grained control over which values Instrument considers changed and thus saves to the database when a model is updated.

This interface states that your class should contain a `compare` method which should return `true` if the given values are considered equal:

```php
/**
 * Determine if the given values are equal.
 *
 * @param  \Voyager\Database\Instrument\Model  $model
 * @param  string  $key
 * @param  mixed  $firstValue
 * @param  mixed  $secondValue
 * @return bool
 */
public function compare(
    Model $model,
    string $key,
    mixed $firstValue,
    mixed $secondValue
): bool {
    return $firstValue === $secondValue;
}
```

### Castables

You may want to allow your application's value objects to define their own custom cast classes. Instead of attaching the custom cast class to your model, you may alternatively attach a value object class that implements the `Voyager\Contracts\Database\Instrument\Castable` interface:

```php
use App\ValueObjects\Address;

protected function casts(): array
{
    return [
        'address' => Address::class,
    ];
}
```

Objects that implement the `Castable` interface must define a `castUsing` method that returns the class name of the custom caster class that is responsible for casting to and from the `Castable` class:

```php
<?php

namespace App\ValueObjects;

use Voyager\Contracts\Database\Instrument\Castable;
use App\Casts\AsAddress;

class Address implements Castable
{
    /**
     * Get the name of the caster class to use when casting from / to this cast target.
     *
     * @param  array<string, mixed>  $arguments
     */
    public static function castUsing(array $arguments): string
    {
        return AsAddress::class;
    }
}
```

When using `Castable` classes, you may still provide arguments in the `casts` method definition. The arguments will be passed to the `castUsing` method:

```php
use App\ValueObjects\Address;

protected function casts(): array
{
    return [
        'address' => Address::class.':argument',
    ];
}
```

#### Castables & Anonymous Cast Classes

By combining "castables" with PHP's [anonymous classes](https://www.php.net/manual/en/language.oop5.anonymous.php), you may define a value object and its casting logic as a single castable object. To accomplish this, return an anonymous class from your value object's `castUsing` method. The anonymous class should implement the `CastsAttributes` interface:

```php
<?php

namespace App\ValueObjects;

use Voyager\Contracts\Database\Instrument\Castable;
use Voyager\Contracts\Database\Instrument\CastsAttributes;
use Voyager\Database\Instrument\Model;

class Address implements Castable
{
    // ...

    /**
     * Get the caster class to use when casting from / to this cast target.
     *
     * @param  array<string, mixed>  $arguments
     */
    public static function castUsing(array $arguments): CastsAttributes
    {
        return new class implements CastsAttributes
        {
            public function get(
                Model $model,
                string $key,
                mixed $value,
                array $attributes,
            ): Address {
                return new Address(
                    $attributes['address_line_one'],
                    $attributes['address_line_two']
                );
            }

            public function set(
                Model $model,
                string $key,
                mixed $value,
                array $attributes,
            ): array {
                return [
                    'address_line_one' => $value->lineOne,
                    'address_line_two' => $value->lineTwo,
                ];
            }
        };
    }
}
```
