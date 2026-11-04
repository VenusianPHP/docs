# Overview

Superconductor MCP brings the Model Context Protocol to a Venusian application: MCP servers and MCP clients, with tools, prompts, resources and tasks, in every protocol version from 2024-11-05 through 2026-07-28.

<a id="introduction"></a>
## Introduction

Superconductor is three packages. `superconductor/core` holds the protocol: the schema of every MCP version, the servers and clients, and the tools, prompts and resources they offer. The transports are their own packages, so an application installs only the ones it speaks:

| Package | Holds |
| --- | --- |
| [`superconductor/core`](https://github.com/superconductor-mcp/core) | Schemas, server and client configurations, tools, prompts, resources, tasks, routing |
| [`superconductor/stdio`](https://github.com/superconductor-mcp/stdio) | Servers your app runs as a process, and clients that launch one |
| [`superconductor/web`](https://github.com/superconductor-mcp/web) | Servers on `php computer serve` over HTTP+SSE and Streamable HTTP, and clients of remote servers |

Want an AI assistant to drive the robot arm your app already controls? Write a tool class, name it on a server, and the assistant can call it. Want your app to call out to someone else's MCP server? Configure a client, connect, and send it requests from your own [event loop](/docs/{{version}}/framework/architecture-concepts/event-loop).

<a id="protocol-versions"></a>
## Protocol Versions

Each MCP version has its own hand-written schema tree, mirroring that version's `schema.ts` class for class. A server answers in whichever version its client speaks, and a client settles on the newest one both sides support, so a tool is written once and serves every version. What changes between versions, including the stateless 2026-07-28, is on the [protocol versions](/docs/{{version}}/superconductor/protocol-versions) page.

| Version | Handshake | stdio | HTTP |
| --- | --- | --- | --- |
| 2024-11-05 | `initialize` | `mcp:cli-legacy` | HTTP+SSE |
| 2025-03-26 | `initialize` | `mcp:cli-legacy` | HTTP+SSE, Streamable HTTP |
| 2025-06-18 | `initialize` | `mcp:cli-legacy` | HTTP+SSE, Streamable HTTP |
| 2025-11-25 | `initialize` | `mcp:cli-legacy` | HTTP+SSE, Streamable HTTP |
| 2026-07-28 | none | `mcp:cli` | Streamable HTTP |

<a id="where-to-next"></a>
## Where to Next

- [Installation](/docs/{{version}}/superconductor/installation) adds the packages and the `App\Mcp` folders.
- [Servers](/docs/{{version}}/superconductor/servers) declares what a server offers; [tools](/docs/{{version}}/superconductor/tools), [prompts](/docs/{{version}}/superconductor/prompts) and [resources](/docs/{{version}}/superconductor/resources) are what it offers.
- [Clients](/docs/{{version}}/superconductor/clients) connects your app to other MCP servers.
- [The stdio transport](/docs/{{version}}/superconductor/stdio) and [the HTTP transports](/docs/{{version}}/superconductor/web) put either on the wire.
