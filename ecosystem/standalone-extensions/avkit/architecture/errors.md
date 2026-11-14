# Errors

How AVFoundation, CoreMedia and CoreVideo failures reach PHP; avkit keeps no refusal.

## Overview

* `NSError**` is `?NSError &$error = null` in native position: `AVAssetReader::assetReaderWithAssetError($asset, $error)` returns `null` and sets `$error` (appkit's `NSError`), or sets it to `null`.
* An `NSException` raised inside a call becomes appkit's `AppKitException` (`APPKIT_BEGIN` / `APPKIT_END`). That is translation, not a refusal.
* CoreMedia and CoreVideo statuses (`OSStatus`, `CVReturn`) are the returned `int`. `CMBlockBufferCopyDataBytes` touches `$destination` only when it returns 0; its buffer comes from `zend_string_safe_alloc`, so a negative or huge length ends in PHP's memory fatal, not in native code.
* Value-class readers (`avkit_cmtime_from`, `avkit_cmtimerange_from`) throw `Error` / `ValueError` for an unset property; they are `helpers.marshal` in `bindings.json`.
* No kept refusal: `sites` is empty and there is no `tests/Probes`. `AVPlayerView`'s main-thread gate is appkit's site `main-thread-appkit-ui`, probed in appkit.
