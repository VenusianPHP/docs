# Digital Pins

Driving and reading individual GPIO lines from PHP: opening a GPIO chip through the `gpio.digital` manager, setting output pins high and low, reading input pins, and catching their edges by waiting, polling, or receiving them as loop mail with `watch()`.

## Introduction

A digital pin is a single line that is either high or low. As an output it lights an LED, switches a relay, resets a chip, or drives a display's data/command line. As an input it reads a button, a limit switch, a sensor's interrupt line, or the echo of an ultrasonic rangefinder. Often what matters about an input is not its level but the moment it changes: an **edge**, rising from low to high or falling from high to low.

ScrapyardIO opens a GPIO chip as a **connection** and hands out each pin as a **transport**: an output transport (`GeneralPurposeIO\Contracts\Digital\DigitalOutTransport`) or an input transport (`GeneralPurposeIO\Contracts\Digital\DigitalInTransport`). Every edge an input sees lands in that pin's queue of unread edges, whoever asked for it, and you take edges from the queue in whichever way suits your program.

## Opening a Chip

### The Digital Manager

The digital connection manager is bound in the container as `gpio.digital`, with `GeneralPurposeIO\Digital\DigitalOConnectionManager` as an alias. There is no facade or global helper; you resolve the manager and ask it for a driver:

```php
$native = app('gpio.digital')->driver('native');   // microscrap/scrapyard-linux
$usb = app('gpio.digital')->driver('usb');         // microscrap/scrapyard-usb
```

Each driver is built once and reused. Calling `driver()` with no name, or calling a driver method on the manager itself, uses the default from the `gpio.protocols.digital-in.default` option of your `config/gpio.php` file. That default is `none` until you set it, and the `none` driver throws `DigitalIOException` on every attempt: "No DigitalIO connection driver is configured. Set gpio.protocols.digital-in.default to an installed adapter." See [Configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration) and [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter).

ScrapyardIO keeps no list of named pins in its config. To keep a chip's wiring, its reset and data/command pins included, in configuration, give it a circuit config and build it with `app('circuit')->conjure(...)`; see [Integrated Circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits).

### Connecting

`connectTo($chip)` names the GPIO chip and returns a connection factory; `register()` opens it and returns the driver:

```php
$pins = app('gpio.digital')->driver('native')
    ->connectTo(0)     // /dev/gpiochip0
    ->register();
```

| Driver | `connectTo()` takes | Opens |
| --- | --- | --- |
| `native` | the chip number, as an `int` or a numeric string | `/dev/gpiochip<n>` through libgpiod |
| `usb` | an MPSSE device name: `ft232h`, `ft2232hl-a`, `ft2232hl-b`, `ft4232hl-a` … `ft4232hl-d` | the FTDI interface, its MPSSE engine in GPIO mode |

The `native` factory takes a `consumer($name)`, the label the kernel shows for your lines in tools such as `gpioinfo`; it is `scrapyard-io-digital-io` unless you set it. The `usb` factory takes a `clockRate()` (`Microscrap\Bindings\MPSSE\Enums\MPSSEClockRate`, `ONE_MHZ` by default) and an `endianness()`:

```php
$pins = app('gpio.digital')->driver('native')
    ->connectTo(0)
    ->consumer('greenhouse')
    ->register();
```

A chip is registered once. Calling `connectTo()` for a chip the driver already holds throws `DigitalIOException` ("Device 0 already connected"). On the `native` driver a chip number with no `/dev/gpiochip<n>` throws "Device 4 does not exist", and a chip that will not open throws when you `register()`.

On an FTDI board, an [I2C](/docs/{{version}}/scrapyard-io/the-basics/i2c) or [SPI](/docs/{{version}}/scrapyard-io/the-basics/spi) connection on the `usb` driver already registers the board with the digital driver, sharing its MPSSE context, so its spare lines are available straight away without a `connectTo()`:

```php
app('gpio.spi')->driver('usb')->connectTo('ft232h')->speed(10_000_000)->register();

$dc = app('gpio.digital')->driver('usb')->output('ft232h', 1);
$reset = app('gpio.digital')->driver('usb')->output('ft232h', 2);
```

On the `usb` driver, pins `0`–`3` are D4–D7 (GPIOL0–3) and `4`–`11` are C0–C7 (GPIOH0–7).

## Output Pins

`output($device, $pin)` returns an output transport for one line, or `null` when the chip was never registered:

```php
$led = $pins->output(0, 17);

$led->high();
$led->low();
$led->write(true);    // true: the level read back
$led->read();         // true
```

| Method | Does |
| --- | --- |
| `high()` | drives the line high |
| `low()` | drives the line low |
| `write(bool $state)` | drives the line to `$state` and returns the level read back |
| `read()` | reads the line's current level |

`write()` reads the line back after setting it. On the `native` driver it returns that level; on the `usb` driver it returns whether the line now matches what you asked for, and `false` when the USB write itself failed.

The driver hands out one transport per pin, so asking for the same output again returns the same object. A pin is either an output or an input: asking for an input on a pin you already took as an output throws `DigitalIOException` ("Pin 17 on device 0 is not an input"), and the other way round.

## Input Pins

`input($device, $pin, $bias = LineBias::AS_IS, $active_low = false)` returns an input transport, or `null` when the chip was never registered:

```php
use GeneralPurposeIO\Contracts\Digital\LineBias;

$button = $pins->input(0, 27, LineBias::PULL_UP);

$pressed = ! $button->read();   // pulled up: pressed reads low
```

`$bias` is a `GeneralPurposeIO\Contracts\Digital\LineBias`: `AS_IS` leaves the line as it is, `PULL_UP` and `PULL_DOWN` enable the internal resistors, and `DISABLED` turns them off. `$active_low` inverts the level the pin reports, so a button wired to ground can read `true` when pressed:

```php
$button = $pins->input(0, 27, LineBias::PULL_UP, active_low: true);

$pressed = $button->read();   // true while held down
```

Both are applied by the kernel on the `native` driver. FTDI lines have no bias resistors or inversion, so the `usb` driver takes the arguments and ignores them.

### Waiting for an Edge

`listen($timeout, $rising_events, $falling_events)` returns the oldest unread edge that matches, waiting up to `$timeout` milliseconds for one if none is queued. It returns `null` on timeout. `-1` waits without limit, and `0` never waits:

```php
$edge = $button->listen(5000, rising_events: false, falling_events: true);

if ($edge === null) {
    $this->line('Nobody pressed the button.');
}
```

Each edge is a `GeneralPurposeIO\Contracts\Digital\DigitalEdgeEvent`:

| Property | Holds |
| --- | --- |
| `device` | the chip, as you passed it to `connectTo()` |
| `pin` | the line number |
| `edge` | `GeneralPurposeIO\Contracts\Digital\SignalEdge::RISING` or `::FALLING` |
| `timestamp` | `CLOCK_MONOTONIC` nanoseconds: the kernel's stamp on the `native` driver, the sample time on the `usb` driver |
| `seqno` | a per-pin sequence number; a gap means an edge was dropped |

Because edges carry the kernel's own timestamps, you can time pulses precisely, as an HC-SR04 rangefinder needs:

```php
$trigger = $pins->output(0, 23);
$echo = $pins->input(0, 24);

$trigger->high();
usleep(10);
$trigger->low();

$rise = $echo->listen(100, rising_events: true, falling_events: false);
$fall = $echo->listen(100, rising_events: false, falling_events: true);

if ($rise && $fall) {
    $centimetres = ($fall->timestamp - $rise->timestamp) / 58_000;
}
```

### Polling for Edges

`pollEdges($rising_events, $falling_events)` returns every unread matching edge, oldest first, and never waits. It suits a sketch's frame loop:

```php
foreach ($encoder->pollEdges(rising_events: true, falling_events: false) as $edge) {
    $this->ticks++;
}
```

### The Edge Queue

Each input pin keeps up to 64 unread edges (`GeneralPurposeIO\Digital\DigitalInputTransport::QUEUE_DEPTH`); past that the oldest is dropped, and the `seqno` gap shows it. On the `native` driver the kernel is asked to buffer the same depth for the line. `listen()` and `pollEdges()` both take from this queue, and edges that do not match the filter you passed stay queued for a later call that asks for them.

On the `usb` driver an FTDI chip has no interrupt lines, so edges are level changes between samples, taken every 10 ms by default. `pollEvery($ms)` on a `usb` input changes the interval, on the loop and in a blocking `listen()` alike; a pulse shorter than the interval can go unseen:

```php
$switch = app('gpio.digital')->driver('usb')->input('ft232h', 3)->pollEvery(2);
```

## Closing

`close()` on a pin gives its line back; the chip stays open for its other pins, and the next `output()` or `input()` for that line requests it fresh. Any call on a closed pin throws `DigitalIOException` ("Pin 17 is closed." for an output, "Pin 27 on device 0 is closed." for an input), including a `listen()` that was waiting on the pin when it closed. `closed()` tells you whether a pin has been closed.

`disconnect($device)` closes every pin on the chip, then the chip itself. `connectTo()` can open it again afterwards. On an FTDI board whose context an I2C or SPI connection opened, disconnecting that I2C or SPI bus closes the digital pins on it first, and the digital driver leaves the context for the bus to close.

## Blocking and the Event Loop

`read()`, `write()`, `high()` and `low()` return at once. Only `listen()` waits.

Without a Venusian [event loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop) bound in the container, `listen()` sleeps in the adapter until an edge arrives or the timeout passes. Once a loop is bound, it shares the loop instead: inside a fiber started with `$loop->async()` it suspends the fiber, and on the main stack it turns the loop until it finishes, so timers and other resources keep running. A pin sits on the loop only while it is watched or a `listen()` is waiting on it.

Digital pins have no `via()`: reading and writing a line is immediate, and waiting for edges is already loop-aware.

### Watching a Pin

`watch($rising_events = true, $falling_events = true)` puts an input pin on the loop and mails a copy of every matching edge. The edge also stays in the pin's queue, so `listen()` and `pollEdges()` still see it. `unwatch()` stops the mail. `watch()` needs a bound loop and throws `DigitalIOException` without one ("No Event Loop is configured.").

Mail is delivered through Venusian's [loop mail](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/loop-mail). Under the `signal` handler each edge is dispatched as a [signal](https://venusian.projectsaturnstudios.com/docs/framework/digging-deeper/signals) named `gpio.edge.<device>.<pin>`. A wildcard listener receives the name and the mail in an array:

```php
use GeneralPurposeIO\Contracts\Digital\DigitalEdgeEvent;
use Voyager\Contracts\IOPools\Loop;

app('signals')->listen('gpio.edge.0.27', fn (DigitalEdgeEvent $edge) => print "Button {$edge->edge->value}\n");
app('signals')->listen('gpio.edge.*', fn (string $name, array $mail) => printf("%s %s\n", $name, $mail[0]->edge->value));

$button->watch(rising_events: false, falling_events: true);

app(Loop::class)->run();
```

In a [sketch](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/sketches), the edges arrive in the `$mail` argument of your next `loop` call:

```php
<?php

namespace App\Runner\Sketches;

use GeneralPurposeIO\Contracts\Digital\DigitalEdgeEvent;
use GeneralPurposeIO\Contracts\Digital\DigitalInTransport;
use GeneralPurposeIO\Contracts\Digital\DigitalOutTransport;
use GeneralPurposeIO\Contracts\Digital\LineBias;
use GeneralPurposeIO\Contracts\Digital\SignalEdge;
use Voyager\Contracts\Sketches\SketchLoopResult;

class Toggle extends Sketch
{
    protected string $description = 'Toggle an LED on each button press.';

    private DigitalOutTransport $led;

    private DigitalInTransport $button;

    public function boot(): void
    {
        $pins = app('gpio.digital')->driver('native')->connectTo(0)->register();

        $this->led = $pins->output(0, 17);
        $this->button = $pins->input(0, 27, LineBias::PULL_UP);
        $this->button->watch(rising_events: false, falling_events: true);
    }

    public function loop(array $mail = []): SketchLoopResult
    {
        foreach ($mail as $piece) {
            if ($piece instanceof DigitalEdgeEvent && $piece->edge === SignalEdge::FALLING) {
                $this->led->write(! $this->led->read());
            }
        }

        return SketchLoopResult::CONTINUE;
    }

    public function shutdown(): void
    {
        app('gpio.digital')->driver('native')->disconnect(0);
    }
}
```

`DigitalEdgeEvent` round-trips through `toData()` and `fromData()`, so an edge crosses a worker or Redis wire intact.

## Adapters

| | `native` | `usb` |
| --- | --- | --- |
| Package | `microscrap/scrapyard-linux` | `microscrap/scrapyard-usb` |
| Hardware | Linux GPIO character devices (libgpiod v2) | FTDI MPSSE lines: FT232H, FT2232H, FT4232H |
| `connectTo()` | chip number | MPSSE device name, or none when I2C or SPI already opened the board |
| Edges | kernel edge events, the line's descriptor wakes the loop | level changes between samples, every 10 ms by default |
| Bias and active-low | yes | ignored |

One FTDI interface runs either its MPSSE engine or its [UART](/docs/{{version}}/scrapyard-io/the-basics/uart), never both: while a UART holds the interface, `connectTo()` throws `GPIOLevelException` until the port is disconnected.

For the adapters themselves, see [scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/digital-io) and [scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/digital-io), and below them [microscrap/gpio](/docs/{{version}}/ecosystem/gpio-modules/gpio/overview) and [microscrap/mpsse](/docs/{{version}}/ecosystem/gpio-modules/mpsse/overview). The [HC-SR04](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/hc-sr04/overview) driver is a digital-pin chip driver to read alongside this page.

## Errors

Every digital failure throws `GeneralPurposeIO\Contracts\Digital\DigitalIOException`, which extends `GeneralPurposeIO\Contracts\Core\GPIOLevelException`. A `listen()` that times out is not an exception: it returns `null`.

| Thrown when | Message |
| --- | --- |
| No adapter is configured | No DigitalIO connection driver is configured. Set gpio.protocols.digital-in.default to an installed adapter. |
| The chip is already registered | Device 0 already connected |
| The chip does not exist (`native`) | Device 4 does not exist |
| The line cannot be requested (`native`) | Could not request line 17 on /dev/gpiochip0 |
| The pin is already taken the other way | Pin 17 on device 0 is not an input |
| The pin is closed | Pin 17 is closed. (output) / Pin 27 on device 0 is closed. (input) |
| The line's level cannot be read (`native`) | Could not read the level of line 17 on /dev/gpiochip0. |
| The pins cannot be read (`usb`) | Could not read pin 3: the MPSSE device did not answer. |
| `watch()` without an event loop | No Event Loop is configured. |
