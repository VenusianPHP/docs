# Routing

Every MCP request a server or client receives is routed by its method to a procedure class, after passing version, role and capability checks.

<a id="introduction"></a>
## Introduction

Incoming messages are read in two stages. The transport classifies the JSON-RPC envelope without any protocol version: a request, notification, response, error, batch, or an invalid message ready to answer with its error. The message is then built as the schema class of the session's version, field by field; a message that doesn't fit is answered with an error naming the member at fault. Requests then go to the procedure router.

<a id="routes"></a>
## Routes

Routes live in `routes/mcp.php`: the application's, or the package's when the application has none ([publishing them](/docs/{{version}}/superconductor/installation#mcp-routes)). `ProcedureRouterFacade` is a plain static class forwarding to the `ProcedureRouter` in the container:

```php
use Fabricate\Core\Routing\ProcedureRouterFacade as Route;
use Fabricate\Core\Rpc\Procedures\Ping\PingProcedure;
use Fabricate\Core\Rpc\Procedures\Tools\ToolsProcedure;

Route::procedure('ping', PingProcedure::class);

Route::group('tools', function () {
    Route::procedure('list', ToolsProcedure::class.'@list');
    Route::procedure('call', ToolsProcedure::class.'@call');
});
```

A route names a class, whose `handle()` runs, or `Class@method`. `group()` prefixes its routes' methods, so the two above are `tools/list` and `tools/call`. A closure works too.

<a id="procedures"></a>
## Procedures

A procedure method takes the request, the configuration of the server or client that received it, and the protocol version, and returns that version's result class:

```php
#[CompatibleVersions('2024-11-05', '2025-03-26', '2025-06-18', '2025-11-25')]
class PingProcedure extends Procedure
{
    public function handle(PingRequest $request, EntityConfiguration $entity_configuration, string $protocol_version): EmptyResult
    {
        return new PingResult();
    }
}
```

`#[CompatibleVersions]` on the method, or else the class, lists the versions the procedure answers; a procedure without one is never reached. `#[RequiresCapability('resources.subscribe')]` names the capability the receiving configuration must declare.

<a id="checks"></a>
## Checks

A request passes these before its procedure runs, the configuration's version first:

| Check | Refuses |
| --- | --- |
| Configuration version | A version the configuration doesn't support: -32602 on a handshake version, -32022 otherwise |
| Route | An unknown method, including `initialize`: -32601 |
| Version | A method the version doesn't have, such as `ping` on 2026-07-28: -32601 |
| Role | A client sending `sampling/createMessage`, or a server sending `tools/call`: -32601 |
| Capability | `tools/list` with `tools` off: -32601 |
| Schema | A request object from another version's schema: -32600 |

A capability a version can't declare isn't held against it: 2024-11-05 has no `completions` capability, but `completion/complete` passes.

The procedure's answer is checked too: it must be a result from the session version's schema that the method can answer with, so a replaced `tools/list` route can't return a `CallToolResult`. A `CreateTaskResult` also needs a request with task metadata and the matching `tasks.requests` capability.

<a id="errors"></a>
## Errors

| Situation | Answer |
| --- | --- |
| A procedure throws `SuperconductorMCPException` with a code the version has | That code and message |
| Any other exception, or an answer that fails its check | Reported, and -32603 `Internal error` |
| `CancelledException` | Rethrown, so the event loop can unwind the request's fiber |

Throw `Fabricate\Contracts\Core\SuperconductorMCPException` to refuse a request with a specific error; its `data` argument goes into the error:

```php
throw new SuperconductorMCPException('No such sensor.', RPCErrorCode::INVALID_PARAMS->value, data: ['sensor' => $name]);
```
