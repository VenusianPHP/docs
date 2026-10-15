# Deferred NASA APIs

Trek WMTS, Exoplanet Archive, Open Science, SSC, SSD/CNEOS, and Techport stubs.

## Overview

These six hosts are catalogued on `NasaURL` and exposed as `NasaClient` accessors, but they have no builders, DTOs, or fixtures yet. Constructing the stub (or calling the accessor) throws `NotYetSupportedException::forApi()`.[^exception][^urls]

## Stubs

| Folder | Class | Accessor | `NasaURL` |
|--------|-------|----------|-----------|
| `src/Trek` | `TrekWmtsAPIService` | `trek()` | `TREK_WMTS` |
| `src/Exoplanet` | `ExoplanetArchive` | `exoplanet()` | `EXOPLANET` |
| `src/OpenScience` | `OpenScienceAPIService` | `openScience()` | `OPEN_SCIENCE` |
| `src/SSC` | `SscAPIService` | `ssc()` | `SATELLITE_SITUATION_CENTER` |
| `src/SSD` | `SsdCneosAPIService` | `ssd()` | `SSD_CNEOS` |
| `src/Techport` | `TechportAPIService` | `techport()` | `TECHPORT` |

When a leaf is implemented, replace the constructor throw with a real `NasaApiService`, add fixtures under `tests/Fixtures/<Name>/`, and move the row from Deferred to Core in [API coverage](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-api-coverage).[^coverage]

[^exception]: NotYetSupportedException
[^urls]: NasaURL deferred cases
[^coverage]: API coverage table
