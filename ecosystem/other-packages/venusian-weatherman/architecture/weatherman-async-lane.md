# Weatherman async lane

get() blocks; async() returns a loop promise of the same DTOs; link followers return another pending request.

## Two lanes, one hydrator

`get()` sends through `app('http')` (or the Factory on `NwsClient`), blocks, hydrates. Non-2xx throws `WeathermanException`; `status()` is the HTTP status (null when no response was involved).[^pending][^exception]

`async()` sends through the same Factory's loop driver and returns `Voyager\Contracts\IOPools\Promise`. Fulfils with what `get()` returns; rejects with what `get()` throws. No loop bound on the Factory → `WeathermanException::loopNotBound()`.[^pending][^exception]

`wait()` on the main stack borrows the loop. Inside `$loop->async()` it suspends the fiber.

## Link follows

Link methods return another `PendingNwsRequest`, not a promise of bytes. Call `get()` or `async()` on that request.

| DTO | Method | Document |
|-----|--------|----------|
| `Point` | `forecast()` | The `forecast` URL, a `Forecast` |
| `Point` | `hourly()` | The `forecastHourly` URL, a `Forecast` |
| `Point` | `stations()` | The `observationStations` URL, a `StationPage` |
| `AlertPage` | `next()` | `pagination.next` when the page has alerts; null on an empty page |
| `StationPage` | `next()` | `pagination.next` when the page has stations or station URLs; null on an empty page |
| `Station` | `latest()` | `observations()->latest()` for its identifier |
| `Observation` | `station()` | The `station` URL, a `Station` |

## Call names

`callName()` is a label only (`weatherman.<family>.<endpoint>`). Nothing coalesces on it.

[^pending]: PendingNwsRequest
[^exception]: WeathermanException
