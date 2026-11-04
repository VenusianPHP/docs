# Clients

A client configuration declares how your application talks to other MCP servers: the versions it speaks, the capabilities it offers them, and the classes that answer their requests.

<a id="introduction"></a>
## Introduction

An MCP client is a class extending `Fabricate\Client\ClientConfiguration` in `App\Mcp\Clients`, carrying a `#[ClientConfig(name, description, version)]` attribute:

```php
<?php

namespace App\Mcp\Clients;

use App\Mcp\Roots\ProjectRoots;
use Fabricate\Client\ClientConfiguration;
use Fabricate\Contracts\Mechanism\Attributes\ClientConfig;

#[ClientConfig('curious-client', 'Asks servers questions.', '1.0.0')]
class CuriousClient extends ClientConfiguration
{
    protected array $supported_protocol_versions = ['2025-06-18', '2025-11-25', '2026-07-28'];

    protected bool|array $roots = ['listChanged' => true];

    public function roots(): ?string
    {
        return ProjectRoots::class;
    }
}
```

As on a [server](/docs/{{version}}/superconductor/servers#protocol-versions), `$supported_protocol_versions` defaults to `['2026-07-28']` alone, and `$request_timeout` overrides `mcp.request_timeout`. `#[ClientConfig]` also takes `title` and `websiteUrl`, sent as the client's `clientInfo` where the version has them.

<a id="capabilities"></a>
## Capabilities

The client capabilities are `$roots`, `$sampling`, `$elicitation`, `$tasks`, `$extensions` and `$experimental`, written as a server's are: `false` for off, `true` or `[]` for on, an array for on with those keys. `$elicitation = ['form' => true]` accepts form elicitation only; an empty declaration means form.

Superconductor never samples a model, asks a user or picks roots itself. Each of those capabilities names a class of yours that does:

| Capability | Method | Extends | Returns |
| --- | --- | --- | --- |
| `$roots` | `roots()` | `Fabricate\Client\Roots` | the version's `ListRootsResult` |
| `$sampling` | `sampling()` | `Fabricate\Client\Sampling` | the version's `CreateMessageResult` |
| `$elicitation` | `elicitation()` | `Fabricate\Client\Elicitation` | the version's `ElicitResult` |

Each class implements `handle()`, called through the container with the request, the client configuration, `$protocol_version` and, if asked for, the `RequestContext`. It builds the result class of the session's version:

```php
class ProjectRoots extends Roots
{
    public function handle(string $protocol_version): ListRootsResult
    {
        $uri = 'file://'.base_path();

        return match($protocol_version) {
            '2025-06-18' => new V20250618\Messaging\Roots\ListRootsResult([new V20250618\Capabilities\Roots\Root($uri, 'project')]),
            '2025-11-25' => new V20251125\Messaging\Roots\ListRootsResult([new V20251125\Capabilities\Roots\Root($uri, 'project')]),
            '2026-07-28' => new V20260728\Messaging\Roots\ListRootsResult([new V20260728\Capabilities\Roots\Root($uri, 'project')]),
        };
    }
}
```

To refuse, throw a `SuperconductorMCPException` with a code the version knows; a user who rejects a sampling request is `SamplingErrorCode::USER_REJECTED`. A class with `protected bool $async = true` may return nothing and call `finish()` or `fail()` later, as an [async tool](/docs/{{version}}/superconductor/tools#async-tools) does. Its answer arrives as `Fabricate\Mechanism\Mail\OutboundMessage` [loop mail](/docs/{{version}}/framework/the-basics/loop-mail), and whatever handles your loop's mail passes it to the connection's `deliver($mail)`, which sends it when the mail belongs to that connection's session. Under `php computer serve` the loop hands mail on as signals:

```php
app('signals')->listen(OutboundMessage::class, fn (OutboundMessage $mail) => $connection->deliver($mail));
```

Before your class runs, the client applies the spec's checks: a root that isn't an absolute `file://` URI without `.` or `..` segments is left out, an elicitation in a mode the client didn't declare is -32602, and so is a sampling request with `tools` from a client without `sampling.tools`. A client that declares `roots` but names no class answers with no roots.

When the roots change, `Roots::changed()` sends `notifications/roots/list_changed` from every open client that declared `roots.listChanged`.

<a id="connecting"></a>
## Connecting

The servers a client can reach are listed by name in `mcp.mcp_servers`, each a definition from a transport package:

```php
use SuperconductorMCP\SSE\ServerDefinitions\StreamableServerDefinition;
use SuperconductorMCP\STDIO\ServerDefinitions\StdioServerDefinition;

'mcp_servers' => [
    'filesystem' => new StdioServerDefinition('npx', ['-y', '@modelcontextprotocol/server-filesystem', '/tmp']),
    'remote' => new StreamableServerDefinition('https://example.com/mcp', ['Authorization' => 'Bearer '.env('REMOTE_MCP_TOKEN')]),
],
```

`connect()` opens a connection as one of your client configurations, running the transport's handshake:

```php
$connection = config('mcp.mcp_servers.filesystem')->connect(app('mcp.clients')->get('curious-client'));

if(! $client = $connection->client()) {
    throw new RuntimeException($connection->failure());
}
```

`client()` is the `MCPClient`, built in the version the handshake settled on, or null when the connection failed, with the reason in `failure()`. The transport pages say how each one negotiates: [stdio](/docs/{{version}}/superconductor/stdio#connecting-to-a-server) and [HTTP](/docs/{{version}}/superconductor/web#connecting-to-a-server). `$connection->close()` ends it.

<a id="sending-requests"></a>
## Sending Requests

`request($request, $id, $then)` sends a request built from the schema classes of the client's version, `$client->active_protocol_version`, and returns its id. From 2025-11-25 the request carries its own id; earlier versions take it as `$id`. The closure gets the response's result or `MCPError`:

```php
use Fabricate\Contracts\Schema\RequestId;
use Fabricate\Schema\V20251125;

$id = new RequestId('tools');

$client->request(new V20251125\Messaging\Tools\ListToolsRequest($id), $id, function ($response) {
    // a V20251125 ListToolsResult, or an MCPError
});
```

The client lives on the application's [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop): the request goes out and its answer comes back while the loop runs. A request left unanswered for `mcp.request_timeout` seconds is cancelled, its closure dropped, and `RequestTimedOut` fires.

On 2026-07-28, when a server answers a tool call, prompt or resource read with `InputRequiredResult`, the client fulfils every input request from your roots, sampling and elicitation classes, then retries the request with the answers; the closure gets the retry's final answer.

<a id="signals"></a>
## Signals

What the client hears outside a closure arrives as [signals](/docs/{{version}}/framework/digging-deeper/signals):

| Signal | Fires when | Carries |
| --- | --- | --- |
| `Fabricate\Client\Signals\ResponseReceived` | A response arrives that no closure waits on | session id, request id, method, response |
| `Fabricate\Client\Signals\NotificationReceived` | The server sends any notification | session id, notification |
| `Fabricate\Client\Signals\ConnectionFailed` | The connection breaks after its handshake | session id, reason |
| `Fabricate\Mechanism\Signals\RequestTimedOut` | A request times out | session id, request id, method |

```php
app('signals')->listen(NotificationReceived::class, function (NotificationReceived $signal) {
    app('log')->info($signal->session_id.': '.$signal->notification::class);
});
```

When a connection breaks, every request still in flight is answered with an `MCPError` carrying the reason, so nothing waits on an answer that can't come.
