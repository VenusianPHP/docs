# Servers

A server configuration declares one MCP server: its name, the protocol versions it speaks, the capabilities it declares, and the tools, prompts and resources it offers.

<a id="introduction"></a>
## Introduction

An MCP server is a class extending `Fabricate\Server\ServerConfiguration` in `App\Mcp\Servers`, carrying a `#[ServerConfig]` attribute. The class says what the server is; [tools](/docs/{{version}}/superconductor/tools), [prompts](/docs/{{version}}/superconductor/prompts) and [resources](/docs/{{version}}/superconductor/resources) are classes of their own, which a server offers by name.

```php
<?php

namespace App\Mcp\Servers;

use Fabricate\Contracts\Mechanism\Attributes\ServerConfig;
use Fabricate\Server\ServerConfiguration;

#[ServerConfig('echo', 'Repeats what it is told.', '1.0.0')]
class EchoServer extends ServerConfiguration
{
    protected array $supported_protocol_versions = ['2025-06-18', '2025-11-25', '2026-07-28'];

    protected bool|array $tools = ['listChanged' => true];

    public function tools(mixed ...$params): array
    {
        return ['echo', 'shout'];
    }
}
```

A transport serves the server by the name in its attribute: `php rocket mcp:cli echo` over [stdio](/docs/{{version}}/superconductor/stdio), or `mcp/echo` over [HTTP](/docs/{{version}}/superconductor/web).

<a id="the-server-attribute"></a>
## The Server Attribute

`#[ServerConfig]` names the server and describes it to clients:

| Argument | Sent as |
| --- | --- |
| `name` | `serverInfo.name`, and the name transports serve it by |
| `description` | `serverInfo.description`, from 2025-11-25 |
| `version` | `serverInfo.version` |
| `title` | `serverInfo.title`, from 2025-06-18 |
| `websiteUrl` | `serverInfo.websiteUrl`, from 2025-11-25 |
| `instructions` | `instructions` on the initialize result, and on 2026-07-28's `server/discover` |

Repeatable `#[Icon]` attributes on the class go in a 2025-11-25 `serverInfo`.

<a id="protocol-versions"></a>
## Protocol Versions

`$supported_protocol_versions` lists the versions the server speaks. It defaults to `['2026-07-28']` alone, so a server meant for today's clients names the earlier versions it serves. A version must also be in `mcp.supported_protocol_versions` to be spoken at all.

During an `initialize` handshake the server answers in the version the client asked for when it supports it, and otherwise in the newest handshake version it supports; 2026-07-28 has no handshake. How the versions differ is on the [protocol versions](/docs/{{version}}/superconductor/protocol-versions) page.

<a id="capabilities"></a>
## Capabilities

Each capability is a property, written in the wire's own terms:

| Value | Meaning |
| --- | --- |
| `false` | Off |
| `true` or `[]` | On, sent as `{}` |
| `['key' => ...]` | On, with these keys, nested as the spec nests them |

```php
protected bool|array $tools = ['listChanged' => true];

protected bool|array $resources = ['subscribe' => true, 'listChanged' => true];

protected bool $completions = true;

protected bool $logging = true;

protected bool|array $tasks = [
    'list' => [],
    'cancel' => [],
    'requests' => ['tools' => ['call' => true]],
];
```

The server properties are `$tools`, `$prompts`, `$resources`, `$completions`, `$logging`, `$tasks`, `$extensions` and `$experimental`. A nested key switches on its parents, and a key the spec doesn't have throws, so a typo can't quietly switch a capability off. Each version is sent only what it has room for: `tasks` on a 2024-11-05 session is valid configuration that version simply leaves out.

To compute a capability instead, override its `{name}Config()` method, such as `toolsConfig()`, returning the array or null for off.

A request whose capability is off is refused with -32601 before anything runs, the way the spec asks.

<a id="what-a-server-offers"></a>
## What a Server Offers

A server offers the tools, prompts and resources whose names its methods return. Every tool, prompt and resource in the application is registered once; each server picks from them:

```php
public function tools(mixed ...$params): array
{
    return ['echo', 'shout', 'list_tools'];
}

public function prompts(mixed ...$params): array
{
    return ['greet'];
}

public function resources(mixed ...$params): array
{
    return ['echo://ponderings', 'echo://reverse/{text}'];
}
```

`tools()` and `prompts()` return names from `#[ToolCall]` and `#[PromptCall]`; `resources()` returns URIs and URI templates. A name nothing is registered under is a configuration mistake, answered with -32603 when the list is asked for.

<a id="logging"></a>
## Logging

With `$logging` on, a tool, prompt or resource can log to the client through its [request context](/docs/{{version}}/superconductor/tools#the-request-context). The client sets the level with `logging/setLevel`; until it does, every level is sent. On 2026-07-28 each request carries its own level instead.

<a id="request-timeouts"></a>
## Request Timeouts

A request the server sends waits `mcp.request_timeout` seconds, 60 by default, for its answer. Set `protected ?float $request_timeout` on the configuration to change it for one server. A request that times out is cancelled with `notifications/cancelled`, and a late answer is dropped.
