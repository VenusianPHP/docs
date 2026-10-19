# Adding a binding

Stub, gen_stub, one .m per stub, config.m4 source list, surface test.

## Overview

1. Declare in the stub of the SDK header group (`stubs/<Class>.stub.php`, `@generate-class-entries`). Enums declared in that header go in the same stub. Values from the SDK header.
2. `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs` → `stubs/<Class>_arginfo.h`. Commit both.
3. New class: `src/<Class>.m` includes its arginfo, defines `appkit_register_<Class>()` (register, `appkit_object_setup()`, `appkit_map_objc_class()` for ObjC); declare it + `appkit_ce_<Class>` in `src/runtime.h`, define the ce in `src/appkit.m`, call register in MINIT after its parent; add CF type IDs to `appkit_box_cf()`; add the `.m` to `APPKIT_SOURCES` in `config.m4`.
4. Method body: parse params, `APPKIT_REQUIRE_MAIN_THREAD()` only on the AppKit UI families the `main-thread-appkit-ui` site covers ([errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/appkit/architecture/errors-and-threads)), body inside `APPKIT_BEGIN … APPKIT_END`, return via `appkit_box_objc/cf`, `appkit_return_enum`, `RETURN_*`; nil → null, error codes as `int`. Mode params through `appkit_run_loop_mode()`. Callback params through `appkit_callout_new()` + native context retain/release; new glue is the maintainer's (`bindings.json` `glue`).
5. No refusal, pre-check or result throw unless a probe on a real build shows the call crashes. A kept one: `if (!APPKIT_PROBE_OFF("<id>") && (<check>))`, `/* binding:<id> */` on the throw line, the maintainer's `sites` entry, a `tests/Probes/<Name>Test.php`.
6. New native symbol: an agent may add it to `bindings.json` `symbols`; ext-guard validates it against the SDK headers.
7. `tests/SurfaceTest.php` picks the declaration up from the stub; add behaviour tests asserting AppKit's own outcome; build, touched tests, smoke per [build](/docs/{{version}}/ecosystem/standalone-extensions/appkit/runbooks/build-install-test).
