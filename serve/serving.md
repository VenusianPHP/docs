# Serving Your Application

Run your application with `php computer serve`: an HTTP/1.1 server on the application's own event loop, configured by `config/serve.php`.

## Introduction

`php computer serve` serves your application over HTTP/1.1 without a separate web server or PHP-FPM. The application boots once; each request then runs in its own task on the [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop), through the same HTTP kernel, middleware and exception rendering a front controller would use. A request that waits on something offloaded, such as a [query on a worker pool](/docs/{{version}}/framework/database/event-loop), lets the loop take other connections in the meantime.

```shell
php computer serve
```

The server listens on `127.0.0.1:8020` by default. It prints one line per request when the console is a terminal, or with `-v`; `--quiet` silences them.

<a id="command-options"></a>
## Command Options

Each option overrides the matching `config/serve.php` value:

| Option | Config key | Description |
| --- | --- | --- |
| `--host=` | `host` | The address to listen on. |
| `--port=` | `port` | The port to listen on. |
| `--max-in-flight=` | `max_in_flight` | How many requests one worker handles at once. |
| `--workers=` | `workers` | Worker processes sharing the port. Above 1 needs Linux. |
| `--driver=` | | How workers run: `process`, `thread`, or `auto` (the default). See [Workers](#workers). |
| `--https` | `https` | Serve as behind a proxy that terminates TLS. |

<a id="configuration"></a>
## Configuration

All of the server's settings live in `config/serve.php`:

| Key | Default | Description |
| --- | --- | --- |
| `host` | `127.0.0.1` (`SERVE_HOST`) | The address to listen on. |
| `port` | `8020` (`SERVE_PORT`) | The port to listen on. |
| `max_in_flight` | `10` (`SERVE_MAX_IN_FLIGHT`) | Requests one worker handles at once, each in its own loop task, so a long-lived stream or a request waiting on another doesn't hold up the rest. Set it to 1 to answer one request at a time. |
| `workers` | `1` (`SERVE_WORKERS`) | Worker processes sharing the port, balanced by the kernel. Values above 1 are refused on anything but Linux. |
| `https` | `false` (`SERVE_HTTPS`) | Mark every request as HTTPS, for a proxy that terminates TLS in front of the server. |
| `health` | `/up` | A path answered `200 OK` without booting a request through the application. `null` turns it off. |
| `static` | `true` | Answer `GET` and `HEAD` for real files under `public/` before the application; see [Static Files](#static-files). `false` sends every path to the application. |
| `header_timeout` | `30.0` | Seconds for a request's line and headers to arrive, from its first byte. |
| `body_timeout` | `30.0` | Seconds a request body may go without a byte arriving. A slow upload that keeps arriving is never cut off. |
| `write_timeout` | `30.0` | Seconds a response may go without a byte leaving. A client that stops reading is disconnected. |
| `max_connections` | `null` (`SERVE_MAX_CONNECTIONS`) | Connections held at once; more wait in the system's accept backlog. `null` means 1024, or fewer when the process's open-file limit leaves room for fewer. |
| `max_buffered` | `1048576` | Bytes of answers queued for one connection beyond which its next requests are not read until the client catches up. |
| `idle_timeout` | `60.0` | Seconds a keep-alive connection may sit between requests. |
| `drain_timeout` | `30.0` | Seconds a stop waits for the requests in flight. |
| `limits.request_line` | `8192` | Bytes in the request line. |
| `limits.header_bytes` | `16384` | Bytes in all the request headers together. |
| `limits.headers` | `100` | Number of request header fields. |
| `limits.body` | `10485760` | Bytes in a request body. |

<a id="limits-and-timeouts"></a>
### Limits and Timeouts

A request that breaks a limit is answered with the status for it, and its connection is closed, since what follows it cannot be trusted to start a request:

| Limit | Status |
| --- | --- |
| `limits.request_line` | `414 URI Too Long` |
| `limits.header_bytes`, `limits.headers` | `431 Request Header Fields Too Large` |
| `limits.body` | `413 Content Too Large` |
| `header_timeout`, `body_timeout` | `408 Request Timeout` |

Malformed requests are refused the same way: a bare line feed, a missing or repeated `Host` header on HTTP/1.1, both `Content-Length` and `Transfer-Encoding`, a transfer coding other than `chunked`, or a protocol other than HTTP/1.0 and HTTP/1.1. These are the framing ambiguities request smuggling relies on.

<a id="max-connections"></a>
### Max Connections

Each connection holds an open file. When you set `max_connections`, the server checks it against the process's soft open-file limit, keeping 64 files for the application's own use, and refuses to start if the setting is more than the process can open:

```shell
ulimit -n 4096
SERVE_MAX_CONNECTIONS=2000 php computer serve
```

<a id="static-files"></a>
### Static Files

With `static` on, the server answers `GET` and `HEAD` requests for files that exist under `public/` itself, the way a web server in front of PHP would: your CSS, JavaScript, images and downloads never reach the application. It sets the content type from the file's extension and honours `Range` requests, so media can seek and downloads can resume.

Everything else goes to the application: any path ending in `.php`, a directory, a path that does not name a file, and any path that would resolve outside `public/`, through `..` or a symlink pointing elsewhere. Set `static` to `false` when something in front of the server already serves `public/`, and every request goes to the application.

<a id="stopping-the-server"></a>
## Stopping the Server

The first `Ctrl-C` or `SIGTERM` stops taking new connections, closes the idle ones, and answers the requests already in flight, waiting up to `drain_timeout` seconds. A second `Ctrl-C` stops at once.

<a id="workers"></a>
## Workers

One worker serves on one event loop. To use more cores, run several workers on the same port:

```shell
php computer serve --workers=4
```

Workers share the port through `SO_REUSEPORT`, which balances connections between them in the kernel. This needs Linux; on other systems the command refuses, and you run one worker per port behind a proxy instead.

A supervisor starts the workers, prefixes each one's console lines with its number, and restarts a worker that dies, after a pause that grows with each restart. A worker that dies more than 5 times in 60 seconds is given up on: the supervisor stops the others and exits with status 1, saying why. A stop signal is passed to every worker, so each drains its own requests.

<a id="worker-drivers"></a>
### Worker Drivers

The `--driver` option chooses how workers run:

| Driver | Workers |
| --- | --- |
| `process` | One PHP process each. |
| `thread` | One thread each in a single process, using `ext-parallel` on a ZTS build of PHP. |
| `auto` | Threads where this PHP can run them, processes otherwise. The command says which it chose and why. |

> [!WARNING]
> Thread workers share one process. A PHP fatal error in any of them ends the whole server, every worker with it. Process workers contain a fatal error to the worker that hit it, which the supervisor then restarts.

<a id="requests-and-state"></a>
## Requests and State

The application boots once and serves many requests, so nothing one request changes may reach the next. Each request runs in a fresh scope of the [service container](/docs/{{version}}/framework/architecture-concepts/container): the services the application keeps for the whole process hold configuration only, and everything that belongs to one request lives in a scoped object each request gets new:

| Service | Its per-request state |
| --- | --- |
| `cookie` | `CookieQueue` |
| `view`, `Vite` | `RenderState`, `ViteState` |
| `session` | `SessionState`, `session.store` |
| `auth` | `GuardState`, `auth.driver` |
| `translator` | `LocaleState` |
| `request`, `url`, `redirect` | scoped themselves |

The same holds when two requests are in flight at once: a request suspended on the loop never sees another's request, session, user or locale. When you write your own services, keep request data in scoped bindings, not in a singleton's properties or a static.
