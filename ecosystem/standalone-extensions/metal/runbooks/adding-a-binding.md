# Adding a binding

Stub, gen_stub, one .m per stub, config.m4 source list, surface test.

## Overview

1. Declare the class in the stub for its SDK header group (`stubs/<Class>.stub.php`, `@generate-class-entries`). Enums from that header go in `stubs/MTLTypes.stub.php`. Copy the numeric value from the macOS SDK header. Case name: the C constant without its type prefix, upper snake case. A case that would start with a digit is prefixed `TYPE_` (`MTLTextureType2D` → `TYPE_2D`).
2. `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs` writes `stubs/<Class>_arginfo.h`. Commit the stub and the header.
3. New class: `src/<Class>.m` includes its arginfo and defines `metal_register_<Class>()` (`register_class_*`, `metal_object_setup` for a handle, `metal_map_native` with `@protocol` or `[X class]`). Declare `metal_register_*` and `metal_ce_<Class>` in `src/runtime.h`, define the `ce` in `src/metal.m`, call register from MINIT, and add the `.m` to `METAL_SOURCES` in `config.m4`.
4. Method body: parse parameters, then `METAL_BEGIN` … `METAL_END`. `new…` and `alloc`/`init` return +1 and use `metal_box_owned`. Autoreleased returns use `metal_box`. Enums use `metal_enum_param` on the way in and `metal_return_enum` on the way out. A nil `NSError**` result calls `metal_throw_nserror` and `RETURN_THROWS()`.
5. `tests/SurfaceTest.php` reads the stubs. Add a behaviour test. Build and run the suite per [build](/docs/{{version}}/ecosystem/standalone-extensions/metal/runbooks/build-install-test).

[^build]: Build runbook
