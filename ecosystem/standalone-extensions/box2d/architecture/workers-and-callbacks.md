# Workers and callbacks

Per-world pthread pool behind Box2D's task callbacks, the queue that runs PHP callbacks on the stepping thread, fork and request-end rules.

## Pool

`workerCount <= 1` → NULL task callbacks, serial step. `> 1` → `b2CreateWorld` starts `min(workerCount, 64)` pthreads; thread i = worker index i for life (Box2D scratch never shared). `b2DestroyWorld` stops + joins.[^tasks]

`enqueueTask`: `[0, itemCount)` split into `min(workers, max(1, itemCount/minRange))` ranges, each ≥ minRange unless itemCount < minRange; FIFO; never inline, never NULL. Solver's workerCount spin-waiting single-item tasks all run at once: FIFO + one thread per index, no deadlock.

`finishTask`: stepping thread waits on the world's cv until the handle's count is 0, serving the callback queue meanwhile.

## Callbacks across threads

Pool threads never enter PHP. Friction, restitution, custom filter, pre-solve on a pool thread → request (kind + C args) queued, stepping thread runs the callable inside `finishTask`, writes result (and edited `b2Manifold`) back, wakes the pool thread. On the stepping thread itself → called directly.[^events] Friction/restitution have no C context: pool threads hold a TLS world pointer; stepping thread sets one for the step (saved/restored).

Results bit-identical for workerCount 0, 4, 65 (200 bodies × 120 steps).[^tests]

## Fork, request end, ZTS

`pthread_atfork` child marks pools dead → stepping a pooled world in the child is `Error("world's worker pool did not survive fork")`; serial worlds fine; child exits clean. RSHUTDOWN stops every pool and destroys every world the request left (128-slot process table would fill in a long-lived SAPI); proven by 20 built-in-server requests × 8 pooled worlds with a flat thread count. ZTS: create/destroy under a process mutex.

[^tasks]: pool, enqueue/finish, callback queue, atfork
[^events]: callback dispatch and trampolines
[^tests]: WorkersTest and LifecycleTest
