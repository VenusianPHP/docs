# Adding a binding

Declare it in the stub, regenerate arginfo, define it in the matching .c, and keep the surface test green.

## Overview

1. Add the function or constant to the stub for its API: `stubs/gl.stub.php` for both platforms, `stubs/CGL.stub.php` on macOS, `stubs/EGL.stub.php` on Linux. Constants use `@cvalue` and the C name. A new handle class is `final`, `@not-serializable`, with a private `__construct`, `pointer()`, and `fromPointer()`.
2. `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs`. Commit the stub and the generated `*_arginfo.h`. Do not hand-edit the header.
3. Define `ZEND_FUNCTION` in the `.c` for that group (`src/gl_state.c`, `src/gl_program.c`, `src/gl_buffer.c`, `src/gl_texture.c`, `src/gl_draw.c`, `src/cgl.c`, `src/egl.c`). A new file is added to `OPENGL_SOURCES` in `config.m4` (`cgl.c` only on darwin, `egl.c` only on Linux). Every `gl*` function starts with `OPENGL_REQUIRE_CONTEXT()`.
4. `src/gl_state.c` includes `stubs/gl_arginfo.h` and is the only file that calls `zend_register_functions` for `gl.stub.php`. Another `.c` that defines more of those functions does not include the header and does not register them again. A new handle's `register_class_*` runs from the `.c` that owns the class, and `opengl_handle_setup` is called on it.
5. `tests/SurfaceTest.php` reads `gl.stub.php` and the platform stub. Add a behaviour test. Build and run the suite per [build](/docs/{{version}}/ecosystem/standalone-extensions/opengl/runbooks/build-install-test).

[^build]: Build runbook
