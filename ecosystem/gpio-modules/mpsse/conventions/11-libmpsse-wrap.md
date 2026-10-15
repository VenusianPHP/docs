# 1:1 libmpsse wrap

Keep MPSSE API aligned with libmpsse / existing surface; helpers stay thin over Microscrap\Bindings\MPSSE\MPSSE; no invented APIs.

## Rule

Match the existing public surface; stay aligned with libmpsse patterns already expressed in `MPSSE`:[^agents][^readme][^mpsse]

1. Global helpers use `mpsse_*` names and stay **thin** over `MPSSE::*`.[^helpers]
2. Protocol logic belongs on `Microscrap\Bindings\MPSSE\MPSSE` — do not invent a second wrapper or bypass into ad-hoc FTDI bitmode scripts from helpers.[^mpsse]
3. Do **not** invent APIs that are not already in `src/` / README — extend only when Angel asks and keep libmpsse alignment.[^agents]
4. Context is package-owned `MPSSEContext` — do not invent parallel DataObjects beyond this.[^readme]
5. Mode / pin / device tokens live in backed enums — see [Enums for MPSSE](/docs/{{version}}/ecosystem/gpio-modules/mpsse/conventions/enums-for-mpsse).
6. Prefer `is_null($var)` over `$var === null`.[^agents]
7. No class-level constants in `src/` — use backed enums.[^agents]
8. No ServiceProvider / Chassis / Core / Fabricate wiring in this package.[^readme][^agents]
9. Do **not** invent a CoverageDrift suite unless Angel asks.[^agents]

## Architecture link

Full call-stack diagram: [Helpers → MPSSE → FTDI](/docs/{{version}}/ecosystem/gpio-modules/mpsse/architecture/helpers-mpsse-ftdi).

[^agents]: Agent wrap rules
[^readme]: Package README wrap description
[^helpers]: Thin helper delegation to MPSSE
[^mpsse]: Pure-PHP libmpsse port
