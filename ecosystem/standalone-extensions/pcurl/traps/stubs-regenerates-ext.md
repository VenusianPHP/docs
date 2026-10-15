# Stubs regenerates ext

Running zephir stubs after pre-install silently discards the clang/ overlays

## Trap

Zephir 0.19's `zephir stubs` re-runs generation ("Cleaning old kernel files… Copying new kernel files…"), rewriting `ext/config.m4` and `ext/kernel/*`. posi's installer runs it after `pre-install.sh`, so the overlays are lost. For pcurl that dropped the libcurl link and the `src` build dir: the `.so` still loaded, but only through macOS `dynamic_lookup`.

## Do

Run `zephir stubs` **before** `pre-install.sh` (as `install-macos.sh` does now).[^install] After building, check `diff -q clang/config.m4 ext/config.m4` and `grep "checking for libcurl" build.log`.

[^install]: [step order](https://github.com/php-io-extensions/pcurl/blob/HEAD/install-macos.sh)
