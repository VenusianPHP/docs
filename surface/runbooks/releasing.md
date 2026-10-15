# Releasing

A `vX.Y.Z` tag on `VenusianPHP/surface` runs the suite, then splits every component to the `venusian-surface` organisation and tags each split with the same version.

## Flow

Push a `vX.Y.Z` tag. `.github/workflows/split.yml` calls `tests.yml` (PHP 8.4/8.5); a red suite means no split. Green → `.github/split.sh` runs splitsh-lite v1.0.1 on every `src/<Namespace>/<Component>/` holding a `composer.json` and pushes each split to `github.com/venusian-surface/<package name after the vendor>`.[^split-sh]

Versions are lockstep: every split gets the monorepo's tag, changed or not. A patch tag bumps every split by the same patch; only a tag you choose moves the minor.

## Branches

The tag must sit at the head of the `X.Y.x` line branch or of `main`, else the run refuses.

| Tag sits on | Monorepo | Splits receive |
|---|---|---|
| `X.Y.x` and `main` | — | `X.Y.x`, `main`, tag |
| `X.Y.x` only (old line) | — | `X.Y.x`, tag |
| `main`, no `X.Y.x` yet (new minor) | creates `X.Y.x` at the tag | `X.Y.x`, `main`, tag |
| `main`, `X.Y.x` behind it | fast-forwards `X.Y.x` | `X.Y.x`, `main`, tag |
| `main`, `X.Y.x` diverged | refuses | nothing |

Split branches are force-pushed (splitsh output is deterministic). Tags are never forced.

## Manifest checks

Run on every tag before any push; all problems are listed at once:

- root and component `version`, when present, equal the tag;
- `extra.branch-alias.dev-main` is `X.Y.x-dev` in the root and every component;
- every require / require-dev on a sibling component is `^X.Y` or `^X.Y.N`.

The commit tagged `vX.Y.0` must already carry the new aliases and sibling constraints. Every split repo must answer `git ls-remote`; one missing repo → nothing pushed.

## Adding a component

Create `github.com/venusian-surface/<name>`, add `src/<Namespace>/<Component>/composer.json` named `<vendor>/<name>`, submit it to Packagist after the first split. No workflow edit: the split list is the directory listing.

## Secret

`SPLIT_TOKEN`: a repository secret of `VenusianPHP/surface`, a token with write access to the `venusian-surface` repositories.[^split-yml]

[^split-sh]: .github/split.sh
[^split-yml]: .github/workflows/split.yml
