# Video

QMediaPlayer + QAudioOutput + QVideoWidget over the platform media backend; status and error flow as signals; the build needs Qt Multimedia.

## Overview

Pipeline, as in Qt: `$player = new QMediaPlayer(); $player->setAudioOutput(new QAudioOutput()); $player->setVideoOutput($videoWidget); $player->setSource(QUrl::fromLocalFile($path)); $player->play();`. Without an audio output Qt plays video silently; `setMuted(true)` or `setVolume(0.0)` keep the suite quiet.[^source]

State arrives through signals, enums as ints ([signals](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/signals)):

| Signal | Meaning |
|---|---|
| `mediaStatusChanged(QMediaPlayer::MediaStatus)` | `LOADING → LOADED → BUFFERED → END_OF_MEDIA` on a clip that plays through; `INVALID_MEDIA` for a file the backend cannot open |
| `playbackStateChanged(QMediaPlayer::PlaybackState)` | `PLAYING`, `PAUSED`, `STOPPED` (also at end of media when not looping) |
| `errorOccurred(QMediaPlayer::Error,QString)` | the `Error` value and `errorString()`; a missing local file is `RESOURCE_ERROR` |
| `positionChanged(qint64)` | milliseconds |

Reads: `position()`, `duration()` (ms; duration is known once `LOADED`), `playbackState()`, `mediaStatus()`, `hasVideo()`, `errorString()`, `source()`. `isAvailable()` is false when no media backend plugin loaded; such a player accepts every call and plays nothing, so it is the check to make before relying on playback. `setLoops(QMediaPlayer::INFINITE_LOOPS)` loops until `stop()`.[^source]

Build: `config.m4` requires `Qt6Multimedia >= 6.4 Qt6MultimediaWidgets >= 6.4` beside Widgets/Gui/Core. Both installers refuse to build without the modules and without a backend plugin in `$(qtpaths6 --query QT_INSTALL_PLUGINS)/multimedia`. Packages: Debian trixie `qt6-multimedia-dev libqt6multimediawidgets6`; the FFmpeg backend, `libffmpegmediaplugin.so`, ships in `libqt6multimedia6`, which the dev package pulls in (trixie has no separate plugins package), and `qtpaths6` in `qt6-base-dev-tools`. Homebrew `qt` carries both modules and the darwin (AVFoundation) plugin.[^config]

Proven on both: macOS Qt 6.11.2 and Pi 5 Qt 6.8.2 play `tests/fixtures/clip.mp4` (H.264 + AAC, 64×64, 1.2 s, made with ffmpeg) to `END_OF_MEDIA` and report `/nope/clip.mp4` as `INVALID_MEDIA` with an error.[^test]

[^source]: QUrl, QAudioOutput, QMediaPlayer, QVideoWidget
[^config]: Module check
[^test]: Play to the end, missing file, pause/seek/loop
