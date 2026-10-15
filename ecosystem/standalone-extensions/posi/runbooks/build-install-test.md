# Build, install, test

gen_stub after a stub edit, scratch builds, the two installers, Pest on Mac and Pi, PIE.

## Needs

php-dev (phpize, php-config) for each target PHP, a C compiler. No library. ext/posix loaded at runtime.

## Stub → arginfo

Edit `posi.stub.php`, never `posi_arginfo.h`. Regenerate with the target PHP's gen_stub:

```bash
php "$(php-config --prefix)/lib/php/build/gen_stub.php" posi.stub.php
```

Holds for Homebrew and source builds (Pi: `/usr/local/php84-zts`). Stub rules: no `use` statements (fully qualify), `@cvalue` + `#ifdef` per constant, docblock `@param` in gen_stub's format. Commit stub and arginfo together; arginfo header carries the stub hash.

## Scratch build

Build outside the repo so phpize output never lands in the tree. Copy the five sources out:

```bash
mkdir -p "$TMP/posi" && cp config.m4 posi.c posi_termios.c php_posi.h posi_arginfo.h "$TMP/posi/"
cd "$TMP/posi" && phpize && ./configure --enable-posi && make -j
```

Run Pest from the repo: `php -d extension=$TMP/posi/modules/posi.so vendor/bin/pest`. A PHP that already loads a posi (0.9 Zephir ext shares the name) warns `Module "posi" is already loaded` and keeps the old one: test with `php -n -d extension=…` (ext/posix is built in on Homebrew and the Pi's source build; elsewhere add `-d extension=posix`).

## Installers

Both: build in `mktemp -d` copy per PHP binary, install `posi.so` into `extension_dir`, write `30-posi.ini` (`extension=posi`) into the conf.d scan dir, verify `extension_loaded('posi')`, delete the copy.[^mac][^debian]

- `install-macos.sh [php …]`: default Homebrew `php@8.4` + `php@8.4-zts`; `codesign --force --sign -` so amfid accepts the `.so` on first load.
- `install-debian-trixie.sh [php …]`: default `php` on PATH; finds versioned `phpize8.4`/`php-config8.4`; writes through a `30-posi.ini` symlink into Debian `mods-available` so every SAPI stays enabled.

## Mac targets

`php84` and `zhp` wrappers = Homebrew NTS and ZTS. Every change builds and passes Pest on both.

## Pi loop

Mac tree authoritative; Pi copy disposable. From the repo:

```bash
COPYFILE_DISABLE=1 tar --no-mac-metadata --no-xattrs -czf - config.m4 posi.c posi_termios.c php_posi.h posi_arginfo.h composer.json phpunit.xml tests \
  | fnk 'rm -rf ~/posi && mkdir ~/posi && tar -xzf - -C ~/posi && cd ~/posi && phpize && ./configure --enable-posi && make -j4'
fnk 'cd ~/posi && composer install -q && php -n -d extension=$PWD/modules/posi.so vendor/bin/pest; rm -rf ~/posi'
```

Without `COPYFILE_DISABLE`/`--no-mac-metadata` the copy carries `._*` AppleDouble files that gen_stub and Pest trip on.

## PIE

`composer.json` `type: php-ext`, `php-ext.extension-name: posi`, priority 30, NTS + ZTS, Windows excluded, configure option `--enable-posi`. `pie install php-io-extensions/posi` builds from the tagged archive; `.gitattributes` export-ignores tests, `phpunit.xml`, `.okf`, `AGENTS.md`, `CLAUDE.md`. Version lives in `composer.json` `version` and `PHP_POSI_VERSION` (`php_posi.h`); bump both together, only past a published tag.[^composer]

[^mac]: install-macos.sh
[^debian]: install-debian-trixie.sh
[^composer]: composer.json
