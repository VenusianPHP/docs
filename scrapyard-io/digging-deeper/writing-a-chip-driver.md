# Writing a Chip Driver

A chip driver is a Composer package that teaches ScrapyardIO one integrated circuit: what kind of chip it is, how it talks over its bus, what it does when it boots, and how an application builds it from config. This page walks through each of those decisions and ends with a complete, small driver modelled on the Dept of Scrapyard Robotics VL6180X time-of-flight sensor.

## Introduction

Every Dept of Scrapyard Robotics package follows the same shape, and yours should too:

| Piece | Job |
| --- | --- |
| The chip class | Extends `Bootable`, implements its kind (`Sensor`, `Actuator` or `DisplayPanel`), and holds the chip's API. |
| A chip transport | Wraps the protocol transport in the chip's own register or command shape (`ReadWriter` or `DataCommander`). |
| A protocol factory | A public static method per protocol, such as `i2c()` or `spi()`, whose parameters are the keys of a config entry. |
| Register breakouts | Readonly `DataRegister` classes that turn a register byte into named fields and back. |
| A config file | The blank wiring for `config/circuits/<slug>.php`. |
| A service provider | Merges and publishes the config, and adds the chip to the `circuit` catalog. |

The framework knows none of your chip's details. The catalog only calls your factory with the app's config, which is what keeps chip packages independent of each other and of the framework's internals.

## Choosing the Chip Kind

The kinds are empty marker interfaces in `GeneralPurposeIO\Contracts\IntegratedCircuits`, each extending `IntegratedCircuit`:

| Kind | Implemented by |
| --- | --- |
| `Sensor` | ADXL343 / ADXL345, VL6180X |
| `Actuator` | the Seesaw mini gamepad, the Wii connector extensions |
| `DisplayPanel` | SSD1306, SH1106, ST77xx, GC9A01, SSD1680, JD79661, Spectra 6 |

Nothing dispatches on the kinds; they exist so consumers can type-hint what they accept. Because they are interfaces rather than base classes, a chip may implement more than one. A display panel also implements the panel capability interfaces described on the [Display Panels](/docs/{{version}}/scrapyard-io/digging-deeper/display-panels) page.

## Choosing the Transport Shape

A chip's own IO takes one of two shapes, independent of its kind and its bus:

| Contract | Methods | Use it for |
| --- | --- | --- |
| `ReadWriter` | `read(int $register, int $length): array`, `write(int $register, array $data): int` | Register chips: accelerometers, range sensors, most I2C parts. |
| `DataCommander` | `data(array\|string $data = []): void`, `command(int $register, array $command_data = []): int` | Chips that separate command bytes from a data stream, such as panels with a data/command line or an I2C control byte. |

The chip transport wraps a protocol transport from `gpio/contracts`, such as `GeneralPurposeIO\Contracts\I2C\I2CTransport` or `GeneralPurposeIO\Contracts\SPI\SPITransport`, and translates the chip's addressing into bus calls. The VL6180X uses 16-bit register indexes sent high byte first, so its transport prepends the two index bytes with the `Splices16Bits` trait's `splitBytes()`. The SSD1306 over I2C prefixes commands with a `0x00` control byte and pixel data with `0x40`. When a chip speaks more than one bus, give it an abstract transport and one concrete transport per bus, as the SSD1306 does with `SSD1306I2CTransport` and `SSD1306SPITransport`.

The [Transports](/docs/{{version}}/scrapyard-io/architecture-concepts/transports) page covers the protocol transports themselves, including `via()` for offloading.

## Booting

`GeneralPurposeIO\IntegratedCircuits\Bootable` is the base class for every chip that needs setting up before use. It extends the abstract `IntegratedCircuit` class, implements `BootSequence`, and uses the `BootScaffolding` trait, which supplies `boot()` and `hasBooted()` over one abstract method you write:

```php
protected function _boot(): void
{
    // reset, confirm the chip ID, write the initial registers...
}
```

`boot()` runs `_boot()` once and records that it did, so calling it again does nothing. The `Bootable` constructor takes a `bool $boot_now` and boots immediately when it is `true`; pass it through from your own constructor. Consumers that need a live chip check `hasBooted()`; Surface's embedded displays, for example, refuse a panel that has not booted.

## Register Breakouts

`GeneralPurposeIO\IntegratedCircuits\DataRegister` is an abstract readonly class for decoding and encoding single register bytes. You implement three methods and inherit a fourth:

| Method | Implemented by | Returns |
| --- | --- | --- |
| `toBits(): string` | you | The register as a string of `0` and `1` characters, most significant bit first. |
| `fromByte(int $byte): static` | you | A breakout decoded from a byte the chip returned. |
| `none(): static` | you | The breakout with every field at its idle value. |
| `toByte(): int` | `DataRegister` | `bindec(toBits())`, ready to write. |

## The Circuit Catalog

The `circuit` container binding is the one chip catalog, a `GeneralPurposeIO\IntegratedCircuits\CircuitRegistry` registered by the `gpio/integrated-circuits` provider. Your package adds its chip to it from its provider's `boot()` method:

```php
app('circuit')->addCircuit('vl6180x', VL6180X::class);
```

`addCircuit()` silently ignores a class that does not implement `IntegratedCircuit`, so one bad entry cannot take the whole application's boot down. Nothing is built until an application asks:

```php
$sensor = app('circuit')->conjure('vl6180x');          // default_config
$left = app('circuit')->conjure('vl6180x', 'left');    // the config named 'left'
```

`conjure()` reads `config('circuits.<slug>')`, picks `default_config` or the config you named, and calls your chip's public static method named after that config's protocol. The protocol is the config's own name unless the entry sets a `protocol` key, which is how an app keeps a `left` and a `right` sensor beside each other. Every other key in the entry is passed as a named argument. A key your factory does not declare is dropped, and a factory parameter without a default that the config does not carry fails with a `CircuitException` naming the parameter. The registry also offers `has()`, `listCircuits()`, `resolveClass()` and `build($slug, $protocol, $params)`, which does the same call from an array instead of config.

So the factory's signature *is* the config's shape. Design them together.

## Package Discovery

Venusian discovers a package's service providers from `extra.venusian.providers` in its `composer.json`, so a chip package needs no registration step in the app. The provider does three things:

- merges the package's config file under `circuits.<slug>`, so `conjure()` finds a blank entry even before the app publishes anything;
- publishes the file to `config/circuits/<slug>.php` under a `<slug>-config` tag, where the application fills in its wiring;
- adds the chip to the catalog, guarded by `$this->app->isBound('circuit')` so the package still loads where the catalog is absent.

The package's own config is a blank with `'driver' => 'none'`. The `none` driver is what every protocol manager falls back to, and it throws an exception naming the config key to set, so a chip that has not been wired fails loudly.

Your factory reaches the protocol managers through the container by key, `gpio.i2c`, `gpio.spi`, `gpio.uart`, `gpio.digital` or `gpio.pwm`, using `Voyager\Vessel\ControlPanel::getInstance()->make()`. Because the managers are looked up at runtime, a chip package requires only `gpio/contracts` and `gpio/integrated-circuits` and lists the protocol splits it uses under `suggest`; the [Packages](/docs/{{version}}/scrapyard-io/digging-deeper/packages) page explains the dependency direction.

## A Complete Example

The driver below is a trimmed VL6180X: it boots the sensor and takes single-shot range readings in millimetres. The real [dept-of-scrapyard-robotics/vl6180x](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/vl6180x/overview) package adds ambient light, the GPIO1 interrupt line, the XSHUT reset pin and the full set of tunable settings on the same skeleton.

### The Manifest

```json
{
    "name": "acme/vl6180x",
    "description": "VL6180X time-of-flight range sensor over I2C for ScrapyardIO.",
    "type": "library",
    "license": "MIT",
    "require": {
        "php": "^8.4|^8.5|^8.6",
        "gpio/contracts": "^0.10.0",
        "gpio/integrated-circuits": "^0.10.0",
        "venusian-voyager/nuts-and-bolts": "^0.10.0",
        "venusian-voyager/vessel": "^0.10.0"
    },
    "suggest": {
        "gpio/i2c": "^0.10.0 - I2C connections",
        "microscrap/scrapyard-linux": "^0.10.0 - native i2c-dev buses",
        "microscrap/scrapyard-usb": "^0.10.0 - MPSSE I2C over FTDI"
    },
    "autoload": {
        "psr-4": {
            "Acme\\VL6180X\\": "src/"
        }
    },
    "extra": {
        "venusian": {
            "providers": [
                "Acme\\VL6180X\\VL6180XServiceProvider"
            ]
        }
    }
}
```

`venusian-voyager/vessel` supplies `ControlPanel`, and `venusian-voyager/nuts-and-bolts` the `ServiceProvider` base class.

### The Config

The blank wiring, in `config/vl6180x.php`. Its keys are exactly the parameters of the `i2c()` factory below:

```php
<?php

return [
    'default_config' => 'i2c',
    'configs' => [
        'i2c' => [
            'driver' => 'none',
            'device' => '',
            'slave' => 0x29,
        ],
    ],
];
```

### The Exception

Chip exceptions extend `CircuitException`, which descends from the framework's `GPIOLevelException`:

```php
<?php

namespace Acme\VL6180X;

use GeneralPurposeIO\Contracts\IntegratedCircuits\CircuitException;

class VL6180XException extends CircuitException
{
    public static function invalidChipId(int $chip_id, int $expected_id): static
    {
        return new static(sprintf('Invalid VL6180X model ID: expected 0x%02X, got 0x%02X.', $expected_id, $chip_id));
    }

    public static function readFailed(int $register, int $length): static
    {
        return new static(sprintf('VL6180X register 0x%03X: the bus refused a %d byte read.', $register, $length));
    }

    public static function shortRead(int $register, int $wanted, int $got): static
    {
        return new static(sprintf('VL6180X register 0x%03X: wanted %d bytes, got %d.', $register, $wanted, $got));
    }

    public static function measurementTimedOut(int $timeout_ms): static
    {
        return new static("VL6180X range measurement not ready after {$timeout_ms} ms.");
    }

    public static function notConnected(string $driver, string|int $device): static
    {
        return new static("VL6180X could not get an I2C connection from driver [{$driver}] on device [{$device}].");
    }
}
```

### The Transport

A `ReadWriter` over an I2C transport. `writeRead()` sends the two index bytes and reads the answer in one combined transfer:

```php
<?php

namespace Acme\VL6180X;

use GeneralPurposeIO\Contracts\I2C\I2CTransport;
use GeneralPurposeIO\Contracts\IntegratedCircuits\ReadWriter;
use GeneralPurposeIO\Contracts\NutsAndBolts\Splices16Bits;

/** Registers are 16-bit indexes, high byte first. */
class VL6180XI2CTransport implements ReadWriter
{
    use Splices16Bits;

    public function __construct(
        protected I2CTransport $transport,
    ) {}

    public function read(int $register, int $length): array
    {
        $bytes = $this->transport->writeRead(array_values($this->splitBytes($register)), $length);

        if ($bytes === false) {
            throw VL6180XException::readFailed($register, $length);
        }

        if (count($bytes) < $length) {
            throw VL6180XException::shortRead($register, $length, count($bytes));
        }

        return array_values($bytes);
    }

    public function write(int $register, array $data): int
    {
        return $this->transport->write([...array_values($this->splitBytes($register)), ...$data]);
    }
}
```

### A Register Breakout

`RESULT__INTERRUPT_STATUS_GPIO` packs three fields into one byte: the ranging status in bits 2:0, the ambient light status in bits 5:3 and an error code in bits 7:6. A ranging status of `4` means a new sample is ready:

```php
<?php

namespace Acme\VL6180X;

use GeneralPurposeIO\IntegratedCircuits\DataRegister;

readonly class VL6180XInterruptStatus extends DataRegister
{
    public const int NEW_SAMPLE_READY = 4;

    public function __construct(
        public int $range = 0,
        public int $als = 0,
        public int $error = 0,
    ) {}

    public function rangeReady(): bool
    {
        return $this->range === self::NEW_SAMPLE_READY;
    }

    public function toBits(): string
    {
        return sprintf('%02b', $this->error).sprintf('%03b', $this->als).sprintf('%03b', $this->range);
    }

    public static function fromByte(int $byte): static
    {
        return new static($byte & 0x07, ($byte >> 3) & 0x07, ($byte >> 6) & 0x03);
    }

    public static function none(): static
    {
        return new static;
    }
}
```

### The Chip

The chip class extends `Bootable`, implements `Sensor`, and carries the `i2c()` protocol factory. The factory reuses a bus the app already connected and connects it otherwise, so two chips on one bus share the connection:

```php
<?php

namespace Acme\VL6180X;

use GeneralPurposeIO\Contracts\IntegratedCircuits\Sensor;
use GeneralPurposeIO\IntegratedCircuits\Bootable;
use Voyager\Vessel\ControlPanel;

class VL6180X extends Bootable implements Sensor
{
    protected const int MODEL_ID = 0x000;
    protected const int SYSTEM_INTERRUPT_CONFIG_GPIO = 0x014;
    protected const int SYSTEM_INTERRUPT_CLEAR = 0x015;
    protected const int SYSTEM_FRESH_OUT_OF_RESET = 0x016;
    protected const int SYSRANGE_START = 0x018;
    protected const int RESULT_INTERRUPT_STATUS_GPIO = 0x04F;
    protected const int RESULT_RANGE_VAL = 0x062;

    protected const int EXPECTED_MODEL_ID = 0xB4;

    /**
     * Private registers ST requires after every reset (AN4545, SR03 settings).
     *
     * @var list<array{int, int}>
     */
    protected const array PRIVATE_SETTINGS = [
        [0x0207, 0x01], [0x0208, 0x01], [0x0096, 0x00], [0x0097, 0xFD],
        [0x00E3, 0x00], [0x00E4, 0x04], [0x00E5, 0x02], [0x00E6, 0x01],
        [0x00E7, 0x03], [0x00F5, 0x02], [0x00D9, 0x05], [0x00DB, 0xCE],
        [0x00DC, 0x03], [0x00DD, 0xF8], [0x009F, 0x00], [0x00A3, 0x3C],
        [0x00B7, 0x00], [0x00BB, 0x3C], [0x00B2, 0x09], [0x00CA, 0x09],
        [0x0198, 0x01], [0x01B0, 0x17], [0x01AD, 0x00], [0x00FF, 0x05],
        [0x0100, 0x05], [0x0199, 0x05], [0x01A6, 0x1B], [0x01AC, 0x3E],
        [0x01A7, 0x1F], [0x0030, 0x00],
    ];

    public function __construct(
        protected readonly VL6180XI2CTransport $transport,
        bool $boot_now = false,
    ) {
        parent::__construct($boot_now);
    }

    /** The protocol factory conjure() calls with the keys of a config/circuits/vl6180x.php entry. */
    public static function i2c(string $driver, string|int $device, int $slave = 0x29, bool $boot_now = true): static
    {
        $bus = ControlPanel::getInstance()->make('gpio.i2c')->driver($driver);
        $i2c = $bus->device($device, $slave) ?? $bus->connectTo($device)->register()->device($device, $slave);

        if (is_null($i2c)) {
            throw VL6180XException::notConnected($driver, $device);
        }

        return new static(new VL6180XI2CTransport($i2c), $boot_now);
    }

    public function transport(): VL6180XI2CTransport
    {
        return $this->transport;
    }

    /** One single-shot range in millimetres: start, wait for the sample, read it, clear the interrupt. */
    public function readRange(int $timeout_ms = 1000): int
    {
        $this->transport->write(self::SYSRANGE_START, [0x01]);
        $deadline = hrtime(true) + ($timeout_ms * 1_000_000);

        while (! $this->interruptStatus()->rangeReady()) {
            if (hrtime(true) >= $deadline) {
                throw VL6180XException::measurementTimedOut($timeout_ms);
            }

            usleep(1_000);
        }

        $range = $this->readByte(self::RESULT_RANGE_VAL);
        $this->transport->write(self::SYSTEM_INTERRUPT_CLEAR, [0x07]);

        return $range;
    }

    public function interruptStatus(): VL6180XInterruptStatus
    {
        return VL6180XInterruptStatus::fromByte($this->readByte(self::RESULT_INTERRUPT_STATUS_GPIO));
    }

    protected function _boot(): void
    {
        $model_id = $this->readByte(self::MODEL_ID);

        if ($model_id !== self::EXPECTED_MODEL_ID) {
            throw VL6180XException::invalidChipId($model_id, self::EXPECTED_MODEL_ID);
        }

        if (($this->readByte(self::SYSTEM_FRESH_OUT_OF_RESET) & 0x01) === 0x01) {
            foreach (self::PRIVATE_SETTINGS as [$register, $value]) {
                $this->transport->write($register, [$value]);
            }

            $this->transport->write(self::SYSTEM_FRESH_OUT_OF_RESET, [0x00]);
        }

        // Raise the ranging status to "new sample ready" when a measurement completes.
        $this->transport->write(self::SYSTEM_INTERRUPT_CONFIG_GPIO, [VL6180XInterruptStatus::NEW_SAMPLE_READY]);
    }

    protected function readByte(int $register): int
    {
        return $this->transport->read($register, 1)[0];
    }
}
```

### The Service Provider

```php
<?php

namespace Acme\VL6180X;

use Voyager\NutsAndBolts\ServiceProvider;

class VL6180XServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->mergeConfigFrom(dirname(__DIR__).'/config/vl6180x.php', 'circuits.vl6180x');
    }

    public function boot(): void
    {
        $this->publishes([
            dirname(__DIR__).'/config/vl6180x.php' => $this->app->configPath('circuits/vl6180x.php'),
        ], 'vl6180x-config');

        if ($this->app->isBound('circuit')) {
            $this->app->make('circuit')->addCircuit('vl6180x', VL6180X::class);
        }
    }
}
```

### Using It

An application publishes the config and fills in its bench. On a Raspberry Pi with `microscrap/scrapyard-linux`, the sensor on `/dev/i2c-1` looks like this:

```shell
php computer vendor:publish --tag=vl6180x-config
```

```php
// config/circuits/vl6180x.php
return [
    'default_config' => 'i2c',
    'configs' => [
        'i2c' => [
            'driver' => 'native',
            'device' => 1,
            'slave' => 0x29,
        ],
    ],
];
```

Then one call builds a wired, booted sensor, with no adapter, bus or address at the call site:

```php
$sensor = app('circuit')->conjure('vl6180x');

$millimetres = $sensor->readRange();
```

On an FT232H with `microscrap/scrapyard-usb`, only the config changes: `'driver' => 'usb'` and `'device' => 'ft232h'`.

## Testing a Chip Package

Chip packages prove their protocol factories without hardware by registering a fake driver on a real protocol manager, then conjuring through a real catalog. The Dept of Scrapyard Robotics suites build that bench like this:

```php
$app->registerInstance('circuit', new \GeneralPurposeIO\IntegratedCircuits\CircuitRegistry);
$app->registerInstance('gpio.i2c', (new \GeneralPurposeIO\I2C\I2CConnectionManager($app))->extend('fake', fn () => $fake_i2c));
```

`$fake_i2c` is an `I2CConnectionDriver` subclass whose transports record every byte written and answer reads from a script. That is why `gpio/i2c` sits in a chip package's `require-dev` while staying out of `require`. The [Writing an Adapter](/docs/{{version}}/scrapyard-io/digging-deeper/writing-an-adapter) page shows the three classes such a driver is made of.
