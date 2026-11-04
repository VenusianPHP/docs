# Installation

Add Superconductor MCP to a Venusian application: `superconductor/core`, the transports it speaks, its configuration and the `App\Mcp` folders it discovers servers, clients, tools, prompts and resources in.

<a id="installing-superconductor"></a>
## Installing Superconductor

Require the core package and each transport you want with Composer:

```shell
composer require superconductor/core
composer require superconductor/stdio
composer require superconductor/web
```

Nothing needs registering by hand. Each package's `composer.json` names its service provider under `extra.venusian.providers`, so package discovery registers it:

| Package | Provider | Merges |
| --- | --- | --- |
| `superconductor/core` | `Fabricate\Core\Providers\SuperconductorMCPServiceProvider` | `config/mcp.php` |
| `superconductor/stdio` | `SuperconductorMCP\STDIO\Providers\STDIOServiceProvider` | `config/stdio.php` |
| `superconductor/web` | `SuperconductorMCP\SSE\Providers\SSEServiceProvider` | `config/sse.php`, `config/streamable.php` |

The HTTP transports are routes, answered by [Venusian Serve](/docs/{{version}}/serve/installation), so an application that installs `superconductor/web` also needs `venusian/serve` 0.11.1 or newer.

<a id="the-application-folders"></a>
## The Application Folders

The core provider discovers every concrete class in five namespaces when the application boots, so a class is available by being in its folder:

| Namespace | Holds |
| --- | --- |
| `App\Mcp\Servers` | [Server configurations](/docs/{{version}}/superconductor/servers) |
| `App\Mcp\Clients` | [Client configurations](/docs/{{version}}/superconductor/clients) |
| `App\Mcp\Tools` | [Tools](/docs/{{version}}/superconductor/tools) |
| `App\Mcp\Prompts` | [Prompts](/docs/{{version}}/superconductor/prompts) |
| `App\Mcp\Resources` | [Resources and resource templates](/docs/{{version}}/superconductor/resources) |

Each namespace is a `discovery_namespace` key in `config/mcp.php` and may be changed, as long as it stays under the application's own namespace; the folder follows from it.

<a id="configuration"></a>
## Configuration

`config/mcp.php` holds the protocol settings. To change one, create `config/mcp.php` in your application: each top-level key you set there replaces the package's whole, so copy a nested array such as `clients` entire when changing one of its keys.

| Key | Default | What it does |
| --- | --- | --- |
| `supported_protocol_versions` | all five | The versions this application speaks at all; a configuration's own list is narrowed to these |
| `max_batch_size` | `100` | Most messages one JSON-RPC batch may carry |
| `servers.discovery_namespace` | `App\Mcp\Servers` | Where server configurations are discovered |
| `clients.discovery_namespace` | `App\Mcp\Clients` | Where client configurations are discovered |
| `clients.initialize_timeout` | `30` | Seconds a client waits for the server to answer its handshake |
| `mcp_servers` | `[]` | The servers clients can connect to, by name; see [Clients](/docs/{{version}}/superconductor/clients#connecting) |
| `tools.discovery_namespace` | `App\Mcp\Tools` | Where tools are discovered |
| `prompts.discovery_namespace` | `App\Mcp\Prompts` | Where prompts are discovered |
| `resources.discovery_namespace` | `App\Mcp\Resources` | Where resources and resource templates are discovered |
| `request_timeout` | `60` | Seconds a sent request waits for its response before it is cancelled |
| `request_state.ttl` | `300` | Seconds a 2026-07-28 `requestState` stays valid for its retry |
| `pagination.page_size` | `50` | Items per page of a list result |

The transports' own settings are on [the stdio transport](/docs/{{version}}/superconductor/stdio#configuration) and [the HTTP transports](/docs/{{version}}/superconductor/web#configuration) pages.

<a id="mcp-routes"></a>
## The MCP Routes

Every MCP method is routed to a procedure class, the way HTTP routes reach controllers. The core provider loads the application's `routes/mcp.php` if it has one, and the package's own otherwise. To customise them, publish the package's file into your application first:

```shell
php computer vendor:publish --tag=mcp-routes
```

An application's `routes/mcp.php` replaces the package's entirely, so keep every route you still want. [Routing](/docs/{{version}}/superconductor/routing) covers the routes and the checks a request passes before its procedure runs.
