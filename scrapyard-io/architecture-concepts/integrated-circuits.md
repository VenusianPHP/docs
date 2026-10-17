# Integrated Circuits

ScrapyardIO gives chip drivers a shared vocabulary, the kinds a chip can be, the two shapes its I/O takes, a boot sequence and register breakouts, and a catalog that builds a live, wired chip from your application's config with one call.

## Introduction

A chip driver, such as the ADXL345 accelerometer or the ST7789 display panel, sits on top of the [transports](/docs/{{version}}/scrapyard-io/architecture-concepts/transports). It knows the chip's registers and its boot sequence; the transport knows how to move bytes. The `gpio/integrated-circuits` package, part of `scrapyard-io/framework`, provides the pieces every chip driver shares:

- **Kinds** that say what a chip is: a sensor, an actuator, a display panel.
- **Chip transports** that give a chip's I/O one of two shapes: register reads and writes, or commands and data.
- **`Bootable`**, a base class for chips that need setting up before use.
- **`DataRegister`**, a base class for breaking a register's byte into named fields.
- **The circuit catalog**, which builds a chip from the wiring in your config.

Chip drivers live in their own packages, published under `dept-of-scrapyard-robotics/*`. The framework catalogs them without knowing any one of them.

## Chip Kinds

Every chip implements `GeneralPurposeIO\Contracts\IntegratedCircuits\IntegratedCircuit`, usually by extending the abstract `GeneralPurposeIO\IntegratedCircuits\IntegratedCircuit` class or `Bootable`. On top of that, a chip implements the kind it is:

| Kind | Implemented by, for example |
|---|---|
| `Contracts\IntegratedCircuits\Sensor` | ADXL343, ADXL345, VL6180X |
| `Contracts\IntegratedCircuits\Actuator` | the Seesaw mini gamepad, the Wii extension controller |
| `Contracts\IntegratedCircuits\DisplayPanel` | SSD1306, SH1106, ST7735, ST7789, ST7796, GC9A01, SSD1680 |

`Sensor` and `Actuator` are marker interfaces with no methods. They exist so your code can type-hint what it accepts. Because they are interfaces rather than base classes, a chip may be more than one kind at once.

`DisplayPanel` does carry methods: `width()`, `height()` and `transmit($origin_x, $origin_y, $raw_data, $frame_width, $frame_height)`, which writes packed bytes into the panel's RAM. A panel then declares what else it can do through `WindowAddressable` (a region write leaves the rest of the panel alone), `PipeablePanel` (it can be fed straight from memory over an SPI bus), `RefreshesOnCommand` (ePaper: writing and showing are separate steps) and `Switchable` (its output can be turned off while RAM keeps its contents). See [Display Panels](/docs/{{version}}/scrapyard-io/digging-deeper/display-panels) for how those are used.

## Chip Transports

A chip's own I/O takes one of two shapes, whichever kind of chip it is. Each is a small contract the chip driver implements over a protocol transport:

| Contract | Methods | Used by |
|---|---|---|
| `Contracts\IntegratedCircuits\ReadWriter` | `read(int $register, int $length): array`, `write(int $register, array $data): int` | register chips: accelerometers, distance sensors |
| `Contracts\IntegratedCircuits\DataCommander` | `command(int $register, array $command_data = []): int`, `data(array\|string $data = []): void` | panels that separate a command byte from a pixel stream |

The chip transport is where one chip talks to several protocols. The ADXL345 speaks both I2C and SPI, so its driver ships one `ReadWriter` for each, and the chip class itself only ever calls `read` and `write`. The I2C one is a thin layer over an `I2CTransport`:

```php
use GeneralPurposeIO\Contracts\I2C\I2CTransport;
use GeneralPurposeIO\Contracts\IntegratedCircuits\ReadWriter;

class TMP102I2CTransport implements ReadWriter
{
    public function __construct(
        protected I2CTransport $transport,
    ) {}

    public function read(int $register, int $length): array
    {
        return $this->transport->writeRead([$register], $length) ?: [];
    }

    public function write(int $register, array $data): int
    {
        return $this->transport->write([$register, ...$data]);
    }
}
```

Register chips that split 16-bit values across two registers may use the `Contracts\NutsAndBolts\Splices16Bits` trait, which splits a value into its high and low bytes and decodes signed little-endian pairs.

## Booting Chips

Most chips need configuring before their first reading: a power mode set, a data format chosen, an ID register checked. The `GeneralPurposeIO\IntegratedCircuits\Bootable` base class gives a chip a boot sequence. You write the steps in a protected `_boot` method, and `Bootable` provides the public `boot()` and `hasBooted()` from the `BootSequence` contract:

```php
<?php

namespace App\Circuits;

use GeneralPurposeIO\Contracts\IntegratedCircuits\Sensor;
use GeneralPurposeIO\IntegratedCircuits\Bootable;

class TMP102 extends Bootable implements Sensor
{
    public function __construct(
        protected readonly TMP102I2CTransport $transport,
        bool $boot_now = false,
    ) {
        parent::__construct($boot_now);
    }

    protected function _boot(): void
    {
        $this->transport->write(0x01, [0x60, 0xA0]);
    }

    public function celsius(): float
    {
        [$msb, $lsb] = $this->transport->read(0x00, 2);

        return (($msb << 4) | ($lsb >> 4)) * 0.0625;
    }
}
```

`boot()` runs `_boot()` once. Calling it again on a chip that has booted does nothing, so code that is handed a chip may call `boot()` without worrying whether someone already did. When the constructor receives `$boot_now` as `true`, the chip boots before the constructor returns.

Code that needs a live chip checks `hasBooted()`. Surface's embedded display manager, for example, refuses to attach a panel that has not booted.

The boot logic lives in the `Contracts\IntegratedCircuits\BootScaffolding` trait, which `Bootable` uses. A chip class that cannot extend `Bootable` may implement `BootSequence` and use the trait directly.

## Register Breakouts

Chip registers pack several settings into one byte. `GeneralPurposeIO\IntegratedCircuits\DataRegister` is an abstract readonly class for breaking one out into named, typed properties. A subclass implements three methods, and `DataRegister` supplies the fourth:

| Method | Returns |
|---|---|
| `toBits(): string` | the register as an eight-character string of `0` and `1`, most significant bit first |
| `toByte(): int` | that string as a byte; provided by `DataRegister` |
| `static fromByte(int $byte): static` | a breakout read back from the chip |
| `static none(): static` | the breakout with every field cleared |

The ADXL345 driver's power control register is a typical breakout:

```php
use GeneralPurposeIO\IntegratedCircuits\DataRegister;

readonly class ADXL345PowerControl extends DataRegister
{
    public function __construct(
        public bool $link = false,
        public bool $measurement_mode = false,
        public bool $sleep_mode = true,
        public ADXL345SleepSamplingRate $wakeup = ADXL345SleepSamplingRate::SLEEP_8HZ,
    ) {}

    public function toBits(): string
    {
        return '000'
            .($this->link ? '1' : '0')
            .($this->measurement_mode ? '1' : '0')
            .($this->sleep_mode ? '1' : '0')
            .$this->wakeup->toBits();
    }

    public static function fromByte(int $byte): static
    {
        $bits = byte2bits($byte);

        return new static($bits[4], $bits[3], $bits[2], ADXL345SleepSamplingRate::from(bindec("{$bits[1]}{$bits[0]}")));
    }

    public static function none(): static
    {
        return new static(false, false, false, ADXL345SleepSamplingRate::SLEEP_8HZ);
    }
}
```

The chip writes `[$power->toByte()]` to its power control register and turns a byte read back from it into a breakout with `fromByte`, so the rest of the driver deals in named fields rather than raw bits.

## The Circuit Catalog

The circuit catalog, `GeneralPurposeIO\IntegratedCircuits\CircuitRegistry`, builds chips from your application's config. It is bound in the container as `circuit`, and aliased by its class and by its contract, `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitRegistry`.

A chip package catalogs each chip it ships under a short **slug**. Your application keeps each chip's wiring in `config/circuits/<slug>.php`. Then one call hands back a wired, booted chip, with no adapter, bus or pin named at the call site:

```php
$accelerometer = app('circuit')->conjure('adxl345');

$left = app('circuit')->conjure('st7789', 'left');
```

### Wiring a Chip

A chip's config file holds one or more named configs and says which one is the default:

```php
// config/circuits/adxl345.php

return [
    'default_config' => 'i2c',
    'configs' => [
        'i2c' => [
            'driver' => 'native',
            'device' => 1,
            'slave' => 0x53,
            'int1' => ['enabled' => true, 'driver' => 'native', 'device' => 0, 'pin' => 17],
        ],
        'spi' => [
            'driver' => 'usb',
            'device' => 'ft232h',
            'chip_select' => 0,
            'speed' => 5_000_000,
        ],
    ],
];
```

Each config's keys are exactly the parameters of one of the chip's public static factory methods. The ADXL345's `i2c` factory reads:

```php
public static function i2c(
    string $driver,
    string|int $device,
    int $slave = ADXL34xI2CAddress::SDO_GROUNDED->value,
    array $int1 = [],
    array $int2 = [],
    bool $boot_now = true,
): static
```

The factory takes the driver's name, asks the `gpio.i2c` manager for that driver, reuses the bus if your application already registered it or connects it if not, wraps the transport in the chip's `ReadWriter`, and constructs the chip. A chip's protocol factory and its config entry are one shape, which is what lets the catalog stay ignorant of both: it knows no chip's constructor and no bus.

### How `conjure` Builds a Chip

`conjure($slug, $config = null)` follows the same steps every time:

1. It finds the class catalogued under `$slug`, or throws `Circuit [adxl345] is not registered.`
2. It reads `config("circuits.{$slug}")`. Without one, it throws an exception telling you to publish the chip package's config into `config/circuits/{$slug}.php`.
3. It takes the config you named, or `default_config` when you named none.
4. It picks the factory. A config is named after its protocol, so the `i2c` config calls the chip's `i2c` factory. When a config sets a `protocol` key, that names the factory instead, so you may keep `left` and `right` configs beside `spi`, both built by `spi`:

```php
'configs' => [
    'left' => ['protocol' => 'spi', 'driver' => 'native', 'device' => 0, 'chip_select' => 0, /* ... */],
    'right' => ['protocol' => 'spi', 'driver' => 'native', 'device' => 0, 'chip_select' => 1, /* ... */],
],
```

5. It calls the factory with the config's keys as named arguments. A key the factory does not declare is dropped. A factory parameter with no default that the config does not carry is an error naming it: `Circuit [adxl345] protocol [i2c] is missing required parameter [device].`
6. It checks the factory returned an `IntegratedCircuit`.

The `build($slug, $protocol, $params)` method skips the config lookup: it finds the class, calls the factory you name with the array you pass, and checks the result, exactly as steps 1, 5 and 6 do. That is useful in tests and in code that assembles wiring at runtime:

```php
$accelerometer = app('circuit')->build('adxl345', 'i2c', [
    'driver' => 'native',
    'device' => 1,
]);
```

Every failure along the way throws a `GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitException`, which descends from `GPIOLevelException` like every other ScrapyardIO exception. The factory must be public and static; one that is not is refused with an exception that says so.

### Inspecting the Catalog

The catalog also answers questions about what is installed. `has($slug)` tells you whether a slug is catalogued, `listCircuits()` returns every slug with its class, and `resolveClass($slug)` returns one class, throwing when the slug is unknown:

```php
if (app('circuit')->has('st7789')) {
    // ...
}

foreach (app('circuit')->listCircuits() as $slug => $class) {
    // 'adxl345' => DeptOfScrapyardRobotics\Sensors\ADXL34x\ADXL345\ADXL345, ...
}
```

## How Chip Packages Register Themselves

A chip package does three things from its service provider, which Venusian finds through the package's `extra.venusian.providers` entry in `composer.json`: it merges its blank config under `circuits.<slug>`, publishes that config to `config/circuits/<slug>.php`, and catalogs its chips. The ADXL34x package's provider is the whole pattern:

```php
<?php

namespace DeptOfScrapyardRobotics\Sensors\ADXL34x\Providers;

use DeptOfScrapyardRobotics\Sensors\ADXL34x\ADXL343\ADXL343;
use DeptOfScrapyardRobotics\Sensors\ADXL34x\ADXL345\ADXL345;
use Voyager\NutsAndBolts\ServiceProvider;

class ADXL34xServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->mergeConfigFrom(dirname(__DIR__, 2).'/config/adxl343.php', 'circuits.adxl343');
        $this->mergeConfigFrom(dirname(__DIR__, 2).'/config/adxl345.php', 'circuits.adxl345');
    }

    public function boot(): void
    {
        $this->publishes([
            dirname(__DIR__, 2).'/config/adxl343.php' => $this->app->configPath('circuits/adxl343.php'),
            dirname(__DIR__, 2).'/config/adxl345.php' => $this->app->configPath('circuits/adxl345.php'),
        ], 'adxl34x-config');

        if ($this->app->isBound('circuit')) {
            $catalog = $this->app->make('circuit');
            $catalog->addCircuit('adxl343', ADXL343::class);
            $catalog->addCircuit('adxl345', ADXL345::class);
        }
    }
}
```

The package's own copy of each config is a blank whose drivers are all `none`; your application publishes it and fills in the bench:

```shell
php computer vendor:publish --tag=adxl34x-config
```

Cataloguing happens in `boot`, after every provider has registered, so the `circuit` binding exists by then whenever `scrapyard-io/framework` or `gpio/integrated-circuits` is installed. The `isBound` check lets the chip package work without the catalog too, constructed by hand from a transport. Nothing is built at boot: `addCircuit` stores a class name, and the chip comes to life only when something calls `conjure`.

`addCircuit` ignores a class that does not implement `IntegratedCircuit` rather than throwing. A catalog is filled from many packages' `boot` methods, and one bad entry should not take the whole application's boot down; the mistake surfaces as `is not registered` the first time you conjure that slug.

Writing the chip side of all this, the chip class, its transports and its protocol factories, is covered step by step in [Writing a Chip Driver](/docs/{{version}}/scrapyard-io/digging-deeper/writing-a-chip-driver).
