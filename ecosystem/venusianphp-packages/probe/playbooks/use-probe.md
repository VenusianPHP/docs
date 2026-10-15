# Use probe

Run the probe REPL, execute one-liners, and tune pcntl / aliases safely.

## Interactive REPL

```bash
computer probe
```

Include files before the shell:

```bash
computer probe path/to/bootstrap-snippet.php
```

## One-shot execute

```bash
computer probe --execute="dump(app()->version())"
```

## Config knobs

| Goal | Action |
|------|--------|
| Hardware / FTDI / MPSSE work | Leave `probe.use_pcntl` false[^config] |
| Extra commands in shell | Add FQCNs to `probe.commands` |
| Alias a vendor class | Add prefix to `probe.alias` |
| Never alias a class | Add to `probe.dont_alias` |

## Related

- [ProbeCommand](/docs/{{version}}/ecosystem/venusianphp-packages/probe/components/probecommand)
- [pcntl trap](/docs/{{version}}/ecosystem/venusianphp-packages/probe/traps/pcntl-hardware-fork)
- [Require probe](/docs/{{version}}/ecosystem/venusianphp-packages/probe/playbooks/require-probe)

[^command]: ProbeCommand CLI surface
[^config]: probe config
