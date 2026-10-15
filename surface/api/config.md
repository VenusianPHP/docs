# Config

config/bridge.php, config/windows.php, config/framebuffers.php, config/rasterize.php, config/images.php, config/drawing.php, config/embedded-displays.php and config/human-input.php keys.

## Schema

`bridge`:[^bridge]

| Key | Default | Values |
|---|---|---|
| `toolkit.mac.default` | `appkit` | `appkit`, `gtk`, `qt` |
| `toolkit.linux.default` | `gtk` | `gtk`, `qt` |
| `stage.mac.default` | `appkit` | stager for `staged-windows`: `appkit`, `sdl3`, `glfw` |
| `stage.linux.default` | `sdl3` | `sdl3`, `glfw` |

Driver keys, read with code defaults by each driver (absent from the published file): `bridge.gtk.application_id`, `bridge.gtk.unique`, `bridge.qt.application_name`, `bridge.qt.desktop_file_name`. See each jovian driver bundle.

`windows`:[^windows]

| Key | Default | Meaning |
|---|---|---|
| `about.name` | `env('APP_NAME', 'Venusian')` | About title |
| `about.version` | `env('APP_VERSION')` | About version line |
| `about.copyright` | `null` | About copyright line |
| `default_menu` | `main` | profile for the macOS default bar; `null` = empty bar |
| `menus` | `main` profile | [menu profiles](/docs/{{version}}/surface/api/menu-profiles) |

`framebuffers`:[^framebuffers]

| Key | Default | Values |
|---|---|---|
| `default` | `env('FRAMEBUFFERS_DRIVER', 'auto')` | `auto` (extended when ext-fb 0.10 is loaded, native when not), `native` (bytes in PHP, always available), `extended` (bytes in C, needs ext-fb 0.10) |

`rasterize`:[^rasterize]

| Key | Default | Values |
|---|---|---|
| `default` | `env('RASTERIZE_DRIVER', 'auto')` | `auto` (extended when ext-rasterize is loaded, native when not), `native` (geometry in PHP, always available), `extended` (geometry in C, needs ext-rasterize 0.10) |

`images`:[^images]

| Key | Default | Values |
|---|---|---|
| `default` | `env('IMAGES_DRIVER', 'auto')` | `auto` (extended when ext-imgdec is loaded, native when not), `native` (PNG/JPEG through ext-gd, TIFF in PHP), `extended` (all three in C, needs ext-imgdec 0.10) |
| `framebuffers` | `null` | framebuffer driver decoded images live on; `null` = `framebuffers.default` |

`drawing`:[^drawing]

| Key | Default | Values |
|---|---|---|
| `default` | `velvet` | the engine `renderer()` builds when none is named: `velvet` (software, built in), or one an engine package registers |

`embedded-displays`:[^embedded-displays]

| Key | Default | Values |
|---|---|---|
| `defaults.refreshing` | `epaper` | framebuffer kind for a panel that refreshes on command |
| `defaults.addressable` | `dirty` | for a panel that takes region writes |
| `defaults.whole` | `full` | for a panel that takes whole frames only |

`human-input`:[^human-input]

| Key | Default | Values |
|---|---|---|
| `pads.mac` | `gamecontroller` | pad source a package registered with `extendPads()`: `gamecontroller`, `sdl3`; `null` = circuits only |
| `pads.linux` | `evdev` | `evdev`, `sdl3`; `null` = circuits only |
| `joysticks` | `[]` | generic joysticks by reported name: `axes`, `buttons` index maps onto `GamepadAxis` / `GamepadButton` names, `hat`; unlisted joysticks use the default map (axes 0/1 left stick, 2/3 right stick, 4/5 triggers; buttons 0-3 south/east/west/north, 4/5 shoulders, 6/7 back/start; hat 0 the dpad) |

Frame length comes from `sketches.refresh_rate` (default 60), not this file.

[^bridge]: config/bridge.php
[^windows]: config/windows.php
[^framebuffers]: config/framebuffers.php
[^rasterize]: config/rasterize.php
[^images]: config/images.php
[^drawing]: config/drawing.php
[^embedded-displays]: config/embedded-displays.php
[^human-input]: config/human-input.php
