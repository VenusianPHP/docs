# Needs ext-curl first

multicurl links against ext-curl's curl_multi_ce and cannot load without it

## Trap

`multicurl.c` uses ext-curl's exported `curl_multi_ce` and `curl_ce` and walks its private structs. The module entry declares `ZEND_MOD_REQUIRED("curl")`, so PHP refuses to start multicurl without ext-curl.[^c] Where curl is a shared module (Debian `20-curl.ini`), it must load before `40-multicurl.ini`. `PHP_ADD_EXTENSION_DEP([multicurl], [curl])` covers static builds.[^m4]

## Do

Keep ext-curl enabled in every SAPI that loads multicurl. Keep multicurl's ini priority after curl's (`40-` after `20-`).

[^c]: [multicurl.c](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/multicurl.c)
[^m4]: [config.m4](https://github.com/php-io-extensions/multicurl/blob/v0.11.1/config.m4)
