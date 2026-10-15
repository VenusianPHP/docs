# Ecosystem docs

Published ScrapyardIO ecosystem docs for microscrap/i2c 0.10.x.

## Entrypoint

Human-facing package docs live on the ScrapyardIO ecosystem site:[^overview][^readme]

[https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/i2c/0.10.x/overview](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/i2c/0.10.x/overview)

README badges and the production docs banner point at that overview.[^readme]

## How agents should use it

- Prefer this OKF bundle for **in-repo** agent rules (wrap layer, enums, traps, peer pairing).
- Prefer the ecosystem site for **published** narrative docs aimed at humans.
- When either drifts from `src/` or README helper tables, update the stale side and note it in [log.md](/docs/{{version}}/ecosystem/gpio-modules/i2c/changelog).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/i2c/orientation/package-010)

[^readme]: README production docs link and badges
[^overview]: Ecosystem overview page
