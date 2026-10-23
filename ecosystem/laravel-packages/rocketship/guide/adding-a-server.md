# Adding a server

Octane hard-codes its servers in the start, stop, reload, status and install commands. Rocketship keeps them in a registry, so a package can add one.

Implement `ProjectSaturnStudios\Rocketship\Servers\ServerDriver`: `start`, `stop`, `reload`, `running` and `install`, each handed the Octane command that was run. Then register it from any service provider:

```php
use Laravel\Octane\Facades\Octane;

public function register(): void
{
    Octane::registerServer('myserver', MyServer::class);
}
```

After that, `octane:start --server=myserver` and every other Octane command run through it, and `octane:install` offers it in its list. A later registration with the same name replaces an earlier one, built-ins included.

`Octane::registerServer()` called before Octane's provider has booted is deferred, so a package provider can register in `register()`.

The built-in drivers (`swoole`, `roadrunner`, `frankenphp`, `native`) are the same mechanism: each delegates to Octane's own command methods, which Rocketship made public so a driver can reuse them.
