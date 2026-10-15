# TLE

Two-line element satellite catalog — collection, search, and NORAD id lookup; page-or-single family.

## Overview

`nasa()->tle()` uses `NasaURL::TLE`. The host is not `api.nasa.gov`, so no `api_key` is sent.[^service]

## Endpoints

| Builder | Path | DTO |
|---------|------|-----|
| `collection()` | `tle` | `TleCollection` |
| `search($query)` | `tle?search=` | `TleCollection` |
| `satellite($id)` | `tle/{id}` | `TleRecord` |

`TleCollection` carries Hydra-style `@context` / `@id` / `@type`, paging parameters, and a `member` list of `TleRecord`.

## Async

`async()` fulfils with `TleCollection` or `TleRecord`. A non-success rejects with `StargazerException`.[^service]

## Related

* [Async lane](/docs/{{version}}/ecosystem/other-packages/venusian-stargazer/architecture/stargazer-async-lane) — page-or-single payload.

[^service]: TleAPIService
