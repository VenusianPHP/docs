# Overview

Venusian Silk (`venusian/silk`, 0.11.x) is the Venusian widget toolkit: self-drawn, springy widgets for Venusian Surface. A widget holds its own state, lays itself out, paints itself through any Surface rendering engine and takes raw input, posting mail to the Venusian event loop — where a Surface `TKButton` stores state and lets the toolkit draw it, a Silk `Button` stores the same state and draws itself. The look and the motion are [Raven](https://github.com/oscar-soirey/Raven)'s — near-native, prettier, springy; Raven is the reference, not a dependency.

## Requirements

- PHP 8.4.27+ or 8.5.12+.
- `venusian-surface/*` 0.11 (contracts, drawing, fonts, framebuffers, human-input, images, nuts-and-bolts, windows) and `venusian-voyager/*` 0.11 (contracts, io-pools, nuts-and-bolts).
- No extension of its own: Velvet, Surface's software engine, draws out of the box, and ext-fb, ext-rasterize and ext-imgdec speed Velvet when it draws. See [drawing](/docs/{{version}}/surface/architecture/drawing).

## Install

```bash
composer require venusian/silk
php computer vendor:publish --tag=silk-config
```

`Silk\Core\Providers\SilkServiceProvider` is discovered through `extra.venusian.providers` and binds the `silk` singleton, `silk.looks` (the LookManager) and `silk.translator`.

## The set

Every Raven widget type:

| Kind | Widgets |
|---|---|
| Panels | Column, Row, Grid, UniformGrid, Stack, Fixed, SizeBox, Switcher, WrapBox, Border, ScrollBox, Splitter, Expander, TabView, DockArea, Island |
| Controls | Label, Button, Checkbox, Radio, Toggle, TextInput, Slider, SpinBox, ProgressBar, ScrollBar, Separator, Image, Rating, Pagination, Breadcrumb |
| Choosing | ComboBox, Dropdown, DropdownList, Menu, MenuBar, MenuItem, DatePicker, TimePicker, Calendar, ColorPicker |
| Data | ListView, TreeView, Table, TileView, FileBrowser, Timeline, NodeGraph |
| Programs | BlockEditor: Scratch-style blocks that snap into each other |
| Text | TextEditor (multi-line, syntax colours), Label markdown |
| Overlay widgets | Dialog, MessageBox, Toast and ToastQueue |
| Window | HeaderBar |
| Surfaces | BackgroundBlur, Sketch |

Widgets are made through factory methods on containers — `$column->button('save', 'Save')` — and where a widget has a Surface `TK*` twin it keeps the twin's creation methods, setter names and mail, so moving a window from [toolkit primitives](/docs/{{version}}/surface/architecture/toolkit-primitives) to Silk is mechanical.

## Config

| Key | Holds |
|---|---|
| `look` | the look every tree starts with (`raven-dark`) |
| `accent` | `auto`, `system`, `theme` or `custom`; `accent_color` when custom |
| `scale` | UI scale, 0.25..4, multiplied by the window scale |
| `reduced_motion` | snap every spring to its target |
| `font.family` / `font.mono` | fontconfig families for the UI and monospace text |

There is no engine key: Surface's `drawing.default` picks the engine, and `SILK_ENGINE` overrides it for one run. Twelve themes ship built in — `raven-dark` through macOS, GNOME and glass — and `app('silk.looks')` switches the active one live.

## Usage

Silk owns a whole staged window (`StagedHost`), or lives inside a canvas beside the native widgets of a toolkit window (`CanvasHost`): the same tree on either host, and an idle tree costs nothing. Every animated value is a damped spring solved in closed form, so hover, popups and scrolling move the same at any frame rate. The [gallery](https://github.com/VenusianPHP/silk/blob/main/examples/gallery.php) — every widget, working, on every built-in theme — is in the Silk repository; start with [composing an app](/docs/{{version}}/surface/runbooks/composing-an-app) for the window underneath.
