# Native buffers

posi_mem_alloc/free/read/write, the live-allocation registry, and how addresses reach ioctl() structs.

## Purpose

`ioctl()` structs such as `i2c_rdwr_ioctl_data`/`i2c_msg` and `spi_ioc_transfer` hold addresses of further buffers. PHP strings move, so they cannot be pointed at. `posi_mem_alloc()` hands out a stable address as an int; caller `pack('P', …)`s it into the struct, passes the struct through `ioctl()` bytes mode, reads results back with `posi_mem_read()`. See [descriptors](/docs/{{version}}/ecosystem/standalone-extensions/posi/api/descriptors-and-paths).

## Functions

| Function | Does | Refuses (`ValueError`) |
|---|---|---|
| `posi_mem_alloc(int $size): int` | `ecalloc(1, size)`, records address → size | size < 1 |
| `posi_mem_free(int $ptr): void` | `efree`, drops record; 0 = no-op like `free(NULL)` | unknown or already freed address |
| `posi_mem_write(int $ptr, string $data, int $offset = 0): void` | `memcpy` in | unknown address; range past end |
| `posi_mem_read(int $ptr, int $size, int $offset = 0): string` | `memcpy` out | unknown address; negative size; range past end |

Range rule: `0 ≤ offset ≤ size` and `length ≤ size − offset`, written to avoid overflow.[^posi-c]

## Registry

`POSI_G(allocations)`, HashTable keyed by address, value = size. Every read/write/free looks the address up first, so a foreign, stale or double-freed address throws before memory is touched. Request memory (`ecalloc`), so `memory_limit` counts it. RSHUTDOWN frees what is left. Per thread under ZTS.[^posi-c]

Registry guards posi's own access only. An address packed into an `ioctl()` struct goes to the kernel unchecked; struct layout (padding, pointer width) is caller's job. 64-bit Linux `i2c_msg` = 16 bytes: `pack('vvvxxP', addr, flags, len, ptr)`; `i2c_rdwr_ioctl_data` = `pack('PVx4', msgs, n)`. Proven on Pi 5 against ADXL343 (README example).

[^posi-c]: posi.c
