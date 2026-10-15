# Processes

Venusian provides an expressive, minimal API around the Symfony Process component, for invoking external processes blocking or on the event loop.

## Introduction

Venusian provides an expressive, minimal API around the [Symfony Process component](https://symfony.com/doc/current/components/process.html), allowing you to conveniently invoke external processes from your Venusian application. Venusian's process features are focused on the most common use cases and a wonderful developer experience.

Processes are built by a `Voyager\Process\Factory`. The factory needs no configuration, so you may create one yourself or have the container inject one wherever you need it:

```php
use Voyager\Process\Factory;

$processes = new Factory;
```

The examples on this page call methods on that `$processes` factory.

## Invoking Processes

To invoke a process, you may use the `run` and `start` methods offered by the factory. The `run` method will invoke a process and wait for the process to finish executing, while the `start` method is used for asynchronous process execution. We'll examine both approaches within this documentation. First, let's examine how to invoke a basic, synchronous process and inspect its result:

```php
$result = $processes->run('ls -la');

echo $result->output();
```

Of course, the `Voyager\Contracts\Process\ProcessResult` instance returned by the `run` method offers a variety of helpful methods that may be used to inspect the process result:

```php
$result = $processes->run('ls -la');

$result->command();
$result->successful();
$result->failed();
$result->output();
$result->errorOutput();
$result->exitCode();
```

#### Throwing Exceptions

If you have a process result and would like to throw an instance of `Voyager\Process\Exceptions\ProcessFailedException` if the exit code is greater than zero (thus indicating failure), you may use the `throw` and `throwIf` methods. If the process did not fail, the `ProcessResult` instance will be returned:

```php
$result = $processes->run('ls -la')->throw();

$result = $processes->run('ls -la')->throwIf($condition);
```

### Process Options

Of course, you may need to customize the behavior of a process before invoking it. Thankfully, Venusian allows you to tweak a variety of process features, such as the working directory, timeout, and environment variables.

#### Working Directory Path

You may use the `path` method to specify the working directory of the process. If this method is not invoked, the process will inherit the working directory of the currently executing PHP script:

```php
$result = $processes->path(__DIR__)->run('ls -la');
```

#### Input

You may provide input via the "standard input" of the process using the `input` method:

```php
$result = $processes->input('Hello World')->run('cat');
```

<a id="timeouts"></a>
#### Timeouts

By default, processes will throw an instance of `Voyager\Process\Exceptions\ProcessTimedOutException` after executing for more than 60 seconds. However, you can customize this behavior via the `timeout` method:

```php
$result = $processes->timeout(120)->run('bash import.sh');
```

Or, if you would like to disable the process timeout entirely, you may invoke the `forever` method:

```php
$result = $processes->forever()->run('bash import.sh');
```

The `idleTimeout` method may be used to specify the maximum number of seconds the process may run without returning any output:

```php
$result = $processes->timeout(60)->idleTimeout(30)->run('bash import.sh');
```

#### Environment Variables

Environment variables may be provided to the process via the `env` method. The invoked process will also inherit all of the environment variables defined by your system:

```php
$result = $processes->forever()
    ->env(['IMPORT_PATH' => __DIR__])
    ->run('bash import.sh');
```

If you wish to remove an inherited environment variable from the invoked process, you may provide that environment variable with a value of `false`:

```php
$result = $processes->forever()
    ->env(['LOAD_PATH' => false])
    ->run('bash import.sh');
```

#### TTY Mode

The `tty` method may be used to enable TTY mode for your process. TTY mode connects the input and output of the process to the input and output of your program, allowing your process to open an editor like Vim or Nano as a process:

```php
$processes->forever()->tty()->run('vim');
```

> [!WARNING]
> TTY mode is not supported on Windows.

### Process Output

As previously discussed, process output may be accessed using the `output` (stdout) and `errorOutput` (stderr) methods on a process result:

```php
$result = $processes->run('ls -la');

echo $result->output();
echo $result->errorOutput();
```

However, output may also be gathered in real-time by passing a closure as the second argument to the `run` method. The closure will receive two arguments: the "type" of output (`stdout` or `stderr`) and the output string itself:

```php
$result = $processes->run('ls -la', function (string $type, string $output) {
    echo $output;
});
```

The result also offers the `seeInOutput` and `seeInErrorOutput` methods, which provide a convenient way to determine if a given string was contained in the process' output:

```php
if ($processes->run('ls -la')->seeInOutput('venusian')) {
    // ...
}
```

<a id="disabling-process-output"></a>
#### Disabling Process Output

If your process is writing a significant amount of output that you are not interested in, you can conserve memory by disabling output retrieval entirely. To accomplish this, invoke the `quietly` method while building the process:

```php
$result = $processes->quietly()->run('bash import.sh');
```

### Pipelines

Sometimes you may want to make the output of one process the input of another process. This is often referred to as "piping" the output of a process into another. The factory's `pipe` method makes this easy to accomplish. The `pipe` method will execute the piped processes synchronously and return the process result for the last process in the pipeline:

```php
use Voyager\Process\Pipe;
$result = $processes->pipe(function (Pipe $pipe) {
    $pipe->command('cat example.txt');
    $pipe->command('grep -i "venusian"');
});

if ($result->successful()) {
    // ...
}
```

If you do not need to customize the individual processes that make up the pipeline, you may simply pass an array of command strings to the `pipe` method:

```php
$result = $processes->pipe([
    'cat example.txt',
    'grep -i "venusian"',
]);
```

The process output may be gathered in real-time by passing a closure as the second argument to the `pipe` method. The closure will receive two arguments: the "type" of output (`stdout` or `stderr`) and the output string itself:

```php
$result = $processes->pipe(function (Pipe $pipe) {
    $pipe->command('cat example.txt');
    $pipe->command('grep -i "venusian"');
}, function (string $type, string $output) {
    echo $output;
});
```

You may also assign string keys to each process within a pipeline via the `as` method. This key will also be passed to the output closure provided to the `pipe` method, allowing you to determine which process the output belongs to:

```php
$result = $processes->pipe(function (Pipe $pipe) {
    $pipe->as('first')->command('cat example.txt');
    $pipe->as('second')->command('grep -i "venusian"');
}, function (string $type, string $output, string $key) {
    // ...
});
```

## Asynchronous Processes

While the `run` method invokes processes synchronously, the `start` method may be used to invoke a process asynchronously. This allows your application to continue performing other tasks while the process runs in the background. Once the process has been invoked, you may utilize the `running` method to determine if the process is still running:

```php
$process = $processes->timeout(120)->start('bash import.sh');

while ($process->running()) {
    // ...
}

$result = $process->wait();
```

As you may have noticed, you may invoke the `wait` method to wait until the process is finished executing and retrieve the `ProcessResult` instance:

```php
$process = $processes->timeout(120)->start('bash import.sh');

// ...

$result = $process->wait();
```

### Process IDs and Signals

The `id` method may be used to retrieve the operating system assigned process ID of the running process:

```php
$process = $processes->start('bash import.sh');

echo $process->id();
```

You may use the `signal` method to send a "signal" to the running process. A list of predefined signal constants can be found within the [PHP documentation](https://www.php.net/manual/en/pcntl.constants.php):

```php
$process->signal(SIGUSR2);
```

### Asynchronous Process Output

While an asynchronous process is running, you may access its entire current output using the `output` and `errorOutput` methods; however, you may utilize the `latestOutput` and `latestErrorOutput` to access the output from the process that has occurred since the output was last retrieved:

```php
$process = $processes->timeout(120)->start('bash import.sh');

while ($process->running()) {
    echo $process->latestOutput();
    echo $process->latestErrorOutput();

    sleep(1);
}
```

Like the `run` method, output may also be gathered in real-time from asynchronous processes by passing a closure as the second argument to the `start` method. The closure will receive two arguments: the "type" of output (`stdout` or `stderr`) and the output string itself:

```php
$process = $processes->start('bash import.sh', function (string $type, string $output) {
    echo $output;
});

$result = $process->wait();
```

Instead of waiting until the process has finished, you may use the `waitUntil` method to stop waiting based on the output of the process. The process will stop being waited on to finish when the closure given to the `waitUntil` method returns `true`:

```php
$process = $processes->start('bash import.sh');

$process->waitUntil(function (string $type, string $output) {
    return $output === 'Ready...';
});
```

### Asynchronous Process Timeouts

While an asynchronous process is running, you may verify that the process has not timed out using the `ensureNotTimedOut` method. This method will throw a [timeout exception](#timeouts) if the process has timed out:

```php
$process = $processes->timeout(120)->start('bash import.sh');

while ($process->running()) {
    $process->ensureNotTimedOut();

    // ...

    sleep(1);
}
```

## Concurrent Processes

Venusian also makes it a breeze to manage a pool of concurrent, asynchronous processes, allowing you to easily execute many tasks simultaneously. To get started, invoke the `pool` method, which accepts a closure that receives an instance of `Voyager\Process\Pool`.

Within this closure, you may define the processes that belong to the pool. Once a process pool is started via the `start` method, you may access the [collection](/docs/{{version}}/framework/digging-deeper/collections) of running processes via the `running` method:

```php
use Voyager\Process\Pool;
$pool = $processes->pool(function (Pool $pool) {
    $pool->path(__DIR__)->command('bash import-1.sh');
    $pool->path(__DIR__)->command('bash import-2.sh');
    $pool->path(__DIR__)->command('bash import-3.sh');
})->start(function (string $type, string $output, int $key) {
    // ...
});

while ($pool->running()->isNotEmpty()) {
    // ...
}

$results = $pool->wait();
```

As you can see, you may wait for all of the pool processes to finish executing and resolve their results via the `wait` method. The `wait` method returns an array accessible object that allows you to access the `ProcessResult` instance of each process in the pool by its key:

```php
$results = $pool->wait();

echo $results[0]->output();
```

Or, for convenience, the `concurrently` method may be used to start an asynchronous process pool and immediately wait on its results. This can provide particularly expressive syntax when combined with PHP's array destructuring capabilities:

```php
[$first, $second, $third] = $processes->concurrently(function (Pool $pool) {
    $pool->path(__DIR__)->command('ls -la');
    $pool->path(app_path())->command('ls -la');
    $pool->path(storage_path())->command('ls -la');
});

echo $first->output();
```

### Naming Pool Processes

Accessing process pool results via a numeric key is not very expressive; therefore, you may assign string keys to each process within a pool via the `as` method. This key will also be passed to the closure provided to the `start` method, allowing you to determine which process the output belongs to:

```php
$pool = $processes->pool(function (Pool $pool) {
    $pool->as('first')->command('bash import-1.sh');
    $pool->as('second')->command('bash import-2.sh');
    $pool->as('third')->command('bash import-3.sh');
})->start(function (string $type, string $output, string $key) {
    // ...
});

$results = $pool->wait();

echo $results['first']->output();
```

### Pool Process IDs and Signals

Since the process pool's `running` method provides a collection of all invoked processes within the pool, you may easily access the underlying pool process IDs:

```php
$processIds = $pool->running()->map->id();
```

And, for convenience, you may invoke the `signal` method on a process pool to send a signal to every process within the pool:

```php
$pool->signal(SIGUSR2);
```

## Waiting on the Event Loop

The `wait` method blocks until the process exits. When your code runs on the event loop, you may instead wait without blocking. The `waitAsync` method of a started process returns a `Voyager\Contracts\IOPools\Promise` at once, and the loop keeps turning until the process exits:

```php
$process = $processes->timeout(120)->start('bash import.sh');

$process->waitAsync()->then(function ($result) {
    echo $result->output();
});
```

The promise is fulfilled with the process's `ProcessResult`, whatever its exit code, or rejected with a `ProcessTimedOutException` if the process runs past its timeout; a timed-out process is stopped. Calling `waitAsync` again on the same process returns the same promise. If you need to block for the outcome, the promise's `wait` method returns the result or throws the exception.

The `runAsync` method starts the process and waits on it through the loop in one call:

```php
$promise = $processes->timeout(120)->runAsync('bash import.sh');
```

Both methods accept an output closure, which receives the "type" of output (`stdout` or `stderr`) and the output string as the output arrives. A closure given to `waitAsync` receives the output read from then on. Output closures may not be used with a [quiet](#disabling-process-output) process; `waitAsync` rejects with a `LogicException` instead:

```php
$process->waitAsync(function (string $type, string $output) {
    echo $output;
});
```

The process's exit wakes the loop: the `kqueue` waiter watches the process directly, and with the other waiters the exit arrives as `SIGCHLD`, which needs the `pcntl` extension. A process timeout is a single deadline, checked once when it runs out.

### Pools and Pipelines on the Loop

Pools and pipelines may wait on the loop as well. A pool's `runAsync` method, or the factory's `concurrentlyAsync` method, starts every process in the pool and returns a promise of the pool's results, keyed as the pool was. If any process fails to be waited on, such as by timing out, the promise is rejected with the first such failure:

```php
use Voyager\Process\Pool;

$processes->concurrentlyAsync(function (Pool $pool) {
    $pool->as('first')->command('bash import-1.sh');
    $pool->as('second')->command('bash import-2.sh');
})->then(function ($results) {
    echo $results['first']->output();
});
```

A pool that has already been started may be waited on through the loop with the `waitAsync` method of the `InvokedProcessPool` returned by `start`:

```php
$results = $processes->pool(function (Pool $pool) {
    // ...
})->start()->waitAsync();
```

The factory's `pipeAsync` method runs a pipeline without blocking. Each process starts once the one before it has finished, receiving its output as input, and the pipeline ends at the first process that fails. The promise is fulfilled with the result of the last process that ran:

```php
use Voyager\Process\Pipe;

$processes->pipeAsync(function (Pipe $pipe) {
    $pipe->command('cat example.txt');
    $pipe->command('grep -i "venusian"');
})->then(function ($result) {
    // ...
});
```

## Testing

The process factory can fake the processes it invokes, returning stubbed / dummy results instead of starting real processes, and can assert which processes were invoked.

<a id="faking-processes"></a>
### Faking Processes

Since faking is done on a factory instance, the code you are testing should receive its factory from the container, for example through constructor injection:

```php
use Voyager\Process\Factory;

class Importer
{
    public function __construct(protected Factory $processes) {}

    public function import(): void
    {
        $this->processes->run('bash import.sh');
    }
}
```

In your test, create a factory, call its `fake` method, and register it in the container so that the code under test receives it. Calling `fake` with no arguments returns a fake, successful process result for every invoked process. In addition, we can even [assert](#available-assertions) that a given process was "run":

```php
<?php

use Voyager\Contracts\Process\ProcessResult;
use Voyager\Process\Factory;
use Voyager\Process\PendingProcess;

test('process is invoked', function () {
    $processes = (new Factory)->fake();

    app()->registerInstance(Factory::class, $processes);

    app(Importer::class)->import();

    // Simple process assertion...
    $processes->assertRan('bash import.sh');

    // Or, inspecting the process configuration...
    $processes->assertRan(function (PendingProcess $process, ProcessResult $result) {
        return $process->command === 'bash import.sh' &&
               $process->timeout === 60;
    });
});
```

As discussed, invoking the `fake` method with no arguments will always return a successful process result with no output. However, you may easily specify the output and exit code for faked processes using the factory's `result` method:

```php
$processes->fake([
    '*' => $processes->result(
        output: 'Test output',
        errorOutput: 'Test error output',
        exitCode: 1,
    ),
]);
```

Faked processes work the same way through `runAsync` and `waitAsync`: the promise is fulfilled with the fake result.

### Faking Specific Processes

As you may have noticed in a previous example, the factory allows you to specify different fake results per process by passing an array to the `fake` method.

The array's keys should represent command patterns that you wish to fake and their associated results. The `*` character may be used as a wildcard character. Any process commands that have not been faked will actually be invoked. You may use the factory's `result` method to construct stub / fake results for these commands:

```php
$processes->fake([
    'cat *' => $processes->result(
        output: 'Test "cat" output',
    ),
    'ls *' => $processes->result(
        output: 'Test "ls" output',
    ),
]);
```

If you do not need to customize the exit code or error output of a faked process, you may find it more convenient to specify the fake process results as simple strings:

```php
$processes->fake([
    'cat *' => 'Test "cat" output',
    'ls *' => 'Test "ls" output',
]);
```

### Faking Process Sequences

If the code you are testing invokes multiple processes with the same command, you may wish to assign a different fake process result to each process invocation. You may accomplish this via the factory's `sequence` method:

```php
$processes->fake([
    'ls *' => $processes->sequence()
        ->push($processes->result('First invocation'))
        ->push($processes->result('Second invocation')),
]);
```

### Faking Asynchronous Process Lifecycles

Thus far, we have primarily discussed faking processes which are invoked synchronously using the `run` method. However, if you are attempting to test code that interacts with asynchronous processes invoked via `start`, you may need a more sophisticated approach to describing your fake processes.

For example, let's imagine the following code which interacts with an asynchronous process:

```php
$process = $this->processes->start('bash import.sh');

while ($process->running()) {
    app('log')->info($process->latestOutput());
    app('log')->info($process->latestErrorOutput());
}
```

To properly fake this process, we need to be able to describe how many times the `running` method should return `true`. In addition, we may want to specify multiple lines of output that should be returned in sequence. To accomplish this, we can use the factory's `describe` method:

```php
$processes->fake([
    'bash import.sh' => $processes->describe()
        ->output('First line of standard output')
        ->errorOutput('First line of error output')
        ->output('Second line of standard output')
        ->exitCode(0)
        ->iterations(3),
]);
```

Let's dig into the example above. Using the `output` and `errorOutput` methods, we may specify multiple lines of output that will be returned in sequence. The `exitCode` method may be used to specify the final exit code of the fake process. Finally, the `iterations` method may be used to specify how many times the `running` method should return `true`.

<a id="available-assertions"></a>
### Available Assertions

As [previously discussed](#faking-processes), the factory provides several process assertions for your tests. We'll discuss each of these assertions below.

#### assertRan

Assert that a given process was invoked:

```php
$processes->assertRan('ls -la');
```

The `assertRan` method also accepts a closure, which will receive an instance of a process and a process result, allowing you to inspect the process' configured options. If this closure returns `true`, the assertion will "pass":

```php
$processes->assertRan(fn ($process, $result) =>
    $process->command === 'ls -la' &&
    $process->path === __DIR__ &&
    $process->timeout === 60
);
```

The `$process` passed to the `assertRan` closure is an instance of `Voyager\Process\PendingProcess`, while the `$result` is an instance of `Voyager\Contracts\Process\ProcessResult`.

#### assertDidntRun

Assert that a given process was not invoked:

```php
$processes->assertDidntRun('ls -la');
```

Like the `assertRan` method, the `assertDidntRun` method also accepts a closure, which will receive an instance of a process and a process result, allowing you to inspect the process' configured options. If this closure returns `true`, the assertion will "fail":

```php
$processes->assertDidntRun(fn (PendingProcess $process, ProcessResult $result) =>
    $process->command === 'ls -la'
);
```

The `assertNotRan` method is an alias of `assertDidntRun`.

#### assertRanTimes

Assert that a given process was invoked a given number of times:

```php
$processes->assertRanTimes('ls -la', times: 3);
```

The `assertRanTimes` method also accepts a closure, which will receive an instance of `PendingProcess` and `ProcessResult`, allowing you to inspect the process' configured options. If this closure returns `true` and the process was invoked the specified number of times, the assertion will "pass":

```php
$processes->assertRanTimes(function (PendingProcess $process, ProcessResult $result) {
    return $process->command === 'ls -la';
}, times: 3);
```

#### assertNothingRan

Assert that no processes were invoked:

```php
$processes->assertNothingRan();
```

### Preventing Stray Processes

If you would like to ensure that all invoked processes have been faked throughout your individual test or complete test suite, you can call the `preventStrayProcesses` method. After calling this method, any processes that do not have a corresponding fake result will throw an exception rather than starting an actual process:

```php
$processes->preventStrayProcesses();

$processes->fake([
    'ls *' => 'Test output...',
]);

// Fake result is returned...
$processes->run('ls -la');

// An exception is thrown...
$processes->run('bash import.sh');
```
