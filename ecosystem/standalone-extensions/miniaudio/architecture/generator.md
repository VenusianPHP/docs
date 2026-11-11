# Generator

How tools/extract.php and tools/generate.php turn miniaudio.h into stubs and binding C, and where per-function decisions live.

## Pipeline

`tools/ast.c` includes `miniaudio.h`; clang's JSON AST goes through `extract.php` into `tools/api.json` (structs with fields and nested records, enums, functions with `variadic`, callback typedefs, typedefs; public section only).[^extract] `generate.php` builds the model and writes `stubs/{types,constants,functions}.stub.php`, `src/gen/{types.c,types.h,functions.c,trampolines.h}`. `gen_stub.php` then writes the `*_arginfo.h`. It prints `bound N, pending M`; M must be 0 and no `FIELD` lines may appear.

## Model

Handles: structs that the last parameter of an `_init`/`_alloc` function initializes, plus `ma_data_source_base`, `ma_node_base`, `ma_default_vfs`, `ma_spinlock`, `ma_mutex`, `ma_sound_group`.[^model] Interfaces by first-member chain to `ma_data_source_base` / `ma_node_base` / `ma_vfs_callbacks` / `ma_async_notification_callbacks`. Values: every non-handle struct reachable from signatures and from value fields. Init target: the last parameter of the handle the function name starts with (`ma_sound_group_init` → `pGroup`, not `pParentGroup`).

## Parameter roles

Default: scalar, str/wstr, alloc, handle, target, iface, value_in, value_inout, ref (scalar pointers not named like buffers), userdata (`*UserData`), callable. From `tools/bindings.php`:[^bindings] `out`, `in`, `inout` (PCM/bytes with `size` `[count, unit]` and optional `len`), `heap` (`_init_preallocated`; size from `*_get_heap_size`, private copy kept by the handle), `retain_in` (input kept by a handle: `ma_audio_buffer_ref_init`, `ma_decoder_init_memory`, `register_*_data`), `chmap_in/out`, `list_in/out`, `strout`, `ptrout` (miniaudio-allocated result copied and `ma_free`d). `{name}` in a size is the C value the call passes for that parameter.

## Guards the generator writes

Narrow-int ranges; size overflow (`phpma_mul_size`, capped at `ZSTR_MAX_LEN`); zero-size frame format with a non-zero count; short inputs; a null handle read by a size returns `MA_INVALID_ARGS` (or `ValueError` for non-`ma_result` functions) first. C-variadic functions are refused. Functions matching `BLOCKING` run through `phpma_run_serving` via a generated thunk.[^functions]

[^extract]: clang JSON AST to tools/api.json
[^model]: handles, values, interfaces, defines
[^bindings]: per-function decisions
[^functions]: parameter roles, wrappers, blocking thunks
