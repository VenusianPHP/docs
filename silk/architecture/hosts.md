# Hosts and the frame loop

CanvasHost and StagedHost bind a tree to an engine and a window; `FrameLoop` runs one frame; `FramePump` joins the Venusian loop. An idle tree costs nothing.

## One frame

`FrameLoop::frame(Host)`, in order:[^loop]

1. Drain the host's queued [SilkEvents](/docs/{{version}}/silk/architecture/input) and dispatch each through the host's Router.
2. Step the [springs](/docs/{{version}}/silk/architecture/motion): `FrameClock` turns the real gap since the last frame (bounded to 0.001..0.25 s) into equal steps of at most 1/30 s, and `Tree::advance()` takes each.
3. Lay the [tree](/docs/{{version}}/silk/architecture/tree) out to the host's viewport (up to 4 measure/arrange passes while something re-dirties).
4. If nothing needs paint and nothing wants paint (`Tree::wantsPaint()`: a full repaint or leftover damage), return: no layout work beyond the check, no paint, no present, and the clock is forgotten.
5. Otherwise, inside `engine->frame()`, `Tree::paintAll(new EnginePainter(...))`: the [painter](/docs/{{version}}/silk/architecture/painter) records only the dirty region, and the engine's own damage diffing limits the pixels touched. Then `host->present()`.

## The hosts

* **CanvasHost** wraps a `TKCanvas`: it watches the pointer, keys and size, converts points to pixels with the canvas scale, and draws through any engine made for the canvas as its output. An engine that draws into the canvas's own framebuffer is made anew when the canvas resizes; a GPU engine on the view's lent layer follows the size itself in `begin()`, and a GPU engine borrowing the canvas is never remade on resize. The canvas presents either. [Overlays](/docs/{{version}}/silk/architecture/overlays) stay inside the canvas. Native and Silk widgets sit side by side in one toolkit window.[^canvas]
* **StagedHost** owns a staged window and the input mail its stager posts while it watches input; the stager's session must have joined the event loop or nothing pumps it.[^staged]
* `Host::bind(engine, pointsW, pointsH, pixelScale)` hands a host its engine and size — the bench binds one by hand, with no window.

## The pump

`FramePump` is the Silk resource on the Venusian loop: it joins when `event-loop` resolves and runs one frame per attached host per tick. `app('silk')->attach(host)` / `detach(host)` hold the live hosts.

Surface's `drawing.default` picks the engine (Velvet unless the app says otherwise); `SILK_ENGINE` overrides it for one run. Nothing picks a GPU engine automatically. Idle frames settle — three in a row painting nothing is the [bench](/docs/{{version}}/silk/runbooks/gallery-and-bench)'s definition of settled.

[^loop]: src/Silk/Hosts/FrameLoop.php, FrameClock.php.
[^canvas]: Class docblock of CanvasHost.
[^staged]: Class docblock of StagedHost.
