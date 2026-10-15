# File Storage

Venusian provides a powerful filesystem abstraction thanks to the wonderful Flysystem PHP package by Frank de Jonge, with every disk call also available on a worker pool.

## Introduction

Venusian provides a powerful filesystem abstraction thanks to the wonderful [Flysystem](https://github.com/thephpleague/flysystem) PHP package by Frank de Jonge. The Venusian Flysystem integration provides simple drivers for working with local filesystems, FTP, SFTP, and Amazon S3. Even better, it's amazingly simple to switch between these storage options between your local development machine and production server as the API remains the same for each system. When your application runs on the event loop, every disk call can also [run on a worker pool](#offloading-to-a-worker-pool) and answer with a promise.

## Configuration

Venusian's filesystem configuration file is located at `config/filesystems.php`. Within this file, you may configure all of your filesystem "disks". Each disk represents a particular storage driver and storage location. Example configurations for the `local` and `s3` drivers are included in the configuration file so you can modify the configuration to reflect your storage preferences and credentials.

The `local` driver interacts with files stored locally on the machine running the Venusian application, while the `ftp` and `sftp` storage drivers are used for FTP and SSH key-based FTP. The `s3` driver is used to write to Amazon's S3 cloud storage service.

> [!NOTE]
> You may configure as many disks as you like and may even have multiple disks that use the same driver.

### The Local Driver

When using the `local` driver, all file operations are relative to the `root` directory defined in your `filesystems` configuration file. By default, this value is set to the `storage/app/private` directory. Therefore, the following method would write to `storage/app/private/example.txt`:

```php
storage()->disk('local')->put('example.txt', 'Contents');
```

### The Public Disk

The `public` disk included in your application's `filesystems` configuration file is intended for files that are going to be publicly accessible. By default, the `public` disk uses the `local` driver, stores its files in `storage/app/public`, and builds [URLs](#file-urls) from your `APP_URL` followed by `/storage`.

### Driver Prerequisites

#### S3 Driver Configuration

Before using the S3 driver, you will need to install the Flysystem S3 package via the Composer package manager:

```shell
composer require league/flysystem-aws-s3-v3 "^3.0" --with-all-dependencies
```

An S3 disk configuration array is located in your `config/filesystems.php` configuration file. Typically, you should configure your S3 information and credentials using the following environment variables which are referenced by the `config/filesystems.php` configuration file:

```ini
AWS_ACCESS_KEY_ID=<your-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=<your-bucket-name>
AWS_USE_PATH_STYLE_ENDPOINT=false
```

For convenience, these environment variables match the naming convention used by the AWS CLI.

#### FTP Driver Configuration

Before using the FTP driver, you will need to install the Flysystem FTP package via the Composer package manager:

```shell
composer require league/flysystem-ftp "^3.0"
```

Venusian's Flysystem integrations work great with FTP; however, a sample configuration is not included with the framework's default `config/filesystems.php` configuration file. If you need to configure an FTP filesystem, you may use the configuration example below:

```php
'ftp' => [
    'driver' => 'ftp',
    'host' => env('FTP_HOST'),
    'username' => env('FTP_USERNAME'),
    'password' => env('FTP_PASSWORD'),

    // Optional FTP Settings...
    // 'port' => env('FTP_PORT', 21),
    // 'root' => env('FTP_ROOT'),
    // 'passive' => true,
    // 'ssl' => true,
    // 'timeout' => 30,
],
```

#### SFTP Driver Configuration

Before using the SFTP driver, you will need to install the Flysystem SFTP package via the Composer package manager:

```shell
composer require league/flysystem-sftp-v3 "^3.0"
```

Venusian's Flysystem integrations work great with SFTP; however, a sample configuration is not included with the framework's default `config/filesystems.php` configuration file. If you need to configure an SFTP filesystem, you may use the configuration example below:

```php
'sftp' => [
    'driver' => 'sftp',
    'host' => env('SFTP_HOST'),

    // Settings for basic authentication...
    'username' => env('SFTP_USERNAME'),
    'password' => env('SFTP_PASSWORD'),

    // Settings for SSH key-based authentication with encryption password...
    'privateKey' => env('SFTP_PRIVATE_KEY'),
    'passphrase' => env('SFTP_PASSPHRASE'),

    // Settings for file / directory permissions...
    'visibility' => 'private', // `private` = 0600, `public` = 0644
    'directory_visibility' => 'private', // `private` = 0700, `public` = 0755

    // Optional SFTP Settings...
    // 'hostFingerprint' => env('SFTP_HOST_FINGERPRINT'),
    // 'maxTries' => 4,
    // 'passphrase' => env('SFTP_PASSPHRASE'),
    // 'port' => env('SFTP_PORT', 22),
    // 'root' => env('SFTP_ROOT', ''),
    // 'timeout' => 30,
    // 'useAgent' => true,
],
```

### Scoped and Read-Only Filesystems

Scoped disks allow you to define a filesystem where all paths are automatically prefixed with a given path prefix. Before creating a scoped filesystem disk, you will need to install an additional Flysystem package via the Composer package manager:

```shell
composer require league/flysystem-path-prefixing "^3.0"
```

You may create a path scoped instance of any existing filesystem disk by defining a disk that utilizes the `scoped` driver. For example, you may create a disk which scopes your existing `s3` disk to a specific path prefix, and then every file operation using your scoped disk will utilize the specified prefix:

```php
's3-videos' => [
    'driver' => 'scoped',
    'disk' => 's3',
    'prefix' => 'path/to/videos',
],
```

"Read-only" disks allow you to create filesystem disks that do not allow write operations. Before using the `read-only` configuration option, you will need to install an additional Flysystem package via the Composer package manager:

```shell
composer require league/flysystem-read-only "^3.0"
```

Next, you may include the `read-only` configuration option in one or more of your disk's configuration arrays:

```php
's3-videos' => [
    'driver' => 's3',
    // ...
    'read-only' => true,
],
```

### Amazon S3 Compatible Filesystems

By default, your application's `filesystems` configuration file contains a disk configuration for the `s3` disk. In addition to using this disk to interact with [Amazon S3](https://aws.amazon.com/s3/), you may use it to interact with any S3-compatible file storage service such as [RustFS](https://github.com/rustfs/rustfs), [DigitalOcean Spaces](https://www.digitalocean.com/products/spaces/), [Vultr Object Storage](https://www.vultr.com/products/object-storage/), [Cloudflare R2](https://www.cloudflare.com/developer-platform/products/r2/), or [Hetzner Cloud Storage](https://www.hetzner.com/storage/object-storage/).

Typically, after updating the disk's credentials to match the credentials of the service you are planning to use, you only need to update the value of the `endpoint` configuration option. This option's value is typically defined via the `AWS_ENDPOINT` environment variable:

```php
'endpoint' => env('AWS_ENDPOINT', 'https://rustfs:9000'),
```

## Obtaining Disk Instances

The global `storage` function returns the application's `Voyager\Filesystem\Storage` instance, which may be used to interact with any of your configured disks. `Storage` is an ordinary object rather than a static entry point. For example, you may use the `put` method to store an avatar on the default disk. If you call disk methods on `Storage` without first calling the `disk` method, the method will automatically be passed to the default disk:

```php
storage()->put('avatars/1', $content);
```

If your application interacts with multiple disks, you may use the `disk` method to work with files on a particular disk:

```php
storage()->disk('s3')->put('avatars/1', $content);
```

The filesystem manager behind `Storage` is registered in the service container as `filesystem`, and is also available from `storage()->manager()`. The default disk is registered as `filesystem.disk`, and the plain local filesystem, which works with absolute paths rather than disks, as `files`.

<a id="on-demand-disks"></a>
### On-Demand Disks

Sometimes you may wish to create a disk at runtime using a given configuration without that configuration actually being present in your application's `filesystems` configuration file. To accomplish this, you may pass a configuration array to the `build` method:

```php
$disk = storage()->build([
    'driver' => 'local',
    'root' => '/path/to/root',
]);

$disk->put('image.jpg', $content);
```

You may also pass just a root directory, which builds a `local` disk rooted there:

```php
$disk = storage()->build('/path/to/root');
```

## Retrieving Files

The `get` method may be used to retrieve the contents of a file. The raw string contents of the file will be returned by the method. Remember, all file paths should be specified relative to the disk's "root" location:

```php
$contents = storage()->get('file.jpg');
```

If the file you are retrieving contains JSON, you may use the `json` method to retrieve the file and decode its contents:

```php
$orders = storage()->json('orders.json');
```

The `readRange` method reads a given number of bytes starting at a given byte offset, without loading the rest of the file:

```php
$header = storage()->readRange('video.mp4', 0, 4096);
```

The `exists` method may be used to determine if a file exists on the disk:

```php
if (storage()->disk('s3')->exists('file.jpg')) {
    // ...
}
```

The `missing` method may be used to determine if a file is missing from the disk:

```php
if (storage()->disk('s3')->missing('file.jpg')) {
    // ...
}
```

<a id="file-urls"></a>
### File URLs

You may use the `url` method to get the URL for a given file. If you are using the `local` driver, this will typically just prepend `/storage` to the given path and return a relative URL to the file. If you are using the `s3` driver, the fully qualified remote URL will be returned:

```php
$url = storage()->url('file.jpg');
```

> [!WARNING]
> When using the `local` driver, the return value of `url` is not URL encoded. For this reason, we recommend always storing your files using names that will create valid URLs.

#### URL Host Customization

If you would like to modify the host for URLs generated by a disk, you may add or change the `url` option in the disk's configuration array:

```php
'public' => [
    'driver' => 'local',
    'root' => storage_path('app/public'),
    'url' => env('APP_URL').'/storage',
    'visibility' => 'public',
    'throw' => false,
],
```

### Temporary URLs

Using the `temporaryUrl` method, you may create temporary URLs to files stored using the `s3` driver. This method accepts a path and a `DateTime` instance specifying when the URL should expire:

```php
$url = storage()->disk('s3')->temporaryUrl(
    'file.jpg', now()->plus(minutes: 5)
);
```

If you would like temporary URLs to point at a different host than the presigned URL S3 returns, set the `temporary_url` option in the disk's configuration array; its scheme, host, and port replace those of every temporary URL the disk creates.

#### S3 Request Parameters

If you need to specify additional [S3 request parameters](https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectGET.html#RESTObjectGET-requests), you may pass the array of request parameters as the third argument to the `temporaryUrl` method:

```php
$url = storage()->disk('s3')->temporaryUrl(
    'file.jpg',
    now()->plus(minutes: 5),
    [
        'ResponseContentType' => 'application/octet-stream',
        'ResponseContentDisposition' => 'attachment; filename=file2.jpg',
    ]
);
```

#### Customizing Temporary URLs

If you need to create temporary URLs for a disk whose driver doesn't support them, such as a `local` disk served by your own file server, you can use the `buildTemporaryUrlsUsing` method. The callback receives the path, the expiration, and the options passed to `temporaryUrl`, and returns the URL. Usually, this method should be called from the `boot` method of a service provider:

```php
<?php

namespace App\Providers;

use DateTimeInterface;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        storage()->disk('local')->buildTemporaryUrlsUsing(
            function (string $path, DateTimeInterface $expiration, array $options) {
                $expires = $expiration->getTimestamp();
                $signature = hash_hmac('sha256', "{$path}|{$expires}", config('app.key'));

                return "https://files.example.com/{$path}?expires={$expires}&signature={$signature}";
            }
        );
    }
}
```

The `providesTemporaryUrls` method tells you whether a disk can create temporary URLs, either natively or through such a callback.

#### Temporary Upload URLs

> [!WARNING]
> The ability to generate temporary upload URLs is only supported by the `s3` driver, or by a disk given a callback with `buildTemporaryUploadUrlsUsing`.

If you need to generate a temporary URL that can be used to upload a file directly from a client, you may use the `temporaryUploadUrl` method. This method accepts a path and a `DateTime` instance specifying when the URL should expire. The `temporaryUploadUrl` method returns an associative array which may be destructured into the upload URL and the headers that should be included with the upload request:

```php
['url' => $url, 'headers' => $headers] = storage()->disk('s3')->temporaryUploadUrl(
    'file.jpg', now()->plus(minutes: 5)
);
```

This method is primarily useful when a client must upload files directly to a cloud storage system such as Amazon S3.

### File Metadata

In addition to reading and writing files, Venusian can also provide information about the files themselves. For example, the `size` method may be used to get the size of a file in bytes:

```php
$size = storage()->size('file.jpg');
```

The `lastModified` method returns the UNIX timestamp of the last time the file was modified:

```php
$time = storage()->lastModified('file.jpg');
```

The MIME type of a given file may be obtained via the `mimeType` method:

```php
$mime = storage()->mimeType('file.jpg');
```

The `checksum` method returns a checksum of the file's contents, which you may compare against another copy without reading both:

```php
$checksum = storage()->checksum('file.jpg');
```

#### File Paths

You may use the `path` method to get the path for a given file. If you are using the `local` driver, this will return the absolute path to the file. If you are using the `s3` driver, this method will return the relative path to the file in the S3 bucket:

```php
$path = storage()->path('file.jpg');
```

## Storing Files

The `put` method may be used to store file contents on a disk. You may also pass a PHP `resource` to the `put` method, which will use Flysystem's underlying stream support. Remember, all file paths should be specified relative to the "root" location configured for the disk:

```php
storage()->put('file.jpg', $contents);

storage()->put('file.jpg', $resource);
```

#### Failed Writes

If the `put` method (or other "write" operations) is unable to write the file to disk, `false` will be returned:

```php
if (! storage()->put('file.jpg', $contents)) {
    // The file could not be written to disk...
}
```

If you wish, you may define the `throw` option within your filesystem disk's configuration array. When this option is defined as `true`, "write" methods such as `put` will throw an instance of `League\Flysystem\UnableToWriteFile` when write operations fail:

```php
'public' => [
    'driver' => 'local',
    // ...
    'throw' => true,
],
```

Alternatively, you may define the `report` option within your filesystem disk's configuration array. When this option is defined as `true`, Venusian will report the underlying exception to your application's exception handler when a "write" operation fails, without throwing the exception or interrupting the write operation's return value:

```php
'public' => [
    'driver' => 'local',
    // ...
    'report' => true,
],
```

If neither the `throw` nor `report` options are defined, the disk will silently return `false` on failure and the underlying exception will not be thrown or logged.

### Prepending and Appending To Files

The `prepend` and `append` methods allow you to write to the beginning or end of a file:

```php
storage()->prepend('file.log', 'Prepended Text');

storage()->append('file.log', 'Appended Text');
```

### Copying and Moving Files

The `copy` method may be used to copy an existing file to a new location on the disk, while the `move` method may be used to rename or move an existing file to a new location:

```php
storage()->copy('old/file.jpg', 'new/file.jpg');

storage()->move('old/file.jpg', 'new/file.jpg');
```

### Automatic Streaming

Streaming files to storage offers significantly reduced memory usage. If you would like Venusian to automatically manage streaming a file on this machine to your storage location, you may use the `putFile` or `putFileAs` method. These methods accept the file's local path and will automatically stream the file to your desired location:

```php
// Automatically generate a unique ID for filename...
$path = storage()->putFile('photos', '/path/to/photo.jpg');

// Manually specify a filename...
$path = storage()->putFileAs('photos', '/path/to/photo.jpg', 'photo.jpg');
```

There are a few important things to note about the `putFile` method. Note that we only specified a directory name and not a filename. By default, the `putFile` method will generate a random 40 character name to serve as the filename. The file's extension will be determined by examining the file's MIME type. The path to the file will be returned by the `putFile` method so you can store the path, including the generated filename, in your database.

The `putFile` and `putFileAs` methods also accept an argument to specify the "visibility" of the stored file. This is particularly useful if you are storing the file on a cloud disk such as Amazon S3 and would like the file to be publicly accessible via generated URLs:

```php
storage()->putFile('photos', '/path/to/photo.jpg', 'public');
```

> [!WARNING]
> Unprintable and invalid unicode characters will automatically be removed from file paths. Therefore, you may wish to sanitize your file paths before passing them to Venusian's file storage methods. File paths are normalized using the `League\Flysystem\WhitespacePathNormalizer::normalizePath` method.

<a id="file-visibility"></a>
### File Visibility

In Venusian's Flysystem integration, "visibility" is an abstraction of file permissions across multiple platforms. Files may either be declared `public` or `private`. When a file is declared `public`, you are indicating that the file should generally be accessible to others. For example, when using the S3 driver, you may retrieve URLs for `public` files.

You can set the visibility when writing the file via the `put` method:

```php
storage()->put('file.jpg', $contents, 'public');
```

If the file has already been stored, its visibility can be retrieved and set via the `getVisibility` and `setVisibility` methods:

```php
$visibility = storage()->getVisibility('file.jpg');

storage()->setVisibility('file.jpg', 'public');
```

#### Local Files and Visibility

When using the `local` driver, `public` [visibility](#file-visibility) translates to `0755` permissions for directories and `0644` permissions for files. You can modify the permissions mappings in your application's `filesystems` configuration file:

```php
'local' => [
    'driver' => 'local',
    'root' => storage_path('app'),
    'permissions' => [
        'file' => [
            'public' => 0644,
            'private' => 0600,
        ],
        'dir' => [
            'public' => 0755,
            'private' => 0700,
        ],
    ],
    'throw' => false,
],
```

## Deleting Files

The `delete` method accepts a single filename or an array of files to delete:

```php
storage()->delete('file.jpg');

storage()->delete(['file.jpg', 'file2.jpg']);
```

If necessary, you may specify the disk that the file should be deleted from:

```php
storage()->disk('s3')->delete('path/file.jpg');
```

## Directories

#### Get All Files Within a Directory

The `files` method returns an array of all files within a given directory. If you would like to retrieve a list of all files within a given directory including subdirectories, you may use the `allFiles` method:

```php
$files = storage()->files($directory);

$files = storage()->allFiles($directory);
```

#### Get All Directories Within a Directory

The `directories` method returns an array of all directories within a given directory. If you would like to retrieve a list of all directories within a given directory including subdirectories, you may use the `allDirectories` method:

```php
$directories = storage()->directories($directory);

$directories = storage()->allDirectories($directory);
```

#### Create a Directory

The `makeDirectory` method will create the given directory, including any needed subdirectories:

```php
storage()->makeDirectory($directory);
```

#### Delete a Directory

Finally, the `deleteDirectory` method may be used to remove a directory and all of its files:

```php
storage()->deleteDirectory($directory);
```

## Offloading to a Worker Pool

Every disk call above blocks the calling process until the storage answers. When your application runs on the event loop, the `via` method returns a `Voyager\Filesystem\OffloadedDisk`: the same disk with each call run in a worker pool and answered by a `Voyager\Contracts\IOPools\Promise`. Each method takes the same arguments as the blocking method of the same name, and its promise resolves with what that method returns:

```php
$disk = storage()->disk('s3')->via();

$disk->put('reports/daily.csv', $csv);

$disk->get('reports/daily.csv')->then(function (?string $contents) {
    // ...
});

$exists = $disk->exists('reports/daily.csv')->wait();
```

`storage()->via()` offloads the default disk. With no argument, `via` uses the thread pool when `io-pools.pool_workers.threads` is enabled and the process pool otherwise; pass `'thread'` or `'process'` to choose one. If the pool is not enabled in your `config/io-pools.php` file, `via` throws an `InvalidArgumentException`. When the blocking method would throw, the promise rejects with a `Voyager\Contracts\IOPools\WorkerPools\RemoteException` carrying the worker's message:

```php
use Voyager\Contracts\IOPools\WorkerPools\RemoteException;

$disk = storage()->disk('local')->via('process');

try {
    $disk->get('missing.txt')->wait();
} catch (RemoteException $e) {
    // ...
}
```

The worker builds the disk from this disk's configuration, so an [on-demand disk](#on-demand-disks) or a [fake](#testing) offloads like any other. A disk whose configuration holds something that cannot cross to a worker, such as a closure, cannot be offloaded and `via` throws an `InvalidArgumentException`. For the same reason, only data crosses: arguments must be strings, numbers, booleans, `null`, or arrays of them, and file contents travel as strings. Offloaded disks therefore have no `readStream` or `writeStream`; use [`stream`](#streaming-a-file-as-mail) to read a file in chunks, and `putFile` / `putFileAs` with a local path, which the worker opens itself:

```php
$path = storage()->disk('s3')->via()->putFile('uploads', '/path/to/photo.jpg')->wait();
```

`path`, `url`, and the temporary URL methods are worked out from the disk's configuration without touching the storage, so they stay on the blocking disk.

#### Call Order

Calls on the same path complete in the order they were made, and a call on a directory waits for the calls inside it; calls on unrelated paths run side by side. Once a disk has been offloaded, its blocking methods also wait for the offloaded calls on their paths, so you may freely mix the two:

```php
storage()->disk('local')->via()->put('handed-over.txt', 'offloaded write');

storage()->disk('local')->get('handed-over.txt'); // "offloaded write"
```

### Offloading the Local Filesystem

The plain local filesystem registered as `files` has a `via` method of its own, which returns a `Voyager\Filesystem\OffloadedFiles` for absolute paths. It follows the same pool, data, and ordering rules as an offloaded disk:

```php
$files = app('files')->via();

$files->put('/var/data/report.txt', $contents);

$files->allFiles('/var/data')->then(function (array $found) {
    // ...
});
```

### Streaming a File as Mail

The `stream` method on an offloaded disk or offloaded local filesystem reads a file a chunk at a time and hands each chunk to your application as loop mail. Each chunk is dispatched as a `Voyager\Filesystem\FileChunk` [signal](/docs/{{version}}/framework/digging-deeper/signals) named `disk:{disk}:{path}` for a disk and `file:{path}` for the local filesystem, oldest first, carrying its `source`, `path`, `offset`, `bytes`, and a `last` flag on the final chunk. The promise resolves with the number of bytes read:

```php
use Voyager\Contracts\IOPools\Loop;
use Voyager\Filesystem\FileChunk;

app('signals')->listen('disk:local:exports/large.bin', function (FileChunk $chunk) {
    // $chunk->offset, $chunk->bytes...

    if ($chunk->last) {
        // ...
    }
});

$read = storage()->disk('local')->via()->stream('exports/large.bin');

app(Loop::class)->run();
```

Chunks are 1 MiB unless you pass a different size as the second argument. An empty file arrives as a single, empty, last chunk. The path is held while it streams, so a write to it made meanwhile lands after the last chunk.

<a id="testing"></a>
## Testing

The `fake` method on `Storage` swaps a disk for an empty local disk under `storage/framework/testing/disks/{disk}`, and the disk's assertion methods greatly simplify testing code that stores files. For example:

```php
<?php

test('albums can be stored', function () {
    storage()->fake('photos');

    storage()->disk('photos')->put('photo1.jpg', 'first');
    storage()->disk('photos')->put('photo2.jpg', 'second');
    storage()->disk('photos')->put('wallpapers/beach.jpg', 'beach');
    storage()->disk('photos')->put('wallpapers/forest.jpg', 'forest');
    storage()->disk('photos')->makeDirectory('drafts');

    // Assert one or more files were stored...
    storage()->disk('photos')->assertExists('photo1.jpg');
    storage()->disk('photos')->assertExists(['photo1.jpg', 'photo2.jpg']);

    // Assert a file was stored with the given contents...
    storage()->disk('photos')->assertExists('photo1.jpg', 'first');

    // Assert one or more files were not stored...
    storage()->disk('photos')->assertMissing('missing.jpg');
    storage()->disk('photos')->assertMissing(['missing.jpg', 'non-existing.jpg']);

    // Assert that the number of files in a given directory matches the expected count...
    storage()->disk('photos')->assertCount('/wallpapers', 2);

    // Assert that a given directory is empty...
    storage()->disk('photos')->assertDirectoryEmpty('/drafts');
});
```

By default, the `fake` method will delete all files in its temporary directory. If you would like to keep these files, you may use the `persistentFake` method instead.

## Custom Filesystems

Venusian's Flysystem integration provides support for several "drivers" out of the box; however, Flysystem is not limited to these and has adapters for many other storage systems. You can create a custom driver if you want to use one of these additional adapters in your Venusian application.

In order to define a custom filesystem you will need a Flysystem adapter. Let's add a community maintained Dropbox adapter to our project:

```shell
composer require spatie/flysystem-dropbox
```

Next, you can register the driver within the `boot` method of one of your application's [service providers](/docs/{{version}}/framework/architecture-concepts/providers). To accomplish this, you should use the `extend` method of the filesystem manager:

```php
<?php

namespace App\Providers;

use League\Flysystem\Filesystem;
use Spatie\Dropbox\Client as DropboxClient;
use Spatie\FlysystemDropbox\DropboxAdapter;
use Voyager\Contracts\Core\FrameworkCore;
use Voyager\Filesystem\FilesystemAdapter;
use Voyager\NutsAndBolts\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // ...
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        storage()->manager()->extend('dropbox', function (FrameworkCore $app, array $config) {
            $adapter = new DropboxAdapter(new DropboxClient(
                $config['authorization_token']
            ));

            return new FilesystemAdapter(
                new Filesystem($adapter, $config),
                $adapter,
                $config
            );
        });
    }
}
```

The first argument of the `extend` method is the name of the driver and the second is a closure that receives the `$app` and `$config` variables. The closure must return an instance of `Voyager\Filesystem\FilesystemAdapter`. The `$config` variable contains the values defined in `config/filesystems.php` for the specified disk.

Once you have created and registered the extension's service provider, you may use the `dropbox` driver in your `config/filesystems.php` configuration file.
