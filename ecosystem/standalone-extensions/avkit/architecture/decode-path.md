# Decode path

A movie read as BGRA frames and PCM through AVAssetReader; what the fixture decodes to.

## Overview

`NSURL::fileURLWithPath()` → `AVURLAsset::URLAssetWithURLOptions()` → `tracksWithMediaType(AVMediaTypeVideo | AVMediaTypeAudio)` → `AVAssetReader::assetReaderWithAssetError()` → `AVAssetReaderTrackOutput::assetReaderTrackOutputWithTrackOutputSettings()` → `addOutput()` → `startReading()` → `copyNextSampleBuffer()` until `null`.

* Conversion is the reader's: output settings `[kCVPixelBufferPixelFormatTypeKey => kCVPixelFormatType_32BGRA]` give BGRA frames; `[AVFormatIDKey => kAudioFormatLinearPCM, AVLinearPCMBitDepthKey => 16, AVLinearPCMIsFloatKey => false, AVLinearPCMIsBigEndianKey => false, AVLinearPCMIsNonInterleaved => false]` gives 16-bit interleaved PCM. The array becomes an `NSDictionary` through appkit's `appkit_nsdictionary` (ints and bools as `NSNumber`).
* Video: `CMSampleBufferGetImageBuffer()` → `CVPixelBuffer`; lock (`kCVPixelBufferLock_ReadOnly`), `CVPixelBufferGetBaseAddress()` (an int address, valid while locked), `GetBytesPerRow`, `GetWidth`, `GetHeight`; unlock. Pixel bytes are not copied into PHP; another extension reads the address.
* Audio: `CMSampleBufferGetDataBuffer()` → `CMBlockBuffer`; `CMBlockBufferCopyDataBytes($block, 0, CMBlockBufferGetDataLength($block), $bytes)` writes the bytes when it returns 0. `CMAudioFormatDescriptionGetStreamBasicDescription(CMSampleBufferGetFormatDescription($sample))` describes them.
* Several outputs on one reader: read them in turn (the [overview's example](/docs/{{version}}/ecosystem/standalone-extensions/avkit/overview#example)); draining one first makes the reader buffer the others.
* Track properties are the synchronous ObjC selectors (`tracksWithMediaType:`, `naturalSize`, `timeRange`, …), deprecated for Swift only; no completion handlers.
* A decoded video frame's `CMSampleBufferGetDuration()` is invalid (NaN seconds); presentation timestamps step by the frame period.

Fixture (`tests/Fixtures/clip.mp4.b64`, SHA-256 `abc0173c…`): 1 s, 64×48 H.264 at 10 fps, 44.1 kHz mono AAC. Decodes to 10 BGRA frames of 256 bytes a row, and 44100 samples (88200 bytes) of PCM. A missing file gives no reader and NSError −11800; a non-media file −11829.
