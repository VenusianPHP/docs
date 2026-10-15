# PrepareSharedBag

Seeds the PocketFlow shared bag for `venusian new`.

## Behavior (tested)

`PrepareSharedBag::run(InputInterface $input, OutputInterface $output): array` returns:[^bag][^bag-test]

| Key | Value |
|-----|-------|
| `success` | `null` |
| `name` | `rtrim((string) $input->getArgument('name'), '/\\')` |
| `actions` | `[]` |
| `interactive` | `$input->isInteractive()` (bool) |
| `output_callback` | `function (string $type, string $buffer) use ($output): void` that `$output->write($buffer)` |

Tests drive the callback with `ArrayInput` + `BufferedOutput` and assert the buffer is written.

No node writes `actions`; see [node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration).

## Related

- [Node orchestration](/docs/{{version}}/ecosystem/venusianphp-packages/installer/core/node-orchestration)
- [NewApplicationCommand](/docs/{{version}}/ecosystem/venusianphp-packages/installer/components/newapplicationcommand)

[^bag]: PrepareSharedBag::run
[^bag-test]: Pest coverage for keys and output_callback
