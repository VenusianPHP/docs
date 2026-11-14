# Overview

The metal rendering engine for Venusian Surface.

The `metal` rendering engine for Venusian Surface. Metal through ext-metal.

## Where it sits

```
DrawingManager → GpuRenderingEngine (Surface) → MetalDevice (this package) → ext-metal → Metal
```

The engine's framebuffer is a `MetalFramebuffer`, a Surface `GLFramebuffer`.

## Requirements

- macOS on Apple silicon. Engine blends by reading the target in its fragment functions; an Intel GPU refuses the pipelines with a `DrawingException` naming it.
- PHP `~8.4.27||^8.5.12` (8.4.27 or newer, 8.5.12 or newer), ext-metal ^0.11, ext-appkit ^0.11, ext-fb ^0.11.1, `venusian-surface/drawing` ^0.11. ext-appkit is required now (it gives the colour spaces for HDR and Display P3 targets and the event cycle presented times arrive through).

## Install

```
composer require jovian/venusian-metal
```

Provider discovered through `extra.venusian.providers`. It registers `metal` on `app('drawing')`.

## Usage

Offscreen. Run as a script; printed pixels are its output.

```php
use Surface\Contracts\Drawing\RenderingEngine;
use Surface\Contracts\Framebuffers\FormatSpec;
use Surface\NutsAndBolts\Color;

$engine = app('drawing')->renderer('metal', ['width' => 320, 'height' => 240]);
$engine->frame(fn (RenderingEngine $g) => $g->clear(Color::rgb(16, 24, 32))->fillEllipse(160, 120, 60, 40, Color::rgb(255, 128, 0)));
$rgba = $engine->framebuffer()->flush(FormatSpec::rgba8());

echo bin2hex(substr($rgba, (120 * 320 + 160) * 4, 4)), "\n";   // ff8000ff  ellipse centre
echo bin2hex(substr($rgba, 0, 4)), "\n";                       // 101820ff  corner
```

On a display. The display sends what changed, in its own format.

```php
$display = app('displays')->panel('st7796');
$engine = app('drawing')->renderer('metal', ['output' => $display]);
```

On a canvas.

```php
$engine = app('drawing')->renderer('metal', ['output' => $canvas]);
```

Needs a toolkit canvas that lends a Metal layer. A window that lends none refuses: `This window cannot host 'metal': it lends … It can host: …`.

## Presenting and HDR

Present = show pass: target any size → window's `presentRect()`, window's filter, black bars, encoded for layer. Follows window vsync (on syncs display; off/mailbox don't). `frames_in_flight` 1-3. `presents()` = when frames hit screen (AppKit event cycle delivers times; `waitPresented()` pumps it). Minimised/hidden window never stalls a present (measured: 20 vsynced presents in 209 ms).

HDR on EDR displays (needs ext-appkit):

    $engine = $drawing->engine('metal', ['output' => $window, 'format' => TargetFormat::Rgba16Float]);
    $engine->frame(fn ($g) => $g->image(HdrImage::fromFloats($rgba, $w, $h), 0, 0));

Target = linear half floats, SDR white 1.0. Pairs: rgba16float extended-linear sRGB / P3 (EDR, × window SDR white), rgb10a2 HDR10 (PQ, BT.2020, HDR10 metadata), rgba8 Display P3.

## What it draws

| Operation | Draws |
|---|---|
| CLEAR | the colour over the whole target, no blend |
| SCISSOR | clip rectangle for what follows |
| SOLID | flat-colour triangles, no blend |
| STENCIL_FILL + COVER | a path: triangle lists into the stencil (winding or even-odd), then a cover quad blended where the stencil is non-zero and zeroed |
| ELLIPSE, RING | per-sample inside tests of the outer (and inner) ellipse |
| UPLOAD + IMAGE | a framebuffer as a texture; sampled at the inverse placement of the pixel centre, nearest or Velvet's 256ths bilinear |
| RECTS | rectangles blended at the colour's alpha |
| ROUNDRECT, ROUNDRING | a rounded box, or its border inside the box, as one quad a pixel past it; coverage per sample inside the rounded box (and outside the box inset by the border) |
| SHADOW | a blurred rounded box: one quad blur + 1 past it, coverage `1 − smoothstep(−blur, blur, d)` at each pixel centre |
| ATLAS + MASK + GLYPHS | TrueType text: each glyph's coverage written once into an 8-bit atlas texture kept across frames, then quads sampling it, blended as Velvet blends spans |
| COVER_GRADIENT | a linear or radial gradient: the path's stencil, then a cover that looks the pixel's position up in the 256-entry ramp, uploaded as a 256 × 1 source |
| TARGET, BACKDROP, FILTER, LAYER_SOURCE | layers: a target of the layer's own, a copy of what lies under it, Surface's `FilterPlan` passes over the box, and the layer target as an image's source |
| GLASS_BACKDROP + GLASS | glass panes: the region under a group of panes read once and taken down and up a dual-filter pyramid (kept across frames while nothing under it changes), then one draw a pane |

Edges: four samples resolved (anti-aliased) or one (hard). Blending: Velvet's integer source-over per sample, so interior pixels match Velvet byte for byte (the parity suite's rule).

## Reference

- `MetalDevice`: `__construct(?MTLDevice)`, `metal()`, `target()`, `draw()`, `surfaces()`, `handles()`, `adopt()`, `present()`, `release()`, `read()`, `write()`, `finish()`.
- `MetalFramebuffer`: `texture()`, the `GLFramebuffer` methods.
- `VenusianMetalServiceProvider::extend(DrawingManager)`.

## Behaviour

- Readback waits for the frame.
- The vertex buffer is made for each frame: ext-metal's `MTLBuffer` has no way to be written in place, so there is no ring. Uploaded image sources and gradient ramps use shared textures pooled by size (8 a size, 24 sizes), taken by a frame and given back once its command buffer completes.
- A pixel call between frames costs a readback and an upload and, with anti-aliased edges, a restore pass.
- `present()` skips the copy while the previous one is in flight, answering false.
- The engine's own framebuffer as an image source shows the frame before the current one.
- A re-made target is a new `MetalFramebuffer`; the old one keeps its own texture.
- A layer with no view hands out drawables; the copy is proven there.

## Measured

Apple M1 Pro, 320 × 240, 100 ellipses and a line of text, anti-aliased: whole redraw 1.25 ms a frame, partial frames 4.57 ms, peak memory 4.0 MB. (Velvet, both extensions, same scene shape: 6.8 ms.)

## Testing

Real GPU only; nothing skipped. `tests/Pest.php` requires Surface's `GpuParity` from the sibling checkout; set `SURFACE_TESTS` to a Surface checkout's `tests` directory to move it. Install with a temporary path repository to `<surface>/src/Surface/*`, run `php -d memory_limit=128M vendor/bin/pest` on `php84` and ZTS. Runbook: [.okf/runbooks/testing.md](/docs/{{version}}/ecosystem/framework-surface-modules/venusian-metal/runbooks/testing).

## Security

See [SECURITY.md](https://github.com/jovian-packages/venusian-metal/blob/HEAD/SECURITY.md).

## License

MIT.
