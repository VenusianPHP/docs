# On appkit

avkit's classes are ext-appkit objects; how avkit compiles against, loads after and boxes through appkit.

## Overview

* Compile: `config.m4` adds `-I$(php-config --include-dir)/ext/appkit` and stops when `php_appkit_api.h` is missing there. appkit's installer and `PHP_INSTALL_HEADERS` put `php_appkit.h`, `php_appkit_api.h`, `src/runtime.h` and `src/controls.h` there.
* Load: `ZEND_MOD_REQUIRED("appkit")`; without appkit PHP warns "Cannot load module "avkit" because required module "appkit" is not loaded" and starts without avkit. `30-avkit.ini` sorts after `30-appkit.ini`, so appkit.so is loaded first.
* Symbols: avkit calls appkit's functions and reads its class entries directly (`appkit_object_setup`, `appkit_map_objc_class`, `appkit_box_objc`, `appkit_box_cf_as`, `appkit_ce_NSObject`, …). The bundle links with `-undefined dynamic_lookup`; they resolve against the loaded appkit.so.
* Objective-C classes: `AVKIT_MAP(name, parent)` registers the class on its appkit parent, gives it appkit's object model, and adds it to appkit's class map, so appkit's boxing (`appkit_box_objc`, e.g. `NSView::subviews()`) returns `AVPlayerView`, not `NSView`.
* CF types: `AVKIT_CF(name, parent)` registers on `CFType` (or an avkit CF parent). `appkit_box_cf_as(rv, ref, ce)` boxes as the given class: `CMSampleBuffer`, `CMBlockBuffer`, `CVPixelBuffer` (`avkit_box_image_buffer`: `CVImageBuffer` unless `CVPixelBufferGetTypeID()`), and `CMVideoFormatDescription` / `CMAudioFormatDescription` by `CMFormatDescriptionGetMediaType()` (`avkit_box_format_description`).
* Lifetime: one PHP object per native object (appkit's identity table), retained while PHP holds it. A +1 result (`copyNextSampleBuffer`) is released after boxing; a `Get` result is retained by the box.
* Bodies use appkit's `controls.h` macros (`ANY_METHOD`, `OBJ_GET`, …). The non-`ANY_` ones carry appkit's main-thread gate (`main-thread-appkit-ui`): only `AVPlayerView` uses them.
