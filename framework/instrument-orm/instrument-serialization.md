# Instrument: Serialization

Instrument converts models, their relationships, and collections of models to arrays or JSON, and controls which attributes the serialized form includes.

## Introduction

You will often need to convert your models and relationships to arrays or JSON, such as when caching them, writing them to a file, or sending them to an API through the [HTTP client](/docs/{{version}}/framework/digging-deeper/http-client). Instrument includes convenient methods for making these conversions, as well as controlling which attributes are included in the serialized representation of your models.

## Serializing Models and Collections

### Serializing to Arrays

To convert a model and its loaded [relationships](/docs/{{version}}/framework/instrument-orm/instrument-relationships) to an array, you should use the `toArray` method. This method is recursive, so all attributes and all relations (including the relations of relations) will be converted to arrays:

```php
use App\Models\User;

$user = User::with('roles')->first();

return $user->toArray();
```

The `attributesToArray` method may be used to convert a model's attributes to an array but not its relationships:

```php
$user = User::first();

return $user->attributesToArray();
```

You may also convert entire [collections](/docs/{{version}}/framework/instrument-orm/instrument-collections) of models to arrays by calling the `toArray` method on the collection instance:

```php
$users = User::all();

return $users->toArray();
```

### Serializing to JSON

To convert a model to JSON, you should use the `toJson` method. Like `toArray`, the `toJson` method is recursive, so all attributes and relations will be converted to JSON. You may also specify any JSON encoding options that are [supported by PHP](https://secure.php.net/manual/en/function.json-encode.php):

```php
use App\Models\User;

$user = User::find(1);

return $user->toJson();

return $user->toJson(JSON_PRETTY_PRINT);
```

The `toPrettyJson` method is a shorthand for `toJson(JSON_PRETTY_PRINT)`, and accepts any additional encoding options:

```php
return $user->toPrettyJson();

return $user->toPrettyJson(JSON_UNESCAPED_SLASHES);
```

Alternatively, you may cast a model or collection to a string, which will automatically call the `toJson` method on the model or collection:

```php
return (string) User::find(1);
```

#### Relationships

When an Instrument model is converted to JSON, its loaded relationships will automatically be included as attributes on the JSON object. Also, though Instrument relationship methods are defined using "camel case" method names, a relationship's JSON attribute will be "snake case".

<a id="hiding-attributes-from-json"></a>
## Hiding Attributes From JSON

Sometimes you may wish to limit the attributes, such as passwords, that are included in your model's array or JSON representation. To do so, add a `$hidden` property to your model. Attributes that are listed in the `$hidden` property will not be included in the serialized representation of your model:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<string>
     */
    protected $hidden = ['password'];
}
```

> [!NOTE]
> To hide relationships, add the relationship's method name to your Instrument model's `$hidden` property.

Alternatively, you may use the `$visible` property to define an "allow list" of attributes that should be included in your model's array and JSON representation. All attributes that are not present in the `$visible` array will be hidden when the model is converted to an array or JSON:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * The attributes that should be visible in serialization.
     *
     * @var array<string>
     */
    protected $visible = ['first_name', 'last_name'];
}
```

<a id="temporarily-modifying-attribute-visibility"></a>
#### Temporarily Modifying Attribute Visibility

If you would like to make some typically hidden attributes visible on a given model instance, you may use the `makeVisible` or `mergeVisible` methods. The `makeVisible` method returns the model instance:

```php
return $user->makeVisible('attribute')->toArray();

return $user->mergeVisible(['name', 'email'])->toArray();
```

Likewise, if you would like to hide some attributes that are typically visible, you may use the `makeHidden` or `mergeHidden` methods:

```php
return $user->makeHidden('attribute')->toArray();

return $user->mergeHidden(['name', 'email'])->toArray();
```

The `makeVisibleIf` and `makeHiddenIf` methods change visibility only when the given condition is true. The condition may be a boolean or a closure that receives the model:

```php
return $user->makeVisibleIf($showContact, ['email', 'phone'])->toArray();

return $user->makeHiddenIf(fn (User $user) => ! $user->is_admin, 'notes')->toArray();
```

If you wish to temporarily override all of the visible or hidden attributes, you may use the `setVisible` and `setHidden` methods respectively:

```php
return $user->setVisible(['id', 'name'])->toArray();

return $user->setHidden(['email', 'password', 'remember_token'])->toArray();
```

<a id="appending-values-to-json"></a>
## Appending Values to JSON

Occasionally, when converting models to arrays or JSON, you may wish to add attributes that do not have a corresponding column in your database. To do so, first define an [accessor](/docs/{{version}}/framework/instrument-orm/instrument-mutators) for the value:

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Casts\Attribute;
use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * Determine if the user is an administrator.
     */
    protected function isAdmin(): Attribute
    {
        return new Attribute(
            get: fn () => 'yes',
        );
    }
}
```

If you would like the accessor to always be appended to your model's array and JSON representations, you may add the attribute name to the `$appends` property of your model. Note that attribute names are typically referenced using their "snake case" serialized representation, even though the accessor's PHP method is defined using "camel case":

```php
<?php

namespace App\Models;

use Voyager\Database\Instrument\Model;

class User extends Model
{
    /**
     * The accessors to append to the model's array form.
     *
     * @var array<string>
     */
    protected $appends = ['is_admin'];
}
```

Once the attribute has been added to the `appends` list, it will be included in both the model's array and JSON representations. Attributes in the `appends` array will also respect the `visible` and `hidden` settings configured on the model.

#### Appending at Run Time

At runtime, you may instruct a model instance to append additional attributes using the `append` or `mergeAppends` methods. Or, you may use the `setAppends` method to override the entire array of appended properties for a given model instance:

```php
return $user->append('is_admin')->toArray();

return $user->mergeAppends(['is_admin', 'status'])->toArray();

return $user->setAppends(['is_admin'])->toArray();
```

Likewise, if you would like to remove all appended properties from a model, you may use the `withoutAppends` method:

```php
return $user->withoutAppends()->toArray();
```

## Date Serialization

#### Customizing the Default Date Format

You may customize the default serialization format by overriding the `serializeDate` method. This method does not affect how your dates are formatted for storage in the database:

```php
/**
 * Prepare a date for array / JSON serialization.
 */
protected function serializeDate(DateTimeInterface $date): string
{
    return $date->format('Y-m-d');
}
```

#### Customizing the Date Format per Attribute

You may customize the serialization format of individual Instrument date attributes by specifying the date format in the model's [cast declarations](/docs/{{version}}/framework/instrument-orm/instrument-mutators#attribute-casting):

```php
protected function casts(): array
{
    return [
        'birthday' => 'date:Y-m-d',
        'joined_at' => 'datetime:Y-m-d H:00',
    ];
}
```
