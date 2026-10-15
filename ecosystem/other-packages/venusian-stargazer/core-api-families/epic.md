# EPIC

DSCOVR Earth Polychromatic Imaging Camera — list-of-rows family with archive link-follow.

## Overview

`nasa()->epic()` uses `NasaURL::EPIC`. Natural and enhanced imagery share `EpicImage`; available-date lists hydrate `EpicAvailableDate`.[^service]

## Endpoints

| Builder | Path | DTO |
|---------|------|-----|
| `natural($date)` | `api/natural` or `api/natural/date/{date}` | `EpicImage` list |
| `enhanced($date)` | `api/enhanced` or `api/enhanced/date/{date}` | `EpicImage` list |
| `naturalAvailable()` | `api/natural/available` | `EpicAvailableDate` list |
| `enhancedAvailable()` | `api/enhanced/available` | `EpicAvailableDate` list |

`EpicImage::archiveUrl()` builds the archive PNG/JPG path from `NasaURL::EPIC` plus `EpicCollection` and `EpicImageType`. Host is `api.nasa.gov`, so `api_key` is appended.

## Async

`async()` fulfils with a list of `EpicImage` or `EpicAvailableDate`. A non-success rejects with `StargazerException`.[^service]

`EpicImage::render()` follows the archive URL and returns `Promise<Response>`. `body()` is the bytes.[^image]

## Related

* [Async lane](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-async-lane) — list-of-rows payload plus DTO link-follow.

[^service]: EpicAPIService
[^image]: EpicImage render
