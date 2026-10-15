# Same libcurl as ext-curl

pcurl must call the exact libcurl that created the CURLM*/CURL* it is handed

## Trap

Handles come from ext-curl. If pcurl links a different libcurl, e.g. macOS `/usr/lib/libcurl` (8.7.1, which `curl-config` on PATH reports) while Homebrew PHP uses `/opt/homebrew/opt/curl` (8.22), both copies end up in the process and pcurl calls one library's functions on the other's structs. That means silent corruption# Do

The shared extension links no libcurl on any OS (`ext/config.m4`, `clang/config.m4`): `curl_multi_*` resolve at load time from the libcurl the process already carries. Under Homebrew PHP that is the dylib PHP links; under a distribution PHP, the `.so` PHP or its `curl.so` links; inside a static micro binary (a `venusian build`), the libcurl compiled into it. Headers still come from `pkg-config libcurl`; point it at PHP's libcurl so the headers match (`install-macos.sh` derives it from `otool -L $PHP_BIN`).[^install] Don't use `curl-config`.

Measured 2026-10-08 on the Pi 5: a `pcurl.so` that linked `libcurl.so.4` carried versioned references (`curl_multi_socket_action@CURL_OPENSSL_4`). Inside a static glibc micro runtime, those bound to the system `.so` while the `CURLM*` came from the runtime's own libcurl, and the first `curlMultiSocketAction` segfaulted inside `/lib/aarch64-linux-gnu/libcurl.so.4`. Built without the link, the references are unversioned and bind to the runtime's libcurl.

[^install]: libcurl resolution
