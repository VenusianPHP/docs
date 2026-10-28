# Database: Graph (Neo4j)

Use Neo4j as a database connection: raw Cypher through two helpers, Instrument models whose query builder compiles to Cypher, and the same worker-pool offloading every connection has.

## Introduction

The Graph component, `Voyager\Graph`, adds a `neo4j` driver to the [database manager](/docs/{{version}}/framework/database/database). Its `Voyager\Graph\GraphServiceProvider` is one of Venusian's default providers, and the connection is configured as `database.connections.neo4j` in `config/database.php`. Opening a Neo4j connection needs the `laudis/neo4j-php-client` package (`^3.3`):

```shell
composer require laudis/neo4j-php-client
```

<a id="raw-cypher"></a>
## Running Raw Cypher

The `cypher` helper runs a query and returns its records as an array of associative arrays; `cypher_run` runs a statement and returns `true`. Both take bindings and an optional connection name, defaulting to the default connection when it is a Neo4j connection, and to `neo4j` otherwise:

```php
cypher_run('CREATE (n:Person {id: $id, name: $name})', ['id' => 'p1', 'name' => 'Ada']);

$records = cypher('MATCH (n:Person) WHERE n.name = ? RETURN n', ['Ada']);
```

Bindings may be named (`$id`) or positional (`?`). A `?` inside a string literal or a backticked name is left as a character.

<a id="models"></a>
## Graph Models

Extend `Voyager\Graph\Instrument\Model` to work with nodes through [Instrument](/docs/{{version}}/framework/instrument-orm/instrument). The model's table is the node label, its columns are node properties, and its key is a string `id` with no auto-increment:

```php
use Voyager\Graph\Instrument\Model;

class Person extends Model
{
    protected $table = 'Person';
}

Person::create(['id' => 'p1', 'name' => 'Ada']);

$people = Person::where('name', 'like', 'a%')->orderBy('name')->get();
```

The `make:graph-model` command generates one:

```shell
php computer make:graph-model Person --label=Person
```

The query builder compiles to Cypher, matching the label as `n`:

| Builder | Cypher |
| --- | --- |
| `get()` | `MATCH (n:Label) WHERE … RETURN n ORDER BY … SKIP … LIMIT …` |
| `insert()` | `UNWIND [{…}] AS row CREATE (n:Label) SET n = row` |
| `update()` | `MATCH … SET n.a = ? RETURN count(n) AS affected` |
| `delete()` | `MATCH … DETACH DELETE n RETURN count(n) AS affected` |
| `upsert()` | `UNWIND … MERGE (n:Label {key: row.key}) ON CREATE SET n = row ON MATCH SET …` |

Supported where clauses are basic, `like`/`whereLike` (a Cypher regular expression; `like` ignores case), `in`, `null`, `between`, column, nested and raw. `update` and `delete` return the number of nodes they touched, and array values are stored as native list properties.

Clauses with no single-label Cypher form are refused by name: joins, `groupBy`, `having`, unions, locks, eager-load limits, and date, JSON, full-text and `exists` where clauses. Write those queries with `cypher`.

<a id="event-loop"></a>
## On the Event Loop

A Neo4j connection offloads like any other connection (see [Using the Database on the Event Loop](/docs/{{version}}/framework/database/event-loop)): `via()` runs a terminal in a worker, `via()->transaction()` a whole transaction, and `stream()` sends its pages as `db-chunk:neo4j:{label}` mail. Blocking calls on the connection wait for its offloaded writes.
