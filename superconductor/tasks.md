# Tasks

A task lets a client start a long tool call, get a handle back at once, and fetch the outcome later: a utility in 2025-11-25, and the `io.modelcontextprotocol/tasks` extension from 2026-07-28.

<a id="introduction"></a>
## Introduction

A tool opts into tasks with its `$task_support` (see [Tools](/docs/{{version}}/superconductor/tools#tasks)), and a server opts in through its `$tasks` capability:

```php
protected bool|array $tasks = [
    'list' => [],
    'cancel' => [],
    'requests' => ['tools' => ['call' => true]],
];
```

Each server configuration keeps its tasks in a `TaskStore`. A task records its status (`working`, `completed`, `failed`, `cancelled`), its result once settled, and its time to live: the client's, or one hour. Expired tasks are dropped, and clients are asked to poll every second.

A task belongs to whoever created it, as the transport authenticated them. Every task call sees only the caller's own tasks, and treats anyone else's as unknown.

<a id="2025-11-25"></a>
## 2025-11-25

A `tools/call` carrying task metadata, on a server that offers `tasks.requests.tools.call`, returns `CreateTaskResult` at once. A sync tool's task is already completed; an [async tool's](/docs/{{version}}/superconductor/tools#async-tools) is working until it finishes. A task request to a tool that forbids tasks, or a plain call to one that requires them, is -32601. Every status change sends `notifications/tasks/status`.

| Method | Answers |
| --- | --- |
| `tasks/get` | The task; an unknown or expired one is -32602 |
| `tasks/result` | The outcome of the call the task ran, waiting until it settles; a failed call's error comes back as the error, and a cancelled task's result is -32602 |
| `tasks/list` | The caller's tasks, oldest first, when the server declares `tasks.list` |
| `tasks/cancel` | Cancels a working task, when the server declares `tasks.cancel`; a settled one is -32602. The work itself isn't interrupted |

<a id="2026-07-28"></a>
## 2026-07-28

From 2026-07-28 tasks are an extension, declared under `$extensions`. The server decides which calls run as tasks: a tool that requires them always does, and one that allows them does for a client whose request declared the extension. A tool that requires tasks refuses a client that didn't declare it with -32021. The answer is `CreateTaskResult` with `resultType: "task"`.

| Method | Answers |
| --- | --- |
| `tasks/get` | The task with what its status carries: `inputRequests` while `input_required`, `result` once `completed`, `error` once `failed` |
| `tasks/update` | Answers outstanding input requests; once every one is answered, the tool runs again with the answers |
| `tasks/cancel` | Acknowledged with an empty result |

There is no `tasks/list` or `tasks/result`. An unknown task is -32602. A tool that asks for [input](/docs/{{version}}/superconductor/protocol-versions#multi-round-trip-requests) as soon as it is called gets `InputRequiredResult` instead of a task, so that exchange ends before any task exists. Clients following a task through `subscriptions/listen` get `notifications/tasks` as it changes.
