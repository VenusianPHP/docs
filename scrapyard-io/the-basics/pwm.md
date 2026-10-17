# PWM

Generating pulse-width modulation from PHP: opening a PWM chip through the `gpio.pwm` manager, setting a channel's period, duty cycle, polarity and enable state, and offloading channel work with `via()`.

## Introduction

Pulse-width modulation switches a line on and off at a fixed rate and varies how long each pulse stays high. The **period** is the length of one cycle, and the **duty cycle** is how much of it the line spends high. A hobby servo reads the pulse width as an angle, a 4-pin PC fan reads the duty cycle as a speed, and an LED driven fast enough looks dimmer as the duty cycle shrinks.

ScrapyardIO opens a hardware PWM chip as a **connection** and hands out each of its channels as a **transport**, `GeneralPurposeIO\Contracts\PWM\PWMTransport`. The hardware keeps generating the waveform on its own once you have set it up; your code only changes the settings.

## Opening a Chip

### The PWM Manager

The PWM connection manager is bound in the container as `gpio.pwm`, with `GeneralPurposeIO\PWM\PWMConnectionManager` as an alias. There is no facade or global helper; you resolve the manager and ask it for a driver:

```php
$pwm = app('gpio.pwm')->driver('native');   // microscrap/scrapyard-linux
```

The driver is built once and reused. Calling `driver()` with no name, or calling a driver method on the manager itself, uses the default from the `gpio.protocols.pwm.default` option of your `config/gpio.php` file. That default is `none` until you set it, and the `none` driver throws `PWMException` on every attempt: "No PWM connection driver is configured. Set gpio.protocols.pwm.default to an installed adapter." See [Configuration](/docs/{{version}}/scrapyard-io/getting-started/configuration).

ScrapyardIO keeps no list of named channels in its config. To keep a servo's or fan's wiring in configuration, give it a circuit config and build it with `app('circuit')->conjure(...)`; see [Integrated Circuits](/docs/{{version}}/scrapyard-io/architecture-concepts/integrated-circuits).

### Connecting

`connectTo($chip)` names the PWM chip and returns a connection factory; `register()` checks the chip exists and returns the driver. `device($chip, $channel)` then hands you one channel:

```php
$servo = app('gpio.pwm')->driver('native')
    ->connectTo(0)        // /sys/class/pwm/pwmchip0
    ->register()
    ->device(0, 0);       // channel 0
```

`connectTo()` takes the chip number, as an `int` or a numeric string. A chip with no `/sys/class/pwm/pwmchip<n>` directory throws `PWMException` ("PWM chip pwmchip2 was not found under /sys/class/pwm."), and connecting a chip the driver already holds throws "PWM chip 0 is already connected.". Which chips and channels exist depends on your board and its device-tree overlays; see [Setting Up a Machine](/docs/{{version}}/scrapyard-io/getting-started/setting-up-a-machine).

### Getting a Channel

`device($chip, $channel)` returns the transport for one channel, or `null` when the chip was never registered. The driver hands out one transport per channel, so asking twice gives you the same object, and `channel()` returns its number.

A channel the kernel has not exported yet is exported for you. The kernel creates the channel's directory a moment before udev makes its files writable for your user, so `device()` waits for them, for up to 500 ms by default. Set a different limit on the factory with `readyTimeout($milliseconds)`:

```php
$driver = app('gpio.pwm')->driver('native')
    ->connectTo(0)
    ->readyTimeout(2000)
    ->register();
```

A channel that cannot be exported throws `PWMException` ("Could not export PWM channel 1 on pwmchip0."), and one whose files are still not writable when the time is up throws "PWM channel attribute is not writable yet: ...".

## Setting a Channel

Each setting has a getter and a setter. Times are in nanoseconds. Every setter writes the value, then reads it back from the kernel and returns what the kernel now holds:

| Method | Does |
| --- | --- |
| `getPeriod(): int` / `setPeriod(int $value): int` | the length of one cycle, in nanoseconds |
| `getDutyCycle(): int` / `setDutyCycle(int $value): int` | how long the line stays high in each cycle, in nanoseconds |
| `getEnable(): bool` / `setEnable(bool $value): bool` | whether the channel is generating pulses |
| `getPolarity(): bool` / `setPolarity(bool $value): bool` | `false` for normal polarity, `true` for inversed |

Set the period before the duty cycle: the kernel refuses a duty cycle longer than the period. A refused write throws `PWMException` ("Could not write PWM sysfs attribute: ...").

### Driving a Servo

A hobby servo expects a pulse every 20 ms, and reads a pulse of about 1 ms as one end of its travel, 1.5 ms as the middle and 2 ms as the other end:

```php
$servo->setPeriod(20_000_000);      // 50 Hz
$servo->setDutyCycle(1_500_000);    // centre
$servo->setEnable(true);

// Swing to one end of its travel
$servo->setDutyCycle(2_000_000);
```

A helper that maps an angle to a pulse width keeps the arithmetic in one place:

```php
function servoPulse(float $degrees): int
{
    $degrees = max(0.0, min(180.0, $degrees));

    return (int) round(1_000_000 + ($degrees / 180) * 1_000_000);
}

$servo->setDutyCycle(servoPulse(90));   // 1500000
```

### Driving a Fan

A 4-pin PC fan expects a 25 kHz signal on its control wire and runs faster as the duty cycle grows:

```php
$fan = $driver->device(0, 1);

$fan->setPeriod(40_000);            // 25 kHz
$fan->setDutyCycle(intdiv(40_000 * 60, 100));   // 60 %
$fan->setEnable(true);
```

### Polarity

`setPolarity(true)` inverts the output, so the line spends the duty cycle low instead of high. `getPolarity()` throws `PWMException` if the kernel reports anything other than `normal` or `inversed`.

## Closing

`close()` disables the channel and hands it back to the kernel (unexports it). The chip stays registered, and the next `device()` call for that channel exports a fresh one. Any call on a closed channel throws `PWMException` ("PWM channel 0 is closed."), and `closed()` tells you whether it has been closed.

`disconnect($chip)` closes every channel on the chip and forgets the chip. `connectTo()` can register it again afterwards.

## Blocking and the Event Loop

Every getter and setter is a blocking call: it reads or writes a sysfs file and returns. These are quick, so most programs call them directly, in a Computer command or a [sketch](https://venusian.projectsaturnstudios.com/docs/framework/the-basics/sketches).

The one wait in PWM is `device()` waiting for a freshly exported channel to become writable. Without a Venusian [event loop](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop) it sleeps in 10 ms steps; with a loop bound it polls on a loop timer instead, suspending its fiber, or turning the loop on the main stack, so timers and other resources keep running.

### Offloading With via()

`via($pool)` returns a handle with the eight getters and setters and `run()`, each returning a `Voyager\Contracts\IOPools\Promise` that settles with what the blocking call returns, or rejects with what it throws:

```php
$servo->via()->setDutyCycle(servoPulse(30))
    ->then(fn (int $applied) => $this->line("Servo pulse now {$applied} ns"))
    ->error(fn (Throwable $e) => $this->error($e->getMessage()));
```

`via()` sends the work to the thread worker pool when it is enabled and the process pool otherwise; `via('thread')` and `via('process')` name one. The worker builds its own driver on the same sysfs tree. It needs a bound event loop: without one, the first call on the handle throws `GPIOLevelException` ("via() needs an event loop. Boot IOPools, or call the blocking method."). With a loop but no worker pool enabled, the promise rejects with an `InvalidArgumentException` naming the option to turn on (`io-pools.pool_workers.threads.enabled` or `io-pools.pool_workers.process.enabled`; see [Named Pools](https://venusian.projectsaturnstudios.com/docs/framework/architecture-concepts/event-loop#named-pools)).

Each channel has its own queue: jobs for one channel run one at a time, in call order, while different channels run side by side. A blocking call on a channel first waits for the jobs already queued for it, so mixing blocking and offloaded calls never reorders your settings. `close()` lets the running job finish and rejects the queued ones, and a `via()` handle checks its channel on every call. A worker's exception comes back as the `PWMException` it was.

To apply several settings as one unit of work, ship a `GeneralPurposeIO\Contracts\NutsAndBolts\BusJob` and run it with `via()->run($job)`. Its `run` method receives the channel and uses the blocking calls:

```php
<?php

namespace App\Jobs;

use GeneralPurposeIO\Contracts\NutsAndBolts\BusJob;
use GeneralPurposeIO\Contracts\NutsAndBolts\GPIOTransport;
use GeneralPurposeIO\Contracts\PWM\PWMTransport;

final class StartFan implements BusJob
{
    public function __construct(
        public readonly int $percent,
    ) {}

    public function run(GPIOTransport $bus): int
    {
        /** @var PWMTransport $bus */
        $bus->setPeriod(40_000);
        $bus->setDutyCycle(intdiv(40_000 * $this->percent, 100));
        $bus->setEnable(true);

        return $bus->getDutyCycle();
    }
}
```

```php
$fan->via()->run(new StartFan(75));
```

A job may cross to a worker, so it holds only scalar state, and its class must be autoloadable there.

## Adapters

PWM is provided by the `native` driver from `microscrap/scrapyard-linux` only. It drives the kernel's sysfs PWM interface under `/sys/class/pwm` and needs no PHP extension. The `usb` adapter has no PWM driver, so `app('gpio.pwm')->driver('usb')` throws an `InvalidArgumentException` ("Driver [usb] not supported.").

For the adapter itself, see [scrapyard-linux](/docs/{{version}}/ecosystem/gpio-modules/scrapyard-linux/concepts/pwm). The [generic servo](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/generic-servo/overview) and [generic fan](/docs/{{version}}/ecosystem/dept-of-scrapyard-robotics/generic-fan/overview) drivers are PWM chip drivers to read alongside this page.

## Errors

Every PWM failure throws `GeneralPurposeIO\Contracts\PWM\PWMException`, which extends `GeneralPurposeIO\Contracts\Core\GPIOLevelException`.

| Thrown when | Message |
| --- | --- |
| No adapter is configured | No PWM connection driver is configured. Set gpio.protocols.pwm.default to an installed adapter. |
| The chip does not exist | PWM chip pwmchip2 was not found under /sys/class/pwm. |
| The chip is already registered | PWM chip 0 is already connected. |
| The channel cannot be exported | Could not export PWM channel 1 on pwmchip0. |
| The channel's files never became writable | PWM channel attribute is not writable yet: /sys/class/pwm/pwmchip0/pwm1/period |
| A setting is refused | Could not write PWM sysfs attribute: /sys/class/pwm/pwmchip0/pwm0/duty_cycle |
| A setting cannot be read | Could not read PWM sysfs attribute: /sys/class/pwm/pwmchip0/pwm0/period |
| The kernel reports an unknown polarity | Invalid PWM polarity '...'. Expected 'normal' or 'inversed'. |
| The channel is closed | PWM channel 0 is closed. |
