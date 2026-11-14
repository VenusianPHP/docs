# Bindings

What ext-soloud binds from SoLoud's C++ API at commit `e82fd32`, what it does not and why, and how each C++ shape becomes PHP.

## Counts

75 classes, their public constructors, methods and fields, and the `SoLoud::FFT`, `SoLoud::Misc` and `SoLoud::Thread` free functions: 789 members, all bound. [SUPPORT.md](https://github.com/php-io-extensions/soloud/blob/HEAD/SUPPORT.md) lists each one; `scripts/support.php --check` fails if one goes missing.

## Not bound

* `soloud_c.h`: the flat C mirror SoLoud generates from this API.
* Methods SoLoud names `*_internal`: its mixer's own entry points.
* `DiskFile(FILE *)`: PHP cannot make a valid `FILE *`, and two `DiskFile`s sharing one would both close it. `DiskFile::open()` is bound.
* SoLoud's private third-party code (dr_wav, dr_mp3, dr_flac, stb_vorbis, its miniaudio copy) and backends other than miniaudio and null.

## Translations

* `SoLoud::X` → `SoLoud\X`; nested scopes are namespaces (`SoLoud\Thread\Pool`, `SoLoud\Misc\Prg`); free functions are namespace functions.
* Enumerators → `int` constants: class enums on their class, namespace enums in the namespace. SoLoud's enums are unscoped and its methods take `unsigned int`, so they are not PHP enums.
* `result`, `handle` → `int`; `time` → `float`. Unsigned and narrow integers are range-checked (`ValueError`).
* Overloads: the one the native name keeps, with SoLoud's defaults.
* Abstract classes → PHP abstract classes; the extendable ones are listed under [Callbacks](/docs/{{version}}/ecosystem/standalone-extensions/soloud/architecture/callbacks). A struct with no constructor gets an aggregate one, one optional parameter per scalar field.
* Public fields → typed properties read and written live, as in C++. A field SoLoud uses as state (`mChannels`) set against the data makes the mixer read past it, as in C++.
* Bytes → `string`. Samples → packed float (`pack('g*')`) or packed int16 strings. In-out buffers (`Soloud::mix()`, `FFT\fft()`, `FilterInstance::filter()`) → by-reference strings the binding sizes from the call's own counts and writes back.
* `loadMem` ownership follows SoLoud's flags; with neither `aCopy` nor `aTakeOwnership`, the object keeps the PHP string until its next load or its free.
* `FILE *`, mutex and thread handles → `int` addresses. Mutex and thread handles are tracked while live.
* Openmpt loads `libopenmpt` at runtime; on macOS it always fails, as upstream calls `dlopen("libopenmpt.so")`.
