# Widgets

Creating widgets: the factory methods on a container, the slot every child sits in, setters that invalidate, and the mail a widget posts.

## Factories

Every container carries the `Widgets` trait, so a widget is made where it lives and the factory returns it, setters chaining on:

```php
$root = new Column('window', 6, 16);
$root->label('title', 'Silk on a staged window');
$root->button('press', 'Press me');
$root->checkbox('agree', 'Springs feel right');
$root->toggle('dark', true);
$root->separator('line');
$root->progressBar('load', 0.4);
```

| Factory | Makes | Notes |
|---|---|---|
| `label(name, text)` | Label | markdown; `setWrap()` wraps |
| `button(name, label)` | Button | |
| `checkbox(name, label, checked)` | Checkbox | |
| `radio(name, label, checked)` | Radio | |
| `toggle(name, on)` | Toggle | |
| `progressBar(name, fraction)` | ProgressBar | |
| `separator(name, horizontal)` | Separator | |
| `spacer(name, width, height)` | Spacer | |
| `column(name, spacing, padding)` | Column | children top to bottom |
| `row(name, spacing, padding)` | Row | children left to right |
| `textInput(name, value, placeholder, secret)` | TextInput | |
| `spinBox(name, value, minimum, maximum, step)` | SpinBox | |
| `grid(name, spacing, padding)` | Grid | as `TKGrid` |
| `uniformGrid(name, spacing, columns)` | UniformGrid | 0 columns: square |
| `stack(name)` | Stack | children on top of each other |
| `sizeBox(name, aspectRatio)` | SizeBox | 0: take the space offered |
| `switcher(name, index)` | Switcher | shows the one child |
| `wrapBox(name, spacing)` | WrapBox | |
| `fixed(name)` | Fixed | as `TKFixed`: Raven's Canvas, anchored placement |
| `border(name, padding)` | Border | one child with edges |
| `backgroundBlur(name)` | BackgroundBlur | one child over a blurred view of what is behind it |
| `image(name, file)` | Image | as `TKImage` |
| `sketch(name, draw)` | Sketch | `$draw(RenderingEngine, Rect $deviceRect, float $scale)` |
| `dropdown(name, options, selected)` | Dropdown | |
| `comboBox(name, value, options)` | ComboBox | |
| `slider(name, min, max, value)` | Slider | |
| `scrollView(name)` | ScrollBox | |
| `scrollBar(name, vertical)` | ScrollBar | |
| `split(name, horizontal)` | Splitter | |
| `tabView(name)` | TabView | |
| `expander(name, title, open)` | Expander | |
| `listView(name, items)` | ListView | |
| `table(name, columns, rows)` | Table | as `TKTable` |
| `treeView(name, columns, nodes)` | TreeView | the name `tree` is `Widget::tree()` in Silk |
| `headerBar(name, title)` | HeaderBar | |
| `menuBar(name)` | MenuBar | |
| `tileView(name)` | TileView | |
| `datepicker(name, date)` | DatePicker | as `TKDatepicker` |
| `timePicker(name, hour, minute, second)` | TimePicker | null second shows HH:MM |
| `colorPicker(name, color, alpha)` | ColorPicker | |
| `toast(name)` | Toast | Raven's snackbar, placed by the layout |
| `breadcrumb(name, items)` | Breadcrumb | |
| `pagination(name, count, page)` | Pagination | pages count from 0 |
| `rating(name, value, max)` | Rating | |

## Slots and layouts

A container's children sit in a `Slot(grow, align)`: `grow` is the child's share of the main axis, `align` its place on the cross axis. Layouts live in `Silk\Core/Layout`: Column, Row, Grid, UniformGrid, Stack, Anchored, Border, SizeBox, Spacer, Switcher, WrapBox.

## Setters

A setter stores the value, marks the widget dirty and returns `static`. `invalidateLayout()` measures and arranges again up the ancestor chain; `invalidatePaint()` paints again. A widget may carry a tooltip, a context menu (a [popup](/docs/{{version}}/silk/architecture/overlays)), an appear/disappear [transition](/docs/{{version}}/silk/architecture/motion), a drop callback ([input](/docs/{{version}}/silk/architecture/input)) and its own colour, metric and class overrides, which resolve above the [theme](/docs/{{version}}/silk/architecture/looks).

## Toolkit twins

Where a Silk widget has a Surface `TK*` twin, it takes the twin's creation method, constructor arguments, setter names and mail, so a toolkit-to-Silk swap is mechanical. A widget posts the mail its twin's driver posts — see [mail](/docs/{{version}}/silk/api/mail) and Surface's [view mail](/docs/{{version}}/surface/api/view-mail) — and only ever for user action: a programmatic setter posts nothing.

[^factories]: src/Silk/Widgets/Widgets.php and src/Silk/Widgets/Factories/ (DataWidgets, EditingWidgets, OverlayWidgets).
