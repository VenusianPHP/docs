# UART

Talking to serial devices from PHP: opening a port through the `gpio.uart` manager with its baud rate and line settings, reading and writing with timeouts, driving the modem lines, and receiving incoming bytes as loop mail with `watch()`.

## Introduction

A UART is a serial port: two wires, one for each direction, and no clock. GPS receivers, LoRa and cellular modules, fingerprint readers, motor controllers and microcontroller boards all talk this way, usually in lines of text such as NMEA sentences or AT commands. Unlike a bus, a serial port joins exactly two devices, and either side may speak at any time.

ScrapyardIO gives you each serial port as one **connection** and one **transport**. Everything the device sends lands in the port's unread buffer whether or not you are reading at that moment, and your reads take from that buffer. Every wait carries a timeout, so a silent device never hangs your program. Chip drivers depend only on the transport contract, `GeneralPurposeIO\Contracts\UART\UARTTransport`, so the same GPS driver runs on a Raspberry Pi's `/dev/ttyAMA0`, a USB serial adapter at `/dev/ttyUSB0`, or an FT232H's UART.

## Opening a Port

### The UART Manager

The UART connection manager is bound in the container as `gpio.uart`, with `GeneralPurposeIO\UART\UARTConnectionManager` as an alias. There is no facade or global helper; you resolve the manager and ask it for a driver:

```php
$native = app('gpio.uart')->driver('native');   // microscrap/scrapyard-linux
$usb = app('gpio.uart')->driver('usb');         // microscrap/scrapyard-usb
```

Each driver is built once and reused. Calling `driver()` with no name, or calling a driver method on the manager itself, uses the default from the `gpio.protocols.uart.default` option of your `config/gpio.php` file. That default is `none` until you set it, and the `none` driver throws `UARTException` on every attempt: "No UART connection driver is configured. Set gpio.protocols.uart.default to an installed adapter." See [Configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration) and [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter).

ScrapyardIO keeps no list of named ports in its config. To keep a chip's wiring in configuration, give it a circuit config and build it with `app('circuit')->conjure(...)`; see [Integrated Circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits).

### Connecting and Configuring

`connectTo($device)` names the port and returns a connection factory. Set the line options on the factory, then `register()` opens the port and returns the driver. `device($device)` then hands you the port's transport:

```php
use GeneralPurposeIO\Contracts\UART\Parity;

$gps = app('gpio.uart')->driver('native')
    ->connectTo('/dev/ttyAMA0')
    ->baud(9600)
    ->parity(Parity::NONE)
    ->register()
    ->device('/dev/ttyAMA0');
```

| Option | Takes | Default |
| --- | --- | --- |
| `baud($rate)` | the baud rate | `9600` |
| `dataBits($bits)` | `GeneralPurposeIO\Contracts\UART\DataBits` (`FIVE` … `EIGHT`) or `5`–`8` | `EIGHT` |
| `parity($parity)` | `GeneralPurposeIO\Contracts\UART\Parity` (`NONE`, `ODD`, `EVEN`) or `0`–`2` | `NONE` |
| `stopBits($bits)` | `GeneralPurposeIO\Contracts\UART\StopBits` (`ONE`, `TWO`) or `1`–`2` | `ONE` |
| `flowControl($mode)` | `GeneralPurposeIO\Contracts\UART\FlowControl` (`NONE`, `HARDWARE`, `SOFTWARE`) or `0`–`2` | `NONE` |

Hardware flow control is RTS/CTS; software flow control is XON/XOFF.

What a device is depends on the adapter:

| Driver | `connectTo()` takes | `path()` returns |
| --- | --- | --- |
| `native` | a tty path: `/dev/ttyAMA0`, `/dev/serial0`, `/dev/ttyUSB0`, `/dev/ttyACM0` | the tty path |
| `usb` | an FTDI product name, any case: `ft232h`, `ft2232h`, `ft4232h`, `ft232r`, `ft230x`, `ft4232hp`, `ft4232ha`, or its USB product id in decimal or `0x` hex | `usb:<device>` |

One port is one connection. Connecting a port that is already open throws `UARTException` ("UART port /dev/ttyAMA0 is already connected."). On the `native` driver a path that does not exist, or a port that will not open, throws "UART port [/dev/ttyAMA0] could not be opened.", and one that refuses its line settings throws "could not be configured". On the `usb` driver an unknown product name throws "Invalid FTDI device ...", and a device that will not open or configure throws a message carrying libftdi's own error.

`device()` returns the same transport every time you ask, or `null` when the port was never registered.

## Reading

Everything the device sends is collected into the port's unread buffer, and the reading methods take from it. The buffer holds 64 KB (`GeneralPurposeIO\UART\UARTTransport::BUFFER_BYTES`); if bytes arrive faster than you read them and the buffer fills, the oldest bytes are dropped. `dropped()` counts how many have been lost that way:

```php
if ($gps->dropped() > 0) {
    $this->warn("Lost {$gps->dropped()} bytes: read the GPS more often.");
}
```

Timeouts are in milliseconds. `-1`, the default, waits without limit, and `0` never waits.

### Reading Lines

`readUntil($delimiter, $timeout_ms = -1)` returns everything up to and including the first `$delimiter`, waiting for it if it has not arrived yet. On timeout it returns `null` and leaves the bytes it has so far in the buffer for the next read:

```php
$sentence = $gps->readUntil("\r\n", timeout_ms: 1000);

if ($sentence !== null && str_starts_with($sentence, '$GPGGA')) {
    $fields = explode(',', rtrim($sentence));
}
```

The delimiter must be at least one byte; an empty string throws `UARTException`.

### Reading Bytes

`read($length, $timeout_ms = -1)` returns up to `$length` bytes as a byte array. When unread bytes are waiting, it returns them at once; otherwise it waits for the first ones to arrive. On timeout it returns an empty array:

```php
$frame = $reader->read(12, timeout_ms: 500);   // [] when nothing came
```

### Taking What Has Arrived

`pollBytes($max_bytes = 4096)` returns whatever has arrived, up to `$max_bytes`, as a binary string, and never waits. It suits a sketch's frame loop, where you look at the port once per frame:

```php
$incoming = $modem->pollBytes();
```

### Discarding Input

`flush()` throws away the bytes the port and the transport hold unread, along with anything the operating system still has queued to send. Use it before a command whose answer you want to read cleanly:

```php
$lora->flush();
$lora->write("AT\r\n");
$reply = $lora->readUntil("\r\n", timeout_ms: 500);   // "+OK\r\n"
```

## Writing

`write($data, $timeout_ms = -1)` hands every byte of `$data` (a binary string or a byte array) to the operating system, the tty queue or libusb, and returns how many bytes that was:

```php
$gps->write("\$PMTK220,200*2C\r\n");   // 5 Hz updates
```

The bytes go out in chunks of 256 as the port has room. If the timeout passes before every byte has gone, `write()` throws `UARTException`, and the exception's `sent` and `total` properties tell you how far it got:

```php
use GeneralPurposeIO\Contracts\UART\UARTException;

try {
    $controller->write($frame, timeout_ms: 100);
} catch (UARTException $e) {
    $this->error("Sent {$e->sent} of {$e->total} bytes: {$e->getMessage()}");
}
```

Writes from different fibers never interleave. Each write goes out whole, and a second writer waits for the first to finish, in the order the writes were made.

## Modem Lines

`dtr($asserted)` and `rts($asserted)` assert or release the port's DTR and RTS lines. Many boards and modules wire one of them to reset or boot-mode pins:

```php
// Pulse a module's reset wired to DTR
$module->dtr(true);
usleep(100_000);
$module->dtr(false);
```

A port with no modem control lines (a pseudo-terminal, for example) throws `UARTException` on the `native` driver ("UART port ... cannot set DTR: the device has no modem control lines, or did not answer."), and a line the FTDI chip would not set throws "Could not set DTR on UART port ...". The `usb` driver releases both lines when it opens the port, so a module wired to reset on DTR always boots, whatever the previous run left behind.

## Closing

Because one port is one connection, `close()` on the transport closes the port itself. `connectTo()` opens it again afterwards. `disconnect($device)` on the driver does the same, and also works when no transport was ever handed out:

```php
$gps->close();

// or
app('gpio.uart')->driver('native')->disconnect('/dev/ttyAMA0');
```

Any call on a closed port throws `UARTException` ("UART port /dev/ttyAMA0 is closed."). `closed()` tells you whether it has been closed.

## Blocking and the Event Loop

Without a Venusian [event loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop) bound in the container, every wait sleeps inside the adapter until bytes arrive, the port has room, or the timeout passes.

Once a loop is bound, the same calls share it instead. Inside a fiber started with `$loop->async()`, a waiting `read()`, `readUntil()` or `write()` suspends its fiber; on the main stack, it turns the loop until it finishes, so timers, other ports and other resources keep running while you wait. A port sits on the loop only while it is watched or a call is waiting on it. Your code does not change either way.

UART transports have no `via()`: a serial port is already event-driven, so there is nothing to offload.

### Watching a Port

`watch()` puts the port on the loop and mails every chunk it receives as a `GeneralPurposeIO\Contracts\UART\UARTReceived`. The bytes also stay in the unread buffer, so `read()` and `readUntil()` still see them. `unwatch()` stops the mail, and the port leaves the loop unless a call is waiting on it. `watch()` needs a bound loop and throws `UARTException` without one ("watch() needs an event loop. Boot IOPools, or read() without one.").

A `UARTReceived` carries:

| Property | Holds |
| --- | --- |
| `device` | the port, as you passed it to `connectTo()` |
| `bytes` | the chunk, as a binary string |
| `timestamp` | `CLOCK_MONOTONIC` nanoseconds when the bytes were collected |
| `seqno` | a per-port counter from `1`; a gap means a lost chunk |

Mail is delivered through Venusian's [loop mail](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/loop-mail). Under the `signal` handler each chunk is dispatched as a [signal](https://venusian.projectsaturnstudios.com/docs/framework/digging-deeper/signals) named `gpio.uart.<device>`, so you can listen for one port, a wildcard, or the class:

```php
use GeneralPurposeIO\Contracts\UART\UARTReceived;
use Voyager\Contracts\IOPools\Loop;

app('signals')->listen('gpio.uart./dev/ttyAMA0', fn (UARTReceived $chunk) => print $chunk->bytes);
app('signals')->listen(UARTReceived::class, fn (UARTReceived $chunk) => error_log(strlen($chunk->bytes).' bytes'));

$gps->watch();

app(Loop::class)->run();
```

In a [sketch](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/sketches), the chunks arrive in the `$mail` argument of your next `loop` call:

```php
<?php

namespace App\Runner\Sketches;

use GeneralPurposeIO\Contracts\UART\UARTReceived;
use GeneralPurposeIO\Contracts\UART\UARTTransport;
use Voyager\Contracts\Sketches\SketchLoopResult;

class GpsMonitor extends Sketch
{
    protected string $description = 'Print NMEA sentences as they arrive.';

    private UARTTransport $gps;

    public function boot(): void
    {
        $this->gps = app('gpio.uart')->driver('native')
            ->connectTo('/dev/ttyAMA0')
            ->baud(9600)
            ->register()
            ->device('/dev/ttyAMA0');

        $this->gps->watch();
    }

    public function loop(array $mail = []): SketchLoopResult
    {
        foreach ($mail as $piece) {
            if ($piece instanceof UARTReceived) {
                // The chunk is also in the buffer: take whole sentences from there.
                while (($sentence = $this->gps->readUntil("\r\n", 0)) !== null) {
                    $this->line(rtrim($sentence));
                }
            }
        }

        return SketchLoopResult::CONTINUE;
    }

    public function shutdown(): void
    {
        $this->gps->close();
    }
}
```

`UARTReceived` round-trips through `toData()` and `fromData()`, with the bytes base64-encoded, so a chunk crosses a worker or Redis wire intact.

### Port Failures

When the port fails while the loop is collecting from it (an unplugged USB serial adapter, for example), the port leaves the loop and the failure goes to whichever call is waiting on it. With nothing waiting, it is thrown out of the loop run itself. Every later call on the port throws the same exception. On the `native` driver a hung-up tty shows up as "Could not read from UART port ...".

## Adapters

| | `native` | `usb` |
| --- | --- | --- |
| Package | `microscrap/scrapyard-linux` | `microscrap/scrapyard-usb` |
| Hardware | any Linux tty | FTDI UARTs: FT232H, FT2232H, FT4232H, FT232R, FT230X … |
| `connectTo()` | tty path | product name or id |
| On the loop | the port's descriptor wakes the loop | sampled every 10 ms |

On the `native` driver, reads never block in the kernel (the line is set to return whatever it holds), and waits are `ppoll` calls carrying your timeout, or the loop. On the `usb` driver, the chip's latency timer is set to 1 ms, sends are asynchronous, and on a loop the port is sampled every 10 ms. On an FT2232H or FT4232H the UART is channel A.

One FTDI interface runs either its UART or its MPSSE engine, never both. While a UART holds an interface, [I2C](/docs/{{version}}/scrapyard-io/the-basics/i2c), [SPI](/docs/{{version}}/scrapyard-io/the-basics/spi) and [digital pins](/docs/{{version}}/scrapyard-io/the-basics/digital-pins) on that interface are refused with a `GPIOLevelException`, and the same goes the other way round, until the holder is disconnected.

For the adapters themselves, see [scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/uart) and [scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/uart), and below them [microscrap/uart](/docs/{{version}}/ecosystem/gpio-modules/uart/overview) and the [ftdi extension](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/overview). The [generic GPS](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/generic-gps/overview) driver is a UART chip driver to read alongside this page.

## Errors

Every UART failure throws `GeneralPurposeIO\Contracts\UART\UARTException`, which extends `GeneralPurposeIO\Contracts\Core\GPIOLevelException`. A read that times out is not an exception: `read()` returns `[]` and `readUntil()` returns `null`. A write that cannot finish is: it throws with `sent` and `total` set.

| Thrown when | Message |
| --- | --- |
| No adapter is configured | No UART connection driver is configured. Set gpio.protocols.uart.default to an installed adapter. |
| The port is already connected | UART port /dev/ttyAMA0 is already connected. |
| The port cannot be opened | UART port [/dev/ttyAMA0] could not be opened. |
| The line settings are refused (`native`) | UART port [/dev/ttyAMA0] could not be configured. |
| The FTDI product is unknown (`usb`) | Invalid FTDI device ft9999. |
| The port is closed | UART port /dev/ttyAMA0 is closed. |
| The port failed while reading | Could not read from UART port /dev/ttyAMA0. |
| A write timed out | UART port /dev/ttyAMA0 took no more bytes before the timeout: 512 of 1024 went out. |
| A write failed | Could not write to UART port /dev/ttyAMA0: 512 of 1024 bytes went out. |
| `readUntil()` with an empty delimiter | readUntil() needs a delimiter of at least one byte. |
| A modem line cannot be set | UART port /dev/pts/3 cannot set DTR: the device has no modem control lines, or did not answer. |
| `watch()` without an event loop | watch() needs an event loop. Boot IOPools, or read() without one. |
