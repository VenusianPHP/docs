# Errors

NSError and NSException become MetalException. A short byte string becomes ValueError.

## Overview

`MetalException` extends `Exception`.

An `NSError**` out-parameter is not in the PHP signature. The method name still keeps `Error`. The call is made with `&error`. A nil result throws `MetalException` whose message is `localizedDescription` and whose code is the `NSError` code. A non-nil result is returned even when `error` is also set (a warning). The shader compiler's log is that message for `newLibraryWithSourceOptionsError`.[^runtime]

`METAL_BEGIN` / `METAL_END` wrap every binding body in an autorelease pool and a `@try`. An `NSException` becomes `MetalException` with message `"<name>: <reason>"`.

Metal aborts the process for some descriptor mistakes (`vertexFunction must not be nil`) unless `METAL_ERROR_MODE=1`, which reports them as `NSException`. MINIT sets that variable when the process has not set it.[^module]

A `string|int` byte argument that is a string shorter than the required count throws `ValueError`. Address `0` throws `ValueError`. Any other address is trusted.

[^runtime]: metal_throw_nserror and METAL_BEGIN
[^module]: METAL_ERROR_MODE
