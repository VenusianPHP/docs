# Deployment

Run `php computer serve` behind nginx, keep it running, or serve through PHP-FPM instead.

## Introduction

There are two ways to put a serve application in front of the internet. `php computer serve` is a long-running server that boots the application once; put a reverse proxy such as nginx in front of it for TLS, static files and the public port. Or serve through PHP-FPM with the `public/index.php` front controller, which boots the application on every request, as a classic PHP deployment does.

<a id="behind-nginx"></a>
## Behind nginx

Run the server on a local port and let nginx proxy to it:

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    root /srv/example.com/public;

    location / {
        try_files $uri @serve;
    }

    location @serve {
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

nginx serves the files under `public/` itself and passes everything else to the application. With nginx doing that, you can set `static` to `false` in `config/serve.php`. Or leave it on and drop the `try_files`, and the server answers the files under `public/` itself; see [Static Files](/docs/{{version}}/serve/serving#static-files).

<a id="https-and-proxy-headers"></a>
### HTTPS and Proxy Headers

The server only sees the plain connection from nginx. So that URLs, redirects and secure cookies use `https`, either start it with `--https` (or `SERVE_HTTPS=true`), which marks every request as HTTPS, or trust the proxy's forwarded headers, which also gives the application the client's address:

```php
use Mariner\Http\Middleware\TrustProxies;

TrustProxies::at('127.0.0.1');
```

<a id="health-checks"></a>
### Health Checks

Point the load balancer's or orchestrator's health check at `/up`. Under `php computer serve`, the server answers it `200 OK` without running a request through the application; set `health` in `config/serve.php` to another path, or `null` to turn it off. Behind PHP-FPM there is no server in front of the application, so the `/up` route that [install:web](/docs/{{version}}/serve/installation#installing-the-web-files) puts in `routes/web.php` answers it instead, through the application.

<a id="keeping-the-server-running"></a>
## Keeping the Server Running

Run `php computer serve` under a process manager such as systemd or Supervisor so it starts with the machine and comes back if it exits. Stop it with `SIGTERM`: it stops taking connections and answers the requests in flight for up to `drain_timeout` seconds before exiting, so give the process manager a stop timeout longer than that.

On Linux, `--workers` runs several workers on the port with their own supervisor, which restarts a worker that dies; see [Workers](/docs/{{version}}/serve/serving#workers).

<a id="deploying-code"></a>
### Deploying New Code

The server loads your code once, so a deploy needs a restart for the new code to run. Take the application [down](/docs/{{version}}/serve/maintenance-mode) first if the deploy changes the database, then restart the server and bring the application back up.

<a id="php-fpm"></a>
## Behind PHP-FPM

To serve through PHP-FPM instead, point the web server's document root at `public/` and send requests to `public/index.php`, which [install:web](/docs/{{version}}/serve/installation#installing-the-web-files) publishes. Each request then boots the application and runs once through the same HTTP kernel; there is no long-running process to restart after a deploy. In maintenance mode, `public/index.php` answers from the prerendered page without booting the application; see [Behind PHP-FPM](/docs/{{version}}/serve/maintenance-mode#the-front-controller).
