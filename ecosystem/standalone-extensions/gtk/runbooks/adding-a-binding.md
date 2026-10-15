# Adding a binding

Stub, gen_stub, one .c per stub, config.m4 source list, guards, ownership, surface test.

## Overview

1. Declare in the stub of the type's header group (`stubs/<Type>.stub.php`, `@generate-class-entries`). Enums from that header in the same stub, values from the header. Doc comment names the C call when the PHP name differs.
2. `php84 /opt/homebrew/opt/php@8.4/lib/php/build/gen_stub.php stubs` → `stubs/<Type>_arginfo.h`. Commit both.
3. New class: `src/<Type>.c` includes its arginfo, defines `phpgtk_register_<Type>()`: `register_class_<Type>(parent ce)`, `phpgtk_object_setup()`, `phpgtk_map_gtype("<GType name>", ce)`. Declare register fn + `phpgtk_ce_<Type>` in `src/runtime.h`, define the ce in `src/gtk.c`, call register in MINIT after its parent. Add the `.c` to `config.m4`.[^runtime]
4. Method body:
   * Parse params; objects via `Z_PARAM_OBJ_OF_CLASS`, native pointer via `PHPGTK_PTR` / `PHPGTK_OPTIONAL_PTR`.
   * `PHPGTK_REQUIRE_MAIN_THREAD()` for GTK entry points; `PHPGTK_REQUIRE_INITIALIZED()` too for widget constructors.
   * Refuse here what GLib would answer with a critical warning (invalid action names, wrong GVariant type, NULL where non-nullable): `zend_argument_value_error`.
   * Return by transfer annotation: `(transfer none)` → `phpgtk_box_gobject` / `phpgtk_box_variant`; `(transfer full)` → `_full` variants. Strings via `phpgtk_return_string`. `GError **` → `phpgtk_throw_gerror`.
   * Callables: `phpgtk_callout_new()` as the GLib user data, with a destroy notify that releases it (`phpgtk_source_destroy` in `src/gtk.c` for sources).
5. Interface methods shared by several classes (GActionMap, GActionGroup on GSimpleActionGroup and GApplication): one body in `INTERNAL_FUNCTION_PARAMETERS` form, declared in `runtime.h`, each `ZEND_METHOD` passes through with `INTERNAL_FUNCTION_PARAM_PASSTHRU`.[^actions]
6. `tests/SurfaceTest.php` picks the declaration up from the stub; add behaviour tests (a fresh process for anything needing GTK uninitialised); build, suite, smoke on Mac and Pi per [build](/docs/{{version}}/ecosystem/standalone-extensions/gtk/runbooks/build-install-test); update [surface](/docs/{{version}}/ecosystem/standalone-extensions/gtk/guide/binding-surface) and README.

[^runtime]: src/runtime.h
[^actions]: src/GAction.c
