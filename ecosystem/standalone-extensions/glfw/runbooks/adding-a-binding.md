# Adding a binding

Stub, gen_stub, the C file that includes the stub's arginfo and registers its functions, the surface test.

## Overview

1. Declare in `stubs/glfw3.stub.php` (or `glfw3native.stub.php` inside the platform's `#ifdef`). Constants: `@var int` + `@cvalue GLFW_…`. Lists in prose, not `@param list<…>` (gen_stub refuses it).
2. `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs`. Commit the stub and its arginfo.
3. `ZEND_FUNCTION` in `src/glfw3.c` / `src/glfw3native.c`: `GLFW_WINDOW_ARG` / `GLFW_MONITOR_ARG` for handles, `GLFW_INT_ARG` for C ints, `ZEND_TRY_ASSIGN_REF_*` for out-params. A native function gets its prototype declared locally, ABI types only.
4. A new callback: a slot in the `GLFW_CB_*` enum, a trampoline, `GLFW_WINDOW_CALLBACK`, and an unset line in `glfw_unset_native_callbacks`.
5. `tests/SurfaceTest.php` sees the declaration (update its function count); add a behaviour test, asserting `GLFW_FEATURE_UNAVAILABLE` where a platform lacks the feature.
