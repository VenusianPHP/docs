# Async Web APIs

Keep the event loop free while a request waits on a database, the filesystem, a mail server or an image: serve's opt-in async variants.

## Introduction

Under `php computer serve`, many requests share one event loop. A blocking call, such as a query or an SMTP conversation, holds the whole loop until it returns. Serve's async variants hand that work to a [worker pool](/docs/{{version}}/framework/architecture-concepts/event-loop#worker-pools) or the event loop instead, so the request waits without holding the loop.

Every async variant is opt-in, exactly as the framework's own are. A plain call stays blocking, and serve never guesses from context: you choose the async variant by calling it, or by a config setting. Where a method takes a `$pool`, pass `'thread'` or `'process'` to name a worker pool, or `null` for the framework's choice: thread workers when they are enabled, process workers otherwise.

> [!NOTE]
> A variant that waits "in place" calls `wait()` on its promise. Inside a task the event loop runs, as every request under `php computer serve` is, that wait suspends only the request; called outside the loop, it blocks as the plain call would.

<a id="sessions"></a>
## Sessions

Turn on async session I/O for every request in `config/session.php`:

```php
'async' => (bool) env('SESSION_ASYNC', false),

'async_pool' => env('SESSION_ASYNC_POOL'),
```

`StartSession` then reads and writes the session through the store's async variant. You can also use it directly: `$store->async($pool)` answers `start()` and `save()` with promises. The file and database handlers offload to the pool; the cache handler uses the cache's async operations; the array and cookie handlers answer at once.

<a id="route-model-binding"></a>
## Route Model Binding

Set `binding_via` in `config/routing.php` to run the query that binds an Instrument model to a route parameter on a worker pool:

```php
'binding_via' => env('ROUTING_BINDING_VIA'),
```

`null`, the default, runs it in place. `auto`, `process` or `thread` offloads it and waits in place. Models that resolve their own binding (`UrlRoutable`) are not affected, and a model's `resolveRouteBindingQuery()` is honoured. Naming a pool that is not enabled fails the request rather than running the query in place.

<a id="rate-limiting"></a>
## Rate Limiting

Set `throttle_async` in `config/routing.php` and the `throttle` middleware reads and writes its counters through the framework's async rate limiter:

```php
'throttle_async' => (bool) env('ROUTING_THROTTLE_ASYNC', false),
```

The limiter's cache store must have async operations, or the request fails. The Redis throttle middleware keeps its own limiter and is not affected.

<a id="authentication"></a>
## Authentication

User providers have an async variant answering with promises:

```php
$users = app('auth')->createUserProvider('users')->via();

$user = $users->retrieveById($id)->wait();
```

The database provider offloads all five calls. The Instrument provider offloads its three lookups as queries and saves the user for `updateRememberToken()` and `rehashPasswordIfRequired()` with the model's `saveAsync()`, so its events and timestamps run in the request and only the SQL runs in a worker. Password reset token repositories have `via($pool)` (database) and `async()` (cache).

<a id="validation"></a>
## Validation

`Validator::async($pool)` validates a copy of the validator in a loop task and returns a promise of `validate()`'s result, rejected with its `ValidationException`:

```php
$validated = validator($request->all(), [
    'email' => 'required|email|unique:users',
    'password' => ['required', Password::min(12)->uncompromised()],
])->async()->wait();
```

In that copy, `unique` and `exists` checks run on the worker pool, and the breached-password check sends its request on the event loop.

<a id="mail"></a>
## Mail

`Mailer::via($pool)` returns a mailer whose `send()` and `sendNow()` answer with promises:

```php
Mail::mailer()->via()->send(new OrderShipped($order))->wait();
```

The message is built, and the `MessageSending` and `MessageSent` events fire, in the request; the message itself goes to a worker, which builds the transport from the mailer's configuration and sends it. Attachments cross whole, streams included. A mailer given a transport object rather than built from configuration, or using the `array` transport, cannot be offloaded and says so.

<a id="notifications"></a>
## Notifications

`ChannelManager::async($pool)` answers `send()` and `sendNow()` with promises:

```php
app(ChannelManager::class)->async()->sendNow($user, new InvoicePaid($invoice))->wait();
```

The database channel saves the notification with the model's `saveAsync()`, and the mail channel sends through a worker, as [Mail](#mail) does.

<a id="images"></a>
## Images

`ImageManager::via($pool)` returns a manager whose images load, process and store through the worker pool, each step waited on in place; `Image::via($pool)` does the same for one image:

```php
$path = Image::via()->fromUpload($request->file('avatar'))
    ->cover(256, 256)
    ->toWebp()
    ->store('avatars', 'public');
```

The image pipeline runs on a worker, which builds the named driver itself. Drivers registered with `extend()` and drivers with runtime transformation handlers are closures a worker never receives, so those images are refused rather than processed differently.
