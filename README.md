This project contains scripts for generating reports about cyclic
dependencies in the [MediaWiki](https://mediawiki.org) code base. 
The analysis is based on [phpda](https://github.com/mamuz/PhpDependencyAnalysis).

Installation
--------------
* clone this repository
* run composer install

Usage
------
* call `mwda *<path-to-mediawiki>*`
* a report will be generated in www/report
* visit [the www directory](./www/) with your browser

License
--------
(c) Wikimedia Foundation 2019, licensed [GPL 2.0 or later](./COPYING).
