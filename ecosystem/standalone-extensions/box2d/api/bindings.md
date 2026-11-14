# Bindings

Every function, class and constant ext-box2d binds, by Box2D header, and the only translations from C.

## Counts

base.h 7, id.h 10, math_functions.h 73, collision.h 72, types.h 17, box2d.h 313, values/macros 13 = 505 functions. 70 struct classes + `b2DynamicTree` handle + `b2AssertionError`. One stub per header.[^stubs]

## Translations (only these)

- Struct → `final class`, typed property per field, field order, ctor = C aggregate init (zero defaults, fresh nested). Ids are structs.
- Fixed C array → list (output holds `count` entries; `colorCounts`, `indexA`, `indexB` full). Struct pointer lists → list props, count props kept.
- `const T*` in → object. Scalar out → by-ref. In/out struct → updated in place. Input array+count → `array, int`. Output array+capacity → `?array &$list, int $capacity`, returns count.
- `uint8_t* data, int count` → `string, int`. `uint64_t` → int, same bits.
- Narrow ints range-checked → `ValueError`.
- Callback + `void* context` → `callable` + `mixed $context` unchanged. Callback fields → `?Closure`.
- Static consts → same-name functions returning fresh instances.
- `b2DynamicTree` opaque; destroyed on free unless `b2DynamicTree_Destroy` ran; use after destroy → `ValueError`.

Callback signatures: the stubs.[^stubs]

[^stubs]: base, id, math_functions, collision, types, box2d stubs
