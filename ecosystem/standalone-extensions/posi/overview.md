# Overview

Exposes ioctl() and fcntl() to php-land.

<div align="center" id="header">

<h2>ext-posi</h2>

<h4>Exposed missing bindings for POSIX that ext-posix didn't. For PHP 8.4+</h4>

Exposes `ioctl()` and `fcntl()` to php-land. 

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/posi/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/posi/actions/workflows/ci.yml)
[![Packagist](https://img.shields.io/packagist/v/php-io-extensions/posi?style=flat-square)](https://packagist.org/packages/php-io-extensions/posi)
[![PHP](https://img.shields.io/packagist/dependency-v/php-io-extensions/posi/php?style=flat-square&label=PHP)](https://packagist.org/packages/php-io-extensions/posi)
[![License](https://img.shields.io/github/license/php-io-extensions/posi?style=flat-square)](https://github.com/php-io-extensions/posi/tree/HEAD/LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux_%7C_macos-blue?style=flat-square&logo=linux&logoColor=white)](https://pubs.opengroup.org/onlinepubs/9799919799/)
[![OKF](https://img.shields.io/badge/OKF-0.2-6f42c1?style=flat-square&label=knowledge%20bundle)](/docs/{{version}}/ecosystem/standalone-extensions/posi/overview)
[![PIE](https://img.shields.io/badge/PIE-installable-4f5b93?style=flat-square&logo=php&logoColor=white)](https://github.com/php/pie)

</div>

PHP talks to files, sockets and pipes through streams, and a stream hides the file descriptor on purpose. For a file that's fine. But if you want to play with, say a UART or I2C sensor, that's not going to work. Sure, you can fopen('/dev/ttyAMA0') but you can't configure the port, and you can't ioctl() anything. 
If you want to work with hardware, you usually need to learn C or Python and use their libraries. Or even less-viable for production: FFI into those runtimes, increasing what you ship.  

ext/posix, which ships with PHP, has the process-level calls and stops before `open(2)`, `read(2)`, `ioctl(2)`, `fcntl(2)`, `termios` and `wait(2)`. Those are the POSIX calls hardware needs.

<b>posi</b> is the rest of ext/posix: the descriptor, device-control, terminal and process-wait calls, bound one to one under the names C uses, with the platform's own constant values compiled in. Though like ext-posix, it does not yet bind all of the POSIX library. It does, however bind what talking to a device node requires, and it never redefines a function ext/posix already has.

`ioctl()` and `fcntl()` are the two that open the door. Every driver that shows up as a node under /dev is driven through them: gpio chips, i2c and spi buses, serial ports, cameras. A C library that is only a wrapper over those calls, libgpiod being the obvious one, can be reimplemented in PHP on top of these two with no C dependency at all.

<b>The only problem?</b> Without an extension the way to reach these calls is FFI: parse a header, declare every struct by hand, guess the constant values per platform, and run with ffi.enable on. posi needs none of that. The constants come from the headers at build time, every argument is checked against the C type it lands in,  it loads under NTS, ZTS and opcache preloaded like any other extension.

### Basic usage

Most ways you will interface with posi are in two parts -

Open the device node with `posix_open()` and get back its file descriptor. Then tell the driver what you want with `ioctl()`: the request number and the shape of its third argument come from the driver's header, and the shape of `$arg` tells posi how to pass it. Here `I2C_SLAVE` takes the address as the argument itself, so an int goes straight through.

```php

const I2C_SLAVE = 0x0703;   // from <linux/i2c-dev.h>

// Open the bus and get back a raw file descriptor, not a stream.
$fd = posix_open('/dev/i2c-1', O_RDWR);
if ($fd < 0) {
    throw new RuntimeException('open: errno ' . posi_errno());
}

// Point the bus at one device for every read and write that follows.
if (ioctl($fd, I2C_SLAVE, 0x53, $unused) < 0) {
    throw new RuntimeException('I2C_SLAVE: errno ' . posi_errno());
}
```

Talk to it: move bytes with `posix_write()` and `posix_read()`, exactly as C would. Close it yourself when you're done; nothing closes a descriptor for you.

```php
// Write the register number, read the byte at it.
posix_write($fd, "\x00", 1);
$byte = posix_read($fd, 1);

if ($byte === false) {
    // The read failed; posi_errno() says why
    $this->handle(posi_errno());
}
else
{
    printf("DEVID 0x%02X\n", ord($byte));   // 0xE5 on an ADXL343
}

posix_close($fd);
```

#### Examples

##### Configure and read a serial port

A serial port is configured through termios rather than `ioctl()`: pull the port's struct, edit it in place, push it back, then wait for bytes with `posix_ppoll()`.

```php
$fd = posix_open('/dev/ttyAMA0', O_RDWR | O_NOCTTY | O_NONBLOCK);
if ($fd < 0) {
    throw new RuntimeException('open: errno ' . posi_errno());
}

$termios = tcgetattr($fd);
$termios['c_iflag'] &= ~(IXON | IXOFF | ICRNL);
$termios['c_oflag'] &= ~OPOST;
$termios['c_lflag'] &= ~(ICANON | constant('ECHO') | ISIG | IEXTEN);
$termios['c_cflag'] = ($termios['c_cflag'] & ~(CSIZE | PARENB | CSTOPB)) | CS8 | CLOCAL | CREAD;
tcsetattr($fd, TCSANOW, $termios);
posi_set_baud_rate($fd, 115200);

posix_write($fd, "AT\r\n", 4);

while (true)
{
    // 1 = readable, 0 = timed out after 2 s, -1 = error with posi_errno() set
    $ready = posix_ppoll($fd, 2_000_000_000, POLLIN);

    if ($ready === 1) {
        $bytes = posix_read($fd, 256);
        $this->handle($bytes);
    }
    else
    {
        // Nothing arrived in time; stop listening and give the descriptor back
        posix_close($fd);
        break;
    }
}
```

### Requirements

| | |
|---|---|
| OS | Linux or macOS. Every call is POSIX; the two Linux-only pieces (`ppoll(2)` and the `termios2` custom baud path) have a POSIX fallback on macOS. Windows is excluded. |
| PHP | 8.4 or newer, NTS or ZTS. |
| Extensions | ext/posix, which ships with PHP. posi requires it and loads after it, because `posix_getuid()` and `posix_setuid()` come from there under the same names. Built in on Homebrew PHP; a shared `posix.so` on Debian packaging, enabled by default. |
| Libraries | None beyond libc. |
| Optional | ext/pcntl, ext/sockets, ext-kqueue. Not needed; when present, posi loads after them so constants they share are registered once. |

To build it you need a C compiler and the development files of the PHP you intend to load it into:

```bash
 # Debian, Ubuntu, Raspberry Pi OS
sudo apt install build-essential php8.4-dev

 # macOS: Xcode Command Line Tools, and Homebrew's PHP ships phpize and php-config
xcode-select --install
brew install php@8.4
```
### Installation

#### With PHP PIE (recommended)

[PIE](https://github.com/php/pie) is the PHP Foundation's installer for extensions. It downloads the tagged source from Packagist, builds it against the PHP on your `PATH`, installs the module and enables it. `sudo` where your PHP's extension directory is root-owned, as on Debian; not on a Homebrew Mac:

```bash
pie install php-io-extensions/posi
```

#### Manually (install script)

The repository ships two installers, one per platform. Each one builds in a temporary copy of the checkout for each PHP it targets, installs `posi.so` into that PHP's `extension_dir`, writes `30-posi.ini` into its `conf.d` scan directory, checks the module loads, and leaves the checkout clean. The macOS one also ad-hoc signs the module so the system loads it on first use.

```bash
git clone https://github.com/php-io-extensions/posi.git
cd posi

./install-debian-trixie.sh             # Debian Trixie, Ubuntu 24.04+, Raspberry Pi OS: the php on PATH
./install-macos.sh                     # Homebrew php@8.4 and php@8.4-zts
./install-macos.sh /path/to/bin/php    # either script takes specific PHP binaries
```

#### Manually (phpize)

```bash
git clone https://github.com/php-io-extensions/posi.git
cd posi
phpize
./configure --enable-posi
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
sudo make install
```

Then enable it: add `extension=posi.so` to your `php.ini`, or drop that line into a file in the scan directory that `php --ini` reports. On Debian packaging that file must sort after the one that loads `posix`, which `30-posi.ini` does next to `20-posix.ini`.

#### Verify

```console
$ php --ri posi

posi

posi support => enabled
Version => 0.10.x
```
### API

Every function is a global, named as C names it. A failed call returns what C returns, `-1` or `false`, and keeps `errno` for `posi_errno()`. A bad PHP argument, an int wider than the C type or a length past the end of the data, throws `ValueError` or `TypeError` before the syscall; nothing is truncated. Constants (`O_*`, `F_*`, `POLL*`, `S_IF*`, `TCSA*`, `B*`, the termios flag bits, `W*`, `E*`) carry the platform's own values from its headers.

#### Descriptors

##### `posix_open(string $device_path, int $flags = O_RDWR, int $mode = 0644): int`

Opens a path and returns a file descriptor, or `-1` (same semantics as C `open(2)`).

* `$device_path` — device node, FIFO, socket path, or regular file.
* `$flags` — `O_*` access mode and creation flags, such as `O_RDWR | O_NOCTTY | O_NONBLOCK`.
* `$mode` — permission bits applied when `O_CREAT` is set, under the process umask.

**Example**

```php
$fd = posix_open('/dev/i2c-1', O_RDWR);
if ($fd < 0) {
    throw new RuntimeException('open: errno ' . posi_errno());
}
```

---

##### `posix_close(int $fd): int`

Closes a descriptor. Returns `0`, or `-1` (same semantics as C `close(2)`). Nothing else closes a descriptor posi opened; a descriptor left open is reclaimed at process exit.

**Example**

```php
posix_close($fd);
```

---

##### `posix_read(int $fd, int $bytes_to_read): string|false`

Reads up to `$bytes_to_read` bytes. Returns the bytes read, `""` at end of file, or `false` (same semantics as C `read(2)`). A negative length throws `ValueError`.

**Example**

```php
$chunk = posix_read($fd, 256);
if ($chunk === false) {
    throw new RuntimeException('read: errno ' . posi_errno());
}
```

---

##### `posix_write(int $fd, string $data, int $bytes_to_write): int`

Writes the first `$bytes_to_write` bytes of `$data`. Returns the number written, or `-1` (same semantics as C `write(2)`). A length past the end of `$data` throws `ValueError`.

**Example**

```php
$written = posix_write($fd, "\x00\x2D\x08", 3);
if ($written !== 3) {
    throw new RuntimeException('short write: ' . $written);
}
```

---

##### `posix_lseek(int $fd, int $offset, int $whence): int`

Repositions the descriptor's offset. Returns the new offset from the start of the file, or `-1` (same semantics as C `lseek(2)`). `$whence` is `SEEK_SET`, `SEEK_CUR` or `SEEK_END`.

**Example**

```php
$fd = posix_open('/tmp/posi-demo.bin', O_RDWR | O_CREAT | O_TRUNC, 0644);
posix_write($fd, "hello world", 11);
posix_lseek($fd, 6, SEEK_SET);
echo posix_read($fd, 5);   // world
posix_close($fd);
```

---

##### `posix_readv(int $fd, array $iovecs): array|false`

Reads into several buffers in one call. `$iovecs` is a list of `['len' => int]`; the result is `['res' => total bytes, 'buffers' => [string, ...]]` with each buffer cut to the bytes that landed in it, or `false` (same semantics as C `readv(2)`). More than `IOV_MAX` entries, or a `len` that is missing, negative or not an int, throws `ValueError`.

**Example**

```php
$fd = posix_open('/tmp/posi-demo.bin', O_RDONLY);
$io = posix_readv($fd, [['len' => 5], ['len' => 6]]);
// $io['res'] === 11, $io['buffers'] === ['hello', ' world']
posix_close($fd);
```

---

##### `posix_recv(int $fd, int $len, int $flags = 0): string|false`

Receives up to `$len` bytes from a socket descriptor. Returns the bytes, or `false` (same semantics as C `recv(2)`). `$flags` takes `MSG_PEEK`, `MSG_WAITALL`, `MSG_OOB`.

**Example**

```php
// $sock is a connected socket descriptor
$peek = posix_recv($sock, 4, MSG_PEEK);   // look without consuming
$data = posix_recv($sock, 4);             // now consume
```

---

##### `posix_ppoll(int $fd, int $timeout_ns = 0, int $events = 0): int`

Waits for one descriptor to become ready. Returns `1` when any requested event (or `POLLHUP`/`POLLERR`) is pending, `0` on timeout, or `-1` (same semantics as C `ppoll(2)`; `poll(2)` on macOS, which rounds the timeout up to whole milliseconds).

* `$timeout_ns` — nanoseconds to wait; `0` returns at once, a negative value waits forever.
* `$events` — a `POLL*` mask; `0` means `POLLIN`.

To wait on many descriptors at once, use ext-epoll or ext-kqueue instead.

**Example**

```php
if (posix_ppoll($fd, 2_000_000_000, POLLIN) === 1) {   // up to 2 s
    $bytes = posix_read($fd, 256);
}
```

---

##### `posix_fdopen(int $fd, string $mode)`

Wraps a descriptor as a PHP stream resource, or returns `false` (same semantics as C `fdopen(3)`). The descriptor is not duplicated: the stream owns it, `fclose()` closes it, and the stream works with `fgets()`, `stream_select()` and everything else that takes a stream. A descriptor that is not open fails with `errno` set.

* `$mode` — a PHP stream mode such as `'r'`, `'w'` or `'r+'`.

**Example**

```php
$fd = posix_open('/dev/ttyAMA0', O_RDWR | O_NOCTTY);
$port = posix_fdopen($fd, 'r+');
$line = fgets($port);
fclose($port);   // closes $fd too
```

---

##### `posix_fileno($stream): int|false`

Returns the descriptor a PHP stream wraps, or `false` when it wraps none (same idea as C `fileno(3)`). Socket streams give their socket, file streams their file descriptor. The descriptor is not duplicated and still belongs to the stream. A stream with no descriptor, such as `php://memory`, fails with `posi_errno()` at `EBADF`.

* `$stream` — any PHP stream resource.

**Example**

```php
[$a, $b] = stream_socket_pair(STREAM_PF_UNIX, STREAM_SOCK_STREAM, STREAM_IPPROTO_IP);
posix_write(posix_fileno($a), 'hi', 2);
echo fread($b, 2);   // hi
```

---

##### `posix_dup(int $fd): int`

Returns a new descriptor for the same open file, or `-1` (same semantics as C `dup(2)`). Closing one copy leaves the other open.

* `$fd` — an open file descriptor.

**Example**

```php
$copy = posix_dup(posix_fileno($a));
posix_write($copy, 'again', 5);
posix_close($copy);   // $a stays open
```

---

##### `posix_socket_fdopen(int $fd)`

Wraps a stream-socket descriptor as a PHP socket stream, or returns `false` (C `fdopen(3)`, for sockets). Where `posix_fdopen()` gives a plain file stream, this one comes from PHP's `tcp` transport: `stream_socket_accept()`, `stream_socket_get_name()` and `stream_socket_enable_crypto()` work on it and on every connection it accepts. The descriptor is not duplicated: the stream owns it and `fclose()` closes it. A descriptor that is not open fails with `EBADF`, a non-socket with `ENOTSOCK`, a datagram socket with `EPROTOTYPE`.

The use: threads can't share PHP streams, but they share descriptors. One thread listens, every other thread opens its own stream over a `dup()` of that socket and accepts on it.

* `$fd` — an open `SOCK_STREAM` socket descriptor (TCP or Unix).

**Example**

```php
$server = stream_socket_server('tcp://127.0.0.1:8080');
$fd = posix_fileno($server);

// In each ext-parallel thread:
$listener = posix_socket_fdopen(posix_dup($fd));
$connection = stream_socket_accept($listener);
```

---

#### Descriptor control

##### `fcntl(int $fd, int $cmd, mixed $arg, mixed &$value): int`

Performs a descriptor control operation and returns the C result (same semantics as C `fcntl(2)`).

* `$cmd` — an `F_*` command.
* `$arg` — an int, a bool, or `null` for commands that take no argument. For `F_GETLK`, `F_SETLK` and `F_SETLKW`, an array `['type', 'whence', 'start', 'len', 'pid']` describing a `struct flock`; missing keys count as `0`. Any other type throws `TypeError`.
* `$value` — on success receives the datum for `F_GETFD`, `F_GETFL` and `F_GETOWN`, the resulting lock array for lock commands, and a copy of `$arg` otherwise. On failure it receives `false`.

**Example — make a descriptor non-blocking**

```php
fcntl($fd, F_GETFL, null, $flags);
fcntl($fd, F_SETFL, $flags | O_NONBLOCK, $unused);
```

**Example — take a write lock on a file**

```php
$lock = ['type' => F_WRLCK, 'whence' => SEEK_SET, 'start' => 0, 'len' => 0];
if (fcntl($fd, F_SETLK, $lock, $result) < 0 && posi_errno() === EAGAIN) {
    // someone else holds it
}
```

---

##### `ioctl(int $fd, int $request, mixed $arg, mixed &$value): int`

Performs a device-specific operation and returns the C result (same semantics as C `ioctl(2)`). `$request` is passed as `unsigned long` unchanged, so Linux `_IOR`/`_IOW` numbers above `INT_MAX` work. The shape of `$arg` decides how the third C argument is passed:

| `$arg` | C receives | `$value` after success |
|---|---|---|
| `['value' => int]` | a pointer to that int | the int, as the kernel left it |
| `['bytes' => string]`, `['data' => string]`, or a plain string | a pointer to a private copy of the bytes | the copy, as the kernel left it |
| an int or bool | the number itself, as the pointer-sized argument | a copy of `$arg` |
| `null` | `NULL` | the return value when positive, else `null` |

On failure `$value` is `false`. An array with none of those keys throws `ValueError`; any other type throws `TypeError`. The driver's header says which shape each request wants; posi cannot know. An int that is an address goes to the kernel as an address, which is what passing a `posi_mem_alloc()` buffer relies on.

**Example — a request that takes a number**

```php
const I2C_SLAVE = 0x0703;
ioctl($fd, I2C_SLAVE, 0x53, $unused);
```

**Example — a request that fills an int**

```php
// FIONREAD: how many bytes are waiting to be read
const FIONREAD = PHP_OS_FAMILY === 'Darwin' ? 0x4004667F : 0x541B;
ioctl($fd, FIONREAD, ['value' => 0], $waiting);
```

**Example — a request that reads and writes a struct**

```php
// SPI_IOC_RD_MODE on Linux: one byte in, one byte out
const SPI_IOC_RD_MODE = 0x80016B01;
ioctl($fd, SPI_IOC_RD_MODE, ['bytes' => "\x00"], $mode);
echo ord($mode);
```

---

#### Paths

##### `posix_chmod(string $path, int $mode): int`

Sets the permission bits on a path. Returns `0`, or `-1` (same semantics as C `chmod(2)`).

**Example**

```php
if (posix_chmod('/dev/gpiochip0', 0660) < 0) {
    throw new RuntimeException('chmod: errno ' . posi_errno());
}
```

---

##### `posix_fchmod(int $fd, int $mode): int`

Like `posix_chmod()`, on an open descriptor (same semantics as C `fchmod(2)`).

**Example**

```php
posix_fchmod($fd, 0600);
```

---

##### `posix_chown(string $path, int $owner, int $group): int`

Sets the owner and group of a path. Returns `0`, or `-1` (same semantics as C `chown(2)`). Pass `-1` for either to leave it unchanged.

**Example**

```php
posix_chown('/tmp/posi-demo.bin', posix_getuid(), -1);
```

---

##### `posix_fchown(int $fd, int $owner, int $group): int`

Like `posix_chown()`, on an open descriptor (same semantics as C `fchown(2)`).

**Example**

```php
posix_fchown($fd, -1, posix_getgid());
```

---

##### `posix_umask(int $mask): int`

Sets the file mode creation mask and returns the previous one (same semantics as C `umask(2)`).

**Example**

```php
$previous = posix_umask(0077);
$fd = posix_open('/tmp/posi-private.bin', O_RDWR | O_CREAT, 0666);   // lands as 0600
posix_umask($previous);
```

---

##### `posix_lstat(string $path): array|false`

Stats a path without following a final symlink. Returns the stat array (`dev`, `ino`, `mode`, `nlink`, `uid`, `gid`, `rdev`, `size`, `atime`, `mtime`, `ctime`, `blksize`, `blocks`), or `false` (same semantics as C `lstat(2)`).

**Example**

```php
$st = posix_lstat('/dev/i2c-1');
if ($st !== false && ($st['mode'] & S_IFMT) === S_IFCHR) {
    // a character device
}
```

---

##### `posix_hostname(): string|false`

Returns the host name, or `false` (same semantics as C `gethostname(3)`).

**Example**

```php
echo posix_hostname();
```

---

#### Processes

##### `posix_wait(?int &$status = null): int`

Waits for any child to change state. Returns the child's pid, or `-1`; `$status` receives the raw wait status (same semantics as C `wait(2)`).

**Example**

```php
$pid = posix_wait($status);
if ($pid > 0 && posix_wifexited($status)) {
    echo "child {$pid} exited with ", posix_wexitstatus($status), "\n";
}
```

---

##### `posix_waitpid(int $pid, ?int &$status = null, int $options = 0): int`

Waits for one child, or any child when `$pid` is `-1`. Returns the pid, `0` when `WNOHANG` is set and nothing has changed, or `-1` (same semantics as C `waitpid(2)`). `$options` takes `WNOHANG`, `WUNTRACED`, `WCONTINUED`.

**Example**

```php
// poll a child without blocking
if (posix_waitpid($child, $status, WNOHANG) === $child) {
    // it is gone; $status says how
}
```

---

##### `posix_wifexited(int $status): bool`, `posix_wexitstatus(int $status): int`, `posix_wifsignaled(int $status): bool`, `posix_wtermsig(int $status): int`, `posix_wifstopped(int $status): bool`, `posix_wstopsig(int $status): int`, `posix_wifcontinued(int $status): bool`

The `<sys/wait.h>` status macros, applied to a `$status` from `posix_wait()` or `posix_waitpid()`.

**Example**

```php
$pid = posix_waitpid(-1, $status);

match (true) {
    posix_wifexited($status)   => printf("exit %d\n", posix_wexitstatus($status)),
    posix_wifsignaled($status) => printf("killed by signal %d\n", posix_wtermsig($status)),
    posix_wifstopped($status)  => printf("stopped by signal %d\n", posix_wstopsig($status)),
    default                    => print("continued\n"),
};
```

---

#### Terminals

A terminal's settings travel as one array mirroring `struct termios`: `c_iflag`, `c_oflag`, `c_cflag`, `c_lflag` (ints), `c_cc` (a list of `NCCS` ints, indexed by `VMIN`, `VTIME`, ...), and `c_ispeed`, `c_ospeed`. Every function that takes the array requires every key; the speeds are there because macOS keeps them outside `c_cflag`, and a round trip without them would apply `B0` and hang up the line. `ECHO` is a PHP keyword, so that flag is read with `constant('ECHO')`.

##### `tcgetattr(int $fd): array|false`

Reads the terminal settings of a descriptor into the array, or returns `false` (same semantics as C `tcgetattr(3)`).

**Example**

```php
$termios = tcgetattr($fd);
if ($termios === false) {
    throw new RuntimeException('not a terminal: errno ' . posi_errno());
}
```

---

##### `tcsetattr(int $fd, int $action, array $termios): int`

Applies the array to the descriptor. Returns `0`, or `-1` (same semantics as C `tcsetattr(3)`). `$action` is `TCSANOW`, `TCSADRAIN` or `TCSAFLUSH`. A Linux custom rate set through `BOTHER` survives a `tcgetattr()` → edit → `tcsetattr()` round trip.

**Example — raw mode, 8N1**

```php
$termios = tcgetattr($fd);
$termios['c_iflag'] &= ~(IXON | IXOFF | ICRNL);
$termios['c_oflag'] &= ~OPOST;
$termios['c_lflag'] &= ~(ICANON | constant('ECHO') | ISIG | IEXTEN);
$termios['c_cflag'] = ($termios['c_cflag'] & ~(CSIZE | PARENB | CSTOPB)) | CS8 | CLOCAL | CREAD;
$termios['c_cc'][VMIN] = 0;
$termios['c_cc'][VTIME] = 10;   // tenths of a second
tcsetattr($fd, TCSANOW, $termios);
```

---

##### `cfsetispeed(array $termios, int $speed): array|false`, `cfsetospeed(array $termios, int $speed): array|false`

Return the array with the input or output speed set to a `B*` constant, or `false` when the platform refuses the speed (same semantics as C `cfsetispeed(3)`/`cfsetospeed(3)`). The array is returned, not modified in place.

**Example**

```php
$termios = cfsetispeed($termios, B9600);
$termios = cfsetospeed($termios, B9600);
tcsetattr($fd, TCSANOW, $termios);
```

---

##### `cfgetispeed(array $termios): int`, `cfgetospeed(array $termios): int`

Return the input or output speed held in the array, as a `B*` value (same semantics as C `cfgetispeed(3)`/`cfgetospeed(3)`).

**Example**

```php
if (cfgetospeed(tcgetattr($fd)) === B115200) {
    // already at 115200
}
```

---

##### `tcdrain(int $fd): int`, `tcflush(int $fd, int $queue): int`, `tcflow(int $fd, int $action): int`

Wait for pending output to be sent, discard queued data (`TCIFLUSH`, `TCOFLUSH`, `TCIOFLUSH`), or suspend and resume flow (`TCOOFF`, `TCOON`, `TCIOFF`, `TCION`). Each returns `0`, or `-1` (same semantics as C `tcdrain(3)`, `tcflush(3)`, `tcflow(3)`).

**Example**

```php
posix_write($fd, $frame, strlen($frame));
tcdrain($fd);               // wait until it has left the UART
tcflush($fd, TCIFLUSH);     // drop whatever arrived meanwhile
```

---

##### `posi_set_baud_rate(int $fd, int $baud): int`

Sets both directions to `$baud` with `TCSANOW`. Returns `0`, or `-1`. The one function here with no C counterpart, because C has no portable way to ask for a rate that isn't a `B*` constant.

* A rate with a `B*` constant (50 through 4000000, where the platform defines it) goes through `tcgetattr`, `cfsetispeed`, `cfsetospeed`, `tcsetattr`.
* Any other rate on Linux goes through the kernel's `termios2` with `BOTHER`.
* Any other rate elsewhere returns `-1` with `posi_errno()` set to `EINVAL`.
* `$baud` outside `1..4294967295` throws `ValueError`.

**Example**

```php
posi_set_baud_rate($fd, 250000);   // DMX: fine on Linux, EINVAL on macOS
```

---

#### Native buffers

Some `ioctl()` requests, `I2C_RDWR` and `SPI_IOC_MESSAGE` among them, take a struct that holds pointers to further buffers. A PHP string has no stable address the kernel can be handed, so posi allocates request memory and gives you its address as an int to `pack('P', ...)` into the struct. Every address is checked against the live allocations before any memory is touched, so a foreign, freed or out-of-range access throws `ValueError` instead of crashing. Buffers still allocated when the request ends are freed then. The registry guards posi's own access only: an address packed into a struct goes to the kernel unchecked, and struct layout (padding, pointer width) is yours to get right.

##### `posi_mem_alloc(int $size): int`

Allocates `$size` zeroed bytes and returns their address. `$size` below `1` throws `ValueError`. The memory counts against `memory_limit`.

---

##### `posi_mem_free(int $ptr): void`

Releases a buffer. `0` is a no-op, like `free(NULL)`; an address not handed out by `posi_mem_alloc()`, or freed already, throws `ValueError`.

---

##### `posi_mem_write(int $ptr, string $data, int $offset = 0): void`

Copies `$data` into the buffer at `$offset`. A range past the end throws `ValueError`.

---

##### `posi_mem_read(int $ptr, int $size, int $offset = 0): string`

Copies `$size` bytes out of the buffer from `$offset`. A negative size or a range past the end throws `ValueError`.

**Example — an `I2C_RDWR` transaction: write a register number, read one byte back**

```php
const I2C_RDWR = 0x0707;
const I2C_M_RD = 0x0001;

$register = posi_mem_alloc(1);
$reply = posi_mem_alloc(1);
posi_mem_write($register, "\x00");

// struct i2c_msg { u16 addr; u16 flags; u16 len; u8 *buf; }: 16 bytes on 64-bit Linux
$messages = posi_mem_alloc(32);
posi_mem_write($messages, pack('vvvxxP', 0x53, 0, 1, $register) . pack('vvvxxP', 0x53, I2C_M_RD, 1, $reply));

// struct i2c_rdwr_ioctl_data { struct i2c_msg *msgs; u32 nmsgs; }
if (ioctl($fd, I2C_RDWR, ['bytes' => pack('PVx4', $messages, 2)], $unused) < 0) {
    throw new RuntimeException('I2C_RDWR: errno ' . posi_errno());
}
printf("DEVID 0x%02X\n", ord(posi_mem_read($reply, 1)));

posi_mem_free($messages);
posi_mem_free($reply);
posi_mem_free($register);
```

---

#### Errors

##### `posi_errno(): int`

Returns the `errno` saved by the last posi call that failed. A successful call leaves it alone. Compare it with the `E*` constants, which carry the platform's values.

**Example**

```php
if (posix_open('/dev/i2c-9', O_RDWR) < 0) {
    echo match (posi_errno()) {
        ENOENT => "no such bus",
        EACCES => "not permitted; check the group on the node",
        default => "errno " . posi_errno(),
    }, "\n";
}
```

### Extensions you might use with this one

* [ext/posix](https://www.php.net/manual/en/book.posix.php): ships with PHP and is required. posi is the other half of it: process identity and signals there, descriptors and devices here, no overlap.
* [ext-epoll](https://github.com/php-io-extensions/epoll): Linux. Wait on many of posi's descriptors at once instead of `posix_ppoll()` on one. Takes the raw int `posix_open()` returns, and hands back an epoll fd that only `posix_close()` can close.
* [ext-kqueue](https://github.com/php-io-extensions/kqueue): macOS. The same job on Darwin, and more than descriptors: a kqueue also watches timers, signals, and the children `posix_waitpid()` reaps. Its fd, too, closes only through `posix_close()`.
* [ext/pcntl](https://www.php.net/manual/en/book.pcntl.php): ships with PHP. `pcntl_fork()` makes the children that `posix_wait()` and `posix_waitpid()` reap.

### AI-assisted development

This codebase was built with LLM assistance under human direction. Prompts, reviews, and architectural decisions were owned by a professional software engineer — the model accelerates drafting and exploration; it does not replace judgment on APIs, dependency direction, or what ships.

### Agentic Documentation

This repository carries an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle at [`.okf/`](https://github.com/php-io-extensions/posi/tree/HEAD/.okf): Markdown with YAML frontmatter, readable by you and loadable by a coding agent. It records what the README doesn't: how the module is laid out, every `ioctl()` and `fcntl()` argument mode and why each check exists, the termios array shape and the `BOTHER` round trip, the native-buffer registry, how the stub becomes `posi_arginfo.h`, the 0.9 to 0.10 call map, and a log of every change that altered behaviour.

Start at [`.okf/index.md`](/docs/{{version}}/ecosystem/standalone-extensions/posi/overview). [`AGENTS.md`](https://github.com/php-io-extensions/posi/blob/HEAD/AGENTS.md) is the short rule sheet an agent reads before touching the C, the stub, or packaging; each rule points into the bundle for the reason behind it.

Point your agent at the repo and it has the same context the maintainer has. Point yourself at it when the README's answer is "it does X" and you want "because".
### Resources

* [POSIX.1-2024](https://pubs.opengroup.org/onlinepubs/9799919799/): the standard every call here comes from. Each function in the API table names its page. The man pages are the manual; this README only adds what PHP changes.
* [`ioctl(2)`](https://man7.org/linux/man-pages/man2/ioctl.2.html) and [`ioctl_list(2)`](https://man7.org/linux/man-pages/man2/ioctl_list.2.html) on Linux: what the third argument is for each request. The driver's own header is the final word.
* [`termios(3)`](https://man7.org/linux/man-pages/man3/termios.3.html): the flag words and control characters the termios array carries.
* [Upgrading from 0.9](/docs/{{version}}/ecosystem/standalone-extensions/posi/reference/upgrade-from-09): the Zephir `Posi\*` statics and `microscrap/posix` helpers mapped call by call onto 0.10.
* [PIE](https://github.com/php/pie): the PHP Foundation's extension installer.
* [`gen_stub.php`](https://github.com/php/php-src/blob/master/build/gen_stub.php): the php-src stub format. [`posi.stub.php`](https://github.com/php-io-extensions/posi/blob/HEAD/posi.stub.php) is the API declaration; `posi_arginfo.h` is generated from it.
* [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): the spec the [`.okf/`](https://github.com/php-io-extensions/posi/tree/HEAD/.okf) bundle follows.
### Running the test suite

The suite is Pest v4 and needs no hardware: pipes, FIFOs, scratch files, ptys and child processes stand in for devices. It runs on Linux and macOS. Build the module in the clone, then point `php` at it:

```bash
git clone https://github.com/php-io-extensions/posi.git
cd posi
phpize && ./configure --enable-posi && make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
composer install
php -n -d extension="$PWD/modules/posi.so" vendor/bin/pest
```

```console
Tests:    1 skipped, 66 passed (202 assertions)
Duration: 0.34s
```

`-n` skips your `php.ini`, so the suite tests the clone and not an installed `posi.so`; without it, a PHP that already loads posi warns `Module "posi" is already loaded` and keeps the installed one. Where ext/posix is a shared extension rather than built in, as on Debian packaging, add `-d extension=posix` before the posi one, since `-n` dropped the ini that loads it. A module only loads in the PHP whose `phpize` built it: for Homebrew's ZTS build, run `phpize` and pass `--with-php-config` from `/opt/homebrew/opt/php@8.4-zts/bin`.
### Contributing

Open an issue first for anything beyond a typo. Pull requests change `posi.stub.php` and `posi.c` (or `posi_termios.c`) together, regenerate `posi_arginfo.h` with gen_stub, and add a Pest test for the behaviour. CI must be green on every cell of the matrix. Read [`AGENTS.md`](https://github.com/php-io-extensions/posi/blob/HEAD/AGENTS.md) for the rules the code follows.

### Security

posi gives PHP code the same access to devices and memory as C code in the same process. See [SECURITY.md](https://github.com/php-io-extensions/posi/blob/HEAD/SECURITY.md) for what that means and how to report a vulnerability.

### License

MIT. See [LICENSE](https://github.com/php-io-extensions/posi/tree/HEAD/LICENSE).
