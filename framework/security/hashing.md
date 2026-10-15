# Hashing

Venusian's hash manager provides secure Bcrypt and Argon2 hashing for storing user passwords, on the calling process or on a worker pool.

## Introduction

Venusian's hash manager provides secure Bcrypt and Argon2 hashing for storing user passwords. It is registered in the service container as `hash`, so you may resolve it with `app('hash')` or type-hint `Voyager\Hashing\HashManager`. The default hasher alone is available as `hash.driver`, which is also what a `Voyager\Contracts\Hashing\Hasher` type-hint receives.

Bcrypt is a great choice for hashing passwords because its "work factor" is adjustable, which means that the time it takes to generate a hash can be increased as hardware power increases. When hashing passwords, slow is good. The longer an algorithm takes to hash a password, the longer it takes malicious users to generate "rainbow tables" of all possible string hash values that may be used in brute force attacks against applications.

## Configuration

By default, Venusian uses the `bcrypt` hashing driver when hashing data. However, several other hashing drivers are supported, including [argon](https://en.wikipedia.org/wiki/Argon2) and [argon2id](https://en.wikipedia.org/wiki/Argon2).

You may specify your application's hashing driver using the `HASH_DRIVER` environment variable. The complete set of hashing driver options lives in your application's `config/hashing.php` configuration file: the Bcrypt `rounds` (`BCRYPT_ROUNDS`) and maximum value length (`BCRYPT_LIMIT`), and the Argon2 `memory`, `threads`, and `time` (`ARGON_MEMORY`, `ARGON_THREADS`, `ARGON_TIME`).

## Basic Usage

### Hashing Passwords

You may hash a password by calling the `make` method on the hash manager:

```php
<?php

namespace App\Services;

use Voyager\Contracts\Hashing\Hasher;

class PasswordService
{
    public function __construct(
        protected Hasher $hasher,
    ) {}

    /**
     * Hash a new password for storage.
     */
    public function hash(string $newPassword): string
    {
        // Validate the new password length...

        return $this->hasher->make($newPassword);
    }
}
```

#### Adjusting The Bcrypt Work Factor

If you are using the Bcrypt algorithm, the `make` method allows you to manage the work factor of the algorithm using the `rounds` option; however, the default work factor managed by Venusian is acceptable for most applications:

```php
$hashed = app('hash')->make('password', [
    'rounds' => 12,
]);
```

When `BCRYPT_LIMIT` is set, `make` throws an `InvalidArgumentException` for a value longer than that many bytes.

#### Adjusting The Argon2 Work Factor

If you are using the Argon2 algorithm, the `make` method allows you to manage the work factor of the algorithm using the `memory`, `time`, and `threads` options; however, the default values managed by Venusian are acceptable for most applications:

```php
$hashed = app('hash')->make('password', [
    'memory' => 1024,
    'time' => 2,
    'threads' => 2,
]);
```

> [!NOTE]
> For more information on these options, please refer to the [official PHP documentation regarding Argon hashing](https://secure.php.net/manual/en/function.password-hash.php).

#### Using a Specific Driver

The `driver` method returns the hasher for a driver other than the default:

```php
$hashed = app('hash')->driver('argon2id')->make('password');
```

### Verifying That a Password Matches a Hash

The `check` method provided by the hash manager allows you to verify that a given plain-text string corresponds to a given hash:

```php
if (app('hash')->check('plain-text', $hashedPassword)) {
    // The passwords match...
}
```

### Determining if a Password Needs to be Rehashed

The `needsRehash` method provided by the hash manager allows you to determine if the work factor used by the hasher has changed since the password was hashed. Some applications choose to perform this check whenever they verify a password:

```php
if (app('hash')->needsRehash($hashed)) {
    $hashed = app('hash')->make('plain-text');
}
```

### Inspecting a Hash

The `info` method returns the algorithm and options a hash was made with, and `isHashed` determines whether a string is already a hash:

```php
$info = app('hash')->info($hashed);

// ['algo' => '2y', 'algoName' => 'bcrypt', 'options' => ['cost' => 12]]

if (! app('hash')->isHashed($value)) {
    $value = app('hash')->make($value);
}
```

## Hashing on a Worker Pool

A hash is deliberately slow CPU work, and `make` and `check` block the calling process until it is done. When your application is running on the event loop, the `makeAsync` and `checkAsync` methods hand the work to a worker pool instead and return a `Voyager\Contracts\IOPools\Promise`:

```php
$hash = app('hash')->makeAsync('correct horse')->wait();

app('hash')->checkAsync('correct horse', $hash)->then(function (bool $matches) {
    // ...
});
```

Both methods accept the same options as their blocking counterparts, followed by an optional driver name. The worker hashes under your application's current `hashing` configuration, so a hash made on a worker matches one made in the calling process:

```php
$hash = app('hash')->makeAsync('correct horse', ['rounds' => 12], 'bcrypt')->wait();

$argon = app('hash')->makeAsync('correct horse', [], 'argon2id')->wait();
```

The work runs on the thread pool when `io-pools.pool_workers.threads` is enabled, and on the process pool otherwise. If neither pool is enabled in your `config/io-pools.php` file, `makeAsync` and `checkAsync` throw an `InvalidArgumentException`. Checking against a `null` hash resolves to `false`.

## Hash Algorithm Verification

To prevent hash algorithm manipulation, the hash manager's `check` method will first verify the given hash was generated using the application's selected hashing algorithm. If the algorithms are different, a `RuntimeException` exception will be thrown.

This is the expected behavior for most applications, where the hashing algorithm is not expected to change and different algorithms can be an indication of a malicious attack. However, if you need to support multiple hashing algorithms within your application, such as when migrating from one algorithm to another, you can disable hash algorithm verification by setting the `HASH_VERIFY` environment variable to `false`:

```ini
HASH_VERIFY=false
```
