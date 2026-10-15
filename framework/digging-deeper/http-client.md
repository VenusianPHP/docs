# HTTP Client

Venusian provides an expressive, minimal API around the Guzzle HTTP client for outgoing HTTP requests, blocking or asynchronous on the event loop.

## Introduction

Venusian provides an expressive, minimal API around the [Guzzle HTTP client](http://docs.guzzlephp.org/en/stable/), allowing you to quickly make outgoing HTTP requests to communicate with other web applications. Venusian's wrapper around Guzzle is focused on its most common use cases and a wonderful developer experience.

The client is the `Voyager\Http\Client\Factory` instance bound in the container as `http`. Every call on it starts a fresh `Voyager\Http\Client\PendingRequest`, so you may reach it through `app('http')` or by type-hinting `Factory` in a constructor. Requests block by default; [asynchronous requests](#asynchronous-requests) ride the event loop.

## Making Requests

To make requests, you may use the `head`, `get`, `post`, `put`, `patch`, and `delete` methods provided by the client. First, let's examine how to make a basic `GET` request to another URL:

```php
$response = app('http')->get('http://example.com');
```

The `get` method returns an instance of `Voyager\Http\Client\Response`, which provides a variety of methods that may be used to inspect the response:

```php
$response->body() : string;
$response->json($key = null, $default = null, $flags = null) : mixed;
$response->object() : object;
$response->collect($key = null) : Voyager\NutsAndBolts\Collection;
$response->resource() : resource;
$response->status() : int;
$response->successful() : bool;
$response->redirect(): bool;
$response->failed() : bool;
$response->clientError() : bool;
$response->header($header) : string;
$response->headers() : array;
```

The `Voyager\Http\Client\Response` object also implements the PHP `ArrayAccess` interface, allowing you to access JSON response data directly on the response:

```php
return app('http')->get('http://example.com/users/1')['name'];
```

In addition to the response methods listed above, the following methods may be used to determine if the response has a specific status code:

```php
$response->ok() : bool;                  // 200 OK
$response->created() : bool;             // 201 Created
$response->accepted() : bool;            // 202 Accepted
$response->noContent() : bool;           // 204 No Content
$response->movedPermanently() : bool;    // 301 Moved Permanently
$response->found() : bool;               // 302 Found
$response->badRequest() : bool;          // 400 Bad Request
$response->unauthorized() : bool;        // 401 Unauthorized
$response->paymentRequired() : bool;     // 402 Payment Required
$response->forbidden() : bool;           // 403 Forbidden
$response->notFound() : bool;            // 404 Not Found
$response->requestTimeout() : bool;      // 408 Request Timeout
$response->conflict() : bool;            // 409 Conflict
$response->unprocessableEntity() : bool; // 422 Unprocessable Entity
$response->tooManyRequests() : bool;     // 429 Too Many Requests
$response->serverError() : bool;         // >= 500 Server Error
```

#### URI Templates

The HTTP client also allows you to construct request URLs using the [URI template specification](https://www.rfc-editor.org/rfc/rfc6570). To define the URL parameters that can be expanded by your URI template, you may use the `withUrlParameters` method:

```php
app('http')->withUrlParameters([
    'endpoint' => 'https://example.com',
    'page' => 'docs',
    'version' => '13.x',
    'topic' => 'validation',
])->get('{+endpoint}/{page}/{version}/{topic}');
```

#### Dumping Requests

If you would like to dump the outgoing request instance before it is sent and terminate the script's execution, you may add the `dd` method to the beginning of your request definition:

```php
return app('http')->dd()->get('http://example.com');
```

### Request Data

Of course, it is common when making `POST`, `PUT`, and `PATCH` requests to send additional data with your request, so these methods accept an array of data as their second argument. By default, data will be sent using the `application/json` content type:

```php
$response = app('http')->post('http://example.com/users', [
    'name' => 'Steve',
    'role' => 'Network Administrator',
]);
```

#### GET Request Query Parameters

When making `GET` requests, you may either append a query string to the URL directly or pass an array of key / value pairs as the second argument to the `get` method:

```php
$response = app('http')->get('http://example.com/users', [
    'name' => 'Taylor',
    'page' => 1,
]);
```

Alternatively, the `withQueryParameters` method may be used:

```php
app('http')->retry(3, 100)->withQueryParameters([
    'name' => 'Taylor',
    'page' => 1,
])->get('http://example.com/users');
```

#### Sending Form URL Encoded Requests

If you would like to send data using the `application/x-www-form-urlencoded` content type, you should call the `asForm` method before making your request:

```php
$response = app('http')->asForm()->post('http://example.com/users', [
    'name' => 'Sara',
    'role' => 'Privacy Consultant',
]);
```

#### Sending a Raw Request Body

You may use the `withBody` method if you would like to provide a raw request body when making a request. The content type may be provided via the method's second argument:

```php
$response = app('http')->withBody(
    base64_encode($photo), 'image/jpeg'
)->post('http://example.com/photo');
```

#### Multi-Part Requests

If you would like to send files as multi-part requests, you should call the `attach` method before making your request. This method accepts the name of the file and its contents. If needed, you may provide a third argument which will be considered the file's filename, while a fourth argument may be used to provide headers associated with the file:

```php
$response = app('http')->attach(
    'attachment', file_get_contents('photo.jpg'), 'photo.jpg', ['Content-Type' => 'image/jpeg']
)->post('http://example.com/attachments');
```

Instead of passing the raw contents of a file, you may pass a stream resource:

```php
$photo = fopen('photo.jpg', 'r');

$response = app('http')->attach(
    'attachment', $photo, 'photo.jpg'
)->post('http://example.com/attachments');
```

### Headers

Headers may be added to requests using the `withHeaders` method. This `withHeaders` method accepts an array of key / value pairs:

```php
$response = app('http')->withHeaders([
    'X-First' => 'foo',
    'X-Second' => 'bar'
])->post('http://example.com/users', [
    'name' => 'Taylor',
]);
```

You may use the `accept` method to specify the content type that your application is expecting in response to your request:

```php
$response = app('http')->accept('application/json')->get('http://example.com/users');
```

For convenience, you may use the `acceptJson` method to quickly specify that your application expects the `application/json` content type in response to your request:

```php
$response = app('http')->acceptJson()->get('http://example.com/users');
```

The `withHeaders` method merges new headers into the request's existing headers. If needed, you may replace all of the headers entirely using the `replaceHeaders` method:

```php
$response = app('http')->withHeaders([
    'X-Original' => 'foo',
])->replaceHeaders([
    'X-Replacement' => 'bar',
])->post('http://example.com/users', [
    'name' => 'Taylor',
]);
```

### Authentication

You may specify basic and digest authentication credentials using the `withBasicAuth` and `withDigestAuth` methods, respectively:

```php
// Basic authentication...
$response = app('http')->withBasicAuth('taylor@example.com', 'secret')->post(/* ... */);

// Digest authentication...
$response = app('http')->withDigestAuth('taylor@example.com', 'secret')->post(/* ... */);
```

#### Bearer Tokens

If you would like to quickly add a bearer token to the request's `Authorization` header, you may use the `withToken` method:

```php
$response = app('http')->withToken('token')->post(/* ... */);
```

### Timeout

The `timeout` method may be used to specify the maximum number of seconds to wait for a response. By default, the HTTP client will timeout after 30 seconds:

```php
$response = app('http')->timeout(3)->get(/* ... */);
```

If the given timeout is exceeded, an instance of `Voyager\Http\Client\ConnectionException` will be thrown.

You may specify the maximum number of seconds to wait while trying to connect to a server using the `connectTimeout` method. The default is 10 seconds:

```php
$response = app('http')->connectTimeout(3)->get(/* ... */);
```

### Retries

If you would like the HTTP client to automatically retry the request if a client or server error occurs, you may use the `retry` method. The `retry` method accepts the maximum number of times the request should be attempted and the number of milliseconds that Venusian should wait in between attempts:

```php
$response = app('http')->retry(3, 100)->post(/* ... */);
```

If you would like to manually calculate the number of milliseconds to sleep between attempts, you may pass a closure as the second argument to the `retry` method:

```php
use Exception;

$response = app('http')->retry(3, function (int $attempt, Exception $exception) {
    return $attempt * 100;
})->post(/* ... */);
```

For convenience, you may also provide an array as the first argument to the `retry` method. This array will be used to determine how many milliseconds to sleep between subsequent attempts:

```php
$response = app('http')->retry([100, 200])->post(/* ... */);
```

If needed, you may pass a third argument to the `retry` method. The third argument should be a callable that determines if the retries should actually be attempted. For example, you may wish to only retry the request if the initial request encounters an `ConnectionException`:

```php
use Voyager\Http\Client\PendingRequest;
use Throwable;

$response = app('http')->retry(3, 100, function (Throwable $exception, PendingRequest $request) {
    return $exception instanceof ConnectionException;
})->post(/* ... */);
```

If a request attempt fails, you may wish to make a change to the request before a new attempt is made. You can achieve this by modifying the request argument provided to the callable you provided to the `retry` method. For example, you might want to retry the request with a new authorization token if the first attempt returned an authentication error:

```php
use Voyager\Http\Client\PendingRequest;
use Voyager\Http\Client\RequestException;
use Throwable;

$response = app('http')->withToken($this->getToken())->retry(2, 0, function (Throwable $exception, PendingRequest $request) {
    if (! $exception instanceof RequestException || $exception->response->status() !== 401) {
        return false;
    }

    $request->withToken($this->getNewToken());

    return true;
})->post(/* ... */);
```

If all of the requests fail, an instance of `Voyager\Http\Client\RequestException` will be thrown. If you would like to disable this behavior, you may provide a `throw` argument with a value of `false`. When disabled, the last response received by the client will be returned after all retries have been attempted:

```php
$response = app('http')->retry(3, 100, throw: false)->post(/* ... */);
```

> [!WARNING]
> If all of the requests fail because of a connection issue, a `Voyager\Http\Client\ConnectionException` will still be thrown even when the `throw` argument is set to `false`.

### Error Handling

Unlike Guzzle's default behavior, Venusian's HTTP client wrapper does not throw exceptions on client or server errors (`400` and `500` level responses from servers). You may determine if one of these errors was returned using the `successful`, `clientError`, or `serverError` methods:

```php
// Determine if the status code is >= 200 and < 300...
$response->successful();

// Determine if the status code is >= 400...
$response->failed();

// Determine if the response has a 400 level status code...
$response->clientError();

// Determine if the response has a 500 level status code...
$response->serverError();

// Immediately execute the given callback if there was a client or server error...
$response->onError(callable $callback);
```

#### Throwing Exceptions

If you have a response instance and would like to throw an instance of `Voyager\Http\Client\RequestException` if the response status code indicates a client or server error, you may use the `throw` or `throwIf` methods:

```php
use Voyager\Http\Client\Response;

$response = app('http')->post(/* ... */);

// Throw an exception if a client or server error occurred...
$response->throw();

// Throw an exception if an error occurred and the given condition is true...
$response->throwIf($condition);

// Throw an exception if an error occurred and the given closure resolves to true...
$response->throwIf(fn (Response $response) => true);

// Throw an exception if an error occurred and the given condition is false...
$response->throwUnless($condition);

// Throw an exception if an error occurred and the given closure resolves to false...
$response->throwUnless(fn (Response $response) => false);

// Throw an exception if the response has a specific status code...
$response->throwIfStatus(403);

// Throw an exception unless the response has a specific status code...
$response->throwUnlessStatus(200);

// Throw an exception if a server error occurred (status >= 500)...
$response->throwIfServerError();

// Throw an exception if a client error occurred (status >= 400 and < 500)...
$response->throwIfClientError();

return $response['user']['id'];
```

The `Voyager\Http\Client\RequestException` instance has a public `$response` property which will allow you to inspect the returned response.

The `throw` method returns the response instance if no error occurred, allowing you to chain other operations onto the `throw` method:

```php
return app('http')->post(/* ... */)->throw()->json();
```

If you would like to perform some additional logic before the exception is thrown, you may pass a closure to the `throw` method. The exception will be thrown automatically after the closure is invoked, so you do not need to re-throw the exception from within the closure:

```php
use Voyager\Http\Client\Response;
use Voyager\Http\Client\RequestException;

return app('http')->post(/* ... */)->throw(function (Response $response, RequestException $e) {
    // ...
})->json();
```

By default, `RequestException` messages are truncated to 120 characters when logged or reported. To customize or disable this behavior, you may utilize the `truncateAt` and `dontTruncate` methods from the `boot` method of your application's `App\Providers\AppServiceProvider`:

```php
use Voyager\Http\Client\RequestException;

public function boot(): void
{
    // Truncate request exception messages to 240 characters...
    RequestException::truncateAt(240);

    // Disable request exception message truncation...
    RequestException::dontTruncate();
}
```

Alternatively, you may customize the exception truncation behavior per request using the `truncateExceptionsAt` method:

```php
return app('http')->truncateExceptionsAt(240)->post(/* ... */);
```

### Guzzle Middleware

Since Venusian's HTTP client is powered by Guzzle, you may take advantage of [Guzzle Middleware](https://docs.guzzlephp.org/en/stable/handlers-and-middleware.html) to manipulate the outgoing request or inspect the incoming response. To manipulate the outgoing request, register a Guzzle middleware via the `withRequestMiddleware` method:

```php
use Psr\Http\Message\RequestInterface;

$response = app('http')->withRequestMiddleware(
    function (RequestInterface $request) {
        return $request->withHeader('X-Example', 'Value');
    }
)->get('http://example.com');
```

Likewise, you can inspect the incoming HTTP response by registering a middleware via the `withResponseMiddleware` method:

```php
use Psr\Http\Message\ResponseInterface;

$response = app('http')->withResponseMiddleware(
    function (ResponseInterface $response) {
        $header = $response->getHeader('X-Example');

        // ...

        return $response;
    }
)->get('http://example.com');
```

#### Global Middleware

Sometimes, you may want to register a middleware that applies to every outgoing request and incoming response. To accomplish this, you may use the `globalRequestMiddleware` and `globalResponseMiddleware` methods. Typically, these methods should be invoked in the `boot` method of your application's `AppServiceProvider`:

```php
app('http')->globalRequestMiddleware(fn ($request) => $request->withHeader(
    'User-Agent', 'Example Application/1.0'
));

app('http')->globalResponseMiddleware(fn ($response) => $response->withHeader(
    'X-Finished-At', now()->toDateTimeString()
));
```

### Guzzle Options

You may specify additional [Guzzle request options](http://docs.guzzlephp.org/en/stable/request-options.html) for an outgoing request using the `withOptions` method. The `withOptions` method accepts an array of key / value pairs:

```php
$response = app('http')->withOptions([
    'debug' => true,
])->get('http://example.com/users');
```

#### Global Options

To configure default options for every outgoing request, you may utilize the `globalOptions` method. Typically, this method should be invoked from the `boot` method of your application's `AppServiceProvider`:

```php
/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('http')->globalOptions([
        'allow_redirects' => false,
    ]);
}
```

## Concurrent Requests

Sometimes, you may wish to make multiple HTTP requests concurrently. In other words, you want several requests to be dispatched at the same time instead of issuing the requests sequentially. This can lead to substantial performance improvements when interacting with slow HTTP APIs.

<a id="request-pooling"></a>
### Request Pooling

Thankfully, you may accomplish this using the `pool` method. The `pool` method accepts a closure which receives an `Voyager\Http\Client\Pool` instance, allowing you to easily add requests to the request pool for dispatching:

```php
use Voyager\Http\Client\Pool;

$responses = app('http')->pool(fn (Pool $pool) => [
    $pool->get('http://localhost/first'),
    $pool->get('http://localhost/second'),
    $pool->get('http://localhost/third'),
]);

return $responses[0]->ok() &&
       $responses[1]->ok() &&
       $responses[2]->ok();
```

As you can see, each response instance can be accessed based on the order it was added to the pool. If you wish, you can name the requests using the `as` method, which allows you to access the corresponding responses by name:

```php
use Voyager\Http\Client\Pool;

$responses = app('http')->pool(fn (Pool $pool) => [
    $pool->as('first')->get('http://localhost/first'),
    $pool->as('second')->get('http://localhost/second'),
    $pool->as('third')->get('http://localhost/third'),
]);

return $responses['first']->ok();
```

The maximum concurrency of the request pool may be controlled by providing the `concurrency` argument to the `pool` method. This value determines the maximum number of HTTP requests that may be concurrently in-flight while processing the request pool:

```php
$responses = app('http')->pool(fn (Pool $pool) => [
    // ...
], concurrency: 5);
```

If a pooled request fails at the connection level (for example, a timeout or DNS failure), the corresponding entry in the `$responses` array will be an `Voyager\Http\Client\ConnectionException` instance instead of a `Response` instance:

```php
foreach ($responses as $response) {
    if ($response instanceof Throwable) {
        // The request failed to connect...
    } elseif ($response->failed()) {
        // The request connected but received an error response...
    }
}
```

#### Customizing Concurrent Requests

The `pool` method cannot be chained with other HTTP client methods such as the `withHeaders` or `middleware` methods. If you want to apply custom headers or middleware to pooled requests, you should configure those options on each request in the pool:

```php
use Voyager\Http\Client\Pool;

$headers = [
    'X-Example' => 'example',
];

$responses = app('http')->pool(fn (Pool $pool) => [
    $pool->withHeaders($headers)->get('http://example.test/test'),
    $pool->withHeaders($headers)->get('http://example.test/test'),
    $pool->withHeaders($headers)->get('http://example.test/test'),
]);
```

<a id="request-batching"></a>
### Request Batching

Another way of working with concurrent requests in Venusian is to use the `batch` method. Like the `pool` method, it accepts a closure which receives an `Voyager\Http\Client\Batch` instance, allowing you to easily add requests to the request pool for dispatching, but it also allows you to define completion callbacks:

```php
use Voyager\Http\Client\Batch;
use Voyager\Http\Client\ConnectionException;
use Voyager\Http\Client\RequestException;
use Voyager\Http\Client\Response;

$responses = app('http')->batch(fn (Batch $batch) => [
    $batch->get('http://localhost/first'),
    $batch->get('http://localhost/second'),
    $batch->get('http://localhost/third'),
])->before(function (Batch $batch) {
    // The batch has been created but no requests have been initialized...
})->progress(function (Batch $batch, int|string $key, Response $response) {
    // An individual request has completed successfully...
})->then(function (Batch $batch, array $results) {
    // All requests completed successfully...
})->catch(function (Batch $batch, int|string $key, Response|RequestException|ConnectionException $response) {
    // Batch request failure detected...
})->finally(function (Batch $batch, array $results) {
    // The batch has finished executing...
})->send();
```

Like the `pool` method, you can use the `as` method to name your requests:

```php
$responses = app('http')->batch(fn (Batch $batch) => [
    $batch->as('first')->get('http://localhost/first'),
    $batch->as('second')->get('http://localhost/second'),
    $batch->as('third')->get('http://localhost/third'),
])->send();
```

After a `batch` is started by calling the `send` method, you can't add new requests to it. Trying to do so will result in a `Voyager\Http\Client\BatchInProgressException` exception being thrown.

The maximum concurrency of the request batch may be controlled via the `concurrency` method. This value determines the maximum number of HTTP requests that may be concurrently in-flight while processing the request batch:

```php
$responses = app('http')->batch(fn (Batch $batch) => [
    // ...
])->concurrency(5)->send();
```

#### Inspecting Batches

The `Voyager\Http\Client\Batch` instance that is provided to batch completion callbacks has a variety of properties and methods to assist you in interacting with and inspecting a given batch of requests:

```php
// The number of requests assigned to the batch...
$batch->totalRequests;

// The number of requests that have not been processed yet...
$batch->pendingRequests;

// The number of requests that have failed...
$batch->failedRequests;

// The number of requests that have been processed thus far...
$batch->processedRequests();

// Indicates if the batch has finished executing...
$batch->finished();

// Indicates if the batch has request failures...
$batch->hasFailures();
```
#### Deferring Batches

When the `defer` method is invoked, the batch of requests is not executed immediately. Instead, Venusian will execute the batch once the current Computer command finishes successfully, or once the current queued job succeeds. `defer` returns the `Voyager\NutsAndBolts\Defer\DeferredCallback` it registered:

```php
use Voyager\Http\Client\Batch;

$deferred = app('http')->batch(fn (Batch $batch) => [
    $batch->get('http://localhost/first'),
    $batch->get('http://localhost/second'),
    $batch->get('http://localhost/third'),
])->then(function (Batch $batch, array $results) {
    // All requests completed successfully...
})->defer();
```

## Asynchronous Requests

The `async` method turns a request into a non-blocking send on the event loop. The transfer starts as soon as you call `get`, `post`, or any other verb, and you receive a `Voyager\Contracts\IOPools\Promise` instead of a response. The promise resolves with the `Voyager\Http\Client\Response`; a connection failure rejects it with a `Voyager\Http\Client\ConnectionException`:

```php
use Voyager\Http\Client\Response;

$promise = app('http')->async()->get('http://example.com/users');

$promise->then(function (Response $response) {
    // ...
})->error(function (Throwable $e) {
    // ...
});

// Or block until it settles...
$response = $promise->wait();
```

Because each transfer is in flight on the loop, several `async` requests run at the same time; waiting on them one after another costs the time of the slowest, not the sum:

```php
$promises = array_map(
    fn (string $url) => app('http')->async()->get($url),
    ['http://example.com/first', 'http://example.com/second', 'http://example.com/third'],
);

$responses = array_map(fn ($promise) => $promise->wait(), $promises);
```

Retries and Guzzle options keep working on asynchronous requests. The `delay` option holds a request back on the loop's timer instead of sleeping:

```php
$response = app('http')->retry(3, 100, throw: false)->async()->get('http://example.com/flaky')->wait();

$promise = app('http')->async()->withOptions(['delay' => 250])->get('http://example.com/later');
```

Request [pools](#request-pooling) and [batches](#request-batching) send through the same loop driver, keeping their concurrency cap.

### Async Drivers

The loop driver that carries asynchronous requests is configured under `async` in your application's `config/http.php` file:

```php
'async' => [
    'default' => env('HTTP_ASYNC_DRIVER', 'auto'),
    'drivers' => [
        'curl'  => ['driver' => 'curl',  'max_handles' => 50, 'multi_options' => []],
        'pcurl' => ['driver' => 'pcurl', 'max_handles' => 50],
    ],
],
```

The `curl` driver uses ext-curl's multi interface. ext-curl never hands out curl's sockets, so while transfers are in flight the driver holds the loop's sleep inside `curl_multi_select`, and other wake sources are checked after it returns. The `pcurl` driver needs the pcurl extension (`ext-pcurl`): curl's own sockets and timer join the loop's wait, so every other wake source on the loop is answered on time while a slow response is still in flight. The default `auto` driver picks `pcurl` when the extension is loaded and `curl` otherwise. Both drivers need ext-curl.

The manager behind these drivers is bound in the container as `http.async`:

```php
$driver = app('http.async')->driver(); // LoopPcurlHandler or LoopCurlHandler
```

> [!WARNING]
> Selecting the `pcurl` driver without the pcurl extension loaded throws a `Voyager\Http\Client\HttpClientException`.

## Macros

The Venusian HTTP client allows you to define "macros", which can serve as a fluent, expressive mechanism to configure common request paths and headers when interacting with services throughout your application. To get started, you may define the macro within the `boot` method of your application's `App\Providers\AppServiceProvider` class:

```php
/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    app('http')->macro('github', function () {
        return $this->withHeaders([
            'X-Example' => 'example',
        ])->baseUrl('https://github.com');
    });
}
```

Once your macro has been configured, you may invoke it from anywhere in your application to create a pending request with the specified configuration:

```php
$response = app('http')->github()->get('/');
```

## Testing

The HTTP client provides functionality to help you easily and expressively write tests. Because `http` is a container singleton, the client's `fake` method allows you to instruct the HTTP client to return stubbed / dummy responses when requests are made.

### Faking Responses

For example, to instruct the HTTP client to return empty, `200` status code responses for every request, you may call the `fake` method with no arguments:

```php
app('http')->fake();

$response = app('http')->post(/* ... */);
```

#### Faking Specific URLs

Alternatively, you may pass an array to the `fake` method. The array's keys should represent URL patterns that you wish to fake and their associated responses. The `*` character may be used as a wildcard character. You may use the static `Factory::response` method to construct stub / fake responses for these endpoints:

```php
use Voyager\Http\Client\Factory;

app('http')->fake([
    // Stub a JSON response for GitHub endpoints...
    'github.com/*' => Factory::response(['foo' => 'bar'], 200, $headers),

    // Stub a string response for Google endpoints...
    'google.com/*' => Factory::response('Hello World', 200, $headers),
]);
```

Any requests made to URLs that have not been faked will actually be executed. If you would like to specify a fallback URL pattern that will stub all unmatched URLs, you may use a single `*` character:

```php
app('http')->fake([
    // Stub a JSON response for GitHub endpoints...
    'github.com/*' => Factory::response(['foo' => 'bar'], 200, ['Headers']),

    // Stub a string response for all other endpoints...
    '*' => Factory::response('Hello World', 200, ['Headers']),
]);
```

For convenience, simple string, JSON, and empty responses may be generated by providing a string, array, or integer as the response:

```php
app('http')->fake([
    'google.com/*' => 'Hello World',
    'github.com/*' => ['foo' => 'bar'],
    'chatgpt.com/*' => 200,
]);
```

#### Faking Exceptions

Sometimes you may need to test your application's behavior if the HTTP client encounters an `Voyager\Http\Client\ConnectionException` when attempting to make a request. You can instruct the HTTP client to throw a connection exception using the `failedConnection` method:

```php
app('http')->fake([
    'github.com/*' => Factory::failedConnection(),
]);
```

When a test double of your own needs to throw a `Voyager\Http\Client\RequestException`, the `failedRequest` method builds one around a stubbed response:

```php
use Voyager\Http\Client\Factory;

$exception = Factory::failedRequest(['code' => 'not_found'], 404);
```

#### Faking Response Sequences

Sometimes you may need to specify that a single URL should return a series of fake responses in a specific order. You may accomplish this using the `Factory::sequence` method to build the responses:

```php
app('http')->fake([
    // Stub a series of responses for GitHub endpoints...
    'github.com/*' => Factory::sequence()
        ->push('Hello World', 200)
        ->push(['foo' => 'bar'], 200)
        ->pushStatus(404),
]);
```

When all the responses in a response sequence have been consumed, any further requests will cause the response sequence to throw an exception. If you would like to specify a default response that should be returned when a sequence is empty, you may use the `whenEmpty` method:

```php
app('http')->fake([
    // Stub a series of responses for GitHub endpoints...
    'github.com/*' => Factory::sequence()
        ->push('Hello World', 200)
        ->push(['foo' => 'bar'], 200)
        ->whenEmpty(Factory::response()),
]);
```

If you would like to fake a sequence of responses but do not need to specify a specific URL pattern that should be faked, you may use the client's `fakeSequence` method:

```php
app('http')->fakeSequence()
    ->push('Hello World', 200)
    ->whenEmpty(Factory::response());
```

#### Fake Callback

If you require more complicated logic to determine what responses to return for certain endpoints, you may pass a closure to the `fake` method. This closure will receive an instance of `Voyager\Http\Client\Request` and should return a response instance. Within your closure, you may perform whatever logic is necessary to determine what type of response to return:

```php
use Voyager\Http\Client\Request;

app('http')->fake(function (Request $request) {
    return Factory::response('Hello World', 200);
});
```

### Inspecting Requests

When faking responses, you may occasionally wish to inspect the requests the client receives in order to make sure your application is sending the correct data or headers. You may accomplish this by calling the client's `assertSent` method after calling `fake`.

The `assertSent` method accepts a closure which will receive an `Voyager\Http\Client\Request` instance and should return a boolean value indicating if the request matches your expectations. In order for the test to pass, at least one request must have been issued matching the given expectations:

```php
use Voyager\Http\Client\Request;

app('http')->fake();

app('http')->withHeaders([
    'X-First' => 'foo',
])->post('http://example.com/users', [
    'name' => 'Taylor',
    'role' => 'Developer',
]);

app('http')->assertSent(function (Request $request) {
    return $request->hasHeader('X-First', 'foo') &&
           $request->url() == 'http://example.com/users' &&
           $request['name'] == 'Taylor' &&
           $request['role'] == 'Developer';
});
```

If needed, you may assert that a specific request was not sent using the `assertNotSent` method:

```php
use Voyager\Http\Client\Request;

app('http')->fake();

app('http')->post('http://example.com/users', [
    'name' => 'Taylor',
    'role' => 'Developer',
]);

app('http')->assertNotSent(function (Request $request) {
    return $request->url() === 'http://example.com/posts';
});
```

You may use the `assertSentCount` method to assert how many requests were "sent" during the test:

```php
app('http')->fake();

app('http')->assertSentCount(5);
```

Or, you may use the `assertNothingSent` method to assert that no requests were sent during the test:

```php
app('http')->fake();

app('http')->assertNothingSent();
```

#### Recording Requests / Responses

You may use the `recorded` method to gather all requests and their corresponding responses. The `recorded` method returns a collection of arrays that contains instances of `Voyager\Http\Client\Request` and `Voyager\Http\Client\Response`:

```php
app('http')->fake([
    'https://example.com' => Factory::response(status: 500),
    'https://api.example.com/' => Factory::response(),
]);

app('http')->get('https://example.com');
app('http')->get('https://api.example.com/');

$recorded = app('http')->recorded();

[$request, $response] = $recorded[0];
```

Additionally, the `recorded` method accepts a closure which will receive an instance of `Voyager\Http\Client\Request` and `Voyager\Http\Client\Response` and may be used to filter request / response pairs based on your expectations:

```php
use Voyager\Http\Client\Request;
use Voyager\Http\Client\Response;

app('http')->fake([
    'https://example.com' => Factory::response(status: 500),
    'https://api.example.com/' => Factory::response(),
]);

app('http')->get('https://example.com');
app('http')->get('https://api.example.com/');

$recorded = app('http')->recorded(function (Request $request, Response $response) {
    return $request->url() !== 'https://example.com' &&
           $response->successful();
});
```

### Preventing Stray Requests

If you would like to ensure that all requests sent via the HTTP client have been faked throughout your individual test or complete test suite, you can call the `preventStrayRequests` method. After calling this method, any requests that do not have a corresponding fake response will throw an exception rather than making the actual HTTP request:

```php
app('http')->preventStrayRequests();

app('http')->fake([
    'github.com/*' => Factory::response('ok'),
]);

// An "ok" response is returned...
app('http')->get('https://github.com/example/repo');

// An exception is thrown...
app('http')->get('https://example.com');
```

Sometimes, you may wish to prevent most stray requests while still allowing specific requests to execute. To accomplish this, you may pass an array of URL patterns to the `allowStrayRequests` method. Any request matching one of the given patterns will be allowed, while all other requests will continue to throw an exception:

```php
app('http')->preventStrayRequests();

app('http')->allowStrayRequests([
    'http://127.0.0.1:5000/*',
]);

// This request is executed...
app('http')->get('http://127.0.0.1:5000/generate');

// An exception is thrown...
app('http')->get('https://example.com');
```
