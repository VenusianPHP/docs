# Protocol Versions

Superconductor speaks every MCP version from 2024-11-05 through 2026-07-28. Each has its own schema classes; this page covers how a version is chosen, what each adds, and the stateless 2026-07-28.

<a id="introduction"></a>
## Introduction

Every version has a hand-written tree of schema classes under `Fabricate\Schema`, one class per type in that version's `schema.ts`: `V20241105`, `V20250326`, `V20250618`, `V20251125` and `V20260728`. Tools, prompts and resources are written once; their definitions and results are built in the session's version, and each version is sent only the fields it has.

| Version | Adds |
| --- | --- |
| 2024-11-05 | The baseline: tools, prompts, resources, sampling, roots, logging, completion |
| 2025-03-26 | Audio content, tool annotations, batches, Streamable HTTP |
| 2025-06-18 | Elicitation, resource links, tool output schemas and structured content, `title` fields; batches removed |
| 2025-11-25 | Tasks, icons, tool use in sampling, URL elicitation, `description` and `websiteUrl` on implementations |
| 2026-07-28 | No handshake: per-request metadata, `server/discover`, multi round-trip requests, `subscriptions/listen`, tasks as an extension |

`config/mcp.php`'s `supported_protocol_versions` lists the versions the application speaks at all, and each server and client configuration its own within those.

<a id="choosing-a-version"></a>
## Choosing a Version

Up to 2025-11-25 a session starts with `initialize`. The client asks for the newest version it supports; the server answers in that version when it supports it too, and otherwise in the newest it does. The session keeps that version until it ends, and every message after is read as that version's classes.

2026-07-28 has no handshake: each request names its version in `_meta`. A client that supports 2026-07-28 asks the server with `server/discover` first, and falls back to `initialize` when the server doesn't speak it; see [stdio](/docs/{{version}}/superconductor/stdio#connecting-to-a-server) and [HTTP](/docs/{{version}}/superconductor/web#connecting-to-a-server).

<a id="2026-07-28"></a>
## 2026-07-28

A 2026-07-28 server answers each request on its own. A request without `_meta.io.modelcontextprotocol/protocolVersion` or `clientCapabilities` is -32602, and one naming a version the server doesn't support is -32022 with the supported versions. `initialize`, `ping`, `logging/setLevel` and `resources/subscribe` are unknown methods.

- `server/discover` answers the versions, capabilities and instructions the server has, and every result carries `serverInfo` in its `_meta` when the server names a version.
- A request carries its own log level and progress token in `_meta`; [the request context](/docs/{{version}}/superconductor/tools#the-request-context) logs and reports progress for it.
- List results are marked not cacheable.
- Tasks are the `io.modelcontextprotocol/tasks` extension; see [Tasks](/docs/{{version}}/superconductor/tasks#2026-07-28).

<a id="multi-round-trip-requests"></a>
### Multi Round-Trip Requests

A tool, prompt or resource that needs the client's input returns `Fabricate\Mechanism\InputRequired`: elicitation, sampling or roots requests keyed by name, and state to get back on the retry. The client answers them and retries; the retry calls `handle()` or `read()` again with `$input_responses` and `$request_state`:

```php
public function handle(?array $input_responses = null, mixed $request_state = null): string|InputRequired
{
    if($input_responses === null) {
        // $confirm: a V20260728 ElicitRequest asking the user to confirm.
        return new InputRequired(['confirm' => $confirm], ['step' => 1]);
    }

    // ...
}
```

Each request must be of a kind the client declared, or the call is -32021 naming what's missing. The state goes to the client sealed with an HMAC under the application key, bound to the method and the tool, prompt or URI, and valid for `mcp.request_state.ttl` seconds; a retry whose state was altered, expired or issued for another request is -32602. Earlier versions have no such exchange, so asking for input there is an internal error.

<a id="subscriptions"></a>
### Subscriptions

`subscriptions/listen` is how a 2026-07-28 client hears about changes. The server first sends `notifications/subscriptions/acknowledged` with what it agreed to: list changes for capabilities that declared `listChanged`, resource URIs when it declared `resources.subscribe`, and task ids for a client that declared the tasks extension. The request stays open, and the subscription gets only what it agreed to. `notifications/cancelled` from the client ends it; a server that closes ends each open subscription with `notifications/cancelled` and a `complete` result.

<a id="mirrored-headers"></a>
### Mirrored Headers

Over Streamable HTTP, a tool argument can be mirrored into a request header so a proxy can route on it without reading the body. `#[Argument(header: 'Region')]` on an `int`, `string` or `bool` parameter adds `x-mcp-header: Region` to the tool's input schema, and the client sends the value as `Mcp-Param-Region`:

```php
public function __construct(
    #[Argument('Where to look.', header: 'Region')] public readonly string $region,
) {}
```

Header names must be HTTP tokens, unique within the tool ignoring case, or the tool is refused when it registers. The server checks every mirrored header against the body; see [the HTTP transports](/docs/{{version}}/superconductor/web#stateless-requests).
