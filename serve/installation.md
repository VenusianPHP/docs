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

A web application needs route files, a public front controller, a page to show at `/` and the tables its users live in. The `install:web` command publishes all five:

```shell
php computer install:web
```

| File | What it holds |
| --- | --- |
| `routes/web.php` | Routes in the `web` middleware group: cookies, the session, shared errors, CSRF protection and route model binding. It starts with a `/` route that shows the welcome page and a `/up` health check route, which answers `200 OK` behind PHP-FPM; under `php computer serve` the server answers `/up` before the application does. |
| `routes/api.php` | Routes in the `api` middleware group, under the `api` prefix. |
| `public/index.php` | The front controller for servers that start PHP for each request, such as PHP-FPM. `php computer serve` does not use it. |
| `resources/views/welcome.blade.php` | The [welcome page](#the-welcome-page) the `/` route shows. |
| `database/migrations/0001_01_01_000000_create_users_table.php` | The `users` table, `password_reset_tokens` for password resets and `sessions` for the `database` session driver. Run `php computer migrate` to create them. If your application already has a `*_create_users_table.php` migration, it is kept and no second one is written. `php computer vendor:publish --tag=mariner-migrations` publishes the same file. |

A file that already exists is left alone. Pass `--force` to overwrite the first four; the migration is never overwritten, since your application may have run or changed it.

The command also gets the application ready to answer its first request:

- It creates `storage/framework/sessions` and `storage/framework/views`, where file sessions and compiled views are written. Sessions use the `file` driver by default, so no database is needed.
- It sets `APP_KEY` in `.env` when the key is empty or missing, creating `.env` from `.env.example` first if there is none. Cookies, sessions and CSRF protection are encrypted with it. An existing key is never replaced, even with `--force`.

Then start the server and open `http://127.0.0.1:8020`:

```shell
php computer serve
```

<a id="the-welcome-page"></a>
### The Welcome Page

`resources/views/welcome.blade.php` is a plain Blade view: it says your app is up and answering, shows the installed versions of `venusian/serve` and `venusian/framework` and the PHP version and SAPI it runs under, and links to the documentation and to serve on GitHub. It is yours to change or replace; point the `/` route in `routes/web.php` at your own page when you have one.

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
