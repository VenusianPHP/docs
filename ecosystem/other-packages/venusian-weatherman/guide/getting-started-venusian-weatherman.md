# Getting started — Venusian Weatherman

How a Venusian sketch reaches api.weather.gov through nws(), NwsClient, a per-API service, and PendingNwsRequest.

## Overview

`nws()` resolves `app('nws')`, the `NwsClient` singleton. The service provider registers that client and merges `config/nws.php` (`user_agent` from `NWS_USER_AGENT`).[^nws-helper][^provider]

api.weather.gov rejects a request with no User-Agent. The config default identifies this library. An application sets `NWS_USER_AGENT` to its own name and a contact URL or email. A client constructed with an empty agent, and no config value, throws `WeathermanException` before the request is sent.[^config]

A sketch calls a per-API accessor (`points()`, `forecast()`, `alerts()`, …) and then a builder method. The builder returns a [`PendingNwsRequest`](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-request-architecture). `get()` is synchronous; `async()` follows the [async lane](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-async-lane).[^nws-client]

Deferred families (`aviation()`, `radar()`, …) throw [`NotYetSupportedException`](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/deferred/deferred-weathergov-apis) until those leaves exist.

## Related

* [Architecture](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-request-architecture) — the builder/DTO/enum pattern.
* [API coverage](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-api-coverage) — which families ship and which are stubs.

[^nws-helper]: nws() helper
[^nws-client]: NwsClient accessors
[^provider]: WeathermanServiceProvider
[^config]: nws.user_agent config
