# Installation

Add Venusian's web stack to an application: the `venusian/serve` package, its routes and its front controller.

## Introduction

`venusian/serve` carries the web side of Venusian: HTTP requests and responses, routing, sessions, cookies, authentication, validation, views, mail, notifications and images, under the `Mariner` namespace, plus the server you run with `php computer serve`. It adds to a Venusian application rather than replacing anything in it: the framework stays the same, and serve brings the pieces a web app needs.

<a id="installing-serve"></a>
## Installing Serve

Require the package with Composer:

```shell
composer require venusian/serve
```

Nothing needs registering by hand. The package's `composer.json` names `Mariner\Core\Providers\MarinerServiceProvider` under `extra.venusian.providers`, so package discovery registers it, and it registers every serve component's own provider and merges serve's configuration files into your application's.

<a id="installing-the-web-files"></a>
## Installing the Web Files

A web application needs route files and a public front controller. The `install:web` command publishes the three of them:

```shell
php computer install:web
```

| File | What it holds |
| --- | --- |
| `routes/web.php` | Routes in the `web` middleware group: cookies, the session, shared errors, CSRF protection and route model binding. It starts with a `/` route and a `/up` health check route, which answers `200 OK` behind PHP-FPM; under `php computer serve` the server answers `/up` before the application does. |
| `routes/api.php` | Routes in the `api` middleware group, under the `api` prefix. |
| `public/index.php` | The front controller for servers that start PHP for each request, such as PHP-FPM. `php computer serve` does not use it. |

A file that already exists is left alone. Pass `--force` to overwrite all three.

<a id="route-files"></a>
### Route Files

Serve loads the route files named in `config/routing.php` when the routes are not cached:

```php
'web' => base_path('routes/web.php'),

'api' => base_path('routes/api.php'),

'api_prefix' => 'api',
```

`web` loads in the `web` middleware group; `api` loads in the `api` group under `api_prefix`. Set a file to `null` to load it yourself, or not at all. A file that does not exist loads nothing.

<a id="next-steps"></a>
## Next Steps

With the files in place, [serve the application](/docs/{{version}}/serve/serving) with `php computer serve`, or put it [behind nginx or PHP-FPM](/docs/{{version}}/serve/deployment).
