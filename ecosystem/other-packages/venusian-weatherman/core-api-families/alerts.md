# Alerts

Active alerts, the full alert collection, one alert, the active count, and event types.

## Overview

| Method | Path | Returns |
|--------|------|---------|
| `active()` | `GET /alerts/active` | `AlertPage` |
| `collection()` | `GET /alerts` | `AlertPage` |
| `at($latitude, $longitude)` | `GET /alerts/active?point=` | `AlertPage` |
| `area($code)` | `GET /alerts/active/area/{area}` | `AlertPage` |
| `zone($id)` | `GET /alerts/active/zone/{zoneId}` | `AlertPage` |
| `region(MarineRegion)` | `GET /alerts/active/region/{region}` | `AlertPage` |
| `find($id)` | `GET /alerts/{id}` | `Alert` |
| `count()` | `GET /alerts/active/count` | `AlertCount` |
| `types()` | `GET /alerts/types` | `Collection` of event names |

`point` is incompatible with `area`, `region`, `region_type`, and `zone`. Combining them is an NWS 400, which surfaces as `WeathermanException` with `status()` 400.[^service][^openapi]

A zone id must match the OpenAPI UGC pattern (`CAZ006`). An area code is two letters. The alert id is placed on the path with its colons intact.

## Query casing

`status` and `message_type` must be lowercase (`actual`, `alert`, `update`, `cancel`). `severity`, `urgency`, and `certainty` must be title case (`Moderate`, `Expected`, `Likely`). `with('status', AlertStatus::ACTUAL)` still sends `actual`. `AlertQueryStatus` and `AlertQueryMessageType` are the query enums. `Ack` and `Error` appear on documents and are not query values.[^openapi]

## Documents

`Alert` stores the CAP strings and `knownStatus()`, `knownMessageType()`, `knownSeverity()`, `knownUrgency()`, and `knownCertainty()`. An unrecognized value stays on the string property and the known-method returns null.[^alert]

`AlertPage::next()` follows `pagination.next` when the page has alerts. An empty page returns null even if `pagination.next` is set.

[^service]: AlertsAPIService
[^alert]: Alert
[^openapi]: weather.gov API OpenAPI 3.11.0
