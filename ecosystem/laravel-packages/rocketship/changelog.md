# Changelog

What changed in this package, newest first.

### v0.10.0

First release. Rocketship is Laravel Octane v2.22.0 with:

* **A server registry.** `Octane::registerServer()` adds a server, or replaces one, from any service provider. Every Octane command runs through the registered driver, and `octane:install` offers it. See [adding a server](/docs/{{version}}/ecosystem/laravel-packages/rocketship/guide/adding-a-server).
* **The native server.** An HTTP/1.1 server written in PHP on ext-epoll (Linux) or ext-kqueue (macOS), with ext-posi. Workers are threads on a ZTS PHP with ext-parallel, or forked processes. Keep-alive, pipelining, chunked bodies, streamed responses, multipart uploads, TLS, static files, `max_requests`, `max_execution_time` with `408`, graceful reload and stop, and `--watch`. Started with `octane:start --server=native` or `octane:native --mode=threads|processes`. See [the native server](/docs/{{version}}/ecosystem/laravel-packages/rocketship/guide/native-server).
* **Benchmarks.** PHP 8.4 NTS and ZTS rounds against Swoole, RoadRunner and FrankenPHP, with the harness and raw data: [BENCHMARKS.md](https://github.com/projectsaturnstudios/rocketship/blob/main/BENCHMARKS.md).

Native has no task workers, ticks or Swoole tables yet.
