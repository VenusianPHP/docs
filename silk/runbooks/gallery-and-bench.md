# Gallery and bench

`examples/gallery.php` shows every widget, working, on every theme; the bench and golden-frames scripts are the gate every drawing change passes. A built widget that is not in the gallery is not done.

## The gallery

One app with a tab for each family of widgets — Controls, Text, Lists and scrolling, Data, Overlays, Pickers, Layout, Pictures, Glass, Docking, Nodes, Blocks, Editor, Timeline — and a Theme dropdown that switches between the built-in [looks](/docs/{{version}}/silk/architecture/looks) while it runs. The Glass tab holds BackgroundBlur panes over a striped, busy backdrop with a blur-radius slider.

Run it as an app: copy `examples/gallery.php` into an app's sketches and `php rocket <name>`. Launching a window is a local matter: it needs the app's session on the event loop, like any [hosted](/docs/{{version}}/silk/guide/hosting) tree.

## bench-gallery

The execution gate: the real gallery, the real `FrameLoop` and `Host`, at scale 2 (900 × 640 points, 1800 × 1280 pixels), on Velvet with the extensions and on Metal offscreen. No window opens. The clock is virtual (each frame 1/60 s later) so springs and timers behave as at 60 fps, and the times are the real cost of each `FrameLoop::frame()`. A scenario runs its input, then frames until three in a row paint nothing — the bench's definition of settled — up to 900.

```bash
php scripts/bench-gallery.php             # both engines
php scripts/bench-gallery.php velvet      # one engine (also: metal, spy)
BENCH_TABS=0 php scripts/bench-gallery.php   # skip every tab's cold frame
```

`spy` records only: the CPU cost of recording a frame, which is all a GPU engine leaves to the CPU. It prints each tab's frames, painted frames, average, p95 and max, then the Nodes tab (pointer pulses, a node drag) with a pass/fail against 16.7 ms, and idle checks.

## bench-timeline

`php scripts/bench-timeline.php`: Timeline paint cost by stage (widget, + lowering through EnginePainter, + Velvet, + Metal) for 5,000 clips with the whole length in view, the same clips in a 20 s view, and 4 items.

## golden-frames

```bash
php scripts/golden-frames.php record [--keep] [filter]
php scripts/golden-frames.php check [filter]
```

Golden frames hold Velvet's pixels byte for byte (sha256 of 134 frames in `tests/Fixtures/golden-frames.json`): Surface's GpuParity scenes, anti-aliased and hard, and the real gallery, every tab settled, in `raven-dark`, `raven-light` and `raven-glass-dark` at scales 1 and 2 (on Velvet with ext-rasterize and ext-fb). The gallery's clock reads are pinned so the frames are deterministic. It is for changes that must not move a pixel; a change that moves pixels on purpose re-records the affected frames. `GOLDEN_SURFACE` points at another Surface checkout for a baseline; `GOLDEN_RAW` is where a failing frame's raw RGBA8 goes.

## Tests

```bash
vendor/bin/pest
```

Hardware-free: a recording `SpyEngine`, `SpyPainter` and `SpyLoop` in `tests/Support`, with the test tree mirroring `src/Silk` — Contracts, Core, Files, Hosts, Looks, Painter, Text, Widgets.

[^bench]: scripts/bench-gallery.php, bench-timeline.php, golden-frames.php; examples/gallery.php.
