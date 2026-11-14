# Bindings

Every class and function avkit binds, by framework.

## Overview

The stubs in `stubs/` are the declaration; [the overview's "What is bound" table](/docs/{{version}}/ecosystem/standalone-extensions/avkit/overview#what-is-bound) lists them by framework.

* Playback (AVFoundation, AVKit): `AVPlayerItem`, `AVPlayer`, `AVPlayerView extends NSView`, their enums, `AVPlayerItemDidPlayToEndTimeNotification`. Observe the end of play with appkit's `NSNotificationCenter` on `NSOperationQueue::mainQueue()`: AVPlayerItem may post on any thread.
* Assets and readers (AVFoundation): `AVAsset`, `AVURLAsset`, `AVAssetTrack`, `AVAssetReader`, `AVAssetReaderOutput`, `AVAssetReaderTrackOutput`, `AVAssetReaderStatus`; media-type and output-settings constants, `kAudioFormatLinearPCM`.
* Buffers (CoreMedia, CoreVideo): `CMSampleBuffer`, `CMBlockBuffer`, `CMFormatDescription` → `CMVideoFormatDescription` / `CMAudioFormatDescription`, `CVBuffer` → `CVImageBuffer` → `CVPixelBuffer`, and their C functions under their C names.
* Values: `CMTime`, `CMTimeRange`, `CMVideoDimensions`, `AudioStreamBasicDescription` — `final`, public properties named as the C fields, every field a constructor argument.

Guard notes (`bindings.json`): `CMVideoDimensions` is under `glue` (an anonymous-struct typedef the guard's index does not read); `typemap` maps `CMMediaType` and `OSType` to `int` (they resolve through `MacTypes.h`'s `FourCharCode`).
