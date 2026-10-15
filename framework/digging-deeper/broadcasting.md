# Broadcasting

Venusian broadcasts your signals outbound to Redis or a Pusher-protocol service, so other processes and clients can react to what happens in your application.

## Introduction

Broadcasting lets your application announce what happened inside it to the outside world. When a signal marked for broadcasting is dispatched, Venusian sends its name and data to a broadcasting service: a Redis channel, a Pusher Channels app, or any server that speaks the Pusher protocol. Whatever is subscribed on the other side, such as a browser, a dashboard, another service, or another Venusian process, receives the message and reacts to it.

For example, imagine your application exports a user's data to a CSV file inside a [queued job](/docs/{{version}}/framework/digging-deeper/queues). When the file is ready, the job may dispatch an `App\Events\UserDataExported` signal. If that signal is marked for broadcasting, its data is published on a channel, and any client listening on that channel can tell the user the export is done.

Broadcasting in Venusian is **outbound only**. The framework publishes messages; it does not receive them. There is no client library, no channel authorization route, and no subscription handling in the broadcasting component. Subscribing to channels, and deciding who may subscribe to a private one, is the job of the broadcasting service and the clients that connect to it.

> [!NOTE]
> Before diving into broadcasting, make sure you have read Venusian's documentation on [signals and listeners](/docs/{{version}}/framework/digging-deeper/signals).

#### Supported Drivers

Venusian includes the following broadcasting drivers:

| Driver | Sends |
|---|---|
| `redis` | A Redis `PUBLISH` of the message to each channel. |
| `pusher` | An HTTP call to a [Pusher Channels](https://pusher.com/channels) app, through the Pusher PHP SDK. |
| `reverb` | The same Pusher protocol, sent to a self-hosted WebSocket server configured by the `REVERB_*` environment variables. |
| `log` | One `info` line per broadcast to your application's log, naming the signal, the channels, and the JSON payload. |
| `null` | Nothing. This is the default, so broadcasting is off until you choose a driver. |

## Configuration

All of your application's broadcasting configuration is stored in the `config/broadcasting.php` configuration file. A connection is defined there for each of the drivers above. The default connection is chosen by the `BROADCAST_CONNECTION` environment variable:

```ini
BROADCAST_CONNECTION=redis
```

The broadcasting manager is bound in the service container as `broadcast`. You may resolve it with `app('broadcast')`, or type-hint the `Voyager\Contracts\Broadcasting\Factory` contract. `app('broadcast.connection')` is the default connection's broadcaster.

> [!NOTE]
> Unless a signal implements `ShouldBroadcastNow`, broadcasting happens in a queued job, so that the code dispatching the signal is not held up while the message is sent. Make sure your [queue](/docs/{{version}}/framework/digging-deeper/queues) is configured, and that a queue worker is running if the queue connection stores its jobs.

### Redis

The `redis` driver publishes over one of the Redis connections in your `config/database.php` configuration file. The `connection` option chooses which one:

```php
'redis' => [
    'driver' => 'redis',
    'connection' => env('REDIS_BROADCAST_CONNECTION', 'default'),
],
```

Each broadcast is published to every channel as one JSON message holding the signal's broadcast name, its data, and the socket ID it should skip, if any:

```json
{
    "event": "order.shipped",
    "data": {"order": 42, "carrier": "ups"},
    "socket": null
}
```

Channel names are prefixed with your Redis connection's `prefix` option, as Redis keys are. Any Redis subscriber may consume these messages.

### Pusher Channels

To broadcast with Pusher Channels, install the Pusher Channels PHP SDK using the Composer package manager. Without it, resolving the `pusher` or `reverb` broadcaster throws a `RuntimeException` naming the package:

```shell
composer require pusher/pusher-php-server
```

Next, you should configure your Pusher Channels credentials in the `config/broadcasting.php` configuration file. An example Pusher Channels configuration is already included in this file, allowing you to quickly specify your key, secret, and application ID. Typically, you should configure your Pusher Channels credentials in your application's `.env` file:

```ini
PUSHER_APP_ID="your-pusher-app-id"
PUSHER_APP_KEY="your-pusher-key"
PUSHER_APP_SECRET="your-pusher-secret"
PUSHER_HOST=
PUSHER_PORT=443
PUSHER_SCHEME="https"
PUSHER_APP_CLUSTER="mt1"
```

The `config/broadcasting.php` file's `pusher` configuration also allows you to specify additional `options` that are supported by Channels, such as the cluster, and `client_options` that are handed to the Guzzle HTTP client the SDK sends with.

Then, set the `BROADCAST_CONNECTION` environment variable to `pusher` in your application's `.env` file:

```ini
BROADCAST_CONNECTION=pusher
```

#### Encryption Master Key

If you plan to use [end-to-end encrypted private channels](#encrypted-private-channels), you should add an `encryption_master_key_base64` option containing a base64 encoded, 32-byte key to the `pusher` connection's `options` array:

```php
'options' => [
    // ...
    'encryption_master_key_base64' => env('PUSHER_ENCRYPTION_MASTER_KEY'),
],
```

You may generate a suitable key using the `openssl` command:

```shell
openssl rand -base64 32
```

### Self-Hosted Pusher-Protocol Servers

The `reverb` connection sends the same Pusher protocol to a WebSocket server you run yourself. It uses the Pusher SDK as well, so install `pusher/pusher-php-server` as shown above, then point the connection at your server:

```ini
BROADCAST_CONNECTION=reverb

REVERB_APP_ID="your-app-id"
REVERB_APP_KEY="your-app-key"
REVERB_APP_SECRET="your-app-secret"
REVERB_HOST="ws.example.com"
REVERB_PORT=443
REVERB_SCHEME="https"
```

## Concept Overview

Broadcast messages are sent on "channels". A channel is simply a name; Venusian gives the names of private and presence channels a prefix so that the service receiving them can tell them apart:

| Class | Published name |
|---|---|
| `Voyager\Broadcasting\Channel` | The name as given, for example `orders`. |
| `Voyager\Broadcasting\PrivateChannel` | `private-` and the name, for example `private-orders.1`. |
| `Voyager\Broadcasting\PresenceChannel` | `presence-` and the name. |
| `Voyager\Broadcasting\EncryptedPrivateChannel` | `private-encrypted-` and the name. |

Any client may subscribe to a public channel. Whether a client may subscribe to a private or presence channel is decided by the broadcasting service when the client subscribes. With Pusher Channels or a Pusher-protocol server, that means an authorization endpoint you provide outside of Venusian; Venusian itself only publishes.

### Using an Example Application

Before diving into each component of broadcasting, let's take a high level overview using an e-commerce store as an example.

In our application, let's assume customers can watch the shipping status of their orders. Let's also assume that an `OrderShipmentStatusUpdated` signal is dispatched when a shipping status update is processed by the application:

```php
use App\Events\OrderShipmentStatusUpdated;

signal(new OrderShipmentStatusUpdated($order));
```

#### The `ShouldBroadcast` Interface

When a customer is watching one of their orders, we want the status updates to reach them as they are created. So, we need to mark the `OrderShipmentStatusUpdated` signal with the `ShouldBroadcast` interface. This will instruct Venusian to broadcast the signal when it is dispatched:

```php
<?php

namespace App\Events;

use App\Models\Order;
use Voyager\Broadcasting\Channel;
use Voyager\Broadcasting\InteractsWithSockets;
use Voyager\Broadcasting\PresenceChannel;
use Voyager\Contracts\Broadcasting\ShouldBroadcast;
use Voyager\Queue\SerializesModels;

class OrderShipmentStatusUpdated implements ShouldBroadcast
{
    /**
     * The order instance.
     *
     * @var \App\Models\Order
     */
    public $order;
}
```

The `ShouldBroadcast` interface requires our signal to define a `broadcastOn` method. This method is responsible for returning the channels that the signal should broadcast on. An empty stub of this method is already defined on signal classes generated by `make:event`, so we only need to fill in its details. We only want the creator of the order to receive status updates, so we will broadcast the signal on a private channel that is tied to the order:

```php
use Voyager\Broadcasting\Channel;
use Voyager\Broadcasting\PrivateChannel;

/**
 * Get the channel the signal should broadcast on.
 */
public function broadcastOn(): Channel
{
    return new PrivateChannel('orders.'.$this->order->id);
}
```

If you wish the signal to broadcast on multiple channels, you may return an `array` instead:

```php
use Voyager\Broadcasting\PrivateChannel;

/**
 * Get the channels the signal should broadcast on.
 *
 * @return array<int, \Voyager\Broadcasting\Channel>
 */
public function broadcastOn(): array
{
    return [
        new PrivateChannel('orders.'.$this->order->id),
        // ...
    ];
}
```

By default, all of the signal's public properties are included in the broadcast, so a client subscribed to `private-orders.1` receives the order along with the `OrderShipmentStatusUpdated` name.

## Defining Broadcast Signals

To inform Venusian that a given signal should be broadcast, you must implement the `Voyager\Contracts\Broadcasting\ShouldBroadcast` interface on the signal class. This interface is already imported into all signal classes generated by the `make:event` command so you may easily add it to any of your signals.

The `ShouldBroadcast` interface requires you to implement a single method: `broadcastOn`. The `broadcastOn` method should return a channel or array of channels that the signal should broadcast on. The channels should be instances of `Channel`, `PrivateChannel`, or `PresenceChannel`. Instances of `Channel` represent public channels that any client may subscribe to, while `PrivateChannels` and `PresenceChannels` represent channels the broadcasting service only lets authorized clients subscribe to:

```php
<?php

namespace App\Events;

use App\Models\User;
use Voyager\Broadcasting\Channel;
use Voyager\Broadcasting\InteractsWithSockets;
use Voyager\Broadcasting\PresenceChannel;
use Voyager\Broadcasting\PrivateChannel;
use Voyager\Contracts\Broadcasting\ShouldBroadcast;
use Voyager\Queue\SerializesModels;

class ServerCreated implements ShouldBroadcast
{
    use SerializesModels;

    /**
     * Create a new signal instance.
     */
    public function __construct(
        public User $user,
    ) {}

    /**
     * Get the channels the signal should broadcast on.
     *
     * @return array<int, \Voyager\Broadcasting\Channel>
     */
    public function broadcastOn(): array
    {
        return [
            new PrivateChannel('user.'.$this->user->id),
        ];
    }
}
```

After implementing the `ShouldBroadcast` interface, you only need to [dispatch the signal](/docs/{{version}}/framework/digging-deeper/signals#dispatching-signals) as you normally would. Once the signal has been dispatched, a [queued job](/docs/{{version}}/framework/digging-deeper/queues) will automatically broadcast the signal using your specified broadcast driver.

### Broadcast Name

By default, Venusian will broadcast the signal using the signal's class name. However, you may customize the broadcast name by defining a `broadcastAs` method on the signal:

```php
/**
 * The signal's broadcast name.
 */
public function broadcastAs(): string
{
    return 'server.created';
}
```

### Broadcast Data

When a signal is broadcast, all of its `public` properties are automatically serialized and broadcast as the signal's payload, allowing any subscriber to read its public data. So, for example, if your signal has a single public `$user` property that contains an Instrument model, the signal's broadcast payload would be:

```json
{
    "user": {
        "id": 1,
        "name": "Patrick Stewart"
        ...
    }
}
```

However, if you wish to have more fine-grained control over your broadcast payload, you may add a `broadcastWith` method to your signal. This method should return the array of data that you wish to broadcast as the signal payload:

```php
/**
 * Get the data to broadcast.
 *
 * @return array<string, mixed>
 */
public function broadcastWith(): array
{
    return ['id' => $this->user->id];
}
```

### Broadcast Queue

By default, each broadcast signal is placed on the default queue for the default queue connection specified in your `queue.php` configuration file. You may customize the queue connection and name used by the broadcaster by defining `connection` and `queue` properties on your signal class:

```php
class ServerCreated implements ShouldBroadcast
{
    /**
     * The name of the queue connection to use when broadcasting the signal.
     */
    public ?string $connection = 'redis';

    /**
     * The name of the queue on which to place the broadcasting job.
     */
    public ?string $queue = 'default';

    // ...
}
```

Alternatively, you may customize the queue name by defining a `broadcastQueue` method on your signal:

```php
/**
 * The name of the queue on which to place the broadcasting job.
 */
public function broadcastQueue(): string
{
    return 'default';
}
```

The broadcasting job copies the signal's `tries`, `timeout`, `backoff`, `maxExceptions`, and `afterCommit` properties, so you may tune its [attempts and timeout](/docs/{{version}}/framework/digging-deeper/queues#max-job-attempts-and-timeout) on the signal itself. A signal that also implements `Voyager\Contracts\Broadcasting\ShouldBeUnique` takes a [unique lock](/docs/{{version}}/framework/digging-deeper/queues#unique-jobs) before it is queued, and is not queued while that lock is held.

If you would like to broadcast your signal right away instead of through the queue, you can implement the `ShouldBroadcastNow` interface instead of `ShouldBroadcast`. A `shouldBroadcastNow` method returning `true` has the same effect for a single dispatch:

```php
<?php

namespace App\Events;

use Voyager\Contracts\Broadcasting\ShouldBroadcastNow;

class OrderShipmentStatusUpdated implements ShouldBroadcastNow
{
    // ...
}
```

### Broadcast Conditions

Sometimes you want to broadcast your signal only if a given condition is true. You may define these conditions by adding a `broadcastWhen` method to your signal class:

```php
/**
 * Determine if this signal should broadcast.
 */
public function broadcastWhen(): bool
{
    return $this->order->value > 100;
}
```

#### Broadcasting and Database Transactions

When broadcast signals are dispatched within database transactions, they may be processed by the queue before the database transaction has committed. When this happens, any updates you have made to models or database records during the database transaction may not yet be reflected in the database. In addition, any models or database records created within the transaction may not exist in the database. If your signal depends on these models, unexpected errors can occur when the job that broadcasts the signal is processed.

If your queue connection's `after_commit` configuration option is set to `false`, you may still indicate that a particular broadcast signal should be dispatched after all open database transactions have been committed by implementing the `ShouldDispatchAfterCommit` interface on the signal class:

```php
<?php

namespace App\Events;

use Voyager\Contracts\Broadcasting\ShouldBroadcast;
use Voyager\Contracts\Signals\ShouldDispatchAfterCommit;
use Voyager\Queue\SerializesModels;

class ServerCreated implements ShouldBroadcast, ShouldDispatchAfterCommit
{
    use SerializesModels;
}
```

> [!NOTE]
> To learn more about working around these issues, please review the documentation regarding [queued jobs and database transactions](/docs/{{version}}/framework/digging-deeper/queues#jobs-and-database-transactions).

## Broadcasting Signals

Once you have defined a signal and marked it with the `ShouldBroadcast` interface, you only need to dispatch the signal. The signal dispatcher will notice that the signal is marked with the `ShouldBroadcast` interface and will queue the signal for broadcasting:

```php
use App\Events\OrderShipmentStatusUpdated;

signal(new OrderShipmentStatusUpdated($order));
```

You may also hand the signal to the `broadcast` helper. It returns a `Voyager\Broadcasting\PendingBroadcast`, which dispatches the signal once you are done configuring it, and which offers the `toOthers` and `via` methods described below. The `broadcast_if` helper does the same only when its first argument is `true`:

```php
broadcast(new OrderShipmentStatusUpdated($order));

broadcast_if($order->isTracked(), new OrderShipmentStatusUpdated($order));
```

### Only to Others

When a client both triggers a change and listens for its broadcast, you may want the broadcast to reach every subscriber except that client. Pusher-protocol services identify each connected client by a socket ID. Pass the client's socket ID to the `toOthers` method and the service will skip that connection:

```php
use App\Events\OrderShipmentStatusUpdated;

broadcast(new OrderShipmentStatusUpdated($update))->toOthers($socketId);
```

The socket ID is whatever the client reported when it asked your application to make the change; Venusian does not read it from a request for you. The `redis` driver includes it in the published message as `socket`, so your own subscribers may apply the same rule.

> [!WARNING]
> Your signal must use the `Voyager\Broadcasting\InteractsWithSockets` trait in order to call the `toOthers` method.

### Customizing the Connection

If your application interacts with multiple broadcast connections and you want to broadcast a signal using a broadcaster other than your default, you may specify which connection to push a signal to using the `via` method:

```php
use App\Events\OrderShipmentStatusUpdated;

broadcast(new OrderShipmentStatusUpdated($update))->via('pusher');
```

Alternatively, you may specify the signal's broadcast connection by calling the `broadcastVia` method within the signal's constructor. However, before doing so, you should ensure that the signal class uses the `InteractsWithBroadcasting` trait:

```php
<?php

namespace App\Events;

use Voyager\Broadcasting\Channel;
use Voyager\Broadcasting\InteractsWithBroadcasting;
use Voyager\Broadcasting\InteractsWithSockets;
use Voyager\Broadcasting\PresenceChannel;
use Voyager\Broadcasting\PrivateChannel;
use Voyager\Contracts\Broadcasting\ShouldBroadcast;
use Voyager\Queue\SerializesModels;

class OrderShipmentStatusUpdated implements ShouldBroadcast
{
    use InteractsWithBroadcasting;

    /**
     * Create a new signal instance.
     */
    public function __construct()
    {
        $this->broadcastVia('pusher');
    }
}
```

The `broadcastVia` method also accepts an array of connection names. The signal is then sent once on each of them:

```php
$this->broadcastVia(['redis', 'pusher']);
```

### Anonymous Signals

Sometimes, you may want to broadcast a simple message without creating a dedicated signal class. To accommodate this, the broadcasting manager allows you to broadcast "anonymous signals":

```php
app('broadcast')->on('orders.'.$order->id)->send();
```

The example above will broadcast the following message:

```json
{
    "event": "AnonymousEvent",
    "data": "[]",
    "channel": "orders.1"
}
```

Using the `as` and `with` methods, you may customize the signal's name and data:

```php
app('broadcast')->on('orders.'.$order->id)
    ->as('OrderPlaced')
    ->with(['id' => $order->id, 'total' => $order->total])
    ->send();
```

The example above will broadcast a message like the following:

```json
{
    "event": "OrderPlaced",
    "data": "{ id: 1, total: 100 }",
    "channel": "orders.1"
}
```

If you would like to broadcast the anonymous signal on a private or presence channel, you may utilize the `private` and `presence` methods:

```php
app('broadcast')->private('orders.'.$order->id)->send();
app('broadcast')->presence('channels.'.$channel->id)->send();
```

Broadcasting an anonymous signal using the `send` method dispatches the signal to your application's [queue](/docs/{{version}}/framework/digging-deeper/queues) for processing. However, if you would like to broadcast the signal immediately, you may use the `sendNow` method:

```php
app('broadcast')->on('orders.'.$order->id)->sendNow();
```

To broadcast the signal to all channel subscribers except a given client, you can pass that client's socket ID to the `toOthers` method. The `via` method chooses the broadcast connection:

```php
app('broadcast')->on('orders.'.$order->id)
    ->toOthers($socketId)
    ->via('pusher')
    ->send();
```

### Rescuing Broadcasts

When your application's queue server is unavailable or Venusian encounters an error while broadcasting a signal, an exception is thrown. Since broadcasting is often supplementary to your application's core functionality, you can prevent these exceptions from interrupting the code that dispatched the signal by implementing the `ShouldRescue` interface on your signals.

Signals that implement the `ShouldRescue` interface automatically utilize Venusian's [rescue helper function](/docs/{{version}}/framework/digging-deeper/helpers#method-rescue) during broadcast attempts. This helper catches any exceptions, reports them to your application's exception handler for logging, and allows the application to continue executing normally:

```php
<?php

namespace App\Events;

use Voyager\Contracts\Broadcasting\ShouldBroadcast;
use Voyager\Contracts\Broadcasting\ShouldRescue;

class ServerCreated implements ShouldBroadcast, ShouldRescue
{
    // ...
}
```

## Presence Channels

Presence channels build on the security of private channels while letting subscribers know who else is subscribed to the channel. Membership is tracked by the broadcasting service; your application decides what to publish to the channel.

### Broadcasting to Presence Channels

Presence channels may receive signals just like public or private channels. Using the example of a chatroom, we may want to broadcast `NewMessage` signals to the room's presence channel. To do so, we'll return an instance of `PresenceChannel` from the signal's `broadcastOn` method:

```php
/**
 * Get the channels the signal should broadcast on.
 *
 * @return array<int, \Voyager\Broadcasting\Channel>
 */
public function broadcastOn(): array
{
    return [
        new PresenceChannel('chat.'.$this->message->room_id),
    ];
}
```

As with other signals, you may use the `broadcast` helper and the `toOthers` method to exclude the sending client from receiving the broadcast:

```php
broadcast(new NewMessage($message));

broadcast(new NewMessage($message))->toOthers($socketId);
```

<a id="encrypted-private-channels"></a>
## Encrypted Private Channels

Private channels ensure that only authorized clients may subscribe to a channel. However, the signal data itself still passes through your broadcasting service in plain text. When using Pusher Channels, you may use end-to-end encrypted private channels so that only your application and its authorized clients are able to read the signal's data.

To get started, configure an [encryption master key](#encryption-master-key) for your `pusher` connection. Then, return an instance of `EncryptedPrivateChannel` from your signal's `broadcastOn` method:

```php
use Voyager\Broadcasting\EncryptedPrivateChannel;

/**
 * Get the channels the signal should broadcast on.
 *
 * @return array<int, \Voyager\Broadcasting\Channel>
 */
public function broadcastOn(): array
{
    return [
        new EncryptedPrivateChannel('orders.'.$this->order->id),
    ];
}
```

The Pusher SDK encrypts the payload with the master key before it leaves your application. Clients subscribing to the channel need a Pusher client build that can decrypt it.

<a id="model-broadcasting"></a>
## Model Broadcasting

> [!WARNING]
> Before reading the following documentation about model broadcasting, we recommend you become familiar with the general concepts of Venusian's model broadcasting services as well as how to manually create broadcast signals.

It is common to broadcast signals when your application's [Instrument models](/docs/{{version}}/framework/instrument-orm/instrument) are created, updated, or deleted. Of course, this can easily be accomplished by manually defining custom signals for Instrument model state changes and marking those signals with the `ShouldBroadcast` interface.

However, if you are not using these signals for any other purposes in your application, it can be cumbersome to create signal classes for the sole purpose of broadcasting them. To remedy this, Venusian allows you to indicate that an Instrument model should automatically broadcast its state changes.

To get started, your Instrument model should use the `Voyager\Database\Instrument\BroadcastsEvents` trait. In addition, the model should define a `broadcastOn` method, which will return an array of channels that the model's signals should broadcast on:

```php
<?php

namespace App\Models;

use Voyager\Broadcasting\Channel;
use Voyager\Broadcasting\PrivateChannel;
use Voyager\Database\Instrument\BroadcastsEvents;
use Voyager\Database\Instrument\Factories\HasFactory;
use Voyager\Database\Instrument\Model;
use Voyager\Database\Instrument\Relations\BelongsTo;

class Post extends Model
{
    use BroadcastsEvents, HasFactory;

    /**
     * Get the user that the post belongs to.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the channels that model signals should broadcast on.
     *
     * @return array<int, \Voyager\Broadcasting\Channel|\Voyager\Database\Instrument\Model>
     */
    public function broadcastOn(string $event): array
    {
        return [$this, $this->user];
    }
}
```

Once your model includes this trait and defines its broadcast channels, it will begin automatically broadcasting signals when a model instance is created, updated, deleted, trashed, or restored.

In addition, you may have noticed that the `broadcastOn` method receives a string `$event` argument. This argument contains the type of change that has occurred on the model and will have a value of `created`, `updated`, `deleted`, `trashed`, or `restored`. By inspecting the value of this variable, you may determine which channels (if any) the model should broadcast to for a particular change:

```php
/**
 * Get the channels that model signals should broadcast on.
 *
 * @return array<string, array<int, \Voyager\Broadcasting\Channel|\Voyager\Database\Instrument\Model>>
 */
public function broadcastOn(string $event): array
{
    return match ($event) {
        'deleted' => [],
        default => [$this, $this->user],
    };
}
```

#### Customizing Model Broadcasting Signal Creation

Occasionally, you may wish to customize how Venusian creates the underlying model broadcasting signal. You may accomplish this by defining a `newBroadcastableEvent` method on your Instrument model. This method should return a `Voyager\Database\Instrument\BroadcastableModelEventOccurred` instance. For example, if your model keeps the socket ID of the client that last edited it in an `editorSocketId` property, you may skip that client:

```php
use Voyager\Database\Instrument\BroadcastableModelEventOccurred;

/**
 * Create a new broadcastable model signal for the model.
 */
protected function newBroadcastableEvent(string $event): BroadcastableModelEventOccurred
{
    $occurred = new BroadcastableModelEventOccurred($this, $event);

    return $this->editorSocketId
        ? $occurred->dontBroadcastToCurrentUser($this->editorSocketId)
        : $occurred;
}
```

#### Model Broadcast Connection and Queue

A model's broadcasts go through the queue like any other broadcast signal. You may choose the queue connection, the queue, and whether the broadcast waits for open database transactions to commit by defining `broadcastConnection`, `broadcastQueue`, and `broadcastAfterCommit` properties, or methods of the same names, on the model:

```php
/**
 * The queue connection the model's broadcasts are pushed to.
 */
public $broadcastConnection = 'redis';

/**
 * The queue the model's broadcasts are pushed to.
 */
public $broadcastQueue = 'broadcasts';

/**
 * Wait for open database transactions to commit before broadcasting.
 */
public $broadcastAfterCommit = true;
```

### Model Broadcasting Conventions

#### Channel Conventions

As you may have noticed, the `broadcastOn` method in the model example above did not return `Channel` instances. Instead, Instrument models were returned directly. If an Instrument model instance is returned by your model's `broadcastOn` method (or is contained in an array returned by the method), Venusian will automatically instantiate a private channel instance for the model using the model's class name and primary key identifier as the channel name.

So, an `App\Models\User` model with an `id` of `1` would be converted into a `Voyager\Broadcasting\PrivateChannel` instance with a name of `App.Models.User.1`. Of course, in addition to returning Instrument model instances from your model's `broadcastOn` method, you may return complete `Channel` instances in order to have full control over the model's channel names:

```php
use Voyager\Broadcasting\PrivateChannel;

/**
 * Get the channels that model signals should broadcast on.
 *
 * @return array<int, \Voyager\Broadcasting\Channel>
 */
public function broadcastOn(string $event): array
{
    return [
        new PrivateChannel('user.'.$this->id)
    ];
}
```

If you plan to explicitly return a channel instance from your model's `broadcastOn` method, you may pass an Instrument model instance to the channel's constructor. When doing so, Venusian will use the model channel conventions discussed above to convert the Instrument model into a channel name string:

```php
return [new Channel($this->user)];
```

If you need to determine the channel name of a model, you may call the `broadcastChannel` method on any model instance. For example, this method returns the string `App.Models.User.1` for an `App\Models\User` model with an `id` of `1`:

```php
$user->broadcastChannel();
```

#### Signal Conventions

Since model broadcast signals are not associated with an "actual" signal within your application's `App\Events` directory, they are assigned a name and a payload based on conventions. Venusian's convention is to broadcast the signal using the class name of the model (not including the namespace) and the name of the model change that triggered the broadcast.

So, for example, an update to the `App\Models\Post` model would broadcast a signal as `PostUpdated` with the following payload:

```json
{
    "model": {
        "id": 1,
        "title": "My first post"
        ...
    },
    ...
    "socket": "someSocketId"
}
```

The deletion of the `App\Models\User` model would broadcast a signal named `UserDeleted`.

If you would like, you may define a custom broadcast name and payload by adding a `broadcastAs` and `broadcastWith` method to your model. These methods receive the name of the model change / operation that is occurring, allowing you to customize the signal's name and payload for each model operation. If `null` is returned from the `broadcastAs` method, Venusian will use the model broadcasting signal name conventions discussed above when broadcasting the signal:

```php
/**
 * The model signal's broadcast name.
 */
public function broadcastAs(string $event): string|null
{
    return match ($event) {
        'created' => 'post.created',
        default => null,
    };
}

/**
 * Get the data to broadcast for the model.
 *
 * @return array<string, mixed>
 */
public function broadcastWith(string $event): array
{
    return match ($event) {
        'created' => ['title' => $this->title],
        default => ['model' => $this],
    };
}
```
