# Dev Commands

ScrapyardIO adds two Computer commands that set a machine up for hardware work: `scrapyard:ext` installs the ScrapyardIO PHP extensions through PIE, and `scrapyard:modules` installs the `microscrap` packages that the machine's operating system and loaded extensions can run, through Composer. Both work out what the machine can take before they offer anything, and both run their installer with the same PHP binary that runs `computer`.

## Introduction

Run the commands in order on a new machine: extensions first, because the modules depend on them.

```shell
php computer scrapyard:ext

php computer scrapyard:modules
```

The commands are registered by `GeneralPurposeIO\Core\Providers\ScrapyardIOServiceProvider`, which ships only in the `scrapyard-io/framework` package. An application that installs the `gpio/*` splits on their own does not get them. Each command is built as a Venusian workflow, a flow of nodes that read and write a shared bag, so every step below corresponds to one node.

The [Setting Up a Machine](/docs/{{version}}/scrapyard-io/getting-started/setting-up-a-machine) page walks through a first install; this page documents both commands in full.

## scrapyard:ext

`scrapyard:ext` installs the two ScrapyardIO extensions with [PIE](https://github.com/php/pie), the PHP extension installer:

| Name | PIE package | Provides |
| --- | --- | --- |
| `posi` | `php-io-extensions/posi:^0.10` | POSIX calls for GPIO character devices, I2C, SPI and serial ports |
| `ftdi` | `php-io-extensions/ftdi:^0.10` | FTDI USB bridges such as the FT232H, through libftdi |

The extensions are documented under [posi](/docs/{{version}}/ecosystem/standalone-extensions/posi/overview) and [ftdi](/docs/{{version}}/ecosystem/standalone-extensions/ftdi/overview).

### Usage

```shell
php computer scrapyard:ext          # list both, pick, install
php computer scrapyard:ext ftdi     # install that one, with no list
```

The command takes one optional argument, `ext`, the extension to install: `posi` or `ftdi`, case-insensitive. Omit it to choose from a list.

### Deciding What Can Be Installed

For each extension, the command asks the running PHP binary which version it loads, and settles on one state:

| Situation | State |
| --- | --- |
| The operating system is Windows | `not on Windows`; neither extension's manifest supports it |
| Loaded at a version from `0.10.0` up to, not including, `0.11.0` | `installed` |
| Loaded at a version off that line, such as `0.9.0` | installable; PIE replaces it |
| Not loaded | installable |

On an interactive run, once `php-config` and PIE have been found as described below, the installable extensions appear in a multi-select list and start selected. An extension loaded off the line is labelled with what it replaces, for example `ftdi (0.9.0 loaded, replaced by ^0.10)`. Any extension that cannot be installed is named above the list with its reason.

When you name an extension, it becomes the selection and no list is shown. If it cannot be installed, the command ends with `Nothing to install` and the reason. A name that is neither `posi` nor `ftdi` ends with an error listing the valid names. When nothing at all can be installed, the command ends with `Nothing to install` and every extension's reason.

A run without a terminal cannot show a list, so it must name the extension; otherwise it ends by asking you to name one.

### Finding php-config

PIE needs the `php-config` that builds for the PHP binary running the command, so the extension lands where that binary loads it. The command tries the `php-config` beside the binary first (`php8.4` beside `php-config8.4`, for example), then the one on your `PATH`, and asks each which binary it builds for. The first one that builds for the running binary is passed to PIE as `--with-php-config`.

When the only `php-config` found builds for a different binary, the command stops and asks you to install the development files for the running one first. When there is no `php-config` at all, the command goes on without it, and PIE checks for build tools itself and offers to install PHP's development files.

### Finding PIE

The command looks for `pie` on your `PATH`, then in `~/.local/bin`. A PIE counts only if the running PHP binary can run it and `pie --version` identifies itself as PIE.

When no PIE is found, an interactive run offers to install it. Accepting downloads `pie.phar` from the latest PIE release on GitHub to `~/.local/bin/pie`, makes it executable, and runs `pie self-verify` to check the release's attestation. A copy that fails verification is removed and the command stops. Nothing is downloaded without a yes, so a non-interactive run without PIE stops and asks you to run the command interactively. A machine with no home directory cannot receive PIE, and the command says so.

### Installing

Each selected extension gets its own PIE run, executed by the PHP binary running the command and attached to your terminal, so PIE can ask for a `sudo` password or offer to install missing build tools:

```shell
<php> <pie> install php-io-extensions/posi:^0.10 --with-php-config=<php-config>
```

A failed build does not stop the extensions after it. After each successful run, the command asks the same binary which version it now loads, and reports one of these outcomes per extension:

| Outcome | Meaning |
| --- | --- |
| `installed` | The binary loads the extension on the `^0.10` line. |
| `failed (PIE exit code N)` | PIE exited with a non-zero code. |
| `failed (<message>)` | PIE could not be started. |
| `installed by PIE, but <php> does not load it` | PIE finished, but the binary does not load the extension. |
| `installed by PIE, but <php> loads <version>` | The binary still loads a version off the `^0.10` line. |

## scrapyard:modules

`scrapyard:modules` installs the `microscrap` packages, which hold the low-level bindings and the two adapters, into your application:

| Module | Package | Provides | Needs |
| --- | --- | --- | --- |
| `gpio` | `microscrap/gpio` | libgpiod digital IO over ext-posi | ext-posi `^0.10` |
| `i2c` | `microscrap/i2c` | i2c-dev buses over ext-posi | ext-posi `^0.10` |
| `spi` | `microscrap/spi` | spidev buses over ext-posi | ext-posi `^0.10` |
| `uart` | `microscrap/uart` | serial ports over ext-posi | ext-posi `^0.10` |
| `mpsse` | `microscrap/mpsse` | MPSSE SPI, I2C and GPIO over ext-ftdi | ext-ftdi `^0.10` |
| `scrapyard-linux` | `microscrap/scrapyard-linux` | the `native` connection drivers for Linux boards | Linux and ext-posi `^0.10` |
| `scrapyard-usb` | `microscrap/scrapyard-usb` | the `usb` connection drivers for FTDI bridges | ext-ftdi `^0.10` |

The two adapters require the binding packages they sit on, so installing `scrapyard-linux` or `scrapyard-usb` brings those along. The [Choosing an Adapter](/docs/{{version}}/scrapyard-io/getting-started/choosing-an-adapter) page helps you decide which you need.

### Usage

```shell
php computer scrapyard:modules                  # list what this machine can run, pick, install
php computer scrapyard:modules scrapyard-usb    # install that one, with no list
```

The command takes one optional argument, `module`, the module's short name from the table above, case-insensitive. Omit it to choose from a list.

### Deciding What Can Be Installed

Each module gets the first reason that applies, checked in this order:

| Check | Reason |
| --- | --- |
| `scrapyard-linux` on any operating system but Linux | `Linux only` |
| The extension the module needs is not loaded | `needs ext-posi` or `needs ext-ftdi` |
| The extension is loaded at a version off the `^0.10` line | `needs ext-posi ^0.10, <version> is loaded` |
| Composer already installed the package into the application | `installed` |

A module with no reason is installable. The list is shown once Composer has been found, as described below. The extension checks match the `ext-*` requirements in the `microscrap` manifests, so anything the command offers is something Composer will accept. The list, the named-module behaviour, the `Nothing to install` endings and the non-interactive rule all work exactly as they do for `scrapyard:ext`.

### Finding Composer

The command looks for `composer` on your `PATH`, then for `composer.phar` in the application's root. A candidate counts only if the running PHP binary can run it and `composer --version` identifies itself as Composer. Composer is never downloaded: when none is found, the command stops and points you to getcomposer.org.

Composer is run by the PHP binary running the command, not by whatever `php` its shebang line finds. That matters because Composer checks each package's `ext-*` requirements against the PHP that runs it, and the extensions you just installed are loaded by this binary.

### Installing

Every selected module goes into one `composer require`, run in the application's root and attached to your terminal:

```shell
<php> <composer> require microscrap/scrapyard-linux:^0.10 microscrap/gpio:^0.10 --working-dir=<app>
```

Composer resolves the modules together, so they land together or not at all, and every selected module reports the same outcome: `installed`, `failed (Composer exit code N)`, or `failed (<message>)` when Composer could not be started.

## Output and Exit Codes

When a command installs something, it prints one line per extension or module with its outcome. Otherwise it prints the note it ended with: an informational note for `Nothing to install` and `None selected.`, and an error for anything else, such as a missing PIE or Composer.

| Exit code | When |
| --- | --- |
| `0` | Every extension or module asked for reports `installed`, there was nothing to install, or you selected nothing. |
| `1` | Any outcome other than `installed`, or the command stopped before installing, for example because no PIE or Composer could be used, or a non-interactive run named nothing. |

Because a named run asks nothing, both commands work in provisioning scripts:

```shell
php computer scrapyard:ext posi && php computer scrapyard:modules scrapyard-linux
```

The first run on a fresh machine still needs PIE installed beforehand, since a non-interactive run never downloads it.
