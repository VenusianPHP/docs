# Event Loop

Every ScrapyardIO call returns its result before your code moves on. When your application has an IOPools event loop, the waits inside those calls share the loop instead of stalling the process, input pins and serial ports can deliver what they receive as loop mail, and bus work can be offloaded to a worker pool.

## Introduction

ScrapyardIO's API is blocking: `$sensor->writeRead([0x32], 6)` returns six bytes, `$gps->readUntil("\r\n", 1000)` returns a line or `null`, and nothing needs a callback. That stays true whether or not an event loop exists. What the loop changes is what happens *while* a call waits, and what else you may do besides calling.

This page assumes you know the Venusian event loop. If you do not, read [Event Loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop) first, in particular [Waiting With `until`](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#waiting-with-until), [Fibers](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#fibers) and [Worker Pools](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#worker-pools), and then [Loop Mail](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/loop-mail). ScrapyardIO builds directly on those pieces and does not re-explain them here.

## How ScrapyardIO Finds the Loop

ScrapyardIO looks for the loop in the container under the `Voyager\Contracts\IOPools\Loop` contract. Venusian's IOPools service provider is one of its default providers, so a Venusian application has a loop bound unless you removed that provider. A container without one, such as the bare container a unit test builds, has no loop, and ScrapyardIO treats a loop that is bound but cannot be resolved the same way.

Each [connection manager](/docs/{{version}}/scrapyard-io/architecture-concepts/connection-managers) hands every driver it builds a closure that performs this lookup, and the drivers pass it on to the transports they hand out. The lookup happens when a call needs the loop, not when the driver or transport is built, so a loop bound after you connected a bus still counts, and the order your providers boot in never matters.

With no loop, nothing on this page applies except what the next section says about waits: they sleep in the adapter, `watch()` throws, and `via()` refuses.

## Loop-Aware Waits

Several calls wait for the hardware: an input pin's `listen`, and a UART port's `read`, `readUntil` and `write`. Without a loop, each one sleeps inside the adapter until it is done or its timeout passes; on Linux that is libgpiod's wait for edge events on the line request, or a `ppoll` on the port's file descriptor.

With a loop bound, the same calls wait through the loop's `until` method instead, so they behave the way every Venusian wait does:

- **On the main stack**, the call borrows the loop: it turns the loop itself until it finishes. Your code still waits for the result, but timers, watched streams, worker pools and every other resource keep being served meanwhile.
- **Inside a fiber** started with `$loop->async()`, the call suspends the fiber and gives control back to the loop. Other fibers run, and this one resumes when its condition holds.

The timeout becomes a loop timer, so a call with a 500 ms timeout returns after 500 ms whether the loop is idle or busy. While a call waits, the pin or port puts itself on the loop, and takes itself off again when the wait ends.

This means several devices can be read side by side without any change to the code that reads each one:

```php
use Voyager\Contracts\IOPools\Loop;

$loop = app(Loop::class);

$line = $loop->async(fn () => $gps->readUntil("\r\n", 2_000));
$press = $loop->async(fn () => $button->listen(5_000, rising_events: false, falling_events: true));

[$sentence, $edge] = [$line->wait(), $press->wait()];
```

A few other waits ride the loop the same way. On Linux, asking for a PWM channel that is not exported yet exports it and waits for udev to make its files writable, up to the factory's `readyTimeout()` (500 ms by default); with a loop it waits on the loop, and without one it sleeps 10 ms at a time. A blocking I2C, SPI or PWM call that must first wait for offloaded jobs queued before it, and an SPI call waiting for another fiber's `select()` to let go of the bus, also wait through `until`.

## Watching Pins and Ports

Input pins and UART ports keep an unread queue of what the hardware reported: up to 64 edges per pin, and up to 64 KB per port, where the oldest bytes are dropped and counted by `dropped()`. `listen`, `pollEdges`, `read`, `readUntil` and `pollBytes` all take from that queue.

The `watch` method also puts a pin or port on the loop and mails a copy of everything it receives, so your code hears about input without asking for it. `unwatch` stops the mail. The queue is unaffected either way, so whatever was mailed is still there to read:

```php
$button->watch(rising_events: false, falling_events: true);
$button->unwatch();

$gps->watch();
$gps->unwatch();
```

A pin's `watch` takes which edges to mail; both default to `true`. `watch` needs a loop: without one, a pin throws a `DigitalIOException` and a port throws `watch() needs an event loop. Boot IOPools, or read() without one.`

Each watched pin or port is a loop resource under its own name, and each piece of mail is a `Voyager\Contracts\Signals\NamedSignal` that carries the same name:

| Watched | Resource and mail name | Mail class | Properties |
|---|---|---|---|
| input pin | `gpio.edge.<device>.<pin>` | `GeneralPurposeIO\Contracts\Digital\DigitalEdgeEvent` | `device`, `pin`, `edge`, `timestamp`, `seqno` |
| UART port | `gpio.uart.<device>` | `GeneralPurposeIO\Contracts\UART\UARTReceived` | `device`, `bytes`, `timestamp`, `seqno` |

`timestamp` is a `CLOCK_MONOTONIC` time in nanoseconds: the kernel's own stamp for a Linux edge, and the collection time otherwise. `seqno` counts per pin or per port, so a gap in it means an edge or chunk was lost. `edge` is a `SignalEdge` enum, `RISING` or `FALLING`. Both classes round-trip through `toData()` and `fromData()`, with a port's bytes base64-encoded, so they cross a worker or Redis wire intact.

How the loop learns of new input depends on the adapter. On the `native` driver, a pin or port puts its file descriptor on the loop, so the loop wakes exactly when the kernel has something. The `usb` driver's FTDI devices have no descriptor to watch, so the pin or port registers a timer and samples the device; a UART port there is sampled every 10 ms.

### Receiving the Mail

The mail is delivered by the loop's mail handler, at the end of each turn of `run()`. With the `signal` handler, the default for Computer commands, each piece is dispatched as a signal, so you may listen for one pin or port by name, for a wildcard, or for the class:

```php
use GeneralPurposeIO\Contracts\Digital\DigitalEdgeEvent;
use GeneralPurposeIO\Contracts\UART\UARTReceived;
use Voyager\Contracts\IOPools\Loop;

app('signals')->listen('gpio.uart./dev/ttyAMA0', function (UARTReceived $chunk) {
    echo $chunk->bytes;
});

app('signals')->listen('gpio.edge.*', function (string $name, array $data) {
    // $data[0] is the DigitalEdgeEvent...
});

app('signals')->listen(function (DigitalEdgeEvent $edge) {
    // Every watched pin...
});

$gps->watch();
$button->watch(rising_events: false, falling_events: true);

app(Loop::class)->run();
```

Under Rocket, the `sketch` handler holds the mail for your sketch instead, and it arrives in the `$mail` argument of the sketch's next `loop` call. Remember that mail is only delivered by turns of `run()`; a wait that borrows the loop turns it without delivering, so a listener never fires in the middle of code that is waiting. [Loop Mail](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/loop-mail) covers both handlers and the delivery rules.

A UART port's intake keeps running while it is watched. If the port fails, for example because a USB serial adapter was unplugged, the failure goes to the call waiting on the port when there is one, and to the loop when there is not; either way the port takes itself off the loop.

<a id="offloading-with-via"></a>
## Offloading with `via()`

Some bus work is slow enough that you would rather not wait for it at all: a large I2C write to a display, a sequence of SPI transfers, a PWM sweep. I2C, SPI and PWM transports have a `via` method that returns the same calls as promises:

```php
$fan = app('gpio.i2c')->driver('native')->device(1, 0x21);

$fan->via()->writeRead([0xFC], 1)
    ->then(fn (array $bytes) => printf("%d °C\n", $bytes[0]))
    ->error(fn (Throwable $e) => report($e));
```

`via` returns an `OffloadedI2C`, `OffloadedSPI` or `OffloadedPWM` with every data call the transport has: `write`, `read`, `writeRead` and `bulkWrite` for I2C; `write`, `read`, `transfer` and `writeRead` for SPI; and the eight period, duty cycle, enable and polarity getters and setters for PWM. Each returns a `Voyager\Contracts\IOPools\Promise` that settles with exactly what the blocking call returns, or rejects with exactly what it throws.

### Choosing Where It Runs

The argument names the worker pool:

| `via(...)` | Runs on |
|---|---|
| `via()` | the adapter's own asynchronous path where it has one; otherwise the thread pool when it is enabled, and the process pool when it is not |
| `via('thread')` | the `thread-workers` pool |
| `via('process')` | the `process-workers` pool |

The pools are Venusian's: the process pool is enabled by `io-pools.pool_workers.process.enabled` and the thread pool by `io-pools.pool_workers.threads.enabled`. See [Named Pools](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#named-pools).

On the `native` driver, each job crosses to a pool worker. The worker builds the same driver class, opens the bus or chip itself and keeps it open between jobs, so only a worker's first job on each bus pays for the open. An SPI job carries the settings the bus was registered with and the slave's own clock, so the worker opens the bus the same way your process did. A PWM job carries what its driver needs to reach the same sysfs tree.

The `usb` driver's FTDI boards cannot leave your process: the USB device is open there. Its I2C and SPI transports run `via()` jobs in loop fibers instead, on a pump the device gets the first time something on it is offloaded. From then on, every USB exchange on the device, offloaded or blocking, takes its turn on that pump, so a blocking call never cuts into an offloaded transfer. Naming a pool there throws, saying MPSSE transfers run on the device's own USB pump.

`via()` needs a loop, and on the `native` driver a pool that is enabled. Without a loop, every call on the handle throws `via() needs an event loop. Boot IOPools, or call the blocking method.` The pool is looked up when the job starts, so when the pool a job needs is off, or you named one that does not exist, its promise rejects with an `InvalidArgumentException` that names the configuration key to enable. An SPI bus registered without its connection factory is refused the same way, since a worker would not know how to open it.

### Ordering

Offloaded jobs run one at a time per queue, in the order you made the calls. What shares a queue depends on what the hardware can safely interleave:

| Protocol and driver | One queue per |
|---|---|
| I2C, `native` | slave: the kernel makes each transfer atomic, so different slaves run side by side |
| I2C and SPI, `usb` | FTDI device |
| SPI, `native` | bus: a job may hold a chip select across several transfers |
| PWM, `native` | channel |

A blocking call keeps program order with the jobs too: before it touches the hardware, it waits for every job queued on its queue before it. It does not wait for jobs queued after it started, so a producer that keeps queueing cannot hold it off. On SPI, a `select()` made outside the queue pauses it and waits for the running job, so the bus is that slave's alone from chip select down to chip select up.

Closing a transport rejects its jobs that have not started, lets the running one finish, and then closes; a `via()` handle checks its transport on every call, so it stops working the moment the transport closes. `disconnect` drops the connection's queues with it.

When a job throws inside a pool worker, the exception crosses back as a remote exception naming its class. ScrapyardIO turns it back into the exception it was, with the same message and the worker's trace reachable through `getPrevious()`, so a `catch (I2CException $e)` works the same for offloaded and blocking calls.

### Bus Jobs

A single offloaded call is one job. When a chip needs several steps that belong together, such as switching on measurement and then reading the axes, ship them as one `GeneralPurposeIO\Contracts\NutsAndBolts\BusJob` and run it with the handle's `run` method. The job's `run` method receives the transport on whichever side of the wire it lands and uses the ordinary blocking calls:

```php
<?php

namespace App\Jobs;

use GeneralPurposeIO\Contracts\NutsAndBolts\BusJob;
use GeneralPurposeIO\Contracts\NutsAndBolts\GPIOTransport;

final class ReadAxes implements BusJob
{
    public function run(GPIOTransport $bus): mixed
    {
        $bus->write([0x2D, 0x08]);

        return $bus->writeRead([0x32], 6);
    }
}
```

```php
$accelerometer = app('gpio.i2c')->driver('native')->device(1, 0x53);

$accelerometer->via()->run(new ReadAxes)->then(function (array $bytes) {
    // ...
});
```

A job may cross a pipe to a process worker, so it holds scalar state only, and its class must be autoloadable in the worker. To hold an SPI chip select across several transfers off-thread, `run` a job that calls `select()` on the transport it is handed.

## Support by Protocol

| Protocol | Loop-aware waits | `watch()` and mail | `via()` |
|---|---|---|---|
| I2C | waits for queued jobs | — | yes |
| SPI | waits for queued jobs and other fibers' `select()` | — | yes |
| UART | `read`, `readUntil`, `write` | `UARTReceived` | — |
| Digital input | `listen` | `DigitalEdgeEvent` | — |
| Digital output | — | — | — |
| PWM | channel readiness on Linux, waits for queued jobs | — | yes |

UART and digital input have no `via()` because they already have something better: their waits share the loop, and `watch()` delivers input as it arrives. Digital outputs do not wait at all.
