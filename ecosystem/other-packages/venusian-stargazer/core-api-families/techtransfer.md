# TechTransfer

NASA TechTransfer patent, software, and spinoff catalogs — one-page-DTO family.

## Overview

`nasa()->techtransfer()` uses `NasaURL::TECHTRANSFER`. Each catalog method takes a search string and hydrates `TechTransferPage` (a count/total/page wrapper around `TechTransferRecord` rows).[^service]

## Endpoints

| Builder | Path | Query key |
|---------|------|-----------|
| `patent($query)` | `patent` | `patent` |
| `software($query)` | `software` | `software` |
| `spinoff($query)` | `spinoff` | `Spinoff` |

`TechTransferCatalog` is the closed set. `NasaURL::TECHTRANSFER` is `https://technology.nasa.gov/api/api` (api.nasa.gov/techtransfer 302s there and drops the path), so no `api_key` is sent. Records arrive as positional arrays and are mapped field-by-field in `TechTransferRecord::fromArray()`.

## Async

`async()` on every catalog builder fulfils with `TechTransferPage`. A non-success rejects with `StargazerException`. `imageUrl` follow is not in this pass.[^service]

## Related

* [Async lane](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-async-lane) — one-page-DTO payload.

[^service]: TechTransferAPIService
