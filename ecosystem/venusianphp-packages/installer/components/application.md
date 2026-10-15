# Application

Symfony Console application that offers a Packagist self-update before dispatching commands.

## Role

`Venusian\Installer\Console\Application` extends `Symfony\Component\Console\Application`.[^app]

`bin/venusian` constructs `new Application('Venusian PHP Application Installer', '0.10.2')` and registers [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand).[^bin]

## doRun

Reads `$_SERVER['argv'] ?? []`, then:[^app][^watcher]

```
$this->releaseWatcher->maybeOfferUpdate($input, $output, $argv, $this->getVersion());
return parent::doRun($input, $output);
```

`offers an update with argv and its own version before running the command` asserts the watcher gets `$_SERVER['argv']` and the app version, and runs before the command.[^app-test] Watcher behavior (offer, skip, cache): `PackagistReleaseWatcherTest`.[^watcher-test]

## bin/venusian

Loads the global Composer autoloader when installed globally (`../../../autoload.php`), else the checkout's `vendor/autoload.php`. Adds `NewApplicationCommand`; a throw prints its message to STDERR, exit 1. `reports the version composer.json declares from bin/venusian` and `registers the new command in bin/venusian` run it with the update check off.[^bin][^bin-test]

The watcher is constructor-injectable (`?PackagistReleaseWatcher $releaseWatcher = null`).

## Related

- [PackagistReleaseWatcher](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/packagistreleasewatcher)
- [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand)
- [Package](/docs/{{version}}/ecosystem/venusianphp-packages/installer/orientation/package)

[^app]: Venusian\\Installer\\Console\\Application
[^bin]: Entrypoint constructs Application 0.10.2
[^watcher]: maybeOfferUpdate
[^watcher-test]: Pest coverage for the watcher itself
[^app-test]: Pest coverage for doRun ordering and arguments
[^bin-test]: Pest coverage for bin/venusian version and commands
