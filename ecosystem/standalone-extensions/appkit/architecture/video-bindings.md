# Video bindings

AVKit/AVFoundation as bound: URL → item → player → view; end-of-play notification; status and time control reads.

## Overview

`NSURL::fileURLWithPath()` → `AVPlayerItem::playerItemWithURL()` → `AVPlayer::playerWithPlayerItem()` → `AVPlayerView::setPlayer()`.[^avkit]

* Ownership: view retains player, player retains item; PHP boxes hold their own references. `setPlayer(null)` detaches.
* Loading is async: `status()` is `UNKNOWN` until the item is ready (`READY_TO_PLAY`) or `FAILED` (`error()` = `?NSError`: domain, code, `localizedDescription()`, userInfo). `duration()` is NaN seconds before ready. `play()` before ready is fine: `timeControlStatus()` reports `WAITING_TO_PLAY_AT_SPECIFIED_RATE` then `PLAYING`.
* End of play: `AVPlayerItemDidPlayToEndTimeNotification` through `NSNotificationCenter::defaultCenter()->addObserverForNameObjectQueueUsingBlock(name, item, NSOperationQueue::mainQueue(), callable)`; the player pauses itself (`timeControlStatus()` = `PAUSED`). Remove the token when done.[^center]
* AVPlayerItem may post its notifications on any thread (`AVPlayerItem.h`). The main queue moves delivery onto the main thread, drained by the run loop the app pumps (`nextEventMatchingMask…`); with a null queue a background post never reaches PHP (callables only run on the thread that registered them).
* `timeControlStatus`/`status` are KVO-observable with `ObjCObserver` for change-driven code instead of polling. AVPlayer posts these changes on the main queue by default (`AVPlayer.h`), so they reach PHP; verified for READY_TO_PLAY, FAILED, WAITING → PLAYING → PAUSED.

Values: `CMTime` is a PHP value class carrying the whole struct (`value`, `timescale`, `flags`, `epoch`; `FLAG_*`), all four required by `new CMTime(…)`. `duration()` before the item is ready is indefinite (`FLAG_INDEFINITE`, NaN seconds). `CMTime::make()` / `makeWithSeconds()` / `getSeconds()` = `CMTimeMake` / `CMTimeMakeWithSeconds` / `CMTimeGetSeconds`.

KVO: `$observer->observe($player, 'timeControlStatus', ObjCObserver::OPTION_NEW, 0)`; the handler reads `$change['new']` from KVO's full change dictionary.

Links: AVKit, AVFoundation, CoreMedia frameworks (config.m4).

[^avkit]: NSURL, CMTime, AVPlayerItem, AVPlayer, AVPlayerView
[^center]: block observers
