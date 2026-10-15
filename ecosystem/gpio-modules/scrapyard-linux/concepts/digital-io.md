# Digital IO

gpiochip connections over libgpiod v2, one line request per pin, edge events drained from the request fd, loop wake through posix_fdopen.

## Connection

`connectTo(N)` → `PosixDigitalIOConnectionFactory`. Handle = `[GPIORequestConfig, GPIOChip]`: `gpiod_chip_open("/dev/gpiochipN")` plus a request config with consumer name (default `scrapyard-io-digital-io`, set with `consumer()`) and kernel event buffer = `DigitalInputTransport::QUEUE_DEPTH` (64). Kernel default is 16 per one-line request; matching the transport queue means neither side drops first. `disconnect()` → `gpiod_chip_close`.

## Pins

One line request per pin, cached per `device:pin`. Asking for the same pin in the other direction throws (`not an output` / `not an input`).

- **Output:** direction OUTPUT. `write()` sets then reads back — returns the level the line reports.
- **Input:** direction INPUT, bias from `LineBias` (mapped 1:1 onto gpiod bias by value), `active_low`, edge detection BOTH always. Request fd set O_NONBLOCK. Rising/falling filtering happens in the framework's queue, not the kernel.

Read failures throw `DigitalIOException::lineReadFailed(chip path, pin)`.

## Edges

- `drainEdges()`: loop `gpiod_line_request_wait_edge_events(…, 0)` + `read_edge_events` into a 64-slot buffer until the kernel queue is empty. The fd is level-triggered; leaving events behind would re-wake select forever.
- Event → `DigitalEdgeEvent(device, pin, RISING|FALLING, timestamp_ns, line_seqno)`. Timestamps and seqnos are the kernel's.
- `awaitEdges($ms)`: `wait_edge_events` with ns timeout (-1 → forever). Blocking path only.
- `edgeStreams()`: request fd wrapped once with `posix_fdopen(fd, 'r')`. `samplingInterval()` null — the fd wakes the loop, no timer.
- `release()`: stream open → `fclose` (closes the fd, which ends the request); never opened → `gpiod_line_request_release`.

Mail name and queue semantics live in the framework (`gpio.edge.<device>.<pin>`).
