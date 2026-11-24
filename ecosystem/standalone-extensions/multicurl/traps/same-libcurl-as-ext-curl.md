# Same libcurl as ext-curl

multicurl must call the exact libcurl that created the CURLM*/CURL* it is handed

## Trap

Handles come from ext-curl. If multicurl links a different libcurl, e.g. macOS `/usr/lib/libcurl` (which `curl-config` on PATH reports) while Homebrew PHP uses Homebrew's curl, both copies end up in the process and multicurl calls one library's functions on the other's structs.

## Do

The shared extension links no libcurl on any OS (`config.m4`): `curl_multi_*` resolve at load time from the libcurl the process already carries. Under Homebrew PHP that is the dylib PHP links; under a distribution PHP, the `.so` PHP or its `curl.so` links; inside a static micro binary (a `venusian build`), the libcurl compiled into it. Headers still come from `pkg-config libcurl`; point it at PHP's libcurl so the headers match (`install-macos.sh` derives it from `otool -L $PHP_BIN`).[^install] Don't use `curl-config`.

Measured 2026-10-08 on aarch64 Linux: a module that linked `libcurl.so.4` carried versioned references (`curl_multi_socket_action@CURL_OPENSSL_4`). Inside a static glibc micro runtime, those bound to the system `.so` while the `CURLM*` came from the runtime's own libcurl, and the first `curlMultiSocketAction` segfaulted. Built without the link, the references are unversioned and bind to the runtime's libcurl.

[^install]: [install-macos.sh](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/install-macos.sh)
