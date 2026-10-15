# Points

Latitude,longitude metadata from /points, including the forecast, hourly, and station links NWS publishes.

## Overview

`points()->at($latitude, $longitude)` requests `GET /points/{latitude},{longitude}`. Coordinates are rounded to four decimal places. A latitude outside -90..90 or a longitude outside -180..180 throws `InvalidArgumentException` before the request.[^service][^openapi]

The document is a GeoJSON Feature. `Point` reads `properties` and the feature `geometry`. `knownKind()` is `PointKind::LAND` or `MARINE`.[^point]

## Links

| Method | Property followed | Result |
|--------|-------------------|--------|
| `forecast()` | `forecast` | [Forecast](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/forecast) |
| `hourly()` | `forecastHourly` | [Forecast](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/forecast) |
| `stations()` | `observationStations` | [Station page](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/stations) |

`/points/{latitude},{longitude}/stations` responds 301 with a problem document. `stations()` does not call that path. It calls the `observationStations` URL, which is `/gridpoints/{office}/{x},{y}/stations`.[^point]

`relative_location`, `astronomical_data`, and `radio` are hydrated when present. Radio playback itself is the deferred [radio](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/deferred/deferred-weathergov-apis) family.

[^service]: PointsAPIService
[^point]: Point
[^openapi]: weather.gov API OpenAPI 3.11.0
