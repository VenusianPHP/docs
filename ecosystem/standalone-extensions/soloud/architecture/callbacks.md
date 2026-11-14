# Callbacks

How PHP extends SoLoud's abstract classes, and how SoLoud's threads reach PHP without entering it.

## Extendable classes

`AudioSource`, `AudioSourceInstance`, `Filter`, `FilterInstance`, `FFTFilterInstance`, `AudioCollider`, `AudioAttenuator`, `File` and `Thread\PoolTask`. A PHP subclass gets a C++ trampoline as its native: a subclass of the SoLoud class whose virtuals call the PHP methods. `parent::__construct()` builds it; otherwise it is built on first use.

## Threads

* SoLoud's mixer, pool workers and threads from `Thread\createThread()` never enter PHP. The trampoline queues the call to the owner thread (the PHP thread that made the object), raises its VM interrupt and waits. The owner runs it at its next opcode boundary, or from its next ext-soloud call.
* Calls on the owner thread run inline: a `File::read()` during `load()`, a PHP-called `filter()`.
* A mixer call waits at most one device buffer (480 frames, 10.9 ms on a Pi 5), then returns SoLoud's no-op: silence, the buffer unchanged, `0`. The mixer holds the engine's audio mutex, which a PHP callback may need. PHP works on a copy of the buffer, so a late result is dropped.
* A thread blocked in `usleep()` or `sleep()` runs no opcodes and serves nothing: run PHP while sound plays.
* Thread functions and pool tasks hold no SoLoud lock; they wait until PHP has run them or the owner's request ends. `Thread\wait()` and pool destruction serve the queue while they block.

## Results

* An override's return is checked against the virtual's type: `TypeError` otherwise. `createInstance()` must return a fresh PHP instance of the matching base.
* An exception thrown in an override is rethrown on the owner thread; the failed call returns its no-op and the voice keeps playing silence.
