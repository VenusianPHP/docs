# Needs ext-curl first

pcurl links against ext-curl's curl_multi_ce and cannot load without it

## Trap

`multi-api.c` references ext-curl's exported `curl_multi_ce` and walks its private structs. `config.json` `requires.extensions: ["curl"]` generates `ZEND_MOD_REQUIRED("curl")`, so PHP refuses to start pcurl without ext-curl.[^config] Where curl is a shared module (Debian `20-curl.ini`), it must load before `40-pcurl.ini`. `PHP_ADD_EXTENSION_DEP` covers static builds.[^m4]

## Do

Keep ext-curl enabled in every SAPI that loads pcurl. Keep pcurl's ini priority above curl's.

[^config]: [requires.extensions](https://github.com/php-io-extensions/pcurl/blob/HEAD/config.json)
[^m4]: [PHP_ADD_EXTENSION_DEP](https://github.com/php-io-extensions/pcurl/blob/HEAD/clang/config.m4)
