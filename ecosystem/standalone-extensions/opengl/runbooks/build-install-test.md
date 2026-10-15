# Build, install, test

install-macos.sh into php84 and zhp, install-debian-trixie.sh on the Pi, then Pest.

## Overview

`bash install-macos.sh` builds in a temp copy for Homebrew php@8.4 (`php84`, NTS) and php@8.4-zts (`zhp`). It installs `opengl.so`, ad-hoc signs it, and writes `30-opengl.ini`. OpenGL.framework is the SDK's. The build defines `GL_SILENCE_DEPRECATION`.[^mac]

`bash install-debian-trixie.sh` builds in the tree with phpize, installs `opengl.so`, and removes the build output. It requires `libegl-dev` and `libgles-dev` (`apt install libegl-dev libgles-dev`). pkg-config must see `egl` 1.5 and `glesv2`. The script prefers the distro pkg-config directory over `/usr/local`.[^pi]

```bash
php84 --ri opengl && zhp --ri opengl
composer install
php84 -d memory_limit=128M vendor/bin/pest
zhp -d memory_limit=128M vendor/bin/pest
rm -rf vendor composer.lock .phpunit.cache
```

Both suites must exit 0. On the Pi, copy the tree (tar without macOS metadata or `._*` files; gen_stub trips on those), run the Debian installer, `composer install`, and `php -d memory_limit=128M vendor/bin/pest`.

## Measured on the Pi (2026-10-04)

Surfaceless EGL (`eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, NULL)`): EGL 1.5, one config with `EGL_OPENGL_ES3_BIT` and `EGL_PBUFFER_BIT`, a 3.1 context made current with no surface, `GL_VERSION` "OpenGL ES 3.1 Mesa 26.2.0-1~bpo13+0~rpt3", `GL_RENDERER` "V3D 7.1.7.0", `GL_MAX_SAMPLES` 4. A framebuffer of a 4× `GL_RGBA8` renderbuffer and a 4× `GL_DEPTH24_STENCIL8` renderbuffer is complete. pkg-config: `egl` 1.5, `glesv2` 3.2.[^measured]

The gate's hypotenuse, pixels `(i, 7 − i)`, is neither solid red nor solid black on CGL or on this V3D.

[^mac]: install-macos.sh
[^pi]: install-debian-trixie.sh
[^measured]: Slice 3 plan, measured before planning
