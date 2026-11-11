# Adding a binding

Stub, gen_stub, the C file that includes the stub's arginfo and registers its functions, the test, the support list.

## Overview

1. Declare in the matching `stubs/*.stub.php`: context, devices and layouts in `soundio.stub.php`, streams and ring buffer in `soundio_stream.stub.php`, classes and fields in `soundio_types.stub.php`, constants (`@var int` + `@cvalue`) in `soundio_constants.stub.php`. Lists in prose, not `@param list<…>` (gen_stub refuses it).
2. `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs`. Commit the stub and its arginfo.
3. `PHP_FUNCTION` in `src/soundio.c` / `src/stream.c`: `SOUNDIO_ARG` / `DEVICE_ARG` / `OUT_ARG` / `IN_ARG` / `RING_ARG` for handles libsoundio dereferences, `LIBSOUNDIO_PTR` where it takes NULL, `libsoundio_list_count` for a list with its count, `ZEND_TRY_ASSIGN_REF_*` for out-params.
4. A new field: its property in `soundio_types.stub.php` and its read/write branch in `src/types.c`. A callback field libsoundio calls off the PHP thread is an `int` address.
5. A refusal needs a site in `bindings.json` (maintainer-edited) and a probe in `tests/Probes` whose off-run crashes; the throw carries `/* binding:<id> */`.
6. Add a behaviour test on `SoundIoBackendDummy`, then `php84 scripts/support.php`.
