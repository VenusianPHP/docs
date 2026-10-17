# Installation

What ScrapyardIO is, what it needs, how to add it to a Venusian application, what its service provider binds, and how to install the adapter that connects it to real hardware.

## Meet ScrapyardIO

ScrapyardIO is a Venusian package for talking to hardware. It gives your application one API for I2C, SPI, UART, digital pins and PWM, whether the bus is a Raspberry Pi's own or a USB board such as the FTDI FT232H plugged into your laptop.

The `scrapyard-io/framework` package gives each protocol a connection manager and defines the transports that chip drivers are written against. Adapter packages plug in the actual hardware, and chip drivers sit on top. From the bottom up, the stack looks like this:

| Layer | Packages | What it does |
| --- | --- | --- |
| PHP extensions | `ext-posi`, `ext-ftdi` | One-to-one POSIX, ioctl, termios and libftdi calls |
| Bindings | `microscrap/gpio`, `i2c`, `spi`, `uart`, `mpsse` | libgpiod, i2c-dev, spidev, termios and MPSSE written in PHP |
| Adapters | `microscrap/scrapyard-linux`, `microscrap/scrapyard-usb` | The `native` and `usb` drivers for each protocol |
| Framework | `scrapyard-io/framework` | Protocol managers, transports, the circuit catalog |
| Chip drivers | `dept-of-scrapyard-robotics/*` | Sensors, displays, servos and other parts |

### Why ScrapyardIO?

#### One API for Every Bus

Every protocol connects the same way: pick a driver, connect to a device, register the connection, and ask it for a transport. Reading a register from a device at `0x21` on a Raspberry Pi's `i2c-1` looks like this:

```php
$device = app('gpio.i2c')->driver('native')
    ->connectTo(1)       // open /dev/i2c-1
    ->register()         // keep the connection on the driver
    ->device(1, 0x21);   // a transport for one address on it

$bytes = $device->writeRead([0xFC], 1);
```

Swap `native` for `usb` and `1` for `ft232h`, and the same code runs against an FT232H on a Mac. The protocol pages, starting with [I2C](/docs/{{version}}/scrapyard-io/the-basics/i2c), cover each one.

#### Chip Drivers That Don't Care About Your Board

A chip driver depends only on the transport contracts in `GeneralPurposeIO\Contracts`, never on an adapter. The same sensor or display driver works on a Pi's own bus and on a USB bridge. With the [circuit catalog](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits), the wiring moves into your application's configuration and `app('circuit')->conjure('st7789')` hands back a wired chip.

#### Blocking When You Want It, Async When You Need It

Every call blocks by default, so a short script that reads a sensor is a few lines of plain PHP. When your application binds a Venusian [event loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop), the same calls share it: waits stop blocking the process, input pins and serial ports can mail what they receive, and bus work can be offloaded to a worker pool with `via()`. See [the event loop](/docs/{{version}}/scrapyard-io/architecture-concepts/event-loop).

#### Small Packages When You Need Them

The framework is also published as components, such as `gpio/i2c` and `gpio/contracts`, so a chip driver can depend on less than the whole framework. See [packages](/docs/{{version}}/scrapyard-io/digging-deeper/packages).

## Requirements

ScrapyardIO needs:

- PHP 8.4 or newer.
- A Venusian 0.10 application. ScrapyardIO requires the `venusian-voyager/*` 0.10 components, and its providers, configuration and commands run inside a booted Venusian application.
- At least one adapter, and the PHP extension that adapter needs:

| Adapter | Driver Name | Protocols | Hardware | Extension |
| --- | --- | --- | --- | --- |
| `microscrap/scrapyard-linux` | `native` | I2C, SPI, UART, digital, PWM | Linux `i2c-dev`, `spidev`, serial ports, `libgpiod` character devices, sysfs PWM | `ext-posi` 0.10 |
| `microscrap/scrapyard-usb` | `usb` | I2C, SPI, UART, digital | FTDI boards such as the FT232H, on Linux or macOS | `ext-ftdi` 0.10 |

[Choosing an adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter) compares the two in detail.

## Installing ScrapyardIO

### Creating a Venusian Application

If you don't have a Venusian application yet, install the Venusian installer with Composer and create one. The [Venusian installation guide](https://venusian.projectsaturnstudios.com/docs/framework/getting-started/installation) covers PHP, the installer and the new application in full:

```shell
composer global require venusian/installer

venusian new some-app

cd some-app
```

### Adding the Framework

From your application's root, require the framework with Composer:

```shell
composer require scrapyard-io/framework
```

The service provider, `GeneralPurposeIO\Core\Providers\ScrapyardIOServiceProvider`, is discovered automatically, so there is nothing to add to your application's providers.

### What the Service Provider Binds

The provider merges the framework's `config/gpio.php` under the `gpio` key, registers the `scrapyard:ext` and `scrapyard:modules` Computer commands, and binds one connection manager per protocol plus the circuit catalog. Each binding is a singleton, and each class name is an alias of its key, so you may resolve a manager with `app('gpio.i2c')` or inject `I2CConnectionManager`:

| Container Key | Class |
| --- | --- |
| `gpio.i2c` | `GeneralPurposeIO\I2C\I2CConnectionManager` |
| `gpio.spi` | `GeneralPurposeIO\SPI\SPIConnectionManager` |
| `gpio.uart` | `GeneralPurposeIO\UART\UARTConnectionManager` |
| `gpio.digital` | `GeneralPurposeIO\Digital\DigitalOConnectionManager` |
| `gpio.pwm` | `GeneralPurposeIO\PWM\PWMConnectionManager` |
| `circuit` | `GeneralPurposeIO\IntegratedCircuits\CircuitRegistry` |

The catalog is also bound as `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitRegistry`. The [connection managers](/docs/{{version}}/scrapyard-io/architecture-concepts/connection-managers) page explains how a manager builds and caches its drivers.

Until an adapter is installed, every manager only knows the built-in `none` driver. Its job is to tell you what is missing: the first `connectTo()` throws an exception that names the configuration key to set:

```
No I2C connection driver is configured. Set gpio.protocols.i2c.default to an installed adapter.
```

### Installing an Adapter

An adapter needs its PHP extension, so install the extension first. The `scrapyard:ext` command builds and installs `ext-posi` and `ext-ftdi` through [PIE](https://github.com/php/pie), and `scrapyard:modules` then offers the adapters and bindings your operating system and extensions can run:

```shell
php computer scrapyard:ext

php computer scrapyard:modules
```

If you would rather do it by hand, install the extension with PIE and require the adapter with Composer. On a Raspberry Pi or another Linux board:

```shell
pie install php-io-extensions/posi

composer require microscrap/scrapyard-linux
```

For an FTDI board, install libftdi1 and libusb first, as described in [setting up a machine](/docs/{{version}}/scrapyard-io/getting-started/setting-up-a-machine#ftdi-boards), then:

```shell
pie install php-io-extensions/ftdi

composer require microscrap/scrapyard-usb
```

The adapter's service provider is discovered automatically too, and registers its driver name on every manager it supports. You may then name the driver at each call, as in `app('gpio.i2c')->driver('native')`, or make it the default for each protocol in `config/gpio.php`; see [configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration).

## Next Steps

Now that ScrapyardIO is installed, these pages finish the setup:

- [Configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration)
- [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter)
- [Setting Up a Machine](/docs/{{version}}/scrapyard-io/getting-started/setting-up-a-machine)

Then pick the bus your hardware speaks: [I2C](/docs/{{version}}/scrapyard-io/the-basics/i2c), [SPI](/docs/{{version}}/scrapyard-io/the-basics/spi), [UART](/docs/{{version}}/scrapyard-io/the-basics/uart), [digital pins](/docs/{{version}}/scrapyard-io/the-basics/digital-pins) or [PWM](/docs/{{version}}/scrapyard-io/the-basics/pwm). When you are ready to wire a real part, read about [integrated circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits) and browse the chip drivers in the [Dept. of Scrapyard Robotics](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/ssd1306/overview) packages.
