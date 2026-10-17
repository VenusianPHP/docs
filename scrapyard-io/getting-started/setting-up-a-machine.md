# Setting Up a Machine

The `scrapyard:ext` and `scrapyard:modules` Computer commands that install ScrapyardIO's PHP extensions and microscrap packages, and the device access a Raspberry Pi, another Linux board, or a machine driving an FTDI board needs.

## Introduction

Before your application can open a bus, the machine it runs on needs three things: the PHP extension your adapter calls into, the adapter package itself, and permission for your user to open the devices. ScrapyardIO ships two Computer commands for the first two, so a fresh Raspberry Pi or laptop goes from a new Venusian application to a working adapter in two steps:

```shell
php computer scrapyard:ext

php computer scrapyard:modules
```

Both commands work with the PHP binary that is running `computer`. The extensions are built for that binary, and the packages are installed by a Composer that binary runs, so what they install is what your application loads. Run them as two separate commands, in this order: `scrapyard:modules` decides what it can offer by looking at the extensions the running PHP has loaded, so it needs a fresh process to see an extension `scrapyard:ext` just installed.

## Installing the Extensions

The `scrapyard:ext` command installs ScrapyardIO's two PHP extensions through [PIE](https://github.com/php/pie), the PHP Foundation's extension installer:

| Extension | PIE Package | What It Provides |
| --- | --- | --- |
| `posi` | `php-io-extensions/posi:^0.10` | POSIX calls for GPIO character devices, I2C, SPI and serial ports |
| `ftdi` | `php-io-extensions/ftdi:^0.10` | FTDI USB bridges such as the FT232H, through libftdi |

Run it without arguments to pick from a list, or name one extension to install just that one:

```shell
php computer scrapyard:ext

php computer scrapyard:ext ftdi
```

### How It Decides What to Offer

For each extension, the command asks the running PHP which version it loads:

- An extension loaded at a version on the 0.10 line is shown as installed and is not offered.
- An extension loaded at an older or newer version, such as a 0.9 build, is offered as a replacement, labelled with the version that is loaded.
- An extension that isn't loaded is offered.
- On Windows, neither extension is offered, since neither builds there.

The list starts with every installable extension selected, and anything that cannot be installed is named above it with the reason. When you name an extension on the command line, that extension is the selection and nothing is asked; if it is already installed, or cannot be installed on this machine, the command says so and stops.

### Finding php-config and PIE

So that PIE builds for the right PHP, the command looks for the `php-config` that belongs to the running binary. It tries the one beside the binary first, so `php8.4` looks for `php-config8.4`, then the one on your `PATH`, and asks each which PHP it builds for. When it finds the matching one, PIE is given it with `--with-php-config`. When the only `php-config` on the machine builds for a different PHP, the command stops and asks you to install the development files for your PHP first. When there is no `php-config` at all, it carries on and lets PIE check for build tools itself.

PIE is looked for on your `PATH`, then in `~/.local/bin`, and only counts when the running PHP can run it. If there is none, the command asks before downloading `pie.phar` from PIE's latest GitHub release to `~/.local/bin/pie`. It then has PIE verify its own release attestation, and removes the download if that check fails. Nothing is downloaded without a yes, so a non-interactive run without PIE stops and asks you to run the command interactively.

### Building and Checking

Each selected extension is installed with its own `pie install`, run by your PHP binary and handed your terminal, so PIE can ask for your password when PHP's extension directory is not writable, or offer to install missing build tools. Building needs a C compiler and your PHP's development files; `ext-ftdi` also needs libftdi1 and libusb, as described [below](#ftdi-boards). One failed build doesn't stop the next.

After each install, the command asks your PHP binary which version of the extension it now loads, and reports one line per extension:

| Outcome | Meaning |
| --- | --- |
| `installed` | Your PHP loads the extension at a 0.10 version |
| `installed by PIE, but <php> does not load it` | PIE finished, but the extension isn't enabled for this PHP |
| `installed by PIE, but <php> loads <version>` | PIE finished, but this PHP still loads another version |
| `failed (PIE exit code N)` | PIE returned an error |
| `failed (<message>)` | PIE could not be started |

The command exits with a failure status unless every selected extension reports `installed`. Choosing nothing, or finding nothing to install, is a success.

The two extensions have their own documentation, including manual builds with `phpize` and the installer scripts in their repositories: [ext-posi](/docs/{{version}}/ecosystem/standalone-extensions/posi/overview) and [ext-ftdi](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/overview).

## Installing the Modules

The `scrapyard:modules` command installs the microscrap packages this machine can run into your application, with Composer:

| Module | What It Is | Offered When |
| --- | --- | --- |
| `gpio` | `microscrap/gpio`: libgpiod digital IO over ext-posi | `ext-posi` 0.10 is loaded |
| `i2c` | `microscrap/i2c`: i2c-dev buses over ext-posi | `ext-posi` 0.10 is loaded |
| `spi` | `microscrap/spi`: spidev buses over ext-posi | `ext-posi` 0.10 is loaded |
| `uart` | `microscrap/uart`: serial ports over ext-posi | `ext-posi` 0.10 is loaded |
| `mpsse` | `microscrap/mpsse`: MPSSE SPI, I2C and GPIO over ext-ftdi | `ext-ftdi` 0.10 is loaded |
| `scrapyard-linux` | `microscrap/scrapyard-linux`: the `native` adapter | Linux, and `ext-posi` 0.10 is loaded |
| `scrapyard-usb` | `microscrap/scrapyard-usb`: the `usb` adapter | `ext-ftdi` 0.10 is loaded |

Run it without arguments to pick from a list, or name one module by its short name:

```shell
php computer scrapyard:modules

php computer scrapyard:modules scrapyard-usb
```

Each package requires its extension at 0.10 in its `composer.json`, and Composer checks that against the PHP running it, so the command only offers a module whose extension is loaded at a 0.10 version. A module whose extension is missing is listed as needing it, and one whose extension is loaded at another version is listed with the version that is loaded. `scrapyard-linux` drives Linux-only kernel interfaces, so it is only offered on Linux. A module already in your application is shown as installed. The adapters require the bindings they use, so installing `scrapyard-linux` or `scrapyard-usb` brings those in too; the bindings are listed separately for code that uses them directly.

As with `scrapyard:ext`, the list starts with every installable module selected and names the rest above it, and a module named on the command line is the selection with nothing asked.

### Finding Composer

The command uses `composer` on your `PATH`, or a `composer.phar` in your application's root, whichever the running PHP can run first. If it finds neither, it stops and points you to [getcomposer.org](https://getcomposer.org).

### Installing

Every selected module goes into one `composer require`, each at `^0.10`, run by your PHP binary in your application's root and handed your terminal. Composer resolves them together, so they land together or not at all, and every selected module reports the same outcome: `installed`, `failed (Composer exit code N)`, or `failed (<message>)`. The command exits with a failure status unless the install succeeded.

## Non-Interactive Runs

Both commands only show their list and ask questions when they have a terminal: the input must be interactive and standard input must be a TTY. Without one, as in a provisioning script, name what to install, and pass `--no-interaction` if you want Computer to treat the run as non-interactive explicitly:

```shell
php computer scrapyard:ext posi --no-interaction

php computer scrapyard:modules scrapyard-linux --no-interaction
```

A non-interactive run with nothing named stops and lists the names it accepts. Since `scrapyard:ext` won't download PIE without asking, install PIE yourself first on a machine you set up this way. Neither command takes any options of its own beyond the optional name.

## Raspberry Pi and Linux Device Access

The `native` adapter opens device nodes under `/dev` and files under `/sys`, so your user needs permission to use them, and the kernel interfaces you need must be turned on. On Raspberry Pi OS, add your user to the `gpio`, `i2c`, `spi` and `dialout` groups, then log out and back in so the new groups apply:

```shell
sudo usermod -aG gpio,i2c,spi,dialout $USER
```

Enable the interfaces you use with `raspi-config`, or with `dtparam` and `dtoverlay` lines in `config.txt`, which lives at `/boot/firmware/config.txt` or `/boot/config.txt` depending on your OS release. What each protocol needs:

| Protocol | Device | Setup |
| --- | --- | --- |
| I2C | `/dev/i2c-N` | The `i2c-dev` kernel module (`modprobe i2c-dev`), the I2C interface enabled, and your user in `i2c` |
| SPI | `/dev/spidevN.CS` | The SPI interface enabled, for example with `dtparam=spi=on`, and access to the spidev nodes (the `spi` group on Raspberry Pi OS) |
| UART | a tty such as `/dev/ttyAMA0` or `/dev/ttyUSB0` | Your user in `dialout` |
| Digital | `/dev/gpiochipN` | A Linux 5.10 or newer kernel for the GPIO v2 character device interface, and your user in `gpio` |
| PWM | `/sys/class/pwm/pwmchipN` | The PWM controller enabled with a `dtoverlay` line in `config.txt`, so its `pwmchipN` directory exists |

To check that a bus is visible before you write any code, list its device nodes, and on I2C scan for devices with `i2cdetect` from i2c-tools:

```shell
ls /dev/i2c-* /dev/spidev* /dev/gpiochip*

i2cdetect -y 1
```

A few details of the Linux adapter depend on the machine's setup:

- **PWM** channels are exported through sysfs the first time `device()` asks for one, and udev then makes the channel's files writable. The driver waits up to 500 ms for that; on a slower system, raise the limit with `connectTo(0)->readyTimeout($ms)`. With an event loop bound, the wait keeps the loop turning.
- **SPI** buses are shared between processes through `flock()` on `/run/lock/scrapyard-spi<bus>.lock`, so your application, its pool workers and other programs using ScrapyardIO never interleave on one bus. A transfer longer than spidev's buffer, set in `/sys/module/spidev/parameters/bufsiz` and 4096 bytes by default, is split into several messages with chip select held throughout.
- **Digital** pins show up in tools such as `gpioinfo` under the consumer name `scrapyard-io-digital-io`, or the name you give with `connectTo(0)->consumer('my-app')`.

Building `ext-posi` on Debian or Raspberry Pi OS needs a compiler and PHP's development files:

```shell
sudo apt install build-essential php8.4-dev
```

## FTDI Boards

The `usb` adapter drives an FTDI board such as the FT232H through libftdi1 and libusb-1.0. It works on Linux, whether that is a Raspberry Pi or an x86 machine, and on macOS. Install the libraries before you build `ext-ftdi`, since its build looks them up.

On Debian, Ubuntu and Raspberry Pi OS:

```shell
sudo apt install build-essential pkg-config libftdi1-dev libusb-1.0-0-dev php8.4-dev
```

On macOS, with Homebrew, which also provides `phpize` and `php-config` with its PHP, plus the Xcode Command Line Tools for the compiler:

```shell
brew install php@8.4 libftdi libusb pkgconf
```

PIE uses `sudo` where your PHP's extension directory is owned by root, as on Debian, and not on a Homebrew Mac.

### USB Access on Linux

On Linux, your user needs read-write access to the USB device. Run as root, or add a udev rule such as `/etc/udev/rules.d/99-ftdi.rules`:

```
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", MODE="0660", GROUP="plugdev"
```

Then reload udev and add your user to `plugdev`. When libftdi opens an interface, it detaches the kernel's `ftdi_sio` serial driver from it, so the board's `/dev/ttyUSB` node disappears while the `usb` adapter holds it. If you would rather keep a board on `ftdi_sio` and use it as a plain serial port, open its `/dev/ttyUSB*` node with the `native` UART driver instead.
