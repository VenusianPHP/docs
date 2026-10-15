# InSight

Mars InSight lander weather feed (JSON 1.0) — single-object family.

## Overview

`nasa()->insight()->weather()` calls `NasaURL::INSIGHT` with `feedtype=json` and `ver=1.0`. The payload hydrates `InsightWeather`, which owns per-sol summaries, sensor validity, and wind compass points.[^service]

NASA retired the live InSight feed; the suite replays a captured fixture rather than a live DEMO_KEY call. Host is `api.nasa.gov`, so `api_key` is still appended.

## Async

`async()` on `weather()` fulfils with `InsightWeather`. A non-success rejects with `StargazerException`.[^service]

## Related

* [Async lane](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-async-lane) — single-object payload.

[^service]: InsightAPIService
