# Configuration

The `config/gpio.php` file and its default driver per protocol, how your copy merges with the framework's, publishing it, and where the wiring for individual chips is configured instead.

## Introduction

ScrapyardIO keeps its configuration small. The framework ships one file, `config/gpio.php`, and its only job is to say which driver each protocol manager uses when you call `driver()` without a name. There are no connection definitions and no environment variables in it: you open a bus in code, with the driver, device and options you pass to `connectTo()`, and when you want that wiring in configuration instead, it lives with the chip in the [circuit catalog](#chip-wiring).

## The GPIO Configuration File

This is the framework's `config/gpio.php`:

```php
return [
    'protocols' => [
        'uart' => [
            'default' => 'none',
        ],
        'i2c' => [
            'default' => 'none',
        ],
        'spi' => [
            'default' => 'none',
        ],
        'digital-in' => [
            'default' => 'none',
        ],
        'digital-out' => [
            'default' => 'none',
        ],
        'pwm' => [
            'default' => 'none',
        ],
    ],
];
```

Each manager reads its default with a fallback of `none`, so a protocol that has no entry at all also uses the `none` driver:

| Key | Read By | Default |
| --- | --- | --- |
| `gpio.protocols.i2c.default` | `gpio.i2c` | `none` |
| `gpio.protocols.spi.default` | `gpio.spi` | `none` |
| `gpio.protocols.uart.default` | `gpio.uart` | `none` |
| `gpio.protocols.digital-in.default` | `gpio.digital` | `none` |
| `gpio.protocols.pwm.default` | `gpio.pwm` | `none` |

The `gpio.digital` manager drives input and output pins alike, and it takes its default from `digital-in`. The file also carries a `digital-out` entry, which no manager reads in 0.10, so the `digital-in` value is the one that decides the default for both directions.

### Choosing Default Drivers

The value of each `default` is a driver name: `none`, or a name an installed adapter registered, which is `native` for `microscrap/scrapyard-linux` and `usb` for `microscrap/scrapyard-usb`. On a Raspberry Pi with the Linux adapter, you would make `native` the default everywhere:

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

With a default in place, `driver()` with no name returns it, and a manager forwards any method it does not have to its default driver, so these three lines open the same bus:

```php
app('gpio.i2c')->driver('native')->connectTo(1);

app('gpio.i2c')->driver()->connectTo(1);

app('gpio.i2c')->connectTo(1);
```

Naming the driver works whatever the defaults are, which is how you use both adapters in one application: keep `native` as the default for the Pi's own buses and name `usb` where an FTDI board is involved. A name that no adapter registered fails when it is first used, with `Driver [name] not supported.`, and the `usb` adapter registers nothing on `gpio.pwm`, so `usb` is not a valid PWM default. See [choosing an adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter) for which adapter supports which protocol.

## Publishing the Configuration

The framework's copy of `config/gpio.php` is merged in automatically, so you only need a file of your own when you want to change a default. The service provider publishes the file under the `gpio-config` tag:

```shell
php computer vendor:publish --tag=gpio-config
```

This copies the file to your application's `config/gpio.php`. `vendor:publish` will not overwrite a file you already have unless you pass `--force`.

### How Your File Is Merged

The provider merges the framework's file with yours one level deep: each top-level key in your `config/gpio.php` replaces the framework's. Since everything sits under `protocols`, your `protocols` array replaces the framework's whole, and any protocol you leave out of it falls back to `none`. This file sets `native` for I2C and leaves every other protocol on `none`:

```php
return [
    'protocols' => [
        'i2c' => ['default' => 'native'],
    ],
];
```

You may read the values back with the `config` helper, like any other Venusian configuration:

```php
$driver = config('gpio.protocols.i2c.default');
```

The file has no `env()` calls, so the defaults are the same on every machine that runs the application. If your workstation drives an FTDI board while the deployed Pi uses its own buses, you may read a default from the environment yourself:

```php
'i2c' => ['default' => env('GPIO_I2C_DRIVER', 'native')],
```

`GPIO_I2C_DRIVER` here is your own variable, not one ScrapyardIO defines. When you [cache your configuration](https://venusian.projectsaturnstudios.com/docs/framework/getting-started/configuration#configuration-caching) with `php computer config:cache`, the merged `gpio` values are cached with everything else, so run it again after you change the file.

## Chip Wiring

The wiring for a particular part, such as which bus, chip select and pins a display is on, is not part of `config/gpio.php`. Each chip package catalogs its chip in the `circuit` registry and publishes its own configuration file, `config/circuits/<slug>.php`, which your application edits. The framework reads it as `circuits.<slug>`:

```php
// config/circuits/st7789.php
return [
    'default_config' => 'spi',

    'configs' => [
        'spi' => [
            'driver' => 'usb', 'device' => 'ft232h', 'chip_select' => 0,
            'speed' => 10_000_000, 'width' => 320, 'height' => 240,
            'dc'  => ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 1],
            'rst' => ['driver' => 'usb', 'device' => 'ft232h', 'pin' => 2],
        ],
    ],
];
```

`default_config` names the configuration `conjure()` uses when you don't name one, and `configs` holds one entry per wiring you keep. A configuration is named after its protocol unless it sets a `protocol` key, so you may keep `left` and `right` beside `spi`. The keys inside an entry are the arguments of the chip's static factory for that protocol, so each chip package documents its own; the `driver` key in it is a driver name, just like the defaults above:

```php
$panel = app('circuit')->conjure('st7789');

$left = app('circuit')->conjure('st7789', 'left');
```

A missing file, a missing `default_config`, an unknown configuration name, or a factory argument the entry does not provide each throws a `CircuitException` that names what is missing. The [integrated circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits) page covers the catalog in full.

## Worker Pool Configuration

On the `native` adapter, offloading bus work with `via()` runs on Venusian's worker pools, which ScrapyardIO does not configure itself. `via()` needs an event loop and a pool that is on, enabled with `io-pools.pool_workers.threads` or `io-pools.pool_workers.process` in your application's `config/io-pools.php`; without one, it throws an exception that says which pool to enable. The `usb` adapter keeps its jobs in your process, because libusb holds the device there, and runs them in a loop fiber on its own USB pump instead. See [the event loop](/docs/{{version}}/scrapyard-io/architecture-concepts/event-loop) and Venusian's [concurrency](https://venusian.projectsaturnstudios.com/docs/framework/digging-deeper/concurrency) documentation.
