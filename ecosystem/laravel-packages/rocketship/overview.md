# Overview

<div align="center" id="header">

<h2>ProjectSaturn Rocketship</h2>
<h4>A drop-in replacement for Laravel Octane, with a server written in PHP</h4>

[![CI](https://img.shields.io/github/actions/workflow/status/projectsaturnstudios/rocketship/tests.yml?style=flat-square&label=CI)](https://github.com/projectsaturnstudios/rocketship/actions/workflows/tests.yml)
[![Packagist](https://img.shields.io/packagist/v/projectsaturnstudios/rocketship?style=flat-square)](https://packagist.org/packages/projectsaturnstudios/rocketship)
[![PHP](https://img.shields.io/packagist/dependency-v/projectsaturnstudios/rocketship/php?style=flat-square&label=PHP)](https://packagist.org/packages/projectsaturnstudios/rocketship)
[![Laravel](https://img.shields.io/badge/Laravel-10%20%7C%2011%20%7C%2012%20%7C%2013-ff2d20?style=flat-square&logo=laravel&logoColor=white)](https://laravel.com/docs/octane)
[![License](https://img.shields.io/github/license/projectsaturnstudios/rocketship?style=flat-square)](https://github.com/projectsaturnstudios/rocketship/blob/main/LICENSE.md)
[![Loop](https://img.shields.io/badge/loop-epoll%20%7C%20kqueue-blue?style=flat-square)](#installation)

</div>

Laravel Octane boots your app once and keeps it in memory. To do that it needs an application server from outside PHP: Swoole, a C extension with its own coroutine runtime; RoadRunner, a Go binary talking to PHP workers over pipes; or FrankenPHP, a Go binary with PHP built in.

PHP can serve HTTP itself if it can ask the kernel which sockets are ready. Linux answers with `epoll`, macOS with `kqueue`. PHP never exposed either to userland, so we wrote [ext-epoll](https://github.com/php-io-extensions/epoll), [ext-kqueue](https://github.com/php-io-extensions/kqueue) and [ext-posi](https://github.com/php-io-extensions/posi): the syscalls, one to one, no opinions.

<b>Rocketship is Octane with a fourth server, `native`, built on those extensions.</b> An HTTP/1.1 server written in PHP. Workers are forked processes on any PHP, or threads on a ZTS PHP with ext-parallel. It runs under Octane's own commands, config and events.

Everything else is Octane's own code, forked at [v2.22.0](https://github.com/laravel/octane/tree/v2.22.0) under its MIT license: the `Laravel\Octane` namespace, `config/octane.php`, the `Octane` facade, the listeners, and the Swoole, RoadRunner and FrankenPHP servers. App code doesn't change. Swap the package, choose a server.

### Benchmarks

Measured on a 2 vCPU Graviton2 box, app, nginx and MySQL sharing it, load sent from a second machine, against Octane's three servers with Octane's defaults:

* **PHP 8.4 ZTS, native in threads mode: 9–20% more requests per second than Swoole**, 13–24% more than FrankenPHP, 61–98% more than RoadRunner, on every route and load measured.
* **8–17% less server CPU per request** than whichever of Octane's servers used the least on each route and load.
* **124 MB for the whole server**, against 189 MB for FrankenPHP, 233 MB for RoadRunner and 315 MB for Swoole.
* **PHP 8.4 NTS, native in processes mode: 11–17% more requests per second than Swoole** on the plain, JSON and Blade routes, 2–8% more on the MySQL route.

Where it doesn't win: at 256 connections native's slowest 1% of requests take longer than Swoole's and FrankenPHP's, and FrankenPHP has the shortest tail at every load.

The science is in [BENCHMARKS.md](https://github.com/projectsaturnstudios/rocketship/blob/main/BENCHMARKS.md): the box, every version, the method, every table, the raw data, the harness, and the numbers that went the other way. **[Open the interactive report](https://htmlpreview.github.io/?https://github.com/projectsaturnstudios/rocketship/blob/main/benchmarks/report.html)**: charts for every round, route, load and metric.

### Installation

| | |
|---|---|
| PHP | 8.4.27 or newer on 8.4, 8.5.12 or newer on 8.5. NTS or ZTS. |
| Laravel | 10, 11, 12 or 13, the same as Octane 2.22. |
| Octane's servers | As in Octane: ext-swoole for Swoole, the binaries `octane:install` fetches for RoadRunner and FrankenPHP. |
| Native, both modes | ext-pcntl and ext-posix. [ext-epoll](https://github.com/php-io-extensions/epoll) on Linux or [ext-kqueue](https://github.com/php-io-extensions/kqueue) on macOS. On Linux, [ext-posi](https://github.com/php-io-extensions/posi) 0.10.6 or newer. |
| Native, threads mode | A ZTS PHP with ext-parallel and ext-posi, without ext-swoole loaded in the same PHP. |

```bash
composer require projectsaturnstudios/rocketship
```

Then the extensions for the native server, with [PIE](https://github.com/php/pie), on the machine that runs it:

```bash
sudo pie install php-io-extensions/epoll   # Linux
pie install php-io-extensions/kqueue       # macOS
sudo pie install php-io-extensions/posi
```

Threads mode also wants [ext-parallel](https://github.com/krakjoe/parallel) on a ZTS PHP.

### Where next

* [Migrating from Octane](/docs/{{version}}/ecosystem/laravel-packages/rocketship/guide/migrating-from-octane): the two-command swap and what stays as it was.
* [The native server](/docs/{{version}}/ecosystem/laravel-packages/rocketship/guide/native-server): modes, what it does, what it doesn't yet, config.
* [Adding a server](/docs/{{version}}/ecosystem/laravel-packages/rocketship/guide/adding-a-server): the registry a package plugs into.
* [Changelog](/docs/{{version}}/ecosystem/laravel-packages/rocketship/changelog).

### AI-assisted development

Built with LLM assistance under human direction. Prompts, reviews and architectural decisions were owned by a professional software engineer; the model sped up drafting and exploration, not judgment on APIs, dependency direction or what ships.

### License

MIT. Rocketship is a fork of [Laravel Octane](https://github.com/laravel/octane) by Taylor Otwell and the Laravel contributors, under the same license.
