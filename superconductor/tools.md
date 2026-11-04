# Tools

A tool is a class a model can call through a server: its constructor is its input schema, and its `handle()` method is what runs.

<a id="introduction"></a>
## Introduction

A tool extends `Fabricate\Mechanism\Tool` in `App\Mcp\Tools` and carries a `#[ToolCall(name, description)]` attribute. Every tool in that folder is registered when the application boots, and a [server](/docs/{{version}}/superconductor/servers#what-a-server-offers) offers it by naming it in `tools()`.

```php
<?php

namespace App\Mcp\Tools;

use Fabricate\Contracts\Mechanism\Attributes\ToolCall;
use Fabricate\Mechanism\Tool;

#[ToolCall('shout', 'Send back the message in upper case.')]
class ShoutTool extends Tool
{
    public function __construct(public readonly string $message) {}

    public function handle(): string
    {
        return strtoupper($this->message);
    }
}
```

A tool name is 1 to 128 characters, each a letter, digit, underscore, hyphen or dot, and unique across the application; a name that breaks either rule is refused when the tool registers.

<a id="arguments"></a>
## Arguments

Each constructor parameter is an argument, and one without a default is required. Parameter types map to JSON Schema types:

| PHP | JSON Schema |
| --- | --- |
| `string` | `string` |
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `array` | `object` |
| anything else | any value |

`tools/call` passes the request's arguments to the constructor by name, under strict types, so a wrong JSON type is refused rather than coerced. Missing, unknown, mistyped or positional arguments are -32602 up to 2025-06-18; from 2025-11-25 they come back as a result with `isError`, so the model can correct its call.

An `#[Argument]` on a parameter describes it:

```php
public function __construct(
    #[Argument('What to think over.')] public readonly string $message,
    #[Argument('How long to think, in seconds.', title: 'Seconds')] public readonly int $seconds = 5,
) {}
```

`description` is sent in every version, `title` from 2025-06-18. `header` mirrors the argument into an HTTP header on 2026-07-28; see [protocol versions](/docs/{{version}}/superconductor/protocol-versions#mirrored-headers).

<a id="metadata"></a>
## Metadata

| Attribute | Sent |
| --- | --- |
| `#[ToolCall(name, description, title)]` | `title` from 2025-06-18 |
| `#[ToolAnnotations(title, readOnlyHint, destructiveHint, idempotentHint, openWorldHint)]` | from 2025-03-26 |
| `#[Icon(src, mimeType, sizes, theme)]`, repeatable | from 2025-11-25 |

<a id="handling-a-call"></a>
## Handling a Call

`handle()` is called through the [service container](/docs/{{version}}/framework/architecture-concepts/container). A parameter typed as the server configuration gets the configuration that received the call, `$protocol_version` gets the session's version, a `RequestContext` gets [the request's context](#the-request-context), and anything else is resolved from the container.

What `handle()` returns becomes the result's content:

| Returned | Content |
| --- | --- |
| `null` | none |
| a string or scalar | one text item |
| a list | one text item per entry |
| the version's own content objects | passed through: text, image, audio, embedded resources, and from 2025-06-18 resource links |
| anything else | one text item holding it as JSON |

An exception thrown from `handle()` becomes a result with `isError` and its message, so the model sees what went wrong.

<a id="structured-output"></a>
### Structured Output

A tool that overrides the static `outputSchema()` is listed with that schema from 2025-06-18, and returns an associative array from `handle()`. The array goes out as `structuredContent` from 2025-06-18, and as JSON text in every version.

<a id="the-request-context"></a>
## The Request Context

A `RequestContext` parameter on `handle()` reaches the client while the tool works:

```php
public function handle(?RequestContext $context = null): string
{
    $context?->log(LoggingLevel::INFO, 'Starting.', 'ponder');
    $context?->progress(0, 10, 'Pondering');

    // ...
}
```

| Method | Does |
| --- | --- |
| `log($level, $data, $logger)` | Sends `notifications/message` when the server declares logging and the level is at or above the client's |
| `progress($progress, $total, $message)` | Sends `notifications/progress` when the request carried a progress token; 2024-11-05 has no `message` |
| `cancelled()` | Whether the client cancelled the request; once it has, nothing more is sent for it |

<a id="async-tools"></a>
## Async Tools

A tool whose work takes a while sets `protected bool $async = true`. `handle()` then starts the work and returns, and the server goes on answering other requests; the work calls `$this->finish($output)` with what `handle()` would have returned, or `$this->fail($reason)` with a `Throwable`:

```php
protected bool $async = true;

public function handle(): ?string
{
    if(! $this->isAsync()) return self::ponder($this->message);

    $message = $this->message;

    app('concurrency')->driver('pool')
        ->async(static fn() => self::ponder($message), 'ponder')
        ->then(fn(array $results) => $this->finish($results[0]), fn(Throwable $e) => $this->fail($e));

    return null;
}
```

The answer goes back to the client as [loop mail](/docs/{{version}}/framework/the-basics/loop-mail). When there is no session to post it to, `isAsync()` is false and the tool must answer at once, so an async tool keeps a sync path.

<a id="tasks"></a>
## Tasks

`protected static string $task_support` says whether a client may run the tool as a [task](/docs/{{version}}/superconductor/tasks): `self::TASKS_FORBIDDEN`, the default, `self::TASKS_OPTIONAL` or `self::TASKS_REQUIRED`. `tools/list` advertises it as `execution.taskSupport`.

<a id="capability-tools"></a>
## Capability Tools

Core registers eight tools of its own, which a server offers by naming them in `tools()` like any other:

| Tool | Does |
| --- | --- |
| `list_tools`, `search_tools` | List the server's tools, or those matching a query |
| `search_prompts` | The server's prompts matching a query |
| `list_resources`, `search_resources` | The server's resources |
| `list_resource_templates`, `search_resource_templates` | The server's resource templates |
| `execute_tool` | Runs another tool the server offers, by name |

The search tools match a query against any text field. `execute_tool` is async: when the tool it runs is async too, that tool's outcome becomes its own without holding the loop.

<a id="listing-tools"></a>
## Listing Tools

`tools/list` pages the server's tools `mcp.pagination.page_size` at a time behind an opaque cursor; a cursor the server didn't issue is -32602. Each entry is built from the class in the session's version. On 2026-07-28 the list is marked not cacheable.

When the set of tools changes, call the static `listChanged()` on any tool class; every session whose server declared `tools.listChanged` gets `notifications/tools/list_changed`. Pass a session id to tell only that session.
