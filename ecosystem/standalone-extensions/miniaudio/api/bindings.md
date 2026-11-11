# Bindings

What ext-miniaudio binds from miniaudio 0.11.26, what it does not and why, and how each C shape becomes PHP.

## Counts

931 `MA_API` declarations in the public section (above `MINIAUDIO_IMPLEMENTATION`).[^api] 924 bound: 891 generated, 33 hand-written (`stubs/manual.stub.php`). 193 classes (value structs, anonymous sub-structs, handles, `ma_vfs_file`, the four proc classes), 4 interfaces, 391 constants (every enum constant plus the public `#define`s).[^stubs] `CoverageTest` fails if a function is missing or extra.

## Not bound

* `ma_malloc`, `ma_calloc`, `ma_realloc`, `ma_free`, `ma_aligned_malloc`, `ma_aligned_free`: raw memory has no PHP meaning; buffers cross as strings.
* `ma_log_postv`: a C `va_list` cannot be built from PHP. `ma_log_postf` is bound and formats with PHP's `sprintf`.
* `static inline` helpers in the header (`ma_get_bytes_per_frame` …) are not `MA_API` and not exported.
* `ma_allocation_callbacks`: the class exists so signatures stay 1:1; only null (all fields null) is accepted.

## Translations

* Value struct → final class, typed property per field in order, constructor with every field optional, nested structs as fresh instances. Anonymous sub-struct → class `<outer>_<field>`. Union → one property per member; written back member by member, zero-valued members skipped; `ma_job.data` writes only the member `toc.breakup.code` names.
* Handle (has `_init`) → final class holding the C struct; see [handles](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/architecture/handles-and-ownership).
* `void` typedefs `ma_data_source`, `ma_node`, `ma_vfs`, `ma_async_notification` → interfaces. Returned pointers into miniaudio's memory come back as borrowed `ma_data_source_base` / `ma_node_base` views.
* Scalars: integers and enums `int` (narrow ones range-checked), `ma_bool*` `bool`, `float`/`double` `float`. `ma_uint64` is the same 64 bits.
* `T*` scalar out/in-out → by-reference. `const V*` → `?V`. `V*` → `?V` written back in place. `const char*` → `?string`; `const wchar_t*` → `?string` (UTF-8). Channel maps, `ma_uint32` lists, backend lists → arrays. `float**` weight matrices → array of rows.
* PCM and bytes → strings sized by the roles in `tools/bindings.php`; see [generator](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/architecture/generator).
* Callbacks → callables / `?Closure` properties; `void*` user data → `mixed`; see [callbacks](/docs/{{version}}/ecosystem/standalone-extensions/miniaudio/architecture/callbacks).
* Pointers inside resource-manager jobs → `int`, accepted back only if miniaudio handed them out in this request.

[^api]: every public struct, enum, function and callback typedef, from clang's AST
[^stubs]: types, constants, functions (generated), manual and backends (hand-written)
