# Packages

ScrapyardIO is developed in one repository and published two ways: as the `scrapyard-io/framework` package an application installs, and as eight `gpio/*` component packages split out of it, so chip drivers and adapters can depend on exactly the parts they use. This page lists the splits, the direction dependencies run between them, which split a chip or adapter should require, and how a release tags and splits them.

## Introduction

Applications install the whole framework:

```shell
composer require scrapyard-io/framework
```

`scrapyard-io/framework` declares every split in its `replace` section at `self.version`, so an application that has the framework already satisfies any package requiring a `gpio/*` split, and Composer never installs a second copy. Packages that build on ScrapyardIO, the chip drivers and the adapters, require the splits instead. That way they install beside the framework in an application, and on their own in their own test suites.

## The Splits

Each split is a directory under `src/GeneralPurposeIO/` with its own `composer.json`, `LICENSE` and `.gitattributes`:

| Package | Namespace | Contents | Service provider | Container key |
| --- | --- | --- | --- | --- |
| `gpio/contracts` | `GeneralPurposeIO\Contracts` | Transports and offloaded transports, protocol enums, exceptions, `BusJob`, the integrated circuit and display panel contracts | none | none |
| `gpio/nuts-and-bolts` | `GeneralPurposeIO\NutsAndBolts` | `CarrierTransport`, `BusQueue`, `OffloadsBusJobs`, `TransportCall`, `Bytes`, and the `array2bytes()`, `bytes2array()`, `byte2bits()` and `bits2byte()` helpers | none | none |
| `gpio/integrated-circuits` | `GeneralPurposeIO\IntegratedCircuits` | `IntegratedCircuit`, `Bootable`, `DataRegister` and the `CircuitRegistry` catalog | `IntegratedCircuitsServiceProvider` | `circuit` |
| `gpio/digital` | `GeneralPurposeIO\Digital` | The digital connection manager and its connection classes | `DigitalIOServiceProvider` | `gpio.digital` |
| `gpio/i2c` | `GeneralPurposeIO\I2C` | The I2C connection manager and its connection classes | `I2CServiceProvider` | `gpio.i2c` |
| `gpio/spi` | `GeneralPurposeIO\SPI` | The SPI connection manager and its connection classes | `SPIServiceProvider` | `gpio.spi` |
| `gpio/uart` | `GeneralPurposeIO\UART` | The UART connection manager and its connection classes | `UARTServiceProvider` | `gpio.uart` |
| `gpio/pwm` | `GeneralPurposeIO\PWM` | The PWM connection manager and its connection classes | `PWMServiceProvider` | `gpio.pwm` |

Each split declares its own provider under `extra.venusian.providers`, so a split installed on its own still registers itself in a Venusian application. ScrapyardIO ships no facades or aliases: the managers and the catalog are container keys.

### Core Is Not Split

`src/GeneralPurposeIO/Core` has no manifest and ships only inside `scrapyard-io/framework`. It holds the aggregate `ScrapyardIOServiceProvider`, which merges `config/gpio.php`, publishes it under the `gpio-config` tag, registers the six component providers above, and registers the [`scrapyard:ext` and `scrapyard:modules`](/docs/{{version}}/scrapyard-io/digging-deeper/dev-commands) commands. The default-driver config file and the dev commands are therefore part of the framework package only, and the framework's own `require` carries what those commands need: `laravel/prompts`, `symfony/process`, `symfony/filesystem`, `composer-runtime-api`, and the Venusian `console`, `process` and `workflows` components.

## Dependency Direction

Dependencies run one way, from the packages that build on ScrapyardIO down to the contracts:

```text
adapters      ──► gpio/digital, gpio/i2c, gpio/spi, gpio/uart, gpio/pwm ──► gpio/nuts-and-bolts ──► gpio/contracts
chip drivers  ──► gpio/integrated-circuits ──► gpio/contracts
```

These are each split's requirements, besides PHP:

| Package | Requires |
| --- | --- |
| `gpio/contracts` | `venusian-voyager/contracts` |
| `gpio/nuts-and-bolts` | `gpio/contracts`, `venusian-voyager/contracts` |
| `gpio/integrated-circuits` | `gpio/contracts`, `venusian-voyager/contracts`, `venusian-voyager/nuts-and-bolts` |
| `gpio/i2c`, `gpio/spi`, `gpio/pwm` | `gpio/contracts`, `gpio/nuts-and-bolts`, `venusian-voyager/collections`, `venusian-voyager/contracts`, `venusian-voyager/nuts-and-bolts` |
| `gpio/digital`, `gpio/uart` | the same, plus `venusian-voyager/io-pools` |

A few rules keep this shape:

- **Requires follow imports.** Each manifest requires exactly what its PHP imports or extends, so a split installed alone loads every class it ships. `gpio/digital` and `gpio/uart` require `venusian-voyager/io-pools` because their edge and port watches extend its `WakeSource`; the other protocols use only the loop and pool interfaces from `venusian-voyager/contracts`.
- **No protocol requires another protocol.** The adapters require every protocol they drive and so sit above all of them.
- **Hardware is only ever suggested.** No split requires a PHP extension or a hardware package. The protocol splits `suggest` the adapters, `microscrap/scrapyard-linux` and, except for PWM, `microscrap/scrapyard-usb`, rather than the low-level bindings those sit on. A machine without ext-posi or ext-ftdi, such as a CI runner or a laptop, installs everything.
- **Nothing requires the framework.** No split imports Core, and none requires `venusian/framework`. The splits depend on Venusian components, never the full framework.
- **Surface stays out.** `gpio/contracts` never imports a Surface class. Surface's `venusian-surface/embedded-displays` requires `gpio/contracts`; the reverse never happens.

The splits still run inside a booted Venusian application: their providers call the `config()` and `app()` helpers, and the catalog reads `config('circuits.<slug>')`.

## Which Splits to Require

### In a Chip Driver

A chip driver requires the contracts and the catalog, plus the Venusian components it uses directly:

```json
"require": {
    "php": "^8.4|^8.5|^8.6",
    "gpio/contracts": "^0.10.0",
    "gpio/integrated-circuits": "^0.10.0",
    "venusian-voyager/nuts-and-bolts": "^0.10.0",
    "venusian-voyager/vessel": "^0.10.0"
}
```

Add `gpio/nuts-and-bolts` when the driver uses its byte helpers or classes; the SSD1306, SH1106, ST77xx and ADXL34x packages require it. A display panel driver also requires `venusian-surface/contracts`, for the `FormatSpec` its `formatSpec()` returns.

A chip driver does not require the protocol splits it talks over. Its factory resolves the managers from the container by key at runtime and types its transports against `gpio/contracts`, so it lists the protocol splits and the adapters under `suggest`, and puts the protocol splits in `require-dev` for its own tests. The VL6180X, for example, suggests `gpio/i2c`, `gpio/digital`, `microscrap/scrapyard-linux` and `microscrap/scrapyard-usb`. [Writing a Chip Driver](/docs/{{version}}/scrapyard-io/digging-deeper/writing-a-chip-driver) builds a complete package on this manifest.

### In an Adapter

An adapter extends the protocol classes, so it requires every protocol split it registers a driver for, plus `gpio/contracts`, `gpio/nuts-and-bolts`, its PHP extension and its low-level bindings. `microscrap/scrapyard-usb`, which drives digital, I2C, SPI and UART, requires `gpio/contracts`, `gpio/digital`, `gpio/i2c`, `gpio/nuts-and-bolts`, `gpio/spi`, `gpio/uart`, `ext-ftdi`, `microscrap/mpsse` and `venusian-voyager/nuts-and-bolts`. [Writing an Adapter](/docs/{{version}}/scrapyard-io/digging-deeper/writing-an-adapter) covers the rest.

### Version Constraints

Every split is versioned in lockstep with the framework, so require each on the release line you build against, `^0.10.0` for this line.

## Releases

Releases are cut from the monorepo by pushing a `vX.Y.Z` tag. The `split` workflow first runs the test suite, which runs on PHP 8.4 and 8.5; a red suite stops the release before anything is split. On a green suite, `.github/split.sh` runs [splitsh-lite](https://github.com/splitsh/lite) on every `src/<Namespace>/<Component>/` directory that holds a `composer.json`, and pushes each split to its own repository in the `general-purpose-io` GitHub organization, named after the package name minus its vendor, so `gpio/i2c` lands in `general-purpose-io/i2c`.

### Lockstep Versions

Every split receives the monorepo's tag, whether or not that component changed. A patch tag moves every split by the same patch.

### Branches

The tag must sit at the head of the `X.Y.x` line branch or of `main`; otherwise the run refuses. Which branches the splits receive depends on where the tag sits:

| Tag sits on | Monorepo | Splits receive |
| --- | --- | --- |
| `X.Y.x` (and `main` too, when `main` is at the tag) | unchanged | `X.Y.x`, plus `main` when `main` is at the tag, and the tag |
| `main`, with no `X.Y.x` yet | `X.Y.x` is created at the tag | `X.Y.x`, `main`, the tag |
| `main`, with `X.Y.x` behind it | `X.Y.x` is fast-forwarded to the tag | `X.Y.x`, `main`, the tag |
| `main`, with `X.Y.x` holding commits `main` lacks | refuses | nothing |

Split branches are force-pushed, since splitsh output is deterministic. Tags are never forced.

### Manifest Checks

Before anything is pushed, the script checks the root manifest and every component manifest against the tag, and lists every problem at once:

- a `version` key, where one is present, must equal the tag's version;
- `extra.branch-alias.dev-main` must be `X.Y.x-dev`;
- every requirement on a sibling split must be `^X.Y` or `^X.Y.N`.

So the commit you tag `vX.Y.0` must already carry the new branch aliases and sibling constraints. Then every split repository must answer; if one is missing, nothing is pushed.

### Adding a Component

A new split needs no workflow change, because the split list is the directory listing. Create the repository in the `general-purpose-io` organization, add `src/GeneralPurposeIO/<Component>/composer.json` named `gpio/<name>`, add it to the root manifest's `replace`, and submit it to Packagist after its first split.
