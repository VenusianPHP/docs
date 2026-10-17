# I2C

Talking to I2C devices from PHP: opening a bus through the `gpio.i2c` manager, addressing a device on it, reading and writing its registers, and moving bus work off the calling thread with `via()`.

## Introduction

I2C is the two-wire bus most small sensors and controllers sit on: temperature and pressure sensors, light sensors, accelerometers, small OLED displays, port expanders. One bus carries many devices, and each answers to its own 7-bit address. Your code is always the controller; it picks an address, writes bytes to it, and reads bytes back.

ScrapyardIO gives you an I2C bus as a **connection** and each device on it as a **transport**. The connection is opened once, by an adapter, and stays open. Transports are cheap views on it: one per address, each sending its own traffic on the shared bus. Chip drivers depend only on the transport contract, `GeneralPurposeIO\Contracts\I2C\I2CTransport`, so the same driver runs on a Raspberry Pi's `/dev/i2c-1` or on an FT232H plugged into your laptop.

## Opening a Bus

### The I2C Manager

The I2C connection manager is bound in the container as `gpio.i2c`, with `GeneralPurposeIO\I2C\I2CConnectionManager` as an alias. There is no facade or global helper; you resolve the manager and ask it for a driver:

```php
$i2c = app('gpio.i2c');

$native = $i2c->driver('native');   // microscrap/scrapyard-linux
$usb = $i2c->driver('usb');         // microscrap/scrapyard-usb
```

Each driver is built once and then reused, so every part of your application that asks for `driver('native')` shares the same open buses.

Calling `driver()` with no name, or calling a driver method on the manager itself, uses the default driver from the `gpio.protocols.i2c.default` option of your `config/gpio.php` file:

```php
// config/gpio.php
'protocols' => [
    'i2c' => ['default' => 'native'],
    // ...
],
```

```php
$bus = app('gpio.i2c')->connectTo(1)->register();   // the default driver
```

The default is `none` until you set it. The `none` driver opens nothing: every attempt throws an `I2CException` that names the option to set:

```
No I2C connection driver is configured. Set gpio.protocols.i2c.default to an installed adapter.
```

See [Configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration) for publishing the config file, and [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter) for which adapter fits your machine.

ScrapyardIO keeps no list of named buses in its config: you name the adapter, then the bus by its device. When you want a chip's wiring (adapter, bus, address) kept in configuration rather than at the call site, give it a circuit config and build it with `app('circuit')->conjure(...)`; see [Integrated Circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits).

### Connecting and Registering

Opening a bus takes two calls. `connectTo($device)` names the bus and hands back a connection factory; `register()` opens it, keeps the handle on the driver, and returns the driver:

```php
$bus = app('gpio.i2c')->driver('native')
    ->connectTo(1)    // /dev/i2c-1
    ->register();
```

What a device is depends on the adapter:

| Driver | `connectTo()` takes | Opens |
| --- | --- | --- |
| `native` | the bus number, as an `int` or a numeric string | `/dev/i2c-<n>` |
| `usb` | an MPSSE device name: `ft232h`, `ft2232hl-a`, `ft2232hl-b`, `ft4232hl-a` … `ft4232hl-d` | the FTDI interface, its MPSSE engine in I2C mode |

The `usb` factory also takes the bus clock before you register, as a `Microscrap\Bindings\MPSSE\Enums\MPSSEClockRate`. It runs at `FOUR_HUNDRED_KHZ` unless you say otherwise:

```php
use Microscrap\Bindings\MPSSE\Enums\MPSSEClockRate;

$bus = app('gpio.i2c')->driver('usb')
    ->connectTo('ft232h')
    ->clockRate(MPSSEClockRate::ONE_HUNDRED_KHZ)
    ->register();
```

A bus is registered once. Calling `connectTo()` for a bus the driver already holds throws `I2CException` ("Device 1 already connected"); after registering, simply call `device()` as often as you need. On the `native` driver, a bus number with no `/dev/i2c-<n>` throws "Device 5 does not exist", and a node that cannot be opened (usually a permissions problem) throws when you `register()`.

### Addressing a Device

`device($device, $address)` returns the transport for one address on a registered bus:

```php
$driver = app('gpio.i2c')->driver('native');
$driver->connectTo(1)->register();

$barometer = $driver->device(1, 0x76);
$light = $driver->device(1, 0x29);
```

The driver hands out one transport per address per bus, so asking twice gives you the same object. If the bus was never registered, `device()` returns `null`. Addresses must lie between `0x03` and `0x77`; anything outside that range throws `I2CException` ("Only valid address between 0x03 and 0x77 allowed").

Transports on the same bus share its connection. On the `native` driver every transport uses the one `/dev/i2c-<n>` descriptor, and each call selects its own address before it touches the wire, so you never have to think about which device spoke last.

## Talking to a Device

Every write takes either a byte array (`[0xF4, 0x27]`) or a binary string (`"\xF4\x27"`). Every read returns a byte array of integers, or `false` when the bus refused the transfer.

### Probing

`probe()` asks whether anything answers at the transport's address. It is the quickest way to check your wiring before you start talking to a chip:

```php
if (! $barometer->probe()) {
    throw new RuntimeException('No barometer at 0x76: check the wiring and the address pin.');
}
```

### Writing

`write($data)` sends bytes to the device in one message and returns how many bytes went out, or `-1` when the bus refused them. Most register-based chips take the register address as the first byte and the value after it:

```php
// BMP280: ctrl_meas (0xF4) = temperature x1, pressure x1, normal mode
$barometer->write([0xF4, 0x27]);
```

### Reading

`read($len)` reads `$len` bytes from the device:

```php
$bytes = $barometer->read(2);   // [0x80, 0x00], or false
```

A plain read continues from wherever the chip's own register pointer is. To read a particular register, use `writeRead`.

### Reading a Register

`writeRead($bytes_to_write, $bytes_to_read)` writes, then reads, as a single transaction with a repeated START between the two halves, so nothing else on the bus can slip in. This is how you read a register: write its address, then read its value:

```php
// BMP280: chip id register 0xD0 reads 0x58
[$id] = $barometer->writeRead([0xD0], 1);

// BMP280: pressure and temperature, six bytes from 0xF7
$raw = $barometer->writeRead([0xF7], 6);

$pressure = ($raw[0] << 12) | ($raw[1] << 4) | ($raw[2] >> 4);
$temperature = ($raw[3] << 12) | ($raw[4] << 4) | ($raw[5] >> 4);
```

### Writing Several Messages

`bulkWrite($messages)` sends a list of messages to the device, each one its own I2C message, and returns the length of each message, or `false` when the bus refused one. It is the fast way to stream a display's command list or a frame of pixel data:

```php
// SSD1306 init: control byte 0x00, then each command
$display->bulkWrite([
    [0x00, 0xAE],          // display off
    [0x00, 0xD5, 0x80],    // clock divide
    [0x00, 0xA8, 0x3F],    // multiplex 64
    [0x00, 0xAF],          // display on
]);
```

`bulkWrite` accepts a single binary string (one message), a flat byte array (one message), or a list of strings and byte arrays (one message each). On the `native` driver, the messages go to the kernel 42 at a time in one `I2C_RDWR` transfer, with a STOP between batches. On the `usb` driver, each message starts with a repeated START and the whole list ends with one STOP.

### Message Size

The Linux `i2c-dev` driver caps one message at 8192 bytes, and both adapters hold to the same cap so a chip driver behaves identically on either. A longer write, read, or `bulkWrite` chunk throws `I2CException` before anything is sent ("9000 bytes is longer than the 8192-byte I2C message limit"). Split larger payloads into several messages with `bulkWrite`. The cap is available as `GeneralPurposeIO\I2C\I2CTransport::MAX_MESSAGE`.

### Address and State

`address()` returns the transport's address, and `closed()` tells you whether it has been closed:

```php
$barometer->address();  // 0x76
$barometer->closed();   // false
```

## Closing

`close()` closes one transport. It holds nothing of its own on the bus, so closing it leaves the bus open for every other device on it, and the next `device()` call for that address hands you a fresh transport. Any call on a closed transport throws `I2CException` ("I2C slave 0x76 is closed.").

`disconnect($device)` closes every transport on the bus, then the bus itself. Afterwards `connectTo()` can open it again:

```php
$driver->disconnect(1);
```

A chip driver should close its transport, never the bus: other chips may be sharing it.

## Blocking and the Event Loop

Every call on an I2C transport is a blocking call: it returns once the transfer is done. I2C transfers are short, so for most work this is exactly what you want, in a Computer command and in a [sketch](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/sketches) alike.

When a transfer is long, or you would rather not hold up the [event loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop) while it runs, offload it with `via()`.

### Offloading With via()

`via($pool)` returns a handle with the same calls as the transport, each returning a `Voyager\Contracts\IOPools\Promise` that settles with what the blocking call would have returned, or rejects with what it would have thrown. From a sketch, for example:

```php
$barometer->via()->writeRead([0xF7], 6)
    ->then(fn (array $raw) => $this->line('Pressure raw: '.(($raw[0] << 12) | ($raw[1] << 4) | ($raw[2] >> 4))))
    ->error(fn (Throwable $e) => $this->error($e->getMessage()));
```

The handle offers `write`, `read`, `writeRead`, `bulkWrite`, and `run`. You may also wait for the result where you are; [waiting on a promise](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#waiting-on-a-promise) turns the loop while it waits, so timers and other resources keep running:

```php
$raw = $barometer->via()->writeRead([0xF7], 6)->wait();
```

Where the work runs depends on the adapter and on `$pool`:

| Driver | `via()` | `via('thread')` / `via('process')` |
| --- | --- | --- |
| `native` | the thread worker pool when it is enabled, the process pool otherwise | that worker pool |
| `usb` | a fiber on the event loop, sharing the FT232H's USB pump | refused: throws `I2CException` |

On the `native` driver, a pool worker opens its own copy of the bus and keeps it open for later jobs. The pools come from Venusian's IOPools; enable them with `io-pools.pool_workers.threads.enabled` or `io-pools.pool_workers.process.enabled` (see [Named Pools](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#named-pools)). On the `usb` driver, libusb holds the device for this process, so jobs stay here: each runs in a loop fiber, and every USB exchange it makes takes its turn on the device's pump.

`via()` needs a bound event loop. Without one, the first call on the handle throws `GPIOLevelException` ("via() needs an event loop. Boot IOPools, or call the blocking method."). With a loop but no worker pool enabled, the promise rejects with an `InvalidArgumentException` naming the option to turn on.

### Ordering

Offloaded jobs keep the order you queued them in:

- On the `native` driver each device has its own queue: jobs for one address run one at a time, in call order, while different addresses run side by side.
- On the `usb` driver the whole bridge shares one queue, because one MPSSE engine drives the bus.
- A blocking call on a device first waits for the jobs already queued for it, so mixing blocking and offloaded calls never reorders your traffic. It waits only for jobs queued before it, not for ones queued afterwards.
- `close()` lets the running job finish and rejects the queued ones with "I2C slave 0x76 is closed."; a `via()` handle checks its device on every call, so it never outlives the transport.

A pool worker's exception comes back as the ScrapyardIO exception it was, with the worker's trace kept as its previous exception, so `->error()` receives the same `I2CException` a blocking call would have thrown.

### Multi-Step Jobs

When one piece of work needs several transfers in a row, ship it as a `GeneralPurposeIO\Contracts\NutsAndBolts\BusJob` and run it with `via()->run($job)`. The job's `run` method receives the transport on whichever side it lands (a pool worker, or a loop fiber on a USB bridge) and uses the ordinary blocking calls:

```php
<?php

namespace App\Jobs;

use GeneralPurposeIO\Contracts\I2C\I2CTransport;
use GeneralPurposeIO\Contracts\NutsAndBolts\BusJob;
use GeneralPurposeIO\Contracts\NutsAndBolts\GPIOTransport;

final class ReadBmp280 implements BusJob
{
    public function run(GPIOTransport $bus): array
    {
        /** @var I2CTransport $bus */
        return [
            'calibration' => $bus->writeRead([0x88], 24),
            'raw' => $bus->writeRead([0xF7], 6),
        ];
    }
}
```

```php
$barometer->via()->run(new ReadBmp280)
    ->then(function (array $reading) {
        $this->latest = $reading;
    });
```

A job may cross to a worker, so it holds only scalar state, and its class must be autoloadable there.

## Adapters

| | `native` | `usb` |
| --- | --- | --- |
| Package | `microscrap/scrapyard-linux` | `microscrap/scrapyard-usb` |
| Hardware | Linux `/dev/i2c-<n>` (`i2c-dev`) | FTDI MPSSE: FT232H, FT2232H, FT4232H |
| `connectTo()` | bus number | MPSSE device name |
| `via()` | worker pools | loop fiber on the USB pump |

On an FTDI board, the I2C driver shares its MPSSE context with the `usb` digital driver, so the spare lines stay usable as [digital pins](/docs/{{version}}/scrapyard-io/the-basics/digital-pins) without connecting anything else, and disconnecting the I2C bus closes those pins first. One FTDI interface runs either its MPSSE engine or its UART, never both: while a [UART](/docs/{{version}}/scrapyard-io/the-basics/uart) holds the interface, `connectTo()` throws `GPIOLevelException` until the port is disconnected.

For the adapters themselves, see [scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/i2c) and [scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/mpsse), and below them [microscrap/i2c](/docs/{{version}}/ecosystem/gpio-modules/i2c/overview) and [microscrap/mpsse](/docs/{{version}}/ecosystem/gpio-modules/mpsse/overview).

## Errors

Every I2C failure throws `GeneralPurposeIO\Contracts\I2C\I2CException`, which extends `GeneralPurposeIO\Contracts\Core\GPIOLevelException`, the root of everything ScrapyardIO throws. A transfer the bus refused is not an exception: `read`, `writeRead`, and `bulkWrite` return `false`, and `write` returns `-1`, so a chip driver decides what a refused transfer means for its chip.

| Thrown when | Message |
| --- | --- |
| No adapter is configured | No I2C connection driver is configured. Set gpio.protocols.i2c.default to an installed adapter. |
| The bus is already registered | Device 1 already connected |
| The address is out of range | Only valid address between 0x03 and 0x77 allowed. Requested: [...]. |
| A message is too long | 9000 bytes is longer than the 8192-byte I2C message limit. |
| The transport is closed | I2C slave 0x76 is closed. |
| A named pool is asked of the `usb` driver | MPSSE I2C transfers run on the device's own USB pump; they cannot go to the [thread] worker pool. |
| `via()` without an event loop | via() needs an event loop. Boot IOPools, or call the blocking method. (`GPIOLevelException`) |
