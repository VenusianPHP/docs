# Observations

The latest observation at a station. History and a single timestamp are deferred.

## Overview

`observations()->latest($station_id, ?bool $require_qc = null)` requests `GET /stations/{stationId}/observations/latest`. `require_qc` is sent as `true` or `false` when passed.[^service][^openapi]

`Observation` hydrates the quantitative readings, cloud layers, present weather, the raw METAR, and the text description. `temperature->knownQuality()` maps the MADIS flag. `station()` follows the station URL back to a [station](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/core-api-families/stations).[^observation]

## Deferred on this service

| Method | OpenAPI path |
|--------|----------------|
| `list($station_id)` | `GET /stations/{stationId}/observations` |
| `atTime($station_id, $time)` | `GET /stations/{stationId}/observations/{time}` |

Both throw `NotYetSupportedException`. The station id is still validated, so a bad id throws `InvalidArgumentException` first.

[^service]: ObservationsAPIService
[^observation]: Observation
[^openapi]: weather.gov API OpenAPI 3.11.0
