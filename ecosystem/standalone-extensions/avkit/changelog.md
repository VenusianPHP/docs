# Changelog

What changed in this package, newest first.

### 2026-11-11

* Bundle created with ext-avkit 0.11.2: AVFoundation, AVKit, CoreMedia and CoreVideo 1:1 on ext-appkit's object model, compiled against appkit's installed `php_appkit_api.h`. [on appkit](/docs/{{version}}/ecosystem/standalone-extensions/avkit/architecture/on-appkit)
* Playback classes moved from ext-appkit: `AVPlayerItem`, `AVPlayer`, `AVPlayerView` (an appkit `NSView`), their enums, `AVPlayerItemDidPlayToEndTimeNotification`, and `CMTime`. appkit's `CMTime::make()`, `makeWithSeconds()`, `getSeconds()` and `FLAG_*` are now `CMTimeMake()`, `CMTimeMakeWithSeconds()`, `CMTimeGetSeconds()` and `kCMTimeFlags_*`.
* Decode path, the same job as ext-ffmpeg's: `AVURLAsset` → `AVAssetReader` → `AVAssetReaderTrackOutput` → `CMSampleBuffer` → `CVPixelBuffer` (BGRA, by address) or `CMBlockBuffer` (PCM bytes). The test clip decodes to 10 frames of 64×48 and 44100 samples of 16-bit mono PCM. Suite 25 passed (311 assertions) on Homebrew PHP 8.4 NTS and ZTS. [decode path](/docs/{{version}}/ecosystem/standalone-extensions/avkit/architecture/decode-path), [bindings](/docs/{{version}}/ecosystem/standalone-extensions/avkit/api/bindings), [errors](/docs/{{version}}/ecosystem/standalone-extensions/avkit/architecture/errors), [build](/docs/{{version}}/ecosystem/standalone-extensions/avkit/runbooks/build-install-test)
