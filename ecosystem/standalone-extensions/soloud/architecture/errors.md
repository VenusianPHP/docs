# Errors

What ext-soloud returns, what it throws, and the calls it refuses.

## Results pass through

SoLoud reports errors as `result` codes; they are returned, never thrown. `Soloud::getErrorString()` names them. Marshalling throws `TypeError` / `ValueError`: an integer out of range for its C++ type, a second `__construct()`, a bad override return.

## Refusals

The extension declines a call only where SoLoud would read or write memory it does not own, kill the process, or run PHP on a non-PHP thread. Each refusal has a probe test that runs the call with the check off on a probe build and shows the crash. Refusals throw `ValueError`; the FFT helpers before their state exists throw `SoLoudException`.

| Refused | Crash it prevents |
|---------|-------------------|
| a length past the PHP string (`loadMem`, `loadRawWave*`, `loadParamsMem`, `openMem`) | read past the string |
| `Soloud::mix()` / `mixSigned16()` past the engine's scratch, or before `init()` | heap overflow |
| `Soloud::play*()` before an `init()` succeeded | stopping the voice later (`stop()`, shutdown) reads state only a successful `init()` allocates |
| a filter instance with more channels than its state, a channel past the count, an FFT instance with no parent | write past the state |
| an FFT helper before `filterChannel()` allocated its state, past its channels or 256 samples | NULL or past-the-end read |
| `FilterInstance::initParams()` below the instance's count, or above 256 | read past the parameters; abort |
| a `LofiFilter` on more than 2 channels (play, `setGlobalFilter`, `init`); `init()` with more channels than a global filter's state | the mixer writes past the filter state |
| reading or loading through a `File` that is not open | NULL `FILE *`, read past a `MemoryFile` |
| a mutex or thread handle not live, already joined or released | freed memory |
| `Thread\Pool::addWork(null)` | NULL call |

Not refused: writing a field SoLoud uses as state, as in C++.
