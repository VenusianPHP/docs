# Encryption

Venusian's encryption services provide a simple, convenient interface for encrypting and decrypting text via OpenSSL using AES-256 and AES-128 encryption.

## Introduction

Venusian's encryption services provide a simple, convenient interface for encrypting and decrypting text via OpenSSL using AES-256 and AES-128 encryption. All of Venusian's encrypted values are authenticated, either by a message authentication code (MAC) or by the cipher's own tag, so that their underlying value cannot be modified or tampered with once encrypted.

## Configuration

Before using Venusian's encrypter, you must set the `key` configuration option in your `config/app.php` configuration file. This configuration value is driven by the `APP_KEY` environment variable. When you create an application with `venusian new`, a random 32 byte key is generated with PHP's secure random bytes generator and written to your `.env` file as a `base64:` value:

```ini
APP_KEY="base64:J63qRTDLub5NuZvP+kb8YIorGS6qFYHKVo6u7179stY="
```

If no key is configured, resolving the encrypter throws a `Voyager\Encryption\MissingAppKeyException`.

The `cipher` option in `config/app.php` selects the algorithm. The supported ciphers are `AES-128-CBC`, `AES-256-CBC`, `AES-128-GCM`, and `AES-256-GCM`; the key must be 16 bytes long for the 128 bit ciphers and 32 bytes long for the 256 bit ciphers. The CBC ciphers are signed with an HMAC-SHA256 MAC, while the GCM ciphers authenticate themselves with a tag. You may generate a key of the right length for a cipher using the `generateKey` method:

```php
use Voyager\Encryption\Encrypter;

$key = 'base64:'.base64_encode(Encrypter::generateKey('AES-256-GCM'));
```

<a id="gracefully-rotating-encryption-keys"></a>
### Gracefully Rotating Encryption Keys

If you change your application's encryption key, it will no longer be possible to decrypt any data that was encrypted with your previous encryption key.

To mitigate this issue, Venusian allows you to list your previous encryption keys in your application's `APP_PREVIOUS_KEYS` environment variable. This variable may contain a comma-delimited list of all of your previous encryption keys:

```ini
APP_KEY="base64:J63qRTDLub5NuZvP+kb8YIorGS6qFYHKVo6u7179stY="
APP_PREVIOUS_KEYS="base64:2nLsGFGzyoae2ax3EF2Lyq/hH6QghBGLIq5uL+Gp8/w="
```

When you set this environment variable, Venusian will always use the "current" encryption key when encrypting values. However, when decrypting values, Venusian will first try the current key, and if decryption fails using the current key, Venusian will try all previous keys until one of the keys is able to decrypt the value.

This approach to graceful decryption allows your application to keep reading the data it has already stored even if your encryption key is rotated.

### Signed Closures

The encryption key also signs serialized closures. When a closure is handed to a worker, such as a queued job or a task on a worker pool, it is signed with the application's key, so a worker only runs closures your application created.

## Using the Encrypter

The encrypter is registered in the service container as `encrypter`. You may resolve it with `app('encrypter')`, or type-hint the `Voyager\Contracts\Encryption\Encrypter` or `Voyager\Contracts\Encryption\StringEncrypter` contract on any class the container builds.

#### Encrypting a Value

You may encrypt a value using the `encryptString` method provided by the encrypter. All encrypted values are encrypted using OpenSSL and the configured cipher, which is AES-256-CBC by default. Furthermore, all encrypted values are authenticated. The integrated message authentication code will prevent the decryption of any values that have been tampered with by malicious users:

```php
<?php

namespace App\Services;

use Voyager\Contracts\Encryption\StringEncrypter;

class TokenVault
{
    public function __construct(
        protected StringEncrypter $encrypter,
    ) {}

    /**
     * Seal a DigitalOcean API token for storage.
     */
    public function seal(string $token): string
    {
        return $this->encrypter->encryptString($token);
    }
}
```

The `encrypt` method serializes the value before encrypting it, so you may encrypt arrays and objects as well as strings. Its counterpart, `decrypt`, unserializes the decrypted value:

```php
$encrypted = app('encrypter')->encrypt(['token' => $token]);

$value = app('encrypter')->decrypt($encrypted);
```

#### Decrypting a Value

You may decrypt values using the `decryptString` method provided by the encrypter. If the value cannot be properly decrypted, such as when the message authentication code is invalid, a `Voyager\Contracts\Encryption\DecryptException` will be thrown:

```php
use Voyager\Contracts\Encryption\DecryptException;

try {
    $decrypted = app('encrypter')->decryptString($encryptedValue);
} catch (DecryptException $e) {
    // ...
}
```

If you need to know whether a string looks like an encrypted payload before decrypting it, the static `Encrypter::appearsEncrypted` method checks its shape without decrypting it.
