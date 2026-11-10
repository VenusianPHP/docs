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

## Pages

| Page | Holds |
|---|---|
| Creating widgets: factories, slots, setters, mail | [widgets](/docs/{{version}}/silk/guide/widgets) |
| A tree in a window: the two hosts, the loop | [hosting](/docs/{{version}}/silk/guide/hosting) |
| The object model: measure, arrange, paint, handle | [the tree](/docs/{{version}}/silk/architecture/tree) |
| CanvasHost, StagedHost, FrameLoop, FramePump | [hosts and the frame loop](/docs/{{version}}/silk/architecture/hosts) |
| SilkEvent, routing, focus, drag and drop | [input](/docs/{{version}}/silk/architecture/input) |
| Popups, tooltips, dialogs and toasts | [overlays](/docs/{{version}}/silk/architecture/overlays) |
| Springs, transitions, theme blending | [motion](/docs/{{version}}/silk/architecture/motion) |
| The 12 themes, tokens, accent, glass | [looks](/docs/{{version}}/silk/architecture/looks) |
| Logical units to engine calls, culling, glass | [painter](/docs/{{version}}/silk/architecture/painter) |
| The BlockEditor's model, rules and interaction | [blocks](/docs/{{version}}/silk/architecture/blocks) |
| What Silk may ask of Surface, and never does | [the Surface contract](/docs/{{version}}/silk/architecture/surface-contract) |
| The mail the widgets post | [mail](/docs/{{version}}/silk/api/mail) |
| `config/silk.php` | [config](/docs/{{version}}/silk/api/config) |
| The gallery, the bench, golden frames | [gallery and bench](/docs/{{version}}/silk/runbooks/gallery-and-bench) |

## Usage

Silk owns a whole staged window, or lives inside a canvas beside the native widgets of a toolkit window — the same tree on either host, and an idle tree costs nothing. Start with [widgets](/docs/{{version}}/silk/guide/widgets) and [hosting](/docs/{{version}}/silk/guide/hosting), or with [composing an app](/docs/{{version}}/surface/runbooks/composing-an-app) for the window underneath; the [gallery](/docs/{{version}}/silk/runbooks/gallery-and-bench) shows every widget, working, on every built-in theme.
