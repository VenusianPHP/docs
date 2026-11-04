# The HTTP Transports

`superconductor/web` serves your application's MCP servers over Streamable HTTP and HTTP+SSE from `php computer serve`, and connects your clients to remote servers over either.

<a id="introduction"></a>
## Introduction

Both transports are routes on [Venusian Serve](/docs/{{version}}/serve/serving), so the MCP endpoints run on the same event loop as the rest of your application. Each is its own option, with its own configuration file, sessions and routes:

| Transport | Route | Versions | Configuration |
| --- | --- | --- | --- |
| Streamable HTTP | `mcp/{server}` | 2025-03-26, 2025-06-18, 2025-11-25 as sessions; 2026-07-28 statelessly | `config/streamable.php` |
| HTTP+SSE | `GET mcp/{server}/sse`, `POST mcp/{server}/messages` | 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25 | `config/sse.php` |

`{server}` is a [server's](/docs/{{version}}/superconductor/servers) `#[ServerConfig]` name; an unknown one is 404.

```shell
composer require superconductor/web venusian/serve
php computer serve
```

<a id="streamable-http"></a>
## Streamable HTTP

POST, GET and DELETE all go to one endpoint. A POST whose body carries `_meta.io.modelcontextprotocol/protocolVersion`, or whose `MCP-Protocol-Version` header names no session version, is served as a stateless 2026-07-28 request; everything else, `initialize` first, goes the session way.

Every request is checked first: an `Origin` that `streamable.allowed_origins` doesn't allow is 403. A request without an `Origin` is always let through.

<a id="sessions"></a>
### Sessions

`initialize` opens a session, and its id comes back in `MCP-Session-Id`, which every later request carries. A missing session id is 400, one naming no open session 404, and an `MCP-Protocol-Version` other than the session's 400.

| Request | Answer |
| --- | --- |
| POST with a request | `application/json`, or an event stream when the answer comes later: the notifications sent while answering, then the response |
| POST with a notification or response | 202 |
| GET | The session's own event stream, for messages tied to no request, such as `list_changed` and `resources/updated` |
| GET with `Last-Event-ID` | Resumes the stream that event belongs to, from just after it |
| DELETE | Ends the session, 204 |

Every POST lists both `application/json` and `text/event-stream` in `Accept`, or it is 406. A 2025-03-26 session takes batches once started; other versions refuse them with 400. Each stream keeps its last `streamable.replay_events` events for resuming, and losing a connection doesn't cancel anything.

<a id="stateless-requests"></a>
### 2026-07-28

Each POST is one request, answered by its own server on the configuration all requests share, so a task one request starts is there for the next. The request's headers must match its body or it is 400 with -32020: `MCP-Protocol-Version` and `Mcp-Method` always, `Mcp-Name` on `tools/call`, `prompts/get` and `resources/read`, and the [mirrored](/docs/{{version}}/superconductor/protocol-versions#mirrored-headers) `Mcp-Param-*` headers on a `tools/call`.

| Answer | HTTP |
| --- | --- |
| -32601 | 404 |
| -32600, -32020, -32021, -32022, and -32602 for missing `_meta` | 400 |
| anything else | 200 |

An answer with nothing sent before it is `application/json`. Otherwise the request streams `text/event-stream`: its log and progress notifications, then the response, which ends it. `subscriptions/listen` streams its acknowledgement and the subscription's notifications. Closing a stream before its response cancels the request. When serve stops, each open subscription is ended with `notifications/cancelled` and a `complete` response before serve drains.

<a id="http-sse"></a>
## HTTP+SSE

A client GETs `mcp/{server}/sse` with `Accept: text/event-stream` and gets a stream whose first event, `endpoint`, names the session's message URL. It POSTs every message there; each POST answers 202 and the answers go out on the stream. The session negotiates with `initialize` and starts its server at `notifications/initialized`. A 2025-03-26 session takes batches once started. The stream, and the session with it, ends when the client disconnects or after `sse.session.idle_timeout` seconds without a message.

<a id="authentication"></a>
## Authentication

The routes are ordinary serve routes, so authenticate MCP requests with your own middleware, added to `streamable.middleware` or `sse.middleware`. On 2026-07-28, where every request shares its server's task store, a task belongs to the authenticated user's `getAuthIdentifier()`, and each caller sees only its own; a session's tasks are its own already. See [Tasks](/docs/{{version}}/superconductor/tasks).

<a id="connecting-to-a-server"></a>
## Connecting to a Server

A [client](/docs/{{version}}/superconductor/clients#connecting) connects with a definition in `mcp.mcp_servers`. Both take the URL and headers sent on every request, an `Authorization` header say:

```php
use SuperconductorMCP\SSE\ServerDefinitions\SSEServerDefinition;
use SuperconductorMCP\SSE\ServerDefinitions\StreamableServerDefinition;

'mcp_servers' => [
    'remote' => new StreamableServerDefinition('https://example.com/mcp', ['Authorization' => 'Bearer '.env('REMOTE_MCP_TOKEN')]),
    'older' => new SSEServerDefinition('https://example.com/sse'),
],
```

A Streamable HTTP client asks for 2026-07-28 with `server/discover` first, as over [stdio](/docs/{{version}}/superconductor/stdio#connecting-to-a-server), and falls back to `initialize`. An `initialize` answered with 400, 404 or 405 and no JSON-RPC answer tries the same URL as HTTP+SSE.

In a session, the client resumes a request's stream that ended early from its last event, and a 404 on the session starts a new one; requests in flight in the old session get an error saying so. On 2026-07-28 a `tools/call` refused with -32020 lists the tools again and is retried once with the headers they ask for. A transfer that never reaches the server fails the connection, and `ConnectionFailed` fires.

<a id="configuration"></a>
## Configuration

`config/streamable.php`:

| Key | Default | What it does |
| --- | --- | --- |
| `enabled` | `MCP_STREAMABLE_ENABLED`, `true` | Whether the endpoint is served |
| `route` | `mcp/{server}` | The endpoint |
| `middleware` | origin, server, era and session checks | Run on the endpoint |
| `allowed_origins` | `localhost`, `127.0.0.1` and `[::1]`, any port | `Origin` patterns let through |
| `session.idle_timeout` | `1800` | Seconds a session may go without a message, and with no stream connected, before it is forgotten |
| `replay_events` | `100` | Events each stream keeps for resuming |

`config/sse.php`:

| Key | Default | What it does |
| --- | --- | --- |
| `enabled` | `MCP_SSE_ENABLED`, `true` | Whether the routes are served |
| `middleware` | `valid-server` | Aliased as `mcp.<key>` and run on both routes |
| `routes.open_stream.route` | `mcp/{server}/sse` | The stream |
| `routes.open_stream.param_name` | `sessionId` | The query parameter naming the session |
| `routes.sse_messages.route` | `mcp/{server}/messages` | Where messages are posted |
| `session.idle_timeout` | `1800` | Seconds a session may go without a message |
