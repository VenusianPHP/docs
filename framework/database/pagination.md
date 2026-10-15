# Database: Pagination

Venusian's paginators split query builder and Instrument results into pages, with no HTTP request behind them.

## Introduction

In other frameworks, pagination can be very painful. We hope Venusian's approach to pagination will be a breath of fresh air. Venusian's paginator is integrated with the [query builder](/docs/{{version}}/framework/database/queries) and [Instrument ORM](/docs/{{version}}/framework/instrument-orm/instrument) and provides convenient, easy-to-use pagination of database records with zero configuration.

Venusian has no HTTP request, so a paginator never reads the current page from a query string on its own. You pass the page you want, or you register a resolver that tells the paginator where the current page comes from. The paginators render no HTML either: they hand you the page's items, the page metadata, and a list of page links as plain data, which you can draw however your application draws things.

## Basic Usage

### Paginating Query Builder Results

There are several ways to paginate items. The simplest is by using the `paginate` method on the [query builder](/docs/{{version}}/framework/database/queries) or an [Instrument query](/docs/{{version}}/framework/instrument-orm/instrument). The `paginate` method automatically takes care of setting the query's "limit" and "offset" based on the current page.

In this example, the only argument passed to the `paginate` method is the number of items you would like displayed "per page". In this case, let's specify that we would like to display `15` items per page:

```php
$users = app('db')->table('users')->paginate(15);
```

The fourth argument is the page to retrieve. When you leave it out, the paginator asks its [current page resolver](#resolving-the-current-page), and falls back to page `1` when none is registered:

```php
$users = app('db')->table('users')->paginate(
    perPage: 15, columns: ['*'], pageName: 'page', page: 3
);
```

#### Simple Pagination

The `paginate` method counts the total number of records matched by the query before retrieving the records from the database. This is done so that the paginator knows how many pages of records there are in total. However, if you do not plan to show the total number of pages in your application's UI then the record count query is unnecessary.

Therefore, if you only need to display simple "Next" and "Previous" links in your application's UI, you may use the `simplePaginate` method to perform a single, efficient query:

```php
$users = app('db')->table('users')->simplePaginate(15);
```

### Paginating Instrument Results

You may also paginate [Instrument](/docs/{{version}}/framework/instrument-orm/instrument) queries. In this example, we will paginate the `App\Models\User` model and indicate that we plan to display 15 records per page. As you can see, the syntax is nearly identical to paginating query builder results:

```php
use App\Models\User;

$users = User::paginate(15);
```

Of course, you may call the `paginate` method after setting other constraints on the query, such as `where` clauses:

```php
$users = User::where('votes', '>', 100)->paginate(15);
```

You may also use the `simplePaginate` method when paginating Instrument models:

```php
$users = User::where('votes', '>', 100)->simplePaginate(15);
```

Similarly, you may use the `cursorPaginate` method to cursor paginate Instrument models:

```php
$users = User::where('votes', '>', 100)->cursorPaginate(15);
```

When you do not pass a per-page count to an Instrument query, the model's `getPerPage` method supplies it.

#### Multiple Paginator Instances per Page

Sometimes you may need two separate paginators on a single screen. If both paginator instances use the `page` name to store the current page, the two paginators will conflict. To resolve this conflict, you may pass the name you wish to use for the paginator's current page via the third argument provided to the `paginate`, `simplePaginate`, and `cursorPaginate` methods. The name is the key your page resolver receives and the query string variable in the URLs the paginator builds:

```php
use App\Models\User;

$users = User::where('votes', '>', 100)->paginate(
    $perPage = 15, $columns = ['*'], $pageName = 'users'
);
```

### Resolving the Current Page

When no page is passed, the paginator calls the resolver registered with the static `currentPageResolver` method. The resolver receives the page name and returns the page number. Register it once, for example in the `boot` method of a service provider, and change the page the closure reads whenever your application moves to another page:

```php
use Voyager\Pagination\Paginator;

$pages = ['page' => 1];

Paginator::currentPageResolver(function (string $pageName) use (&$pages) {
    return $pages[$pageName] ?? 1;
});
```

A page number that is not a positive integer is treated as page `1`. Cursor paginators use their own resolver, registered with `CursorPaginator::currentCursorResolver`, which receives the cursor name and returns a `Voyager\Pagination\Cursor` instance, or `null` for the first page. `Cursor::fromEncoded` turns an encoded cursor string back into an instance:

```php
use Voyager\Pagination\Cursor;
use Voyager\Pagination\CursorPaginator;

$cursors = [];

CursorPaginator::currentCursorResolver(function (string $cursorName) use (&$cursors) {
    return isset($cursors[$cursorName]) ? Cursor::fromEncoded($cursors[$cursorName]) : null;
});
```

Two more resolvers fill in what a request would otherwise supply: `Paginator::currentPathResolver` returns the base path used in page URLs (it defaults to `/`), and `Paginator::queryStringResolver` returns the array of query string values that [withQueryString](#appending-query-string-values) appends.

### Paginating on the Event Loop

A query builder or Instrument builder can run its paginator in a worker pool through `via()`, so the calling code keeps the event loop moving while the queries run. `paginate`, `simplePaginate`, and `cursorPaginate` are reads: they answer with a `Voyager\Contracts\IOPools\Promise` that fulfills with the same paginator the blocking call returns:

```php
use App\Models\User;
use Voyager\Pagination\LengthAwarePaginator;

User::where('votes', '>', 100)
    ->via()
    ->paginate(15, ['*'], 'page', 2)
    ->then(function (LengthAwarePaginator $users) {
        // ...
    });
```

`via()` accepts the pool to use, `'thread'` or `'process'`; without one it uses thread workers when they are bound and process workers otherwise. The paginated models arrive in the caller and fire their `retrieved` signals there. The page is serialized into the worker when the call is made, so pass it explicitly: a page resolver registered in the caller does not run in the worker. `via()` throws a `LogicException` for an in-memory SQLite connection, a connection with no name, and a connection with a transaction open: a worker opens its own connection, so it could not find an unnamed one, would open a different, empty in-memory database, and would run outside the open transaction.

### Cursor Pagination

While `paginate` and `simplePaginate` create queries using the SQL "offset" clause, cursor pagination works by constructing "where" clauses that compare the values of the ordered columns contained in the query, providing the most efficient database performance available amongst all of Venusian's pagination methods. This method of pagination is particularly well-suited for large data-sets and "infinite" scrolling user interfaces.

Unlike offset based pagination, which includes a page number in the query string of the URLs generated by the paginator, cursor-based pagination places a "cursor" string in the query string. The cursor is an encoded string containing the location that the next paginated query should start paginating and the direction that it should paginate:

```text
/users?cursor=eyJpZCI6MTUsIl9wb2ludHNUb05leHRJdGVtcyI6dHJ1ZX0
```

You may create a cursor-based paginator instance via the `cursorPaginate` method offered by the query builder. This method returns an instance of `Voyager\Pagination\CursorPaginator`:

```php
$users = app('db')->table('users')->orderBy('id')->cursorPaginate(15);
```

The fourth argument is the cursor to continue from, either the encoded string or a `Voyager\Pagination\Cursor` instance. When you leave it out, the paginator asks its [cursor resolver](#resolving-the-current-page):

```php
$next = app('db')->table('users')->orderBy('id')->cursorPaginate(
    15, ['*'], 'cursor', $users->nextCursor()
);
```

Once you have retrieved a cursor paginator instance, you may [display the pagination results](#displaying-pagination-results) as you typically would when using the `paginate` and `simplePaginate` methods. For more information on the instance methods offered by the cursor paginator, please consult the [cursor paginator instance method documentation](#cursor-paginator-instance-methods).

> [!WARNING]
> Your query must contain an "order by" clause in order to take advantage of cursor pagination. In addition, the columns that the query are ordered by must belong to the table you are paginating.

#### Cursor vs. Offset Pagination

To illustrate the differences between offset pagination and cursor pagination, let's examine some example SQL queries. Both of the following queries will both display the "second page" of results for a `users` table ordered by `id`:

```sql
# Offset Pagination...
select * from users order by id asc limit 15 offset 15;

# Cursor Pagination...
select * from users where id > 15 order by id asc limit 15;
```

The cursor pagination query offers the following advantages over offset pagination:

- For large data-sets, cursor pagination will offer better performance if the "order by" columns are indexed. This is because the "offset" clause scans through all previously matched data.
- For data-sets with frequent writes, offset pagination may skip records or show duplicates if results have been recently added to or deleted from the page a user is currently viewing.

However, cursor pagination has the following limitations:

- Like `simplePaginate`, cursor pagination can only be used to display "Next" and "Previous" links and does not support generating links with page numbers.
- It requires that the ordering is based on at least one unique column or a combination of columns that are unique. Columns with `null` values are not supported.
- Query expressions in "order by" clauses are supported only if they are aliased and added to the "select" clause as well.
- Query expressions with parameters are not supported.

### Manually Creating a Paginator

Sometimes you may wish to create a pagination instance manually, passing it an array of items that you already have in memory. You may do so by creating either a `Voyager\Pagination\Paginator`, `Voyager\Pagination\LengthAwarePaginator` or `Voyager\Pagination\CursorPaginator` instance, depending on your needs.

The `Paginator` and `CursorPaginator` classes do not need to know the total number of items in the result set; however, because of this, these classes do not have methods for retrieving the index of the last page. The `LengthAwarePaginator` accepts almost the same arguments as the `Paginator`; however, it requires a count of the total number of items in the result set.

In other words, the `Paginator` corresponds to the `simplePaginate` method on the query builder, the `CursorPaginator` corresponds to the `cursorPaginate` method, and the `LengthAwarePaginator` corresponds to the `paginate` method.

```php
use Voyager\Pagination\CursorPaginator;
use Voyager\Pagination\LengthAwarePaginator;
use Voyager\Pagination\Paginator;

// Items, total, per page, current page, options...
$paginator = new LengthAwarePaginator(['c', 'd'], 5, 2, 2, ['path' => '/items']);

// Items, per page, current page, options. Hand it one extra item to signal another page...
$paginator = new Paginator(['a', 'b', 'c'], 2, 1, ['path' => '/items']);

// Items, per page, cursor, options. "parameters" names the ordered columns...
$paginator = new CursorPaginator(
    [['id' => 1], ['id' => 2], ['id' => 3]],
    2,
    null,
    ['path' => '/items', 'parameters' => ['id']],
);
```

> [!WARNING]
> When manually creating a paginator instance, you should manually "slice" the array of results you pass to the paginator. If you're unsure how to do this, check out the [array_slice](https://secure.php.net/manual/en/function.array-slice.php) PHP function.

### Customizing Pagination URLs

By default, links generated by the paginator use the path returned by the [current path resolver](#resolving-the-current-page), which is `/` when none is registered. The paginator's `withPath` method allows you to customize the path used by the paginator when generating links. For example, if you want the paginator to generate links like `/admin/users?page=N`, you should pass `/admin/users` to the `withPath` method:

```php
use App\Models\User;

$users = User::paginate(15);

$users->withPath('/admin/users');
```

<a id="appending-query-string-values"></a>
#### Appending Query String Values

You may append to the query string of pagination links using the `appends` method. For example, to append `sort=votes` to each pagination link, you should make the following call to `appends`:

```php
use App\Models\User;

$users = User::paginate(15);

$users->appends(['sort' => 'votes']);
```

You may use the `withQueryString` method if you would like to append all of the values returned by the `Paginator::queryStringResolver` resolver to the pagination links. With no resolver registered, `withQueryString` appends nothing:

```php
$users = User::paginate(15)->withQueryString();
```

#### Appending Hash Fragments

If you need to append a "hash fragment" to URLs generated by the paginator, you may use the `fragment` method. For example, to append `#users` to the end of each pagination link, you should invoke the `fragment` method like so:

```php
$users = User::paginate(15)->fragment('users');
```

<a id="displaying-pagination-results"></a>
## Displaying Pagination Results

When calling the `paginate` method, you will receive an instance of `Voyager\Pagination\LengthAwarePaginator`, while calling the `simplePaginate` method returns an instance of `Voyager\Pagination\Paginator`. And, finally, calling the `cursorPaginate` method returns an instance of `Voyager\Pagination\CursorPaginator`.

These objects provide several methods that describe the result set. In addition to these helper methods, the paginator instances are iterators and may be looped as an array, and any method they do not define is forwarded to the collection of the current page's items:

```php
foreach ($users as $user) {
    echo $user->name;
}

$names = $users->pluck('name');
```

A `LengthAwarePaginator` describes the links to the rest of the pages in the result set through its `linkCollection` method. Each entry is an array with a `url`, a `label`, a `page`, and an `active` flag; the first entry is the "Previous" link, the last is the "Next" link, and gaps in a long page list appear as entries labelled `...` with a `null` URL:

```php
foreach ($users->linkCollection() as $link) {
    // $link['url'], $link['label'], $link['page'], $link['active']...
}
```

### Adjusting the Pagination Link Window

The link collection includes the current page number as well as links for the three pages before and after the current page. Using the `onEachSide` method, you may control how many additional links are included on each side of the current page within the middle, sliding window of links generated by the paginator:

```php
$links = $users->onEachSide(5)->linkCollection();
```

### Converting Results to JSON

The Venusian paginator classes implement the `Voyager\Contracts\NutsAndBolts\Jsonable` contract and expose the `toJson` method, so it's very easy to convert your pagination results to JSON. They also implement `JsonSerializable`, so you may pass a paginator straight to `json_encode`:

```php
use App\Models\User;

$json = User::paginate()->toJson();
```

The JSON from the paginator will include meta information such as `total`, `current_page`, `last_page`, and more. The result records are available via the `data` key in the JSON array, and the `links` key holds the [link collection](#displaying-pagination-results). Here is an example of the JSON created from a length aware paginator:

```json
{
   "current_page": 1,
   "data":[
        {
            // Record...
        },
        {
            // Record...
        }
   ],
   "first_page_url": "/users?page=1",
   "from": 1,
   "last_page": 4,
   "last_page_url": "/users?page=4",
   "links": [
        // Link entries...
   ],
   "next_page_url": "/users?page=2",
   "path": "/users",
   "per_page": 15,
   "prev_page_url": null,
   "to": 15,
   "total": 50
}
```

## Paginator / LengthAwarePaginator Instance Methods

Each paginator instance provides additional pagination information via the following methods:

| Method                                  | Description                                                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `$paginator->count()`                   | Get the number of items for the current page.                                                                |
| `$paginator->currentPage()`             | Get the current page number.                                                                                 |
| `$paginator->firstItem()`               | Get the result number of the first item in the results.                                                      |
| `$paginator->getOptions()`              | Get the paginator options.                                                                                   |
| `$paginator->getUrlRange($start, $end)` | Create a range of pagination URLs.                                                                           |
| `$paginator->hasPages()`                | Determine if there are enough items to split into multiple pages.                                            |
| `$paginator->hasMorePages()`            | Determine if there are more items in the data store.                                                         |
| `$paginator->items()`                   | Get the items for the current page.                                                                          |
| `$paginator->lastItem()`                | Get the result number of the last item in the results.                                                       |
| `$paginator->lastPage()`                | Get the page number of the last available page. (Not available when using `simplePaginate`).                 |
| `$paginator->linkCollection()`          | Get the page links as a collection. (Not available when using `simplePaginate`).                             |
| `$paginator->nextPageUrl()`             | Get the URL for the next page.                                                                               |
| `$paginator->onFirstPage()`             | Determine if the paginator is on the first page.                                                             |
| `$paginator->onLastPage()`              | Determine if the paginator is on the last page.                                                              |
| `$paginator->perPage()`                 | The number of items to be shown per page.                                                                    |
| `$paginator->previousPageUrl()`         | Get the URL for the previous page.                                                                           |
| `$paginator->total()`                   | Determine the total number of matching items in the data store. (Not available when using `simplePaginate`). |
| `$paginator->url($page)`                | Get the URL for a given page number.                                                                         |
| `$paginator->getPageName()`             | Get the query string variable used to store the page.                                                        |
| `$paginator->setPageName($name)`        | Set the query string variable used to store the page.                                                        |
| `$paginator->through($callback)`        | Transform each item using a callback.                                                                        |

<a id="cursor-paginator-instance-methods"></a>
## Cursor Paginator Instance Methods

Each cursor paginator instance provides additional pagination information via the following methods:

| Method                          | Description                                                       |
| ------------------------------- | ----------------------------------------------------------------- |
| `$paginator->count()`           | Get the number of items for the current page.                     |
| `$paginator->cursor()`          | Get the current cursor instance.                                  |
| `$paginator->getOptions()`      | Get the paginator options.                                        |
| `$paginator->hasPages()`        | Determine if there are enough items to split into multiple pages. |
| `$paginator->hasMorePages()`    | Determine if there are more items in the data store.              |
| `$paginator->getCursorName()`   | Get the query string variable used to store the cursor.           |
| `$paginator->items()`           | Get the items for the current page.                               |
| `$paginator->nextCursor()`      | Get the cursor instance for the next set of items.                |
| `$paginator->nextPageUrl()`     | Get the URL for the next page.                                    |
| `$paginator->onFirstPage()`     | Determine if the paginator is on the first page.                  |
| `$paginator->onLastPage()`      | Determine if the paginator is on the last page.                   |
| `$paginator->perPage()`         | The number of items to be shown per page.                         |
| `$paginator->previousCursor()`  | Get the cursor instance for the previous set of items.            |
| `$paginator->previousPageUrl()` | Get the URL for the previous page.                                |
| `$paginator->setCursorName()`   | Set the query string variable used to store the cursor.           |
| `$paginator->url($cursor)`      | Get the URL for a given cursor instance.                          |
