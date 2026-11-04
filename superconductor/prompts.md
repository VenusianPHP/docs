# Prompts

A prompt is a message template a client can ask a server for: its constructor is its argument list, and its `handle()` method writes the messages.

<a id="introduction"></a>
## Introduction

A prompt extends `Fabricate\Mechanism\Prompt` in `App\Mcp\Prompts` and carries a `#[PromptCall(name, description)]` attribute. Every prompt in that folder is registered when the application boots, and a [server](/docs/{{version}}/superconductor/servers#what-a-server-offers) offers it by naming it in `prompts()`.

```php
<?php

namespace App\Mcp\Prompts;

use Fabricate\Contracts\Mechanism\Attributes\PromptCall;
use Fabricate\Mechanism\Prompt;

#[PromptCall('greet', 'Ask for a greeting in the given tone.')]
class GreetPrompt extends Prompt
{
    public function __construct(public readonly string $name, public readonly string $tone = 'friendly') {}

    public function handle(): string
    {
        return "Write a {$this->tone} greeting for {$this->name}.";
    }
}
```

<a id="arguments"></a>
## Arguments

Each constructor parameter is an argument, and one without a default is required. Prompt arguments are strings on the wire, so every parameter must be a `string`; a prompt with any other type is refused when it registers. An `#[Argument]` on a parameter gives it a `description`, and from 2025-06-18 a `title`.

`#[PromptCall]` takes a `title`, sent from 2025-06-18, and repeatable `#[Icon]` attributes are sent from 2025-11-25.

<a id="getting-a-prompt"></a>
## Getting a Prompt

`prompts/get` builds the prompt from the request's arguments by name and calls `handle()`, which is resolved through the container the way a [tool's](/docs/{{version}}/superconductor/tools#handling-a-call) is. It returns:

| Returned | Becomes |
| --- | --- |
| a string | one `user` text message |
| the version's own `PromptMessage` | that message, for the `assistant` role or other content |
| a list of those | those messages, in order |

Anything else is -32603. An unknown prompt, and missing, unknown or positional arguments, are -32602 in every version. The result's description is the prompt's. A prompt can set `protected bool $async = true` and answer later, as an [async tool](/docs/{{version}}/superconductor/tools#async-tools) does.

`prompts/list` pages the server's prompts like `tools/list`, with each argument's name and whether it is required.

<a id="completion"></a>
## Completion

A prompt suggests values for an argument by overriding the static `complete()`, which returns a `Fabricate\Mechanism\CompletionResult`:

```php
public static function complete(string $argument, string $value, array $context = []): CompletionResult
{
    $tones = ['friendly', 'formal', 'pirate'];

    return new CompletionResult(array_values(array_filter($tones, fn(string $tone) => str_starts_with($tone, $value))));
}
```

`$context` holds the arguments the client has already filled in, which clients send from 2025-06-18. A result holds at most 100 values; past that they are cut and `hasMore` is set, and the optional `total` says how many exist. The default suggests nothing.

`completion/complete` needs the server's `$completions` capability on, or it is -32601. An unknown prompt, or an argument the prompt doesn't have, is -32602.
