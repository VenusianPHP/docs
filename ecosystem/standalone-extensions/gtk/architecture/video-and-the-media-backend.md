# Video and the media backend

GtkVideo over GtkMediaFile; GTK loads a media backend module (GStreamer on Debian, none in Homebrew gtk4); the probe, the installers, and what runs where.

## Overview

`GtkMediaFile::newForFilename(path)` asks GTK for its media-file implementation: GTK loads the module under `lib/gtk-4.0/4.0.0/media` on first use and instantiates its subclass (`GtkGstMediaFile` with `libgtk-4-media-gstreamer`); without a module it instantiates `GtkNoMediaFile`, which reports an error and plays nothing. Both box as `GtkMediaFile`. `GtkVideo::new()` + `setMediaStream` shows it; `play`/`pause`, `seek` (µs), `duration`, `ended`, `loop`, `muted`, `has_video` are the stream's. `get_error()` returns the stream's GError as a `GError` object without throwing: a missing file, or no backend.[^video]

Probe: `gtk_media_backend_available()` builds a `gtk_media_file_new()` and answers whether its type is not `GtkNoMediaFile`. Both the probe and `newForFilename` need GTK initialised: `gtk_init` registers the `gtk-media-file` extension point, and the lookup traps before that, so the binding refuses with `GtkException` first.

Platforms: Debian trixie / Raspberry Pi OS ship the backend as `libgtk-4-media-gstreamer` (plus `gstreamer1.0-plugins-good`/`-bad` for H.264 in MP4); `install-debian-trixie.sh` dies without it.[^debian] Homebrew's gtk4 has no `media` directory: `install-macos.sh` warns, the probe answers false, `GtkVideo` shows nothing, and the playback test skips.[^macos] The suite's clip (`tests/fixtures/clip.mp4`) is a 1.2 s 160×120 H.264 test pattern.

[^video]: GtkMediaStream, GtkMediaFile, GtkVideo, probe
[^debian]: Debian installer
[^macos]: macOS installer
