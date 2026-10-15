# Deferred weather.gov APIs

Aviation, glossary, raw gridpoint data, icons, thumbnails, offices, radar, radio, products, zones, and TAFs.

## Overview

These families are exposed as `NwsClient` accessors, but they have no builders, DTOs, or fixtures yet. Constructing the stub (or calling the accessor) throws `NotYetSupportedException::forApi()`.[^exception][^client]

## Stubs

| Folder | Class | Accessor | Label |
|--------|-------|----------|-------|
| `src/Aviation` | `AviationAPIService` | `aviation()` | Aviation |
| `src/Glossary` | `GlossaryAPIService` | `glossary()` | Glossary |
| `src/Gridpoints` | `GridpointAPIService` | `gridpoints()` | Gridpoint data |
| `src/Icons` | `IconsAPIService` | `icons()` | Icons |
| `src/Thumbnails` | `ThumbnailsAPIService` | `thumbnails()` | Satellite thumbnails |
| `src/Offices` | `OfficesAPIService` | `offices()` | Offices |
| `src/Radar` | `RadarAPIService` | `radar()` | Radar |
| `src/Radio` | `RadioAPIService` | `radio()` | NOAA Weather Radio |
| `src/Products` | `ProductsAPIService` | `products()` | Products |
| `src/Zones` | `ZonesAPIService` | `zones()` | Zones |
| `src/Tafs` | `TafsAPIService` | `tafs()` | TAFs |

`observations()->list()` and `observations()->atTime()` throw from the live observations service. They are not separate accessors.[^observations]

`gridpoints()` is only the raw quantitative grid document. The narrative forecast and the gridpoint station list are core. See [API coverage](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-api-coverage).[^coverage]

When a leaf is implemented, replace the constructor throw with a real `NwsApiService`, add fixtures under `tests/Fixtures/<Name>/`, and move the row from Deferred to Core in [API coverage](/docs/{{version}}/ecosystem/other-packages/venusian-weatherman/architecture/weatherman-api-coverage).

[^exception]: NotYetSupportedException
[^client]: NwsClient deferred accessors
[^coverage]: API coverage table
[^observations]: Deferred observation methods
