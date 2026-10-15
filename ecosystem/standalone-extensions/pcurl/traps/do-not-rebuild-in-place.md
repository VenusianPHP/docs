# Do not rebuild in place

Committed ext/ is ship-ready — regenerate only on a disposable copy

## Trap

The committed `ext/` tree is the ship-ready PIE/`phpize` input (`build-path: ext`).[^composer] The installer runs `zephir fullclean`/`generate` and `make` in place, which rewrites or dirties that tree.[^install] (The first `ext/` was generated in place only because the package did not exist yet.)

## Do

1. Copy the package tree to a disposable directory.
2. Run the installer in the copy, once per PHP build (NTS and ZTS).
3. Sync back only intentional artifacts: `ext/` sources and `ide/`.
4. Delete the copy.

[^composer]: [composer.json build-path](https://github.com/php-io-extensions/pcurl/blob/HEAD/composer.json)
[^install]: [install-macos.sh](https://github.com/php-io-extensions/pcurl/blob/HEAD/install-macos.sh)
