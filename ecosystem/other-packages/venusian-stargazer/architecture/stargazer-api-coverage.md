# Stargazer API coverage

Core versus deferred status for every NasaURL host Stargazer catalogues. Every core family has an async lane.

## Overview

`NasaURL` holds sixteen base URLs. Ten core families have builders, captured fixtures, Pest coverage, and an async lane. Six deferred families exist as stubs that throw `NotYetSupportedException`.[^urls][^api-nasa][^seam]

## Core

Every core family has an async lane: `async()` fulfils with what `get()` returns.

| Family | `NasaURL` | Accessor | Async | Concept |
|--------|-----------|----------|-------|---------|
| DONKI | `DONKI` | `donki()` | promise | [DONKI](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/donki) |
| NeoWs | `NEOWS` | `neows()` | promise | [NeoWs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/neows) |
| EONET | `EONET` (v3) | `eonet()` | promise | [EONET](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/eonet) |
| APOD | `APOD` | `apod()` | promise | [APOD](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/apod) |
| EPIC | `EPIC` | `epic()` | promise | [EPIC](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/epic) |
| InSight | `INSIGHT` | `insight()` | promise | [InSight](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/insight) |
| TLE | `TLE` | `tle()` | promise | [TLE](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/tle) |
| TechTransfer | `TECHTRANSFER` | `techtransfer()` | promise | [TechTransfer](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/techtransfer) |
| Image Library | `IMAGE_LIBRARY` | `imageLibrary()` | promise | [Image and Video Library](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/image-and-video-library) |
| GIBS | `GIBS` | `gibs()` | promise | [GIBS](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/core-api-families/gibs) |

## Deferred

| Family | `NasaURL` | Accessor | Notes |
|--------|-----------|----------|-------|
| Trek WMTS | `TREK_WMTS` | `trek()` | See [deferred APIs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) |
| Exoplanet Archive | `EXOPLANET` | `exoplanet()` | See [deferred APIs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) |
| Open Science | `OPEN_SCIENCE` | `openScience()` | See [deferred APIs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) |
| Satellite Situation Center | `SATELLITE_SITUATION_CENTER` | `ssc()` | See [deferred APIs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) |
| SSD/CNEOS | `SSD_CNEOS` | `ssd()` | See [deferred APIs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) |
| Techport | `TECHPORT` | `techport()` | See [deferred APIs](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/deferred/deferred-nasa-apis) |

EONET is v3 (`/api/v3`), not the older v2.1 host. GIBS, Image Library, EONET, TLE, DONKI, APOD (science.nasa.gov's `apod-basic`), and TechTransfer (`technology.nasa.gov`) are not `api.nasa.gov` hosts and do not receive `api_key`.

TechTransfer `imageUrl` follow and Image Library `GET /album/{name}` are not in this pass.

[^urls]: NasaURL enum
[^api-nasa]: NASA Open APIs catalog
[^seam]: Async lane
