<h1 align="center">Venusian Documentation</h1>

<p align="center">
<a href="https://github.com/VenusianPHP/docs/actions/workflows/links.yml"><img src="https://github.com/VenusianPHP/docs/actions/workflows/links.yml/badge.svg" alt="Links"></a>
<a href="https://github.com/VenusianPHP/docs/blob/0.10.x/LICENSE"><img src="https://img.shields.io/github/license/VenusianPHP/docs.svg" alt="License"></a>
</p>

## Introduction

This repository holds the documentation for Venusian, the core framework, Surface (displays and graphics) and the ecosystem of extensions and packages around them, and for ScrapyardIO, the GPIO framework for Venusian with its PHP IO extensions, microscrap modules and chip drivers. Venusian's documentation lives at [venusian.projectsaturnstudios.com/docs](https://venusian.projectsaturnstudios.com/docs), ScrapyardIO's at [scrapyard-io.projectsaturnstudios.com/docs](https://scrapyard-io.projectsaturnstudios.com/docs).

## Layout

Each release line has its own branch: `0.10.x` documents Venusian 0.10. Pages are plain Markdown, one file per page, under `framework/`, `surface/`, `scrapyard-io/` and `ecosystem/`. Each site has its own sidebar: [`documentation.md`](documentation.md) for Venusian and [`scrapyard-io.md`](scrapyard-io.md) for ScrapyardIO. A sidebar's `##` entries are its top-level sections, and its links set the reading order. Every page belongs to exactly one sidebar.

Links between pages of the same site use the `{{version}}` placeholder, which the site replaces with the branch being read; a page on the other site is linked by its absolute URL, such as `https://scrapyard-io.projectsaturnstudios.com/docs/scrapyard-io/getting-started/installation`:

```markdown
[Service Container](/docs/{{version}}/framework/architecture-concepts/container)
```

## Contributing

Thank you for considering contributing to the Venusian documentation! Open a pull request against the branch of the release line you are documenting. A new page needs an entry in its site's sidebar; the link check fails the pull request when a sidebar entry has no page, a page is in no sidebar or in both, or a `/docs/{{version}}/…` link points at a page that does not exist or lives on the other site.

## Code of Conduct

In order to ensure that the Venusian community is welcoming to all, please review and abide by the [Code of Conduct](https://venusian.projectsaturnstudios.com/docs/contributions#code-of-conduct).

## License

The Venusian documentation is open-sourced software licensed under the [MIT license](LICENSE).
