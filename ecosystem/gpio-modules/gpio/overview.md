# Overview

> Docs (production): ScrapyardIO · microscrap/gpio 0.10.x

> **Docs (production):** [ScrapyardIO · microscrap/gpio 0.10.x](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/gpio/0.10.x/overview)

[![Docs](https://img.shields.io/badge/docs-ScrapyardIO-0ea5e9?logo=readthedocs&logoColor=white)](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/gpio/0.10.x/overview)
[![Packagist Version](https://img.shields.io/packagist/v/microscrap/gpio.svg?label=packagist)](https://packagist.org/packages/microscrap/gpio)
[![PHP Version Require](https://img.shields.io/packagist/php-v/microscrap/gpio.svg)](https://packagist.org/packages/microscrap/gpio)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/microscrap/gpio/tree/HEAD/LICENSE)
[![Requires ext-posi](https://img.shields.io/badge/ext--posi-%5E0.10-777bb4?logo=php&logoColor=white)](https://github.com/php-io-extensions/posi)

PHP library that wraps the [**posi**](https://github.com/php-io-extensions/posi) extension (`ext-posi`, which also provides the `posix_*` functions) with global helpers, enums, and data objects. Every helper delegates to a facade class under `Microscrap\Bindings\GPIO`.

This is the **bindings** package — not the native extension. It mirrors the public surface of [libgpiod v2](https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/) over Linux GPIO character device uAPI v2. Ecosystem docs: [`0.10.x`](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/gpio/0.10.x/overview).

## Highlights

* Open and interrogate GPIO chips (`/dev/gpiochip0`, etc.)
* Snapshot any line's metadata — name, direction, bias, drive, edge, debounce
* Request exclusive ownership of one or more lines in a single ioctl
* Read and write line values individually or in bulk
* Watch for line-configuration changes on the chip file descriptor
* Stream rising/falling edge events with nanosecond-precision kernel timestamps
* Full libgpiod-compatible helper API (`gpiod_chip_open`, `gpiod_line_request_set_value`, etc.)

## Requirements

* PHP `^8.4|^8.5|^8.6`
* Linux kernel 5.10+ (GPIO uAPI v2)
* **ext-posi** `^0.10.0` — install from [php-io-extensions/posi](https://github.com/php-io-extensions/posi)

## Installation

Confirm **ext-posi** is loaded:

```bash
php -m | grep posi
```

```bash
composer require microscrap/gpio
```

Composer autoloads all helper files in `src/Helpers/`, registering global `gpiod_*` functions when the package is installed.

## Usage

GPIO is controlled through **global helper functions** named after their libgpiod counterparts (`gpiod_chip_open`, `gpiod_line_request_set_value`, etc.). Helpers are only defined if the name is not already taken (`function_exists` guard).

Enums live under `Microscrap\Bindings\GPIO\Enums` — cases are **FULLY UPPERCASE**. Data objects live under `Microscrap\Bindings\GPIO\DataObjects`.

**Example — blink an LED on GPIO 17, read a button on GPIO 27**

```php
<?php

use Microscrap\Bindings\GPIO\Enums\LineDirection;
use Microscrap\Bindings\GPIO\Enums\LineEdge;
use Microscrap\Bindings\GPIO\Enums\LineValue;

$chip = gpiod_chip_open('/dev/gpiochip0');

$led_settings = gpiod_line_settings_new();
gpiod_line_settings_set_direction($led_settings, LineDirection::OUTPUT);
gpiod_line_settings_set_output_value($led_settings, LineValue::INACTIVE);

$btn_settings = gpiod_line_settings_new();
gpiod_line_settings_set_direction($btn_settings, LineDirection::INPUT);
gpiod_line_settings_set_edge_detection($btn_settings, LineEdge::RISING);

$line_config = gpiod_line_config_new();
gpiod_line_config_add_line_settings($line_config, [17], $led_settings);
gpiod_line_config_add_line_settings($line_config, [27], $btn_settings);

$req_config = gpiod_request_config_new();
gpiod_request_config_set_consumer($req_config, 'blink-example');

$request = gpiod_chip_request_lines($chip, $req_config, $line_config);

// Blink 5 times
for ($i = 0; $i < 5; $i++) {
    gpiod_line_request_set_value($request, 17, LineValue::ACTIVE);
    usleep(500_000);
    gpiod_line_request_set_value($request, 17, LineValue::INACTIVE);
    usleep(500_000);
}

gpiod_line_request_release($request);
gpiod_chip_close($chip);
```

See `example/sr04.php` for a complete HC-SR04 ultrasonic distance sensor example using edge-event timestamps.

---

## Global Helper API

### Chip

#### `gpiod_chip_open(string $path): ?GPIOChip`

Opens a GPIO character device. Returns a `GPIOChip` data object holding the file descriptor and path, or `null` on failure. The path must point to a valid GPIO chip device (e.g. `/dev/gpiochip0`); symlinks are resolved and the subsystem is verified before opening.

```php
$chip = gpiod_chip_open('/dev/gpiochip0');
if ($chip === null) {
    throw new RuntimeException('Failed to open GPIO chip');
}
```

---

#### `gpiod_chip_close(GPIOChip $chip): int`

Closes the chip file descriptor. Returns `0` on success, `-1` on failure. Always call this when finished with a chip.

---

#### `gpiod_chip_get_info(GPIOChip $chip): ?GPIOChipInfo`

Returns a `GPIOChipInfo` snapshot with `name`, `label`, and `num_lines` properties. Returns `null` on failure.

```php
$info = gpiod_chip_get_info($chip);
echo $info->name . ' — ' . $info->num_lines . " lines\n";
```

---

#### `gpiod_chip_get_path(GPIOChip $chip): string`

Returns the path the chip was opened with.

---

#### `gpiod_chip_get_fd(GPIOChip $chip): int`

Returns the raw file descriptor. Do not close it directly; use `gpiod_chip_close()`.

---

#### `gpiod_chip_get_line_info(GPIOChip $chip, int $offset): ?GPIOLineInfo`

Returns a `GPIOLineInfo` snapshot for the line at `$offset`. Returns `null` on failure.

```php
$line = gpiod_chip_get_line_info($chip, 17);
echo $line->name . ' used=' . ($line->used ? 'yes' : 'no') . "\n";
```

---

#### `gpiod_chip_watch_line_info(GPIOChip $chip, int $offset): ?GPIOLineInfo`

Same as `gpiod_chip_get_line_info()` but also registers the line for configuration-change events readable via `gpiod_chip_read_info_event()`.

---

#### `gpiod_chip_unwatch_line_info(GPIOChip $chip, int $offset): int`

Stops watching a previously registered line. Returns `0` on success.

---

#### `gpiod_chip_wait_info_event(GPIOChip $chip, int $timeout_ns): ?int`

Polls the chip file descriptor for a pending info event. Returns `1` if an event is ready, `0` on timeout, `-1` on error. `$timeout_ns < 0` blocks indefinitely.

```php
$ready = gpiod_chip_wait_info_event($chip, 1_000_000_000); // 1 s
if ($ready === 1) {
    $event = gpiod_chip_read_info_event($chip);
}
```

---

#### `gpiod_chip_read_info_event(GPIOChip $chip): ?GPIOInfoEvent`

Reads one info event from the chip. Returns a `GPIOInfoEvent` with `event_type` (`InfoEventType`), `timestamp` (nanoseconds), and `info` (`GPIOLineInfo` snapshot). Returns `null` on failure.

---

#### `gpiod_chip_get_line_offset_from_name(GPIOChip $chip, string $name): ?int`

Searches all lines on the chip for one matching `$name`. Returns the offset, or `null` if not found.

```php
$offset = gpiod_chip_get_line_offset_from_name($chip, 'GPIO17');
```

---

#### `gpiod_chip_request_lines(GPIOChip $chip, GPIORequestConfig $request, GPIOLineConfig $line_config): ?GPIOLineRequest`

Issues `GPIO_V2_GET_LINE` to claim exclusive ownership of all configured lines. Returns a `GPIOLineRequest` holding the request file descriptor, or `null` on failure. The request must be released with `gpiod_line_request_release()` when finished.

```php
$request = gpiod_chip_request_lines($chip, $req_config, $line_config);
if ($request === null) {
    throw new RuntimeException('Failed to request lines');
}
```

---

### ChipInfo

All getters operate on a `GPIOChipInfo` returned by `gpiod_chip_get_info()`.

| Helper | Returns |
|--------|---------|
| `gpiod_chip_info_get_name(GPIOChipInfo $info): string` | Kernel chip name |
| `gpiod_chip_info_get_label(GPIOChipInfo $info): string` | Chip label (`"unknown"` if empty) |
| `gpiod_chip_info_get_num_lines(GPIOChipInfo $info): int` | Number of lines on this chip |

---

### LineInfo

All getters operate on a `GPIOLineInfo` returned by `gpiod_chip_get_line_info()` or embedded in a `GPIOInfoEvent`.

#### `gpiod_line_info_copy(GPIOLineInfo $info): GPIOLineInfo`

Returns a deep copy (PHP `clone`).

| Helper | Returns |
|--------|---------|
| `gpiod_line_info_get_offset(GPIOLineInfo $info): int` | Offset on the chip |
| `gpiod_line_info_get_name(GPIOLineInfo $info): string` | Line name (`""` if unnamed) |
| `gpiod_line_info_is_used(GPIOLineInfo $info): bool` | Whether the line is currently claimed |
| `gpiod_line_info_get_consumer(GPIOLineInfo $info): string` | Consumer label (`""` if none) |
| `gpiod_line_info_get_direction(GPIOLineInfo $info): LineDirection` | `INPUT` or `OUTPUT` |
| `gpiod_line_info_get_edge_detection(GPIOLineInfo $info): LineEdge` | `NONE`, `RISING`, `FALLING`, or `BOTH` |
| `gpiod_line_info_get_bias(GPIOLineInfo $info): LineBias` | `UNKNOWN`, `DISABLED`, `PULL_UP`, or `PULL_DOWN` |
| `gpiod_line_info_get_drive(GPIOLineInfo $info): LineDrive` | `PUSH_PULL`, `OPEN_DRAIN`, or `OPEN_SOURCE` |
| `gpiod_line_info_is_active_low(GPIOLineInfo $info): bool` | Active-low flag |
| `gpiod_line_info_is_debounced(GPIOLineInfo $info): bool` | Whether debounce is active |
| `gpiod_line_info_get_debounce_period_us(GPIOLineInfo $info): int` | Debounce period in microseconds |
| `gpiod_line_info_get_event_clock(GPIOLineInfo $info): LineClock` | `MONOTONIC`, `REALTIME`, or `HTE` |

---

### LineSettings

`GPIOLineSettings` is a mutable builder. All setters return `0` on success, `-1` if the value is invalid.

#### `gpiod_line_settings_new(): GPIOLineSettings`

Returns a new settings object with defaults: direction `AS_IS`, edge `NONE`, bias `AS_IS`, drive `PUSH_PULL`, active-low `false`, clock `MONOTONIC`, debounce `0`, output value `INACTIVE`.

#### `gpiod_line_settings_reset(GPIOLineSettings $settings): void`

Resets all fields to their defaults in place.

#### `gpiod_line_settings_copy(GPIOLineSettings $settings): GPIOLineSettings`

Returns a clone.

| Setter | Getter |
|--------|--------|
| `gpiod_line_settings_set_direction($s, LineDirection $v): int` | `gpiod_line_settings_get_direction($s): LineDirection` |
| `gpiod_line_settings_set_edge_detection($s, LineEdge $v): int` | `gpiod_line_settings_get_edge_detection($s): LineEdge` |
| `gpiod_line_settings_set_bias($s, LineBias $v): int` | `gpiod_line_settings_get_bias($s): LineBias` |
| `gpiod_line_settings_set_drive($s, LineDrive $v): int` | `gpiod_line_settings_get_drive($s): LineDrive` |
| `gpiod_line_settings_set_active_low($s, bool $v): void` | `gpiod_line_settings_get_active_low($s): bool` |
| `gpiod_line_settings_set_debounce_period_us($s, int $v): void` | `gpiod_line_settings_get_debounce_period_us($s): int` |
| `gpiod_line_settings_set_event_clock($s, LineClock $v): int` | `gpiod_line_settings_get_event_clock($s): LineClock` |
| `gpiod_line_settings_set_output_value($s, LineValue $v): int` | `gpiod_line_settings_get_output_value($s): LineValue` |

---

### LineConfig

`GPIOLineConfig` maps GPIO offsets to `GPIOLineSettings` objects. It serialises to the `gpio_v2_line_config` kernel structure at request time.

#### `gpiod_line_config_new(): GPIOLineConfig`

Returns an empty line configuration.

#### `gpiod_line_config_reset(GPIOLineConfig $config): void`

Clears all configured offsets and output values.

#### `gpiod_line_config_add_line_settings(GPIOLineConfig $config, array $offsets, ?GPIOLineSettings $settings): int`

Assigns `$settings` to each offset in `$offsets`. Passing `null` applies default settings. Returns `0` on success, `-1` if `$offsets` is empty, any offset is invalid, or the total configured count would exceed 64 (`GPIO_V2_LINES_MAX`).

```php
$line_config = gpiod_line_config_new();
gpiod_line_config_add_line_settings($line_config, [4, 17, 27], $settings);
```

#### `gpiod_line_config_get_line_settings(GPIOLineConfig $config, int $offset): ?GPIOLineSettings`

Returns a copy of the settings for `$offset`, or `null` if the offset is not configured.

#### `gpiod_line_config_set_output_values(GPIOLineConfig $config, array $values): int`

Overrides the output values for all configured offsets, by configuration index. `$values` must be an array of `LineValue` (or int-castable equivalents); `LineValue::ERROR` is rejected. Returns `0` on success.

| Helper | Returns |
|--------|---------|
| `gpiod_line_config_get_num_configured_offsets(GPIOLineConfig $config): int` | Count of configured offsets |
| `gpiod_line_config_get_configured_offsets(GPIOLineConfig $config, int $max): array` | Offsets (up to `$max`) |
| `gpiod_line_config_to_uapi(GPIOLineConfig $config): ?GPIOV2LineConfig` | Serialise to kernel struct |

---

### RequestConfig

`GPIORequestConfig` carries the consumer label and kernel event-buffer size passed at request time.

#### `gpiod_request_config_new(): GPIORequestConfig`

Returns a new request configuration with empty consumer and buffer size `0` (kernel default: `16 × num_lines`).

| Setter | Getter |
|--------|--------|
| `gpiod_request_config_set_consumer($rc, string $v): void` | `gpiod_request_config_get_consumer($rc): string` |
| `gpiod_request_config_set_event_buffer_size($rc, int $v): void` | `gpiod_request_config_get_event_buffer_size($rc): int` |

Consumer strings longer than 32 bytes are silently truncated to `GPIO_MAX_NAME_SIZE`.

---

### LineRequest

All value I/O targets the **request file descriptor** via `GPIO_V2_LINE_GET_VALUES` / `GPIO_V2_LINE_SET_VALUES` ioctls. Offsets must belong to the original request.

#### `gpiod_line_request_release(GPIOLineRequest $request): int`

Closes the request file descriptor and releases all lines. Returns `0` on success.

| Helper | Returns |
|--------|---------|
| `gpiod_line_request_get_fd($req): int` | Raw request file descriptor |
| `gpiod_line_request_get_chip_name($req): string` | Name of the chip the lines were requested from |
| `gpiod_line_request_get_num_requested_lines($req): int` | Number of lines in this request |
| `gpiod_line_request_get_requested_offsets($req, int $max): array` | Offsets (up to `$max`) |

#### `gpiod_line_request_get_value(GPIOLineRequest $request, int $offset): ?LineValue`

Reads the current value of a single line. Returns `LineValue::ACTIVE`, `LineValue::INACTIVE`, or `null` on failure.

```php
$v = gpiod_line_request_get_value($request, 27);
echo $v === LineValue::ACTIVE ? "HIGH\n" : "LOW\n";
```

#### `gpiod_line_request_get_values(GPIOLineRequest $request): ?array`

Reads values for all requested lines. Returns an indexed array of `LineValue` in offset order, or `null` on failure.

#### `gpiod_line_request_get_values_subset(GPIOLineRequest $request, array $offsets): ?array`

Reads values for the specified subset of offsets.

#### `gpiod_line_request_set_value(GPIOLineRequest $request, int $offset, LineValue|int $value): int`

Drives a single line. Returns `0` on success, `-1` on failure.

```php
gpiod_line_request_set_value($request, 17, LineValue::ACTIVE);
```

#### `gpiod_line_request_set_values(GPIOLineRequest $request, array $values): int`

Drives all requested lines. `$values` must be indexed in the same order as the configured offsets.

#### `gpiod_line_request_set_values_subset(GPIOLineRequest $request, array $offsets, array $values): int`

Drives a subset of lines. `$offsets` and `$values` must be the same length.

#### `gpiod_line_request_reconfigure_lines(GPIOLineRequest $request, GPIOLineConfig $config): int`

Applies a new line configuration to the existing request without releasing it (`GPIO_V2_LINE_SET_CONFIG`). Returns `0` on success.

#### `gpiod_line_request_wait_edge_events(GPIOLineRequest $request, int $timeout_ns): ?int`

Polls the request file descriptor for pending edge events. Returns `1` if ready, `0` on timeout, `-1` on error. `$timeout_ns < 0` blocks indefinitely.

#### `gpiod_line_request_read_edge_events(GPIOLineRequest $request, GPIOEdgeEventBuffer $buffer, int $max_events): int`

Reads up to `$max_events` (capped to buffer capacity) edge events from the request file descriptor into `$buffer`. Returns the number of events read, or `-1` on failure.

```php
$buffer = gpiod_edge_event_buffer_new(16);

$ready = gpiod_line_request_wait_edge_events($request, -1); // block
if ($ready === 1) {
    $n = gpiod_line_request_read_edge_events($request, $buffer, 16);
    for ($i = 0; $i < $n; $i++) {
        $event = gpiod_edge_event_buffer_get_event($buffer, $i);
        printf("offset=%d type=%s ts=%d ns\n",
            $event->line_offset,
            $event->event_type->name,
            $event->timestamp_ns,
        );
    }
}
```

---

### InfoEvent

Getters for `GPIOInfoEvent` objects returned by `gpiod_chip_read_info_event()`.

| Helper | Returns |
|--------|---------|
| `gpiod_info_event_get_event_type(GPIOInfoEvent $event): InfoEventType` | `LINE_REQUESTED`, `LINE_RELEASED`, or `LINE_CONFIG_CHANGED` |
| `gpiod_info_event_get_timestamp_ns(GPIOInfoEvent $event): int` | Kernel monotonic timestamp (nanoseconds) |
| `gpiod_info_event_get_line_info(GPIOInfoEvent $event): GPIOLineInfo` | Line snapshot at event time |

---

### EdgeEvent

Getters for `GPIOEdgeEvent` objects retrieved from an `GPIOEdgeEventBuffer`.

#### `gpiod_edge_event_copy(GPIOEdgeEvent $event): GPIOEdgeEvent`

Returns a clone of the event, detached from the buffer.

| Helper | Returns |
|--------|---------|
| `gpiod_edge_event_get_event_type(GPIOEdgeEvent $event): EdgeEventType` | `RISING_EDGE` or `FALLING_EDGE` |
| `gpiod_edge_event_get_timestamp_ns(GPIOEdgeEvent $event): int` | Kernel timestamp (nanoseconds) |
| `gpiod_edge_event_get_line_offset(GPIOEdgeEvent $event): int` | Line offset that produced the event |
| `gpiod_edge_event_get_global_seqno(GPIOEdgeEvent $event): int` | Sequence number across all lines in the request |
| `gpiod_edge_event_get_line_seqno(GPIOEdgeEvent $event): int` | Per-line sequence number |

---

### EdgeEventBuffer

A reusable buffer for batch-reading edge events from a request file descriptor.

#### `gpiod_edge_event_buffer_new(int $capacity = 64): GPIOEdgeEventBuffer`

Allocates a buffer. Maximum capacity is 1024 (`GPIO_V2_LINES_MAX × 16`).

| Helper | Returns |
|--------|---------|
| `gpiod_edge_event_buffer_get_capacity(GPIOEdgeEventBuffer $buf): int` | Maximum events the buffer can hold |
| `gpiod_edge_event_buffer_get_num_events(GPIOEdgeEventBuffer $buf): int` | Events from the last `read_edge_events` call |
| `gpiod_edge_event_buffer_get_event(GPIOEdgeEventBuffer $buf, int $index): ?GPIOEdgeEvent` | Event at `$index` (do not free; owned by buffer) |

---

### Misc

#### `gpiod_is_gpiochip_device(string $path): bool`

Returns `true` if `$path` is a GPIO character device (or a symlink resolving to one). Checks the kernel subsystem via `/sys/dev/char/`. Used internally by `gpiod_chip_open()`.

#### `gpiod_api_version(): string`

Returns the package version string (e.g. `"0.10.0"`).

---

## Enums

All enums are `int`-backed with `SCREAMING_SNAKE_CASE` cases where they map to kernel constants.

| Enum | Namespace | Cases |
|------|-----------|-------|
| `GPIOOpCode` | `Enums` | 8 GPIO ioctl opcodes |
| `GPIOV2LineFlag` | `Enums` | 13 `gpio_v2_line_flag` bitmask values |
| `GPIOV2LineAttrId` | `Enums` | `FLAGS`, `OUTPUT_VALUES`, `DEBOUNCE` |
| `InfoEventType` | `Enums` | `LINE_REQUESTED`, `LINE_RELEASED`, `LINE_CONFIG_CHANGED` |
| `EdgeEventType` | `Enums` | `RISING_EDGE`, `FALLING_EDGE` |
| `LineDirection` | `Enums` | `AS_IS`, `INPUT`, `OUTPUT` |
| `LineEdge` | `Enums` | `NONE`, `RISING`, `FALLING`, `BOTH` |
| `LineBias` | `Enums` | `AS_IS`, `UNKNOWN`, `DISABLED`, `PULL_UP`, `PULL_DOWN` |
| `LineDrive` | `Enums` | `PUSH_PULL`, `OPEN_DRAIN`, `OPEN_SOURCE` |
| `LineClock` | `Enums` | `MONOTONIC`, `REALTIME`, `HTE` |
| `LineValue` | `Enums` | `ERROR` (-1), `INACTIVE` (0), `ACTIVE` (1) |

---

## Quick reference

| Helper | Signature |
|--------|-----------|
| `gpiod_chip_open` | `(string $path): ?GPIOChip` |
| `gpiod_chip_close` | `(GPIOChip $chip): int` |
| `gpiod_chip_get_info` | `(GPIOChip $chip): ?GPIOChipInfo` |
| `gpiod_chip_get_path` | `(GPIOChip $chip): string` |
| `gpiod_chip_get_fd` | `(GPIOChip $chip): int` |
| `gpiod_chip_get_line_info` | `(GPIOChip $chip, int $offset): ?GPIOLineInfo` |
| `gpiod_chip_watch_line_info` | `(GPIOChip $chip, int $offset): ?GPIOLineInfo` |
| `gpiod_chip_unwatch_line_info` | `(GPIOChip $chip, int $offset): int` |
| `gpiod_chip_wait_info_event` | `(GPIOChip $chip, int $timeout_ns): ?int` |
| `gpiod_chip_read_info_event` | `(GPIOChip $chip): ?GPIOInfoEvent` |
| `gpiod_chip_get_line_offset_from_name` | `(GPIOChip $chip, string $name): ?int` |
| `gpiod_chip_request_lines` | `(GPIOChip $chip, GPIORequestConfig $req, GPIOLineConfig $cfg): ?GPIOLineRequest` |
| `gpiod_chip_info_get_name` | `(GPIOChipInfo $info): string` |
| `gpiod_chip_info_get_label` | `(GPIOChipInfo $info): string` |
| `gpiod_chip_info_get_num_lines` | `(GPIOChipInfo $info): int` |
| `gpiod_line_info_copy` | `(GPIOLineInfo $info): GPIOLineInfo` |
| `gpiod_line_info_get_offset` | `(GPIOLineInfo $info): int` |
| `gpiod_line_info_get_name` | `(GPIOLineInfo $info): string` |
| `gpiod_line_info_is_used` | `(GPIOLineInfo $info): bool` |
| `gpiod_line_info_get_consumer` | `(GPIOLineInfo $info): string` |
| `gpiod_line_info_get_direction` | `(GPIOLineInfo $info): LineDirection` |
| `gpiod_line_info_get_edge_detection` | `(GPIOLineInfo $info): LineEdge` |
| `gpiod_line_info_get_bias` | `(GPIOLineInfo $info): LineBias` |
| `gpiod_line_info_get_drive` | `(GPIOLineInfo $info): LineDrive` |
| `gpiod_line_info_is_active_low` | `(GPIOLineInfo $info): bool` |
| `gpiod_line_info_is_debounced` | `(GPIOLineInfo $info): bool` |
| `gpiod_line_info_get_debounce_period_us` | `(GPIOLineInfo $info): int` |
| `gpiod_line_info_get_event_clock` | `(GPIOLineInfo $info): LineClock` |
| `gpiod_line_settings_new` | `(): GPIOLineSettings` |
| `gpiod_line_settings_reset` | `(GPIOLineSettings $s): void` |
| `gpiod_line_settings_copy` | `(GPIOLineSettings $s): GPIOLineSettings` |
| `gpiod_line_settings_set_direction` | `(GPIOLineSettings $s, LineDirection $v): int` |
| `gpiod_line_settings_get_direction` | `(GPIOLineSettings $s): LineDirection` |
| `gpiod_line_settings_set_edge_detection` | `(GPIOLineSettings $s, LineEdge $v): int` |
| `gpiod_line_settings_get_edge_detection` | `(GPIOLineSettings $s): LineEdge` |
| `gpiod_line_settings_set_bias` | `(GPIOLineSettings $s, LineBias $v): int` |
| `gpiod_line_settings_get_bias` | `(GPIOLineSettings $s): LineBias` |
| `gpiod_line_settings_set_drive` | `(GPIOLineSettings $s, LineDrive $v): int` |
| `gpiod_line_settings_get_drive` | `(GPIOLineSettings $s): LineDrive` |
| `gpiod_line_settings_set_active_low` | `(GPIOLineSettings $s, bool $v): void` |
| `gpiod_line_settings_get_active_low` | `(GPIOLineSettings $s): bool` |
| `gpiod_line_settings_set_debounce_period_us` | `(GPIOLineSettings $s, int $v): void` |
| `gpiod_line_settings_get_debounce_period_us` | `(GPIOLineSettings $s): int` |
| `gpiod_line_settings_set_event_clock` | `(GPIOLineSettings $s, LineClock $v): int` |
| `gpiod_line_settings_get_event_clock` | `(GPIOLineSettings $s): LineClock` |
| `gpiod_line_settings_set_output_value` | `(GPIOLineSettings $s, LineValue $v): int` |
| `gpiod_line_settings_get_output_value` | `(GPIOLineSettings $s): LineValue` |
| `gpiod_line_config_new` | `(): GPIOLineConfig` |
| `gpiod_line_config_reset` | `(GPIOLineConfig $c): void` |
| `gpiod_line_config_add_line_settings` | `(GPIOLineConfig $c, array $offsets, ?GPIOLineSettings $s): int` |
| `gpiod_line_config_get_line_settings` | `(GPIOLineConfig $c, int $offset): ?GPIOLineSettings` |
| `gpiod_line_config_set_output_values` | `(GPIOLineConfig $c, array $values): int` |
| `gpiod_line_config_get_num_configured_offsets` | `(GPIOLineConfig $c): int` |
| `gpiod_line_config_get_configured_offsets` | `(GPIOLineConfig $c, int $max): array` |
| `gpiod_line_config_to_uapi` | `(GPIOLineConfig $c): ?GPIOV2LineConfig` |
| `gpiod_request_config_new` | `(): GPIORequestConfig` |
| `gpiod_request_config_set_consumer` | `(GPIORequestConfig $rc, string $v): void` |
| `gpiod_request_config_get_consumer` | `(GPIORequestConfig $rc): string` |
| `gpiod_request_config_set_event_buffer_size` | `(GPIORequestConfig $rc, int $v): void` |
| `gpiod_request_config_get_event_buffer_size` | `(GPIORequestConfig $rc): int` |
| `gpiod_line_request_release` | `(GPIOLineRequest $req): int` |
| `gpiod_line_request_get_fd` | `(GPIOLineRequest $req): int` |
| `gpiod_line_request_get_chip_name` | `(GPIOLineRequest $req): string` |
| `gpiod_line_request_get_num_requested_lines` | `(GPIOLineRequest $req): int` |
| `gpiod_line_request_get_requested_offsets` | `(GPIOLineRequest $req, int $max): array` |
| `gpiod_line_request_get_value` | `(GPIOLineRequest $req, int $offset): ?LineValue` |
| `gpiod_line_request_get_values` | `(GPIOLineRequest $req): ?array` |
| `gpiod_line_request_get_values_subset` | `(GPIOLineRequest $req, array $offsets): ?array` |
| `gpiod_line_request_set_value` | `(GPIOLineRequest $req, int $offset, LineValue\|int $v): int` |
| `gpiod_line_request_set_values` | `(GPIOLineRequest $req, array $values): int` |
| `gpiod_line_request_set_values_subset` | `(GPIOLineRequest $req, array $offsets, array $values): int` |
| `gpiod_line_request_reconfigure_lines` | `(GPIOLineRequest $req, GPIOLineConfig $cfg): int` |
| `gpiod_line_request_wait_edge_events` | `(GPIOLineRequest $req, int $timeout_ns): ?int` |
| `gpiod_line_request_read_edge_events` | `(GPIOLineRequest $req, GPIOEdgeEventBuffer $buf, int $max): int` |
| `gpiod_info_event_get_event_type` | `(GPIOInfoEvent $e): InfoEventType` |
| `gpiod_info_event_get_timestamp_ns` | `(GPIOInfoEvent $e): int` |
| `gpiod_info_event_get_line_info` | `(GPIOInfoEvent $e): GPIOLineInfo` |
| `gpiod_edge_event_copy` | `(GPIOEdgeEvent $e): GPIOEdgeEvent` |
| `gpiod_edge_event_get_event_type` | `(GPIOEdgeEvent $e): EdgeEventType` |
| `gpiod_edge_event_get_timestamp_ns` | `(GPIOEdgeEvent $e): int` |
| `gpiod_edge_event_get_line_offset` | `(GPIOEdgeEvent $e): int` |
| `gpiod_edge_event_get_global_seqno` | `(GPIOEdgeEvent $e): int` |
| `gpiod_edge_event_get_line_seqno` | `(GPIOEdgeEvent $e): int` |
| `gpiod_edge_event_buffer_new` | `(int $capacity = 64): GPIOEdgeEventBuffer` |
| `gpiod_edge_event_buffer_get_capacity` | `(GPIOEdgeEventBuffer $buf): int` |
| `gpiod_edge_event_buffer_get_num_events` | `(GPIOEdgeEventBuffer $buf): int` |
| `gpiod_edge_event_buffer_get_event` | `(GPIOEdgeEventBuffer $buf, int $index): ?GPIOEdgeEvent` |
| `gpiod_is_gpiochip_device` | `(string $path): bool` |
| `gpiod_api_version` | `(): string` |

## License

MIT. See [LICENSE](https://github.com/microscrap/gpio/tree/HEAD/LICENSE).
