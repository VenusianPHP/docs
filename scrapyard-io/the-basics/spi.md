# SPI

Talking to SPI devices from PHP: opening a bus through the `gpio.spi` manager with its mode and clock, selecting a device by chip select, sending and receiving bytes, holding chip select across several calls, and offloading bus work with `via()`.

## Introduction

SPI is the fast, clocked bus that displays, ADCs, flash chips, radios and e-paper panels use. The controller drives a clock, sends bits out on one line and receives bits on another at the same time, and picks which device is listening by pulling that device's **chip select** low. Where I2C devices answer to addresses, SPI devices answer to chip selects.

ScrapyardIO gives you an SPI bus as a **connection**, opened once with its mode, clock and bit order, and each device on it as a **transport**, one per chip select. Chip drivers depend only on the transport contract, `GeneralPurposeIO\Contracts\SPI\SPITransport`, so the same display driver runs on a Raspberry Pi's `/dev/spidev0.0` or on an FT232H.

## Opening a Bus

### The SPI Manager

The SPI connection manager is bound in the container as `gpio.spi`, with `GeneralPurposeIO\SPI\SPIConnectionManager` as an alias. There is no facade or global helper; you resolve the manager and ask it for a driver:

```php
$native = app('gpio.spi')->driver('native');   // microscrap/scrapyard-linux
$usb = app('gpio.spi')->driver('usb');         // microscrap/scrapyard-usb
```

Each driver is built once and reused. Calling `driver()` with no name, or calling a driver method on the manager itself, uses the default from the `gpio.protocols.spi.default` option of your `config/gpio.php` file. That default is `none` until you set it, and the `none` driver throws `SPIException` on every attempt: "No SPI connection driver is configured. Set gpio.protocols.spi.default to an installed adapter." See [Configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration) and [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter).

ScrapyardIO keeps no list of named buses in its config. To keep a chip's wiring (adapter, bus, chip select, clock, data/command pin) in configuration, give it a circuit config and build it with `app('circuit')->conjure(...)`; see [Integrated Circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits).

### Connecting and Configuring

`connectTo($device)` names the bus and returns a connection factory. Set the bus options on the factory, then `register()` opens the bus and returns the driver:

```php
use GeneralPurposeIO\Contracts\SPI\SPIMode;

$driver = app('gpio.spi')->driver('native')
    ->connectTo(0)              // /dev/spidev0.*
    ->mode(SPIMode::MODE_0)
    ->speed(8_000_000)          // Hz
    ->register();
```

| Option | Takes | Default |
| --- | --- | --- |
| `mode($value)` | `GeneralPurposeIO\Contracts\SPI\SPIMode` (`MODE_0` … `MODE_3`) or `0`–`3` | `MODE_0` |
| `speed($hz)` | the clock in Hz | `800_000` |
| `endianness($order)` | `GeneralPurposeIO\Contracts\SPI\SPIEndianness::MSB` or `::LSB` | `MSB` |
| `bitsPerByte($bits)` | word size, `native` only | `8` |
| `clockRate($rate)` | a `Microscrap\Bindings\MPSSE\Enums\MPSSEClockRate`, `usb` only | `FOUR_HUNDRED_KHZ` |

What a device is depends on the adapter:

| Driver | `connectTo()` takes | Opens |
| --- | --- | --- |
| `native` | the bus number | `/dev/spidev<bus>.<chip select>`, one node per chip select |
| `usb` | an MPSSE device name: `ft232h`, `ft2232hl-a`, `ft2232hl-b`, `ft4232hl-a` … `ft4232hl-d` | the FTDI interface, its MPSSE engine in SPI mode |

On the `usb` driver, `speed()` takes any frequency in Hz and `clockRate()` takes one of the enum's rates; whichever of the two you call last decides the clock.

LSB-first bit order is asked of the kernel on the `native` driver. A controller that refuses it (the Raspberry Pi 5's does) still works for 8-bit words: ScrapyardIO reverses the bits in PHP. For any other word size, opening the chip select throws `SPIException`.

A bus is registered once; a second `connectTo()` for it throws `SPIException` ("SPI device 0 is already connected."). On the `native` driver a bus number with no `/dev/spidev<bus>.*` node throws "SPI device 3 does not exist".

### Selecting a Device

`device($device, $chip_select = 0)` returns the transport for one chip select on a registered bus:

```php
$panel = $driver->device(0, 0);   // /dev/spidev0.0
$adc = $driver->device(0, 1);     // /dev/spidev0.1
```

The driver hands out one transport per chip select per bus, so asking twice gives you the same object, and `device()` returns `null` for a bus that was never registered. On the `native` driver each chip select opens its own `/dev/spidev<bus>.<cs>`, and a chip select with no node throws `SPIException` ("/dev/spidev0.2 could not be opened.").

On the `usb` driver, a chip select is a digital pin of the FTDI board: `0`–`3` are D4–D7 and `4`–`11` are C0–C7. Any other number throws `SPIException`. The pin becomes an output for as long as the bus is open, so it is no longer available as a digital input. Every chip select is driven high (deselected) when the bus registers, and the engine's own chip select, D3, stays parked high.

`chipSelect()` returns the transport's chip select, and `closed()` whether it has been closed.

## Talking to a Device

Every write takes either a byte array or a binary string. Every read returns a byte array of integers, or `false` when the bus refused the transfer. Each call asserts the device's chip select for its whole length and releases it at the end, however long the call is: on the `native` driver a call longer than the kernel's `spidev` buffer goes out as several messages with chip select held between them.

### Writing

`write($data)` clocks bytes out and returns how many bytes went out, or `-1` when the bus refused them. Anything the device sends back meanwhile is discarded:

```php
// ST7789 pixel data, straight after a RAMWR command
$panel->write($rgb565_row);
```

### Reading

`read($len)` clocks `$len` bytes in, sending zeros while it does:

```php
$status = $sensor->read(2);
```

### Full-Duplex Transfers

`transfer($data)` sends `$data` and returns the same number of bytes received at the same time. This is the natural shape for devices that answer while you are still talking, such as an MCP3008 ADC:

```php
// MCP3008: start bit, single-ended channel 0, then a byte to clock the answer in
$rx = $adc->transfer([0x01, 0x80 | (0 << 4), 0x00]);

$value = (($rx[1] & 0x03) << 8) | $rx[2];   // 0–1023
```

### Write, Then Read

`writeRead($bytes_to_write, $bytes_to_read)` sends a command, then reads its answer, with chip select held across both halves. Only the answer comes back:

```php
// SPI NOR flash: JEDEC ID
[$manufacturer, $type, $capacity] = $flash->writeRead([0x9F], 3);
```

### Holding Chip Select

Some devices need chip select held across several calls: a display that takes a command byte with its data/command pin low and the parameters with it high, or a radio that expects a register write and a FIFO burst in one selection. `select($body)` runs the closure with the device's chip select held for every call it makes, releases it afterwards (also when the closure throws), and returns whatever the closure returns. The closure receives the transport:

```php
$dc = app('gpio.digital')->driver('native')->connectTo(0)->register()->output(0, 25);

$panel->select(function ($panel) use ($dc) {
    $dc->low();
    $panel->write([0x2A]);                     // CASET
    $dc->high();
    $panel->write([0x00, 0x00, 0x00, 0xEF]);   // columns 0–239
});
```

While a `select()` runs, the bus belongs to that device. Another device's call on the same bus from the same code path throws `SPIException` ("SPI device 0 is held by chip select 0's select(): only that slave may use it until select() returns."). A call from somewhere else (another fiber, a queued job) waits until `select()` returns. Calling `select()` again inside the closure on the same device simply runs the inner closure inside the outer selection.

On the `native` driver, every call and every whole `select()` also takes a lock on the bus, `/run/lock/scrapyard-spi<bus>.lock`, so another process using a different chip select on the same bus can never drive the wire in the middle of your selection.

### Per-Device Clock

Devices on one bus often run at different speeds. `speed($hz)` gives a transport its own clock from then on; until you call it, the device runs at the connection's speed. `clock()` returns the device's own clock, or `null` while it uses the connection's:

```php
$panel->speed(40_000_000);
$adc->speed(1_350_000);

$adc->clock();   // 1350000
```

On the `native` driver the kernel checks the speed at once and a refused speed throws `SPIException` ("/dev/spidev0.0 refused a clock of ... Hz."). On the `usb` driver the engine clock is switched whenever a device with a different clock takes the bus.

### Writing From Memory

The `native` transport also implements `GeneralPurposeIO\Contracts\SPI\WritesFromMemory`. `writeFrom($spans)` sends bytes straight from memory addresses, each span an `[address, length]` pair, under one chip select, without copying them into PHP strings. It is how a panel is fed directly from an `ext-fb` framebuffer; see [Display Panels](/docs/{{version}}/scrapyard-io/digging-deeper/display-panels). It returns the number of bytes written, or `-1` when the bus refused the write. A transport whose bits are reversed in software (LSB first on a controller that refuses it) cannot send from memory and throws `SPIException`.

## Closing

`close()` closes one transport: on the `native` driver it closes that chip select's `/dev/spidev` node, and the bus stays open for the other devices. Called inside that device's `select()`, the close waits until chip select goes up. The next `device()` call for that chip select hands you a fresh transport. Any call on a closed transport throws `SPIException` ("SPI chip select 0 is closed.").

`disconnect($device)` closes every transport on the bus, then the bus itself, and forgets its settings. `connectTo()` can open it again afterwards.

## Blocking and the Event Loop

Every call on an SPI transport is blocking: it returns once the transfer is done. With a Venusian [event loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop) bound, a call that has to wait for the bus (because another fiber's `select()` holds it, or because offloaded jobs are queued ahead of it) waits on the loop, so timers and other resources keep running meanwhile. Without a loop there is nothing to wait on, so a call that finds the bus held by another fiber's `select()` throws the "is held by chip select" `SPIException` instead.

### Offloading With via()

`via($pool)` returns a handle with the same calls (`write`, `read`, `transfer`, `writeRead`, and `run`), each returning a `Voyager\Contracts\IOPools\Promise` that settles with what the blocking call returns, or rejects with what it throws:

```php
$adc->via()->transfer([0x01, 0x80, 0x00])
    ->then(fn (array $rx) => $this->line('Channel 0: '.((($rx[1] & 0x03) << 8) | $rx[2])))
    ->error(fn (Throwable $e) => $this->error($e->getMessage()));
```

| Driver | `via()` | `via('thread')` / `via('process')` |
| --- | --- | --- |
| `native` | the thread worker pool when it is enabled, the process pool otherwise | that worker pool |
| `usb` | a fiber on the event loop, sharing the FT232H's USB pump | refused: throws `SPIException` |

On the `native` driver, a pool worker opens the bus with the same mode, speed, bit order and word size this process registered it with, and runs the device at its own clock. A bus you registered by hand, without going through `connectTo()->register()`, has no recorded settings, and offloading on it throws `SPIException`. On the `usb` driver libusb holds the device for this process, so jobs run here in loop fibers and every USB exchange takes its turn on the device's pump.

`via()` needs a bound event loop: without one, the first call on the handle throws `GPIOLevelException` ("via() needs an event loop. Boot IOPools, or call the blocking method."). With a loop but no worker pool enabled, the promise rejects with an `InvalidArgumentException` naming the option to turn on (`io-pools.pool_workers.threads.enabled` or `io-pools.pool_workers.process.enabled`; see [Named Pools](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#named-pools)).

### Ordering

Every device on a bus shares one queue of offloaded jobs, because a job may hold chip select across several messages and two jobs on one bus must never overlap. Jobs run one at a time, in the order you queued them. A blocking call first waits for the jobs queued on the bus before it, and for a `select()` running elsewhere, so mixing blocking and offloaded calls never reorders your traffic. A `select()` outside the queue pauses it and waits for the running job, so the bus is that device's alone from chip select down to chip select up.

`close()` lets the device's running job finish and rejects its queued jobs; a `via()` handle checks its device on every call, so it never outlives the transport.

### Holding Chip Select Off-Thread

The `via()` handle has no `select()`. To hold chip select across several calls on the far side, ship a `GeneralPurposeIO\Contracts\NutsAndBolts\BusJob` that calls `select()` on the transport it receives, and run it with `run()`:

```php
<?php

namespace App\Jobs;

use GeneralPurposeIO\Contracts\NutsAndBolts\BusJob;
use GeneralPurposeIO\Contracts\NutsAndBolts\GPIOTransport;
use GeneralPurposeIO\Contracts\SPI\SPITransport;

final class ReadFlashPage implements BusJob
{
    public function __construct(
        public readonly int $address,
    ) {}

    public function run(GPIOTransport $bus): array
    {
        /** @var SPITransport $bus */
        return $bus->select(fn (SPITransport $flash) => $flash->writeRead([
            0x03,                               // READ
            ($this->address >> 16) & 0xFF,
            ($this->address >> 8) & 0xFF,
            $this->address & 0xFF,
        ], 256));
    }
}
```

```php
$page = $flash->via()->run(new ReadFlashPage(0x001000))->wait();
```

A job may cross to a worker, so it holds only scalar state, and its class must be autoloadable there.

## Adapters

| | `native` | `usb` |
| --- | --- | --- |
| Package | `microscrap/scrapyard-linux` | `microscrap/scrapyard-usb` |
| Hardware | Linux `spidev` | FTDI MPSSE: FT232H, FT2232H, FT4232H |
| Chip select | `/dev/spidev<bus>.<cs>` | a digital pin, `0`–`11` |
| Options | `mode`, `speed`, `endianness`, `bitsPerByte` | `mode`, `speed`, `endianness`, `clockRate` |
| `writeFrom()` | yes | no |
| `via()` | worker pools | loop fiber on the USB pump |

On an FTDI board, the SPI driver opens the MPSSE context and shares it with the `usb` digital driver, so the lines you do not use as chip selects stay usable as [digital pins](/docs/{{version}}/scrapyard-io/the-basics/digital-pins), such as a display's data/command and reset lines. Because of that, connect SPI first: if the digital driver already opened that board, `connectTo()` throws `SPIException` ("ft232h is already open for I2C or DigitalIO: its one MPSSE engine runs one protocol at a time."). One FTDI interface runs either its MPSSE engine or its UART: while a [UART](/docs/{{version}}/scrapyard-io/the-basics/uart) holds it, `connectTo()` throws `GPIOLevelException`.

For the adapters themselves, see [scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/spi) and [scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/concepts/mpsse), and below them [microscrap/spi](/docs/{{version}}/ecosystem/gpio-modules/spi/overview) and [microscrap/mpsse](/docs/{{version}}/ecosystem/gpio-modules/mpsse/overview). The [ST77xx](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/overview) display driver is a complete SPI chip driver to read alongside this page.

## Errors

Every SPI failure throws `GeneralPurposeIO\Contracts\SPI\SPIException`, which extends `GeneralPurposeIO\Contracts\Core\GPIOLevelException`. A transfer the bus refused is not an exception: `read`, `transfer` and `writeRead` return `false`, and `write` and `writeFrom` return `-1`.

| Thrown when | Message |
| --- | --- |
| No adapter is configured | No SPI connection driver is configured. Set gpio.protocols.spi.default to an installed adapter. |
| The bus is already registered | SPI device 0 is already connected. |
| A chip select's node cannot be opened (`native`) | /dev/spidev0.2 could not be opened. |
| LSB first with a word size other than 8 on a controller that refuses it (`native`) | SPI device 0 cannot send 16-bit words LSB first: ... |
| A per-device clock is refused (`native`) | /dev/spidev0.0 refused a clock of ... Hz. |
| The chip select is not a usable pin (`usb`) | Pin 12 cannot be a chip select on ft232h: use a DigitalIO pin, 0-3 (D4-D7) or 4-11 (C0-C7). |
| Another device's `select()` holds the bus | SPI device 0 is held by chip select 0's select(): only that slave may use it until select() returns. |
| The transport is closed | SPI chip select 0 is closed. |
| The bus lock cannot be taken (`native`) | The SPI bus lock /run/lock/scrapyard-spi0.lock could not be opened or taken. |
| Offloading a bus registered without its factory | SPI device 0 was registered without its connection factory, ... |
| A named pool is asked of the `usb` driver | MPSSE SPI transfers run on the device's own USB pump; they cannot go to the [thread] worker pool. |
| `writeFrom()` on a bit-reversing transport | SPI device [/dev/spidev0.0] reverses bits in software; bytes sent straight from memory cannot be reversed without a copy. |
