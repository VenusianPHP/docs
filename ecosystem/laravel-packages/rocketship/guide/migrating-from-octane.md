# Migrating from Octane

Two commands. Nothing in your app changes.

```bash
composer remove laravel/octane
composer require projectsaturnstudios/rocketship
```

Rocketship declares a conflict with `laravel/octane`, so Octane comes out first.

### What stays as it was

| | |
|---|---|
| Your code | The namespace is still `Laravel\Octane`. The `Octane` facade, `Octane::concurrently()`, `Octane::table()`, ticks, the `octane` cache store and Octane's events resolve as before. |
| `config/octane.php` | Rocketship reads the file you published. It adds one `native` section; its defaults apply until you publish again. |
| `.env` | `OCTANE_SERVER`, `OCTANE_HTTPS` and the other `OCTANE_*` keys are read as before. |
| Your server | Swoole, RoadRunner and FrankenPHP run Octane's own code. A FrankenPHP worker file Octane published is pointed at Rocketship's worker on start or install. |
| Your process manager | `octane:start`, `octane:stop`, `octane:reload` and `octane:status` keep their names and options. |

Everything in [Octane's docs](https://laravel.com/docs/octane) still applies.

### Switching to the native server

Optional, and the reason to switch. Install the extensions from the [overview](/docs/{{version}}/ecosystem/laravel-packages/rocketship/overview#installation), then:

```bash
php artisan octane:install --server=native
php artisan octane:start --server=native
```

`octane:install --server=native` checks this PHP's extensions and prints what each mode is missing. Set `OCTANE_SERVER=native` to make it the default. Details in [the native server](/docs/{{version}}/ecosystem/laravel-packages/rocketship/guide/native-server).

Put nginx or another proxy in front in production, as with Octane's other servers.
