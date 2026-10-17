# Choosing an Adapter

The built-in `none` driver, the `native` driver from `microscrap/scrapyard-linux` and the `usb` driver from `microscrap/scrapyard-usb`: which protocols and hardware each one covers, what it needs installed, and how a driver name is registered and selected.

## Introduction

The framework defines what a bus can do; an adapter makes it happen on real hardware. Each adapter is a Composer package that registers one driver name on the protocol managers it supports. Your code asks a manager for a driver by that name, or lets the manager use its configured default, and gets back a driver that opens connections and hands out transports.

There are two first-party adapters, plus a placeholder the framework ships for when neither is installed:

| Driver | Package | I2C | SPI | UART | Digital | PWM | Runs On | Extension |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `none` | `scrapyard-io/framework` | Yes | Yes | Yes | Yes | Yes | Anywhere | None |
| `native` | `microscrap/scrapyard-linux` | Yes | Yes | Yes | Yes | Yes | Linux | `ext-posi` 0.10 |
| `usb` | `microscrap/scrapyard-usb` | Yes | Yes | Yes | Yes | No | Linux, macOS | `ext-ftdi` 0.10 |

Both adapters can live in the same application. A common setup is a Raspberry Pi using `native` for its own buses while an FTDI board on one of its USB ports runs `usb`, or a Mac that uses `usb` while you develop, with the deployed Pi switching to `native`.

## The None Driver

Every protocol manager builds a `none` driver itself, so it exists even before any adapter is installed, and it is the default for every protocol in `config/gpio.php`. It doesn't talk to anything. Its only job is to tell you what is missing: the first `connectTo()` throws the protocol's exception, naming the configuration key to set:

| Manager | Exception | Message |
| --- | --- | --- |
| `gpio.i2c` | `I2CException` | No I2C connection driver is configured. Set gpio.protocols.i2c.default to an installed adapter. |
| `gpio.spi` | `SPIException` | No SPI connection driver is configured. Set gpio.protocols.spi.default to an installed adapter. |
| `gpio.uart` | `UARTException` | No UART connection driver is configured. Set gpio.protocols.uart.default to an installed adapter. |
| `gpio.digital` | `DigitalIOException` | No DigitalIO connection driver is configured. Set gpio.protocols.digital-in.default to an installed adapter. |
| `gpio.pwm` | `PWMException` | No PWM connection driver is configured. Set gpio.protocols.pwm.default to an installed adapter. |

Each exception descends from `GeneralPurposeIO\Contracts\Core\GPIOLevelException`. When you see one, install an adapter and either make its driver the default or name it at the call.

## The Linux Adapter

`microscrap/scrapyard-linux` registers the `native` driver for all five protocols. It talks to the standard Linux kernel interfaces, so it runs on a Raspberry Pi or any Linux board that exposes them:

| Protocol | Kernel Interface | `connectTo()` | `device()` |
| --- | --- | --- | --- |
| I2C | `/dev/i2c-N` (i2c-dev) | bus number | slave address |
| SPI | `/dev/spidevN.CS` (spidev) | bus number | chip select |
| UART | a tty such as `/dev/ttyAMA0` or `/dev/ttyUSB0` | device path | the same path |
| Digital | `/dev/gpiochipN` (libgpiod v2 character device) | chip number | `input()` / `output()` line offset |
| PWM | `/sys/class/pwm/pwmchipN` (sysfs) | chip number | channel |

It needs PHP 8.4 or newer on Linux and `ext-posi` 0.10, which its `composer.json` requires, and pulls in the `microscrap/gpio`, `i2c`, `spi` and `uart` bindings. PWM is driven through plain sysfs files and makes no extension calls of its own. Your user also needs access to the device nodes; [setting up a machine](/docs/{{version}}/scrapyard-io/getting-started/setting-up-a-machine#raspberry-pi-and-linux-device-access) covers the groups and interfaces to enable.

```shell
pie install php-io-extensions/posi

composer require microscrap/scrapyard-linux
```

```php
use GeneralPurposeIO\Contracts\Digital\LineBias;

$fan = app('gpio.i2c')->driver('native')->connectTo(1)->register()->device(1, 0x21);

$pins = app('gpio.digital')->driver('native')->connectTo(0)->register();
$button = $pins->input(0, 27, LineBias::PULL_UP);
```

Because every resource it opens is a file descriptor, the Linux adapter fits the event loop closely: a watched input pin puts its line-request descriptor on the loop and a serial port its tty, so edges and bytes wake the loop directly. Its `via()` jobs run on the application's thread or process worker pool, and each pool worker opens its own bus. The [scrapyard-linux package documentation](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/overview) covers each protocol's details.

## The USB Adapter

`microscrap/scrapyard-usb` registers the `usb` driver on the I2C, SPI, UART and digital managers. It drives FTDI USB boards such as the FT232H through libftdi1, so any machine with a USB port can talk to hardware, including a Mac. It has no PWM driver.

| Protocol | FTDI Engine | Device Names |
| --- | --- | --- |
| I2C, SPI, digital | MPSSE | `ft232h`, `ft2232hl-a`, `ft2232hl-b`, `ft4232hl-a`, `ft4232hl-b`, `ft4232hl-c`, `ft4232hl-d` |
| UART | FTDI serial | a product name such as `ft232h`, `ft2232h`, `ft4232h`, `ft232r` or `ft230x`, or a USB product id such as `0x6014` |

It needs PHP 8.4 or newer on Linux or macOS, the libftdi1 and libusb-1.0 libraries, and `ext-ftdi` 0.10, which its `composer.json` requires. It pulls in the `microscrap/mpsse` bindings. On Linux your user also needs access to the USB device; see [setting up a machine](/docs/{{version}}/scrapyard-io/getting-started/setting-up-a-machine#ftdi-boards).

```shell
pie install php-io-extensions/ftdi

composer require microscrap/scrapyard-usb
```

Where the Linux adapter takes a bus number, the USB adapter takes the board's device name:

```php
$sensor = app('gpio.i2c')->driver('usb')->connectTo('ft232h')->register()->device('ft232h', 0x76);

$id = $sensor->writeRead([0xD0], 1);
```

An FTDI interface runs its MPSSE engine or its UART engine, never both. Once one is registered, opening the other on the same interface throws before any USB traffic, and `disconnect()` frees the interface for the other engine. A UART on an FT2232H or FT4232H uses interface A, the same interface as `ft2232hl-a` and `ft4232hl-a`.

I2C and SPI share their MPSSE interface with the `usb` digital driver, so once you register either one, the board's spare lines are available as pins with no `connectTo()` of their own:

```php
$panel = app('gpio.spi')->driver('usb')->connectTo('ft232h')->speed(10_000_000)->register()->device('ft232h', 0);

$dc = app('gpio.digital')->driver('usb')->output('ft232h', 1);
```

Connect I2C or SPI first when you need both, since SPI refuses an interface the digital driver opened on its own. FTDI pins have no interrupts, so a watched input is sampled on a loop timer, every 10 ms unless you set another interval with `pollEvery($ms)`, and a watched serial port is sampled every 10 ms too. libusb holds the board for your process, so the USB adapter's `via()` jobs stay in it: each one runs in a loop fiber, taking turns with the rest of the interface's traffic, and `via()` takes no pool name. The [scrapyard-usb package documentation](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-usb/overview) covers the MPSSE and UART details.

## How Drivers Are Registered

An adapter registers its driver from its service provider's `boot()` method, by calling `extend` on each manager it supports with the driver name and a closure that builds the driver. This is how `microscrap/scrapyard-linux` registers its I2C driver:

```php
use GeneralPurposeIO\I2C\I2CConnectionManager;
use Microscrap\ScrapyardLinux\I2C\PosixI2CConnectionDriver;

public function boot(): void
{
    $this->app->make(I2CConnectionManager::class)
        ->extend('native', fn () => new PosixI2CConnectionDriver);
}
```

The closure doesn't run until the driver is first asked for. When it does, the manager hands the new driver a way to look up the event loop, and the worker pools on the protocols that offload, at the moment they are needed, so provider order never matters, and then caches it: every later `driver('native')` call returns the same instance, along with the connections registered on it. The [connection managers](/docs/{{version}}/scrapyard-io/architecture-concepts/connection-managers) page covers this in more depth, and [writing an adapter](/docs/{{version}}/scrapyard-io/digging-deeper/writing-an-adapter) shows how to add a driver name of your own.

## Selecting a Driver

You select a driver in one of two ways. Name it on the manager:

```php
$bus = app('gpio.i2c')->driver('usb');
```

Or leave the name out and let the manager use its default, read from `config/gpio.php`:

```php
$bus = app('gpio.i2c')->driver();
```

The default for each protocol is set under `gpio.protocols.<protocol>.default`; see [configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration#choosing-default-drivers). Asking for a name no adapter has registered throws an `InvalidArgumentException` with the message `Driver [name] not supported.`, so a typo, or a `usb` default on the PWM manager, fails at the first call instead of silently using another adapter.

Chips built through the [circuit catalog](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits) take a driver name the same way, as a `driver` entry in the chip's configuration, which the chip's factory passes on to the manager.
