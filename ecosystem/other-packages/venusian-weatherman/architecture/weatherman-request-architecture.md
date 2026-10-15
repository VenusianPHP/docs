# Weatherman request architecture

Shared builder, DTO, and NwsURL pattern every core weather.gov family inherits.

## Overview

The public surface is `nws()` → `NwsClient` → a typed `*APIService` → `PendingNwsRequest`. Services never hard-code the host; they pass [`NwsURL::API`](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-api-coverage) into `pending()`.[^urls][^service]

`PendingNwsRequest` carries the endpoint path, query params, extra headers, a namespaced call name (`weatherman.<family>.<endpoint>`), and a hydrator (a DTO class-string or a closure). Fluent `with()` / `__call` add query params. `header()` adds a header such as `Feature-Flags`. `get()` blocks and hydrates; `async()` returns a loop promise of the same value. See the [async lane](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-async-lane).[^pending]

Every request sends `User-Agent` and `Accept: application/geo+json`. There is no API key.[^pending]

## Links

NWS documents are hypermedia. A `Point` stores the forecast, hourly, and observation-station URLs from the payload, and `forecast()` / `hourly()` / `stations()` return a new `PendingNwsRequest` for that absolute URL. `AlertPage::next()` and `StationPage::next()` do the same with `pagination.next`. The client that hydrated the DTO is required; `fromArray()` without it throws `WeathermanException::followUnavailable()`. A missing URL throws `WeathermanException::missingLink()`.[^pending]

`/points/{latitude},{longitude}/stations` responds 301. The point's `observationStations` property is already the gridpoint stations URL, and that is the one `stations()` requests.

## DTOs

DTOs are `final readonly` classes. They implement `HydratesFromArray::fromArray()`.[^hydrator] GeoJSON features keep their fields under `properties`; hydrators unwrap that object. List payloads become a `Voyager\NutsAndBolts\Collection` of DTOs; a FeatureCollection is one page DTO whose features are the collection. Shared coercion lives in `HydratesNwsData`.

`QuantitativeValue` is the measurement object (`value`, `min_value`, `max_value`, `unit_code`, `quality_control`). `knownQuality()` maps the MADIS flag onto `QualityControl` and returns null for an unknown flag, leaving the raw string in place.

Closed value sets are string-backed enums with FULLY UPPERCASE cases. There are no class constants. `ForecastOffice` is the OpenAPI 3.11.0 office list.[^openapi]

Query casing is not the document casing for two filters. `status` and `message_type` are lowercase on the wire (`actual`, `alert`). `severity`, `urgency`, and `certainty` stay title case (`Moderate`). `PendingNwsRequest` lowercases `AlertStatus` and `AlertMessageType` so either the document enum or the query enum sends the accepted form.[^pending][^openapi]

## Schema

| Piece | Role |
|-------|------|
| `NwsURL` | Only place the weather.gov host literal may live |
| `NwsApiService` | Shared `pending()` / `query()` for every family |
| `PendingNwsRequest` | URL + query + headers + hydrator; `get()` / `async()` |
| `HydratesFromArray` | `fromArray(array $data): static` |

[^pending]: PendingNwsRequest
[^service]: NwsApiService
[^hydrator]: HydratesFromArray
[^urls]: NwsURL host catalog
[^openapi]: weather.gov API OpenAPI 3.11.0
