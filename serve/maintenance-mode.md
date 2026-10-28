# Maintenance Mode

Take the application down while you deploy or migrate, show a page or redirect meanwhile, and let yourself through with a secret.

## Introduction

While the application is in maintenance mode, every request is answered with `503 Service Unavailable`, or the status and page you choose, instead of running. The check is the global `Mariner\Http\Middleware\PreventRequestsDuringMaintenance` middleware, which runs on every request after CORS handling, and it reads the maintenance state on each request, so a running `php computer serve` notices `down` and `up` at once.

<a id="enabling-maintenance-mode"></a>
## Enabling Maintenance Mode

```shell
php computer down
```

Run it again with other options to change them while down. The command accepts:

| Option | Description |
| --- | --- |
| `--retry=` | Seconds, or a date and time, after which the client may retry. Sent as the `Retry-After` header; a date is converted to an HTTP date in GMT. |
| `--refresh=` | Seconds after which the browser should reload, sent as the `Refresh` header. |
| `--redirect=` | A path to redirect every request to, except requests expecting JSON. |
| `--render=` | A view to render once, now, and answer every request with, except requests expecting JSON. The view receives `$retryAfter`. |
| `--secret=` | A phrase that lets you through; see [Bypassing Maintenance Mode](#bypassing-maintenance-mode). |
| `--with-secret` | Generate a random secret and print the bypass URL. |
| `--status=` | The status to answer with. The default is `503`. |

```shell
php computer down --render="errors.503" --retry=60
```

`--render` takes any view name; Mariner renders an application's error pages from `resources/views/errors/{status}.blade.php`, so `errors.503` is the usual choice.

<a id="disabling-maintenance-mode"></a>
## Disabling Maintenance Mode

```shell
php computer up
```

<a id="bypassing-maintenance-mode"></a>
## Bypassing Maintenance Mode

Give `down` a secret, and visiting it as a path lets that browser through:

```shell
php computer down --secret="1630542a-246b-4b66-afa1-dd72a4c43515"
```

Visiting `https://example.com/1630542a-246b-4b66-afa1-dd72a4c43515` sets a `venusian_maintenance` cookie and redirects to the page you were heading for, or to `/`. The cookie is valid for 12 hours and carries an HMAC of its expiry signed with the secret, so it cannot be forged without the secret.

<a id="excluding-paths"></a>
## Excluding Paths

Paths that must stay reachable while down, such as a payment provider's webhook, can be excluded in a subclass of the middleware, through its `$except` property, or from a service provider:

```php
use Mariner\Http\Middleware\PreventRequestsDuringMaintenance;

PreventRequestsDuringMaintenance::except(['/webhooks/*']);
```

<a id="maintenance-mode-drivers"></a>
## Maintenance Mode Drivers

The state lives where `config/app.php` says:

```php
'maintenance' => [
    'driver' => env('APP_MAINTENANCE_DRIVER', 'file'),
    'store' => env('APP_MAINTENANCE_STORE'),
],
```

| Driver | Keeps the state |
| --- | --- |
| `file` | In `storage/framework/down`, on this machine. |
| `cache` | In the cache store named by `store`, or the default store, so every machine sharing it goes down together. |
| `array` | In memory, for tests. |

<a id="the-front-controller"></a>
## Behind PHP-FPM

`down` also writes `storage/framework/maintenance.php`, and the `public/index.php` that `install:web` publishes includes it before loading the framework. Under PHP-FPM a request in maintenance is then answered from the prerendered page, a redirect or a bypass check, without booting the application. `up` removes the file. `php computer serve` does not need it.

> [!NOTE]
> Queue workers keep processing jobs while the application is in maintenance mode.
