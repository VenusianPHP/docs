# Resources

A resource is data a server lets clients read by URI: one class per URI, or a template class answering every URI that fits a pattern.

<a id="introduction"></a>
## Introduction

Resources and templates live in `App\Mcp\Resources`, and a [server](/docs/{{version}}/superconductor/servers#what-a-server-offers) offers them by returning their URIs and URI templates from `resources()`.

A resource at one URI extends `Fabricate\Mechanism\Resource` and carries `#[ResourceCall(uri, name, description, mimeType)]`:

```php
<?php

namespace App\Mcp\Resources;

use Fabricate\Contracts\Mechanism\Attributes\ResourceCall;
use Fabricate\Mechanism\Resource;

#[ResourceCall('echo://ponderings', 'ponderings', 'Every answer ponder has come back with.', 'text/plain')]
class PonderingsResource extends Resource
{
    /** @var list<string> */
    private static array $ponderings = [];

    public static function record(string $pondering): void
    {
        self::$ponderings[] = $pondering;
        static::updated();
    }

    public function read(): string
    {
        return implode("\n", self::$ponderings);
    }
}
```

A template extends `Fabricate\Mechanism\ResourceTemplate` and carries `#[ResourceTemplateCall(uriTemplate, name, description, mimeType)]`:

```php
#[ResourceTemplateCall('echo://reverse/{text}', 'reverse', 'Any text, read back to front.', 'text/plain')]
class ReverseTemplate extends ResourceTemplate
{
    public function read(string $uri, string $text): string
    {
        return strrev($text);
    }
}
```

Templates use RFC 6570 simple expansion: `{name}` fills one path segment and `{+name}` may span several. Values are URL-decoded before `read()` gets them.

<a id="reading"></a>
## Reading

`read()` is called through the container. It can ask for `$uri`, a template's variables by name, the server configuration, `$protocol_version` and the [request context](/docs/{{version}}/superconductor/tools#the-request-context). It returns:

| Returned | Becomes |
| --- | --- |
| a string | the resource's text, with its declared MIME type |
| the version's own contents objects | those contents |
| a list of either | each of them |

`resources/read` reads the resource with that exact URI, or else the first offered template the URI fits. A URI nothing reads is -32002 with `data.uri` through 2025-11-25, and -32602 on 2026-07-28. A resource can set `protected bool $async = true` and answer later, as an [async tool](/docs/{{version}}/superconductor/tools#async-tools) does.

<a id="metadata"></a>
## Metadata

`#[ResourceCall]` also takes a `title` and the resource's `size` in bytes; `#[ResourceTemplateCall]` takes a `title`. `#[ResourceAnnotations(audience, priority, lastModified)]` adds annotations. Each version is sent what it has room for: `size`, `audience` and `priority` in every version, `title` from 2025-06-18, `lastModified` and repeatable `#[Icon]` attributes from 2025-11-25.

<a id="completion"></a>
## Completion

A template suggests values for its variables by overriding the static `complete($argument, $value, $context)`, which returns a `CompletionResult` as a [prompt's](/docs/{{version}}/superconductor/prompts#completion) does. An unknown template or variable is -32602.

<a id="subscriptions-and-changes"></a>
## Subscriptions and Changes

On a server declaring `resources.subscribe`, a client subscribes to a URI with `resources/subscribe`, up to 2025-11-25; 2026-07-28 subscribes through `subscriptions/listen` instead. When a resource's data changes, tell its subscribers:

```php
PonderingsResource::updated();

ReverseTemplate::updated('echo://reverse/saturn');
```

Every session subscribed to that URI gets `notifications/resources/updated`. When the set of resources changes, the static `listChanged()` on any resource sends `notifications/resources/list_changed` to sessions whose server declared `resources.listChanged`.
