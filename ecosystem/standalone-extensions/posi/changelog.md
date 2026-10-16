# Changelog

What changed in this package, newest first.

### 2026-10-14

* **Socket descriptors**: `posix_fileno`, `posix_dup`, `posix_socket_fdopen` added for sharing one listening socket across ext-parallel threads ([descriptors](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/descriptors-and-paths)). Suite 67 passed (66 + 1 skipped on php84, which has no ext-parallel). Shipped in tag v0.10.5; `PHP_POSI_VERSION` and the composer.json `version` read 0.10.6 at that tag.

### 2026-10-11

* **README rewritten** for 0.10.5 to the php-io-extensions template: centered header with badges, problem/solution intro, two-part Basic usage sketch (ioctl on i2c-dev, with a serial-port example), per-function API in the 0.4.0 style with every hardware-free example run on php84, zhp and the Pi, requirements table, both installers, test-suite run proven from a fresh clone on php84, zhp and the Pi (55 passed, 173 assertions). No code change; `PHP_POSI_VERSION` and the composer.json `version` move to 0.10.5. Concepts untouched.

### 2026-10-04

* **Creation**: Bundle created for ext-posi 0.10.0, the plain-C rewrite: [module](/docs/{{version}}/ecosystem/standalone-extensions/posi/guide/module), [descriptors](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/descriptors-and-paths), [processes](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/processes), [termios](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/termios), [native buffers](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/native-buffers), [constants](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/constants), [build](/docs/{{version}}/ecosystem/standalone-extensions/posi/runbooks/build-install-test), [upgrade from 0.9](/docs/{{version}}/ecosystem/standalone-extensions/posi/reference/upgrade-from-09).
