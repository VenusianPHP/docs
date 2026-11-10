# The Surface contract

What Silk may ask of Surface, and what it must never do. Silk describes what to draw; every per-pixel job belongs to Surface's drivers.

## The contract

* **Silk describes, the drivers draw.** A widget calls the [painter](/docs/{{version}}/silk/architecture/painter) (`rect`, `shadow`, `glass`, `blur`, `line`, `text`, `image`, `layer`, `sketch`, paths, gradients). `EnginePainter` turns those into `RenderingEngine` calls. Silk holds no per-pixel loop: no blur, no distance field, no gradient fill, no image scaling, no glyph rasterising.
* **One engine API.** Silk reaches Surface only through `RenderingEngine` and the framebuffer and window contracts. No engine-specific branch in a widget or the painter, and no `instanceof` on an engine. The same widget [tree](/docs/{{version}}/silk/architecture/tree) draws on Velvet, Metal, OpenGL, Vulkan and SDL3.
* **Velvet CPU work only when Velvet draws.** On a GPU engine the CPU records commands and nothing else. Nothing is built in PHP and uploaded for a GPU engine.
* **Every path in one change.** A drawing feature lands in Velvet, all four GPU engines, the extension (ext-fb, ext-rasterize, ext-imgdec) and the plain-PHP fallback together, and gives one result. The plain-PHP path is the fallback, never the design.
* **A new drawing job is Surface's.** When Silk needs something the engine cannot do (a shape, a filter, a blur), the answer is a Surface verb with its parity tests, not PHP in Silk. `roundRect`, `shadow`, `layer` and `glass` all went that way.
* **No downstream shapes in Surface.** Surface stays module-agnostic: the verbs describe drawing, never Silk's widgets, looks or Raven's names.

## Judging a change

The execution gate is the real [gallery](/docs/{{version}}/silk/runbooks/gallery-and-bench) at scale 2 on Velvet with the extensions and on Metal, with idle frames settling and a scripted theme switch, hover and click settling in a budget. Engines are judged by the visible result, not only by diffs against each other: look at the frame. Engines agreeing with one broken Velvet hid a BackgroundBlur bug once. Every plan states its thread, its driver or engine, its cost per frame, and its cache invalidation.

[^canon]: The execution canon in the Silk repository's AGENTS.md, rules 1 to 5.
