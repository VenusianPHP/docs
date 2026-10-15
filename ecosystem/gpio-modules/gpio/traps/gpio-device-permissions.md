# GPIO device permissions

Opening /dev/gpiochip* or requesting lines fails when the process lacks device permissions or lines are already claimed.

## Symptom

`gpiod_chip_open('/dev/gpiochip0')` returns `null`, or `gpiod_chip_request_lines` fails even though `php -m | grep posi` shows the extension and the chip node exists. Line info may show `used=yes` with another consumer.[^readme][^helpers-chip]

## Cause

Linux GPIO character devices (`/dev/gpiochipN`) are typically mode-restricted (often root or a `gpio` group). This package opens chips with `posix_open` (`O_RDWR | O_CLOEXEC`) after verifying the path is a GPIO chip device — it does not escalate privileges or install udev rules.[^chip][^composer]

Separately, `GPIO_V2_GET_LINE` requests exclusive ownership of configured lines. If another process already claimed a line, the request fails (`null` / error return) even when the chip opened successfully.[^readme]

## Mitigation

- Confirm **ext-posi** `^0.10.0` is installed and the host kernel supports GPIO uAPI v2 (5.10+).[^readme]
- Ensure the PHP process can open `/dev/gpiochip*` (user in `gpio` group, udev `MODE`/`GROUP`, or appropriate container device mounts).
- Use `gpiod_is_gpiochip_device($path)` / `gpiod_chip_get_line_info` to distinguish “not a chip” / “line busy” from other failures.[^readme]
- Release requests with `gpiod_line_request_release` and chips with `gpiod_chip_close` so lines are not left claimed.[^readme]
- Higher-level adapters in `scrapyard-io/gpio-framework` still expect host device permissions to be correct.

## Related

* [Helpers → gpiod facades → posi](/docs/{{version}}/ecosystem/gpio-modules/gpio/architecture/helpers-gpiod-facades-posi)
* [Package (0.10)](/docs/{{version}}/ecosystem/gpio-modules/gpio/orientation/package-010)

[^readme]: Requirements, chip open, request_lines null-on-failure
[^chip]: Chip open verifies device then posix_open
[^helpers-chip]: gpiod_chip_open / gpiod_chip_request_lines helpers
[^composer]: Requires ext-posi
