# Overview

![Tests](https://github.com/projectsaturnstudios/venusian-weatherman/actions/workflows/tests.yml)

[![Tests](https://github.com/projectsaturnstudios/venusian-weatherman/actions/workflows/tests.yml/badge.svg)](https://github.com/projectsaturnstudios/venusian-weatherman/actions/workflows/tests.yml)

The National Weather Service API for [Venusian](https://github.com/VenusianPHP/framework) apps.

```php
$point = nws()->points()->at(38.8894, -77.0352)->get();

echo $point->relative_location->city; // "Washington"

$tonight = $point->forecast()->get()->periods->first();

echo $tonight->short_forecast; // "Chance Rain Showers"
echo $tonight->temperature;    // 60
```

## Requirements

- PHP 8.4 or 8.5
- A Venusian 0.10 app, or standalone `venusian-voyager/http`, `io-pools` and `nuts-and-bolts` 0.10+

## Installation

```bash
composer require projectsaturnstudios/venusian-weatherman
```

After install, call `nws()`.

api.weather.gov refuses a request that does not identify the application. The published config sends a library User-Agent. Set your own in `.env`:

```dotenv
NWS_USER_AGENT="your-app/1.0 (https://example.com; you@example.com)"
```

To publish the config file:

```bash
php computer vendor:publish --tag=nws-config
```

There is no API key. Every request sends `Accept: application/geo+json`.

## Usage

Pick a family, then an endpoint. Nothing is sent until `get()` or `async()`. `get()` blocks and returns a DTO, or a page object whose list is a `Collection`. A non-2xx response throws `WeathermanException`, whose `status()` is the HTTP status. `async()` returns a promise on the event loop that fulfils with what `get()` returns and rejects with what it throws. With no loop bound, `async()` throws `WeathermanException`.

```php
$alerts = nws()->alerts()->area('CA')->get();

echo $alerts->alerts->first()->event; // "Heat Advisory"
```

### On the event loop

```php
nws()->points()->at(38.8894, -77.0352)->async()
    ->then(fn ($point) => $point->forecast()->async())
    ->then(fn ($forecast) => printf("%s\n", $forecast->periods->first()->short_forecast))
    ->error(fn (\Throwable $e) => printf("Forecast failed: %s\n", $e->getMessage()));
```

Two `async()` calls run concurrently. `wait()` resolves each one to its DTOs:

```php
$forecast = nws()->forecast()->grid('LWX', 97, 71)->async();
$latest = nws()->observations()->latest('KDCA')->async();

printf("%s, %s°C\n", $forecast->wait()->periods->first()->name, $latest->wait()->temperature->value);
```

### Query parameters

`with()` adds any parameter the endpoint accepts and returns a new request. `header()` adds a request header the same way.

```php
use ProjectSaturnStudios\Weatherman\Enums\AlertSeverity;
use ProjectSaturnStudios\Weatherman\Enums\ForecastFeatureFlag;
use ProjectSaturnStudios\Weatherman\Enums\ForecastUnits;

$moderate = nws()->alerts()->active()->with('severity', AlertSeverity::MODERATE)->get();

$metric = nws()->forecast()->grid('LWX', 97, 71)
    ->with('units', ForecastUnits::SI)
    ->header('Feature-Flags', ForecastFeatureFlag::FORECAST_TEMPERATURE_QV)
    ->get();
```

`status` and `message_type` go out in lowercase (`actual`, `alert`). `severity`, `urgency`, and `certainty` stay title case (`Moderate`, `Expected`, `Likely`). Passing the document enum `AlertStatus::ACTUAL` still sends `actual`.

### Following links

A point document carries the forecast, hourly forecast, and station URLs NWS wants you to use. Those methods return another pending request, so both lanes stay available:

```php
$point = nws()->points()->at(38.8894, -77.0352)->get();

$forecast = $point->forecast()->get();
$hourly = $point->hourly()->async();
$stations = $point->stations()->get();
```

`/points/{latitude},{longitude}/stations` answers 301. `stations()` follows `observationStations` instead, which is `/gridpoints/{office}/{x},{y}/stations`.

Alert pages and station pages expose `next()` when the page has records and NWS sent `pagination.next`. An empty page returns null, including when the payload still carries `pagination.next`. The gridpoint station list does that on the pages after the last station, and each empty page points at another empty page.

## Supported APIs

| Accessor | API | Endpoints |
|---|---|---|
| `points()` | Point metadata | `at` |
| `forecast()` | Gridpoint narrative forecast | `grid`, `hourly` |
| `alerts()` | Watches, warnings, and advisories | `active`, `collection`, `at`, `area`, `zone`, `region`, `find`, `count`, `types` |
| `stations()` | Observation stations | `index`, `find`, `grid` |
| `observations()` | Latest station observation | `latest` |

A point's `forecast()`, `hourly()`, and `stations()` follow the links on that document. A station's `latest()` loads its latest observation. An observation's `station()` follows its station link.

### Not yet supported

`aviation()`, `glossary()`, `gridpoints()`, `icons()`, `thumbnails()`, `offices()`, `radar()`, `radio()`, `products()`, `zones()`, and `tafs()` exist and throw `NotYetSupportedException`.

`gridpoints()` is the raw quantitative grid. The narrative forecast is `forecast()`. `observations()->list()` and `observations()->atTime()` throw the same exception; `latest()` is implemented.

## API reference

Coordinates are decimal degrees. A point is rounded to four decimal places, which is as much precision as api.weather.gov accepts. Enums live under `ProjectSaturnStudios\Weatherman\Enums`. Forecast offices are `ForecastOffice` (`LWX`, `OKX`, and the rest of the OpenAPI 3.11.0 list). A string office id is accepted and must be one of those cases.

### Points

```php
$point = nws()->points()->at(38.8894, -77.0352)->get();

$point->grid_id;                      // "LWX"
$point->grid_x;                       // 97
$point->grid_y;                       // 71
$point->relative_location->city;      // "Washington"
$point->knownKind()->value;           // "land"
```

| Method | Returns |
|---|---|
| `at(float $latitude, float $longitude)` | `Point` |

`Point` has `id`, `kind`, `cwa`, `forecast_office`, `grid_id`, `grid_x`, `grid_y`, the four follow URLs (`forecast_url`, `hourly_url`, `grid_url`, `stations_url`), `forecast_zone`, `county`, `fire_weather_zone`, `time_zone`, `radar_station`, `relative_location`, `astronomical_data`, `radio`, and `geometry`. `geometry->latitude()` and `longitude()` read a GeoJSON Point. A latitude outside -90 to 90, or a longitude outside -180 to 180, throws `InvalidArgumentException` before a request is sent.

### Forecast

```php
use ProjectSaturnStudios\Weatherman\Enums\ForecastOffice;

$tonight = nws()->forecast()->grid(ForecastOffice::LWX, 97, 71)->get()->periods->first();

$tonight->name;            // "Tonight"
$tonight->temperature;     // 60.0
$tonight->temperature_unit; // "F"
$tonight->wind_speed;      // "5 mph"
```

| Method | Returns |
|---|---|
| `grid(ForecastOffice\|string $office, int $x, int $y)` | `Forecast`, the 12-hour periods |
| `hourly(ForecastOffice\|string $office, int $x, int $y)` | `Forecast`, the hourly periods |

`Forecast` has `units`, `generated_at`, `update_time`, `valid_times`, `forecast_generator`, `elevation`, `periods`, and `geometry`. Each `ForecastPeriod` has `number`, `name`, `start_time`, `end_time`, `is_daytime`, `temperature`, `temperature_unit`, `temperature_reading`, `temperature_trend`, `probability_of_precipitation`, `dewpoint`, `relative_humidity`, `wind_speed`, `wind_speed_reading`, `wind_direction`, `icon`, `short_forecast`, and `detailed_forecast`.

Temperature and wind speed arrive as a number and a string unless you send `ForecastFeatureFlag::FORECAST_TEMPERATURE_QV` or `FORECAST_WIND_SPEED_QV`. Without the flag, `temperature_unit` is `F` or `C` and `wind_speed` is text such as `5 mph`. With the flag, `temperature_reading` or `wind_speed_reading` is a `QuantitativeValue`, `temperature_unit` is that value's unit code (`wmoUnit:degC`), `wind_speed` is null, and `windSpeedText()` joins the number and the unit code (`8 wmoUnit:km_h-1`). `knownTrend()` is `TemperatureTrend::RISING` or `FALLING`, or null.

An unknown office, or a negative grid axis, throws `InvalidArgumentException`.

### Alerts

```php
use ProjectSaturnStudios\Weatherman\Enums\MarineRegion;

$heat = nws()->alerts()->area('CA')->get()->alerts->first();

$heat->event;     // "Heat Advisory"
$heat->headline;  // "Heat Advisory remains in effect until 10 PM PDT Sunday"
```

| Method | Returns |
|---|---|
| `active()` | `AlertPage` of active alerts |
| `collection()` | `AlertPage` of the full collection. `with('start')` and `with('end')` bound it |
| `at(float $latitude, float $longitude)` | `AlertPage` of active alerts at that point |
| `area(string $area)` | `AlertPage` for a two-letter state, territory, or marine area |
| `zone(string $zone_id)` | `AlertPage` for one UGC zone id, such as `CAZ006` |
| `region(MarineRegion $region)` | `AlertPage` for a marine region |
| `find(string $id)` | One `Alert` |
| `count()` | `AlertCount`: `total`, `land`, `marine`, `regions`, `areas`, `zones` |
| `types()` | `Collection<string>` of event names |

`Alert` keeps the CAP fields: `id`, `area_desc`, `geocode`, `affected_zones`, `references`, the times (`sent`, `effective`, `onset`, `expires`, `ends`), `status`, `message_type`, `category`, `severity`, `certainty`, `urgency`, `event`, `sender`, `sender_name`, `headline`, `description`, `instruction`, `response`, and `parameters`. `knownStatus()`, `knownMessageType()`, `knownSeverity()`, `knownUrgency()`, and `knownCertainty()` return the matching enum, or null when NWS sends a value that is not in the set. The raw string stays on the property.

`AlertPage::next()` follows `pagination.next`. A zone id that is not UGC throws `InvalidArgumentException`.

### Stations and observations

```php
$station = nws()->stations()->find('KDCA')->get();

$station->name; // "Washington/Reagan National Airport, DC"

$latest = $station->latest()->get();

$latest->text_description;     // "Cloudy"
$latest->temperature->value;   // 18.0
$latest->temperature->knownQuality(); // QualityControl::V
```

| Method | Returns |
|---|---|
| `stations()->index(?string $state = null, ?int $limit = null)` | `StationPage`. `$limit` is 1 to 500 |
| `stations()->find(string $station_id)` | `Station` |
| `stations()->grid(ForecastOffice\|string $office, int $x, int $y)` | `StationPage` for that gridpoint |
| `observations()->latest(string $station_id, ?bool $require_qc = null)` | `Observation` |

`Station` has `station_identifier`, `name`, `time_zone`, `provider`, `sub_provider`, `elevation`, `forecast_zone`, `county`, `fire_weather_zone`, `distance`, `bearing`, and `geometry`. `StationPage` also carries `observation_station_urls` and `next()`.

`Observation` has the quantitative readings (`temperature`, `dewpoint`, `wind_direction`, `wind_speed`, `wind_gust`, pressure, visibility, precipitation, `relative_humidity`, `wind_chill`, `heat_index`), `cloud_layers`, `present_weather`, `raw_message`, `text_description`, `timestamp`, and `station_id`. `station()` follows the station URL on the observation.

`observations()->list($station_id)` and `observations()->atTime($station_id, $time)` throw `NotYetSupportedException`.
