# Overview

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/avkit/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/avkit/actions/workflows/ci.yml)
[![AVFoundation API](https://img.shields.io/badge/AVFoundation_API-3.0%25_%2879%2F2658%29-blue?style=flat-square)](https://github.com/php-io-extensions/avkit/blob/main/SUPPORT.md)

1:1 PHP bindings of AVFoundation, AVKit, CoreMedia and CoreVideo, as classes and functions named after their native counterparts. Version 0.11.2. macOS only.

A handle is one PHP object per native object, retained while PHP holds it. Requires ext-appkit 0.11.2: avkit's classes are appkit objects, `AVPlayerView` is an appkit `NSView`, and an `NSURL`, `NSError`, `CGSize` or `CFTypeRef` is appkit's `NSURL`, `NSError`, `NSSize` or `CFType`. An `NSException` becomes appkit's `AppKitException`.

## Requirements

- macOS
- PHP 8.4, NTS or ZTS
- ext-appkit 0.11.2, installed first (avkit compiles against its headers and loads after it)

## Install

Through PIE:

```bash
pie install php-io-extensions/avkit
```

From a checkout of this repository:

```bash
./install-macos.sh
```

That builds into Homebrew `php@8.4` and `php@8.4-zts`, ad-hoc signs the `.so`, and writes `30-avkit.ini`. Pass other PHP binaries as arguments to install those instead.

## Names

- One PHP class per native class or CF type, one method per selector. Keywords are joined in camelCase: `assetReaderTrackOutputWithTrack:outputSettings:` is `assetReaderTrackOutputWithTrackOutputSettings()`.
- A C function is a global function under its C name: `CMTimeMake()`, `CMSampleBufferGetImageBuffer()`, `CVPixelBufferGetBytesPerRow()`.
- Enum cases are the C constant without its type prefix, in upper snake case: `AVAssetReaderStatusCompleted` is `AVAssetReaderStatus::COMPLETED`.
- An `NSDictionary` argument (asset options, reader output settings) is a PHP array with string keys and string, int, float, bool or object values.
- An `NSError**` is a by-reference `?NSError &$error` in native position. A nil result is `null`.
- A pixel address is an `int` (`CVPixelBufferGetBaseAddress()`), valid while the buffer is locked. `CMBlockBufferCopyDataBytes()` writes the bytes into its by-reference string when it returns 0.

## What is bound

| Framework | Bound |
|---|---|
| AVFoundation | `AVAsset` (duration, tracks, tracksWithMediaType:), `AVURLAsset` (URLAssetWithURL:options:, URL), `AVAssetTrack` (trackID, mediaType, naturalSize, nominalFrameRate, timeRange, formatDescriptions), `AVAssetReader` (assetReaderWithAsset:error:, asset, status, error, timeRange (+set), canAddOutput:, addOutput:, startReading, cancelReading), `AVAssetReaderOutput` (mediaType, alwaysCopiesSampleData (+set), copyNextSampleBuffer), `AVAssetReaderTrackOutput` (assetReaderTrackOutputWithTrack:outputSettings:, track), `AVPlayerItem` (playerItemWithURL:, status, duration, error), `AVPlayer` (playerWithPlayerItem:, play, pause, rate (+set), currentTime, seekToTime:, isMuted (+set), timeControlStatus, actionAtItemEnd (+set), currentItem, replaceCurrentItemWithPlayerItem:). Enums `AVAssetReaderStatus`, `AVPlayerItemStatus`, `AVPlayerTimeControlStatus`, `AVPlayerActionAtItemEnd`. Constants `AVMediaTypeVideo`, `AVMediaTypeAudio`, `AVPlayerItemDidPlayToEndTimeNotification`, `AVFormatIDKey`, `AVSampleRateKey`, `AVNumberOfChannelsKey`, `AVLinearPCMBitDepthKey`, `AVLinearPCMIsFloatKey`, `AVLinearPCMIsBigEndianKey`, `AVLinearPCMIsNonInterleaved`, `kAudioFormatLinearPCM` |
| AVKit | `AVPlayerView extends NSView` (player (+set), controlsStyle (+set)), enum `AVPlayerViewControlsStyle` |
| CoreMedia | `CMTime`, `CMTimeRange`, `CMVideoDimensions`, `AudioStreamBasicDescription` value classes; `CMSampleBuffer`, `CMBlockBuffer`, `CMFormatDescription`, `CMVideoFormatDescription`, `CMAudioFormatDescription`; `CMTimeMake`, `CMTimeMakeWithSeconds`, `CMTimeGetSeconds`, `CMTimeCompare`, `CMTimeRangeMake`, `CMTimeRangeGetEnd`, `CMSampleBufferGetImageBuffer`, `CMSampleBufferGetDataBuffer`, `CMSampleBufferGetFormatDescription`, `CMSampleBufferGetPresentationTimeStamp`, `CMSampleBufferGetDuration`, `CMSampleBufferGetNumSamples`, `CMBlockBufferGetDataLength`, `CMBlockBufferCopyDataBytes`, `CMFormatDescriptionGetMediaType`, `CMVideoFormatDescriptionGetDimensions`, `CMAudioFormatDescriptionGetStreamBasicDescription`; `kCMTimeFlags_*`, `kCMMediaType_Video`, `kCMMediaType_Audio` |
| CoreVideo | `CVBuffer`, `CVImageBuffer`, `CVPixelBuffer`; `CVPixelBufferLockBaseAddress`, `CVPixelBufferUnlockBaseAddress`, `CVPixelBufferGetBaseAddress`, `CVPixelBufferGetBytesPerRow`, `CVPixelBufferGetWidth`, `CVPixelBufferGetHeight`, `CVPixelBufferGetPixelFormatType`, `CVPixelBufferGetDataSize`, `CVPixelBufferIsPlanar`, `CVPixelBufferGetPlaneCount` and the `…OfPlane` getters; `kCVPixelBufferLock_ReadOnly`, `kCVPixelFormatType_32BGRA`, `kCVPixelBufferPixelFormatTypeKey` |

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/avkit/blob/main/SUPPORT.md) lists every method and property accessor that the SDK's AVFoundation,
AVKit, CoreMedia and CoreVideo headers declare on a class or category, and their `AV`, `CM` and
`CV` C functions, not deprecated or unavailable on macOS, each marked bound or not; protocol
methods (delegates) are not counted. The API badge is computed from it. Regenerate both after a
binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

## Example

Every frame of a movie as BGRA pixels, every audio chunk as 16-bit PCM:

```php
$asset = AVURLAsset::URLAssetWithURLOptions(NSURL::fileURLWithPath('movie.mp4'), null);
$reader = AVAssetReader::assetReaderWithAssetError($asset, $error) ?? throw new RuntimeException($error->localizedDescription());
$video = AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrackOutputSettings(
    $asset->tracksWithMediaType(AVMediaTypeVideo)[0],
    [kCVPixelBufferPixelFormatTypeKey => kCVPixelFormatType_32BGRA],
);
$audio = AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrackOutputSettings(
    $asset->tracksWithMediaType(AVMediaTypeAudio)[0],
    [AVFormatIDKey => kAudioFormatLinearPCM, AVLinearPCMBitDepthKey => 16, AVLinearPCMIsFloatKey => false,
        AVLinearPCMIsBigEndianKey => false, AVLinearPCMIsNonInterleaved => false],
);
$reader->addOutput($video);
$reader->addOutput($audio);
$reader->startReading();

// One reader feeds both outputs: read them in turn so neither backs up behind the other.
do {
    if (($frame = $video->copyNextSampleBuffer()) !== null) {
        $pixels = CMSampleBufferGetImageBuffer($frame);
        CVPixelBufferLockBaseAddress($pixels, kCVPixelBufferLock_ReadOnly);
        $address = CVPixelBufferGetBaseAddress($pixels);   // BGRA, CVPixelBufferGetBytesPerRow() bytes a row
        CVPixelBufferUnlockBaseAddress($pixels, kCVPixelBufferLock_ReadOnly);
    }
    if (($chunk = $audio->copyNextSampleBuffer()) !== null) {
        $block = CMSampleBufferGetDataBuffer($chunk);
        CMBlockBufferCopyDataBytes($block, 0, CMBlockBufferGetDataLength($block), $pcm);
    }
} while ($frame !== null || $chunk !== null);
```

## Test

```bash
composer install
php84 -d memory_limit=128M vendor/bin/pest
zhp -d memory_limit=128M vendor/bin/pest
```

## License

MIT. See [LICENSE](https://github.com/php-io-extensions/avkit/blob/main/LICENSE).
