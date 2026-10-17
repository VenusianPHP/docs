# Writing an Adapter

An adapter is the package that connects ScrapyardIO's protocol managers to real hardware. It registers a driver name, such as `native` or `usb`, on each manager it supports, and supplies the connection classes that open a bus and hand out transports. This page shows how both first-party adapters, `microscrap/scrapyard-linux` and `microscrap/scrapyard-usb`, are built, so you can write one for a new kind of hardware.

## Introduction

Each protocol has a connection manager in the container, and each manager hands out drivers by name:

| Container key | Manager | Default from |
| --- | --- | --- |
| `gpio.i2c` | `GeneralPurposeIO\I2C\I2CConnectionManager` | `gpio.protocols.i2c.default` |
| `gpio.spi` | `GeneralPurposeIO\SPI\SPIConnectionManager` | `gpio.protocols.spi.default` |
| `gpio.uart` | `GeneralPurposeIO\UART\UARTConnectionManager` | `gpio.protocols.uart.default` |
| `gpio.digital` | `GeneralPurposeIO\Digital\DigitalOConnectionManager` | `gpio.protocols.digital-in.default` |
| `gpio.pwm` | `GeneralPurposeIO\PWM\PWMConnectionManager` | `gpio.protocols.pwm.default` |

Every manager ships one driver of its own, `none`, which throws an exception naming the config key to set. Every other driver comes from an adapter. The two first-party adapters register these names:

| Adapter | Name | Protocols | Built on |
| --- | --- | --- | --- |
| [microscrap/scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/overview) | `native` | I2C, SPI, UART, digital, PWM | ext-posi: i2c-dev, spidev, termios, libgpiod, sysfs PWM |
| [microscrap/scrapyard-usb](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/overview) | `usb` | I2C, SPI, UART, digital | ext-ftdi: MPSSE on FTDI bridges such as the FT232H |

The managers are explained on the [Connection Managers](/docs/{{version}}/scrapyard-io/architecture-concepts/connection-managers) page. Here we look at the other side of them.

## Registering Driver Names

The managers extend Venusian's `Voyager\NutsAndBolts\Manager`, so an adapter registers a driver with `extend()`, passing a closure that builds the driver. The manager calls the closure, with the container, the first time the driver is asked for and caches the instance it returns. Registration happens in the adapter provider's `boot()` method, after every framework provider has registered its manager. Here is `ScrapyardLinuxServiceProvider`, with its five private `boot*()` helpers folded into `boot()`:

```php
<?php

namespace Microscrap\ScrapyardLinux\Providers;

use GeneralPurposeIO\Digital\DigitalOConnectionManager;
use GeneralPurposeIO\I2C\I2CConnectionManager;
use GeneralPurposeIO\PWM\PWMConnectionManager;
use GeneralPurposeIO\SPI\SPIConnectionManager;
use GeneralPurposeIO\UART\UARTConnectionManager;
use Microscrap\ScrapyardLinux\Digital\PosixDigitalIOConnectionDriver;
use Microscrap\ScrapyardLinux\I2C\PosixI2CConnectionDriver;
use Microscrap\ScrapyardLinux\PWM\PosixPWMConnectionDriver;
use Microscrap\ScrapyardLinux\SPI\PosixSPIConnectionDriver;
use Microscrap\ScrapyardLinux\UART\PosixUARTConnectionDriver;
use Voyager\NutsAndBolts\ServiceProvider;

class ScrapyardLinuxServiceProvider extends ServiceProvider
{
    public function register(): void
    {
    }

    public function boot(): void
    {
        $this->app->make(I2CConnectionManager::class)->extend('native', fn () => new PosixI2CConnectionDriver);
        $this->app->make(SPIConnectionManager::class)->extend('native', fn () => new PosixSPIConnectionDriver);
        $this->app->make(UARTConnectionManager::class)->extend('native', fn () => new PosixUARTConnectionDriver);
        $this->app->make(DigitalOConnectionManager::class)->extend('native', fn () => new PosixDigitalIOConnectionDriver);
        $this->app->make(PWMConnectionManager::class)->extend('native', fn () => new PosixPWMConnectionDriver);
    }
}
```

The manager classes are aliases of their container keys, so `make(I2CConnectionManager::class)` and `make('gpio.i2c')` answer the same instance. List the provider under `extra.venusian.providers` in the adapter's `composer.json` and Venusian discovers it.

Drivers can depend on each other. On an FT232H, I2C, SPI and the pins all share one USB context, so `ScrapyardUSBServiceProvider` builds its I2C and SPI drivers around the `usb` digital driver:

```php
$this->app->make(I2CConnectionManager::class)->extend('usb', fn () => new MpsseI2CConnectionDriver(
    $this->app->make(DigitalOConnectionManager::class)->driver('usb')
));
```

Whatever the closure builds, every manager then hands the driver a closure that finds the event loop at call time, and the I2C, SPI and PWM managers also one that finds the worker pools, so provider order never matters.

## The Three Connection Classes

For each protocol, an adapter extends three abstract classes from that protocol's split: a connection driver, a connection factory and a transport. The application only ever sees them through a four-step chain:

```php
$sensor = app('gpio.i2c')->driver('native')   // the adapter's driver
    ->connectTo(1)                            // your factory for /dev/i2c-1
    ->register()                              // your factory opens it, the driver keeps the handle
    ->device(1, 0x29);                        // your transport for one address
```

The base classes own that chain, the connection bookkeeping, transport caching and offloading. You write the parts that touch hardware.

### The Connection Driver

The driver decides whether a device can be connected, builds transports from a stored handle, and closes handles. These are the methods each protocol's driver leaves to you:

| Protocol | Base class | Abstract methods |
| --- | --- | --- |
| I2C | `GeneralPurposeIO\I2C\I2CConnectionDriver` | `newConnection(int\|string $device): I2CConnectionFactory`, `getTransport(string\|int $device, int $slave_address): I2CTransport`, `closeConnection(mixed $handle): void` |
| SPI | `GeneralPurposeIO\SPI\SPIConnectionDriver` | `newConnection(int\|string $device): SPIConnectionFactory`, `getTransport(int\|string $device, int $chip_select): SPITransport`, `closeConnection(mixed $handle): void` |
| UART | `GeneralPurposeIO\UART\UARTConnectionDriver` | `newConnection(string $device): UARTConnectionFactory`, `getTransport(string $device): UARTTransport`, `closeConnection(mixed $handle): void` |
| Digital | `GeneralPurposeIO\Digital\DigitalIOConnectionDriver` | `newConnection(int\|string $device): DigitalIOConnectionFactory`, `getOutputTransport(string\|int $device, int $pin): DigitalOutTransport`, `getInputTransport(string\|int $device, int $pin, LineBias $bias = LineBias::AS_IS, bool $active_low = false): DigitalInTransport`, `closeConnection(mixed $handle): void` |
| PWM | `GeneralPurposeIO\PWM\PWMConnectionDriver` | `newConnection(int\|string $device): PWMConnectionFactory`, `getTransport(string\|int $device, int $channel): PWMTransport`, `closeConnection(mixed $handle): void` |

`connectTo()` throws when the device is already connected, then calls your `newConnection()`. `device()` returns `null` for a device that was never registered, and otherwise calls your `getTransport()` with the handle stored under that device. `disconnect()` closes every transport on the device, then passes the handle to your `closeConnection()`.

Here is the I2C driver from `scrapyard-linux`. The handle is the file descriptor of `/dev/i2c-N`, shared by every slave on that bus:

```php
<?php

namespace Microscrap\ScrapyardLinux\I2C;

use GeneralPurposeIO\Contracts\I2C\I2CException;
use GeneralPurposeIO\I2C\I2CConnectionDriver;
use GeneralPurposeIO\I2C\I2CTransport;

class PosixI2CConnectionDriver extends I2CConnectionDriver
{
    protected function newConnection(int|string $device): PosixI2CConnectionFactory
    {
        if (is_string($device)) {
            $device = intval($device);
        }

        if (! file_exists("/dev/i2c-{$device}")) {
            throw new I2CException("Device {$device} does not exist");
        }

        return new PosixI2CConnectionFactory($device, $this);
    }

    protected function getTransport(int|string $device, int $slave_address): I2CTransport
    {
        return new PosixI2CTransport($slave_address, $this->connections->get($device));
    }

    /** @param int $handle the /dev/i2c-N fd every slave on the bus shares */
    protected function closeConnection(mixed $handle): void
    {
        posix_close($handle);
    }
}
```

### The Connection Factory

The factory is what `connectTo()` returns. It carries any bus options the application sets before opening, and its `register()` opens the device and stores the handle on the driver. You write two methods, `device()` and `getHandle()`:

```php
<?php

namespace Microscrap\ScrapyardLinux\I2C;

use GeneralPurposeIO\Contracts\I2C\I2CException;
use GeneralPurposeIO\I2C\I2CConnectionFactory;

class PosixI2CConnectionFactory extends I2CConnectionFactory
{
    public function __construct(int $device, PosixI2CConnectionDriver $driver)
    {
        parent::__construct($device, $driver);
    }

    protected function device(): int
    {
        return $this->device;
    }

    protected function getHandle(): int
    {
        // close-on-exec: pool workers and other children open their own bus, never inherit this one
        $fd = posix_open("/dev/i2c-{$this->device}", O_RDWR | O_CLOEXEC);

        if ($fd < 0) {
            throw new I2CException("POSIX I2C handle for [i2c-{$this->device}] could not be opened.");
        }

        return $fd;
    }
}
```

The SPI and UART factories carry options. `SPIConnectionFactory` already provides `mode()`, `speed()` and `endianness()`, and leaves `getHandle()` and `chipSelect(int $chip_select): static` to you, both public. `UARTConnectionFactory` provides `baud()`, `parity()`, `stopBits()`, `dataBits()` and `flowControl()`. Read those properties in `getHandle()` when you open the device.

### The Transport

The transport is the object a chip driver talks to. Each protocol's base transport implements that protocol's contract from `gpio/contracts` partially, and you finish it. For I2C, the base `GeneralPurposeIO\I2C\I2CTransport` validates the address, owns `close()`, `closed()` and `via()`, and leaves you:

- `handle(): mixed` and `release(): void`, which gives back whatever this one transport holds while the bus stays open for the others;
- the contract's IO methods: `probe()`, `read()`, `write()`, `writeRead()` and `bulkWrite()`.

Inside each IO method, call the base class's guards in order: `ensureOpen()` refuses a closed transport, `ensureFits($length)` refuses a message over the 8192-byte cap every I2C adapter holds, and `awaitTurn()` lets this slave's offloaded jobs finish first so blocking calls keep program order. This is `write()` from `PosixI2CTransport`:

```php
public function write(array|string $data): int
{
    if (is_array($data)) {
        $data = array2bytes($data);
    }

    $this->ensureOpen();
    $this->ensureFits(strlen($data));
    $this->awaitTurn();

    $bus = $this->addressedBus();

    if (is_null($bus)) {
        return -1;
    }

    return i2c_write($bus, $data);
}
```

The other protocols follow the same pattern with their own abstract methods. `SPITransport` adds `beginSelection()` and `endSelection()` around a transfer. `UARTTransport` asks for the primitives its buffering and loop integration are built on: `drainBytes()`, `awaitBytes()`, `roomNow()`, `awaitRoom()`, `transmit()`, `purge()`, `intakeStreams()` and `samplingInterval()`. `DigitalInputTransport` asks for `drainEdges()`, `awaitEdges()`, `edgeStreams()` and `samplingInterval()`, which is how its edge watches join the event loop. Read the abstract class for the protocol you are implementing before you start; each method carries a docblock saying what it must do.

## Offloading

The I2C, SPI and PWM drivers use the `GeneralPurposeIO\NutsAndBolts\OffloadsBusJobs` trait, which gives every transport `via()`. Jobs queue one at a time per queue, and the base driver's `dispatch()` sends each one to a worker pool as a gig. The worker builds your driver class anew, connects the same device and runs the job there. For I2C, `BusGig` builds it with `new ($driver)()`, so a driver that keeps the default `dispatch()` needs a constructor without required arguments. The PWM driver passes `workerArguments()`, scalars only, so its worker reaches the same hardware.

When your hardware cannot be opened twice, or has an async path of its own, override `queueKey()` and `dispatch()`. The `usb` I2C driver does both: every slave on one FT232H shares one queue, keyed by the device alone, and each job runs on the event loop in a fiber against the already-open context instead of in a worker:

```php
protected function queueKey(string|int $device, int $address): string
{
    return (string) $device;
}

protected function dispatch(string|int $device, int $address, BusJob $job, ?string $pool, Loop $loop, BusQueue $queue): Promise
{
    /** @var MPSSEContext $context */
    $context = $this->connections->get($device);
    MpssePump::for($context, $loop);

    return $loop->async(function () use ($device, $address, $job, $queue): mixed {
        $queue->claim(Fiber::getCurrent());

        return $job->run($this->device($device, $address));
    });
}
```

It also overrides `offload()` to throw `I2CException::offloadPoolUnsupported()` when a pool is named, since its jobs never go to a worker pool. The [Event Loop](/docs/{{version}}/scrapyard-io/architecture-concepts/event-loop) page covers `via()` from the application side.

## The Adapter Manifest

An adapter requires every `gpio/*` protocol split it extends, plus the PHP extension and the low-level bindings it is built on. Here are the `require` sections of the two first-party adapters, abridged to the GPIO and hardware entries:

| Adapter | Requires |
| --- | --- |
| `microscrap/scrapyard-linux` | `ext-posi`, `gpio/contracts`, `gpio/digital`, `gpio/i2c`, `gpio/nuts-and-bolts`, `gpio/pwm`, `gpio/spi`, `gpio/uart`, `microscrap/gpio`, `microscrap/i2c`, `microscrap/spi`, `microscrap/uart`, `venusian-voyager/nuts-and-bolts` |
| `microscrap/scrapyard-usb` | `ext-ftdi`, `gpio/contracts`, `gpio/digital`, `gpio/i2c`, `gpio/nuts-and-bolts`, `gpio/spi`, `gpio/uart`, `microscrap/mpsse`, `venusian-voyager/nuts-and-bolts` |

Every constraint is on the `^0.10.0` line. An adapter requires the splits rather than `scrapyard-io/framework`, which keeps it installable beside any application that has the framework, since the framework replaces those splits. In the other direction, the protocol splits only `suggest` the adapters, so a machine without the extension still installs the framework. The [Packages](/docs/{{version}}/scrapyard-io/digging-deeper/packages) page has the full dependency picture.

## Testing an Adapter

The framework's own suite tests the managers and base classes against fake drivers, so an adapter's suite covers its own classes. `scrapyard-linux` proves its provider by building real managers on a bare container, booting the provider against them, and checking that each default driver resolves to the adapter's class:

```php
use GeneralPurposeIO\Digital\DigitalOConnectionManager;
use GeneralPurposeIO\I2C\I2CConnectionManager;
use GeneralPurposeIO\PWM\PWMConnectionManager;
use GeneralPurposeIO\SPI\SPIConnectionManager;
use GeneralPurposeIO\UART\UARTConnectionManager;
use Microscrap\ScrapyardLinux\I2C\PosixI2CConnectionDriver;
use Microscrap\ScrapyardLinux\Providers\ScrapyardLinuxServiceProvider;
use Voyager\Config\Repository;
use Voyager\Contracts\Core\FrameworkCore;
use Voyager\Vessel\ControlPanel;

it('boots the native I2C driver', function () {
    $container = new ControlPanel;
    $container->registerInstance('config', new Repository(['gpio' => ['protocols' => ['i2c' => ['default' => 'native']]]]));

    $managers = [
        DigitalOConnectionManager::class => new DigitalOConnectionManager($container),
        I2CConnectionManager::class => new I2CConnectionManager($container),
        SPIConnectionManager::class => new SPIConnectionManager($container),
        PWMConnectionManager::class => new PWMConnectionManager($container),
        UARTConnectionManager::class => new UARTConnectionManager($container),
    ];

    $app = $this->createMock(FrameworkCore::class);
    $app->method('make')->willReturnCallback(fn (string $abstract): object => $managers[$abstract]);

    (new ScrapyardLinuxServiceProvider($app))->boot();

    expect($managers[I2CConnectionManager::class]->driver())->toBeInstanceOf(PosixI2CConnectionDriver::class);
});
```

The provider's `boot()` extends all five managers, so the test hands it all five. For the transports, point the driver at something your tests control rather than at a device: the `scrapyard-linux` PWM driver takes the sysfs root as a constructor argument, and its tests build a throwaway `pwmchip0` tree in a temporary directory, connect to it and assert on the files each call writes.
