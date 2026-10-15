# Getting started — Venusian Stargazer

How a Venusian sketch reaches NASA through nasa(), NasaClient, a per-API service, and PendingNasaRequest.

## Overview

`nasa()` resolves `app('nasa')`, the `NasaClient` singleton. The service provider registers that client and merges `config/nasa.php` (`api_key` from `NASA_API_KEY`, default `DEMO_KEY`).[^nasa-helper][^provider]

A sketch calls a per-API accessor (`donki()`, `eonet()`, `imageLibrary()`, …) and then a builder method. The builder returns a [`PendingNasaRequest`](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-request-architecture). `get()` is synchronous; `async()` follows the [async lane](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-async-lane).[^nasa-client]

Deferred hosts (`trek()`, `exoplanet()`, …) throw [`NotYetSupportedException`](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) until those leaves exist.

## Related

* [Architecture](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-request-architecture) — the builder/DTO/enum pattern.
* [API coverage](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-api-coverage) — which families ship and which are stubs.

[^nasa-helper]: nasa() helper
[^nasa-client]: NasaClient accessors
[^provider]: StargazerServiceProvider
