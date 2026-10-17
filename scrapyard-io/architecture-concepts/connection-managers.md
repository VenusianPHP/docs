# Connection Managers

Every protocol ScrapyardIO speaks has a connection manager: one object in the container that hands out drivers by name, and the drivers open buses, chips and ports and hand out transports for them.

## Introduction

ScrapyardIO talks to five kinds of hardware: I2C buses, SPI buses, UART ports, digital pins and PWM channels. Each one has a **connection manager** bound in the [service container](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/container). A manager does not talk to hardware itself. It hands out **drivers** by name, and a driver is what opens a connection and hands out [transports](/docs/{{version}}/scrapyard-io/architecture-concepts/transports) on it.

The framework ships no hardware drivers of its own. Adapter packages register them: `microscrap/scrapyard-linux` adds a driver named `native` to each manager, and `microscrap/scrapyard-usb` adds one named `usb`. Until an adapter is installed and chosen, every manager hands out its built-in `none` driver.

The managers are registered by `GeneralPurposeIO\Core\Providers\ScrapyardIOServiceProvider`, which Venusian discovers automatically when you install `scrapyard-io/framework`:

| Container key | Manager | Default driver config |
|---|---|---|
| `gpio.i2c` | `GeneralPurposeIO\I2C\I2CConnectionManager` | `gpio.protocols.i2c.default` |
| `gpio.spi` | `GeneralPurposeIO\SPI\SPIConnectionManager` | `gpio.protocols.spi.default` |
| `gpio.uart` | `GeneralPurposeIO\UART\UARTConnectionManager` | `gpio.protocols.uart.default` |
| `gpio.digital` | `GeneralPurposeIO\Digital\DigitalOConnectionManager` | `gpio.protocols.digital-in.default` |
| `gpio.pwm` | `GeneralPurposeIO\PWM\PWMConnectionManager` | `gpio.protocols.pwm.default` |

Each manager is also aliased by its class name, so you may type-hint `I2CConnectionManager` wherever the container injects dependencies, or resolve it with `app('gpio.i2c')`.

## Drivers

A manager's `driver` method returns the driver registered under a name. Called without a name, it returns the default driver named in your `config/gpio.php` file:

```php
$native = app('gpio.i2c')->driver('native');

$default = app('gpio.i2c')->driver();
```

A manager builds each driver once and returns the same instance every time it is asked for that name. That matters, because the driver is where connections live: every part of your application that asks the `gpio.i2c` manager for its `native` driver shares the same open buses.

The manager also passes any method it does not have itself to its default driver, so `app('gpio.i2c')->connectTo(1)` is the same as `app('gpio.i2c')->driver()->connectTo(1)`.

### Choosing Default Drivers

The framework's `config/gpio.php` file sets every protocol's default to `none`. Publish it to choose the drivers your machine uses:

```shell
php computer vendor:publish --tag=gpio-config
```

```php
return [
    'protocols' => [
        'uart' => ['default' => 'native'],
        'i2c' => ['default' => 'native'],
        'spi' => ['default' => 'native'],
        'digital-in' => ['default' => 'native'],
        'digital-out' => ['default' => 'native'],
        'pwm' => ['default' => 'native'],
    ],
];
```

One `gpio.digital` manager serves both input and output pins, and it reads its default from the `digital-in` key. Naming the driver explicitly, as most examples in these pages do, works whatever the defaults are, so you may mix adapters in one application: a Raspberry Pi's own I2C bus through `native` beside an FT232H's SPI bus through `usb`.

### The `none` Driver

Every manager has a `none` driver built in: `NoneI2CConnectionDriver`, `NoneSPIConnectionDriver`, `NoneUARTConnectionDriver`, `NoneDigitalIOConnectionDriver` and `NonePWMConnectionDriver`. It is what an application without an adapter gets, and it refuses every attempt to open a connection with an exception that names the configuration key to set:

```
No I2C connection driver is configured. Set gpio.protocols.i2c.default to an installed adapter.
```

Because the `none` driver never opens anything, an application can install `scrapyard-io/framework` and boot on a machine with no hardware at all. Nothing fails until code actually tries to reach a bus.

### Adapter Driver Names

Adapters register their drivers from their own service provider's `boot` method, using the manager's `extend` method. The two adapters register these names:

| Adapter | Driver name | Managers |
|---|---|---|
| `microscrap/scrapyard-linux` | `native` | `gpio.i2c`, `gpio.spi`, `gpio.uart`, `gpio.digital`, `gpio.pwm` |
| `microscrap/scrapyard-usb` | `usb` | `gpio.i2c`, `gpio.spi`, `gpio.uart`, `gpio.digital` |

The `usb` adapter has no PWM driver, so `app('gpio.pwm')->driver('usb')` throws `Driver [usb] not supported.` See [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter) for what each one needs, and the [scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/overview) and [scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/overview) pages for their details.

## The Connection Lifecycle

Every protocol follows the same lifecycle. You pick a driver, start a connection with `connectTo`, open it with `register`, and then ask the driver for transports with `device`, `input` or `output`:

```php
$bus = app('gpio.i2c')->driver('native')
    ->connectTo(1)      // a connection factory for /dev/i2c-1
    ->register();       // open it and keep it on the driver

$display = $bus->device(1, 0x3C);
$fan = $bus->device(1, 0x21);
```

### Connecting

The `connectTo` method returns a **connection factory** for one device: an I2C or SPI bus, a GPIO chip, a PWM chip or a serial port. Nothing is opened yet. The factory is where you set a connection's options before it opens. SPI factories take `mode`, `speed`, `endianness` and `chipSelect`; UART factories take `baud`, `parity`, `stopBits`, `dataBits` and `flowControl`:

```php
use GeneralPurposeIO\Contracts\SPI\SPIMode;
use GeneralPurposeIO\Contracts\UART\Parity;

$spi = app('gpio.spi')->driver('native')
    ->connectTo(0)
    ->mode(SPIMode::MODE_3)
    ->speed(5_000_000)
    ->register();

$serial = app('gpio.uart')->driver('native')
    ->connectTo('/dev/ttyAMA0')
    ->baud(115_200)
    ->parity(Parity::NONE)
    ->register();
```

An SPI factory defaults to mode 0, 800 kHz and most-significant bit first. A UART factory defaults to 9600 baud, eight data bits, no parity, one stop bit and no flow control. Adapters may add options of their own to their factories; the adapter's pages list them.

### Named Connections

The factory's `register` method opens the connection and stores its handle on the driver under the device's name, then returns the driver. That name is whatever you passed to `connectTo`: a bus number such as `1`, a GPIO chip number such as `0`, a serial path such as `/dev/ttyAMA0`, or, on the `usb` driver, an FTDI product name such as `ft232h`. From then on, you refer to the connection by that name:

```php
$pins = app('gpio.digital')->driver('native')->connectTo(0)->register();

$led = $pins->output(0, 17);
$button = $pins->input(0, 27);
```

A driver holds each name once. Calling `connectTo` for a name that is already registered throws, so register a connection once, usually in a service provider or at the start of a command, and call `device` as often as you need afterwards. Every driver exposes its open connections on its readonly `connections` property, a `Voyager\NutsAndBolts\Collection` keyed by name, so code that might run after the connection exists can check before opening it:

```php
$bus = app('gpio.i2c')->driver('native');

if (! $bus->connections->has(1)) {
    $bus->connectTo(1)->register();
}
```

Chip drivers do exactly this: when a chip is built from its config, it reuses a bus the application already registered and connects one only when it is missing.

### Handing Out Transports

Once a connection is registered, the driver hands out transports on it. The method and its arguments depend on the protocol:

| Manager | Hands out | Keyed by |
|---|---|---|
| `gpio.i2c` | `device($bus, $address)` | bus and 7-bit slave address |
| `gpio.spi` | `device($bus, $chip_select = 0)` | bus and chip select |
| `gpio.uart` | `device($port)` | port: one transport per connection |
| `gpio.digital` | `output($chip, $pin)`, `input($chip, $pin, $bias, $active_low)` | chip and line offset |
| `gpio.pwm` | `device($chip, $channel)` | PWM chip and channel |

Each of these returns `null` when the named connection was never registered, rather than opening it behind your back.

I2C, SPI and PWM drivers keep one transport per key. Asking for the same address, chip select or channel again returns the same transport, and once that transport has been closed, the next request hands out a fresh one. A UART driver keeps one transport per port, and that port *is* the connection: closing the port closes the connection too, so you call `connectTo` again to reopen it.

### Disconnecting

A driver's `disconnect` method closes everything on one connection and forgets it. For a bus or chip, it closes every transport the driver handed out on it, then closes the connection's handle. For a UART port, it closes the port. Afterwards, `connectTo` may open the same name again:

```php
app('gpio.i2c')->driver('native')->disconnect(1);
```

Closing a single transport is different. A transport's `close` method gives back only what that one transport holds: the Linux line request for a pin, the export of a PWM channel. The bus stays open for every other device on it. The [Transports](/docs/{{version}}/scrapyard-io/architecture-concepts/transports) page covers what closing a transport guarantees.

## Extending a Manager

A manager's `extend` method registers a driver under a name. It takes the name and a closure that builds the driver; the closure receives the container. This is how both adapters register `native` and `usb`, and you may use it the same way to add a driver of your own, typically from a service provider's `boot` method:

```php
<?php

namespace App\Providers;

use App\Hardware\BenchI2CConnectionDriver;
use GeneralPurposeIO\I2C\I2CConnectionManager;
use Voyager\NutsAndBolts\ServiceProvider;

class BenchServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap any application services.
     */
    public function boot(I2CConnectionManager $manager): void
    {
        $manager->extend('bench', fn () => new BenchI2CConnectionDriver);
    }
}
```

The closure is not called until something asks for the driver, and the manager builds the driver once. An extended name takes precedence over a built-in one, so you may also use `extend` to replace the `none` driver.

The closure must return a driver of the protocol's base class: `GeneralPurposeIO\I2C\I2CConnectionDriver`, `SPI\SPIConnectionDriver`, `UART\UARTConnectionDriver`, `Digital\DigitalIOConnectionDriver` or `PWM\PWMConnectionDriver`. Those base classes carry the connection lifecycle described above, and the manager relies on them: as it builds every driver, built in or extended, it hands the driver a closure that looks up the [event loop](/docs/{{version}}/scrapyard-io/architecture-concepts/event-loop) when it is needed, and for I2C, SPI and PWM a second one that finds the worker pool `via()` offloads to. Because both lookups happen when the driver uses them rather than when it is built, the order your providers boot in never matters, and an IOPools loop bound after the driver was created still counts.

A driver built with `new` outside its manager has neither lookup. It still works for every blocking call, but it cannot offload, and its `via()` calls throw an exception saying so.

Writing the driver class itself, with its connection factory and transports, is covered in [Writing an Adapter](/docs/{{version}}/scrapyard-io/digging-deeper/writing-an-adapter).
