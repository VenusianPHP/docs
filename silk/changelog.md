# Changelog

What changed in this package, newest first.

### 2026-11-08

* **Version**: 0.11.2. Silk is one package: the seven per-component `composer.json` files under `src/Silk` (and the root `replace` block naming them) are gone, and the root PSR-4 `Silk\` → `src/Silk` covers every folder. The path repositories are gone from `composer.json`, so dependencies resolve from Packagist. [overview](/docs/{{version}}/silk/overview)
* CI: `tests.yml` runs eight cells (Linux and macOS, PHP 8.4 and 8.5, NTS and ZTS) against a sibling Surface checkout; the real-text rows skip on runners without the font extensions. The BackgroundBlur light-look test now runs. [ci](/docs/{{version}}/silk/runbooks/ci)
* **Version**: 0.11.0 with the Venusian 0.11 ecosystem. One package, PSR-4 `Silk\` → `src/Silk`, requiring `venusian-surface/*` and `venusian-voyager/*` `^0.11.0` and PHP `~8.4.27||^8.5.12`; `dev-main` is `0.11.x-dev`. [overview](/docs/{{version}}/silk/overview)
* The set is whole: every Raven widget type, BlockEditor (the last of the 50) included; twelve built-in themes over generated tokens; springs, transitions and live theme blending; StagedHost and CanvasHost; the gallery, the bench and golden frames as the drawing gates. [overview](/docs/{{version}}/silk/overview)

### 2026-11-04

* The design: an opinionated module of self-drawn widgets for Surface that look and move like Raven's — Raven the reference, not a dependency. Two hosts (a staged window, a canvas in a toolkit window), no engine-specific code, themable through the service container and config.
