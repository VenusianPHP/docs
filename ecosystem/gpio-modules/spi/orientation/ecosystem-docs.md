# Ecosystem docs

Published ScrapyardIO ecosystem docs for microscrap/spi 0.10.x.

## Entrypoint

Human-facing package docs live on the ScrapyardIO ecosystem site:[^overview][^readme][^composer]

[https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/spi/0.10.x/overview](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/spi/0.10.x/overview)

README badges, the production docs banner, and `composer.json` `homepage` / `support.docs` point at that overview.[^readme][^composer]

## How agents should use it

- Prefer this OKF bundle for **in-repo** agent rules (wrap layer, enums, traps, peer pairing).
- Prefer the ecosystem site for **published** narrative docs aimed at humans.
- When either drifts from `src/` or README helper tables, update the stale side and note it in [log.md](/docs/{{version}}/ecosystem/gpio-modules/spi/changelog).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/spi/orientation/package-010)

[^readme]: README production docs link and badges
[^composer]: homepage and support.docs URLs
[^overview]: Ecosystem overview page
