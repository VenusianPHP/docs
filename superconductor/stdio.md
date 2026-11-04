# The stdio Transport

`superconductor/stdio` runs your application's MCP servers as a process an MCP host launches, and connects your clients to stdio servers your application launches.

<a id="introduction"></a>
## Introduction

Over stdio, each JSON-RPC message is one line: the client writes to the server's stdin and reads its stdout. The package adds two [sketches](/docs/{{version}}/framework/the-basics/sketches), one per era of the protocol, and a server definition for clients.

```shell
composer require superconductor/stdio
```

<a id="serving"></a>
## Serving

Run a [server](/docs/{{version}}/superconductor/servers) by its `#[ServerConfig]` name through `php rocket`:

| Sketch | Versions |
| --- | --- |
| `php rocket mcp:cli-legacy {server}` | 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25 |
| `php rocket mcp:cli {server}` | 2026-07-28 |

An MCP host launches the command itself. A host's configuration names PHP, your application's `rocket` file and the sketch:

```json
{
    "mcpServers": {
        "echo": {
            "command": "php",
            "args": ["/path/to/your-app/rocket", "mcp:cli-legacy", "echo"]
        }
    }
}
```

<a id="the-legacy-sketch"></a>
### mcp:cli-legacy

`mcp:cli-legacy` runs the `initialize` handshake, answering in the version the host asked for when the server supports it, then starts the server in that version. Whatever arrives in the same read as `notifications/initialized` goes to the started server. A started 2025-03-26 session also takes batches.

<a id="the-modern-sketch"></a>
### mcp:cli

`mcp:cli` serves 2026-07-28, which has no handshake: one server answers each request on its own, as the [protocol versions](/docs/{{version}}/superconductor/protocol-versions#2026-07-28) page describes. Everything goes out on stdout oldest first, with answers from async work arriving as mail. Batches are refused with -32600. Closing stdin closes the server, which ends each open subscription first, and the process exits once those messages are written.

<a id="connecting-to-a-server"></a>
## Connecting to a Server

A `StdioServerDefinition` names a server's command, arguments and extra environment variables; listed in `mcp.mcp_servers`, a [client](/docs/{{version}}/superconductor/clients#connecting) connects to it:

```php
use SuperconductorMCP\STDIO\ServerDefinitions\StdioServerDefinition;

'mcp_servers' => [
    'filesystem' => new StdioServerDefinition('npx', ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'], ['DEBUG' => '0']),
],
```

`connect()` launches the server and settles a version with it before returning:

| Client supports | Server | Outcome |
| --- | --- | --- |
| 2026-07-28 | answers `server/discover` listing 2026-07-28 | 2026-07-28, no `initialize` |
| 2026-07-28 | answers with a modern error (-32020, -32021, -32022) | fails, naming the versions it supports |
| 2026-07-28 and a handshake version | any other error, or silence for `mcp.clients.initialize_timeout` seconds | falls back to `initialize` |
| only 2026-07-28 | is legacy | fails |
| no 2026-07-28 | | `initialize` straight away |

`initialize` carries the newest handshake version the client supports, and an answer in a version it doesn't support fails the connection. `$connection->server` holds what the server said about itself: its `InitializeResult` or `DiscoverResult`. The server's stderr is read and dropped.

<a id="shutdown-and-restarts"></a>
### Shutdown and Restarts

`close()` closes the server's stdin and gives it two seconds to exit, then sends `SIGTERM` and waits again, then `SIGKILL`.

A 2026-07-28 server that exits on its own is launched again, keeping the same client; requests it was answering get an error saying so. A relaunched server that exits before writing a line is not launched a third time. That, a command that cannot start, and any other server exiting fail the connection: every request in flight gets the reason as its error, `failure()` says it, and `ConnectionFailed` fires.

<a id="configuration"></a>
## Configuration

`config/stdio.php`:

| Key | Default | What it does |
| --- | --- | --- |
| `server_pipe_name` | `mcp.stdio.server` | The name the server's stdin pipe registers under on the event loop |
| `read_chunk_size` | `65536` | Bytes read from stdin per read |
