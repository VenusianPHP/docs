# The native server

An HTTP/1.1 server written in PHP, on ext-epoll (Linux) or ext-kqueue (macOS) with ext-posi. Octane's fourth server.

```bash
php artisan octane:start --server=native
```

`octane:start` takes Octane's options: `--host`, `--port`, `--workers` (default: CPU count), `--max-requests` (default: 500), `--watch` and `--poll`.

### Modes

Native picks its mode when it starts. `auto`, the default, chooses threads when this PHP can run them and processes when it can't.

| Mode | Needs | Workers |
|---|---|---|
| `threads` | ZTS PHP, ext-parallel, ext-posi, no ext-swoole loaded | Threads in one process. The benchmark leader. |
| `processes` | Any PHP with ext-pcntl and ext-posix | Forked processes. |

To force one:

```bash
OCTANE_NATIVE_MODE=processes php artisan octane:start --server=native
php artisan octane:native --mode=threads
```

`octane:native` is the command `octane:start --server=native` runs, as `octane:swoole` is for Swoole.

### What it does

* HTTP/1.1 with keep-alive, pipelining, chunked bodies, `100 Continue`, streamed responses and multipart uploads.
* TLS, when you give it a certificate.
* Static files from `public/`, with ETag, `Last-Modified`, `304` and byte ranges.
* `max_requests`, and `max_execution_time` with a `408` and a fresh worker, as on Swoole.
* `octane:reload` without dropping a request, `octane:stop` with a drain, and a replacement for a worker that dies.

### What it doesn't do yet

No task workers, ticks or Swoole tables. `Octane::concurrently()` runs its tasks in the request, ticks don't fire, and `Octane::table()` and the `octane` cache behave as they do on RoadRunner and FrankenPHP. No HTTP/2. Where a behaviour question comes up, the answer is what Octane's Swoole server does.

### Config

The `native` section of `config/octane.php`:

| Key | Default | |
|---|---|---|
| `mode` | `env('OCTANE_NATIVE_MODE', 'auto')` | `auto`, `threads` or `processes`. |
| `tls.cert`, `tls.key` | `OCTANE_NATIVE_TLS_CERT`, `OCTANE_NATIVE_TLS_KEY` | PEM paths. The key can live in the certificate file. |
| `drain_timeout` | `30` | Seconds a stop or reload waits for requests in flight. |
| `keepalive_timeout` | `5` | Seconds an idle keep-alive connection stays open. |
| `header_timeout` | `30` | Seconds a client has to send a request head, answered `408` after. |
| `max_body` | `10485760` | Largest request body in bytes, answered `413` past it. |
| `php_options` | `[]` | Extra arguments for the PHP that runs the server, such as `-d` settings. |

### Production

Put nginx or another proxy in front, as with Octane's other servers. Native is a network server: it parses HTTP from clients, serves files from `public/` and terminates TLS when given a certificate. The model and how to report a vulnerability are in [SECURITY.md](https://github.com/projectsaturnstudios/rocketship/blob/main/SECURITY.md).
