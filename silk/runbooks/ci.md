# CI

How Silk's tests run on GitHub Actions (`.github/workflows/tests.yml`): eight cells, the patched PHP floor, a sibling Surface checkout, and what runs on a runner and what skips.

## tests.yml

Runs on push (every branch), pull requests and `workflow_call`, the same pattern as the framework, Surface and serve. Two jobs, Linux on `ubuntu-24.04` and macOS on `macos-latest`, each a matrix of PHP 8.4 and 8.5 by NTS and ZTS: eight cells, `fail-fast` off. Each cell checks out the repo, sets up PHP with `dom`, `gd`, `intl` and `mbstring` (the newest patch of the line, never a cached older build), checks the floor, runs `composer update --prefer-stable --no-interaction --no-progress` and then `vendor/bin/pest`. The ZTS cells need no ext-parallel: the suite has no thread rows.

## The patched floor

`composer.json`'s `"php": "~8.4.27||^8.5.12"` is a security floor: each line's lowest patched release. The matrix carries the floor per line, and a step refuses a runner PHP below it.

## The sibling Surface checkout

`tests/Pest.php` requires Surface's `FakeFontDriver`, and `tests/Support/M2Helpers.php` reads Surface's fixtures, through `SURFACE_TESTS` (by default a sibling `../surface/tests`). The Packagist dist leaves Surface's tests out, so each job clones [VenusianPHP/surface](https://github.com/VenusianPHP/surface) to `../surface` and points `SURFACE_TESTS` at it. The clone follows Surface's default branch; when the two drift, a line branch may need the clone pinned to its tag.

## What runs on a runner

Dependencies resolve from Packagist: the path repositories are gone from `composer.json`. The suite is engine-free (`SpyEngine`, `SpyPainter`, `SpyLoop`), so nothing needs a display. The native font and raster extensions (freetype, harfbuzz, fontconfig, fb, rasterize, imgdec) are not built on GitHub runners, so the real-text rows skip there (the `hasFontExts()` guards in `ButtonTest`, `LabelWrapTest`, `CaretGeometryTest` and `TextMeasurerTest`, 11 rows on a stock PHP); the `intl` rows run. Locally, under PHP 8.4.27 ZTS with every extension, the whole suite (1690 tests) runs with nothing skipped.

The staged hit-test fixture opens the gallery's window size (900 × 640 points at UI scale 2), so the header bar's centre clears its buttons on both system sides (macOS puts them left, Linux right) and the row is the same on every OS.
