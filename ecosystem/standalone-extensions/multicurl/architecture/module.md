# Module

Scope, file layout, how ext-curl's handles are reached, the callback state and its lifetime, the ext-curl dependency, and why no libcurl is linked.

## Scope

libcurl's multi interface, 1:1, plain C on the Zend API: one static class `Multicurl\Multi` whose ten methods bind the `curl_multi_*` calls ext-curl leaves out, plus `curlSocketStream()`. It works on ext-curl's own `CurlMultiHandle` and `CurlHandle` objects. No event loop, no constants, no FFI, no throwing on a non-`CURLM_OK` code.[^c] Linux and macOS; Windows is excluded in `composer.json`.

Through 0.11.0 the package was Zephir (`pcurl/multi.zep` / `multicurl/multi.zep`, optimizers, a generated `ext/` tree). The C in `src/multi-api.c` behind it is what `multicurl.c` carries now, unchanged in behaviour.

## Files

| File | Holds |
|---|---|
| `multicurl.c` | Everything: handle access, callback state, trampolines, the ten methods, MINIT/RINIT/RSHUTDOWN/MINFO, module entry |
| `php_multicurl.h` | `PHP_MULTICURL_VERSION`, module entry extern, TSRMLS cache |
| `multicurl.stub.php` | The declaration of `Multicurl\Multi`; gen_stub turns it into `multicurl_arginfo.h` |
| `config.m4` | `--enable-multicurl`, libcurl headers, the dependency on ext-curl |

## Reaching libcurl handles

ext-curl's structs are private, but both start with the libcurl handle and end with `zend_object std`:[^c]

* `php_curlm { CURLM *multi; zend_llist easyh; …; zend_object std; }`
* `php_curl  { CURL *cp; …; zend_object std; }`

So `(char *) obj - obj->handlers->offset` is the struct head. `multicurl_multi_ptr()` does this only after `Z_OBJCE_P(mh) == curl_multi_ce`, an exact match; anything else throws `Exception("expected a CurlMultiHandle")`. The socket trampoline maps a `CURL *` back to its `CurlHandle` by walking `easyh` (the zvals ext-curl adds on `curl_multi_add_handle`), dereferencing only entries whose class is exactly `curl_ce`.

## Callback state

A `ZEND_TLS HashTable *` registry keyed by `CURLM *` holds one `multicurl_multi_state { multi, socket_cb, socket_data, timer_cb, timer_data, sockp }` per multi that has used setopt's callback options or `curlMultiAssign()`. `ZEND_TLS` makes it per-thread under ZTS. The registry's destructor owns every zval in a state.[^c]

* libcurl's `SOCKETDATA`/`TIMERDATA` always point at the state; the PHP `*DATA` values live in the state.
* `sockp` owns the zvals given to `curl_multi_assign` (socket → `zval *`); reassigning frees the old one after libcurl accepts the new pointer.
* **free_obj hook.** When a state is created, its multi's `handlers` are swapped for a process-global copy of ext-curl's handlers (copied once, under a pthread mutex) whose `free_obj` is `multicurl_multi_free_obj`. That hook unhooks both `*FUNCTION` options, calls ext-curl's own `free_obj` (`curl_multi_cleanup`), then deletes the state. Every registry entry therefore belongs to a live multi, no state survives address reuse, and the state holds no reference to its multi. `handlers->offset` is copied with the table, so handle access still works.
* RSHUTDOWN detaches the registry (sets it to NULL first, so frees during teardown see none), unhooks every multi still alive, then destroys the states. Multis freed after RSHUTDOWN go straight to ext-curl's `free_obj`.
* The cycle collector cannot see into the registry. A callback that captures its own multi (`use ($m)`) forms `$m → state → closure → $m`, and that multi lives until the option is set back to `null` or the request ends. See [callback cycles](/docs/{{version}}/ecosystem/standalone-extensions/multicurl/traps/callback-cycles).

## Dependency on ext-curl

`multicurl.c` uses ext-curl's exported `curl_multi_ce` and `curl_ce` and walks its structs. The module entry declares `ZEND_MOD_REQUIRED("curl")`, so PHP refuses to start multicurl without ext-curl, and `config.m4` adds `PHP_ADD_EXTENSION_DEP([multicurl], [curl])` for static builds.[^c][^config] Where curl is a shared module (Debian's `20-curl.ini`), its ini sorts before `40-multicurl.ini`. See [needs ext-curl first](/docs/{{version}}/ecosystem/standalone-extensions/multicurl/traps/needs-ext-curl-first).

## libcurl: headers only, never linked

The `CURLM*` and `CURL*` handed to multicurl come from the libcurl ext-curl uses, so multicurl must call that same library. `config.m4` takes only the header flags from `pkg-config libcurl` (7.69.0 or newer: `CURLM_BAD_FUNCTION_ARGUMENT` first appears there) and links no libcurl on any OS: `curl_multi_*` resolve at load time from the libcurl the process already carries, which is the dylib Homebrew PHP links, the `.so` a distribution PHP or its `curl.so` links, or the libcurl compiled into a static micro binary.[^config] See [same libcurl as ext-curl](/docs/{{version}}/ecosystem/standalone-extensions/multicurl/traps/same-libcurl-as-ext-curl).

[^c]: [multicurl.c](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/multicurl.c)
[^config]: [config.m4](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/config.m4)
