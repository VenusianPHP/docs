# Ecosystem docs

Published ScrapyardIO ecosystem docs linked from microscrap/mpsse 0.10.

## Entrypoint

Human-facing package docs live on the ScrapyardIO ecosystem site:[^overview]

[https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/mpsse/0.10.x/overview](https://scrapyard-io.projectsaturnstudios.com/ecosystem/microscrap/mpsse/0.10.x/overview)

`composer.json` `homepage` and `support.docs` point at that overview.[^composer-homepage][^readme]

## How agents should use it

- Prefer this OKF bundle for **in-repo** agent rules (wrap layer, traps, enums).
- Prefer the ecosystem site for **published** narrative docs aimed at humans.
- When either drifts from `src/`, update the stale side and note it in [log.md](/docs/{{version}}/ecosystem/gpio-modules/mpsse/changelog).

## Related

* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/mpsse/orientation/package-010)

[^composer-homepage]: composer.json homepage / support.docs fields
[^overview]: Ecosystem overview page
[^readme]: README docs badge and link
