# Changelog

What changed in this package, newest first.

### 2026-10-04
* **Creation**: `projectsaturnstudios/venusian-weatherman` 0.10.0 — National Weather Service client on the Stargazer seam (`nws()`, `NwsClient`, `PendingNwsRequest`, `get()` / `async()`). Core families are [points](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/points), [forecast](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/forecast), [alerts](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/alerts), [stations](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/stations), and [observations](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/observations). The rest of api.weather.gov OpenAPI 3.11.0 is catalogued as [deferred stubs](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/deferred/deferred-weathergov-apis). An empty alert or station page does not expose `next()`, even when `pagination.next` is still set.
