# Changelog

What changed in this package, newest first.

### 2026-10-09

* **0.10.2**: Discarded output goes to the app's log. With stderr closed or on `/dev/null` (Finder, a desktop menu, launchd), stderr — and stdout when it is discarded too — is appended to `~/Library/Logs/<name>/<name>.log` on macOS or `$XDG_STATE_HOME/<name>/<name>.log` (default `~/.local/state`) elsewhere, behind a timestamped header. [Behaviour](/docs/{{version}}/ecosystem/venusianphp-packages/sapi/behaviour).

* **0.10.1**: `CG(skip_shebang)` set as the CLI sets it. Packaged Stargazer on the gaming PC printed `rocket`'s `#!/usr/bin/env php`, and its pool workers wrote it onto their protocol pipes. [Behaviour](/docs/{{version}}/ecosystem/venusianphp-packages/sapi/behaviour).

* **Creation**: Venusian SAPI 0.10.0, the executable of a packaged app, replacing phpmicro in venusian/build's design. [Behaviour](/docs/{{version}}/ecosystem/venusianphp-packages/sapi/behaviour) records what it reports and where it finds the phar.
