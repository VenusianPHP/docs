# Lifetime

How ext-soloud keeps the objects SoLoud points at alive, and why no order of `unset()` or request shutdown crashes the process.

## Identity

One PHP object per native address. PHP deletes the C++ objects it constructs. A native SoLoud owns (an instance, an object reached through a field) is wrapped borrowed, with its owner kept alive.

## Holds

SoLoud keeps raw pointers between objects. The holder keeps the held PHP object alive:

| Native pointer | Kept alive by |
|----------------|---------------|
| source → engine (`Soloud::play*`, `Bus::play*`) | the source |
| slot → filter (`setFilter`, `setGlobalFilter`) | the source or engine; resetting the slot does not release it, since a voice may still run its instance |
| queue → source (`Queue::play`) | the queue |
| source → collider, attenuator, file | the source; a replaced one stays held until the source goes, since voices copy the pointer at play |
| `loadMem` bytes, neither flag set | the source, until its next load |

## Free order

Request shutdown frees objects in its own order, so each object makes its own deletion safe first:

* A source leaves every queue that holds it; its destructor stops its voices.
* A filter leaves every slot that holds it.
* An engine's destructor deinitialises it, joining the mixer thread; then every source pointing at it is cleared.
* A `Thread\Pool` is destroyed while serving the owner's queue, since its workers may wait on a PHP task.
* A PHP subclass's trampoline is deleted as its own type; calls still queued for it become no-ops.

The test suite runs every order with everything live at exit.
