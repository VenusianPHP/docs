# Strings

Venusian includes a variety of functions for manipulating string values.

## Introduction

Venusian includes a variety of functions for manipulating string values. Many of these functions are used by the framework itself; however, you are free to use them in your own applications if you find them convenient.

## Available Methods

### Strings

[class_basename](#method-class-basename)
[e](#method-e)
[preg_replace_array](#method-preg-replace-array)
[Str::after](#method-str-after)
[Str::afterLast](#method-str-after-last)
[Str::apa](#method-str-apa)
[Str::ascii](#method-str-ascii)
[Str::before](#method-str-before)
[Str::beforeLast](#method-str-before-last)
[Str::between](#method-str-between)
[Str::betweenFirst](#method-str-between-first)
[Str::camel](#method-camel-case)
[Str::charAt](#method-char-at)
[Str::chopStart](#method-str-chop-start)
[Str::chopEnd](#method-str-chop-end)
[Str::contains](#method-str-contains)
[Str::containsAll](#method-str-contains-all)
[Str::doesntContain](#method-str-doesnt-contain)
[Str::doesntEndWith](#method-str-doesnt-end-with)
[Str::doesntStartWith](#method-str-doesnt-start-with)
[Str::deduplicate](#method-deduplicate)
[Str::endsWith](#method-ends-with)
[Str::excerpt](#method-excerpt)
[Str::finish](#method-str-finish)
[Str::fromBase64](#method-str-from-base64)
[Str::headline](#method-str-headline)
[Str::initials](#method-str-initials)
[Str::inlineMarkdown](#method-str-inline-markdown)
[Str::is](#method-str-is)
[Str::isAscii](#method-str-is-ascii)
[Str::isJson](#method-str-is-json)
[Str::isUlid](#method-str-is-ulid)
[Str::isUrl](#method-str-is-url)
[Str::isUuid](#method-str-is-uuid)
[Str::kebab](#method-kebab-case)
[Str::lcfirst](#method-str-lcfirst)
[Str::length](#method-str-length)
[Str::limit](#method-str-limit)
[Str::lower](#method-str-lower)
[Str::markdown](#method-str-markdown)
[Str::mask](#method-str-mask)
[Str::match](#method-str-match)
[Str::matchAll](#method-str-match-all)
[Str::isMatch](#method-str-is-match)
[Str::orderedUuid](#method-str-ordered-uuid)
[Str::padBoth](#method-str-padboth)
[Str::padLeft](#method-str-padleft)
[Str::padRight](#method-str-padright)
[Str::password](#method-str-password)
[Str::plural](#method-str-plural)
[Str::pluralStudly](#method-str-plural-studly)
[Str::position](#method-str-position)
[Str::random](#method-str-random)
[Str::remove](#method-str-remove)
[Str::repeat](#method-str-repeat)
[Str::replace](#method-str-replace)
[Str::replaceArray](#method-str-replace-array)
[Str::replaceFirst](#method-str-replace-first)
[Str::replaceLast](#method-str-replace-last)
[Str::replaceMatches](#method-str-replace-matches)
[Str::replaceStart](#method-str-replace-start)
[Str::replaceEnd](#method-str-replace-end)
[Str::reverse](#method-str-reverse)
[Str::singular](#method-str-singular)
[Str::slug](#method-str-slug)
[Str::snake](#method-snake-case)
[Str::squish](#method-str-squish)
[Str::start](#method-str-start)
[Str::startsWith](#method-starts-with)
[Str::studly](#method-studly-case)
[Str::substr](#method-str-substr)
[Str::substrCount](#method-str-substrcount)
[Str::substrReplace](#method-str-substrreplace)
[Str::swap](#method-str-swap)
[Str::take](#method-take)
[Str::title](#method-title-case)
[Str::toBase64](#method-str-to-base64)
[Str::transliterate](#method-str-transliterate)
[Str::trim](#method-str-trim)
[Str::ltrim](#method-str-ltrim)
[Str::rtrim](#method-str-rtrim)
[Str::ucfirst](#method-str-ucfirst)
[Str::ucsplit](#method-str-ucsplit)
[Str::ucwords](#method-str-ucwords)
[Str::upper](#method-str-upper)
[Str::ulid](#method-str-ulid)
[Str::unwrap](#method-str-unwrap)
[Str::uuid](#method-str-uuid)
[Str::uuid7](#method-str-uuid7)
[Str::wordCount](#method-str-word-count)
[Str::wordWrap](#method-str-word-wrap)
[Str::words](#method-str-words)
[Str::wrap](#method-str-wrap)
[str](#method-str)

### Fluent Strings

[after](#method-fluent-str-after)
[afterLast](#method-fluent-str-after-last)
[apa](#method-fluent-str-apa)
[append](#method-fluent-str-append)
[ascii](#method-fluent-str-ascii)
[basename](#method-fluent-str-basename)
[before](#method-fluent-str-before)
[beforeLast](#method-fluent-str-before-last)
[between](#method-fluent-str-between)
[betweenFirst](#method-fluent-str-between-first)
[camel](#method-fluent-str-camel)
[charAt](#method-fluent-str-char-at)
[classBasename](#method-fluent-str-class-basename)
[chopStart](#method-fluent-str-chop-start)
[chopEnd](#method-fluent-str-chop-end)
[contains](#method-fluent-str-contains)
[containsAll](#method-fluent-str-contains-all)
[decrypt](#method-fluent-str-decrypt)
[deduplicate](#method-fluent-str-deduplicate)
[dirname](#method-fluent-str-dirname)
[doesntContain](#method-fluent-str-doesnt-contain)
[doesntEndWith](#method-fluent-str-doesnt-end-with)
[doesntStartWith](#method-fluent-str-doesnt-start-with)
[encrypt](#method-fluent-str-encrypt)
[endsWith](#method-fluent-str-ends-with)
[exactly](#method-fluent-str-exactly)
[excerpt](#method-fluent-str-excerpt)
[explode](#method-fluent-str-explode)
[finish](#method-fluent-str-finish)
[fromBase64](#method-fluent-str-from-base64)
[hash](#method-fluent-str-hash)
[headline](#method-fluent-str-headline)
[initials](#method-fluent-str-initials)
[inlineMarkdown](#method-fluent-str-inline-markdown)
[is](#method-fluent-str-is)
[isAscii](#method-fluent-str-is-ascii)
[isEmpty](#method-fluent-str-is-empty)
[isNotEmpty](#method-fluent-str-is-not-empty)
[isJson](#method-fluent-str-is-json)
[isUlid](#method-fluent-str-is-ulid)
[isUrl](#method-fluent-str-is-url)
[isUuid](#method-fluent-str-is-uuid)
[kebab](#method-fluent-str-kebab)
[lcfirst](#method-fluent-str-lcfirst)
[length](#method-fluent-str-length)
[limit](#method-fluent-str-limit)
[lower](#method-fluent-str-lower)
[markdown](#method-fluent-str-markdown)
[mask](#method-fluent-str-mask)
[match](#method-fluent-str-match)
[matchAll](#method-fluent-str-match-all)
[isMatch](#method-fluent-str-is-match)
[newLine](#method-fluent-str-new-line)
[padBoth](#method-fluent-str-padboth)
[padLeft](#method-fluent-str-padleft)
[padRight](#method-fluent-str-padright)
[pipe](#method-fluent-str-pipe)
[plural](#method-fluent-str-plural)
[position](#method-fluent-str-position)
[prepend](#method-fluent-str-prepend)
[remove](#method-fluent-str-remove)
[repeat](#method-fluent-str-repeat)
[replace](#method-fluent-str-replace)
[replaceArray](#method-fluent-str-replace-array)
[replaceFirst](#method-fluent-str-replace-first)
[replaceLast](#method-fluent-str-replace-last)
[replaceMatches](#method-fluent-str-replace-matches)
[replaceStart](#method-fluent-str-replace-start)
[replaceEnd](#method-fluent-str-replace-end)
[scan](#method-fluent-str-scan)
[singular](#method-fluent-str-singular)
[slug](#method-fluent-str-slug)
[snake](#method-fluent-str-snake)
[split](#method-fluent-str-split)
[squish](#method-fluent-str-squish)
[start](#method-fluent-str-start)
[startsWith](#method-fluent-str-starts-with)
[stripTags](#method-fluent-str-strip-tags)
[studly](#method-fluent-str-studly)
[substr](#method-fluent-str-substr)
[substrReplace](#method-fluent-str-substrreplace)
[swap](#method-fluent-str-swap)
[take](#method-fluent-str-take)
[tap](#method-fluent-str-tap)
[test](#method-fluent-str-test)
[title](#method-fluent-str-title)
[toBase64](#method-fluent-str-to-base64)
[toHtmlString](#method-fluent-str-to-html-string)
[transliterate](#method-fluent-str-transliterate)
[trim](#method-fluent-str-trim)
[ltrim](#method-fluent-str-ltrim)
[rtrim](#method-fluent-str-rtrim)
[ucfirst](#method-fluent-str-ucfirst)
[ucsplit](#method-fluent-str-ucsplit)
[ucwords](#method-fluent-str-ucwords)
[unwrap](#method-fluent-str-unwrap)
[upper](#method-fluent-str-upper)
[when](#method-fluent-str-when)
[whenContains](#method-fluent-str-when-contains)
[whenContainsAll](#method-fluent-str-when-contains-all)
[whenDoesntEndWith](#method-fluent-str-when-doesnt-end-with)
[whenDoesntStartWith](#method-fluent-str-when-doesnt-start-with)
[whenEmpty](#method-fluent-str-when-empty)
[whenNotEmpty](#method-fluent-str-when-not-empty)
[whenStartsWith](#method-fluent-str-when-starts-with)
[whenEndsWith](#method-fluent-str-when-ends-with)
[whenExactly](#method-fluent-str-when-exactly)
[whenNotExactly](#method-fluent-str-when-not-exactly)
[whenIs](#method-fluent-str-when-is)
[whenIsAscii](#method-fluent-str-when-is-ascii)
[whenIsUlid](#method-fluent-str-when-is-ulid)
[whenIsUuid](#method-fluent-str-when-is-uuid)
[whenTest](#method-fluent-str-when-test)
[wordCount](#method-fluent-str-word-count)
[words](#method-fluent-str-words)
[wrap](#method-fluent-str-wrap)

## Strings

<a id="method-class-basename"></a>
#### `class_basename()`

The `class_basename` function returns the class name of the given class with the class's namespace removed:

```php
$class = class_basename('Foo\Bar\Baz');

// Baz
```

<a id="method-e"></a>
#### `e()`

The `e` function runs PHP's `htmlspecialchars` function with the `double_encode` option set to `true` by default:

```php
echo e('<html>foo</html>');

// &lt;html&gt;foo&lt;/html&gt;
```

<a id="method-preg-replace-array"></a>
#### `preg_replace_array()`

The `preg_replace_array` function replaces a given pattern in the string sequentially using an array:

```php
$string = 'The event will take place between :start and :end';

$replaced = preg_replace_array('/:[a-z_]+/', ['8:30', '9:00'], $string);

// The event will take place between 8:30 and 9:00
```

<a id="method-str-after"></a>
#### `Str::after()`

The `Str::after` method returns everything after the given value in a string. The entire string will be returned if the value does not exist within the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::after('This is my name', 'This is');

// ' my name'
```

<a id="method-str-after-last"></a>
#### `Str::afterLast()`

The `Str::afterLast` method returns everything after the last occurrence of the given value in a string. The entire string will be returned if the value does not exist within the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::afterLast('App\Http\Controllers\Controller', '\\');

// 'Controller'
```

<a id="method-str-apa"></a>
#### `Str::apa()`

The `Str::apa` method converts the given string to title case following the [APA guidelines](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$title = Str::apa('Creating A Project');

// 'Creating a Project'
```

<a id="method-str-ascii"></a>
#### `Str::ascii()`

The `Str::ascii` method will attempt to transliterate the string into an ASCII value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::ascii('û');

// 'u'
```

<a id="method-str-before"></a>
#### `Str::before()`

The `Str::before` method returns everything before the given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::before('This is my name', 'my name');

// 'This is '
```

<a id="method-str-before-last"></a>
#### `Str::beforeLast()`

The `Str::beforeLast` method returns everything before the last occurrence of the given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::beforeLast('This is my name', 'is');

// 'This '
```

<a id="method-str-between"></a>
#### `Str::between()`

The `Str::between` method returns the portion of a string between two values:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::between('This is my name', 'This', 'name');

// ' is my '
```

<a id="method-str-between-first"></a>
#### `Str::betweenFirst()`

The `Str::betweenFirst` method returns the smallest possible portion of a string between two values:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::betweenFirst('[a] bc [d]', '[', ']');

// 'a'
```

<a id="method-camel-case"></a>
#### `Str::camel()`

The `Str::camel` method converts the given string to `camelCase`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::camel('foo_bar');

// 'fooBar'
```

<a id="method-char-at"></a>
#### `Str::charAt()`

The `Str::charAt` method returns the character at the specified index. If the index is out of bounds, `false` is returned:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$character = Str::charAt('This is my name.', 6);

// 's'
```

<a id="method-str-chop-start"></a>
#### `Str::chopStart()`

The `Str::chopStart` method removes the first occurrence of the given value only if the value appears at the start of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::chopStart('https://example.com', 'https://');

// 'example.com'
```

You may also pass an array as the second argument. If the string starts with any of the values in the array then that value will be removed from string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::chopStart('http://example.com', ['https://', 'http://']);

// 'example.com'
```

<a id="method-str-chop-end"></a>
#### `Str::chopEnd()`

The `Str::chopEnd` method removes the last occurrence of the given value only if the value appears at the end of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::chopEnd('app/Models/Photograph.php', '.php');

// 'app/Models/Photograph'
```

You may also pass an array as the second argument. If the string ends with any of the values in the array then that value will be removed from string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::chopEnd('example.com/index.php', ['/index.html', '/index.php']);

// 'example.com'
```

<a id="method-str-contains"></a>
#### `Str::contains()`

The `Str::contains` method determines if the given string contains the given value. By default, this method is case sensitive:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$contains = Str::contains('This is my name', 'my');

// true
```

You may also pass an array of values to determine if the given string contains any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$contains = Str::contains('This is my name', ['my', 'foo']);

// true
```

You may disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$contains = Str::contains('This is my name', 'MY', ignoreCase: true);

// true
```

<a id="method-str-contains-all"></a>
#### `Str::containsAll()`

The `Str::containsAll` method determines if the given string contains all of the values in a given array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$containsAll = Str::containsAll('This is my name', ['my', 'name']);

// true
```

You may disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$containsAll = Str::containsAll('This is my name', ['MY', 'NAME'], ignoreCase: true);

// true
```

<a id="method-str-doesnt-contain"></a>
#### `Str::doesntContain()`

The `Str::doesntContain` method determines if the given string doesn't contain the given value. By default, this method is case sensitive:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$doesntContain = Str::doesntContain('This is name', 'my');

// true
```

You may also pass an array of values to determine if the given string doesn't contain any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$doesntContain = Str::doesntContain('This is name', ['my', 'framework']);

// true
```

You may disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$doesntContain = Str::doesntContain('This is name', 'MY', ignoreCase: true);

// true
```

<a id="method-deduplicate"></a>
#### `Str::deduplicate()`

The `Str::deduplicate` method replaces consecutive instances of a character with a single instance of that character in the given string. By default, the method deduplicates spaces:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::deduplicate('The   Venusian   Framework');

// The Venusian Framework
```

You may specify a different character to deduplicate by passing it in as the second argument to the method:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::deduplicate('The---Venusian---Framework', '-');

// The-Venusian-Framework
```

<a id="method-str-doesnt-end-with"></a>
#### `Str::doesntEndWith()`

The `Str::doesntEndWith` method determines if the given string doesn't end with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::doesntEndWith('This is my name', 'dog');

// true
```

You may also pass an array of values to determine if the given string doesn't end with any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::doesntEndWith('This is my name', ['this', 'foo']);

// true

$result = Str::doesntEndWith('This is my name', ['name', 'foo']);

// false
```

<a id="method-str-doesnt-start-with"></a>
#### `Str::doesntStartWith()`

The `Str::doesntStartWith` method determines if the given string doesn't begin with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::doesntStartWith('This is my name', 'That');

// true
```

If an array of possible values is passed, the `doesntStartWith` method will return `true` if the string doesn't begin with any of the given values:

```php
$result = Str::doesntStartWith('This is my name', ['What', 'That', 'There']);

// true
```

<a id="method-ends-with"></a>
#### `Str::endsWith()`

The `Str::endsWith` method determines if the given string ends with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::endsWith('This is my name', 'name');

// true
```

You may also pass an array of values to determine if the given string ends with any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::endsWith('This is my name', ['name', 'foo']);

// true

$result = Str::endsWith('This is my name', ['this', 'foo']);

// false
```

<a id="method-excerpt"></a>
#### `Str::excerpt()`

The `Str::excerpt` method extracts an excerpt from a given string that matches the first instance of a phrase within that string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$excerpt = Str::excerpt('This is my name', 'my', [
    'radius' => 3
]);

// '...is my na...'
```

The `radius` option, which defaults to `100`, allows you to define the number of characters that should appear on each side of the truncated string.

In addition, you may use the `omission` option to define the string that will be prepended and appended to the truncated string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$excerpt = Str::excerpt('This is my name', 'name', [
    'radius' => 3,
    'omission' => '(...) '
]);

// '(...) my name'
```

<a id="method-str-finish"></a>
#### `Str::finish()`

The `Str::finish` method adds a single instance of the given value to a string if it does not already end with that value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$adjusted = Str::finish('this/string', '/');

// this/string/

$adjusted = Str::finish('this/string/', '/');

// this/string/
```

<a id="method-str-from-base64"></a>
#### `Str::fromBase64()`

The `Str::fromBase64` method decodes the given Base64 string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$decoded = Str::fromBase64('VmVudXNpYW4=');

// Venusian
```

<a id="method-str-headline"></a>
#### `Str::headline()`

The `Str::headline` method will convert strings delimited by casing, hyphens, or underscores into a space delimited string with each word's first letter capitalized:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$headline = Str::headline('steve_jobs');

// Steve Jobs

$headline = Str::headline('EmailNotificationSent');

// Email Notification Sent
```

<a id="method-str-initials"></a>
#### `Str::initials()`

The `Str::initials` method will return the initials of a given string, optionally capitalizing them:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$initials = Str::initials('taylor otwell');

// to

$initials = Str::initials('taylor otwell', capitalize: true);

// TO
```

<a id="method-str-inline-markdown"></a>
#### `Str::inlineMarkdown()`

The `Str::inlineMarkdown` method converts GitHub flavored Markdown into inline HTML using [CommonMark](https://commonmark.thephpleague.com/). However, unlike the `markdown` method, it does not wrap all generated HTML in a block-level element:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$html = Str::inlineMarkdown('**Venusian**');

// <strong>Venusian</strong>
```

#### Markdown Security

By default, Markdown supports raw HTML, which will expose Cross-Site Scripting (XSS) vulnerabilities when used with raw user input. As per the [CommonMark Security documentation](https://commonmark.thephpleague.com/security/), you may use the `html_input` option to either escape or strip raw HTML, and the `allow_unsafe_links` option to specify whether to allow unsafe links. If you need to allow some raw HTML, you should pass your compiled Markdown through an HTML Purifier:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::inlineMarkdown('Inject: <script>alert("Hello XSS!");</script>', [
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// Inject: alert(&quot;Hello XSS!&quot;);
```

<a id="method-str-is"></a>
#### `Str::is()`

The `Str::is` method determines if a given string matches a given pattern. Asterisks may be used as wildcard values:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$matches = Str::is('foo*', 'foobar');

// true

$matches = Str::is('baz*', 'foobar');

// false
```

You may disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$matches = Str::is('*.jpg', 'photo.JPG', ignoreCase: true);

// true
```

<a id="method-str-is-ascii"></a>
#### `Str::isAscii()`

The `Str::isAscii` method determines if a given string is 7-bit ASCII:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$isAscii = Str::isAscii('Taylor');

// true

$isAscii = Str::isAscii('ü');

// false
```

<a id="method-str-is-json"></a>
#### `Str::isJson()`

The `Str::isJson` method determines if the given string is valid JSON:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::isJson('[1,2,3]');

// true

$result = Str::isJson('{"first": "John", "last": "Doe"}');

// true

$result = Str::isJson('{first: "John", last: "Doe"}');

// false
```

<a id="method-str-is-url"></a>
#### `Str::isUrl()`

The `Str::isUrl` method determines if the given string is a valid URL:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$isUrl = Str::isUrl('http://example.com');

// true

$isUrl = Str::isUrl('venusian');

// false
```

The `isUrl` method considers a wide range of protocols as valid. However, you may specify the protocols that should be considered valid by providing them to the `isUrl` method:

```php
$isUrl = Str::isUrl('http://example.com', ['http', 'https']);
```

<a id="method-str-is-ulid"></a>
#### `Str::isUlid()`

The `Str::isUlid` method determines if the given string is a valid ULID:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$isUlid = Str::isUlid('01gd6r360bp37zj17nxb55yv40');

// true

$isUlid = Str::isUlid('venusian');

// false
```

<a id="method-str-is-uuid"></a>
#### `Str::isUuid()`

The `Str::isUuid` method determines if the given string is a valid UUID:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$isUuid = Str::isUuid('a0a2a2d2-0b87-4a18-83f2-2529882be2de');

// true

$isUuid = Str::isUuid('venusian');

// false
```

You may also validate that the given UUID matches a UUID specification by version (1, 3, 4, 5, 6, 7, or 8):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$isUuid = Str::isUuid('a0a2a2d2-0b87-4a18-83f2-2529882be2de', version: 4);

// true

$isUuid = Str::isUuid('a0a2a2d2-0b87-4a18-83f2-2529882be2de', version: 1);

// false
```

<a id="method-kebab-case"></a>
#### `Str::kebab()`

The `Str::kebab` method converts the given string to `kebab-case`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::kebab('fooBar');

// foo-bar
```

<a id="method-str-lcfirst"></a>
#### `Str::lcfirst()`

The `Str::lcfirst` method returns the given string with the first character lowercased:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::lcfirst('Foo Bar');

// foo Bar
```

<a id="method-str-length"></a>
#### `Str::length()`

The `Str::length` method returns the length of the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$length = Str::length('Venusian');

// 8
```

<a id="method-str-limit"></a>
#### `Str::limit()`

The `Str::limit` method truncates the given string to the specified length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$truncated = Str::limit('The quick brown fox jumps over the lazy dog', 20);

// The quick brown fox...
```

You may pass a third argument to the method to change the string that will be appended to the end of the truncated string:

```php
$truncated = Str::limit('The quick brown fox jumps over the lazy dog', 20, ' (...)');

// The quick brown fox (...)
```

If you would like to preserve complete words when truncating the string, you may utilize the `preserveWords` argument. When this argument is `true`, the string will be truncated to the nearest complete word boundary:

```php
$truncated = Str::limit('The quick brown fox', 12, preserveWords: true);

// The quick...
```

<a id="method-str-lower"></a>
#### `Str::lower()`

The `Str::lower` method converts the given string to lowercase:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::lower('VENUSIAN');

// venusian
```

<a id="method-str-markdown"></a>
#### `Str::markdown()`

The `Str::markdown` method converts GitHub flavored Markdown into HTML using [CommonMark](https://commonmark.thephpleague.com/):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$html = Str::markdown('# Venusian');

// <h1>Venusian</h1>

$html = Str::markdown('# Taylor <b>Otwell</b>', [
    'html_input' => 'strip',
]);

// <h1>Taylor Otwell</h1>
```

#### Markdown Security

By default, Markdown supports raw HTML, which will expose Cross-Site Scripting (XSS) vulnerabilities when used with raw user input. As per the [CommonMark Security documentation](https://commonmark.thephpleague.com/security/), you may use the `html_input` option to either escape or strip raw HTML, and the `allow_unsafe_links` option to specify whether to allow unsafe links. If you need to allow some raw HTML, you should pass your compiled Markdown through an HTML Purifier:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::markdown('Inject: <script>alert("Hello XSS!");</script>', [
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// <p>Inject: alert(&quot;Hello XSS!&quot;);</p>
```

<a id="method-str-mask"></a>
#### `Str::mask()`

The `Str::mask` method masks a portion of a string with a repeated character, and may be used to obfuscate segments of strings such as email addresses and phone numbers:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::mask('taylor@example.com', '*', 3);

// tay***************
```

If needed, you may provide a negative number as the third argument to the `mask` method, which will instruct the method to begin masking at the given distance from the end of the string:

```php
$string = Str::mask('taylor@example.com', '*', -15, 3);

// tay***@example.com
```

<a id="method-str-match"></a>
#### `Str::match()`

The `Str::match` method will return the portion of a string that matches a given regular expression pattern:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::match('/bar/', 'foo bar');

// 'bar'

$result = Str::match('/foo (.*)/', 'foo bar');

// 'bar'
```

<a id="method-str-match-all"></a>
#### `Str::matchAll()`

The `Str::matchAll` method will return a collection containing the portions of a string that match a given regular expression pattern:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::matchAll('/bar/', 'bar foo bar');

// collect(['bar', 'bar'])
```

If you specify a matching group within the expression, Venusian will return a collection of the first matching group's matches:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::matchAll('/f(\w*)/', 'bar fun bar fly');

// collect(['un', 'ly']);
```

If no matches are found, an empty collection will be returned.

<a id="method-str-is-match"></a>
#### `Str::isMatch()`

The `Str::isMatch` method will return `true` if the string matches a given regular expression:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::isMatch('/foo (.*)/', 'foo bar');

// true

$result = Str::isMatch('/foo (.*)/', 'venusian');

// false
```

<a id="method-str-ordered-uuid"></a>
#### `Str::orderedUuid()`

The `Str::orderedUuid` method generates a "timestamp first" UUID that may be efficiently stored in an indexed database column. Each UUID that is generated using this method will be sorted after UUIDs previously generated using the method:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

return (string) Str::orderedUuid();
```

<a id="method-str-padboth"></a>
#### `Str::padBoth()`

The `Str::padBoth` method wraps PHP's `str_pad` function, padding both sides of a string with another string until the final string reaches a desired length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::padBoth('James', 10, '_');

// '__James___'

$padded = Str::padBoth('James', 10);

// '  James   '
```

<a id="method-str-padleft"></a>
#### `Str::padLeft()`

The `Str::padLeft` method wraps PHP's `str_pad` function, padding the left side of a string with another string until the final string reaches a desired length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::padLeft('James', 10, '-=');

// '-=-=-James'

$padded = Str::padLeft('James', 10);

// '     James'
```

<a id="method-str-padright"></a>
#### `Str::padRight()`

The `Str::padRight` method wraps PHP's `str_pad` function, padding the right side of a string with another string until the final string reaches a desired length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::padRight('James', 10, '-');

// 'James-----'

$padded = Str::padRight('James', 10);

// 'James     '
```

<a id="method-str-password"></a>
#### `Str::password()`

The `Str::password` method may be used to generate a secure, random password of a given length. The password will consist of a combination of letters, numbers, and symbols. By default, passwords are 32 characters long:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$password = Str::password();

// 'EbJo2vE-AS:U,$%_gkrV4n,q~1xy/-_4'

$password = Str::password(12);

// 'qwuar>#V|i]N'
```

<a id="method-str-plural"></a>
#### `Str::plural()`

The `Str::plural` method converts a singular word string to its plural form. This function supports any language the Doctrine Inflector supports; English is the default, and `Voyager\NutsAndBolts\DataObjects\Pluralizer::useLanguage` selects another:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$plural = Str::plural('car');

// cars

$plural = Str::plural('child');

// children
```

You may provide an integer as a second argument to the function to retrieve the singular or plural form of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$plural = Str::plural('child', 2);

// children

$singular = Str::plural('child', 1);

// child
```

The `prependCount` argument may be provided to prefix the pluralized string with the formatted `$count`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$label = Str::plural('car', 1000, prependCount: true);

// 1,000 cars
```

<a id="method-str-plural-studly"></a>
#### `Str::pluralStudly()`

The `Str::pluralStudly` method converts a singular word string formatted in studly caps case to its plural form. This function supports any language the Doctrine Inflector supports; English is the default, and `Voyager\NutsAndBolts\DataObjects\Pluralizer::useLanguage` selects another:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$plural = Str::pluralStudly('VerifiedHuman');

// VerifiedHumans

$plural = Str::pluralStudly('UserFeedback');

// UserFeedback
```

You may provide an integer as a second argument to the function to retrieve the singular or plural form of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$plural = Str::pluralStudly('VerifiedHuman', 2);

// VerifiedHumans

$singular = Str::pluralStudly('VerifiedHuman', 1);

// VerifiedHuman
```

<a id="method-str-position"></a>
#### `Str::position()`

The `Str::position` method returns the position of the first occurrence of a substring in a string. If the substring does not exist in the given string, `false` is returned:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$position = Str::position('Hello, World!', 'Hello');

// 0

$position = Str::position('Hello, World!', 'W');

// 7
```

<a id="method-str-random"></a>
#### `Str::random()`

The `Str::random` method generates a random string of the specified length. This function uses PHP's `random_bytes` function:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$random = Str::random(40);
```

During testing, it may be useful to "fake" the value that is returned by the `Str::random` method. To accomplish this, you may use the `createRandomStringsUsing` method:

```php
Str::createRandomStringsUsing(function () {
    return 'fake-random-string';
});
```

To instruct the `random` method to return to generating random strings normally, you may invoke the `createRandomStringsNormally` method:

```php
Str::createRandomStringsNormally();
```

<a id="method-str-remove"></a>
#### `Str::remove()`

The `Str::remove` method removes the given value or array of values from the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = 'Peter Piper picked a peck of pickled peppers.';

$removed = Str::remove('e', $string);

// Ptr Pipr pickd a pck of pickld ppprs.
```

You may also pass `false` as a third argument to the `remove` method to ignore case when removing strings.

<a id="method-str-repeat"></a>
#### `Str::repeat()`

The `Str::repeat` method repeats the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = 'a';

$repeat = Str::repeat($string, 5);

// aaaaa
```

<a id="method-str-replace"></a>
#### `Str::replace()`

The `Str::replace` method replaces a given string within the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = 'Venusian 11.x';

$replaced = Str::replace('11.x', '12.x', $string);

// Venusian 12.x
```

The `replace` method also accepts a `caseSensitive` argument. By default, the `replace` method is case sensitive:

```php
$replaced = Str::replace(
    'php',
    'Venusian',
    'PHP Framework for Embedded Devices',
    caseSensitive: false
);

// Venusian Framework for Embedded Devices
```

<a id="method-str-replace-array"></a>
#### `Str::replaceArray()`

The `Str::replaceArray` method replaces a given value in the string sequentially using an array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = 'The event will take place between ? and ?';

$replaced = Str::replaceArray('?', ['8:30', '9:00'], $string);

// The event will take place between 8:30 and 9:00
```

<a id="method-str-replace-first"></a>
#### `Str::replaceFirst()`

The `Str::replaceFirst` method replaces the first occurrence of a given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::replaceFirst('the', 'a', 'the quick brown fox jumps over the lazy dog');

// a quick brown fox jumps over the lazy dog
```

<a id="method-str-replace-last"></a>
#### `Str::replaceLast()`

The `Str::replaceLast` method replaces the last occurrence of a given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::replaceLast('the', 'a', 'the quick brown fox jumps over the lazy dog');

// the quick brown fox jumps over a lazy dog
```

<a id="method-str-replace-matches"></a>
#### `Str::replaceMatches()`

The `Str::replaceMatches` method replaces all portions of a string matching a pattern with the given replacement string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::replaceMatches(
    pattern: '/[^A-Za-z0-9]++/',
    replace: '',
    subject: '(+1) 501-555-1000'
);

// '15015551000'
```

The `replaceMatches` method also accepts a closure that will be invoked with each portion of the string matching the given pattern, allowing you to perform the replacement logic within the closure and return the replaced value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::replaceMatches('/\d/', function (array $matches) {
    return '['.$matches[0].']';
}, '123');

// '[1][2][3]'
```

<a id="method-str-replace-start"></a>
#### `Str::replaceStart()`

The `Str::replaceStart` method replaces the first occurrence of the given value only if the value appears at the start of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::replaceStart('Hello', 'Venusian', 'Hello World');

// Venusian World

$replaced = Str::replaceStart('World', 'Venusian', 'Hello World');

// Hello World
```

<a id="method-str-replace-end"></a>
#### `Str::replaceEnd()`

The `Str::replaceEnd` method replaces the last occurrence of the given value only if the value appears at the end of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::replaceEnd('World', 'Venusian', 'Hello World');

// Hello Venusian

$replaced = Str::replaceEnd('Hello', 'Venusian', 'Hello World');

// Hello World
```

<a id="method-str-reverse"></a>
#### `Str::reverse()`

The `Str::reverse` method reverses the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$reversed = Str::reverse('Hello World');

// dlroW olleH
```

<a id="method-str-singular"></a>
#### `Str::singular()`

The `Str::singular` method converts a string to its singular form. This function supports any language the Doctrine Inflector supports; English is the default, and `Voyager\NutsAndBolts\DataObjects\Pluralizer::useLanguage` selects another:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$singular = Str::singular('cars');

// car

$singular = Str::singular('children');

// child
```

<a id="method-str-slug"></a>
#### `Str::slug()`

The `Str::slug` method generates a URL-friendly "slug" from the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slug = Str::slug('Venusian 5 Framework', '-');

// venusian-5-framework
```

<a id="method-snake-case"></a>
#### `Str::snake()`

The `Str::snake` method converts the given string to `snake_case`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::snake('fooBar');

// foo_bar

$converted = Str::snake('fooBar', '-');

// foo-bar
```

<a id="method-str-squish"></a>
#### `Str::squish()`

The `Str::squish` method removes all extraneous white space from a string, including extraneous white space between words:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::squish('    venusian    framework    ');

// venusian framework
```

<a id="method-str-start"></a>
#### `Str::start()`

The `Str::start` method adds a single instance of the given value to a string if it does not already start with that value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$adjusted = Str::start('this/string', '/');

// /this/string

$adjusted = Str::start('/this/string', '/');

// /this/string
```

<a id="method-starts-with"></a>
#### `Str::startsWith()`

The `Str::startsWith` method determines if the given string begins with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::startsWith('This is my name', 'This');

// true
```

If an array of possible values is passed, the `startsWith` method will return `true` if the string begins with any of the given values:

```php
$result = Str::startsWith('This is my name', ['This', 'That', 'There']);

// true
```

<a id="method-studly-case"></a>
#### `Str::studly()`

The `Str::studly` method converts the given string to `StudlyCase`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::studly('foo_bar');

// FooBar
```

<a id="method-str-substr"></a>
#### `Str::substr()`

The `Str::substr` method returns the portion of string specified by the start and length parameters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::substr('The Venusian Framework', 4, 8);

// Venusian
```

<a id="method-str-substrcount"></a>
#### `Str::substrCount()`

The `Str::substrCount` method returns the number of occurrences of a given value in the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$count = Str::substrCount('If you like ice cream, you will like snow cones.', 'like');

// 2
```

<a id="method-str-substrreplace"></a>
#### `Str::substrReplace()`

The `Str::substrReplace` method replaces text within a portion of a string, starting at the position specified by the third argument and replacing the number of characters specified by the fourth argument. Passing `0` to the method's fourth argument will insert the string at the specified position without replacing any of the existing characters in the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::substrReplace('1300', ':', 2);
// 13:

$result = Str::substrReplace('1300', ':', 2, 0);
// 13:00
```

<a id="method-str-swap"></a>
#### `Str::swap()`

The `Str::swap` method replaces multiple values in the given string using PHP's `strtr` function:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::swap([
    'Tacos' => 'Burritos',
    'great' => 'fantastic',
], 'Tacos are great!');

// Burritos are fantastic!
```

<a id="method-take"></a>
#### `Str::take()`

The `Str::take` method returns a specified number of characters from the beginning of a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$taken = Str::take('Build something amazing!', 5);

// Build
```

<a id="method-title-case"></a>
#### `Str::title()`

The `Str::title` method converts the given string to `Title Case`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::title('a nice title uses the correct case');

// A Nice Title Uses The Correct Case
```

<a id="method-str-to-base64"></a>
#### `Str::toBase64()`

The `Str::toBase64` method converts the given string to Base64:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$base64 = Str::toBase64('Venusian');

// VmVudXNpYW4=
```

<a id="method-str-transliterate"></a>
#### `Str::transliterate()`

The `Str::transliterate` method will attempt to convert a given string into its closest ASCII representation:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$email = Str::transliterate('ⓣⓔⓢⓣ@ⓔⓧⓐⓜⓟⓛⓔ.ⓒⓞⓜ');

// 'test@example.com'
```

<a id="method-str-trim"></a>
#### `Str::trim()`

The `Str::trim` method strips whitespace (or other characters) from the beginning and end of the given string. Unlike PHP's native `trim` function, the `Str::trim` method also removes unicode whitespace characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::trim(' foo bar ');

// 'foo bar'
```

<a id="method-str-ltrim"></a>
#### `Str::ltrim()`

The `Str::ltrim` method strips whitespace (or other characters) from the beginning of the given string. Unlike PHP's native `ltrim` function, the `Str::ltrim` method also removes unicode whitespace characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::ltrim('  foo bar  ');

// 'foo bar  '
```

<a id="method-str-rtrim"></a>
#### `Str::rtrim()`

The `Str::rtrim` method strips whitespace (or other characters) from the end of the given string. Unlike PHP's native `rtrim` function, the `Str::rtrim` method also removes unicode whitespace characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::rtrim('  foo bar  ');

// '  foo bar'
```

<a id="method-str-ucfirst"></a>
#### `Str::ucfirst()`

The `Str::ucfirst` method returns the given string with the first character capitalized:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::ucfirst('foo bar');

// Foo bar
```

<a id="method-str-ucsplit"></a>
#### `Str::ucsplit()`

The `Str::ucsplit` method splits the given string into an array by uppercase characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$segments = Str::ucsplit('FooBar');

// [0 => 'Foo', 1 => 'Bar']
```

<a id="method-str-ucwords"></a>
#### `Str::ucwords()`

The `Str::ucwords` method converts the first character of each word in the given string to uppercase:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::ucwords('venusian framework');

// Venusian Framework
```

<a id="method-str-upper"></a>
#### `Str::upper()`

The `Str::upper` method converts the given string to uppercase:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::upper('venusian');

// VENUSIAN
```

<a id="method-str-ulid"></a>
#### `Str::ulid()`

The `Str::ulid` method generates a ULID, which is a compact, time-ordered unique identifier:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

return (string) Str::ulid();

// 01gd6r360bp37zj17nxb55yv40
```

If you would like to retrieve a `Voyager\NutsAndBolts\DataObjects\Carbon` date instance representing the date and time that a given ULID was created, you may use the `createFromId` method provided by Venusian's Carbon integration:

```php
use Voyager\NutsAndBolts\DataObjects\Carbon;
use Voyager\NutsAndBolts\DataObjects\Str;

$date = Carbon::createFromId((string) Str::ulid());
```

During testing, it may be useful to "fake" the value that is returned by the `Str::ulid` method. To accomplish this, you may use the `createUlidsUsing` method:

```php
use Symfony\Component\Uid\Ulid;

Str::createUlidsUsing(function () {
    return new Ulid('01HRDBNHHCKNW2AK4Z29SN82T9');
});
```

To instruct the `ulid` method to return to generating ULIDs normally, you may invoke the `createUlidsNormally` method:

```php
Str::createUlidsNormally();
```

<a id="method-str-unwrap"></a>
#### `Str::unwrap()`

The `Str::unwrap` method removes the specified strings from the beginning and end of a given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::unwrap('-Venusian-', '-');

// Venusian

Str::unwrap('{framework: "Venusian"}', '{', '}');

// framework: "Venusian"
```

<a id="method-str-uuid"></a>
#### `Str::uuid()`

The `Str::uuid` method generates a UUID (version 4):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

return (string) Str::uuid();
```

During testing, it may be useful to "fake" the value that is returned by the `Str::uuid` method. To accomplish this, you may use the `createUuidsUsing` method:

```php
use Ramsey\Uuid\Uuid;

Str::createUuidsUsing(function () {
    return Uuid::fromString('eadbfeac-5258-45c2-bab7-ccb9b5ef74f9');
});
```

To instruct the `uuid` method to return to generating UUIDs normally, you may invoke the `createUuidsNormally` method:

```php
Str::createUuidsNormally();
```

<a id="method-str-uuid7"></a>
#### `Str::uuid7()`

The `Str::uuid7` method generates a UUID (version 7):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

return (string) Str::uuid7();
```

A `DateTimeInterface` may be passed as an optional parameter which will be used to generate the ordered UUID:

```php
return (string) Str::uuid7(time: now());
```

<a id="method-str-word-count"></a>
#### `Str::wordCount()`

The `Str::wordCount` method returns the number of words that a string contains:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::wordCount('Hello, world!'); // 2
```

<a id="method-str-word-wrap"></a>
#### `Str::wordWrap()`

The `Str::wordWrap` method wraps a string to a given number of characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$text = "The quick brown fox jumped over the lazy dog.";

Str::wordWrap($text, characters: 20, break: "<br />\n");

/*
The quick brown fox<br />
jumped over the lazy<br />
dog.
*/
```

<a id="method-str-words"></a>
#### `Str::words()`

The `Str::words` method limits the number of words in a string. An additional string may be passed to this method via its third argument to specify which string should be appended to the end of the truncated string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

return Str::words('Perfectly balanced, as all things should be.', 3, ' >>>');

// Perfectly balanced, as >>>
```

<a id="method-str-wrap"></a>
#### `Str::wrap()`

The `Str::wrap` method wraps the given string with an additional string or pair of strings:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::wrap('Venusian', '"');

// "Venusian"

Str::wrap('is', before: 'This ', after: ' Venusian!');

// This is Venusian!
```

<a id="method-str"></a>
#### `str()`

The `str` function returns a new `Voyager\NutsAndBolts\DataObjects\Stringable` instance of the given string. This function is equivalent to the `Str::of` method:

```php
$string = str('Taylor')->append(' Otwell');

// 'Taylor Otwell'
```

If no argument is provided to the `str` function, the function returns an object that proxies method calls to `Voyager\NutsAndBolts\DataObjects\Str`:

```php
$snake = str()->snake('FooBar');

// 'foo_bar'
```

<a id="fluent-strings"></a>
## Fluent Strings

Fluent strings provide a more fluent, object-oriented interface for working with string values, allowing you to chain multiple string operations together using a more readable syntax compared to traditional string operations.

<a id="method-fluent-str-after"></a>
#### `after`

The `after` method returns everything after the given value in a string. The entire string will be returned if the value does not exist within the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::of('This is my name')->after('This is');

// ' my name'
```

<a id="method-fluent-str-after-last"></a>
#### `afterLast`

The `afterLast` method returns everything after the last occurrence of the given value in a string. The entire string will be returned if the value does not exist within the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::of('App\Http\Controllers\Controller')->afterLast('\\');

// 'Controller'
```

<a id="method-fluent-str-apa"></a>
#### `apa`

The `apa` method converts the given string to title case following the [APA guidelines](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('a nice title uses the correct case')->apa();

// A Nice Title Uses the Correct Case
```

<a id="method-fluent-str-append"></a>
#### `append`

The `append` method appends the given values to the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Taylor')->append(' Otwell');

// 'Taylor Otwell'
```

<a id="method-fluent-str-ascii"></a>
#### `ascii`

The `ascii` method will attempt to transliterate the string into an ASCII value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('ü')->ascii();

// 'u'
```

<a id="method-fluent-str-basename"></a>
#### `basename`

The `basename` method will return the trailing name component of the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('/foo/bar/baz')->basename();

// 'baz'
```

If needed, you may provide an "extension" that will be removed from the trailing component:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('/foo/bar/baz.jpg')->basename('.jpg');

// 'baz'
```

<a id="method-fluent-str-before"></a>
#### `before`

The `before` method returns everything before the given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::of('This is my name')->before('my name');

// 'This is '
```

<a id="method-fluent-str-before-last"></a>
#### `beforeLast`

The `beforeLast` method returns everything before the last occurrence of the given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slice = Str::of('This is my name')->beforeLast('is');

// 'This '
```

<a id="method-fluent-str-between"></a>
#### `between`

The `between` method returns the portion of a string between two values:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('This is my name')->between('This', 'name');

// ' is my '
```

<a id="method-fluent-str-between-first"></a>
#### `betweenFirst`

The `betweenFirst` method returns the smallest possible portion of a string between two values:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('[a] bc [d]')->betweenFirst('[', ']');

// 'a'
```

<a id="method-fluent-str-camel"></a>
#### `camel`

The `camel` method converts the given string to `camelCase`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('foo_bar')->camel();

// 'fooBar'
```

<a id="method-fluent-str-char-at"></a>
#### `charAt`

The `charAt` method returns the character at the specified index. If the index is out of bounds, `false` is returned:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$character = Str::of('This is my name.')->charAt(6);

// 's'
```

<a id="method-fluent-str-class-basename"></a>
#### `classBasename`

The `classBasename` method returns the class name of the given class with the class's namespace removed:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$class = Str::of('Foo\Bar\Baz')->classBasename();

// 'Baz'
```

<a id="method-fluent-str-chop-start"></a>
#### `chopStart`

The `chopStart` method removes the first occurrence of the given value only if the value appears at the start of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::of('https://example.com')->chopStart('https://');

// 'example.com'
```

You may also pass an array. If the string starts with any of the values in the array then that value will be removed from string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::of('http://example.com')->chopStart(['https://', 'http://']);

// 'example.com'
```

<a id="method-fluent-str-chop-end"></a>
#### `chopEnd`

The `chopEnd` method removes the last occurrence of the given value only if the value appears at the end of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::of('https://example.com')->chopEnd('.com');

// 'https://example'
```

You may also pass an array. If the string ends with any of the values in the array then that value will be removed from string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$url = Str::of('http://example.com')->chopEnd(['.com', '.io']);

// 'http://example'
```

<a id="method-fluent-str-contains"></a>
#### `contains`

The `contains` method determines if the given string contains the given value. By default, this method is case sensitive:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$contains = Str::of('This is my name')->contains('my');

// true
```

You may also pass an array of values to determine if the given string contains any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$contains = Str::of('This is my name')->contains(['my', 'foo']);

// true
```

You can disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$contains = Str::of('This is my name')->contains('MY', ignoreCase: true);

// true
```

<a id="method-fluent-str-contains-all"></a>
#### `containsAll`

The `containsAll` method determines if the given string contains all of the values in the given array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$containsAll = Str::of('This is my name')->containsAll(['my', 'name']);

// true
```

You can disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$containsAll = Str::of('This is my name')->containsAll(['MY', 'NAME'], ignoreCase: true);

// true
```

<a id="method-fluent-str-decrypt"></a>
#### `decrypt`

The `decrypt` method [decrypts](/docs/{{version}}/framework/security/encryption) the encrypted string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$decrypted = $encrypted->decrypt();

// 'secret'
```

For the inverse of `decrypt`, see the [encrypt](#method-fluent-str-encrypt) method.

<a id="method-fluent-str-deduplicate"></a>
#### `deduplicate`

The `deduplicate` method replaces consecutive instances of a character with a single instance of that character in the given string. By default, the method deduplicates spaces:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('The   Venusian   Framework')->deduplicate();

// The Venusian Framework
```

You may specify a different character to deduplicate by passing it in as the first argument to the method:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('The---Venusian---Framework')->deduplicate('-');

// The-Venusian-Framework
```

<a id="method-fluent-str-dirname"></a>
#### `dirname`

The `dirname` method returns the parent directory portion of the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('/foo/bar/baz')->dirname();

// '/foo/bar'
```

If necessary, you may specify how many directory levels you wish to trim from the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('/foo/bar/baz')->dirname(2);

// '/foo'
```

<a id="method-fluent-str-doesnt-contain"></a>
#### `doesntContain()`

The `doesntContain` method determines if the given string does not contain the given value. This method is the inverse of the [contains](#method-fluent-str-contains) method. By default, this method is case sensitive:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$doesntContain = Str::of('This is name')->doesntContain('my');

// true
```

You may also pass an array of values to determine if the given string does not contain any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$doesntContain = Str::of('This is name')->doesntContain(['my', 'framework']);

// true
```

You may disable case sensitivity by setting the `ignoreCase` argument to `true`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$doesntContain = Str::of('This is my name')->doesntContain('MY', ignoreCase: true);

// false
```

<a id="method-fluent-str-doesnt-end-with"></a>
#### `doesntEndWith`

The `doesntEndWith` method determines if the given string doesn't end with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->doesntEndWith('dog');

// true
```

You may also pass an array of values to determine if the given string doesn't end with any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->doesntEndWith(['this', 'foo']);

// true

$result = Str::of('This is my name')->doesntEndWith(['name', 'foo']);

// false
```

<a id="method-fluent-str-doesnt-start-with"></a>
#### `doesntStartWith`

The `doesntStartWith` method determines if the given string doesn't begin with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->doesntStartWith('That');

// true
```

You may also pass an array of values to determine if the given string doesn't start with any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->doesntStartWith(['What', 'That', 'There']);

// true
```

<a id="method-fluent-str-encrypt"></a>
#### `encrypt`

The `encrypt` method [encrypts](/docs/{{version}}/framework/security/encryption) the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$encrypted = Str::of('secret')->encrypt();
```

For the inverse of `encrypt`, see the [decrypt](#method-fluent-str-decrypt) method.

<a id="method-fluent-str-ends-with"></a>
#### `endsWith`

The `endsWith` method determines if the given string ends with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->endsWith('name');

// true
```

You may also pass an array of values to determine if the given string ends with any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->endsWith(['name', 'foo']);

// true

$result = Str::of('This is my name')->endsWith(['this', 'foo']);

// false
```

<a id="method-fluent-str-exactly"></a>
#### `exactly`

The `exactly` method determines if the given string is an exact match with another string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('Venusian')->exactly('Venusian');

// true
```

<a id="method-fluent-str-excerpt"></a>
#### `excerpt`

The `excerpt` method extracts an excerpt from the string that matches the first instance of a phrase within that string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$excerpt = Str::of('This is my name')->excerpt('my', [
    'radius' => 3
]);

// '...is my na...'
```

The `radius` option, which defaults to `100`, allows you to define the number of characters that should appear on each side of the truncated string.

In addition, you may use the `omission` option to change the string that will be prepended and appended to the truncated string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$excerpt = Str::of('This is my name')->excerpt('name', [
    'radius' => 3,
    'omission' => '(...) '
]);

// '(...) my name'
```

<a id="method-fluent-str-explode"></a>
#### `explode`

The `explode` method splits the string by the given delimiter and returns a collection containing each section of the split string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$collection = Str::of('foo bar baz')->explode(' ');

// collect(['foo', 'bar', 'baz'])
```

<a id="method-fluent-str-finish"></a>
#### `finish`

The `finish` method adds a single instance of the given value to a string if it does not already end with that value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$adjusted = Str::of('this/string')->finish('/');

// this/string/

$adjusted = Str::of('this/string/')->finish('/');

// this/string/
```

<a id="method-fluent-str-from-base64"></a>
#### `fromBase64`

The `fromBase64` method decodes the given Base64 string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$decoded = Str::of('VmVudXNpYW4=')->fromBase64();

// Venusian
```

<a id="method-fluent-str-hash"></a>
#### `hash`

The `hash` method hashes the string using the given [algorithm](https://www.php.net/manual/en/function.hash-algos.php):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$hashed = Str::of('secret')->hash(algorithm: 'sha256');

// '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b'
```

<a id="method-fluent-str-headline"></a>
#### `headline`

The `headline` method will convert strings delimited by casing, hyphens, or underscores into a space delimited string with each word's first letter capitalized:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$headline = Str::of('taylor_otwell')->headline();

// Taylor Otwell

$headline = Str::of('EmailNotificationSent')->headline();

// Email Notification Sent
```

<a id="method-fluent-str-initials"></a>
#### `initials`

The `initials` method will convert the string to its initials:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$initials = Str::of('Taylor Otwell')->initials()->upper();

// TO
```

<a id="method-fluent-str-inline-markdown"></a>
#### `inlineMarkdown`

The `inlineMarkdown` method converts GitHub flavored Markdown into inline HTML using [CommonMark](https://commonmark.thephpleague.com/). However, unlike the `markdown` method, it does not wrap all generated HTML in a block-level element:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$html = Str::of('**Venusian**')->inlineMarkdown();

// <strong>Venusian</strong>
```

#### Markdown Security

By default, Markdown supports raw HTML, which will expose Cross-Site Scripting (XSS) vulnerabilities when used with raw user input. As per the [CommonMark Security documentation](https://commonmark.thephpleague.com/security/), you may use the `html_input` option to either escape or strip raw HTML, and the `allow_unsafe_links` option to specify whether to allow unsafe links. If you need to allow some raw HTML, you should pass your compiled Markdown through an HTML Purifier:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::of('Inject: <script>alert("Hello XSS!");</script>')->inlineMarkdown([
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// Inject: alert(&quot;Hello XSS!&quot;);
```

<a id="method-fluent-str-is"></a>
#### `is`

The `is` method determines if a given string matches a given pattern. Asterisks may be used as wildcard values

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$matches = Str::of('foobar')->is('foo*');

// true

$matches = Str::of('foobar')->is('baz*');

// false
```

<a id="method-fluent-str-is-ascii"></a>
#### `isAscii`

The `isAscii` method determines if a given string is an ASCII string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('Taylor')->isAscii();

// true

$result = Str::of('ü')->isAscii();

// false
```

<a id="method-fluent-str-is-empty"></a>
#### `isEmpty`

The `isEmpty` method determines if the given string is empty:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('  ')->trim()->isEmpty();

// true

$result = Str::of('Venusian')->trim()->isEmpty();

// false
```

<a id="method-fluent-str-is-not-empty"></a>
#### `isNotEmpty`

The `isNotEmpty` method determines if the given string is not empty:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('  ')->trim()->isNotEmpty();

// false

$result = Str::of('Venusian')->trim()->isNotEmpty();

// true
```

<a id="method-fluent-str-is-json"></a>
#### `isJson`

The `isJson` method determines if a given string is valid JSON:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('[1,2,3]')->isJson();

// true

$result = Str::of('{"first": "John", "last": "Doe"}')->isJson();

// true

$result = Str::of('{first: "John", last: "Doe"}')->isJson();

// false
```

<a id="method-fluent-str-is-ulid"></a>
#### `isUlid`

The `isUlid` method determines if a given string is a ULID:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('01gd6r360bp37zj17nxb55yv40')->isUlid();

// true

$result = Str::of('Taylor')->isUlid();

// false
```

<a id="method-fluent-str-is-url"></a>
#### `isUrl`

The `isUrl` method determines if a given string is a URL:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('http://example.com')->isUrl();

// true

$result = Str::of('Taylor')->isUrl();

// false
```

The `isUrl` method considers a wide range of protocols as valid. However, you may specify the protocols that should be considered valid by providing them to the `isUrl` method:

```php
$result = Str::of('http://example.com')->isUrl(['http', 'https']);
```

<a id="method-fluent-str-is-uuid"></a>
#### `isUuid`

The `isUuid` method determines if a given string is a UUID:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('5ace9ab9-e9cf-4ec6-a19d-5881212a452c')->isUuid();

// true

$result = Str::of('Taylor')->isUuid();

// false
```

You may also validate that the given UUID matches a UUID specification by version (1, 3, 4, 5, 6, 7, or 8):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$isUuid = Str::of('a0a2a2d2-0b87-4a18-83f2-2529882be2de')->isUuid(version: 4);

// true

$isUuid = Str::of('a0a2a2d2-0b87-4a18-83f2-2529882be2de')->isUuid(version: 1);

// false
```

<a id="method-fluent-str-kebab"></a>
#### `kebab`

The `kebab` method converts the given string to `kebab-case`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('fooBar')->kebab();

// foo-bar
```

<a id="method-fluent-str-lcfirst"></a>
#### `lcfirst`

The `lcfirst` method returns the given string with the first character lowercased:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Foo Bar')->lcfirst();

// foo Bar
```

<a id="method-fluent-str-length"></a>
#### `length`

The `length` method returns the length of the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$length = Str::of('Venusian')->length();

// 8
```

<a id="method-fluent-str-limit"></a>
#### `limit`

The `limit` method truncates the given string to the specified length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$truncated = Str::of('The quick brown fox jumps over the lazy dog')->limit(20);

// The quick brown fox...
```

You may also pass a second argument to change the string that will be appended to the end of the truncated string:

```php
$truncated = Str::of('The quick brown fox jumps over the lazy dog')->limit(20, ' (...)');

// The quick brown fox (...)
```

If you would like to preserve complete words when truncating the string, you may utilize the `preserveWords` argument. When this argument is `true`, the string will be truncated to the nearest complete word boundary:

```php
$truncated = Str::of('The quick brown fox')->limit(12, preserveWords: true);

// The quick...
```

<a id="method-fluent-str-lower"></a>
#### `lower`

The `lower` method converts the given string to lowercase:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('VENUSIAN')->lower();

// 'venusian'
```

<a id="method-fluent-str-markdown"></a>
#### `markdown`

The `markdown` method converts GitHub flavored Markdown into HTML:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$html = Str::of('# Venusian')->markdown();

// <h1>Venusian</h1>

$html = Str::of('# Taylor <b>Otwell</b>')->markdown([
    'html_input' => 'strip',
]);

// <h1>Taylor Otwell</h1>
```

#### Markdown Security

By default, Markdown supports raw HTML, which will expose Cross-Site Scripting (XSS) vulnerabilities when used with raw user input. As per the [CommonMark Security documentation](https://commonmark.thephpleague.com/security/), you may use the `html_input` option to either escape or strip raw HTML, and the `allow_unsafe_links` option to specify whether to allow unsafe links. If you need to allow some raw HTML, you should pass your compiled Markdown through an HTML Purifier:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::of('Inject: <script>alert("Hello XSS!");</script>')->markdown([
    'html_input' => 'strip',
    'allow_unsafe_links' => false,
]);

// <p>Inject: alert(&quot;Hello XSS!&quot;);</p>
```

<a id="method-fluent-str-mask"></a>
#### `mask`

The `mask` method masks a portion of a string with a repeated character, and may be used to obfuscate segments of strings such as email addresses and phone numbers:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('taylor@example.com')->mask('*', 3);

// tay***************
```

If needed, you may provide negative numbers as the second or third argument to the `mask` method, which will instruct the method to begin masking at the given distance from the end of the string:

```php
$string = Str::of('taylor@example.com')->mask('*', -15, 3);

// tay***@example.com

$string = Str::of('taylor@example.com')->mask('*', 4, -4);

// tayl**********.com
```

<a id="method-fluent-str-match"></a>
#### `match`

The `match` method will return the portion of a string that matches a given regular expression pattern:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('foo bar')->match('/bar/');

// 'bar'

$result = Str::of('foo bar')->match('/foo (.*)/');

// 'bar'
```

<a id="method-fluent-str-match-all"></a>
#### `matchAll`

The `matchAll` method will return a collection containing the portions of a string that match a given regular expression pattern:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('bar foo bar')->matchAll('/bar/');

// collect(['bar', 'bar'])
```

If you specify a matching group within the expression, Venusian will return a collection of the first matching group's matches:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('bar fun bar fly')->matchAll('/f(\w*)/');

// collect(['un', 'ly']);
```

If no matches are found, an empty collection will be returned.

<a id="method-fluent-str-is-match"></a>
#### `isMatch`

The `isMatch` method will return `true` if the string matches a given regular expression:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('foo bar')->isMatch('/foo (.*)/');

// true

$result = Str::of('venusian')->isMatch('/foo (.*)/');

// false
```

<a id="method-fluent-str-new-line"></a>
#### `newLine`

The `newLine` method appends an "end of line" character to a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::of('Venusian')->newLine()->append('Framework');

// 'Venusian
//  Framework'
```

<a id="method-fluent-str-padboth"></a>
#### `padBoth`

The `padBoth` method wraps PHP's `str_pad` function, padding both sides of a string with another string until the final string reaches the desired length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::of('James')->padBoth(10, '_');

// '__James___'

$padded = Str::of('James')->padBoth(10);

// '  James   '
```

<a id="method-fluent-str-padleft"></a>
#### `padLeft`

The `padLeft` method wraps PHP's `str_pad` function, padding the left side of a string with another string until the final string reaches the desired length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::of('James')->padLeft(10, '-=');

// '-=-=-James'

$padded = Str::of('James')->padLeft(10);

// '     James'
```

<a id="method-fluent-str-padright"></a>
#### `padRight`

The `padRight` method wraps PHP's `str_pad` function, padding the right side of a string with another string until the final string reaches the desired length:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$padded = Str::of('James')->padRight(10, '-');

// 'James-----'

$padded = Str::of('James')->padRight(10);

// 'James     '
```

<a id="method-fluent-str-pipe"></a>
#### `pipe`

The `pipe` method allows you to transform the string by passing its current value to the given callable:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$hash = Str::of('Venusian')->pipe('md5')->prepend('Checksum: ');

// 'Checksum: 28394d88182b75d2261ced8f4e62bd00'

$closure = Str::of('foo')->pipe(function (Stringable $str) {
    return 'bar';
});

// 'bar'
```

<a id="method-fluent-str-plural"></a>
#### `plural`

The `plural` method converts a singular word string to its plural form. This function supports any language the Doctrine Inflector supports; English is the default, and `Voyager\NutsAndBolts\DataObjects\Pluralizer::useLanguage` selects another:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$plural = Str::of('car')->plural();

// cars

$plural = Str::of('child')->plural();

// children
```

You may provide an integer argument to the function to retrieve the singular or plural form of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$plural = Str::of('child')->plural(2);

// children

$plural = Str::of('child')->plural(1);

// child
```

You may provide the `prependCount` argument to prefix the pluralized string with the formatted `$count`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$label = Str::of('car')->plural(1000, prependCount: true);

// 1,000 cars
```

<a id="method-fluent-str-position"></a>
#### `position`

The `position` method returns the position of the first occurrence of a substring in a string. If the substring does not exist within the string, `false` is returned:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$position = Str::of('Hello, World!')->position('Hello');

// 0

$position = Str::of('Hello, World!')->position('W');

// 7
```

<a id="method-fluent-str-prepend"></a>
#### `prepend`

The `prepend` method prepends the given values onto the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Framework')->prepend('Venusian ');

// Venusian Framework
```

<a id="method-fluent-str-remove"></a>
#### `remove`

The `remove` method removes the given value or array of values from the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Arkansas is quite beautiful!')->remove('quite ');

// Arkansas is beautiful!
```

You may also pass `false` as a second parameter to ignore case when removing strings.

<a id="method-fluent-str-repeat"></a>
#### `repeat`

The `repeat` method repeats the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$repeated = Str::of('a')->repeat(5);

// aaaaa
```

<a id="method-fluent-str-replace"></a>
#### `replace`

The `replace` method replaces a given string within the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('Venusian 6.x')->replace('6.x', '7.x');

// Venusian 7.x
```

The `replace` method also accepts a `caseSensitive` argument. By default, the `replace` method is case sensitive:

```php
$replaced = Str::of('macOS 13.x')->replace(
    'macOS', 'iOS', caseSensitive: false
);
```

<a id="method-fluent-str-replace-array"></a>
#### `replaceArray`

The `replaceArray` method replaces a given value in the string sequentially using an array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = 'The event will take place between ? and ?';

$replaced = Str::of($string)->replaceArray('?', ['8:30', '9:00']);

// The event will take place between 8:30 and 9:00
```

<a id="method-fluent-str-replace-first"></a>
#### `replaceFirst`

The `replaceFirst` method replaces the first occurrence of a given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('the quick brown fox jumps over the lazy dog')->replaceFirst('the', 'a');

// a quick brown fox jumps over the lazy dog
```

<a id="method-fluent-str-replace-last"></a>
#### `replaceLast`

The `replaceLast` method replaces the last occurrence of a given value in a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('the quick brown fox jumps over the lazy dog')->replaceLast('the', 'a');

// the quick brown fox jumps over a lazy dog
```

<a id="method-fluent-str-replace-matches"></a>
#### `replaceMatches`

The `replaceMatches` method replaces all portions of a string matching a pattern with the given replacement string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('(+1) 501-555-1000')->replaceMatches('/[^A-Za-z0-9]++/', '');

// '15015551000'
```

The `replaceMatches` method also accepts a closure that will be invoked with each portion of the string matching the given pattern, allowing you to perform the replacement logic within the closure and return the replaced value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('123')->replaceMatches('/\d/', function (array $matches) {
    return '['.$matches[0].']';
});

// '[1][2][3]'
```

<a id="method-fluent-str-replace-start"></a>
#### `replaceStart`

The `replaceStart` method replaces the first occurrence of the given value only if the value appears at the start of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('Hello World')->replaceStart('Hello', 'Venusian');

// Venusian World

$replaced = Str::of('Hello World')->replaceStart('World', 'Venusian');

// Hello World
```

<a id="method-fluent-str-replace-end"></a>
#### `replaceEnd`

The `replaceEnd` method replaces the last occurrence of the given value only if the value appears at the end of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$replaced = Str::of('Hello World')->replaceEnd('World', 'Venusian');

// Hello Venusian

$replaced = Str::of('Hello World')->replaceEnd('Hello', 'Venusian');

// Hello World
```

<a id="method-fluent-str-scan"></a>
#### `scan`

The `scan` method parses input from a string into a collection according to a format supported by the [`sscanf` PHP function](https://www.php.net/manual/en/function.sscanf.php):

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$collection = Str::of('filename.jpg')->scan('%[^.].%s');

// collect(['filename', 'jpg'])
```

<a id="method-fluent-str-singular"></a>
#### `singular`

The `singular` method converts a string to its singular form. This function supports any language the Doctrine Inflector supports; English is the default, and `Voyager\NutsAndBolts\DataObjects\Pluralizer::useLanguage` selects another:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$singular = Str::of('cars')->singular();

// car

$singular = Str::of('children')->singular();

// child
```

<a id="method-fluent-str-slug"></a>
#### `slug`

The `slug` method generates a URL-friendly "slug" from the given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$slug = Str::of('Venusian Framework')->slug('-');

// venusian-framework
```

<a id="method-fluent-str-snake"></a>
#### `snake`

The `snake` method converts the given string to `snake_case`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('fooBar')->snake();

// foo_bar
```

<a id="method-fluent-str-split"></a>
#### `split`

The `split` method splits a string into a collection using a regular expression:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$segments = Str::of('one, two, three')->split('/[\s,]+/');

// collect(["one", "two", "three"])
```

<a id="method-fluent-str-squish"></a>
#### `squish`

The `squish` method removes all extraneous white space from a string, including extraneous white space between words:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('    venusian    framework    ')->squish();

// venusian framework
```

<a id="method-fluent-str-start"></a>
#### `start`

The `start` method adds a single instance of the given value to a string if it does not already start with that value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$adjusted = Str::of('this/string')->start('/');

// /this/string

$adjusted = Str::of('/this/string')->start('/');

// /this/string
```

<a id="method-fluent-str-starts-with"></a>
#### `startsWith`

The `startsWith` method determines if the given string begins with the given value:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->startsWith('This');

// true
```

You may also pass an array of values to determine if the given string starts with any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('This is my name')->startsWith(['This', 'That']);

// true
```

<a id="method-fluent-str-strip-tags"></a>
#### `stripTags`

The `stripTags` method removes all HTML and PHP tags from a string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('<a href="https://example.com">Taylor <b>Otwell</b></a>')->stripTags();

// Taylor Otwell

$result = Str::of('<a href="https://example.com">Taylor <b>Otwell</b></a>')->stripTags('<b>');

// Taylor <b>Otwell</b>
```

<a id="method-fluent-str-studly"></a>
#### `studly`

The `studly` method converts the given string to `StudlyCase`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('foo_bar')->studly();

// FooBar
```

<a id="method-fluent-str-substr"></a>
#### `substr`

The `substr` method returns the portion of the string specified by the given start and length parameters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Venusian Framework')->substr(9);

// Framework

$string = Str::of('Venusian Framework')->substr(9, 5);

// Frame
```

<a id="method-fluent-str-substrreplace"></a>
#### `substrReplace`

The `substrReplace` method replaces text within a portion of a string, starting at the position specified by the second argument and replacing the number of characters specified by the third argument. Passing `0` to the method's third argument will insert the string at the specified position without replacing any of the existing characters in the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('1300')->substrReplace(':', 2);

// 13:

$string = Str::of('The Framework')->substrReplace(' Venusian', 3, 0);

// The Venusian Framework
```

<a id="method-fluent-str-swap"></a>
#### `swap`

The `swap` method replaces multiple values in the string using PHP's `strtr` function:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Tacos are great!')
    ->swap([
        'Tacos' => 'Burritos',
        'great' => 'fantastic',
    ]);

// Burritos are fantastic!
```

<a id="method-fluent-str-take"></a>
#### `take`

The `take` method returns a specified number of characters from the beginning of the string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$taken = Str::of('Build something amazing!')->take(5);

// Build
```

<a id="method-fluent-str-tap"></a>
#### `tap`

The `tap` method passes the string to the given closure, allowing you to examine and interact with the string while not affecting the string itself. The original string is returned by the `tap` method regardless of what is returned by the closure:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('Venusian')
    ->append(' Framework')
    ->tap(function (Stringable $string) {
        dump('String after append: '.$string);
    })
    ->upper();

// VENUSIAN FRAMEWORK
```

<a id="method-fluent-str-test"></a>
#### `test`

The `test` method determines if a string matches the given regular expression pattern:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$result = Str::of('Venusian Framework')->test('/Venusian/');

// true
```

<a id="method-fluent-str-title"></a>
#### `title`

The `title` method converts the given string to `Title Case`:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$converted = Str::of('a nice title uses the correct case')->title();

// A Nice Title Uses The Correct Case
```

<a id="method-fluent-str-to-base64"></a>
#### `toBase64`

The `toBase64` method converts the given string to Base64:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$base64 = Str::of('Venusian')->toBase64();

// VmVudXNpYW4=
```

<a id="method-fluent-str-to-html-string"></a>
#### `toHtmlString`

The `toHtmlString` method converts the given string to an instance of `Voyager\NutsAndBolts\HtmlString`, which the [e](#method-e) helper returns unescaped:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$htmlString = Str::of('Nuno Maduro')->toHtmlString();
```

<a id="method-fluent-str-transliterate"></a>
#### `transliterate`

The `transliterate` method will attempt to convert a given string into its closest ASCII representation:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$email = Str::of('ⓣⓔⓢⓣ@ⓔⓧⓐⓜⓟⓛⓔ.ⓒⓞⓜ')->transliterate();

// 'test@example.com'
```

<a id="method-fluent-str-trim"></a>
#### `trim`

The `trim` method trims the given string. Unlike PHP's native `trim` function, Venusian's `trim` method also removes unicode whitespace characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('  Venusian  ')->trim();

// 'Venusian'

$string = Str::of('/Venusian/')->trim('/');

// 'Venusian'
```

<a id="method-fluent-str-ltrim"></a>
#### `ltrim`

The `ltrim` method trims the left side of the string. Unlike PHP's native `ltrim` function, Venusian's `ltrim` method also removes unicode whitespace characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('  Venusian  ')->ltrim();

// 'Venusian  '

$string = Str::of('/Venusian/')->ltrim('/');

// 'Venusian/'
```

<a id="method-fluent-str-rtrim"></a>
#### `rtrim`

The `rtrim` method trims the right side of the given string. Unlike PHP's native `rtrim` function, Venusian's `rtrim` method also removes unicode whitespace characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('  Venusian  ')->rtrim();

// '  Venusian'

$string = Str::of('/Venusian/')->rtrim('/');

// '/Venusian'
```

<a id="method-fluent-str-ucfirst"></a>
#### `ucfirst`

The `ucfirst` method returns the given string with the first character capitalized:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('foo bar')->ucfirst();

// Foo bar
```

<a id="method-fluent-str-ucsplit"></a>
#### `ucsplit`

The `ucsplit` method splits the given string into a collection by uppercase characters:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Foo Bar')->ucsplit();

// collect(['Foo ', 'Bar'])
```

<a id="method-fluent-str-ucwords"></a>
#### `ucwords`

The `ucwords` method converts the first character of each word in the given string to uppercase:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('venusian framework')->ucwords();

// Venusian Framework
```

<a id="method-fluent-str-unwrap"></a>
#### `unwrap`

The `unwrap` method removes the specified strings from the beginning and end of a given string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::of('-Venusian-')->unwrap('-');

// Venusian

Str::of('{framework: "Venusian"}')->unwrap('{', '}');

// framework: "Venusian"
```

<a id="method-fluent-str-upper"></a>
#### `upper`

The `upper` method converts the given string to uppercase:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$adjusted = Str::of('venusian')->upper();

// VENUSIAN
```

<a id="method-fluent-str-when"></a>
#### `when`

The `when` method invokes the given closure if a given condition is `true`. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('Taylor')
    ->when(true, function (Stringable $string) {
        return $string->append(' Otwell');
    });

// 'Taylor Otwell'
```

If necessary, you may pass another closure as the third parameter to the `when` method. This closure will execute if the condition parameter evaluates to `false`.

<a id="method-fluent-str-when-contains"></a>
#### `whenContains`

The `whenContains` method invokes the given closure if the string contains the given value. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('tony stark')
    ->whenContains('tony', function (Stringable $string) {
        return $string->title();
    });

// 'Tony Stark'
```

If necessary, you may pass another closure as the third parameter. The closure will be invoked if the string does not contain the given value.

You may also pass an array of values to determine if the given string contains any of the values in the array:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('tony stark')
    ->whenContains(['tony', 'hulk'], function (Stringable $string) {
        return $string->title();
    });

// Tony Stark
```

<a id="method-fluent-str-when-contains-all"></a>
#### `whenContainsAll`

The `whenContainsAll` method invokes the given closure if the string contains all of the given sub-strings. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('tony stark')
    ->whenContainsAll(['tony', 'stark'], function (Stringable $string) {
        return $string->title();
    });

// 'Tony Stark'
```

If necessary, you may pass another closure as the third parameter. The closure will be invoked if the condition parameter evaluates to `false`.

<a id="method-fluent-str-when-doesnt-end-with"></a>
#### `whenDoesntEndWith`

The `whenDoesntEndWith` method invokes the given closure if the string doesn't end with the given sub-string. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('disney world')->whenDoesntEndWith('land', function (Stringable $string) {
    return $string->title();
});

// 'Disney World'
```

<a id="method-fluent-str-when-doesnt-start-with"></a>
#### `whenDoesntStartWith`

The `whenDoesntStartWith` method invokes the given closure if the string doesn't start with the given sub-string. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('disney world')->whenDoesntStartWith('sea', function (Stringable $string) {
    return $string->title();
});

// 'Disney World'
```

<a id="method-fluent-str-when-empty"></a>
#### `whenEmpty`

The `whenEmpty` method invokes the given closure if the string is empty. If the closure returns a value, that value will also be returned by the `whenEmpty` method. If the closure does not return a value, the fluent string instance will be returned:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('  ')->trim()->whenEmpty(function (Stringable $string) {
    return $string->prepend('Venusian');
});

// 'Venusian'
```

<a id="method-fluent-str-when-not-empty"></a>
#### `whenNotEmpty`

The `whenNotEmpty` method invokes the given closure if the string is not empty. If the closure returns a value, that value will also be returned by the `whenNotEmpty` method. If the closure does not return a value, the fluent string instance will be returned:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('Framework')->whenNotEmpty(function (Stringable $string) {
    return $string->prepend('Venusian ');
});

// 'Venusian Framework'
```

<a id="method-fluent-str-when-starts-with"></a>
#### `whenStartsWith`

The `whenStartsWith` method invokes the given closure if the string starts with the given sub-string. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('disney world')->whenStartsWith('disney', function (Stringable $string) {
    return $string->title();
});

// 'Disney World'
```

<a id="method-fluent-str-when-ends-with"></a>
#### `whenEndsWith`

The `whenEndsWith` method invokes the given closure if the string ends with the given sub-string. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('disney world')->whenEndsWith('world', function (Stringable $string) {
    return $string->title();
});

// 'Disney World'
```

<a id="method-fluent-str-when-exactly"></a>
#### `whenExactly`

The `whenExactly` method invokes the given closure if the string exactly matches the given string. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('venusian')->whenExactly('venusian', function (Stringable $string) {
    return $string->title();
});

// 'Venusian'
```

<a id="method-fluent-str-when-not-exactly"></a>
#### `whenNotExactly`

The `whenNotExactly` method invokes the given closure if the string does not exactly match the given string. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('framework')->whenNotExactly('venusian', function (Stringable $string) {
    return $string->title();
});

// 'Framework'
```

<a id="method-fluent-str-when-is"></a>
#### `whenIs`

The `whenIs` method invokes the given closure if the string matches a given pattern. Asterisks may be used as wildcard values. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('foo/bar')->whenIs('foo/*', function (Stringable $string) {
    return $string->append('/baz');
});

// 'foo/bar/baz'
```

<a id="method-fluent-str-when-is-ascii"></a>
#### `whenIsAscii`

The `whenIsAscii` method invokes the given closure if the string is 7-bit ASCII. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('venusian')->whenIsAscii(function (Stringable $string) {
    return $string->title();
});

// 'Venusian'
```

<a id="method-fluent-str-when-is-ulid"></a>
#### `whenIsUlid`

The `whenIsUlid` method invokes the given closure if the string is a valid ULID. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('01gd6r360bp37zj17nxb55yv40')->whenIsUlid(function (Stringable $string) {
    return $string->substr(0, 8);
});

// '01gd6r36'
```

<a id="method-fluent-str-when-is-uuid"></a>
#### `whenIsUuid`

The `whenIsUuid` method invokes the given closure if the string is a valid UUID. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('a0a2a2d2-0b87-4a18-83f2-2529882be2de')->whenIsUuid(function (Stringable $string) {
    return $string->substr(0, 8);
});

// 'a0a2a2d2'
```

<a id="method-fluent-str-when-test"></a>
#### `whenTest`

The `whenTest` method invokes the given closure if the string matches the given regular expression. The closure will receive the fluent string instance:

```php
use Voyager\NutsAndBolts\DataObjects\Str;
use Voyager\NutsAndBolts\DataObjects\Stringable;

$string = Str::of('venusian framework')->whenTest('/venusian/', function (Stringable $string) {
    return $string->title();
});

// 'Venusian Framework'
```

<a id="method-fluent-str-word-count"></a>
#### `wordCount`

The `wordCount` method returns the number of words that a string contains:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::of('Hello, world!')->wordCount(); // 2
```

<a id="method-fluent-str-words"></a>
#### `words`

The `words` method limits the number of words in a string. If necessary, you may specify an additional string that will be appended to the truncated string:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

$string = Str::of('Perfectly balanced, as all things should be.')->words(3, ' >>>');

// Perfectly balanced, as >>>
```

<a id="method-fluent-str-wrap"></a>
#### `wrap`

The `wrap` method wraps the given string with an additional string or pair of strings:

```php
use Voyager\NutsAndBolts\DataObjects\Str;

Str::of('Venusian')->wrap('"');

// "Venusian"

Str::of('is')->wrap(before: 'This ', after: ' Venusian!');

// This is Venusian!
```
