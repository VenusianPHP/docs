# Callback cycles

A callback that captures its own CurlMultiHandle is a cycle the GC cannot see

## Trap

multicurl stores callbacks and `*DATA`/`assign` values in a per-thread registry, not in the handle's own GC table. When a `CurlMultiHandle` is freed, its state is dropped through multicurl's `free_obj` hook.[^c] But a callback that captures the multi (`function () use ($m)`) forms `$m → state → closure → $m`, and the cycle collector cannot see the state half of it. That multi lives until the option is set back to `null` or the request ends (RSHUTDOWN cleans up safely).

Dropping a multi whose callbacks don't reference it frees it immediately, callbacks and all.

## Do

In long-running loops, don't capture the multi in its own callbacks. The timer callback already receives it as its first argument. If you must capture it, `curlMultiSetopt($m, 20001, null)` / `(…, 20004, null)` before dropping it.

[^c]: [multicurl_multi_free_obj](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/multicurl.c)
