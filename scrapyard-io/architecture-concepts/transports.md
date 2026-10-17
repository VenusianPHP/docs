# Transports

A transport is one device's handle on a connection: an I2C address, an SPI chip select, a serial port, a pin or a PWM channel. Chip drivers are written against the transport contracts, never against an adapter, which is what lets one driver run on a Raspberry Pi's own bus and on an FTDI USB board without a change.

## Introduction

When you ask a driver for `device(1, 0x3C)`, you get back a **transport**: an object that reads and writes one device on a connection the driver owns. Every transport implements a contract from the `GeneralPurposeIO\Contracts` namespace, and those contracts are the whole surface a chip driver needs. The ADXL345 accelerometer driver, for example, accepts any `GeneralPurposeIO\Contracts\I2C\I2CTransport`; it never learns whether the bytes travel through Linux's `i2c-dev` or an FT232H's MPSSE engine.

The contracts live in the `gpio/contracts` package, which `scrapyard-io/framework` includes. A chip package may require `gpio/contracts` alone and leave the choice of adapter, and of the rest of the framework, to the application.

## Where Transports Sit

ScrapyardIO is a stack of packages, each written against the one below it:

```
ext-posi / ext-ftdi                 1:1 POSIX and libftdi calls in C
  → microscrap/*                    libgpiod, i2c-dev, spidev, termios and libmpsse in PHP
    → microscrap/scrapyard-*        adapters: the `native` and `usb` drivers
      → scrapyard-io/framework      connection managers, transports, circuits
        → dept-of-scrapyard-robotics/*   chip drivers
```

At the bottom, the [posi](/docs/{{version}}/ecosystem/standalone-extensions/posi/overview) and [ftdi](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/overview) extensions expose system calls and libftdi one to one. The `microscrap/*` packages build each protocol in PHP on top of them: [microscrap/gpio](/docs/{{version}}/ecosystem/gpio-modules/gpio/overview), [microscrap/i2c](/docs/{{version}}/ecosystem/gpio-modules/i2c/overview), [microscrap/spi](/docs/{{version}}/ecosystem/gpio-modules/spi/overview) and [microscrap/uart](/docs/{{version}}/ecosystem/gpio-modules/uart/overview) over ext-posi, and [microscrap/mpsse](/docs/{{version}}/ecosystem/gpio-modules/mpsse/overview) over ext-ftdi.

The adapters, [microscrap/scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/overview) and [microscrap/scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/overview), are where those libraries meet ScrapyardIO. Each adapter extends the framework's abstract driver, factory and transport classes for every protocol it supports, and registers its drivers on the [connection managers](/docs/{{version}}/scrapyard-io/architecture-concepts/connection-managers). The adapters depend on the framework's split packages (`gpio/contracts`, `gpio/i2c` and so on), not on the whole framework.

Above the framework, the Dept. of Scrapyard Robotics chip drivers, such as [ADXL34x](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/adxl34x/overview) and [ST77xx](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/st77xx/overview), accept transports by contract. Everything a chip driver does to the hardware goes through the methods on this page.

## The Contracts

Every transport extends `GeneralPurposeIO\Contracts\NutsAndBolts\GPIOTransport`, which has two methods: `close()` and `closed(): bool`. Each protocol adds its own:

| Contract | Methods |
|---|---|
| `I2C\I2CTransport` | `probe()`, `read($len)`, `write($data)`, `writeRead($bytes_to_write, $bytes_to_read)`, `bulkWrite($messages)`, `via($pool)` |
| `SPI\SPITransport` | `read($len)`, `write($data)`, `transfer($data)`, `writeRead($bytes_to_write, $bytes_to_read)`, `select($body)`, `speed($hz)`, `chipSelect()`, `via($pool)` |
| `UART\UARTTransport` | `read($length, $timeout_ms)`, `readUntil($delimiter, $timeout_ms)`, `write($data, $timeout_ms)`, `pollBytes($max_bytes)`, `flush()`, `dropped()`, `dtr($asserted)`, `rts($asserted)`, `path()`, `watch()`, `unwatch()` |
| `Digital\DigitalOutTransport` | `low()`, `high()`, `read()`, `write($state)` |
| `Digital\DigitalInTransport` | `read()`, `pollEdges($rising_events, $falling_events)`, `listen($timeout, $rising_events, $falling_events)`, `watch($rising_events, $falling_events)`, `unwatch()` |
| `PWM\PWMTransport` | `getPeriod()`, `setPeriod($value)`, `getDutyCycle()`, `setDutyCycle($value)`, `getEnable()`, `setEnable($value)`, `getPolarity()`, `setPolarity($value)`, `channel()`, `via($pool)` |

The [I2C](/docs/{{version}}/scrapyard-io/the-basics/i2c), [SPI](/docs/{{version}}/scrapyard-io/the-basics/spi), [UART](/docs/{{version}}/scrapyard-io/the-basics/uart), [Digital Pins](/docs/{{version}}/scrapyard-io/the-basics/digital-pins) and [PWM](/docs/{{version}}/scrapyard-io/the-basics/pwm) pages walk through each protocol's methods in use. The rest of this page covers what every transport has in common.

### Bytes In and Out

Byte-oriented writes take either an array of integers or a binary string, so `write([0x00, 0xAF])` and `write("\x00\xAF")` send the same two bytes. Reads return an array of integers.

I2C and SPI reads return `false` when the bus refuses the transfer, and their writes return the number of bytes written. The PWM setters return the value read back from the hardware after the write, so you see what the channel actually accepted.

The framework's global helpers `array2bytes()`, `bytes2array()`, `byte2bits()` and `bits2byte()` convert between the two forms and individual bits.

### Timeouts

The calls that wait take their timeout in milliseconds. `-1` waits without limit and `0` never waits. A digital input's `listen` returns `null` when the timeout passes without a matching edge. A UART `read` returns `[]`, and `readUntil` returns `null` and leaves the bytes it has seen unread. A UART `write` that cannot hand every byte to the operating system in time throws a `UARTException` whose `sent` and `total` properties say how far it got.

### Offloaded Transports

The I2C, SPI and PWM contracts have a `via` method that returns the same calls as promises: `OffloadedI2C`, `OffloadedSPI` and `OffloadedPWM`. Each promise settles with exactly what the blocking call would have returned, or rejects with exactly what it would have thrown. Each also has a `run` method that takes a `GeneralPurposeIO\Contracts\NutsAndBolts\BusJob`, so a chip driver can send several steps as one job. [Event Loop](/docs/{{version}}/scrapyard-io/architecture-concepts/event-loop#offloading-with-via) covers when `via` is available and where the work runs.

## What a Transport Guarantees

The contracts are only useful to a chip driver if every adapter behaves the same behind them. These are the rules every transport the framework hands out keeps, whichever adapter built it.

### One Transport Per Device

A driver hands out one transport per I2C address, SPI chip select or PWM channel on a connection, and one per UART port. Asking again for the same device returns the same object, so two parts of your application that talk to the chip at `0x3C` share one transport. Once that transport is closed, the next request hands out a fresh one.

### A Transport Is a View on Its Connection

The bus belongs to the driver, not to the transport. Every transport on I2C bus `1` shares the bus's one connection; each call simply addresses its own device. Closing a transport gives back only what that device alone holds: a pin's line request, a PWM channel's export. Every other device on the bus keeps working.

That is why a chip driver's own `close` method should close the chip's pins and leave the bus alone: other chips may share it. The bus closes when the application calls `disconnect` on the driver, which closes every transport on it first.

A UART port is the exception, because a port has nothing else on it: the port is the connection, and closing it closes both.

### Closed Means Closed

Once a transport is closed, `closed()` returns `true` and every further call throws the protocol's exception, such as `I2C slave 0x3C is closed.` or `UART port /dev/ttyAMA0 is closed.`. Calling `close` again does nothing. A transport never reopens itself; you ask the driver for a fresh one.

Closing an I2C, SPI or PWM transport that has offloaded work queued rejects the jobs that have not started, lets the running one finish, and then closes. An SPI transport closed from inside its own `select` closure is released once its chip select goes up.

### Device Limits Are Checked Up Front

A transport refuses requests the protocol cannot carry before anything reaches the wire. An I2C transport accepts only addresses from `0x03` to `0x77` and refuses a message longer than 8192 bytes, the limit Linux's `i2c-dev` sets, which every adapter holds to. An SPI transport inside another slave's `select` on the same stack refuses to use the bus, rather than corrupting the selected slave's transfer.

### Errors Share One Root

Every exception a transport, driver or connection factory throws descends from `GeneralPurposeIO\Contracts\Core\GPIOLevelException`, with one subclass per protocol: `I2CException`, `SPIException`, `UARTException`, `DigitalIOException` and `PWMException`. You may catch one protocol's failures, or every hardware failure at once without naming a protocol:

```php
use GeneralPurposeIO\Contracts\Core\GPIOLevelException;

try {
    $bytes = $sensor->writeRead([0x32], 6);
} catch (GPIOLevelException $e) {
    report($e);
}
```

The managers themselves throw `InvalidArgumentException` for a mistake in your own code rather than in the hardware: asking for a driver name nothing registered, or offloading to a worker pool that does not exist or is not enabled.

## From Connection to Transport

The path from a connection to a transport is the same for every protocol, and following it once explains what a driver keeps and why:

```php
$bus = app('gpio.i2c')->driver('native');   // 1. the driver: one per name, shared app-wide

$factory = $bus->connectTo(1);              // 2. a connection factory: options, nothing open yet

$factory->register();                       // 3. opens /dev/i2c-1, stores the handle on the driver as "1"

$sensor = $bus->device(1, 0x53);            // 4. a transport for one address on connection "1"
```

1. The manager builds the driver once and hands it the lookups it needs for the event loop and worker pools.
2. `connectTo` checks the name is not already connected and returns the adapter's factory for it.
3. The factory's `register` opens the hardware and stores the handle on the driver's `connections` collection under the name. An SPI factory also records the settings the bus was opened with, so a pool worker can open the same bus the same way later.
4. `device` looks up the connection by name. If the driver already holds a live transport for that key, it returns it. Otherwise it asks the adapter for a new transport over the stored handle and attaches it to the driver and the connection name, so the transport can queue offloaded work on its driver and close cleanly.

`device` returns `null` at step 4 when the connection was never registered. A chip driver that builds its own connection uses that to decide:

```php
$bus = app('gpio.i2c')->driver($driver);

$i2c = $bus->device($device, $slave)
    ?? $bus->connectTo($device)->register()->device($device, $slave);
```

This is how the Dept. of Scrapyard Robotics drivers connect themselves: a bus your application already opened is shared as it is, and a missing one is opened for the chip.

The adapter's side of this, the factory's `getHandle` and the driver's `getTransport` and `closeConnection`, is described in [Writing an Adapter](/docs/{{version}}/scrapyard-io/digging-deeper/writing-an-adapter). Writing a chip driver on top of the contracts is described in [Writing a Chip Driver](/docs/{{version}}/scrapyard-io/digging-deeper/writing-a-chip-driver).
